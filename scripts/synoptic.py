"""Credential-gated exact-ID Synoptic/MesoWest archived wind and MSLP."""
import os
import requests
from common import inventory,finite,bounds,timestamp
from iem import write_wind

URL='https://api.synopticdata.com/v2/stations/timeseries'
FACTORS={'wind_speed':{'m/s':1.9438444924406,'knots':1,'kts':1},
         'wind_gust':{'m/s':1.9438444924406,'knots':1,'kts':1},
         'sea_level_pressure':{'Pa':0.01,'Pascals':0.01,'hPa':1,'mb':1}}

def parse(payload,station,start,end,network=None):
    if (payload.get('SUMMARY') or {}).get('RESPONSE_CODE')!=1:raise ValueError('Synoptic API rejected request')
    a,b=bounds(start,end);units=payload.get('UNITS') or {};rows=[]
    for st in payload.get('STATION',[]):
        if st.get('STID')!=station:continue
        obs=st.get('OBSERVATIONS') or {}
        def series(name):
            # Never mix sensor sets or silently pick an alternative sensor.
            keys=[k for k in obs if k.startswith(name+'_set_')]
            return obs[keys[0]] if len(keys)==1 else []
        for n,rawtime in enumerate(obs.get('date_time',[])):
            t=timestamp(rawtime)
            if not t or not a<=t<b:continue
            row={'time':t,'gust_dir':None}
            for name,key,lo,hi in [('wind_speed','wind',0,180),('wind_gust','gust',0,200),('sea_level_pressure','pressure',850,1100)]:
                values=series(name);factor=FACTORS[name].get(units.get(name));v=finite(values[n]) if n<len(values) else None
                row[key]=finite(v*factor,lo,hi) if v is not None and factor is not None else None
                row[key+'_original_value']=v;row[key+'_original_unit']=units.get(name)
            if row.get('wind') is not None and row.get('gust') is not None and row['gust']<row['wind']:
                row['wind_qc']='Gust below concurrent speed; both observations quarantined'
                row['wind']=None;row['gust']=None
            sensors=(st.get('SENSOR_VARIABLES') or {}).get('wind_speed') or {}
            descriptions=[v for k,v in sensors.items() if k.startswith('wind_speed_set_') and isinstance(v,dict)]
            period=finite(descriptions[0].get('averaging_period_minutes')) if len(descriptions)==1 else None
            if period in (1,2,8,10):
                row['wind_averaging_period_minutes']=period
                row['wind_period_basis']='explicit station sensor metadata'
            elif period is None and str(network or '').upper()=='CWOP' and row.get('wind') is not None and not row.get('wind_qc'):
                # APRS weather packet s field is a nominal one-minute sustained
                # wind. The station's own sampling configuration is unverified.
                row['wind_averaging_period_minutes']=1
                row['wind_period_basis']='APRS CWOP 1-minute convention; station-specific averaging unverified; review required'
            else:
                row['unqualified_wind']=row.get('wind');row['wind']=None
            directions=series('wind_direction')
            row['dir']=finite(directions[n],0,360) if n<len(directions) and units.get('wind_direction') in ('Degrees','degrees') else None
            rows.append(row)
    # A gust maximum below the source's maximum speed is not a defensible storm gust.
    raw_speeds=[finite(x.get('wind_original_value'))*FACTORS['wind_speed'].get(x.get('wind_original_unit'),1) for x in rows if finite(x.get('wind_original_value')) is not None and x.get('wind_original_unit') in FACTORS['wind_speed']]
    gusts=[x['gust'] for x in rows if x.get('gust') is not None]
    if raw_speeds and gusts and max(gusts)<max(raw_speeds) and any(x.get('wind_qc') for x in rows):
        for x in rows:x['gust']=None;x['wind_qc']='Gust series inconsistent with concurrent speeds; maximum withheld'
    return rows

