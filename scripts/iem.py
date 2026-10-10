"""IEM archived METAR observations. Never sum overlapping rolling rain reports."""
import csv
import datetime as dt
import io
from pathlib import Path
import re
import requests
from common import UTC,bounds,finite,identifier,inventory,interval_total

URL='https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py'

def station_id(value):
    sid=identifier(value).upper()
    return sid[1:] if len(sid)==4 and sid.startswith('K') else sid

def parse(text,station,start,end):
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {'station','valid'}.issubset(reader.fieldnames):
        raise ValueError('IEM CSV missing station identity or valid time')
    begin,stop=bounds(start,end);rows=[]
    for raw in reader:
        if station_id(raw.get('station'))!=station_id(station):continue
        try:t=dt.datetime.strptime(raw['valid'],'%Y-%m-%d %H:%M').replace(tzinfo=UTC)
        except (ValueError,TypeError):continue
        if not begin<=t<stop:continue
        rows.append({'time':t,'wind':finite(raw.get('sknt'),0,180),'gust':finite(raw.get('gust'),0,200),
                     'dir':finite(raw.get('drct'),0,360),'pressure':finite(raw.get('mslp'),850,1100),
                     'rain':finite(raw.get('p01i'),0,25),'trace':raw.get('p01i')=='T',
                     'report_type':(4 if str(raw.get('metar') or '').lstrip().upper().startswith('SPECI ') else 3 if str(raw.get('metar') or '').strip() else None),'raw':raw})
        # PK WND is the measured peak since the previous routine report, not
        # the gust at METAR issuance. Preserve its own direction and occurrence.
        match=re.search(r'\bPK WND (\d{3})(\d{2,3})/(\d{2})(\d{2})?\b',raw.get('metar') or '')
        if match:
            direction,speed,first,last=match.groups()
            hour=int(first) if last is not None else t.hour
            minute=int(last) if last is not None else int(first)
            try:
                peak=t.replace(hour=hour,minute=minute)
                if peak>t:peak-=dt.timedelta(days=1) if last is not None else dt.timedelta(hours=1)
                if begin<=peak<stop:
                    rows.append({'time':peak,'wind':None,'gust':finite(speed,0,200),'gust_dir':finite(direction,0,360),
                                 'pressure':None,'rain':None,'raw':raw,'gust_original_unit':'kn',
                                 'peak_kind':'METAR PK WND remark'})
            except ValueError:pass
    return rows

def collect(station,start,end,session=requests):
    stop=end+dt.timedelta(days=1)
    params={'station':station_id(station),'data':['sknt','gust','drct','mslp','p01i','metar'],
            'year1':start.year,'month1':start.month,'day1':start.day,
            'year2':stop.year,'month2':stop.month,'day2':stop.day,
            'tz':'Etc/UTC','format':'onlycomma','latlon':'no','missing':'M','trace':'T','direct':'no',
            'report_type':[3,4]}
    r=session.get(URL,params=params,timeout=30);r.raise_for_status()
    rows=parse(r.text,station,start,end)
    for row in rows:row['url']=r.url
    return rows,r.url

def rain_total(rows,start,end):
    periods={}
    for row in rows:
        # Routine METAR hourly accumulations only; SPECI overlaps are not added.
        if row.get('report_type')!=3:continue
        t=row['time'];begin=t-dt.timedelta(hours=1)
        if begin<start or t>end:continue
        v=row.get('rain');key=(begin,t)
        if key in periods and periods[key]!=v:return None
        periods[key]=v
    return interval_total([(a,b,v) for (a,b),v in periods.items()],start,end)

