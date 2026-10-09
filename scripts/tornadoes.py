"""Confirmed NCEI Storm Events tornadoes explicitly associated with the storm.

Preliminary LSRs, date-only coincidences and unknown timezone records are withheld.
"""
import csv
import datetime as dt
import gzip
import io
import re
import requests
from common import UTC,bounds,finite

BASE='https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/'
STATES={'LOUISIANA':'LA','MISSISSIPPI':'MS'}

def parse(records,storm,start,end):
    a,b=bounds(start,end);name=re.sub(r'^(Hurricane|Tropical Storm|Tropical Depression)\s+','',storm,flags=re.I).strip();events=[]
    if len(name)<2:return []
    for x in records:
        if x.get('EVENT_TYPE')!='Tornado' or x.get('WFO')!='LIX':continue
        narrative=(x.get('EPISODE_NARRATIVE') or '')+' '+(x.get('EVENT_NARRATIVE') or '')
        if not re.search(r'\b'+re.escape(name)+r'\b',narrative,re.I):continue
        zone=re.fullmatch(r'[A-Z]{3}([+-]\d{1,2})',x.get('CZ_TIMEZONE',''))
        if not zone:continue
        try:
            t=dt.datetime.strptime(x['BEGIN_DATE_TIME'],'%d-%b-%y %H:%M:%S').replace(tzinfo=dt.timezone(dt.timedelta(hours=int(zone[1])))).astimezone(UTC)
        except (ValueError,KeyError):continue
        lat=finite(x.get('BEGIN_LAT'),-90,90);lon=finite(x.get('BEGIN_LON'),-180,180)
        if not a<=t<b or lat is None or lon is None or x.get('STATE') not in STATES:continue
        rating=x.get('TOR_F_SCALE','');rating=rating if re.fullmatch(r'EF[0-5]',rating) else None
        events.append({'id':x.get('EVENT_ID'),'time':t,'lat':lat,'lon':lon,'rating':rating,
                       'city':x.get('BEGIN_LOCATION'),'county':x.get('CZ_NAME'),'state':STATES[x['STATE']],
                       'narrative':narrative,'zone':x['CZ_TIMEZONE']})
    return list({x['id']:x for x in events if x['id']}.values())

def collect(storm,start,end,session=requests):
    r=session.get(BASE,timeout=20);r.raise_for_status();events=[];urls=[]
    for year in range(start.year,end.year+1):
        files=re.findall(r'StormEvents_details-ftp_v1\.0_d'+str(year)+r'_c\d{8}\.csv\.gz',r.text)
        if not files:raise ValueError('Confirmed NCEI annual archive not yet available for '+str(year))
        url=BASE+max(files);response=session.get(url,timeout=45);response.raise_for_status()
        records=csv.DictReader(io.StringIO(gzip.decompress(response.content).decode('utf-8-sig')))
        for event in parse(records,storm,start,end):event['url']=url;events.append(event)
        urls.append(url)
    return events,urls

def populate(wb,qc,start,end,counts,audit):
    import os
    s=wb['Tornadoes']
    try:
        events,urls=collect(os.environ['STORM_NAME'],start,end)
        slots=[r for r in range(2,s.max_row+1) if all(s.cell(r,c).value is None for c in range(1,12))]
        if len(events)>len(slots):raise ValueError('Template tornado capacity exceeded; no events written')
        for event,r in zip(events,slots):
            t=event['time'];values=[event['city'],event['lat'],event['lon'],event['county'],event['state'],
                t.strftime('%H%M'),t.day,t.month,t.year,event['rating'],'NCEI event '+event['id']+'; '+event['narrative']]
            for c,v in enumerate(values,1):s.cell(r,c).value=v
            audit.add('Tornadoes',r,event['id'],'tornado',1,'event',t,event['url'],details='Confirmed Storm Events; '+event['zone']+' converted to UTC; storm explicitly named in narrative')
        wb['Summary']['B11']=len(events) if events else None
        qc.append(['Tornadoes','','NCEI','REVIEW REQUIRED',f'{len(events)} confirmed records explicitly name storm; zero matched records does not establish no tornadoes',urls[0] if urls else BASE])
        counts['confirmed_tornado_records']=len(events)
    except (requests.RequestException,ValueError,KeyError,OSError,UnicodeError):
        wb['Summary']['B11']=None
        qc.append(['Tornadoes','','NCEI','UNAVAILABLE','Confirmed archive retrieval/schema unavailable; tornado count remains unknown',BASE]);counts['tornado_archive_unavailable']+=1
