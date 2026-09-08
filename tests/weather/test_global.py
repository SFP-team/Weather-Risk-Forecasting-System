import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

CODE = Path(__file__).resolve().parents[2] / 'pipelines/weather'
if not CODE.exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
import global_daily as g
from pilot import GROUPS, NAMES, digest


def fake_source(name):
    class Group(dict):
        attrs = {'version': 'synthetic-test-only'}
    group = Group()
    for variable in GROUPS[name]:
        unit = ('W m-2' if variable.startswith('ALLSKY') else 'C' if variable.startswith('T2M')
                else {'PRECTOTCORR': 'mm', 'RH2M': '%', 'WS2M': 'm/s'}[variable])
        group[variable] = SimpleNamespace(chunks=(4000, 2, 3), attrs={
            '_ARRAY_DIMENSIONS': ['time', 'lat', 'lon'], 'units': unit})
    return SimpleNamespace(name=name, lat=np.array([-1., 1.]), lon=np.array([-180., 0., 179.5]),
                           times=pd.date_range('2010-01-01', '2025-12-31'), group=group)


class GlobalTests(unittest.TestCase):
    def test_plan_gating_and_size(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'state').mkdir()
            (root / 'state/probes.json').write_text('{"status":"blocked"}')
            with self.assertRaises(RuntimeError):
                g.build_plan(root, None)
            (root / 'state/probes.json').write_text('{"status":"complete"}')
            with patch.object(g, 'Source', side_effect=lambda d, n: fake_source(n)):
                plan = g.build_plan(root, None)
            self.assertEqual(plan['job_count'], 8)
            self.assertEqual(plan['normalized_float32_bytes'], 5844*2*3*8*4)
            self.assertEqual(len({j['id'] for j in plan['jobs']}), 8)
            self.assertEqual(plan['status'], 'ready')

    def test_output_roundtrip_and_conflict(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = fake_source('met_daily')
            out = g.output_group(root, source)
            values = np.arange(5844*2*3, dtype='f4').reshape(5844, 2, 3)
            values[0, 0, 0] = np.nan
            out['tmean_c'][:] = values
            self.assertEqual(digest(out['tmean_c'][:].tobytes()), digest(values.tobytes()))
            reopened = g.output_group(root, source)
            self.assertEqual(digest(reopened['tmean_c'][:].tobytes()), digest(values.tobytes()))
            source.lat = np.array([-2., 1.])
            with self.assertRaises(RuntimeError):
                g.output_group(root, source)

    def test_probe_registry(self):
        self.assertEqual(len(g.PROBES), 40)
        self.assertEqual(len({p[0] for p in g.PROBES}), 40)
        self.assertTrue(all(-90 <= p[1] <= 90 and -180 <= p[2] <= 180 for p in g.PROBES))


if __name__ == '__main__':
    unittest.main()
