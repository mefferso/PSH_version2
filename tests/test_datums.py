import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import datums
from common import UTC
class DatumTests(unittest.TestCase):
    def test_offset_requires_identity_independent_evidence_and_effective_window(self):
        a=dt.datetime(2024,9,11,tzinfo=UTC);b=a+dt.timedelta(days=1)
        st={'id':'BSGL1','row':10,'url':'https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=82742'}
        x={'site_id':'BSGL1','rivergages_sid':'82742','datum':'NAVD88','offset_ft':0.11,'reviewed':True,
            'effective_start_utc':'2024-01-01T00:00:00Z','effective_end_utc':'2025-01-01T00:00:00Z',
            'evidence':['https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=82742','https://www.weather.gov/lix/']}
        self.assertAlmostEqual(datums.offset(x,st,a,b),0.11)
        for change in [{'rivergages_sid':'76030'},{'reviewed':False},{'effective_end_utc':'2024-09-11T12:00:00Z'},{'evidence':x['evidence'][:1]}]:
            with self.subTest(change=change),self.assertRaises(ValueError):datums.offset(dict(x,**change),st,a,b)
    def test_hml_requires_explicit_utc_and_feet(self):
        a=dt.date(2024,9,11)
        rows=datums.parse_hml('station,valid[utc],stage[ft]\nBSGL1,2024-09-11 12:00,2.5\nOTHER,2024-09-11 12:00,30\nBSGL1,2024-09-12 12:00,20\n','BSGL1',a,a)
        self.assertEqual([x[0] for x in rows],[2.5])
        with self.assertRaises(ValueError):datums.parse_hml('station,valid,stage\nBSGL1,2024-09-11 12:00,2.5\n','BSGL1',a,a)
