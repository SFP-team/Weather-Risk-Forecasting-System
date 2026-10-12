"""ODEPA adapters: orchard census species filter, export tariff-line filter and both jobs through the runner."""
import functools
import http.server
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
import pandas as pd
from evidence import runner
from evidence.adapters import odepa_catastro as cat, odepa_exports as exp

FIX = Path(__file__).resolve().parent/'fixtures'


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Serve:
    """Local http.server over a folder, so the runner fetches without network access."""
    def __init__(self, folder):
        self.httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(folder)))
        self.url = f'http://127.0.0.1:{self.httpd.server_address[1]}/'
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown(); self.httpd.server_close()


def package(base, names):
    return {'success': True, 'result': {'license_id': 'cc-by', 'resources': [
        {'id': f'r{i}', 'format': 'CSV', 'name': name, 'url': base + file} for i, (name, file) in enumerate(names)]}}


class Catastro(unittest.TestCase):
    def test_species_filter_folds_accents_case_and_spaces(self):
        for s in ['Arándano Americano', 'ARANDANO AMERICANO', 'arándano  americano ', 'Arándano', 'ARÁNDANO']:
            self.assertTrue(cat.is_blueberry(s), s)
        for s in ['Arándano Rojo', 'Frambuesa', 'Mandarino', 'Naranjo', '']:
            self.assertFalse(cat.is_blueberry(s), s)

    def test_number_parsing(self):
        got = cat.number(pd.Series(['0,25', '1.002,50', '6067', '', None])).tolist()
        self.assertEqual(got[:3], [0.25, 1002.5, 6067])
        self.assertTrue(pd.isna(got[3]) and pd.isna(got[4]))

    def test_blocks_and_summary(self):
        b = cat.blueberry_blocks(cat.read_csv(FIX/'odepa_catastro_sample.csv'))
        self.assertEqual(len(b), 7)
        self.assertNotIn('Frambuesa', set(b.species))
        self.assertEqual(str(b.planting_year.dtype), 'Int64')
        co = b[b.commune == 'Coihueco']
        self.assertEqual(len(co), 6)
        self.assertAlmostEqual(float(co.area_ha.sum()), 1006.02, places=6)
        s = cat.summarise(b).set_index(['commune', 'variety'])
        self.assertEqual(int(s.loc[('Coihueco', 'Duke'), 'blocks']), 4)
        self.assertEqual(int(s.loc[('Coihueco', 'Duke'), 'farms']), 2)
        self.assertAlmostEqual(float(s.loc[('Coihueco', 'Duke'), 'area_ha']), 3.12, places=6)
        self.assertEqual(int(s.loc[('Coihueco', 'Duke'), 'plants']), 1190 + 1267 + 2231 + 6067)

    def test_missing_column_is_an_error(self):
        raw = cat.read_csv(FIX/'odepa_catastro_sample.csv').drop(columns=['Superficie (ha)'])
        with self.assertRaises(ValueError):
            cat.blueberry_blocks(raw)


class Exports(unittest.TestCase):
    def test_tariff_lines(self):
        self.assertEqual(exp.line_scope('08104029', 'Los demás arándanos azules o blueberry, frescos'), 'blueberry')
        self.assertEqual(exp.line_scope('08104021', 'x'), 'blueberry')
        self.assertEqual(exp.line_scope('08104020', 'x'), 'blueberry')
        self.assertEqual(exp.line_scope('08104000', 'x'), 'vaccinium_total')
        self.assertEqual(exp.line_scope('08104031', 'Arándanos azules o blueberry, frescos (desde 2030)'), 'blueberry')
        for code, product in [('08104019', 'Los demás arándanos rojos, frescos'), ('08104099', 'Mirtilos y demás frutos'),
                              ('08119019', 'Los demás arándanos, congelados'), ('08134049', 'Los demás arándanos secos')]:
            self.assertIsNone(exp.line_scope(code, product), code)

    def test_rows(self):
        r = exp.blueberry_rows(exp.read_csv(FIX/'odepa_exports_sample.csv'))
        self.assertEqual(len(r), 10)
        self.assertEqual(set(r.code), {'08104000', '08104020', '08104021', '08104029'})
        nl = r[(r.year == 2025) & (r.destination == 'Países Bajos')].iloc[0]
        self.assertEqual((nl.month, nl.region, nl.line_scope, bool(nl.organic)), (1, 'Maule', 'blueberry', False))
        self.assertAlmostEqual(nl.tonnes, 3146.2447, places=6)
        self.assertAlmostEqual(nl.usd_fob, 12271728.72, places=4)
        unspecified = r[r.unit == 'sin especificar'].iloc[0]
        self.assertTrue(pd.isna(unspecified.tonnes))
        self.assertEqual(unspecified.usd_fob, 13019.0)
        self.assertEqual(int(r.organic.sum()), 2)


