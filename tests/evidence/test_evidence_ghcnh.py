"""GHCNh adapter: parsers on real NCEI samples, station selection geometry and request planning."""
import contextlib
import datetime as dt
import functools
import io
import json
import os
import shutil
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import pandas as pd
from evidence import runner
from evidence.adapters import ghcnh_stations as g

FIX = Path(__file__).resolve().parent/'fixtures'


class Parsers(unittest.TestCase):
    def test_psv_hamilton_frost_night(self):
        # Real Hamilton AWS rows; NIWA reported the 7 October 2022 frost (night of 6 to 7 October NZDT).
        t = g.read_station_file(FIX/'ghcnh_NZM00093173_2022-10-05_07.psv')
        self.assertEqual(len(t), 72)
        self.assertEqual(str(t.time_utc.dt.tz), 'UTC')
        self.assertEqual(set(t.station_id), {'NZM00093173'})
        coldest = t.loc[t.temperature_c.idxmin()]
        self.assertEqual((coldest.time_utc.isoformat(), coldest.temperature_c), ('2022-10-06T18:00:00+00:00', -2.8))
        self.assertTrue(t.temperature_qc_pass.all())
        self.assertEqual(set(t.temperature_qc), {'1'})
        self.assertTrue(t.relative_humidity_pct.between(1, 100).all())

    def test_parquet_alma_subhourly_codes(self):
        t = g.read_station_file(FIX/'ghcnh_USW00013870_2022-03-11_14.parquet')
        self.assertTrue(t.time_utc.is_monotonic_increasing)
        self.assertIn(53, set(t.time_utc.dt.minute))
        self.assertTrue(t.temperature_qc.dropna().isin(['1', '5', 'A', 'P']).all())
        self.assertTrue(t.temperature_qc_pass[t.temperature_c.notna()].all())
        self.assertFalse(t.temperature_qc_pass[t.temperature_c.isna()].any())
        self.assertLess(t.temperature_c.min(), 0)

    def test_null_quality_code_is_blank(self):
        t = g.read_station_file(FIX/'ghcnh_CIN00360011_2018-10-01_02.parquet')
        self.assertEqual(len(t), 48)
        self.assertTrue(t.temperature_qc.isna().all())
        self.assertTrue(t.temperature_qc_pass[t.temperature_c.notna()].all())

    def test_quality_rules(self):
        codes = pd.Series(['1', '5', '5', 'A', None, 'Null', 'c', 's', '2', '7', '0'])
        sources = pd.Series(['220', '343', '220', '343', '343', '333', '343', '343', '313', '313', '220'])
        ok = g.temperature_ok(codes.where(codes != 'Null'), sources)
        self.assertEqual(ok.tolist(), [True, True, False, True, True, True, False, False, False, False, True])

    def test_station_list_and_inventory(self):
        st = g.read_station_list(FIX/'ghcnh_station_list_sample.csv')
        self.assertEqual(len(st), 10)
        self.assertTrue(pd.isna(st.set_index('station_id').loc['CIN00360011', 'elevation_m']))
        inv = g.read_inventory(FIX/'ghcnh_inventory_sample.txt', 2010, 2026)
        self.assertNotIn(2009, inv['ASN00091126'])
        self.assertEqual(inv['ASN00091126'][2015], 8756)
        self.assertNotIn(2019, inv['CIN00360011'])
        self.assertNotIn('CIA00856571', inv)
        self.assertEqual(min(inv['NZM00093173']), 2021)


def stations(rows):
    return pd.DataFrame([{'station_id': s, 'name': s, 'lat': la, 'lon': lo, 'elevation_m': 0., 'wmo_id': '', 'country': ''}
                         for s, la, lo in rows])


def pin(pid, lat, lon):
    return {'pin_id': pid, 'pin_name': pid, 'pin_source': 'benchmark', 'pin_lat': lat, 'pin_lon': lon}


