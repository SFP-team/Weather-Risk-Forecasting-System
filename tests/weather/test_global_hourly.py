from pathlib import Path
import sqlite3
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[2] / 'pipelines/weather'
if not CODE.exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
import global_hourly as g


def fake_source(end='2026-01-01', chunks=(8, 2, 2)):
    class Group(dict):
        attrs = {'version': 'synthetic-test-only'}
    group = Group()
    for variable in ('T2M', 'T2MDEW'):
        group[variable] = SimpleNamespace(chunks=chunks, attrs={
            '_ARRAY_DIMENSIONS': ['time', 'lat', 'lon'], 'units': 'C'})
    times = pd.date_range('2009-12-01', end, freq='h', inclusive='left')
    return SimpleNamespace(name='met_hourly', lat=np.array([-1., 0., 1.]),
                           lon=np.array([-180., -100., 0., 100.]), times=times, group=group)


class EastLand:
    """Land only where lon >= 0: blocks [x 0:2] are ocean, [x 2:4] contain land."""
    metadata = {'version': 'synthetic'}

    def covers(self, lat, lon):
        return lon >= 0


def fake_downloads(directory):
    db = sqlite3.connect(Path(directory) / 'jobs.sqlite')
    db.execute('CREATE TABLE objects (url TEXT, path TEXT, status TEXT, bytes INTEGER)')
    return SimpleNamespace(db=db)


class GlobalHourlyTests(unittest.TestCase):
    def test_plan_keeps_only_land_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'state').mkdir()
            with patch.object(g, 'Source', side_effect=lambda d, n: fake_source()), \
                    patch.object(g, 'LandMask', side_effect=lambda r: EastLand()):
                plan = g.build_plan(root, fake_downloads(directory))
            # lat blocks: [0:2], [2:3]; lon blocks: [0:2] ocean, [2:4] land -> 2 land blocks x 2 variables
            self.assertEqual(plan['land_blocks'], 2)
            self.assertEqual(plan['total_blocks'], 4)
            self.assertEqual(plan['job_count'], 4)
            self.assertTrue(all(j['x'] == [2, 4] for j in plan['jobs']))
            self.assertEqual({j['variable'] for j in plan['jobs']}, {'T2M', 'T2MDEW'})
            self.assertEqual(plan['time_slice'][1] - plan['time_slice'][0], g.HOURS)
            self.assertEqual(plan['status'], 'ready')
            self.assertIsNone(plan['estimated_compressed_bytes'])

    def test_plan_refuses_wrong_time_extent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            short = fake_source(end='2025-12-31')
            with patch.object(g, 'Source', side_effect=lambda d, n: short), \
                    patch.object(g, 'LandMask', side_effect=lambda r: EastLand()):
                with self.assertRaises(RuntimeError):
                    g.build_plan(root, fake_downloads(directory))


if __name__ == '__main__':
    unittest.main()
