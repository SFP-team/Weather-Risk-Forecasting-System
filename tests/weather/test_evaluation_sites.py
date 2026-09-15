import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import numpy as np
import pandas as pd
from evaluation_sites import cell_key, hourly_index
from location_api import hourly_for

AXES = {'lat': [-90 + .5 * i for i in range(361)], 'lon': [-180 + .625 * j for j in range(576)]}


class EvaluationSiteTests(unittest.TestCase):
    def test_cell_key_matches_stored_pilot_cells(self):
        self.assertEqual(cell_key(AXES, 28.05562, -81.56122), '236,158')   # Dole, as recorded on the server
        self.assertEqual(cell_key(AXES, 27.547, -81.811), '235,157')       # Wauchula shares River Valley's cell
        self.assertEqual(cell_key(AXES, 27.221, -81.868), '234,157')       # Arcadia is a new cell

    def root(self, rows=140256):
        directory = tempfile.TemporaryDirectory()
        root = Path(directory.name)
        site = root / 'data/normalized/pilot/pilot/UF_X'
        site.mkdir(parents=True)
        pd.DataFrame({'time': pd.date_range('2010-01-01', periods=rows, freq='h'), 'tmean_c': 5.}).to_parquet(site / 'met_hourly.parquet', index=False)
        sha = hashlib.sha256((site / 'met_hourly.parquet').read_bytes()).hexdigest()
        (site / 'met_hourly.json').write_text(json.dumps({'site': {'id': 'UF_X', 'name': 'X'}, 'source_indices': [235, 157],
            'source_lat': 27.5, 'source_lon': -81.875, 'rows': rows, 'start': '2010-01-01', 'end': '2025-12-31', 'parquet_sha256': sha}))
        (root / 'config').mkdir()
        (root / 'config/hourly_index.json').write_text(json.dumps(hourly_index(root, AXES)))
        return directory, root

    def test_pin_inside_stored_cell_reuses_series_and_reports_sharing(self):
        keep, root = self.root()
        series, source = hourly_for(27.547, -81.811, root)
        self.assertEqual(len(series), 140256)
        self.assertEqual(source['site'], 'X')
        self.assertGreater(source['distance_km'], 5)
        self.assertIsNone(hourly_for(27.221, -81.868, root)[0])
        keep.cleanup()

    def test_incomplete_series_is_not_indexed(self):
        keep, root = self.root(rows=1000)
        self.assertEqual(hourly_index(root, AXES)['cells'], {})
        keep.cleanup()

    def test_tampered_series_is_refused(self):
        keep, root = self.root()
        path = root / 'data/normalized/pilot/pilot/UF_X/met_hourly.parquet'
        path.write_bytes(path.read_bytes() + b'\0')
        with self.assertRaises(RuntimeError):
            hourly_for(27.547, -81.811, root)
        keep.cleanup()


if __name__ == '__main__':
    unittest.main()