class Selection(unittest.TestCase):
    def test_haversine(self):
        self.assertAlmostEqual(float(g.haversine_km(0, 0, 1, 0)), 111.195, places=2)
        self.assertAlmostEqual(float(g.haversine_km(0, 179.9, 0, -179.9)), 22.239, places=2)

    def test_radius_fallback_and_data_filter(self):
        st = stations([('A', 0.1, 0), ('B', 0.2, 0), ('C', 0.3, 0), ('NODATA', 0.01, 0),
                       ('D', 10.4, 0), ('E', 20.5, 0)])
        inv = {s: {2020: 8000} for s in 'ABCDE'}
        meta = g.select(st, [pin('p1', 0, 0), pin('p2', 10, 0), pin('p3', 20, 0)], inv, events={})
        got = {(r.pin_id, r.station_id, r.rule) for r in meta.itertuples()}
        # A 11.1 km, B 22.2 km in; C 33.4 km out; D 44.5 km is the fallback; E 55.6 km is beyond 50 km.
        self.assertEqual(got, {('p1', 'A', 'within_25km'), ('p1', 'B', 'within_25km'), ('p2', 'D', 'nearest_within_50km')})
        self.assertAlmostEqual(meta.set_index('station_id').loc['A', 'distance_km'], 11.12, places=2)

    def test_fallback_skips_stations_without_temperature(self):
        st = stations([('PRECIP', 10.3, 0), ('T', 10.44, 0), ('NEAR_PRECIP', 0.1, 0), ('NEAR_T', 0.2, 0)])
        inv = {s: {2020: 8000} for s in ('PRECIP', 'T', 'NEAR_PRECIP', 'NEAR_T')}
        meta = g.select(st, [pin('p1', 0, 0), pin('p2', 10, 0)], inv, events={}, exclude=['PRECIP', 'NEAR_PRECIP'])
        self.assertEqual(set(zip(meta.pin_id, meta.station_id)), {('p1', 'NEAR_T'), ('p2', 'T')})
        self.assertLess(meta.set_index('station_id').loc['T', 'distance_km'], 50)

    def test_event_stations_always_attached(self):
        st = stations([('NEAR', 0.05, 0), ('EV30', 0.27, 0), ('EVFAR', 5, 0), ('EVNONE', 0.01, 0)])
        inv = {'NEAR': {2020: 8000}, 'EV30': {2020: 8000}}
        meta = g.select(st, [pin('p1', 0, 0)], inv, events={'EV30': 'x', 'EVFAR': 'y', 'EVNONE': 'z', 'MISSING': 'w'})
        rules = dict(zip(meta.station_id, meta.rule))
        self.assertEqual(rules, {'NEAR': 'within_25km', 'EV30': 'event_station', 'EVFAR': 'event_station', 'EVNONE': 'event_station'})
        self.assertTrue(meta.set_index('station_id').loc[['EV30', 'EVFAR', 'EVNONE'], 'event_station'].all())
        self.assertEqual(meta.set_index('station_id').loc['EVNONE', 'inventory_years'], 0)

    def test_year_plan_lag_years_and_cap(self):
        meta = pd.DataFrame({'station_id': ['A', 'B'], 'distance_km': [5., 1.]})
        inv = {'A': {2010: 100, 2011: 100}, 'B': {2024: 100}}
        years, est, capped = g.year_plan(meta, inv, dt.date(2026, 10, 12))
        self.assertEqual(years, [('B', 2024), ('B', 2025), ('B', 2026), ('A', 2010), ('A', 2011)])
        self.assertFalse(capped)
        years, est, capped = g.year_plan(meta, inv, dt.date(2026, 10, 12), cap=150*g.BYTES_PER_RECORD)
        self.assertEqual((years, capped), ([('B', 2024)], True))


class Asset(SimpleNamespace):
    pass


