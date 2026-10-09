import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import synoptic
class SynopticTests(unittest.TestCase):
    def test_units_identity_and_variable_specific_direction(self):
        data={'SUMMARY':{'RESPONSE_CODE':1},'UNITS':{'wind_speed':'m/s','wind_gust':'m/s','sea_level_pressure':'Pa','wind_direction':'Degrees'},'STATION':[{'STID':'BBNL1','OBSERVATIONS':{'date_time':['2024-09-11T12:00:00Z'],'wind_speed_set_1':[10],'wind_gust_set_1':[15],'wind_direction_set_1':[90],'sea_level_pressure_set_1':[99000]}}]}
        rows=synoptic.parse(data,'BBNL1',dt.date(2024,9,11),dt.date(2024,9,11))
        self.assertAlmostEqual(rows[0]['wind'],19.4384449244)
        self.assertEqual(rows[0]['pressure'],990)
        self.assertIsNone(rows[0]['gust_dir'])
        self.assertEqual(rows[0]['wind_original_value'],10)
        self.assertEqual(rows[0]['wind_original_unit'],'m/s')
        self.assertEqual(synoptic.parse(data,'OTHER',dt.date(2024,9,11),dt.date(2024,9,11)),[])
        data['UNITS']['wind_speed']='unknown'
        self.assertIsNone(synoptic.parse(data,'BBNL1',dt.date(2024,9,11),dt.date(2024,9,11))[0]['wind'])

class SynopticRainTests(unittest.TestCase):
    def test_exact_requested_interval_and_explicit_units_required(self):
        a=dt.datetime(2024,9,10,12,tzinfo=dt.timezone.utc);b=a+dt.timedelta(days=2)
        payload={'SUMMARY':{'RESPONSE_CODE':1},'UNITS':{'precipitation':'Inches'},'STATION':[{'STID':'LIX','OBSERVATIONS':{'precipitation':[{'total':7.93,'count':48,'first_report':a.isoformat(),'last_report':b.isoformat(),'intervals':[{'start_utc':a.isoformat(),'end_utc':b.isoformat(),'total':7.93}]}]}}]}
        self.assertEqual(synoptic.precip_total(payload,'LIX',a,b),7.93)
        self.assertIsNone(synoptic.precip_total(payload,'NEARBY',a,b))
        payload['STATION'][0]['OBSERVATIONS']['precipitation'][0]['last_report']=(b-dt.timedelta(hours=12)).isoformat()
        self.assertIsNone(synoptic.precip_total(payload,'LIX',a,b))

class InteriorRainGapTests(unittest.TestCase):
    def test_two_endpoints_do_not_prove_a_full_day_of_precipitation(self):
        a=dt.datetime(2024,9,11,tzinfo=dt.timezone.utc);b=a+dt.timedelta(days=1)
        payload={'SUMMARY':{'RESPONSE_CODE':1},'UNITS':{'precipitation':'Inches'},'STATION':[{'STID':'LIX','OBSERVATIONS':{'precipitation':[{'total':7,'count':2,'first_report':a.isoformat(),'last_report':b.isoformat()}]}}]}
        self.assertIsNone(synoptic.precip_total(payload,'LIX',a,b))
