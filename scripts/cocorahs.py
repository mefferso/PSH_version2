"""Official historical daily rain: exact station, explicit UTC times and full intervals."""
import datetime as dt
import os
import re
import requests
from common import inventory,finite,timestamp,interval_total,bounds,public_url

URL='https://api2.cocorahs.org/api/DailyPrecipObs'

def canonical(sid):
    m=re.fullmatch(r'([A-Z]{2}-[A-Z]+)-0*(\d+)',str(sid).upper())
    return m.group(1)+'-'+str(int(m.group(2))) if m else str(sid).upper()

def rain_bounds(start,end):
    a,b=bounds(start,end)
    # Daily volunteer gauges commonly use morning observation boundaries.
    # Align default to 12 UTC; explicit user bounds always win.
    a+=dt.timedelta(hours=12);b+=dt.timedelta(hours=12)
    if os.environ.get('RAIN_START_UTC') or os.environ.get('RAIN_END_UTC'):
        a=timestamp(os.environ.get('RAIN_START_UTC'));b=timestamp(os.environ.get('RAIN_END_UTC'))
        if not a or not b or a>=b or b-a>dt.timedelta(days=36):raise ValueError('Invalid explicit rainfall UTC window')
    return a,b

def field(report,name):return report.get(name,report.get(name[0].upper()+name[1:]))

def total(reports,station,start,end):
    periods={}
    for report in reports:
        if canonical(field(report,'stationNumber'))!=canonical(station):continue
        t=timestamp(field(report,'obsDateTime'));days=finite(field(report,'numDays'),1,36)
        # No assumed local timezone or daily period for undocumented responses.
        if not t or days is None:continue
        a=t-dt.timedelta(days=days)
        if a<start or t>end:continue
        value=finite(field(report,'gaugeCatch'),0,30)
        if field(report,'gaugeCatchIsTrace') or field(report,'precipIsTrace'):value=None
        key=(a,t)
        if key in periods and periods[key]!=value:return None
        periods[key]=value
    return interval_total([(a,b,v) for (a,b),v in periods.items()],start,end)

def collect_station(station,start,end,session=requests):
    reports=[];urls=[];offset=0
    for page in range(100):
        params={'offset':offset,'limit':250,'startDate':(start-dt.timedelta(days=1)).date().isoformat(),
            'endDate':(end+dt.timedelta(days=1)).date().isoformat(),'sortField':'ObsDateTime','sortDir':'asc',
            'stationField':'StationNumber','stationFieldValue':canonical(station),'units':'english'}
        r=session.get(URL,params=params,timeout=20);r.raise_for_status();data=r.json();urls.append(r.url)
        if not isinstance(data.get('results'),list):raise ValueError('CoCoRaHS unexpected results schema')
        results=data['results']
        if not results:break
        reports.extend(results);offset+=len(results)
        count=finite(((data.get('metadata') or {}).get('resultset') or {}).get('totalCount'),0,20000)
        if count is not None and offset>=count:break
    else:raise ValueError('CoCoRaHS incomplete pagination; series discarded')
    return reports,urls

# The official export explicitly supports TimesInGMT. API2's obsDateTime
# has a +00:00 suffix on local clock values; it is NOT used for this adapter.
EXPORT_URL='https://data.cocorahs.org/cocorahs/export/exportreports.aspx'
CONVENTION='https://www.cocorahs.org/Content.aspx?page=welcometococorahs'

