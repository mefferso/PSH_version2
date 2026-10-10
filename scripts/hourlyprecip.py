"""IEM processed exact-station hourly precipitation for LA/MS ASOS and AWOS.

The archive provides the precipitation falling in each UTC-labelled hour.
Only a completely tiled requested period qualifies for the PSH rain cell.
"""
import csv
import datetime as dt
import io
from concurrent.futures import ThreadPoolExecutor
import requests
from cocorahs import rain_bounds
from common import inventory,finite,interval_total,public_url,observation_now,elapsed_window

URL='https://mesonet.agron.iastate.edu/cgi-bin/request/hourlyprecip.py'
NETWORKS=('LA_ASOS','MS_ASOS')

def parse(text,station,network,start,end):
    reader=csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or not {'station','network','valid','precip_in'}.issubset(reader.fieldnames):
        raise ValueError('IEM hourly precipitation schema missing')
    intervals={};trace_count=0
    for row in reader:
        if str(row.get('station','')).upper()!=station.upper():continue
        if row.get('network')!=network:continue
        try: t=dt.datetime.strptime(row['valid'],'%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc)
        except (TypeError,ValueError):continue
        if not start<=t<end or t+dt.timedelta(hours=1)>observation_now():continue
        raw=finite(row.get('precip_in'),0,100)
        if raw is None:continue
        if raw==0.0001:trace_count+=1
        key=(t,t+dt.timedelta(hours=1))
        if key in intervals and intervals[key]!=raw:
            raise ValueError('Conflicting IEM hourly rainfall readings')
        intervals[key]=raw
    total=interval_total([(a,b,v) for (a,b),v in intervals.items()],start,end)
    return total,len(intervals),trace_count

def coverage_details(text,station,network,start,end):
    """Report actual observed intervals and gaps without inventing zeros."""
    reader=csv.DictReader(io.StringIO(text));hours={}
    for row in reader:
        if str(row.get('station','')).upper()!=station.upper() or row.get('network')!=network:continue
        try:t=dt.datetime.strptime(row['valid'],'%Y-%m-%d %H:%M').replace(tzinfo=dt.timezone.utc)
        except (ValueError,KeyError,TypeError):continue
        if not start<=t<end or t+dt.timedelta(hours=1)>observation_now():continue
        v=finite(row.get('precip_in'),0,100)
        if v is None:continue
        if t in hours and hours[t]!=v:raise ValueError('Conflicting hourly values')
        hours[t]=v
    elapsed_end=elapsed_window(start,end)
    expected=int((elapsed_end-start).total_seconds()/3600)
    present=len(hours)
    missing=[(start+dt.timedelta(hours=i)).isoformat() for i in range(expected)
             if start+dt.timedelta(hours=i) not in hours]
    # Partial measured accumulation is a lower bound, never a 48h total.
    observed=sum(v for v in hours.values() if v!=0.0001)
    return {'observed_hours':present,'expected_hours':expected,
            'missing_hours_utc':missing,'observed_sum_inches':round(observed,2),
            'provisional':elapsed_end<end,'elapsed_end_utc':elapsed_end.isoformat(),
            'first_observed_utc':min(hours).isoformat() if hours else None,
            'last_observed_utc':(max(hours)+dt.timedelta(hours=1)).isoformat() if hours else None,
            'observed_intervals':[{'start':t.isoformat(),'end':(t+dt.timedelta(hours=1)).isoformat(),'inches':v} for t,v in sorted(hours.items())]}

def certify_dry_hour(metar_rows,start,end):
    """Prove an absent hour dry using overlapping zero-precip routine METARs.

    A METAR ending at t gives the preceding one-hour interval. Its value
    cannot be used for arbitrary calendar hours unless those intervals cover
    the entire missing hour. PNO and unknown sensor/report types are rejected.
    """
    coverage=[]
    for row in metar_rows:
        if row.get('report_type')!=3 or row.get('rain')!=0:continue
        raw=row.get('raw') or {}
        message=str(raw.get('metar') or '').upper()
        if 'PNO' in message.split() or not ('AO2' in message.split() or 'AO1' in message.split()):
            continue
        t=row['time']
        coverage.append((t-dt.timedelta(hours=1),t))
    cursor=start
    while cursor<end:
        candidates=[b for a,b in coverage if a<=cursor<b]
        if not candidates:return False
        cursor=max(candidates)
    return True

def recover_missing_dry_hours(text,station,network,start,end,metar_rows):
    """Add only independently certified zero-precip hours, never guessed rain."""
    info=coverage_details(text,station,network,start,end)
    if not info['missing_hours_utc']:return parse(text,station,network,start,end)[0],0
    certified=[]
    for iso in info['missing_hours_utc']:
        t=dt.datetime.fromisoformat(iso)
        if not certify_dry_hour(metar_rows,t,t+dt.timedelta(hours=1)):
            return None,0
        certified.append(t)
    appended=chr(10).join(f"{station},{network},{t:%Y-%m-%d %H:%M},0.0" for t in certified)
    total,_,_=parse(text.rstrip()+chr(10)+appended+chr(10),station,network,start,end)
    return total,len(certified)

def populate(wb,qc,start,end,counts,audit):
    a,b=rain_bounds(start,end);sheet=wb['Rainfall']
    stations=[x for x in inventory(wb,'Rainfall') if x['network'].upper() in ('ASOS','AWOS')
              and sheet.cell(x['row'],8).value is None]
    if not stations:return
    names=sorted({x['id'].upper().removeprefix('K') if len(x['id'])==4 and x['id'].upper().startswith('K')
                  else x['id'].upper() for x in stations})
    def fetch(network):
        try:
            r=requests.get(URL,params={'network':network,'station':','.join(names),
                'sts':a.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'ets':b.strftime('%Y-%m-%dT%H:%M:%SZ'),'tz':'Etc/UTC'},timeout=50)
            r.raise_for_status()
            return network,r.text,public_url(r.url),None
        except requests.RequestException as exc:return network,None,URL,type(exc).__name__
    with ThreadPoolExecutor(max_workers=2) as pool:responses=list(pool.map(fetch,NETWORKS))
    for st in stations:
        sid=st['id'].upper()
        if len(sid)==4 and sid.startswith('K'):sid=sid[1:]
        qualified=[]
        findings=[]
        available=[]
        for network,body,url,error in responses:
            if error:findings.append(network+' '+error);continue
            try:total,count,traces=parse(body,sid,network,a,b)
            except (ValueError,TypeError) as exc:
                findings.append(network+' '+type(exc).__name__);continue
            if count:
                details=coverage_details(body,sid,network,a,b)
                available.append((count,details['observed_sum_inches'],network,url,details))
                findings.append(f"{network}: {count}/{details['expected_hours']} hours, {traces} traces, reported-hours sum {details['observed_sum_inches']:.2f} in (INCOMPLETE where gaps exist); first missing UTC {details['missing_hours_utc'][:6]}")
            if total is None and count and details['missing_hours_utc']:
                try:
                    from iem import collect as metar_collect
                    metars,metar_url=metar_collect(sid,a.date(),b.date())
                    recovered,filled=recover_missing_dry_hours(body,sid,network,a,b,metars)
                    if recovered is not None:
                        total=recovered
                        findings.append(f'{network}: recovered {filled} provably dry missing hours from independent routine METAR p01i; no PNO; {public_url(metar_url)}')
                        counts['iem_hourly_dry_hours_certified']+=filled
                except (requests.RequestException,ValueError,TypeError):
                    findings.append(f'{network}: independent METAR dry-hour verification unavailable')
            if total is not None:qualified.append((network,total,url,count,traces))
        status='INCOMPLETE';detail='Processed IEM hourly precipitation; full continuous UTC hourly coverage required. '+ '; '.join(findings)
        if len(qualified)==1:
            network,value,url,count,traces=qualified[0]
            result=round(value,2)
            sheet.cell(st['row'],8).value=result;sheet.cell(st['row'],9).value='I'
            audit.add('Rainfall',st['row'],st['id'],'rain',result,'in',b,url,
                      interval_start=a,raw_value=value,details=detail+f'; qualified network {network}; trace sentinel 0.0001 in')
            counts['iem_hourly_rain_collected']+=1
            status='REVIEW REQUIRED'
        elif not qualified and len(available)==1:
            hours,amount,network,url,info=available[0]
            amount=round(amount,2)
            sheet.cell(st['row'],8).value=amount
            sheet.cell(st['row'],9).value='I'
            entry=audit.add('Rainfall',st['row'],st['id'],'rain',amount,'in',b,url,interval_start=a,status='INCOMPLETE',details=detail)
            entry['observed_intervals']=info['observed_intervals']
            entry['coverage']=info
            counts['iem_hourly_incomplete_populated']+=1
            status='INCOMPLETE — POPULATED'
        elif len(qualified)>1:
            detail+='; ambiguous station in multiple networks; withheld'
            counts['iem_hourly_rain_ambiguous']+=1
        qc.append(['Rainfall',st['id'],st['network'],status,detail,
                   qualified[0][2] if len(qualified)==1 else URL])
        counts['iem_hourly_rain_'+status]+=1
