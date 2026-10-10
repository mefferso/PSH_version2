import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import coopobs
from cocorahs import export_total

class CoopDailyTests(unittest.TestCase):
    def test_exact_observation_clock_and_contiguous_rain(self):
        csv_text=('nwsli,date,time,high_F,low_F,precip,snow_inch,snowd_inch\n'
                  'ABCL1,2024-09-11,07 AM,80,70,1.5,0,0\n'
                  'ABCL1,2024-09-12,07 AM,80,70,2.3,0,0\n'
                  'OTHER,2024-09-12,07 AM,,,99,0,0\n')
        records=coopobs.parse(csv_text,'ABCL1')
        self.assertEqual(len(records),2)
        start=dt.datetime(2024,9,10,12,tzinfo=dt.timezone.utc)
        end=dt.datetime(2024,9,12,12,tzinfo=dt.timezone.utc)
        self.assertAlmostEqual(export_total(records,start,end),3.8)
        self.assertIsNone(export_total(records[:1],start,end))
        self.assertEqual(coopobs.parse(csv_text,'WRONG'),[])

    def test_missing_precip_not_assumed_zero(self):
        csv_text=('nwsli,date,time,high_F,low_F,precip,snow_inch,snowd_inch\n'
                  'ABCL1,2024-09-11,07 AM,,,,,\n')
        self.assertEqual(coopobs.parse(csv_text,'ABCL1'),[])
