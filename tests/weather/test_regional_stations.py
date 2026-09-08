"""Guard the observation conventions used by the regional pilot."""
import unittest
import pandas as pd


class RegionalConventions(unittest.TestCase):
    def test_decimal_quality_flags(self):
        raw=pd.Series(['0','0.0','0.00','7.0','17.0',None])
        flags=raw.str.replace(r'\.0+$','',regex=True)
        self.assertEqual((flags=='0').tolist(),[True,True,True,False,False,False])

    def test_interval_ending_at_midnight(self):
        times=pd.date_range('2020-01-01 01:00','2020-01-02 00:00',freq='h',tz='UTC')
        hourly=pd.Series(range(24),index=times-pd.Timedelta(nanoseconds=1))
        self.assertEqual(hourly.resample('D').count().tolist(),[24])
        self.assertEqual(str(hourly.resample('D').min().index[0].date()),'2020-01-01')

    def test_complete_day_excludes_one_missing_sample(self):
        times=pd.date_range('2020-01-01',periods=96,freq='15min',tz='UTC')
        values=pd.Series(1.,index=times)
        self.assertTrue(values.resample('D').count().eq(96).iloc[0])
        values.iloc[12]=float('nan')
        self.assertFalse(values.resample('D').count().eq(96).iloc[0])


if __name__=='__main__':
    unittest.main()
