import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from usgs import site_from_link, parse_observations, collect

class USGSTests(unittest.TestCase):
    def test_link_identity(self):
        cell=Mock()
        cell.hyperlink.target="https://waterdata.usgs.gov/monitoring-location/07374527/"
        self.assertEqual(site_from_link(cell),"07374527")
        cell.hyperlink.target="https://example.com/monitoring-location/07374527/"
        self.assertIsNone(site_from_link(cell))
    def test_direct_navd88_only(self):
        payload={"features":[{"properties":{"monitoring_location_id":"USGS-07374527","parameter_code":code,
            "unit_of_measure":"ft","value":val,"time":"2026-10-09T07:15:00Z"}} for code,val in
            (("00065","12.5"),("62620","3.25"),("62615","4.1"))]}
        rows=parse_observations(payload,"07374527",dt.date(2026,10,8),dt.date(2026,10,9))
        self.assertEqual(len(rows),2)
        self.assertEqual(max(v[0] for v in rows),4.1)
    def test_rejects_unknown_unit_and_other_station(self):
        payload={"features":[{"properties":{"monitoring_location_id":"USGS-00000001","parameter_code":"62620",
            "unit_of_measure":"ft","value":"9","time":"2026-10-09T02:00:00Z"}},
            {"properties":{"monitoring_location_id":"USGS-07374527","parameter_code":"62620",
            "unit_of_measure":"m","value":"8","time":"2026-10-09T02:00:00Z"}}]}
        self.assertEqual(parse_observations(payload,"07374527",dt.date(2026,10,8),dt.date(2026,10,9)),[])
    def test_data_response(self):
        response=Mock()
        response.url="https://api.waterdata.usgs.gov/ogcapi/v1/collections/continuous/items"
        response.json.return_value={"type":"FeatureCollection","features":[{"properties":{
            "monitoring_location_id":"USGS-07374527","parameter_code":"62620",
            "unit_of_measure":"ft","value":"2.2","time":"2026-10-09T02:00:00Z"}}],"links":[]}
        session=Mock()
        session.get.return_value=response
        peak,links=collect("07374527",dt.date(2026,10,8),dt.date(2026,10,9),session)
        self.assertEqual(peak[0],2.2)
        self.assertEqual(len(links),1)

if __name__=="__main__": unittest.main()

class USGSSafetyTests(unittest.TestCase):
    def test_different_elevation_series_are_not_combined(self):
        response=Mock();response.url='https://api.waterdata.usgs.gov/ogcapi/v1/collections/continuous/items'
        response.json.return_value={'type':'FeatureCollection','features':[{'properties':{
            'monitoring_location_id':'USGS-07374527','parameter_code':code,'time_series_id':code,
            'unit_of_measure':'ft','value':'3','time':'2024-09-11T12:00:00Z'}} for code in ('62620','62615')], 'links':[]}
        session=Mock();session.get.return_value=response
        with self.assertRaises(ValueError):collect('07374527',dt.date(2024,9,11),dt.date(2024,9,11),session)
