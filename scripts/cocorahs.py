"""Official historical daily rain: exact station, explicit UTC times and full intervals."""
import datetime as dt
import os
import re
import requests
from common import inventory,finite,timestamp,interval_total,bounds,public_url

URL='https://api2.cocorahs.org/api/DailyPrecipObs'

def canonical(sid):
    m=re.fullmatch(r'([A-Z]{2}-[A-Z]+)-0*(\d+)',str(sid).upper())
    return m.group(1)+'-'+str(int(m.group(2))) if m else str(sid).upper()

def rain_bounds(start,end):
    a,b=bounds(start,end)
    if os.environ.get('RAIN_START_UTC') or os.environ.get('RAIN_END_UTC'):
        a=timestamp(os.environ.get('RAIN_START_UTC'));b=timestamp(os.environ.get('RAIN_END_UTC'))
        if not a or not b or a>=b or b-a>dt.timedelta(days=36):raise ValueError('Invalid explicit rainfall UTC window')
    return a,b

def field(report,name):return report.get(name,report.get(name[0].upper()+name[1:]))

def total(reports,station,start,end):
    periods={}
    for report in reports:
        if canonical(field(report,'stationNumber'))!=canonical(station):continue
        t=timestamp(field(report,'obsDateTime'));days=finite(field(report,'numDays'),1,36)
        # No assumed local timezone or daily period for undocumented responses.
        if not t or days is None:continue
        a=t-dt.timedelta(days=days)
        if a<start or t>end:continue
        value=finite(field(report,'gaugeCatch'),0,30)
        if field(report,'gaugeCatchIsTrace') or field(report,'precipIsTrace'):value=None
        key=(a,t)
        if key in periods and periods[key]!=value:return None
        periods[key]=value
    return interval_total([(a,b,v) for (a,b),v in periods.items()],start,end)

def collect_station(station,start,end,session=requests):
    reports=[];urls=[];offset=0
    for page in range(100):
        params={'offset':offset,'limit':250,'startDate':(start-dt.timedelta(days=1)).date().isoformat(),
            'endDate':(end+dt.timedelta(days=1)).date().isoformat(),'sortField':'ObsDateTime','sortDir':'asc',
            'stationField':'StationNumber','stationFieldValue':canonical(station),'units':'english'}
        r=session.get(URL,params=params,timeout=20);r.raise_for_status();data=r.json();urls.append(r.url)
        if not isinstance(data.get('results'),list):raise ValueError('CoCoRaHS unexpected results schema')
        results=data['results']
        if not results:break
        reports.extend(results);offset+=len(results)
        count=finite(((data.get('metadata') or {}).get('resultset') or {}).get('totalCount'),0,20000)
        if count is not None and offset>=count:break
    else:raise ValueError('CoCoRaHS incomplete pagination; series discarded')
    return reports,urls

def populate(wb,qc,start,end,counts,audit):
    from concurrent.futures import ThreadPoolExecutor
    a,b=rain_bounds(start,end);s=wb['Rainfall']
    stations=[st for st in inventory(wb,'Rainfall') if st['network']=='CoCoRaHS']
    def fetch(st):
        try:return st['id'],collect_station(st['id'],a,b)
        except (requests.RequestException,ValueError,TypeError):return st['id'],None
    with ThreadPoolExecutor(max_workers=6) as pool:cache=dict(pool.map(fetch,stations))
    for st in inventory(wb,'Rainfall'):
        if st['network']!='CoCoRaHS':continue
        data=cache.get(st['id']);status='ERROR';detail='Official CoCoRaHS historical request unavailable; not evidence of no reports';url=URL
        if data:
            reports,urls=data;value=total(reports,st['id'],a,b);url=urls[0] if urls else URL
            status='REVIEW REQUIRED' if value is not None else 'INCOMPLETE'
            detail='Exact-ID, reported UTC and numDays; complete interval coverage required; trace reports require manual review'
            if value is not None:
                s.cell(st['row'],8).value=round(value,2);s.cell(st['row'],9).value='I'
                audit.add('Rainfall',st['row'],st['id'],'rain',round(value,2),'in',b,url,interval_start=a,raw_value=value,details=detail)
        qc.append(['Rainfall',st['id'],st['network'],status,detail,public_url(url)]);counts['cocorahs_'+status]+=1
