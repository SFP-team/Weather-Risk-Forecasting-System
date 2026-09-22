import hashlib
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import zarr

from discover import BASE, STORES
from hourly_archive import hourly_from_cache
from location_api import hourly_for


class HourlyArchiveTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.cache = self.root / 'data/raw/zarr/met_hourly'
        group = zarr.open_group(str(self.cache), mode='w')
        for name, values in [('lat', [43., 43.5]), ('lon', [-180., -92.5]), ('time', np.arange(140256))]:
            array = group.create_dataset(name, data=np.asarray(values), chunks=(len(values),))
            array.attrs['_ARRAY_DIMENSIONS'] = [name]
            if name == 'time':
                array.attrs['units'] = 'hours since 2010-01-01 00:00:00'
        for name, value in [('T2M', 5.), ('T2MDEW', 2.)]:
            array = group.create_dataset(name, shape=(140256, 2, 2), chunks=(70128, 1, 1), dtype='f4', fill_value=np.nan)
            array[:] = value
            array[:, 1, :] = value + 1
            array.attrs.update({'_ARRAY_DIMENSIONS': ['time', 'lat', 'lon'], 'units': 'C'})
        zarr.consolidate_metadata(str(self.cache))
        (self.root / 'state').mkdir()
        self.db = sqlite3.connect(self.root / 'state/jobs.sqlite')
        self.addCleanup(self.db.close)
        self.db.execute('CREATE TABLE objects (url TEXT PRIMARY KEY, status TEXT, sha256 TEXT)')
        self.register()

    def register(self):
        for path in self.cache.rglob('*'):
            if path.is_file():
                url = BASE + STORES['met_hourly'] + '/' + path.relative_to(self.cache).as_posix()
                self.db.execute('INSERT OR REPLACE INTO objects VALUES (?,?,?)',
                                (url, 'downloaded', hashlib.sha256(path.read_bytes()).hexdigest()))
        self.db.commit()

    def test_unindexed_cell_and_padding_without_network_or_state_changes(self):
        before = self.db.execute('SELECT * FROM objects ORDER BY url').fetchall()
        with patch('requests.sessions.Session.request', side_effect=AssertionError('Network forbidden')):
            values, source = hourly_for(43.06, -92.55, self.root)
            nearby, other = hourly_from_cache(self.root, 43.1, -92.6)
        self.assertTrue(values.index.equals(pd.date_range('2010-01-01', '2026-01-01', freq='h', inclusive='left', name='time')))
        self.assertTrue((values == 5.).all())
        pd.testing.assert_series_equal(values, nearby)
        self.assertEqual(source['sha256'], other['sha256'])
        self.assertEqual((source['source_lat'], source['source_lon']), (43., -92.5))
        self.assertEqual(before, self.db.execute('SELECT * FROM objects ORDER BY url').fetchall())

    def test_dateline_wrap_and_distinct_latitude_cell(self):
        values, source = hourly_from_cache(self.root, 43.49, 180.)
        self.assertTrue((values == 6.).all())
        self.assertEqual((source['source_lat'], source['source_lon']), (43.5, -180.))

    def test_missing_chunk_is_not_zarr_fill(self):
        (self.cache / 'T2M/0.0.1').unlink()
        with self.assertRaises(RuntimeError):
            hourly_from_cache(self.root, 43., -92.5)

    def test_corrupt_chunk_is_refused(self):
        path = self.cache / 'T2M/0.0.1'
        path.write_bytes(path.read_bytes() + b'corruption')
        with self.assertRaises(RuntimeError):
            hourly_from_cache(self.root, 43., -92.5)

    def test_valid_checksum_does_not_make_missing_weather_complete(self):
        group = zarr.open_group(str(self.cache), mode='a')
        group['T2M'][0, 0, 1] = np.nan
        self.register()
        with self.assertRaises(RuntimeError):
            hourly_from_cache(self.root, 43., -92.5)

    def test_no_installed_archive_remains_unavailable(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(hourly_from_cache(Path(empty), 43., -92.5), (None, None))


if __name__ == '__main__':
    unittest.main()
