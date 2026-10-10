"""Review metadata derived from the same values used by the official tables."""
import csv
import json
from pathlib import Path
from common import inventory, finite, timestamp, observation_now, elapsed_window

FILES=['marine_summary_review.json','marine_summary_review.csv','observation_coverage_review.json','rainfall_archive_review.json','rainfall_archive_review.csv']

def marine(wb):
    s=wb['Wind and Pressure'];records=[]
    metadata=json.loads(Path(__file__).with_name('marine_station_metadata.json').read_text())
    for st in inventory(wb,'Wind and Pressure'):
        r=st['row']
        if str(s.cell(r,7).value or '').strip().upper()!='M':continue
        height=finite(s.cell(r,9).value,0,1000);period=finite(s.cell(r,10).value,0,60)
        rec=dict(st,height_m=height,averaging_minutes=period,height_basis='existing station template; event-specific metadata review required',
                 sustained_kn=finite(s.cell(r,11).value,0,200),gust_kn=finite(s.cell(r,17).value,0,200),human_review=True)
        rec['official_height_evidence']=metadata.get(st['id'])
        if rec['official_height_evidence']:rec['height_basis']+='; '+rec['official_height_evidence']['source']+'; '+rec['official_height_evidence']['applies_to']
        for variable,key in [('wind','sustained_kn'),('gust','gust_kn')]:
            value=rec[key]
            reason=('Anemometer height unresolved; review required' if height is None else
                    'Anemometer height >=20 m; excluded by Summary footnote' if height>=20 else
                    'No qualified '+variable+' measurement; source availability/collector QC in station QC' if value is None else
                    'Sustained averaging period unresolved/incompatible' if variable=='wind' and period not in (1,2,8,10) else '')
            rec[variable+'_eligible']=not reason;rec[variable+'_reason']=reason or 'Eligible marine workbook value; height below 20 m'
        records.append(rec)
    for variable,key in [('wind','sustained_kn'),('gust','gust_kn')]:
        ordered=sorted([r for r in records if r[variable+'_eligible']],key=lambda r:(-r[key],r['id'],r['row']))
        seen=set();rank=0
        for r in ordered:
            identity=(r['id'],r['url'])
            if identity in seen:r[variable+'_eligible']=False;r[variable+'_reason']='Duplicate exact observing source';continue
            seen.add(identity);rank+=1;r[variable+'_rank']=rank if rank<=10 else None
    return records

def interval_coverage(intervals,start,end,as_of):
    """Coverage from actual disjoint reports; unfinished report periods are pending."""
    elapsed=elapsed_window(start,end,as_of)
    parsed=[]
    for r in intervals or []:
        a,b=timestamp(r.get('start')),timestamp(r.get('end'))
        if a and b and start<=a<b<=elapsed:parsed.append((a,b))
    if not parsed:return {'coverage_known':False,'reason':'Source reporting cadence/intervals unresolved; no missing count inferred'}
    parsed=sorted(set(parsed))
    if any(a<previous_b for (_,previous_b),(a,_) in zip(parsed,parsed[1:])):
        raise ValueError('Overlapping rain provenance intervals')
    durations={(b-a).total_seconds() for a,b in parsed};cadence=next(iter(durations)) if len(durations)==1 else None
    due=int((elapsed-start).total_seconds()//cadence) if cadence else None
    aligned=cadence and all((a-start).total_seconds()%cadence==0 for a,b in parsed)
    observed={(a-start).total_seconds()/cadence for a,b in parsed} if aligned else set()
    return dict(coverage_known=True,observed_hours=sum((b-a).total_seconds()/3600 for a,b in parsed),
                elapsed_hours=(elapsed-start).total_seconds()/3600,report_interval_seconds=cadence,
                missing_due_report_count=len(set(range(due))-observed) if aligned else None,
                pending_elapsed_hours=((elapsed-start).total_seconds()%cadence)/3600 if aligned else None,
                future_hours=(end-elapsed).total_seconds()/3600,
                basis='Actual reported interval lengths; pending interval is not a missing report; irregular/off-grid cadence requires review')

def write(wb,audit,start,end,rain_start,rain_end,directory):
    directory=Path(directory);records=marine(wb)
    (directory/FILES[0]).write_text(json.dumps(records,indent=2)+'\n')
    keys=['id','name','network','height_m','averaging_minutes','sustained_kn','wind_rank','wind_reason','gust_kn','gust_rank','gust_reason','url','height_basis']
    with (directory/FILES[1]).open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(records)
    now=observation_now();coverage=[]
    for e in audit.entries:
        a,b=(rain_start,rain_end) if e['variable']=='rain' else (start,end)
        provisional=now<b
        e['requested_start_utc']=a.isoformat();e['requested_end_utc']=b.isoformat();e['as_of_utc']=now.isoformat();e['provisional']=provisional
        e['elapsed_end_utc']=elapsed_window(a,b,now).isoformat()
        if provisional and 'PROVISIONAL observed value:' not in e['details']:e['details']+='; PROVISIONAL observed value: requested event period has not ended; future reports are not missing'
        if e['variable']=='rain':e['interval_coverage']=interval_coverage(e.get('observed_intervals'),a,b,now)
        coverage.append(dict(site_id=e['site_id'],row=e['row'],tab=e['tab'],variable=e['variable'],value=e['value'],
            source_url=e['source_url'],requested_start_utc=a.isoformat(),requested_end_utc=b.isoformat(),
            elapsed_end_utc=e['elapsed_end_utc'],as_of_utc=now.isoformat(),provisional=provisional,
            interval_coverage=e.get('interval_coverage'),coverage_status='PARTIAL' if 'INCOMPLETE' in e['status'] else 'SOURCE COVERAGE REVIEW',
            qualification=e['details'],observed_intervals=e.get('observed_intervals'),
            interpretation='Observed accumulation only; not a complete storm total' if e['variable']=='rain' and ('INCOMPLETE' in e['status'] or provisional) else 'Measured observation; meteorologist review required'))
    (directory/FILES[2]).write_text(json.dumps(coverage,indent=2)+'\n')
    return records