def populate(wb,qc,start,end,counts,audit):
    token=os.environ.get('SYNOPTIC_TOKEN')
    for st in inventory(wb,'Wind and Pressure'):
        if st['network'].upper() not in ('CWOP','RAWS'):continue
        if not token:
            qc.append(['Wind and Pressure',st['id'],st['network'],'CREDENTIAL REQUIRED','SYNOPTIC_TOKEN required for exact-ID historical timeseries',st['url']]);counts['synoptic_credential_required']+=1;continue
        try:
            a,b=bounds(start,end)
            r=requests.get(URL,params={'token':token,'stid':st['id'],'start':a.strftime('%Y%m%d%H%M'),
                'end':b.strftime('%Y%m%d%H%M'),'vars':'wind_speed,wind_gust,wind_direction,sea_level_pressure','obtimezone':'utc'},timeout=20)
            r.raise_for_status();rows=parse(r.json(),st['id'],start,end,network=st['network'])
            from common import public_url
            qualified=[x for x in rows if x.get('wind') is not None]
            inferred=[x for x in qualified if 'convention' in x.get('wind_period_basis','')]
            basis='APRS weather format convention (nominal 1-minute), station averaging not independently verified; ' if inferred else ''
            n=write_wind(wb['Wind and Pressure'],st['row'],rows,st['id'],audit,public_url(r.url),
                         'Synoptic exact-ID sensor; '+basis+'unit-qualified; MSLP only')
            if inferred:
                for entry in audit.entries:
                    if entry['tab']=='Wind and Pressure' and entry['row']==st['row'] and entry['variable']=='wind':
                        entry['averaging_period_minutes']=1
                        entry['averaging_period_basis']='CWOP APRS convention, not confirmed sensor configuration'
                        entry['status']='REVIEW REQUIRED'
                        break
            from common import public_url
            candidates=[x for x in rows if x.get('unqualified_wind') is not None]
            detail=f'{len(rows)} samples; {n}/3 variables. Explicit station averaging metadata used when available.'
            if inferred:detail+=' CWOP wind populated using nominal APRS 1-minute convention; actual station averaging period requires review.'
            inconsistent=sum(bool(x.get('wind_qc')) for x in rows)
            if inconsistent:detail+=f' {inconsistent} records flagged for inconsistent gust/speed; see source.'
            if candidates:
                peak=max(candidates,key=lambda x:x['unqualified_wind'])
                detail+=f' Unqualified speed peak {peak["wind_original_value"]} {peak["wind_original_unit"]} at {peak["time"].isoformat()} withheld from PSH sustained column.'
            qc.append(['Wind and Pressure',st['id'],st['network'],'REVIEW REQUIRED' if n else 'METADATA REVIEW' if candidates else 'NO DATA',detail,public_url(r.url)])
            counts['synoptic_collected' if n else 'synoptic_no_data']+=1
        except (requests.RequestException,ValueError,KeyError,TypeError):
            # Requests exceptions can contain the credential-bearing URL.
            qc.append(['Wind and Pressure',st['id'],st['network'],'ERROR','Synoptic request/schema unsuccessful; token redacted',URL]);counts['synoptic_errors']+=1

PRECIP_URL='https://api.synopticdata.com/v2/stations/precip'

PRECIP_DOC='https://docs.synopticdata.com/services/precipitation-service-explained'
PRECIP_PERIODS={'precip_accum_one_minute':1/60,'precip_accum_five_minute':5/60,
    'precip_accum_ten_minute':10/60,'precip_accum_fifteen_minute':.25,
    'precip_accum_one_hour':1,'precip_accum_three_hour':3,'precip_accum_six_hour':6,
    'precip_accum_12_hour':12,'precip_accum_24_hour':24}

