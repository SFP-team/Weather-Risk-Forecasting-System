"""Comext adapter: JSON-stat decoding on a real DS-045409 response, request splitting and the job through the runner."""
import http.server
import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import parse_qs, urlsplit
import pandas as pd
from evidence import runner
from evidence.adapters import comext_blueberry as c

FIX = Path(__file__).resolve().parent/'fixtures'
SAMPLE = json.loads((FIX/'comext_ds045409_eu27_sample.json').read_text())


class JsonStat(unittest.TestCase):
    def test_real_response(self):
        # EU27 imports of CN 08104050, September to November 2024; Serbia was asked for but has no cells.
        t = c.imports_table(SAMPLE)
        self.assertEqual(len(t), 6)
        self.assertEqual(set(t.partner), {'PE', 'ZW'})
        pe = t[(t.partner == 'PE') & (t.period == '2024-10')].iloc[0]
        self.assertEqual((pe.reporter, pe['product'], pe.year, pe.month), ('EU27_2020', '08104050', 2024, 10))
        self.assertAlmostEqual(pe.quantity_100kg, 122024.21)
        self.assertAlmostEqual(pe.tonnes, 12202.421)
        self.assertEqual(pe.value_eur, 109929373)
        zw = t[t.partner == 'ZW'].set_index('month').tonnes
        self.assertEqual(zw.idxmax(), 10)

    def test_array_values_and_status_flags(self):
        doc = {'id': ['reporter', 'partner', 'indicators', 'time'], 'size': [1, 1, 2, 2],
               'dimension': {'reporter': {'category': {'index': {'NL': 0}}}, 'partner': {'category': {'index': {'CL': 0}}},
                             'indicators': {'category': {'index': {'VALUE_IN_EUROS': 0, 'QUANTITY_IN_100KG': 1}}},
                             'time': {'category': {'index': ['2023-01', '2023-02']}}},
               'value': [100, None, 5.5, None], 'status': {'0': 'c'}}
        long = c.jsonstat_frame(doc)
        self.assertEqual(len(long), 2)
        self.assertEqual(long.iloc[0].to_dict(), {'reporter': 'NL', 'partner': 'CL', 'indicators': 'VALUE_IN_EUROS',
                                                  'time': '2023-01', 'value': 100, 'flag': 'c'})
        self.assertEqual(long.iloc[1][['indicators', 'time', 'value']].tolist(), ['QUANTITY_IN_100KG', '2023-01', 5.5])

    def test_not_a_dataset(self):
        with self.assertRaises(ValueError):
            c.jsonstat_frame({'warning': {'status': 413, 'label': 'asynchronous'}})

    def test_plan_splits_by_reporter_within_sync_limit(self):
        reqs = c.plan(None)
        self.assertEqual([r.params['reporter'] for r in reqs], c.REPORTERS)
        self.assertEqual(len({r.filename for r in reqs}), len(reqs))
        months = (2026 - 2010 + 1) * 12
        for r in reqs:
            self.assertNotIn(r.params['reporter'], r.params['partner'])
            self.assertLess(len(r.params['partner']) * len(r.params['indicators']) * months, 500_000)
            self.assertEqual((r.params['product'], r.params['flow'], r.params['sinceTimePeriod']), ('08104050', '1', '2010-01'))


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlsplit(self.path).query)
        doc = json.loads(json.dumps(SAMPLE))
        doc['dimension']['reporter']['category'] = {'index': {q['reporter'][0]: 0}, 'label': {}}
        body = json.dumps(doc).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def log_message(self, *a):
        pass


class ThroughRunner(unittest.TestCase):
    def test_job(self):
        httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close); self.addCleanup(httpd.shutdown)
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(runner, 'MIN_HOST_INTERVAL', 0), mock.patch.object(runner, '_sleep', lambda s: None), \
                mock.patch.object(c, 'API', f'http://127.0.0.1:{httpd.server_address[1]}/data/DS-045409'):
            self.assertEqual(runner.run_job(c, root=tmp), 0)
            t = pd.read_parquet(Path(tmp)/'data/evidence/derived/comext-blueberry/comext_blueberry_monthly.parquet')
            self.assertEqual(sorted(t.reporter.unique()), sorted(c.REPORTERS))
            self.assertEqual(len(t), 6 * len(c.REPORTERS))
            self.assertTrue(t.cn_scope.str.contains('cranberry').all())
            raw = sorted(p.name for p in (Path(tmp)/'data/evidence/raw/comext-blueberry').glob('*.json') if 'manifest' not in p.name)
            self.assertEqual(len(raw), len(c.REPORTERS))


if __name__ == '__main__':
    unittest.main()