def write_wind(sheet,r,rows,site,audit,default_url,details):
    written=0
    for field,col,dircol in [('wind',11,12),('gust',17,18),('pressure',23,None)]:
        good=[x for x in rows if x.get(field) is not None]
        if not good:continue
        sample=(min if field=='pressure' else max)(good,key=lambda x:x[field]);value=sample[field];t=sample['time']
        sheet.cell(r,col).value=round(value,1)
        direction=sample.get('gust_dir') if field=='gust' else sample.get('dir')
        if dircol and direction is not None:sheet.cell(r,dircol).value=round(direction)
        offset=col+2 if dircol else col+1
        for n,v in enumerate((t.strftime('%H%M'),t.day,t.month,t.year)):sheet.cell(r,offset+n).value=v
        audit.add('Wind and Pressure',r,site,field,round(value,1),'hPa' if field=='pressure' else 'kn',t,
                  sample.get('url') or default_url,raw_value=sample.get(field+'_original_value',value),
                  raw_unit=sample.get(field+'_original_unit'),status='REVIEW REQUIRED',
                  details=details+f'; {len(good)} available readings for this variable, first {min(x["time"] for x in good).isoformat()}, last {max(x["time"] for x in good).isoformat()}; no claim of complete event coverage')
        if sample.get('retrieval'):audit.entries[-1]['retrieval']=sample['retrieval']
        written+=1
    sheet.cell(r,28).value='I';sheet.cell(r,29).value='A'
    sheet.cell(r,30).value=details+'; sampling/coverage and station exposure require review'
    return written

def populate(wb,qc,start,end,counts,audit,output_dir=None):
    from cocorahs import rain_bounds
    ra,rb=rain_bounds(start,end)
    fetch_start=min(start,ra.date());fetch_end=max(end,rb.date())
    rain_partials=[]
    cache={}
    def get(site):
        sid=station_id(site)
        if sid not in cache:
            try:cache[sid]=collect(sid,fetch_start,fetch_end)
            except requests.RequestException as e:cache[sid]=ValueError('IEM request failed: '+type(e).__name__)
            except ValueError as e:cache[sid]=e
        if isinstance(cache[sid],Exception):raise cache[sid]
        return cache[sid]
    for tab in ('Wind and Pressure','Rainfall'):
        s=wb[tab]
        for st in inventory(wb,tab):
            if st['network'].upper() not in ('ASOS','AWOS'):continue
            try:
                rows,url=get(st['id']);r=st['row']
                if tab=='Wind and Pressure':
                    n=write_wind(s,r,[x for x in rows if bounds(start,end)[0]<=x['time']<bounds(start,end)[1]],st['id'],audit,url,'IEM archived METAR; sea-level pressure only')
                    status='REVIEW REQUIRED' if n else 'NO DATA';detail=f'{len(rows)} samples; {n}/3 variables; UTC window'
                else:
                    from cocorahs import rain_bounds
                    a,b=rain_bounds(start,end);total=rain_total(rows,a,b)
                    status='REVIEW REQUIRED' if total is not None else 'INCOMPLETE'
                    detail='Hourly precipitation requires complete nonoverlapping routine METAR intervals; traces/missing periods are not zero'
                    if total is None:
                        # Preserve observed hourly accumulations as reported;
                        # do not turn them into a guessed event total.
                        for sample in rows:
                            v=sample.get('rain')
                            t=sample['time']
                            if v is None or not a<t<=b or sample.get('report_type')==4:continue
                            rain_partials.append({'station_id':st['id'],'report_type':'IEM METAR hourly p01i',
                                'period_start_utc':(t-dt.timedelta(hours=1)).isoformat(),
                                'period_end_utc':t.isoformat(),'reported_in':v,
                                'requested_start_utc':a.isoformat(),'requested_end_utc':b.isoformat(),
                                'classification':'PARTIAL REPORT — NOT A VERIFIED STORM TOTAL',
                                'source_url':url})
                    if total is not None:
                        s.cell(r,8).value=round(total,2);s.cell(r,9).value='I'
                        audit.add(tab,r,st['id'],'rain',round(total,2),'in',b,url,interval_start=a,details=detail)
                qc.append([tab,st['id'],st['network'],status,detail,url]);counts['iem_'+status]+=1
            except ValueError as e:
                qc.append([tab,st['id'],st['network'],'ERROR',str(e),URL]);counts['iem_errors']+=1

    if rain_partials:
        import csv
        target=(Path(output_dir) if output_dir is not None else Path('output'))/'Rainfall_partial_reports.csv'
        with target.open('a',newline='',encoding='utf-8') as fh:
            writer=csv.DictWriter(fh,fieldnames=['station_id','report_type','period_start_utc',
                'period_end_utc','reported_in','requested_start_utc','requested_end_utc',
                'classification','source_url'])
            writer.writerows(rain_partials)
    counts['iem_rain_partial_reports']=len(rain_partials)
