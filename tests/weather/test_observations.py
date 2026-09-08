import unittest
from validate_observations import parse_daily


class ObservationParsingTests(unittest.TestCase):
    def record(self, year=2020, element='PRCP', first='   12   '):
        return 'USW00012816'+str(year)+'02'+element+first+('-9999   '*30)

    def test_units_and_leap_day(self):
        frame=parse_daily(self.record(first='   12  W'))
        self.assertEqual(len(frame),29)
        self.assertEqual(frame.iloc[0].value,1.2)
        self.assertTrue(frame.iloc[0].accepted)
        self.assertFalse(frame.iloc[1].accepted)

    def test_quality_and_presumed_zero_excluded(self):
        for block in ['   12 XW','    0P W','   12L W']:
            self.assertFalse(parse_daily(self.record(first=block)).iloc[0].accepted)

    def test_flags_preserved(self):
        row=parse_daily(self.record(first='    0T W')).iloc[0]
        self.assertEqual(row.mflag,'T')
        self.assertEqual(row.sflag,'W')
        self.assertTrue(row.accepted)

    def test_nonleap_and_outside_baseline(self):
        self.assertEqual(len(parse_daily(self.record(year=2019))),28)
        self.assertTrue(parse_daily(self.record(year=2010)).empty)


if __name__=='__main__':
    unittest.main()