class ThroughRunner(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)/'root'
        self.web = Path(self.tmp.name)/'web'
        self.web.mkdir()
        self.server = Serve(self.web)
        for p in [mock.patch.object(runner, 'MIN_HOST_INTERVAL', 0), mock.patch.object(runner, '_sleep', lambda s: None)]:
            p.start(); self.addCleanup(p.stop)

    def tearDown(self):
        self.server.close(); self.tmp.cleanup()

    def derived(self, job, name):
        return pd.read_parquet(self.root/'data/evidence/derived'/job/f'{name}.parquet')

    def test_catastro_job(self):
        (self.web/'catastro_2024.csv').write_bytes((FIX/'odepa_catastro_sample.csv').read_bytes())
        meta = package(self.server.url, [('Catastro frutícola ODEPA - CIREN año 2024', 'catastro_2024.csv')])
        (self.web/'package.json').write_text(json.dumps(meta))
        with mock.patch.object(cat, 'PACKAGE', self.server.url + 'package.json'):
            self.assertEqual(runner.run_job(cat, root=self.root), 0)
            self.assertTrue((self.root/'data/evidence/raw/odepa-catastro/catastro_fruticola_2024.csv').is_file())
            b = self.derived('odepa-catastro', 'catastro_blueberry_blocks')
            self.assertEqual(len(b), 7)
            s = self.derived('odepa-catastro', 'catastro_blueberry_summary')
            self.assertEqual(int(s[s.commune == 'Coihueco'].blocks.sum()), 6)
            state = json.loads((self.root/'state/evidence/odepa-catastro.json').read_text())
            self.assertEqual(state['last_run']['summary']['blueberry_species_names'],
                             {'Arándano Americano': 4, 'ARANDANO AMERICANO': 1, 'arándano  americano ': 1, 'Arándano': 1})
            # Nothing changed upstream: the second run is unchanged and does not parse again.
            self.assertEqual(runner.run_job(cat, root=self.root), 0)
            state = json.loads((self.root/'state/evidence/odepa-catastro.json').read_text())
            self.assertFalse(state['last_run']['parsed'])

    def test_exports_job_skips_import_files(self):
        (self.web/'exp_2025.csv').write_bytes((FIX/'odepa_exports_sample.csv').read_bytes())
        meta = package(self.server.url, [('Exportaciones del año 2025', 'exp_2025.csv'), ('Importaciones del año 2025', 'imp_2025.csv')])
        (self.web/'package.json').write_text(json.dumps(meta))
        with mock.patch.object(exp, 'PACKAGE', self.server.url + 'package.json'):
            self.assertEqual(runner.run_job(exp, root=self.root), 0)
        m = self.derived('odepa-exports', 'exports_blueberry_monthly')
        self.assertEqual(len(m), 10)
        by_region = self.derived('odepa-exports', 'exports_blueberry_region_monthly')
        maule = by_region[(by_region.year == 2025) & (by_region.month == 1) & (by_region.region == 'Maule')].iloc[0]
        self.assertAlmostEqual(maule.tonnes, 1.8 + 3146.2447 + 168.01681, places=6)
        self.assertFalse((self.root/'data/evidence/raw/odepa-exports/comex_importacion_2025.csv').exists())


if __name__ == '__main__':
    unittest.main()