def precip_total(payload,station,start,end):
    if (payload.get('SUMMARY') or {}).get('RESPONSE_CODE')!=1:raise ValueError('Synoptic precipitation API rejected request')
    unit=str((payload.get('UNITS') or {}).get('precipitation') or '').lower()
    factor={'inches':1,'in':1,'millimeters':1/25.4,'mm':1/25.4}.get(unit)
    if factor is None:return None
    from common import interval_total
    for st in payload.get('STATION',[]):
        if st.get('STID')!=station:continue
        records=(st.get('OBSERVATIONS') or {}).get('precipitation') or []
        readings=[]
        for x in records:
            a=timestamp(x.get('first_report'));b=timestamp(x.get('last_report'));v=finite(x.get('total'),0,10000)
            if a is None or b is None or a>=b or v is None:return None
            # Providers may include adjacent observations outside the requested
            # window. They must not invalidate a complete exact-window tiling.
            # Intervals crossing either requested boundary remain unqualified.
            if b<=start or a>=end:continue
            if a<start or b>end:return None
            nested=x.get('intervals')
            if isinstance(nested,list):
                parts=[(timestamp(i.get('start_utc')),timestamp(i.get('end_utc')),finite(i.get('total'),0,10000)) for i in nested]
                if any(not aa or not bb for aa,bb,vv in parts):return None
                value=interval_total(parts,a,b)
                if value is None or abs(value-v)>1e-6:return None
            else:
                # Actual native pmode=intervals records, not imaginary nested
                # fields. Daily reports do not require minute samples. A totals
                # aggregate with no sensor/report type is still insufficient.
                if not finite(x.get('interval'),1,10000):return None
                count=finite(x.get('count'),1,100000);period=PRECIP_PERIODS.get(x.get('report_type'))
                hours=(b-a).total_seconds()/3600
                if period is not None:
                    if count is None or hours/period!=round(hours/period) or count<hours/period:return None
                elif x.get('report_type')=='precip_accum':
                    # Documented provider reconstruction of continuous counters,
                    # explicitly labelled derived rather than a reported total.
                    if count is None or count<2:return None
                else:return None
            readings.append((a,b,v))
        value=interval_total(readings,start,end)
        return finite(value*factor,0,100) if value is not None else None
    return None

def populate_rain(wb,qc,start,end,counts,audit):
    from cocorahs import rain_bounds
    from concurrent.futures import ThreadPoolExecutor
    from common import public_url
    a,b=rain_bounds(start,end);token=os.environ.get('SYNOPTIC_TOKEN');s=wb['Rainfall']
    stations=[st for st in inventory(wb,'Rainfall') if st['network'].upper() in ('ASOS','AWOS','COOP','HADS','RAWS') and s.cell(st['row'],8).value is None]
    def fetch(st):
        # Only canonical ASOS ICAO prefix is normalized; COOP/HADS IDs unchanged.
        sid=('K'+st['id']) if st['network'].upper() in ('ASOS','AWOS') and len(st['id'])==3 else st['id']
        if not token:return st,None,None,'CREDENTIAL REQUIRED',None
        try:
            r=requests.get(PRECIP_URL,params={'token':token,'stid':sid,'start':a.strftime('%Y%m%d%H%M'),
                'end':b.strftime('%Y%m%d%H%M'),'pmode':'intervals','interval':'day','interval_window':'0','units':'english,precip|in','obtimezone':'UTC','all_reports':1,'complete':0},timeout=20)
            r.raise_for_status();value=precip_total(r.json(),sid,a,b)
            return st,value,public_url(r.url),'REVIEW REQUIRED' if value is not None else 'INCOMPLETE',r.json()
        except (requests.RequestException,ValueError,TypeError,KeyError):return st,None,None,'ERROR',None
    with ThreadPoolExecutor(max_workers=6) as pool:results=list(pool.map(fetch,stations))
    for st,value,url,status,payload in results:
        detail='Exact ID and units; native Synoptic reported intervals, verified report frequency/count and nonoverlapping UTC coverage. Provider-derived amounts require review. '+PRECIP_DOC
        records=[x for station in (payload or {}).get('STATION',[]) if station.get('STID')==(('K'+st['id']) if st['network'].upper() in ('ASOS','AWOS') and len(st['id'])==3 else st['id']) for x in (station.get('OBSERVATIONS') or {}).get('precipitation',[])]
        if records:
            import json
            detail+='; returned interval candidates: '+json.dumps(records,allow_nan=False)
        if payload and (payload.get('SUMMARY') or {}).get('RESPONSE_CODE')!=1:detail+='; provider response '+str((payload.get('SUMMARY') or {}).get('RESPONSE_MESSAGE','rejected'))
        if value is not None:
            s.cell(st['row'],8).value=round(value,2);s.cell(st['row'],9).value='I'
            audit.add('Rainfall',st['row'],st['id'],'rain',round(value,2),'in',b,url,interval_start=a,raw_value=value,details=detail)
            audit.entries[-1]['accumulation_kind']='provider_derived_interval_total'
            audit.entries[-1]['reports']=records
        qc.append(['Rainfall',st['id'],st['network'],status,detail,url or PRECIP_URL]);counts['synoptic_rain_'+status]+=1
