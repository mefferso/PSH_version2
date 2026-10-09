import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import iem
from common import UTC

class IEMTests(unittest.TestCase):
    def test_wrong_identity_nonfinite_and_outside_time_rejected(self):
        text='station,valid,sknt,gust,drct,mslp,p01i\nMSY,2024-09-11 01:00,40,60,90,990,0.1\nBTR,2024-09-11 02:00,120,150,90,900,1\nMSY,2024-09-12 01:00,60,80,90,970,2\nMSY,2024-09-11 03:00,nan,inf,999,9999,M\n'
        rows=iem.parse(text,'MSY',dt.date(2024,9,11),dt.date(2024,9,11))
        self.assertEqual(len(rows),2)
        self.assertEqual(rows[0]['wind'],40)
        self.assertIsNone(rows[1]['gust'])
        self.assertIsNone(rows[1]['pressure'])

    def test_hourly_accumulations_dedup_and_missing_reject(self):
        a=dt.datetime(2024,9,11,tzinfo=UTC);b=a+dt.timedelta(hours=2)
        rows=[{'time':a+dt.timedelta(hours=1),'rain':0.2,'report_type':3},
              {'time':a+dt.timedelta(hours=1),'rain':0.2,'report_type':3},
              {'time':b,'rain':0.3,'report_type':3}]
        self.assertAlmostEqual(iem.rain_total(rows,a,b),0.5)
        self.assertIsNone(iem.rain_total(rows[:1],a,b))
        rows.append({'time':b,'rain':0.4,'report_type':3})
        self.assertIsNone(iem.rain_total(rows,a,b))

    def test_trace_requires_review_not_silent_zero(self):
        rows=iem.parse('station,valid,p01i,metar\nMSY,2024-09-11 01:00,T,METAR\n','MSY',dt.date(2024,9,11),dt.date(2024,9,11))
        self.assertIsNone(rows[0]['rain'])
        self.assertTrue(rows[0]['trace'])
