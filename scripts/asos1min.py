"""NOAA ASOS page-1/page-2 minute archive served by IEM, exact station only.

NOAA documents sknt as a two-minute average, gust_sknt as a five-second
maximum, and precip as a one-minute amount in inches. Station pressure is
never converted to sea-level pressure. Complete minute coverage is mandatory
for rain; observational peaks remain review candidates, not official values.
"""
import csv
import datetime as dt
import io
from concurrent.futures import ThreadPoolExecutor
import requests
from common import UTC,bounds,finite,inventory,interval_total
from cocorahs import rain_bounds
from iem import station_id,write_wind
URL='https://mesonet.agron.iastate.edu/cgi-bin/request/asos1min.py'
DOC='https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg1/doc/asos-1min-pg1_documentation.pdf'
RAIN_DOC='https://www.ncei.noaa.gov/data/automated-surface-observing-system-one-minute-pg2/doc/asos-1min-pg2_documentation.pdf'

def parse(text,station,start,end,include_end=False):
    reader=csv.DictReader(io.StringIO(text));required={'station','valid(Etc/UTC)','sknt','gust_sknt','gust_drct','drct','precip'}
    if not reader.fieldnames or not required.issubset(reader.fieldnames):raise ValueError('ASOS minute schema/UTC units missing')
    a,b=bounds(start,end);rows=[]
    for x in reader:
        if station_id(x['station'])!=station_id(station):continue
        try:t=dt.datetime.strptime(x['valid(Etc/UTC)'],'%Y-%m-%d %H:%M').replace(tzinfo=UTC)
        except ValueError:continue
        if t<a or t>b or (t==b and not include_end):continue
        rows.append({'time':t,'wind':finite(x['sknt'],0,180),'gust':finite(x['gust_sknt'],0,200),
                     'dir':finite(x['drct'],0,360),'gust_dir':finite(x['gust_drct'],0,360),
                     'pressure':None,'rain':finite(x['precip'],0,.5)})
    # Conflicting values at a timestamp invalidate the minute series.
    seen={}
    for row in rows:
        if row['time'] in seen and row!=seen[row['time']]:raise ValueError('Conflicting ASOS minute records')
        seen[row['time']]=row
    return sorted(seen.values(),key=lambda x:x['time'])

def collect(station,start,end,session=requests):
    stop=end+dt.timedelta(days=1)
    params={'station':station_id(station),'year1':start.year,'month1':start.month,'day1':start.day,
        'year2':stop.year,'month2':stop.month,'day2':stop.day,'hour2':0,'minute2':1,'tz':'Etc/UTC',
        'vars':['sknt','drct','gust_sknt','gust_drct','precip'],'sample':'1min','what':'download','delim':'comma','gis':'no'}
    r=session.get(URL,params=params,timeout=35);r.raise_for_status()
    rows=parse(r.text,station,start,end,include_end=True)
    for x in rows:x['url']=r.url
    return rows,r.url

def rain_total(rows,start,end):
    periods={}
    for row in rows:
        t=row['time'];a=t-dt.timedelta(minutes=1)
        if a<start or t>end:continue
        key=(a,t);v=row.get('rain')
        if key in periods and periods[key]!=v:return None
        periods[key]=v
    return interval_total([(a,b,v) for (a,b),v in periods.items()],start,end)

def populate(wb,qc,start,end,counts,audit):
    a,b=bounds(start,end);ra,rb=rain_bounds(start,end)
    stations={station_id(st['id']) for tab in ('Wind and Pressure','Rainfall') for st in inventory(wb,tab) if st['network'].upper()=='ASOS'}
    fetch_start=min(start,ra.date());fetch_end=max(end,rb.date())
    def fetch(sid):
        try:return sid,collect(sid,fetch_start,fetch_end)
        except (requests.RequestException,ValueError):return sid,None
    with ThreadPoolExecutor(max_workers=4) as pool:cache=dict(pool.map(fetch,sorted(stations)))
    for tab in ('Wind and Pressure','Rainfall'):
        s=wb[tab]
        for st in inventory(wb,tab):
            if st['network'].upper()!='ASOS':continue
            result=cache.get(station_id(st['id']));n=0;detail='NOAA/IEM exact-ID minute archive; '+DOC
            if result is None:status='UNAVAILABLE'
            else:
                rows,url=result
                if tab=='Wind and Pressure':
                    candidates=[dict(x) for x in rows if a<=x['time']<b]
                    # Keep the greatest same-variable extreme across qualified archives.
                    for field,col in [('wind',11),('gust',17)]:
                        good=[x for x in candidates if x[field] is not None]
                        peak=max(good,key=lambda x:x[field]) if good else None
                        old=finite(s.cell(st['row'],col).value)
                        if not peak or (old is not None and peak[field]<=old):
                            for x in candidates:x[field]=None
                        else:
                            audit.entries[:]=[e for e in audit.entries if (e['tab'],e['row'],e['variable'])!=(tab,st['row'],field)]
                    n=write_wind(s,st['row'],candidates,st['id'],audit,url,'NOAA/IEM two-minute average and five-second maximum; '+DOC)
                    status='REVIEW REQUIRED' if n else 'NO ADDITIONAL PEAKS';detail+=f'; {len(rows)} samples; {n} improved extremes'
                else:
                    total=rain_total(rows,ra,rb);status='INCOMPLETE'
                    if total is not None and s.cell(st['row'],8).value is None:
                        n=1;s.cell(st['row'],8).value=round(total,2);s.cell(st['row'],9).value='I';status='REVIEW REQUIRED'
                        audit.add(tab,st['row'],st['id'],'rain',round(total,2),'in',rb,url,interval_start=ra,raw_value=total,
                            details='Complete one-minute amounts, intervals ending at UTC report time; '+RAIN_DOC)
                    detail='Complete one-minute rainfall coverage required; missing/trace minutes withheld; '+RAIN_DOC
            qc.append([tab,st['id'],st['network'],status,detail,result[1] if result else URL]);counts['asos_minute_'+status]+=1
