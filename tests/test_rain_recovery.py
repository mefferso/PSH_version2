import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from common import UTC
import cocorahs
import iem

class RainRecoveryTests(unittest.TestCase):
    def test_official_gmt_daily_export_recovers_exact_window(self):
        text='ObservationDate,ObservationTime,StationNumber,TotalPrecipAmt\n2024-09-10,12:00 PM,LA-ST-11,0.03\n2024-09-11,12:00 PM,LA-ST-11,0.38\n2024-09-12,12:00 PM,LA-ST-11,9.25\n'
        a=dt.datetime(2024,9,10,12,tzinfo=UTC);b=a+dt.timedelta(days=2)
        records=cocorahs.parse_daily_export(text,'LA-ST-011')
        self.assertAlmostEqual(cocorahs.export_total(records,a,b),9.63)
        self.assertIsNone(cocorahs.export_total(records[:2],a,b))
        self.assertEqual(cocorahs.parse_daily_export(text,'LA-JF-20'),[])

    def test_dst_daily_interval_uses_local_calendar_day(self):
        text='ObservationDate,ObservationTime,StationNumber,TotalPrecipAmt\n2024-03-09,01:00 PM,LA-ST-11,0\n2024-03-10,12:00 PM,LA-ST-11,1.2\n'
        a=dt.datetime(2024,3,9,13,tzinfo=UTC);b=dt.datetime(2024,3,10,12,tzinfo=UTC)
        self.assertEqual(cocorahs.export_total(cocorahs.parse_daily_export(text,'LA-ST-11'),a,b),1.2)

    def test_trace_conflict_overlap_and_outside_reports_remain_candidates(self):
        header='ObservationDate,ObservationTime,StationNumber,TotalPrecipAmt\n'
        a=dt.datetime(2024,9,10,12,tzinfo=UTC);b=a+dt.timedelta(days=1)
        for values in ['2024-09-11,12:00 PM,LA-ST-11,T\n', '2024-09-11,12:00 PM,LA-ST-11,1\n2024-09-11,12:00 PM,LA-ST-11,2\n']:
            self.assertIsNone(cocorahs.export_total(cocorahs.parse_daily_export(header+values,'LA-ST-11'),a,b))

    def test_metar_peak_wind_remark_has_its_own_timestamp_direction(self):
        text='station,valid,sknt,gust,drct,mslp,p01i,metar\nBTR,2024-09-11 23:53,20,30,40,999,0.1,KBTR 112353Z 04020G30KT RMK AO2 PK WND 05047/2332\n'
        rows=iem.parse(text,'KBTR',dt.date(2024,9,11),dt.date(2024,9,11))
        peak=max(rows,key=lambda x:x.get('gust') or 0)
        self.assertEqual(peak['gust'],47)
        self.assertEqual(peak['time'],dt.datetime(2024,9,11,23,32,tzinfo=UTC))
        self.assertEqual(peak['gust_dir'],50)
        self.assertIsNone(peak['wind'])

class SynopticIntervalRecoveryTests(unittest.TestCase):
    def test_native_reported_daily_intervals_do_not_need_fabricated_nested_intervals(self):
        import synoptic
        a=dt.datetime(2024,9,10,12,tzinfo=UTC);b=a+dt.timedelta(days=2)
        payload={'SUMMARY':{'RESPONSE_CODE':1},'UNITS':{'precipitation':'Inches'},'STATION':[{'STID':'LIX','OBSERVATIONS':{'precipitation':[
            {'interval':n+1,'total':v,'first_report':(a+dt.timedelta(days=n)).isoformat(),'last_report':(a+dt.timedelta(days=n+1)).isoformat(),'count':1,'report_type':'precip_accum_24_hour'} for n,v in enumerate([.38,9.25])]}}]}
        self.assertAlmostEqual(synoptic.precip_total(payload,'LIX',a,b),9.63)
        payload['STATION'][0]['OBSERVATIONS']['precipitation'][1]['first_report']=(a+dt.timedelta(days=1,hours=1)).isoformat()
        self.assertIsNone(synoptic.precip_total(payload,'LIX',a,b))

class CoCoMultidayRecoveryTests(unittest.TestCase):
    def test_multiday_uses_verified_prior_observation_and_inclusive_reporting_date(self):
        a=dt.datetime(2024,9,10,12,tzinfo=UTC);b=a+dt.timedelta(days=2)
        daily=cocorahs.parse_daily_export('ObservationDate,ObservationTime,StationNumber,TotalPrecipAmt\n2024-09-10,12:00 PM,LA-ST-11,0.03\n','LA-ST-11')
        text='StartDate,EndDateTime,StationNumber,TotalPrecipAmt\n2024-09-11,2024-09-12 12:00 PM,LA-ST-11,9.63\n'
        reports=cocorahs.parse_multiday_export(text,'LA-ST-11',daily)
        self.assertEqual(cocorahs.export_total(reports,a,b),9.63)
        self.assertIsNone(cocorahs.export_total(cocorahs.parse_multiday_export(text,'LA-ST-11',[]),a,b))
