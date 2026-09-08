import unittest
import pandas as pd
import numpy as np
from evidence_report import chill,dry_spell,complete


class Indicators(unittest.TestCase):
    def test_inclusive_chill_boundaries(self):
        s=pd.Series([-1,0,7.2,7.21],index=pd.date_range('2020-01-01',periods=4,freq='h'))
        self.assertEqual(chill(s,'2020-01-01','2020-01-01 04:00'),2)
    def test_missing_hour_not_zero(self):
        s=pd.Series([1.,np.nan],index=pd.date_range('2020-01-01',periods=2,freq='h'))
        self.assertIsNone(chill(s,'2020-01-01','2020-01-01 02:00'))
    def test_cross_year_and_leap(self):
        s=pd.Series(5.,index=pd.date_range('2019-11-01','2020-03-01',freq='h',inclusive='left'))
        self.assertEqual(chill(s,'2019-11-01','2020-03-01'),121*24)
    def test_dry_runs(self):
        s=pd.Series([0,.9,1,0,0,0,2],index=pd.date_range('2020-01-01',periods=7))
        self.assertEqual(dry_spell(s,'2020-01-01','2020-01-08'),3)
        s.iloc[2]=1001
        self.assertIsNone(dry_spell(s,'2020-01-01','2020-01-08'))
    def test_missing_date(self):
        s=pd.Series([0],index=pd.date_range('2020-01-01',periods=1))
        self.assertIsNone(dry_spell(s,'2020-01-01','2020-01-03'))
    def test_duplicates(self):
        s=pd.Series([1,2],index=pd.to_datetime(['2020-01-01','2020-01-01']))
        with self.assertRaises(ValueError):complete(s,'2020-01-01','2020-01-02','D')


if __name__=='__main__':unittest.main()
