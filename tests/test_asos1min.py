import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import asos1min
from common import UTC
class MinuteTests(unittest.TestCase):
    def test_exact_id_two_minute_average_five_second_gust_and_units(self):
        text='station,valid(Etc/UTC),sknt,drct,gust_sknt,gust_drct,precip\nMSY,2024-09-11 12:00,43,90,68,100,0.01\nOTHER,2024-09-11 12:01,99,10,100,20,2\nMSY,2024-09-13 00:00,80,20,99,30,1\n'
        rows=asos1min.parse(text,'KMSY',dt.date(2024,9,11),dt.date(2024,9,12))
        self.assertEqual(len(rows),1);self.assertEqual(rows[0]['wind'],43);self.assertEqual(rows[0]['gust'],68);self.assertEqual(rows[0]['gust_dir'],100);self.assertIsNone(rows[0]['pressure'])
        with self.assertRaises(ValueError):asos1min.parse(text.replace('valid(Etc/UTC)','valid(America/Chicago)'),'MSY',dt.date(2024,9,11),dt.date(2024,9,12))
    def test_missing_trace_or_conflicting_minute_rain_is_withheld(self):
        a=dt.datetime(2024,9,11,12,tzinfo=UTC);b=a+dt.timedelta(minutes=2)
        rows=[{'time':a+dt.timedelta(minutes=1),'rain':.01},{'time':b,'rain':.02}]
        self.assertEqual(asos1min.rain_total(rows,a,b),.03)
        self.assertIsNone(asos1min.rain_total(rows[:1],a,b))
        self.assertIsNone(asos1min.rain_total(rows+[dict(rows[0],rain=.05)],a,b))
