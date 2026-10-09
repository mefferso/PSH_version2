import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import coops
from common import public_url

class SafetyTests(unittest.TestCase):
    def test_noaa_requires_explicit_mhhw_datum_metadata(self):
        self.assertEqual(coops.verify_datums({'datums':[{'name':'MHHW','value':'1.2'}]},'8761724'),True)
        with self.assertRaises(ValueError):coops.verify_datums({'datums':[{'name':'MSL','value':'1.0'}]},'8761724')
        with self.assertRaises(ValueError):coops.verify_datums({'id':'0000000','datums':[{'name':'MHHW','value':'1.2'}]},'8761724')

    def test_token_never_saved_in_provenance(self):
        self.assertEqual(public_url('https://api.synopticdata.com/v2/?token=secret&stid=MSY'),'https://api.synopticdata.com/v2/?stid=MSY')
