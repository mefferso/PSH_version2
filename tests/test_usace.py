import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from usace import station_link

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
if __name__=="__main__": unittest.main()
