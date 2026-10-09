"""Execute shipped dashboard scripts against a DOM and exercise manual entry."""
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class DashboardBrowserTests(unittest.TestCase):
    def test_tabs_qc_filter_and_reviewed_weatherflow_entry(self):
        browser=shutil.which('node')
        self.assertTrue(browser,'Node is required for dashboard integration tests')
        values=['XBTR','Baton Rouge',30.5,-91.1,'East Baton Rouge','LA','L','WeatherFlow',10,1]+[None]*20
        payload={'meta':{'storm':'Hurricane Isaias','start_utc':'2026-10-08','end_utc':'2026-10-09','coverage':'DEVELOPMENT','qc_status_counts':{'MANUAL':1},'measurement_count':0},'download':'review.xlsx','tabs':{
            'Wind and Pressure':{'headers':['Site ID','Site Name']+[None]*28,'rows':[{'v':values,'row':91,'links':{'0':'https://ds.weatherflow.com/map'}}]},
            'Summary':{'headers':['Summary'],'rows':[{'v':['Highest 10 Land Winds',42],'row':20,'links':{}}]},
            'QC':{'headers':['Tab','ID','Network','Status','Details','Source'],'rows':[{'v':['Wind and Pressure','XBTR','WeatherFlow','MANUAL','test',''],'links':{}}]},
            'Provenance':{'headers':['Source'],'rows':[]}}}
        source=(ROOT/'site/index.html').read_text()
        injected='window.fetch=()=>Promise.resolve({ok:true,json:()=>Promise.resolve('+json.dumps(payload)+')});'
        source=source.replace('<script>','<script>'+injected,1)
        driver="""<script>setTimeout(()=>{try{
 document.querySelector('[data-tab="Summary"]').click();if(!document.getElementById('rows').textContent.includes('Highest 10'))throw Error('summary missing');
 document.querySelector('[data-tab="QC"]').click();document.getElementById('qcfilter').value='MANUAL';document.getElementById('qcfilter').dispatchEvent(new Event('change'));
 if(!document.getElementById('rows').textContent.includes('XBTR'))throw Error('QC filter missing');
 document.getElementById('manualbutton').click();if(!document.getElementById('manual').open)throw Error('manual dialog missing');
 document.getElementById('manualvalue').value='50';document.getElementById('manualtime').value='2026-10-08T12:30';document.getElementById('manualreview').checked=true;
 document.getElementById('manualform').dispatchEvent(new Event('submit',{cancelable:true}));
 if(!document.getElementById('manualstatus').textContent.includes('1 reviewed observations'))throw Error('manual staging failed');
 document.body.dataset.test='PASS';
 }catch(e){document.body.dataset.test='FAIL: '+e.message}},500)</script>"""
        source=source.replace('</body>',driver+'</body>')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.html';p.write_text(source)
            runner="""const {JSDOM}=require('jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync(process.argv[1],'utf8'),{runScripts:'dangerously',url:'https://mefferso.github.io/PSH_version2/',beforeParse(w){w.HTMLDialogElement.prototype.showModal=function(){this.open=true};w.HTMLDialogElement.prototype.close=function(){this.open=false};w.URL.createObjectURL=()=> 'blob:test';}});
setTimeout(()=>{console.log(dom.serialize());dom.window.close()},1000);"""
            result=subprocess.run([browser,'-e',runner,str(p)],cwd=ROOT,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr[-1000:])
            self.assertIn('data-test="PASS"',result.stdout,result.stdout[-2000:])
