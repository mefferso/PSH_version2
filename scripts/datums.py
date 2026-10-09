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
    if not os.environ.get('PSH_DATUM_REGISTRY'):return
    entries=json.loads(Path(os.environ['PSH_DATUM_REGISTRY']).read_text());a,b=bounds(start,end)
    if len({x['site_id'] for x in entries})!=len(entries):raise ValueError('Duplicate IDs in datum registry')
    registry={x['site_id']:x for x in entries}
    for st in inventory(wb,'Water Level'):
        if st['network'] not in ('USACE','LA CPRA') or st['id'] not in registry:continue
        record=registry[st['id']]
        # Registry validation errors fail the build; access errors are per-source QC.
        adjustment=offset(record,st,a,b)
        try:
            rows,url=collect(st['id'],start,end)
            if not rows:
                qc.append(['Water Level',st['id'],st['network'],'NO DATA','No exact-ID HML stage readings',url]);continue
            raw,t=max(rows,key=lambda x:x[0]);value=finite(raw+adjustment,-30,100)
            if value is None:raise ValueError('Converted elevation outside QC range')
            s=wb['Water Level'];s.cell(st['row'],7).value=round(value,2);s.cell(st['row'],8).value='NAVD88'
            for n,v in enumerate((t.strftime('%H%M'),t.day,t.month,t.year)):s.cell(st['row'],9+n).value=v
            s.cell(st['row'],14).value='I'
            audit.add('Water Level',st['row'],st['id'],'water',round(value,2),'ft',t,url,datum='NAVD88',
                evidence=record['evidence'],raw_value=raw,raw_unit='ft gage stage',
                details=f'Human-reviewed event-effective registry: stage + {adjustment} ft; effective {record["effective_start_utc"]} to {record["effective_end_utc"]}')
            qc.append(['Water Level',st['id'],st['network'],'REVIEW REQUIRED','Registry conversion applied; independent citations in provenance',url]);counts['registry_water_collected']+=1
        except requests.RequestException:
            qc.append(['Water Level',st['id'],st['network'],'ERROR','HML historical stage request unavailable',HML]);counts['registry_water_errors']+=1
