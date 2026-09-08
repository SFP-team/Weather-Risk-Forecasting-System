import importlib.util
from pathlib import Path
import sys
import unittest

import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[2] / 'pipelines/weather'
if not CODE.exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
from pilot import canonical, nearest_indices, quality, digest


class PilotTests(unittest.TestCase):
    def test_solar_units(self):
        np.testing.assert_allclose(canonical([100], 'ALLSKY_SFC_SW_DWN', 'W m-2'), [8.64])
        np.testing.assert_allclose(canonical([1], 'ALLSKY_SFC_SW_DWN', 'kW-hr/m^2/day'), [3.6])

    def test_unknown_units_fail(self):
        with self.assertRaises(ValueError):
            canonical([270], 'T2M', 'K')

    def test_missing_not_zero(self):
        q = quality(pd.DataFrame({'precip_mm': [np.nan, 0., 2.]}))
        self.assertEqual(q['precip_mm']['missing'], 1)
        self.assertEqual(q['precip_mm']['valid'], 2)

    def test_invalid_physics(self):
        with self.assertRaises(ValueError):
            quality(pd.DataFrame({'precip_mm': [-1.]}))
        with self.assertRaises(ValueError):
            quality(pd.DataFrame({'tmin_c': [10.], 'tmean_c': [5.], 'tmax_c': [12.]}))

    def test_dateline(self):
        self.assertEqual(nearest_indices(np.array([0]), np.array([-180., 0., 179.375]), 0, 180), (0, 0))

    def test_invalid_coordinate(self):
        with self.assertRaises(ValueError):
            nearest_indices(np.array([0]), np.array([0]), 95, 0)

    def test_period_counts(self):
        self.assertEqual(len(pd.date_range('2010-01-01', '2025-12-31')), 5844)
        self.assertEqual(len(pd.date_range('2011-01-01', '2025-12-31')), 5479)
        self.assertEqual(len(pd.date_range('2020-01-01', '2020-12-31 23:00', freq='h')), 8784)

    def test_timestamp_precision(self):
        decoded = pd.DatetimeIndex(np.datetime64('2020-01-01 00:00:00') + np.arange(366).astype('timedelta64[D]')).as_unit('ns')
        self.assertTrue(decoded.equals(pd.date_range('2020-01-01', '2020-12-31')))

    def test_digest(self):
        self.assertEqual(digest(b'abc'), 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad')


if __name__ == '__main__':
    unittest.main()
