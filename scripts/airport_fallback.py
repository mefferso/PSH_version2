"""Exact-station Synoptic fallback for missing ASOS/AWOS fields.

The primary IEM/NOAA observations always retain precedence. Only independently
unit-qualified, source-reported values fill blank cells; no altimeter-to-MSLP
inference or nearby-station substitution.
"""
import os
import requests
from common import bounds, finite, inventory, public_url, timestamp
from synoptic import URL, parse
from iem import write_wind

def station_id(site):
    value=str(site).upper()
    return value if len(value)==4 and value.startswith('K') else 'K'+value if len(value)==3 else value

def populate(wb,qc,start,end,counts,audit):
    sheet=wb['Wind and Pressure']
    stations=[st for st in inventory(wb,'Wind and Pressure')
              if st['network'].upper() in ('ASOS','AWOS')
              and (any(sheet.cell(st['row'],col).value is None for col in (11,17,23))
                   or (sheet.cell(st['row'],11).value is not None and sheet.cell(st['row'],12).value is None))]
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
            # A direction-only recovery must describe the same *selected*
            # peak observation. A direction from another hour is not valid.
            direction_status='not needed'
            if sheet.cell(r,11).value is not None and sheet.cell(r,12).value is None:
                original=next((x for x in audit.entries if x['tab']=='Wind and Pressure'
                               and x['row']==r and x['variable']=='wind'),None)
                peak_time=timestamp(original.get('time_utc')) if original else None
                peak_speed=finite(sheet.cell(r,11).value)
                matches=[x for x in rows if peak_time is not None and x['time']==peak_time
                         and x.get('dir') is not None and x.get('wind') is not None
                         and peak_speed is not None and abs(x['wind']-peak_speed)<=0.15]
                directions={round(x['dir']) for x in matches}
                if len(directions)==1:
                    direction=next(iter(directions))
                    sheet.cell(r,12).value=direction
                    original['direction_source']='Synoptic exact-timestamp matched wind direction'
                    original['direction_source_url']=public_url(response.url)
                    original['direction_original_value']=direction
                    counts['synoptic_airport_peak_directions_recovered']+=1
                    direction_status='recovered exact timestamp and speed'
                    status='REVIEW REQUIRED'
                else:
                    direction_status='withheld: no unique exact-time speed-matched direction'
            detail=(f'Exact station {sid}; {len(rows)} time-indexed source rows; '
                    f'originally missing: {sorted(missing)}; recovered: {sorted(eligible)}; '
                    f'peak direction: {direction_status}; '
                    'wind requires documented averaging period; pressure requires direct sea_level_pressure; '
                    'no inferred or neighboring values.')
            qc.append(['Wind and Pressure',st['id'],st['network'],status,detail,public_url(response.url)])
        except (requests.RequestException,ValueError,KeyError,TypeError) as exc:
            qc.append(['Wind and Pressure',st['id'],st['network'],'ERROR',
                       'Optional Synoptic fallback failed ('+type(exc).__name__+'); token omitted',URL])
            counts['synoptic_airport_errors']+=1


def write_inventory_audit(wb,output_dir):
    """List source candidates and remaining fields; no coverage claims without requests."""
    import csv
    from pathlib import Path
    path=Path(output_dir)/'Synoptic_inventory_review.csv'
    path.parent.mkdir(parents=True,exist_ok=True)
    fields=['tab','station_id','network','source_station_id','eligible_for_synoptic',
            'wind_missing','wind_direction_missing','gust_missing','gust_direction_missing',
            'mslp_missing','rain_missing','notes']
    with path.open('w',newline='',encoding='utf-8') as handle:
        writer=csv.DictWriter(handle,fieldnames=fields);writer.writeheader()
        for st in inventory(wb,'Wind and Pressure'):
            s=wb['Wind and Pressure'];r=st['row'];network=st['network'].upper()
            eligible=network in ('ASOS','AWOS','CWOP','RAWS')
            writer.writerow({'tab':'Wind and Pressure','station_id':st['id'],
                'network':st['network'],'source_station_id':station_id(st['id']) if network in ('ASOS','AWOS') else st['id'],
                'eligible_for_synoptic':'candidate' if eligible else 'not configured',
                'wind_missing':s.cell(r,11).value is None,
                'wind_direction_missing':s.cell(r,12).value is None,
                'gust_missing':s.cell(r,17).value is None,
                'gust_direction_missing':s.cell(r,18).value is None,
                'mslp_missing':s.cell(r,23).value is None,'rain_missing':'',
                'notes':('Airport fallback queried for blank wind/gust/MSLP or peak direction'
                         if network in ('ASOS','AWOS') else
                         'CWOP/RAWS time-series collector already active' if network in ('CWOP','RAWS') else
                         'No Synoptic wind mapping verified')})
        for st in inventory(wb,'Rainfall'):
            s=wb['Rainfall'];network=st['network'].upper()
            eligible=network in ('ASOS','AWOS','COOP','HADS','RAWS')
            writer.writerow({'tab':'Rainfall','station_id':st['id'],'network':st['network'],
                'source_station_id':station_id(st['id']) if network in ('ASOS','AWOS') else st['id'],
                'eligible_for_synoptic':'candidate' if eligible else 'not configured',
                'wind_missing':'','wind_direction_missing':'','gust_missing':'',
                'gust_direction_missing':'','mslp_missing':'',
                'rain_missing':s.cell(st['row'],8).value is None,
                'notes':'Synoptic precipitation collector already active' if eligible else 'No Synoptic rain mapping verified'})
    return path
