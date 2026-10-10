"""Exact-station Synoptic fallback for missing ASOS/AWOS fields.

The primary IEM/NOAA observations always retain precedence. Only independently
unit-qualified, source-reported values fill blank cells; no altimeter-to-MSLP
inference or nearby-station substitution.
"""
import os
import requests
from common import bounds, finite, inventory, public_url
from synoptic import URL, parse
from iem import write_wind

def station_id(site):
    value=str(site).upper()
    return value if len(value)==4 and value.startswith('K') else 'K'+value if len(value)==3 else value

def populate(wb,qc,start,end,counts,audit):
    sheet=wb['Wind and Pressure']
    stations=[st for st in inventory(wb,'Wind and Pressure')
              if st['network'].upper() in ('ASOS','AWOS')
              and any(sheet.cell(st['row'],col).value is None for col in (11,17,23))]
    token=os.environ.get('SYNOPTIC_TOKEN')
    if not token:
        for st in stations:
            qc.append(['Wind and Pressure',st['id'],st['network'],'CREDENTIAL REQUIRED',
                       'Optional exact-station Synoptic missing-field fallback requires SYNOPTIC_TOKEN',URL])
        return
    a,b=bounds(start,end)
    for st in stations:
        r=st['row'];sid=station_id(st['id'])
        missing={field for field,col in (('wind',11),('gust',17),('pressure',23))
                 if sheet.cell(r,col).value is None}
        try:
            response=requests.get(URL,params={
                'token':token,'stid':sid,'start':a.strftime('%Y%m%d%H%M'),
                'end':b.strftime('%Y%m%d%H%M'),
                'vars':'wind_speed,wind_gust,wind_direction,sea_level_pressure',
                'sensorvars':1,'complete':1,'hfmetars':1,'obtimezone':'utc'
            },timeout=25)
            response.raise_for_status()
            payload=response.json()
            # Parsing enforces exact STID, explicit units, unique sensor
            # series and an explicitly documented wind averaging period.
            rows=parse(payload,sid,start,end,network=st['network'])
            found=[dict(x) for x in rows]
            for item in found:
                for field in ('wind','gust','pressure'):
                    if field not in missing:item[field]=None
            eligible={field for field in missing if any(x.get(field) is not None for x in found)}
            if eligible:
                n=write_wind(sheet,r,found,st['id'],audit,public_url(response.url),
                    'Synoptic exact-ICAO alternate archive; explicit unit/sensor metadata; '
                    'only missing PSH fields populated; no altimeter or station-pressure conversion')
                for entry in audit.entries:
                    if entry['tab']=='Wind and Pressure' and entry['row']==r and entry['variable'] in eligible:
                        entry['source_kind']='Synoptic station timeseries missing-field fallback'
                        entry['source_station_id']=sid
                        entry['validation']='Exact ICAO, unique sensor series, explicit original unit'
                counts['synoptic_airport_fields_recovered']+=n
                status='REVIEW REQUIRED'
            else:
                status='METADATA REVIEW' if any(x.get('unqualified_wind') is not None for x in rows) else 'NO DATA'
            detail=(f'Exact station {sid}; {len(rows)} time-indexed source rows; '
                    f'originally missing: {sorted(missing)}; recovered: {sorted(eligible)}; '
                    'wind requires documented averaging period; pressure requires direct sea_level_pressure; '
                    'no inferred or neighboring values.')
            qc.append(['Wind and Pressure',st['id'],st['network'],status,detail,public_url(response.url)])
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            qc.append(['Wind and Pressure',st['id'],st['network'],'ERROR',
                       'Optional Synoptic fallback failed ('+type(exc).__name__+'); token omitted',URL])
            counts['synoptic_airport_errors']+=1
