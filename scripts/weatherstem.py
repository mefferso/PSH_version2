"""Exact linked WeatherSTEM historical sensor retrieval with metadata unit gates.

The public form contract follows mefferso/PSH_project. Native minute Anemometer readings retained as review candidates following the
historically tested v0.10 PSH approach, without assuming a one-minute mean.
"""
import datetime as dt
import re
from urllib.parse import urlparse,parse_qs
import requests
from common import inventory,finite,bounds,UTC,timestamp
from iem import write_wind

CDN='https://cdn.weatherstem.com/dashboard/data/dynamic/model'
FACTORS={'mph':0.8689762419006479,'m/s':1.9438444924406,'kn':1,'knots':1}

def link_parts(link):
    p=urlparse(link);host=p.hostname or '';slug=parse_qs(p.query).get('refer',[''])[0].lstrip('/')
    if not re.fullmatch(r'[a-z0-9-]+\.weatherstem\.com',host) or p.path!='/data' or not re.fullmatch(r'[a-z0-9_-]+',slug):
        raise ValueError('No exact WeatherSTEM station hyperlink')
    return host.split('.')[0],slug

def sensors(metadata):
    return [s for t in metadata.get('transmitters',[]) for s in t.get('sensors',[]) if isinstance(s,dict)]

def parse(raw,metadata,start,end):
    if not isinstance(raw,list) or not raw or not isinstance(raw[0],list):raise ValueError('WeatherSTEM unexpected table schema')
    known={}
    for sensor in sensors(metadata):
        name=sensor.get('name') or sensor.get('type');unit=sensor.get('unit') or sensor.get('units')
        if isinstance(unit,dict):unit=unit.get('symbol') or unit.get('abbreviation') or unit.get('name')
        if name in known:known[name]=None
        else:known[name]=dict(sensor,unit=unit)
    a,b=bounds(start,end);rows=[]
    for values in raw[1:]:
        if not isinstance(values,list) or len(values)!=len(raw[0]):continue
        record=dict(zip(raw[0],values));rawtime=record.get('Timestamp');t=timestamp(rawtime)
        if t is None:
            # /data was explicitly requested with timezone_offset=0.
            try:t=dt.datetime.fromisoformat(str(rawtime)).replace(tzinfo=UTC)
            except ValueError:continue
        if not a<=t<b:continue
        row={'time':t,'wind':None,'gust':None,'pressure':None,'dir':None,'gust_dir':None,'unqualified_speed':None}
        for name,meta in known.items():
            if not meta:continue
            n=str(name).lower();v=finite(record.get(name));unit=meta.get('unit')
            if v is None:continue
            if n=='anemometer' and unit in FACTORS:
                period=finite(meta.get('averaging_period_minutes'),1,10)
                row['wind']=finite(v*FACTORS[unit],0,180)
                row['wind_averaging_period_minutes']=period
                row['wind_averaging_period_basis']='explicit station metadata' if period in (1,2,8,10) else 'unverified native Anemometer average'
                row['wind_sensor_id']=meta.get('id')
            elif re.fullmatch(r'10\s*minute\s*wind\s*gust',n) and unit in FACTORS:
                if t-dt.timedelta(minutes=10)>=a:row['gust']=finite(v*FACTORS[unit],0,200)
            elif n=='wind vane' and unit in ('degrees','Degrees','deg','&deg;'):row['dir']=finite(v,0,360)
            elif n in ('sea level pressure','mean sea level pressure') and unit in ('hPa','mb','Pa'):
                row['pressure']=finite(v*(.01 if unit=='Pa' else 1),850,1100)
        for field,names in [('wind',['anemometer']),('gust',['10 minute wind gust']),('pressure',['sea level pressure','mean sea level pressure'])]:
            for name,meta in known.items():
                if meta and str(name).lower() in names and row[field] is not None:
                    row[field+'_original_value']=finite(record.get(name));row[field+'_original_unit']=meta['unit']
        rows.append(row)
    directions=[x for x in rows if x['dir'] is not None]
    for row in rows:
        if row['wind'] is None or row['dir'] is not None or not directions:continue
        closest=min(directions,key=lambda x:(abs((x['time']-row['time']).total_seconds()),x['time']))
        if abs((closest['time']-row['time']).total_seconds())<=300:
            row['dir']=closest['dir']
            row['direction_time_utc']=closest['time'].isoformat()
    return rows