def parse_daily_export(text,station):
    """Official Daily, English-unit export requested with TimesInGMT=True.

    Daily report type establishes daily accumulation, not multiday. For LA/MS
    inventory stations the prior local calendar day establishes the normal
    start boundary, with DST handled by ZoneInfo. Changed/irregular observation
    times remain review candidates rather than being stretched to match a window.
    """
    import csv,io
    from zoneinfo import ZoneInfo
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {'ObservationDate','ObservationTime','StationNumber','TotalPrecipAmt'}.issubset(reader.fieldnames):
        raise ValueError('Official daily CSV schema missing')
    if not canonical(station).startswith(('LA-','MS-')):raise ValueError('Station timezone not established')
    zone=ZoneInfo('America/Chicago');records=[]
    for raw in reader:
        raw={k:(v or '').strip() for k,v in raw.items() if k}
        if canonical(raw.get('StationNumber'))!=canonical(station):continue
        try:t=dt.datetime.strptime(raw['ObservationDate']+' '+raw['ObservationTime'],'%Y-%m-%d %I:%M %p').replace(tzinfo=dt.timezone.utc)
        except ValueError:continue
        local=t.astimezone(zone);a=(local-dt.timedelta(days=1)).astimezone(dt.timezone.utc)
        v=finite(raw.get('TotalPrecipAmt'),0,100)
        records.append({'start':a,'end':t,'value':v,'reported_amount':raw['TotalPrecipAmt'],
                        'type':'daily','interval_basis':'Official Daily report type; previous local calendar day at reported observation clock; '+CONVENTION})
    return records

def export_total(records,start,end):
    """Choose a complete nonoverlapping tiling; contradictory paths withheld."""
    periods={}
    for x in records:
        a,b=x['start'],x['end']
        if a is None or b is None or a<start or b>end:continue
        key=(a,b);v=x['value']
        if key in periods and periods[key]!=v:return None
        periods[key]=v
    # Reports need not all be used (e.g. redundant multiday vs daily observations).
    # Never add overlapping totals; require all available complete paths to agree.
    paths=[]
    def visit(cursor,value,depth):
        if depth>36:return
        if cursor==end:paths.append(value);return
        for (a,b),v in periods.items():
            if a==cursor and b>a and v is not None:visit(b,value+v,depth+1)
    visit(start,0.,0)
    if not paths or max(paths)-min(paths)>.005:return None
    return paths[0]

def observed_partial_sum(records,start,end):
    """Best nonoverlapping observed accumulation subset wholly inside window.

    Prioritize covered time, not rainfall magnitude. Never split a daily
    measurement at storm boundaries or sum parallel overlapping reports.
    """
    values={}
    for r in records:
        a,b,v=r.get('start'),r.get('end'),r.get('value')
        if a is None or b is None or v is None or not start<=a<b<=end:continue
        key=(a,b)
        if key in values and abs(values[key]-v)>.005:return None
        values[key]=v
    times=sorted({t for pair in values for t in pair})
    if not times:return None
    best={t:(0,0.0,[]) for t in times}
    for index,t in enumerate(times):
        if index and best[times[index-1]][0]>best[t][0]:
            best[t]=best[times[index-1]]
        for (a,b),v in values.items():
            if a!=t:continue
            current=best[a];candidate=(current[0]+(b-a).total_seconds(),current[1]+v,current[2]+[(a,b,v)])
            if candidate[0]>best[b][0]:best[b]=candidate
    covered,total,used=best[times[-1]]
    return (total,covered/3600,used) if used else None

def nearby_complete_total(records,start,end,tolerance_hours=2):
    """Find an independently continuous station window near requested bounds.

    This is a review candidate, NOT an exact storm-period total.
    """
    tolerance=dt.timedelta(hours=tolerance_hours)
    starts={r['start'] for r in records if r.get('start') is not None}
    ends={r['end'] for r in records if r.get('end') is not None}
    matches=[]
    for a in starts:
        if abs(a-start)>tolerance:continue
        for b in ends:
            if abs(b-end)>tolerance or b<=a:continue
            amount=export_total(records,a,b)
            if amount is not None:matches.append((abs(a-start)+abs(b-end),amount,a,b))
    if not matches:return None
    matches.sort(key=lambda item:item[0])
    best=matches[0]
    if any(item[0]==best[0] and abs(item[1]-best[1])>.005 for item in matches):
        return None
    return best[1:]

