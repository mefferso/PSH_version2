import datetime as dt
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import tornadoes
class TornadoTests(unittest.TestCase):
    def test_confirmed_storm_association_cwa_and_standard_time_to_utc(self):
        row={'EVENT_TYPE':'Tornado','WFO':'LIX','EPISODE_NARRATIVE':'Hurricane Francine affected the area.',
             'EVENT_NARRATIVE':'Survey confirmed tornado.','BEGIN_DATE_TIME':'11-SEP-24 18:30:00','CZ_TIMEZONE':'CST-6',
             'BEGIN_LAT':'30.2','BEGIN_LON':'-90.2','BEGIN_LOCATION':'NEW ORLEANS','CZ_NAME':'ORLEANS',
             'STATE':'LOUISIANA','TOR_F_SCALE':'EF1','EVENT_ID':'123'}
        events=tornadoes.parse([row],'Hurricane Francine',dt.date(2024,9,11),dt.date(2024,9,12))
        self.assertEqual(len(events),1)
        self.assertEqual(events[0]['time'].isoformat(),'2024-09-12T00:30:00+00:00')
        row['EPISODE_NARRATIVE']='Thunderstorms during a cold front.'
        self.assertEqual(tornadoes.parse([row],'Hurricane Francine',dt.date(2024,9,11),dt.date(2024,9,12)),[])
        row['EPISODE_NARRATIVE']='Francine';row['CZ_TIMEZONE']='unknown'
        self.assertEqual(tornadoes.parse([row],'Hurricane Francine',dt.date(2024,9,11),dt.date(2024,9,12)),[])
