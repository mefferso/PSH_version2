"""Exact-inventory numerical comparison; missing readings are never accuracy passes."""
import argparse
import json
from pathlib import Path
from collections import defaultdict
from openpyxl import load_workbook
from common import inventory,finite

FIELDS={'Wind and Pressure':[('wind',11,1.0),('gust',17,1.0),('pressure',23,.5)],
        'Rainfall':[('rain',8,.12)],'Water Level':[('water',7,.15)]}

def compare(generated,reference):
    observations=[];counts={'compared':0,'within_tolerance':0,'discrepancies':0,'missing':0,'ambiguous':0}
    for tab,fields in FIELDS.items():
        index=defaultdict(list)
        for st in inventory(generated,tab):index[st['id']].append(st)
        refs=list(inventory(reference,tab));refcounts=defaultdict(int)
        for st in refs:refcounts[st['id']]+=1
        for st in refs:
            for variable,col,tolerance in fields:
                expected=finite(reference[tab].cell(st['row'],col).value)
                if expected is None:continue
                candidates=index[st['id']];actual=None;delta=None
                if len(candidates)>1 or refcounts[st['id']]>1:status='AMBIGUOUS';counts['ambiguous']+=1
                else:
                    if candidates:actual=finite(generated[tab].cell(candidates[0]['row'],col).value)
                    if actual is None:status='MISSING';counts['missing']+=1
                    elif variable=='water' and generated[tab].cell(candidates[0]['row'],8).value!=reference[tab].cell(st['row'],8).value:
                        status='DATUM MISMATCH';counts['discrepancies']+=1
                    else:
                        delta=actual-expected;counts['compared']+=1
                        status='WITHIN TOLERANCE' if abs(delta)<=tolerance else 'DISCREPANCY'
                        counts['within_tolerance' if status=='WITHIN TOLERANCE' else 'discrepancies']+=1
                observations.append({'tab':tab,'site_id':st['id'],'variable':variable,'reference':expected,
                    'generated':actual,'difference':delta,'tolerance':tolerance,'status':status,'reference_url':st['url']})
    counts['agreement']=counts['within_tolerance']/counts['compared'] if counts['compared'] else None
    return dict(counts,observations=observations)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('workbook');p.add_argument('--reference',default='tests/fixtures/PSHLIX_2024AL06_Francine_Data.xlsx');p.add_argument('--output',default='output/Francine-regression.json');a=p.parse_args()
    result=compare(load_workbook(a.workbook,data_only=True),load_workbook(a.reference,data_only=True))
    Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='observations'},indent=2))
