import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ndbc import station_id, parse_text, KNOTS_PER_MS

class NDBCTests(unittest.TestCase):
    def test_station_link(self):
        cell = Mock()
        cell.hyperlink.target = "https://www.ndbc.noaa.gov/data/realtime2/BURL1.txt"
        self.assertEqual(station_id(cell), "BURL1")
        cell.hyperlink.target = "https://www.ndbc.noaa.gov/station_page.php?station=ptfl1"
        self.assertEqual(station_id(cell), "PTFL1")

    def test_data(self):
        sample = ("#YY MM DD hh mm WDIR WSPD GST WVHT DPD APD MWD PRES\n"
                  "#yr mo dy hr mn degT m/s m/s m sec sec degT hPa\n"
                  "2026 10 08 12 00 100 15.0 20.0 99 99 99 99 995.0\n"
                  "2026 10 09 06 00 999 99.0 99.0 99 99 99 99 9999.0\n"
                  "2026 10 10 01 00 080 30.0 35.0 99 99 99 99 981.0\n")
        rows = parse_text(sample, dt.date(2026, 10, 8), dt.date(2026, 10, 9))
        self.assertEqual(len(rows), 2)
        self.assertAlmostEqual(rows[0]["wind"], 15*KNOTS_PER_MS)
        self.assertEqual(rows[0]["pressure"], 995)
        self.assertIsNone(rows[1]["wind"])
        self.assertIsNone(rows[1]["pressure"])

    def test_bad_format(self):
        with self.assertRaises(ValueError):
            parse_text("not a weather record", dt.date(2026,10,8), dt.date(2026,10,9))

if __name__ == "__main__":
    unittest.main()

class NDBCSafetyTests(unittest.TestCase):
    def test_wrong_units_are_not_interpreted_as_metres_per_second(self):
        sample='#YY MM DD hh mm WDIR WSPD GST PRES\n#yr mo dy hr mn degT mph mph hPa\n2024 09 11 12 00 90 50 60 990\n'
        with self.assertRaises(ValueError):parse_text(sample,dt.date(2024,9,11),dt.date(2024,9,11))

class FeedConflictTests(unittest.TestCase):
    def test_conflicting_realtime_archive_timestamp_is_withheld(self):
        import ndbc
        from unittest.mock import patch
        session=Mock();response=Mock(status_code=200,content=b'x',text='unused',url='https://www.ndbc.noaa.gov/data/realtime2/BURL1.txt');session.get.return_value=response
        t=dt.datetime.now(dt.timezone.utc).replace(hour=12,minute=0,second=0,microsecond=0)
        first={'time':t,'wind':10,'gust':20,'pressure':990,'dir':90};second=dict(first,gust=40)
        with patch.object(ndbc,'parse_text',side_effect=[[first],[second]]):
            rows,urls,errors=ndbc.retrieve('BURL1',t.date(),t.date(),session)
        self.assertEqual(rows,[]);self.assertTrue(any('Conflicting feeds' in x for x in errors))
