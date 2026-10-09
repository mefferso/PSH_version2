"""Event-effective, independently reviewed datum registry for exact USACE/CPRA gauges.

Never infer offsets from site altitude, present-day gauge zero or nearby stations.
Registry citations attest a human review; no offsets are shipped or auto-approved.
"""
import csv
import datetime as dt
import io
import json
import os
from pathlib import Path
from urllib.parse import urlparse
import requests
from common import inventory,finite,UTC,bounds,timestamp,public_url
from usace import station_link

HML='https://mesonet.agron.iastate.edu/cgi-bin/request/hml.py'

def offset(entry,station,start,end):
    from urllib.parse import parse_qs
    sid=parse_qs(urlparse(station['url']).query).get('sid',[''])[0]
    if entry.get('site_id')!=station['id'] or entry.get('rivergages_sid')!=sid or not sid:raise ValueError('Datum identity mismatch')
    a=timestamp(entry.get('effective_start_utc'));b=timestamp(entry.get('effective_end_utc'))
    if entry.get('reviewed') is not True or entry.get('datum')!='NAVD88' or not a or not b or not a<=start<end<=b:
        raise ValueError('Datum is not reviewed or not valid for full requested window')
    citations=entry.get('evidence') or []
    if len({urlparse(public_url(u)).hostname for u in citations})<2:raise ValueError('Two independent datum evidence sources required')
    value=finite(entry.get('offset_ft'),-1000,1000)
    if value is None:raise ValueError('Invalid event-effective datum offset')
    return value

def parse_hml(text,station,start,end):
    reader=csv.DictReader(io.StringIO(text))
    if reader.fieldnames:reader.fieldnames=[name.strip().lower() for name in reader.fieldnames]
    if not reader.fieldnames or not {'station','valid[utc]','stage[ft]'}.issubset(reader.fieldnames):
        raise ValueError('HML requires explicit stage[ft] and valid[utc] headers')
    a,b=bounds(start,end);rows=[]
    for x in reader:
        if x.get('station')!=station:continue
        try:t=dt.datetime.strptime(x['valid[utc]'],'%Y-%m-%d %H:%M').replace(tzinfo=UTC)
        except ValueError:continue
        v=finite(x.get('stage[ft]'),-100,100)
        if v is not None and a<=t<b:rows.append((v,t))
    return rows

def collect(station,start,end,session=requests):
    stop=end+dt.timedelta(days=1)
    r=session.get(HML,params={'station':station,'kind':'obs','tz':'UTC','fmt':'csv',
        'year1':start.year,'month1':start.month,'day1':start.day,'year2':stop.year,'month2':stop.month,'day2':stop.day},timeout=20)
    r.raise_for_status();return parse_hml(r.text,station,start,end),r.url

def populate(wb,qc,start,end,counts,audit):
    from collections import Counter
    from concurrent.futures import ThreadPoolExecutor
    path=os.environ.get('PSH_DATUM_REGISTRY')
    entries=json.loads(Path(path).read_text()) if path else [];a,b=bounds(start,end)
    if len({x['site_id'] for x in entries})!=len(entries):raise ValueError('Duplicate IDs in datum registry')
    registry={x['site_id']:x for x in entries}
    all_stations=list(inventory(wb,'Water Level'));duplicates=Counter(st['id'] for st in all_stations)
    stations=[st for st in all_stations if st['network'] in ('USACE','LA CPRA')]
    eligible=[st for st in stations if duplicates[st['id']]==1 and station_link(wb['Water Level'].cell(st['row'],1))]
    def fetch(st):
        try:return st['id'],collect(st['id'],start,end)
        except (requests.RequestException,ValueError) as exc:return st['id'],exc
    with ThreadPoolExecutor(max_workers=4) as pool:cache=dict(pool.map(fetch,eligible))
    for st in stations:
        if duplicates[st['id']]>1:
            qc.append(['Water Level',st['id'],st['network'],'AMBIGUOUS ID','Duplicate inventory identifier; HML mapping and conversion withheld',st['url']]);continue
        if st['id'] not in cache:
            qc.append(['Water Level',st['id'],st['network'],'UNSUPPORTED','No valid original RiverGages station hyperlink; no historical mapping invented',st['url']]);continue
        result=cache[st['id']]
        if isinstance(result,Exception):
            qc.append(['Water Level',st['id'],st['network'],'ERROR','Historical HML stage request/schema unavailable: '+type(result).__name__,HML]);counts['registry_water_errors']+=1;continue
        rows,url=result
        if not rows:
            qc.append(['Water Level',st['id'],st['network'],'NO DATA','No exact-ID historical HML stage readings',url]);continue
        raw,t=max(rows,key=lambda x:x[0])
        counts['historical_stage_series_retrieved']+=1
        if st['id'] not in registry:
            qc.append(['Water Level',st['id'],st['network'],'DATUM REVIEW',
                f'{len(rows)} exact-ID HML observations; available stage peak {raw} ft gage stage at {t.isoformat()}. NOT NAVD88/inundation; no workbook elevation inserted without independently reviewed event-effective datum evidence.',url]);continue
        record=registry[st['id']]
        # Invalid reviewed metadata fails the build; stage alone never establishes elevation.
        adjustment=offset(record,st,a,b);value=finite(raw+adjustment,-30,100)
        if value is None:raise ValueError('Converted elevation outside QC range')
        s=wb['Water Level'];s.cell(st['row'],7).value=round(value,2);s.cell(st['row'],8).value='NAVD88'
        for n,v in enumerate((t.strftime('%H%M'),t.day,t.month,t.year)):s.cell(st['row'],9+n).value=v
        s.cell(st['row'],14).value='I'
        audit.add('Water Level',st['row'],st['id'],'water',round(value,2),'ft',t,url,datum='NAVD88',
            evidence=record['evidence'],raw_value=raw,raw_unit='ft gage stage',
            details=f'Human-reviewed event-effective registry: stage + {adjustment} ft; effective {record["effective_start_utc"]} to {record["effective_end_utc"]}')
        qc.append(['Water Level',st['id'],st['network'],'REVIEW REQUIRED','Registry conversion applied; independent citations in provenance',url]);counts['registry_water_collected']+=1
