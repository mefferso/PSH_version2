import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from coops import collect, station_from_cell

class CoopsTests(unittest.TestCase):
    def test_extracts_only_valid_noaa_hyperlink(self):
        cell = Mock()
        cell.hyperlink.target = "https://tidesandcurrents.noaa.gov/waterlevels.html?id=8761724"
        self.assertEqual(station_from_cell(cell), "8761724")
        cell.hyperlink.target = "https://example.org/?id=8761724"
        self.assertIsNone(station_from_cell(cell))

    def test_peak_and_utc_bounds(self):
        response = Mock()
        response.url = "https://api.tidesandcurrents.noaa.gov/"
        response.json.return_value = {"metadata":{"id":"8761724"}, "data":[
            {"t":"2026-10-08 12:00","v":"2.53","f":"0"},
            {"t":"2026-10-09 08:30","v":"3.12","f":"0"},
            {"t":"2026-10-10 00:00","v":"9.9","f":"0"},
            {"t":"2026-10-08 13:00","v":""}
        ]}
        session = Mock()
        session.get.return_value = response
        start = dt.date(2026,10,8)
        end = dt.date(2026,10,9)
        peak, urls = collect("8761724",start,end,session=session)
        self.assertEqual(peak[0],3.12)
        self.assertEqual(peak[1].strftime("%Y-%m-%d %H:%M"),"2026-10-09 08:30")
        self.assertEqual(len(urls),1)
        self.assertEqual(session.get.call_args.kwargs["params"]["datum"],"MHHW")

    def test_api_error_not_silent(self):
        response = Mock()
        response.url = "https://api.tidesandcurrents.noaa.gov/"
        response.json.return_value = {"error":{"message":"No data"}}
        session=Mock()
        session.get.return_value=response
        with self.assertRaises(ValueError):
            collect("8761724",dt.date(2026,10,8),dt.date(2026,10,9),session=session)

if __name__=="__main__":
    unittest.main()
