"""NWS COOP daily rainfall from exact-station IEM historical observations.

Observation clocks are local for LA/MS. Only exact contiguous daily reports
covering the configured rain window qualify; all others remain review candidates.
"""
import csv
import datetime as dt
import io
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo
import requests
from cocorahs import rain_bounds,export_total,nearby_complete_total
from common import inventory,finite,public_url

URL='https://mesonet.agron.iastate.edu/cgi-bin/request/coopobs.py'
NETWORKS=('LA_COOP','MS_COOP')
ZONE=ZoneInfo('America/Chicago')
FIELDS=['station_id','report_type','period_start_utc','period_end_utc','reported_in',
        'requested_start_utc','requested_end_utc','classification','source_url']

def parse(text,station):
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {'nwsli','date','time','precip'}.issubset(reader.fieldnames):
        raise ValueError('COOP daily archive schema missing')
    records=[]
    for raw in reader:
        if str(raw.get('nwsli') or '').strip().upper()!=station.upper():continue
        when=str(raw.get('time') or '').strip()
        try:
            local=dt.datetime.strptime(str(raw['date'])+' '+when,'%Y-%m-%d %I %p').replace(tzinfo=ZONE)
            t=local.astimezone(dt.timezone.utc)
            prior=(local-dt.timedelta(days=1)).astimezone(dt.timezone.utc)
        except (ValueError,KeyError,TypeError):continue
        v=finite(raw.get('precip'),0,100)
        if v is None:continue
        records.append({'start':prior,'end':t,'value':v,'type':'IEM_COOP_daily',
                        'interval_basis':'Daily COOP reported observation date/time, America/Chicago; check observer reporting interval'})
    return records

def populate(wb,qc,start,end,counts,audit,output_dir=None):
    a,b=rain_bounds(start,end);sheet=wb['Rainfall']
    stations=[x for x in inventory(wb,'Rainfall') if x['network'].upper()=='COOP'
              and sheet.cell(x['row'],8).value is None]
    if not stations:return
    station_ids=','.join(sorted({x['id'].upper() for x in stations}))
    def fetch(network):
        try:
            r=requests.get(URL,params={'network':network,'stations':station_ids,
                'sts':(a-dt.timedelta(days=2)).date().isoformat(),
                'ets':(b+dt.timedelta(days=1)).date().isoformat(),'what':'view','delim':'comma'},timeout=50)
            r.raise_for_status();return network,r.text,public_url(r.url),None
        except requests.RequestException as exc:return network,None,URL,type(exc).__name__
    with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(fetch,NETWORKS))
    partial=[]
    for station in stations:
        candidates=[];qualified=[];issues=[]
        for network,body,url,error in responses:
            if error:issues.append(network+' '+error);continue
            try:records=parse(body,station['id'])
            except (ValueError,TypeError):issues.append(network+' schema error');continue
            if records:candidates.extend((record,url,network) for record in records)
            total=export_total(records,a,b)
            if total is not None:qualified.append((total,url,network,records))
        if not qualified and candidates:
            nearby=[(nearby_complete_total([r for r,u,n in candidates if n==network],a,b),network)
                    for network in NETWORKS]
            for item,network in nearby:
                if item:
                    amount,observed_start,observed_end=item
                    issues.append(f'NEARBY COMPLETE COOP WINDOW {network}: {amount:.2f} in {observed_start.isoformat()} to {observed_end.isoformat()} (REVIEW ONLY; not requested period)')
                    counts['iem_coop_nearby_complete_review']+=1
        detail='Exact IEM COOP daily reports with local observation times; no assumption of missing day precipitation. '+ '; '.join(issues)
        if len(qualified)==1:
            amount,url,network,records=qualified[0]
            value=round(amount,2)
            sheet.cell(station['row'],8).value=value;sheet.cell(station['row'],9).value='I'
            e=audit.add('Rainfall',station['row'],station['id'],'rain',value,'in',b,url,
                        interval_start=a,details=detail+'; complete daily reports from '+network)
            e['accumulation_kind']='sum_of_reported_COOP_daily'
            e['reports']=[dict(item,start=item['start'].isoformat(),end=item['end'].isoformat()) for item in records]
            counts['iem_coop_collected']+=1
            status='REVIEW REQUIRED'
        else:
            status='INTERVAL REVIEW' if candidates else 'NO REPORTS'
            if len(qualified)>1:status='AMBIGUOUS ID'
            for record,url,network in candidates:
                if not record['start']<b or not record['end']>a:continue
                partial.append({'station_id':station['id'],'report_type':'COOP '+network,
                    'period_start_utc':record['start'].isoformat(),
                    'period_end_utc':record['end'].isoformat(),'reported_in':record['value'],
                    'requested_start_utc':a.isoformat(),'requested_end_utc':b.isoformat(),
                    'classification':'PARTIAL REPORT — NOT A VERIFIED STORM TOTAL','source_url':url})
        qc.append(['Rainfall',station['id'],station['network'],status,
                   detail+f'; {len(candidates)} reported daily observations',qualified[0][1] if len(qualified)==1 else URL])
        counts['iem_coop_'+status]+=1
    if partial:
        path=(Path(output_dir) if output_dir is not None else Path('output'))/'Rainfall_partial_reports.csv'
        with path.open('a',newline='',encoding='utf-8') as handle:
            csv.DictWriter(handle,fieldnames=FIELDS).writerows(partial)
    counts['iem_coop_partial_reports']=len(partial)