def parse_multiday_export(text,station,daily):
    """Inclusive reporting dates, actual prior daily endpoint when available.

    A multiday start DATE lacks a start clock. Only an existing daily observation
    on the immediately preceding reporting date establishes that boundary here.
    Otherwise retain the amount/end/date in QC without inventing a start time.
    """
    import csv,io
    from zoneinfo import ZoneInfo
    reader=csv.DictReader(io.StringIO(text));zone=ZoneInfo('America/Chicago');records=[]
    if not reader.fieldnames or not {'StartDate','EndDateTime','StationNumber','TotalPrecipAmt'}.issubset(reader.fieldnames):
        raise ValueError('Official multiday CSV schema missing')
    for raw in reader:
        raw={k:(v or '').strip() for k,v in raw.items() if k}
        if canonical(raw.get('StationNumber'))!=canonical(station):continue
        try:
            date=dt.date.fromisoformat(raw['StartDate'])
            b=dt.datetime.strptime(raw['EndDateTime'],'%Y-%m-%d %I:%M %p').replace(tzinfo=dt.timezone.utc)
        except ValueError:continue
        prior={x['end'] for x in daily if x['end'].astimezone(zone).date()==date-dt.timedelta(days=1)}
        a=next(iter(prior)) if len(prior)==1 else None
        records.append({'start':a,'end':b,'value':finite(raw['TotalPrecipAmt'],0,100),
            'reported_start_date':raw['StartDate'],'reported_amount':raw['TotalPrecipAmt'],'type':'multiday',
            'interval_basis':'Inclusive reporting dates; start established by prior daily observation, otherwise unknown. https://media.cocorahs.org/docs/CoCoRaHS_MobileApp_User_Guide.pdf'})
    return records

def collect_export(station,start,end,session=requests):
    r=session.get(EXPORT_URL,params={'ReportType':'Daily','Station':canonical(station),
        'StartDate':(start-dt.timedelta(days=1)).strftime('%m/%d/%Y'),
        'EndDate':(end+dt.timedelta(days=1)).strftime('%m/%d/%Y'),'Format':'CSV','TimesInGMT':'True'},timeout=25)
    r.raise_for_status();records=parse_daily_export(r.text,station)
    urls=[r.url]
    if export_total(records,start,end) is None:
        try:
            params=dict(ReportType='MultiDay',Station=canonical(station),StartDate=(start-dt.timedelta(days=2)).strftime('%m/%d/%Y'),
                        EndDate=(end+dt.timedelta(days=1)).strftime('%m/%d/%Y'),Format='CSV',TimesInGMT='True')
            m=session.get(EXPORT_URL,params=params,timeout=25);m.raise_for_status()
            records.extend(parse_multiday_export(m.text,station,records));urls.append(m.url)
        except (requests.RequestException,ValueError):
            # Preserve usable daily reports even when the alternate fails.
            records.append({'start':None,'end':end,'value':None,'type':'multiday_request_error','interval_basis':'Alternate official multiday request/schema failed','reported_amount':None})
    return records,urls[0]

