"""Reviewed source imports. No automatic WeatherFlow access or guessed datum offsets."""
import json
from pathlib import Path
from urllib.parse import urlparse
from common import inventory,finite,bounds,timestamp,public_url

UNITS={'wind':('kn',0,180),'gust':('kn',0,200),'pressure':('hPa',850,1100),'rain':('in',0,100),'water':('ft',-30,100)}

def apply(wb,readings,start,end,audit):
    inventory_map={(tab,s['row']):s for tab in ('Wind and Pressure','Rainfall','Water Level') for s in inventory(wb,tab)}
    a,b=bounds(start,end);checked=[];seen=set()
    for x in readings:
        tab=x.get('tab');r=x.get('row');st=inventory_map.get((tab,r));field=x.get('variable')
        if not st or st['id']!=x.get('site_id') or st['network']!=x.get('network'):raise ValueError('Import inventory identity mismatch')
        if x.get('reviewed') is not True:raise ValueError('Imports require explicit human review')
        if field not in UNITS:raise ValueError('Unsupported variable')
        unit,lo,hi=UNITS[field];v=finite(x.get('value'),lo,hi);t=timestamp(x.get('time_utc'))
        if x.get('unit')!=unit or v is None or not t:raise ValueError('Invalid units, value or UTC time')
        if tab=='Wind and Pressure' and field not in ('wind','gust','pressure'):raise ValueError('Wrong variable for tab')
        if tab=='Rainfall' and field!='rain' or tab=='Water Level' and field!='water':raise ValueError('Wrong variable for tab')
        if field=='rain':
            if timestamp(x.get('interval_start_utc'))!=a or t!=b:raise ValueError('Rainfall does not cover full requested UTC window')
        elif not a<=t<b:raise ValueError('Observation outside requested UTC window')
        url=public_url(x.get('source_url',''))
        if field=='water':
            evidence=x.get('datum_evidence')
            if x.get('datum') not in ('MHHW','NAVD88') or not isinstance(evidence,list) or len(set(evidence))<2:
                raise ValueError('Water imports require two independent datum citations and reviewed elevation')
            if len({urlparse(public_url(u)).hostname for u in evidence})<2:
                raise ValueError('Datum evidence must have independent source hosts')
        key=(tab,r,field)
        if key in seen:raise ValueError('Duplicate imported variable')
        seen.add(key);checked.append((x,st,v,t,url))
    # Entire input validated before any workbook changes.
    for x,st,v,t,url in checked:
        tab=x['tab'];r=st['row'];field=x['variable'];s=wb[tab]
        if field in ('wind','gust','pressure'):
            col={'wind':11,'gust':17,'pressure':23}[field];s.cell(r,col).value=round(v,1)
            if field!='pressure' and finite(x.get('direction'),0,360) is not None:s.cell(r,col+1).value=round(float(x['direction']))
            offset=col+1 if field=='pressure' else col+2
            for n,part in enumerate((t.strftime('%H%M'),t.day,t.month,t.year)):s.cell(r,offset+n).value=part
            s.cell(r,28).value='I';s.cell(r,29).value='A';s.cell(r,30).value='Reviewed source import; see provenance'
        elif field=='rain':s.cell(r,8).value=round(v,2);s.cell(r,9).value='I'
        else:
            s.cell(r,7).value=round(v,2);s.cell(r,8).value=x['datum']
            for n,part in enumerate((t.strftime('%H%M'),t.day,t.month,t.year)):s.cell(r,9+n).value=part
            s.cell(r,14).value='I'
        audit.add(tab,r,st['id'],field,s.cell(r,{'wind':11,'gust':17,'pressure':23,'rain':8,'water':7}[field]).value,
                  x['unit'],t,url,datum=x.get('datum'),evidence=x.get('datum_evidence'),raw_value=v,
                  interval_start=timestamp(x.get('interval_start_utc')),status='REVIEWED IMPORT',
                  details='Human-reviewed import; datum citations are reviewer attestations, not an automatic conversion')

def load(wb,path,start,end,audit):apply(wb,json.loads(Path(path).read_text()),start,end,audit)

def template(wb,path):
    examples=[]
    for st in inventory(wb,'Wind and Pressure'):
        if st['network'].upper()!='WEATHERFLOW':continue
        examples.append({'tab':'Wind and Pressure','row':st['row'],'site_id':st['id'],'network':st['network'],
                         'variable':'gust','value':None,'unit':'kn','time_utc':'','direction':None,
                         'source_url':st['url'],'reviewed':False})
    Path(path).write_text(json.dumps(examples,indent=2))
