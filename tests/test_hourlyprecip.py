import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import hourlyprecip

class IEMHourlyRainTests(unittest.TestCase):
    def test_complete_hourly_ASOS_reports_fill_requested_window(self):
        text=('station,network,valid,precip_in\n'
              'MSY,LA_ASOS,2024-09-11 12:00,0.50\n'
              'MSY,LA_ASOS,2024-09-11 13:00,1.25\n'
              'BTR,LA_ASOS,2024-09-11 13:00,9.0\n')
        start=dt.datetime(2024,9,11,12,tzinfo=dt.timezone.utc)
        end=start+dt.timedelta(hours=2)
        total,count,traces=hourlyprecip.parse(text,'MSY','LA_ASOS',start,end)
        self.assertEqual(total,1.75)
        self.assertEqual(count,2)
        self.assertEqual(traces,0)
        self.assertIsNone(hourlyprecip.parse(text,'MSY','MS_ASOS',start,end)[0])

    def test_missing_hour_not_zero_filled_and_trace_is_identified(self):
        start=dt.datetime(2024,9,11,12,tzinfo=dt.timezone.utc)
        end=start+dt.timedelta(hours=3)
        rows='station,network,valid,precip_in\nMSY,LA_ASOS,2024-09-11 12:00,0.0001\nMSY,LA_ASOS,2024-09-11 14:00,2.0\n'
        total,count,traces=hourlyprecip.parse(rows,'MSY','LA_ASOS',start,end)
        self.assertIsNone(total)
        self.assertEqual(count,2)
        self.assertEqual(traces,1)

    def test_duplicate_disagreement_is_rejected(self):
        start=dt.datetime(2024,9,11,12,tzinfo=dt.timezone.utc)
        text='station,network,valid,precip_in\nMSY,LA_ASOS,2024-09-11 12:00,1\nMSY,LA_ASOS,2024-09-11 12:00,2\n'
        with self.assertRaises(ValueError):
            hourlyprecip.parse(text,'MSY','LA_ASOS',start,start+dt.timedelta(hours=1))

    def test_gap_summary_is_not_treated_as_storm_total(self):
        a=dt.datetime(2026,10,8,tzinfo=dt.timezone.utc)
        b=a+dt.timedelta(hours=3)
        csvdata='station,network,valid,precip_in\nMSY,LA_ASOS,2026-10-08 00:00,0.25\nMSY,LA_ASOS,2026-10-08 02:00,0.75\n'
        result=hourlyprecip.coverage_details(csvdata,'MSY','LA_ASOS',a,b)
        self.assertEqual(result['observed_hours'],2)
        self.assertEqual(result['expected_hours'],3)
        self.assertEqual(result['observed_sum_inches'],1.0)
        self.assertEqual(result['missing_hours_utc'],['2026-10-08T01:00:00+00:00'])