def collect(link,start,end,session=requests):
    network,slug=link_parts(link);metadata_url=f'{CDN}/{network}/{slug}/station.json'
    r=session.get(metadata_url,timeout=20);r.raise_for_status();metadata=r.json()
    if not metadata.get('id'):raise ValueError('WeatherSTEM station identity missing')
    a,b=bounds(start,end);ids=[str(x['id']) for x in sensors(metadata) if x.get('id') is not None]
    if not ids:raise ValueError('WeatherSTEM sensor IDs missing')
    payload={'timezone_offset':0,'id':str(metadata['id']),'start_date':a.strftime('%Y-%m-%d %H:%M'),
        'end_date':b.strftime('%Y-%m-%d %H:%M'),'operation':'datapoint','interval':'minute',
        'sensors':ids,'format':'json','timestamp_format':'standard','record_id':'1','mysql_mode':False,'query':''}
    import json
    response=session.post(f'https://{network}.weatherstem.com/data',data=json.dumps(payload),
        headers={'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8','Referer':link,'X-Requested-With':'XMLHttpRequest'},timeout=30)
    response.raise_for_status()
    rows=parse(response.json(),metadata,start,end)
    for row in rows:
        row['url']=link;row['retrieval']={'method':'POST','url':f'https://{network}.weatherstem.com/data','parameters':payload,'metadata_url':metadata_url}
    return rows,metadata_url

def populate(wb,qc,start,end,counts,audit):
    for st in inventory(wb,'Wind and Pressure'):
        if st['network']!='WeatherSTEM':continue
        try:
            rows,meta=collect(st['url'],start,end)
            n=write_wind(wb['Wind and Pressure'],st['row'],rows,st['id'],audit,st['url'],
                'WeatherSTEM exact sensor; explicit units/averaging required; metadata '+meta)
            for entry in audit.entries:
                if entry['tab']!='Wind and Pressure' or entry['row']!=st['row'] or entry['variable']!='wind':continue
                sample=next((x for x in rows if x['wind'] is not None and round(x['wind'],1)==entry['value'] and x['time'].isoformat()==entry['time_utc']),None)
                if sample:
                    entry['source_kind']='WeatherSTEM native Anemometer'
                    entry['sensor_id']=sample['wind_sensor_id']
                    entry['averaging_period_minutes']=sample['wind_averaging_period_minutes']
                    entry['averaging_period_basis']=sample['wind_averaging_period_basis']
                    entry['reporting_interval_minutes']=1
                    entry['interpretation']='Native observed maximum; averaging semantics require meteorologist review'
                    if sample.get('direction_time_utc'):entry['direction_time_utc']=sample['direction_time_utc']
                break
            status='REVIEW REQUIRED' if n else 'METADATA REVIEW'
            detail=f'{len(rows)} samples; {n}/3 variables. Native minute Anemometer maximum retained without rolling average; averaging interval remains review-required unless explicit. Original native gust unchanged. Rainfall sensor/window unvalidated.'
            candidates=[x for x in rows if x.get('unqualified_speed') is not None]
            if candidates:
                best=max(candidates,key=lambda x:x['unqualified_speed'])
                detail+=f"; unqualified anemometer maximum {best['unqualified_speed']:.1f} kt at {best['time'].isoformat()} (NOT a verified sustained wind; averaging period unknown)"
                counts['weatherstem_unqualified_speed_candidates']+=1
        except (requests.RequestException,ValueError,KeyError,TypeError):
            status='ERROR';detail='Exact WeatherSTEM metadata/archive request or schema unavailable; no nearby fallback'
        qc.append(['Wind and Pressure',st['id'],st['network'],status,detail,st['url']]);counts['weatherstem_'+status]+=1
