"""Exact-ID IEM archived CoCoRaHS reports when primary downloads fail.

Calendar-date summaries lack actual observation clocks and accumulation bounds.
Preserve each measured amount separately for review; never populate/sum PSH.
"""
import csv
import datetime as dt
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import requests
from common import inventory,finite,observation_now,public_url
from cocorahs import canonical,rain_bounds

FILES=['rainfall_archive_review.json','rainfall_archive_review.csv']
URL='https://mesonet.agron.iastate.edu/api/1/daily.json'
DOC='https://mesonet.agron.iastate.edu/request/daily.phtml'
FIELDS=['site_id','source_station_id','network','template_name','source_name','source_date','reported_inches','trace','actual_observation_time_utc','period_start_utc','period_end_utc','can_populate_psh','qualification','source_url']

def parse(payload,station,network,start_date,end_date):
    data=payload.get('data')
    if not isinstance(data,list):raise ValueError('IEM daily archive schema missing')
    reports=[];seen={}
    for raw in data:
        if raw.get('station')!=canonical(station) or raw.get('id')!=canonical(station):continue
        try:date=dt.date.fromisoformat(raw['date'])
        except (ValueError,TypeError,KeyError):continue
        # Current local reporting day cannot be assigned a fabricated UTC clock.
        if not start_date<=date<end_date:continue
        value=finite(raw.get('precip'),0,100)
        if value is None:continue
        if date in seen and seen[date]!=value:raise ValueError('Conflicting daily archive amounts')
        if date in seen:continue
        seen[date]=value
        reports.append(dict(site_id=station,source_station_id=raw['station'],network=network,source_name=raw.get('name'),source_date=date.isoformat(),
            reported_inches=None if value==.0001 else value,original_value=value,trace=value==.0001,actual_observation_time_utc=None,period_start_utc=None,period_end_utc=None,can_populate_psh=False,
            qualification='I — archived CoCoRaHS daily observation; actual UTC observation clock and accumulation bounds unavailable. Individual report, NOT a storm total. Unit basis: IEM daily precipitation inches; '+DOC))
    return reports

def populate(wb,qc,start,end,counts,audit,output_dir=Path('output')):
    out=Path(output_dir);reports=[];pages=[]
    failed={str(qc.cell(r,2).value) for r in range(2,qc.max_row+1) if qc.cell(r,1).value=='Rainfall' and qc.cell(r,3).value=='CoCoRaHS' and qc.cell(r,4).value=='ERROR'}
    stations=[s for s in inventory(wb,'Rainfall') if s['network']=='CoCoRaHS' and s['id'] in failed and wb['Rainfall'].cell(s['row'],8).value is None]
    a,b=rain_bounds(start,end)
    from zoneinfo import ZoneInfo
    cutoff=min(b.date()+dt.timedelta(days=1),observation_now().astimezone(ZoneInfo('America/Chicago')).date())
    days=[];date=a.date()
    while date<cutoff:days.append(date);date+=dt.timedelta(days=1)
    networks=sorted({s['id'][:2]+'_COCORAHS' for s in stations})
    def fetch(key):
        network,date=key
        try:
            r=requests.get(URL,params={'network':network,'date':date.isoformat()},timeout=(5,20));r.raise_for_status();payload=r.json()
            if not isinstance(payload.get('data'),list):raise ValueError('IEM daily schema')
            return dict(network=network,date=date.isoformat(),url=public_url(r.url),payload=payload)
        except (requests.RequestException,ValueError) as exc:return dict(network=network,date=date.isoformat(),error=type(exc).__name__)
    with ThreadPoolExecutor(max_workers=2) as pool:pages=list(pool.map(fetch,[(n,d) for n in networks for d in days]))
    for st in stations:
        network=st['id'][:2]+'_COCORAHS';rows=[]
        for page in pages:
            if page['network']!=network or 'payload' not in page:continue
            found=parse(page['payload'],st['id'],network,a.date(),cutoff)
            for r in found:r.update(row=st['row'],template_name=st['name'],source_url=page['url'])
            rows.extend(found)
        reports.extend(rows)
        if rows:qc.append(['Rainfall',st['id'],'CoCoRaHS','ARCHIVE INTERVAL REVIEW',f'{len(rows)} exact-ID archived daily measurements preserved separately; no UTC clock or accumulation period inferred',rows[0]['source_url']])
    (out/FILES[0]).write_text(json.dumps(dict(reports=reports,retrievals=pages),indent=2,allow_nan=False)+'\n')
    with (out/FILES[1]).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS,extrasaction='ignore');w.writeheader();w.writerows(reports)
    counts['cocorahs_archive_review_stations']=len({r['site_id'] for r in reports});counts['cocorahs_archive_review_reports']=len(reports)
    return reports
