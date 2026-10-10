import datetime as dt
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from cocorahs import observed_partial_sum
from hourlyprecip import coverage_details
from synoptic import partial_precip_from_reports

UTC=dt.timezone.utc

class PartialObservationPolicyTests(unittest.TestCase):
    def setUp(self):
        # These completed-event fixtures must not depend on today's date.
        import os
        from unittest.mock import patch
        p=patch.dict(os.environ,PSH_AS_OF_UTC='2026-10-12T00:00:00Z')
        p.start();self.addCleanup(p.stop)

    def test_discontinuous_reports_contribute_without_imputing_gaps(self):
        a=dt.datetime(2026,10,8,tzinfo=UTC); day=dt.timedelta(days=1)
        obs=[{'start':a,'end':a+day,'value':1.2},
             {'start':a+2*day,'end':a+3*day,'value':2.3}]
        value,hours,intervals=observed_partial_sum(obs,a,a+3*day)
        self.assertAlmostEqual(value,3.5)
        self.assertEqual(hours,48)
        self.assertEqual(len(intervals),2)

    def test_overlapping_daily_and_multiday_cannot_double_count(self):
        a=dt.datetime(2026,10,8,tzinfo=UTC);day=dt.timedelta(days=1)
        obs=[{'start':a,'end':a+2*day,'value':4.0},
             {'start':a,'end':a+day,'value':2.0},
             {'start':a+day,'end':a+2*day,'value':2.0}]
        value,hours,intervals=observed_partial_sum(obs,a,a+2*day)
        self.assertEqual(value,4.0)
        self.assertEqual(hours,48)

    def test_synoptic_partial_observation_is_distinct_from_storm_total(self):
        a=dt.datetime(2026,10,8,tzinfo=UTC);b=a+dt.timedelta(days=2)
        payload={'UNITS':{'precipitation':'inches'},'STATION':[{
          'STID':'KMSY','OBSERVATIONS':{'precipitation':[{
             'first_report':a.isoformat(),'last_report':(a+dt.timedelta(days=1)).isoformat(),
             'total':1.4}]}}]}
        result=partial_precip_from_reports(payload,'KMSY',a,b)
        self.assertAlmostEqual(result[0],1.4)
        self.assertEqual(result[1],24)

    def test_missing_hour_is_measured_as_missing_not_zero(self):
        a=dt.datetime(2026,10,8,tzinfo=UTC)
        txt='station,network,valid,precip_in\nMSY,LA_ASOS,2026-10-08 00:00,0.8\n'
        coverage=coverage_details(txt,'MSY','LA_ASOS',a,a+dt.timedelta(hours=2))
        self.assertEqual(coverage['observed_hours'],1)
        self.assertEqual(coverage['missing_hours_utc'],['2026-10-08T01:00:00+00:00'])
        self.assertEqual(coverage['observed_sum_inches'],0.8)
