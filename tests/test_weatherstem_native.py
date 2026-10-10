"""WeatherSTEM v0.10 native minute maxima and exact station separation."""
import datetime as dt
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import weatherstem
from common import UTC

def metadata(station_id=1313):
    return {'id':station_id,'transmitters':[{'sensors':[
        {'id':11,'name':'Anemometer','units':{'symbol':'mph'}},
        {'id':12,'name':'10 Minute Wind Gust','units':{'symbol':'mph'}},
        {'id':13,'name':'Wind Vane','units':{'symbol':'degrees'}}]}]}

class WeatherSTEMNativeTests(unittest.TestCase):
    def test_maximum_native_anemometer_without_rolling_average(self):
        raw=[['Timestamp','Anemometer','10 Minute Wind Gust','Wind Vane'],
             ['2024-09-11T00:00:00+00:00',30,40,90],
             ['2024-09-11T00:01:00+00:00',54,60,None],
             ['2024-09-11T00:02:00+00:00',30,55,100]]
        rows=weatherstem.parse(raw,metadata(),dt.date(2024,9,11),dt.date(2024,9,11))
        peak=max(rows,key=lambda r:r['wind'] or -1)
        self.assertAlmostEqual(peak['wind'],54*weatherstem.FACTORS['mph'])
        self.assertEqual(peak['dir'],90)
        self.assertEqual(peak['direction_time_utc'],'2024-09-11T00:00:00+00:00')
        self.assertAlmostEqual(max(x['gust'] for x in rows if x['gust'] is not None),60*weatherstem.FACTORS['mph'])
        self.assertEqual(peak['wind_averaging_period_basis'],'unverified native Anemometer average')
    def test_exact_station_id_and_sensor_request(self):
        class Response:
            url='https://eastbatonrouge.weatherstem.com/data'
            def raise_for_status(self): pass
            def __init__(self,value):self.value=value
            def json(self):return self.value
        class Session:
            def __init__(self):self.requests=[]
            def get(self,url,timeout):return Response(metadata(1313 if '/alexbox/' in url else 1314))
            def post(self,url,data,headers,timeout):
                import json
                request=json.loads(data)
                self.requests.append((url,request))
                return Response([['Timestamp','Anemometer','10 Minute Wind Gust','Wind Vane'],
                    ['2024-09-11T01:00:00+00:00',29 if request['id']=='1313' else 51,40,45]])
        session=Session()
        alex,_=weatherstem.collect('https://eastbatonrouge.weatherstem.com/data?refer=/alexbox',dt.date(2024,9,11),dt.date(2024,9,11),session)
        tiger,_=weatherstem.collect('https://eastbatonrouge.weatherstem.com/data?refer=/tigerstadium',dt.date(2024,9,11),dt.date(2024,9,11),session)
        self.assertNotEqual(alex[0]['wind'],tiger[0]['wind'])
        self.assertEqual([r[1]['id'] for r in session.requests],['1313','1314'])
        self.assertEqual(session.requests[0][1]['interval'],'minute')
