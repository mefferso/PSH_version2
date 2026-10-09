"""Credential-gated exact-ID Synoptic/MesoWest archived wind and MSLP."""
import os
import requests
from common import inventory,finite,bounds,timestamp
from iem import write_wind

URL='https://api.synopticdata.com/v2/stations/timeseries'
FACTORS={'wind_speed':{'m/s':1.9438444924406,'knots':1,'kts':1},
         'wind_gust':{'m/s':1.9438444924406,'knots':1,'kts':1},
         'sea_level_pressure':{'Pa':0.01,'Pascals':0.01,'hPa':1,'mb':1}}

def parse(payload,station,start,end):
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
            directions=series('wind_direction')
            row['dir']=finite(directions[n],0,360) if n<len(directions) and units.get('wind_direction') in ('Degrees','degrees') else None
            rows.append(row)
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
            r.raise_for_status();rows=parse(r.json(),st['id'],start,end)
            n=write_wind(wb['Wind and Pressure'],st['row'],rows,st['id'],audit,r.url,'Synoptic exact-ID sensor; unit-qualified; MSLP only')
            from common import public_url
            qc.append(['Wind and Pressure',st['id'],st['network'],'REVIEW REQUIRED' if n else 'NO DATA',f'{len(rows)} samples; {n}/3 variables',public_url(r.url)])
            counts['synoptic_collected' if n else 'synoptic_no_data']+=1
        except (requests.RequestException,ValueError,KeyError,TypeError):
            # Requests exceptions can contain the credential-bearing URL.
            qc.append(['Wind and Pressure',st['id'],st['network'],'ERROR','Synoptic request/schema unsuccessful; token redacted',URL]);counts['synoptic_errors']+=1
