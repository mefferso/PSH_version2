import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from usace import station_link, metadata_from_html, fetch_station_metadata

class RiverGagesTests(unittest.TestCase):
    def test_valid_station(self):
        cell=Mock()
        cell.hyperlink.target="https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=52800&fid=&dt=S"
        self.assertEqual(station_link(cell)[0],"52800")
        cell.hyperlink.target="https://rivergages.mvr.usace.army.mil/WaterControl/shefdata2.cfm?sid=85750LA&d=7&dt=S"
        self.assertEqual(station_link(cell)[0],"85750LA")
    def test_untrusted_host(self):
        cell=Mock()
        cell.hyperlink.target="https://example.org/WaterControl/stationinfo2.cfm?sid=52800"
        self.assertIsNone(station_link(cell))
    def test_bad_station(self):
        cell=Mock()
        cell.hyperlink.target="https://rivergages.mvr.usace.army.mil/WaterControl/stationinfo2.cfm?sid=52800%26bad"
        self.assertIsNone(station_link(cell))
    def test_parses_datum_notes_and_ignores_scripts(self):
        source = """<html><script>fake</script><div>Gage Zero: 0 Ft. GAGE</div>
        <div>Longitude: -89.79</div><p>Location of Gage : Gage zero set to
        NAVD88 (2009.55) on 01/09/2018. Current adjustment is 0.11 ft
        (add 0.11 ft to gage data).</p></html>"""
        result = metadata_from_html(source)
        self.assertIn("0 Ft. GAGE", result["gage_zero"])
        self.assertTrue(result["has_navd88_reference"])
        self.assertIn("0.11", result["datum_notes"])
    def test_missing_datum_is_not_verified(self):
        result = metadata_from_html("<div>Stage 5.3 feet</div>")
        self.assertFalse(result["has_navd88_reference"])
        self.assertEqual(result["gage_zero"], "")
if __name__=="__main__": unittest.main()
