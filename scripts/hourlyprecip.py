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
from common import inventory,finite,interval_total,public_url

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
        if not start<=t<end:continue
        raw=finite(row.get('precip_in'),0,100)
        if raw is None:continue
        if raw==0.0001:trace_count+=1
        key=(t,t+dt.timedelta(hours=1))
        if key in intervals and intervals[key]!=raw:
            raise ValueError('Conflicting IEM hourly rainfall readings')
        intervals[key]=raw
    total=interval_total([(a,b,v) for (a,b),v in intervals.items()],start,end)
    return total,len(intervals),trace_count

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
        for network,body,url,error in responses:
            if error:findings.append(network+' '+error);continue
            try:total,count,traces=parse(body,sid,network,a,b)
            except (ValueError,TypeError) as exc:
                findings.append(network+' '+type(exc).__name__);continue
            if count:findings.append(f'{network}: {count} hourly reports, {traces} traces')
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
        elif len(qualified)>1:
            detail+='; ambiguous station in multiple networks; withheld'
            counts['iem_hourly_rain_ambiguous']+=1
        qc.append(['Rainfall',st['id'],st['network'],status,detail,
                   qualified[0][2] if len(qualified)==1 else URL])
        counts['iem_hourly_rain_'+status]+=1