# Keep the explicit-metadata JSON parser available for fixtures and other clients;
# production historical recovery uses the official GMT export contract.
def populate(wb,qc,start,end,counts,audit,output_dir=None):
    import json,csv
    from pathlib import Path
    from concurrent.futures import ThreadPoolExecutor
    a,b=rain_bounds(start,end);sheet=wb['Rainfall']
    stations=[st for st in inventory(wb,'Rainfall') if st['network']=='CoCoRaHS']
    def fetch(st):
        try:return st,collect_export(st['id'],a,b),None
        except (requests.RequestException,ValueError,TypeError) as e:return st,None,type(e).__name__
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(fetch,stations))
    partial=[]
    for st,data,error in results:
        value=None;url=EXPORT_URL;records=[]
        if data:
            records,url=data;value=export_total(records,a,b)
        candidates=[dict(x,start=x['start'].isoformat() if x['start'] else None,end=x['end'].isoformat()) for x in records if x['end']>a and (x['start'] is None or x['start']<b)]
        detail='Official English Daily CSV with TimesInGMT=True; exact station; daily report convention and local calendar boundary. '+CONVENTION
        if value is not None:
            value=round(value,2);sheet.cell(st['row'],8).value=value;sheet.cell(st['row'],9).value='I'
            e=audit.add('Rainfall',st['row'],st['id'],'rain',value,'in',b,url,interval_start=a,details=detail)
            e['accumulation_kind']='sum_of_reported_daily_accumulations';e['reports']=candidates
        status='REVIEW REQUIRED' if value is not None else 'INTERVAL REVIEW' if candidates else 'ERROR' if error else 'NO REPORTS'
        if value is None and records:
            partial_sum=observed_partial_sum(records,a,b)
            if partial_sum and sheet.cell(st['row'],8).value is None:
                amount,hours,used=partial_sum
                amount=round(amount,2)
                sheet.cell(st['row'],8).value=amount;sheet.cell(st['row'],9).value='I'
                e=audit.add('Rainfall',st['row'],st['id'],'rain',amount,'in',b,url,
                    interval_start=a,status='INCOMPLETE',details=f'Observed subset {hours:.1f}/{(b-a).total_seconds()/3600:.1f} hours; missing time NOT estimated; '+detail)
                e['observed_intervals']=[{'start':x.isoformat(),'end':y.isoformat(),'inches':v} for x,y,v in used]
                counts['cocorahs_incomplete_populated']+=1
            nearby=nearby_complete_total(records,a,b)
            if nearby:
                amount,obs_start,obs_end=nearby
                detail+=f'; NEARBY COMPLETE GAUGE WINDOW (review only): {amount:.2f} inches from {obs_start.isoformat()} through {obs_end.isoformat()}, NOT exact requested storm total'
                counts['cocorahs_nearby_complete_review']+=1
                if sheet.cell(st['row'],8).value is None:
                    observed_value=round(amount,2)
                    sheet.cell(st['row'],8).value=observed_value
                    sheet.cell(st['row'],9).value='I'
                    entry=audit.add('Rainfall',st['row'],st['id'],'rain',observed_value,'in',b,url,
                        interval_start=a,status='INCOMPLETE',
                        details=detail+'; actual observation window differs from requested window')
                    entry['actual_interval_start_utc']=obs_start.isoformat()
                    entry['actual_interval_end_utc']=obs_end.isoformat()
                    entry['reporting_window_mismatch']=True
                    counts['cocorahs_shifted_window_populated']+=1
        if value is None:detail+='; no complete tiling of requested window; available reports retained for review. '+json.dumps(candidates,allow_nan=False)
        if value is None:
            for record in records:
                if record.get('value') is None or record.get('end') is None:continue
                first=record.get('start');last=record['end']
                if last<=a or (first is not None and first>=b):continue
                partial.append({'station_id':st['id'],'report_type':record['type'],
                    'period_start_utc':first.isoformat() if first else '',
                    'period_end_utc':last.isoformat(),'reported_in':record['value'],
                    'requested_start_utc':a.isoformat(),'requested_end_utc':b.isoformat(),
                    'classification':'PARTIAL REPORT — NOT A VERIFIED STORM TOTAL',
                    'source_url':public_url(url)})
        if value is None and sheet.cell(st['row'],8).value is not None:
            status='INCOMPLETE — POPULATED'
        if error:detail+='; request/schema failure '+error+'; not evidence of absent historical observations'
        qc.append(['Rainfall',st['id'],st['network'],status,detail,public_url(url)]);counts['cocorahs_'+status]+=1

    # Separate observed daily/multiday rain from qualified storm totals.
    # Deliberately no arithmetic sum across partial/overlapping intervals.
    target=(Path(output_dir) if output_dir is not None else Path('output'))/'Rainfall_partial_reports.csv'
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('a',newline='',encoding='utf-8') as fh:
        fields=['station_id','report_type','period_start_utc','period_end_utc','reported_in',
                'requested_start_utc','requested_end_utc','classification','source_url']
        writer=csv.DictWriter(fh,fieldnames=fields);writer.writerows(partial)
    counts['cocorahs_partial_reports']=len(partial)