def write_pins(root, benchmark=None):
    (root/'code').mkdir(parents=True)
    (root/'config').mkdir()
    (root/'code/benchmark_sites.json').write_text(json.dumps({'sites': benchmark or [
        {'id': 'nz-waikato-ohaupo', 'name': 'Ohaupo', 'lat': -37.9236, 'lon': 175.3067},
        {'id': 'au-tas-penguin', 'name': 'Penguin', 'lat': -41.1204, 'lon': 146.0722}]}))
    (root/'config/sites.json').write_text(json.dumps([{'id': 'UF_Georgia', 'name': 'Georgia', 'lat': 31.511125, 'lon': -82.460729}]))
    (root/'config/evaluation_sites.json').write_text(json.dumps([
        {'id': 'UF_Georgia', 'name': 'Georgia', 'lat': 31.511125, 'lon': -82.460729},
        {'id': 'EVAL_Homerville', 'name': 'Homerville', 'lat': 31.037, 'lon': -82.747}]))


class PlanAndParse(unittest.TestCase):
    def ctx(self, root):
        fetched = {'station-list': FIX/'ghcnh_station_list_sample.csv', 'inventory': FIX/'ghcnh_inventory_sample.txt'}
        logs = []
        tables = {}
        ctx = SimpleNamespace(root=root, today=dt.date(2026, 10, 12), force=False, state={}, logs=logs, tables=tables,
                              paths=SimpleNamespace(raw=root/'code'),
                              log=lambda event, **f: logs.append((event, f)),
                              fetch=lambda r: Asset(key=r.key, path=fetched[r.key], status='fetched', changed=True),
                              write_table=lambda name, df: tables.__setitem__(name, df.copy()))
        return ctx

    def test_plan_drops_stations_learned_to_lack_temperature(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pins(root)
            ctx = self.ctx(root)
            ctx.state['stations'] = {'USI0000KBHC': {'files': 3, 'temperature_rows': 0},
                                     'USW00000128': {'files': 0, 'temperature_rows': 0}}
            keys = {r.key.split('.')[0] for r in g.plan(ctx)}
            self.assertNotIn('USI0000KBHC', keys)
            self.assertIn('USW00000128', keys)  # never read, so not yet known to lack temperature

    def test_plan_then_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_pins(root)
            ctx = self.ctx(root)
            requests = g.plan(ctx)
            meta = pd.DataFrame(ctx.state['selection']['meta'])
            pairs = set(zip(meta.pin_id, meta.station_id))
            self.assertIn(('nz-waikato-ohaupo', 'NZM00093173'), pairs)
            self.assertIn(('au-tas-penguin', 'ASN00091009'), pairs)
            self.assertIn(('au-tas-penguin', 'ASN00091126'), pairs)  # Devonport Airport, an event station beyond 25 km
            self.assertIn(('EVAL_Homerville', 'USW00000128'), pairs)
            self.assertEqual(meta.pin_id.nunique(), 4)
            keys = {r.key for r in requests}
            self.assertIn('NZM00093173.2022', keys)
            self.assertNotIn('NZM00093173.2020', keys)
            self.assertTrue(all(r.optional for r in requests))
            r = next(r for r in requests if r.key == 'NZM00093173.2022')
            self.assertEqual(r.url, g.BASE+'access/by-year/2022/parquet/GHCNh_NZM00093173_2022.parquet')
            self.assertEqual(r.filename, 'by-year/2022/GHCNh_NZM00093173_2022.parquet')
            assets = {'station-list': Asset(path=FIX/'ghcnh_station_list_sample.csv', status='unchanged', changed=False),
                      'NZM00093173.2022': Asset(path=FIX/'ghcnh_NZM00093173_2022-10-05_07.psv', status='fetched', changed=True),
                      'NZM00093173.2023': Asset(path=None, status='missing', changed=False),
                      'USW00013870.2022': Asset(path=FIX/'ghcnh_USW00013870_2022-03-11_14.parquet', status='unchanged', changed=False)}
            summary = g.parse(ctx, assets)
            self.assertEqual(len(ctx.tables['hourly_NZM00093173']), 72)
            self.assertIn('hourly_USW00013870', ctx.tables)
            sm = ctx.tables['station_meta'].set_index('station_id')
            self.assertEqual(int(sm.loc['NZM00093173', 'rows']), 72)
            self.assertEqual(summary['station_years_missing'], 1)
            self.assertEqual(ctx.state['stations']['NZM00093173']['missing_years'], [2023])
            ctx.tables.clear()
            g.parse(ctx, {k: Asset(**{**vars(a), 'changed': False}) for k, a in assets.items()})
            self.assertEqual(set(ctx.tables), {'station_meta'})


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class RunnerEndToEnd(unittest.TestCase):
    """Full job through the runner against a local server laid out like the NCEI bucket."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        www = base/'www'
        layout = {'doc/ghcnh-station-list.csv': 'ghcnh_station_list_sample.csv',
                  'doc/ghcnh-inventory.txt': 'ghcnh_inventory_sample.txt',
                  'access/by-year/2022/parquet/GHCNh_USW00013870_2022.parquet': 'ghcnh_USW00013870_2022-03-11_14.parquet',
                  'access/by-year/2018/parquet/GHCNh_CIN00360011_2018.parquet': 'ghcnh_CIN00360011_2018-10-01_02.parquet'}
        for rel, name in layout.items():
            (www/rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(FIX/name, www/rel)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(www)))
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{self.server.server_address[1]}/'
        self.root = base/'root'
        write_pins(self.root, [{'id': 'cl-chillan-nuble', 'name': 'Chillán', 'lat': -36.6066, 'lon': -72.1034}])
        self.patches = [mock.patch.object(g, 'BASE', url), mock.patch.object(g, 'STATION_LIST', url+'doc/ghcnh-station-list.csv'),
                        mock.patch.object(g, 'INVENTORY', url+'doc/ghcnh-inventory.txt'),
                        mock.patch.object(runner, 'MIN_HOST_INTERVAL', 0), mock.patch.object(runner, '_sleep', lambda s: None),
                        mock.patch.dict(os.environ, {'EVIDENCE_ROOT': str(self.root)})]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.server.shutdown()
        self.server.server_close()
        self.tmp.cleanup()

    def test_backfill_then_unchanged(self):
        with contextlib.redirect_stdout(io.StringIO()):
            code = runner.run_job(g, root=self.root)
        self.assertEqual(code, 0)
        derived = self.root/'data/evidence/derived/ghcnh-stations'
        alma = pd.read_parquet(derived/'hourly_USW00013870.parquet')
        pd.testing.assert_frame_equal(alma, g.read_station_file(FIX/'ghcnh_USW00013870_2022-03-11_14.parquet'))
        chillan = pd.read_parquet(derived/'hourly_CIN00360011.parquet')
        self.assertEqual(len(chillan), 48)
        meta = pd.read_parquet(derived/'station_meta.parquet')
        self.assertLessEqual({'CIN00360011', 'CIA00856571'}, set(meta.loc[meta.pin_id == 'cl-chillan-nuble', 'station_id']))
        state = json.loads((self.root/'state/evidence/ghcnh-stations.json').read_text())
        self.assertEqual(state['adapter']['summary']['stations_with_temperature'], 2)
        self.assertTrue((self.root/'data/evidence/raw/ghcnh-stations/by-year/2022/GHCNh_USW00013870_2022.parquet').exists())
        before = (derived/'hourly_USW00013870.parquet').stat().st_mtime_ns
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.run_job(g, root=self.root), 0)
        state = json.loads((self.root/'state/evidence/ghcnh-stations.json').read_text())
        self.assertEqual(state['last_run']['outcome'], 'unchanged')
        self.assertEqual((derived/'hourly_USW00013870.parquet').stat().st_mtime_ns, before)


if __name__ == '__main__':
    unittest.main()
