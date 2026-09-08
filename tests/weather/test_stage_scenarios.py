import unittest
import numpy as np
import pandas as pd
from stage_scenarios import scenario, paired


class StageTests(unittest.TestCase):
    def setUp(self):
        self.hourly = pd.Series(5., index=pd.date_range('2020-01-01','2020-07-01',freq='h',inclusive='left'))
        self.daily = pd.DataFrame({'tmean_c':17.,'tmin_c':-2.2,'precip_mm':10.,
            'precip_suspect_extreme':False},index=pd.date_range('2020-01-01','2021-06-01'))
    def calc(self, n=50):
        return scenario(self.hourly,self.daily,'2020-01-01','2020-07-01',n)
    def test_known_dates_and_inclusive_stages(self):
        r=self.calc()
        self.assertEqual(r['chill_date'],'2020-01-03')
        self.assertEqual(r['budbreak_date'],'2020-01-17')
        self.assertEqual(r['flowering'],['2020-01-31','2020-02-21'])
        self.assertEqual(r['metrics']['flower_freeze_days'],22)
        self.assertEqual(r['metrics']['harvest_rain_mm'],410.)
        self.assertEqual(r['metrics']['harvest_heavy_rain_days'],41)
        self.assertEqual(r['status'],'complete')
    def test_strict_upper_and_no_lower_bound(self):
        self.hourly[:]=7.2
        self.assertEqual(self.calc()['status'],'chill_not_met')
        self.hourly[:]=-1
        self.assertEqual(self.calc()['status'],'complete')
    def test_missing_chill_not_concatenated(self):
        self.hourly.iloc[-1]=np.nan
        self.assertEqual(self.calc()['status'],'incomplete_chill')
    def test_missing_gdd_not_zero_filled(self):
        self.daily.loc['2020-01-04','tmean_c']=np.nan
        self.assertEqual(self.calc()['status'],'incomplete_gdd')
    def test_flagged_rain_declines_even_below_numeric_threshold(self):
        self.daily.loc['2020-04-15','precip_suspect_extreme']=True
        r=self.calc()
        self.assertIsNone(r['metrics']['harvest_rain_mm'])
        self.assertIsNone(r['metrics']['production_max_dry_days'])
        self.assertEqual(r['metrics']['flower_freeze_days'],22)
    def test_truncated_archive(self):
        self.daily=self.daily.loc[:'2020-03-01']
        self.assertEqual(self.calc()['status'],'incomplete_metrics')
    def test_paired_denominator(self):
        a,b=self.calc(50),self.calc(100)
        b['metrics']['harvest_rain_mm']=None
        p=paired([{'scenarios':[a,b]}])
        self.assertEqual(p['harvest_rain_mm']['paired_years'],0)
        self.assertIsNone(p['harvest_rain_mm']['mean_difference_100_minus_50'])
        self.assertEqual(p['flower_freeze_days']['paired_years'],1)


if __name__ == '__main__': unittest.main()
