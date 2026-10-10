"""Exact-station IEM HADS/SHEF daily precipitation recovery.

Only SHEF PPD (24-hour precipitation) reports with UTC endpoints and a
complete contiguous requested accumulation window can populate PSH.
Other reported variables (including cumulative PC and hourly PPH) are
not interpreted as event totals. All partial series remain QC context.
"""
import csv
import datetime as dt
import io
from concurrent.futures import ThreadPoolExecutor
import requests
from common import inventory, finite, timestamp, public_url
from cocorahs import rain_bounds, export_total

URL='https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py'
DOC='https://mesonet.agron.iastate.edu/cgi-bin/request/hads.py?help='

def parse(text, station):
    reader=csv.DictReader(io.StringIO(text))
    fields=reader.fieldnames or []
    station_key=next((x for x in fields if x.strip().lower() in ('station','site','stid')),None)
    time_key=next((x for x in fields if x.strip().lower() in ('valid','valid[utc]','utc','timestamp')),None)
    if not station_key or not time_key:raise ValueError('SHEF archive station/UTC columns missing')
    # IEM exposes raw SHEF variable names. Third character D specifies a
    # daily duration. Exact variable identity is retained in provenance.
    precip_keys=[x for x in fields if x.upper().startswith('PPD') and len(x)>=6]
    records=[]
    for row in reader:
        if str(row.get(station_key,'')).strip().upper()!=station.upper():continue
        t=timestamp(str(row.get(time_key,'')).strip())
        if t is None:
            try:t=dt.datetime.strptime(str(row.get(time_key,'')).strip(),'%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc)
            except ValueError:continue
        for key in precip_keys:
            v=finite(row.get(key),0,100)
            if v is None:continue
            records.append({'start':t-dt.timedelta(days=1),'end':t,'value':v,
                'type':'SHEF_'+key,'interval_basis':'IEM UTC valid time, SHEF PPD 24-hour duration'})
    return records

def populate(wb,qc,start,end,counts,audit):
    a,b=rain_bounds(start,end);sheet=wb['Rainfall']
    stations=[st for st in inventory(wb,'Rainfall') if st['network'].upper() in ('HADS','COOP') and sheet.cell(st['row'],8).value is None]
    def fetch(st):
        try:
            response=requests.get(URL,params={'stations':st['id'],'sts':(a-dt.timedelta(days=1)).strftime('%Y-%m-%dT%H:%MZ'),
                'ets':(b+dt.timedelta(days=1)).strftime('%Y-%m-%dT%H:%MZ'),'what':'txt','delim':'comma'},timeout=35)
            response.raise_for_status()
            return st,parse(response.text,st['id']),public_url(response.url),None
        except (requests.RequestException,ValueError,TypeError) as e:
            return st,[],URL,type(e).__name__
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(fetch,stations))
    for st,records,url,error in results:
        # Different SHEF source codes are not interchangeable; do not
        # double-count parallel radio/observer feeds for a station.
        series={}
        for item in records:series.setdefault(item['type'],[]).append(item)
        totals={key:export_total(items,a,b) for key,items in series.items()}
        qualified={key:v for key,v in totals.items() if v is not None}
        value=next(iter(qualified.values())) if len(qualified)==1 else None
        if len(qualified)>1 and max(qualified.values())-min(qualified.values())<=.005:
            value=next(iter(qualified.values()))
        detail='Exact-ID IEM HADS SHEF PPD 24-hour UTC reports; '+DOC
        detail+=f'; {len(records)} valid daily readings; {len(qualified)} complete source-code series'
        if error:detail+='; archive/schema request failed: '+error
        if value is not None:
            sheet.cell(st['row'],8).value=round(value,2)
            sheet.cell(st['row'],9).value='I'
            used=next(k for k,v in qualified.items() if abs(v-value)<=.005)
            entry=audit.add('Rainfall',st['row'],st['id'],'rain',round(value,2),'in',b,url,
                interval_start=a,details=detail+'; qualified SHEF code '+used)
            entry['accumulation_kind']='sum_of_SHEF_PPD_24h'
            entry['reports']=[dict(item,start=item['start'].isoformat(),end=item['end'].isoformat()) for item in series[used]]
        status='REVIEW REQUIRED' if value is not None else 'ERROR' if error else 'INTERVAL REVIEW' if records else 'NO REPORTS'
        qc.append(['Rainfall',st['id'],st['network'],status,detail,url]);counts['hads_'+status]+=1
