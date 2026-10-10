"""Manifest-selected workbook, all PSH tabs, measurement audit and review downloads."""
import datetime as dt
import json
from pathlib import Path
import shutil
import zipfile
from openpyxl import load_workbook

def clean(v):return v.isoformat() if isinstance(v,(dt.datetime,dt.date)) else v

def export(out=Path('output'),site=Path('site')):
    out=Path(out);site=Path(site);meta=json.loads((out/'QC.json').read_text())
    target=out/meta['workbook'];book=load_workbook(target)
    audit=json.loads((out/'provenance.json').read_text());result={'meta':meta,'tabs':{},'download':target.name,'audit':audit}
    for s in book:
        header_row=5 if s.title in ('Impacts','Inland Flooding') else 1
        headers=[clean(s.cell(header_row,c).value) for c in range(1,s.max_column+1)]
        rows=[]
        for r in range(1 if s.title=='Summary' else header_row+1,s.max_row+1):
            values=[clean(s.cell(r,c).value) for c in range(1,s.max_column+1)]
            if not any(v is not None for v in values):continue
            if s.title!='Summary' and (values[0] is None or str(values[0]).startswith('[Insert')):continue
            links={str(c-1):s.cell(r,c).hyperlink.target for c in range(1,s.max_column+1) if s.cell(r,c).hyperlink and str(s.cell(r,c).hyperlink.target).startswith(('https://','http://'))}
            rows.append({'v':values,'links':links,'row':r})
        result['tabs'][s.title]={'status':'REVIEW','headers':headers,'rows':rows}
    result['tabs']['Provenance']={'status':'REVIEW','headers':['Tab','Row','Site ID','Variable','Value','Unit','UTC time','Datum','Status','Source URL','Details'],
        'rows':[{'v':[e.get(k) for k in ('tab','row','site_id','variable','value','unit','time_utc','datum','status','source_url','details')],
                 'links':{'9':e['source_url']}} for e in audit]}
    from common import identifier
    from coastal_water import FILES
    review=json.loads((out/FILES[0]).read_text());result['water_review']=review
    by_id={(r['site_id'],r['row']):r for r in review}
    water=result['tabs']['Water Level'];base=len(water['headers'])
    water['headers'].extend(['Review peak (ft; original datum)','Review peak UTC','Review datum','Coverage / qualification','Historical observations'])
    water['notice']='PSH water values require verified datum evidence. Review peaks retain measured stage in its original datum; I identifies incomplete or unqualified observations. Human meteorologist review required.'
    for row in water['rows']:
        r=by_id.get((identifier(row['v'][0]),row['row']));row['v']+=[None]*5
        if r:
            row['v'][base:]=[r.get('peak_ft'),r.get('peak_time_utc'),r.get('observed_datum'),r.get('reason'),r.get('source_url')]
            if r.get('source_url'):row['links'][str(base+4)]=r['source_url']
    site.mkdir(parents=True,exist_ok=True);(site/'data').mkdir(exist_ok=True)
    (site/'data/latest.json').write_text(json.dumps(result,ensure_ascii=False,allow_nan=False))
    shutil.copyfile(target,site/target.name)
    with zipfile.ZipFile(site/'review-outputs.zip','w',zipfile.ZIP_DEFLATED) as z:
        paths=[target,out/'QC.json',out/'provenance.json',out/'WeatherFlow-import-template.json',out/'Rainfall_partial_reports.csv',out/'USGS_stage_review.csv']
        paths.extend(out/name for name in FILES)
        paths.extend(out/'csv'/name for name in meta.get('csv_files',[]))
        for path in paths:
            if not path.is_file():raise ValueError('Missing manifested artifact: '+str(path))
            z.write(path,path.relative_to(out))
    shutil.copyfile(out/'WeatherFlow-import-template.json',site/'WeatherFlow-import-template.json')
    shutil.copyfile(out/'Rainfall_partial_reports.csv',site/'Rainfall_partial_reports.csv')
    shutil.copyfile(out/'USGS_stage_review.csv',site/'USGS_stage_review.csv')
    for name in FILES:shutil.copyfile(out/name,site/name)
    (site/'.nojekyll').write_text('')
    print(f'Dashboard: {len(book.sheetnames)} workbook tabs + provenance; {len(audit)} measurements');return result

if __name__=='__main__':export()
