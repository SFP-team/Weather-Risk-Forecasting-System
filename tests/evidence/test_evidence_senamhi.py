"""SENAMHI blueberry bulletin adapter: listing, dekad dates, stage sentences, PDF text and the job through the runner."""
import functools
import http.server
import json
import shutil
import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
import pandas as pd
from evidence import runner
from evidence.adapters import senamhi_arandano as s

FIX = Path(__file__).resolve().parent/'fixtures'
HAS_PDFTOTEXT = shutil.which('pdftotext') is not None


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


class Listing(unittest.TestCase):
    def test_only_blueberry_links(self):
        # Real page excerpt: the disease forecast card sits next to the blueberry card and must be ignored.
        e = s.listing_entries((FIX/'senamhi_listing_sample.html').read_text(encoding='utf-8'))
        self.assertEqual([x['seq'] for x in e], [70, 69, 68, 67, 66, 65])
        self.assertEqual({x['prefix'] for x in e}, {'02981SENA'})
        self.assertEqual(e[0]['label'], 'Octubre - 2026')
        self.assertEqual(e[0]['url'], 'https://www.senamhi.gob.pe/load/file/02981SENA-70.pdf')


class Dates(unittest.TestCase):
    def test_real_layout_text(self):
        d = s.bulletin_dates((FIX/'senamhi_bulletin_70_layout.txt').read_text(encoding='utf-8'))
        self.assertEqual((d['volume'], d['edition']), ('V', 'XXVII'))
        self.assertEqual((d['forecast_start'], d['forecast_end']), (pd.Timestamp('2026-10-03'), pd.Timestamp('2026-10-12')))
        self.assertEqual((d['monitor_year'], d['monitor_month'], d['monitor_dekad']), (2026, 9, 3))
        self.assertEqual((d['monitor_start'], d['monitor_end']), (pd.Timestamp('2026-09-21'), pd.Timestamp('2026-09-30')))
        self.assertEqual(d['next_update'], pd.Timestamp('2026-10-14'))

    def test_header_variants(self):
        cases = {'Del 24 de julio 02 de agosto 2025': ('2025-07-24', '2025-08-02'),
                 'Del 23 de diciembre 2025 al 01 de enero de 2026': ('2025-12-23', '2026-01-01'),
                 'Del 22 de setiembre al 01 de octubre 2026': ('2026-09-22', '2026-10-01'),
                 'Del 15 al 24 de septiembre de 2026': ('2026-09-15', '2026-09-24')}
        for text, (a, b) in cases.items():
            d = s.bulletin_dates(text)
            self.assertEqual((d['forecast_start'], d['forecast_end']), (pd.Timestamp(a), pd.Timestamp(b)), text)
        d = s.bulletin_dates('3° DÉCADA DE FEBRERO DE 2026 (21 al 28 de febrero)')
        self.assertEqual(d['monitor_end'], pd.Timestamp('2026-02-28'))
        d = s.bulletin_dates('PRONÓSTICO AGROMETEROLÓGICO')
        self.assertTrue(pd.isna(d['forecast_start']) and d['monitor_dekad'] is None)


class Sentences(unittest.TestCase):
    def test_justified_columns_are_rejoined(self):
        # Bulletin 26 reading-order text: justified lines come out one word per paragraph.
        rows = s.stage_sentences((FIX/'senamhi_bulletin_26.txt').read_text(encoding='utf-8'))
        stages = [r for r in rows if r['section'] == 'stages']
        self.assertEqual(stages[0]['sentence'], 'Según el monitoreo fenológico realizado en la estación Cayaltí, ubicada en la región '
                         'Lambayeque, el cultivo de arándano se encuentra principalmente en la fase de fructificación.')
        self.assertEqual((stages[0]['stage_terms'], stages[0]['localities'], stages[0]['regions']),
                         ('fases,fructificacion', 'Cayaltí', 'Lambayeque'))
        self.assertEqual((stages[1]['localities'], stages[1]['regions']), ('Chao,San José', 'La Libertad'))
        self.assertTrue(all(r['sentence'][0].isupper() for r in rows))
        self.assertEqual({r['section'] for r in rows}, {'stages', 'notes', 'impacts'})
        self.assertTrue(any(r['section'] == 'notes' and r['sentence'].startswith('El mapa contiene') for r in rows))

    def test_terms_are_accent_insensitive(self):
        rows = s.stage_sentences('Etapas de crecimiento\n\nEn Chao la FLORACION avanza. Sin novedades en el riego. '
                                 'Inicia la cosecha de la variedad Ventura en Olmos.')
        self.assertEqual([(r['stage_terms'], r['localities'], r['varieties']) for r in rows],
                         [('floracion', 'Chao', ''), ('cosecha', 'Olmos', 'Ventura')])


def ctx_for(root, state=None):
    tables = {}
    paths = SimpleNamespace(raw=root/'raw', derived=root/'derived', tmp=root/'tmp')
    for p in vars(paths).values():
        p.mkdir(parents=True, exist_ok=True)
    return SimpleNamespace(paths=paths, state=state or {}, tables=tables, write_table=lambda n, df: tables.__setitem__(n, df))


@unittest.skipUnless(HAS_PDFTOTEXT, 'pdftotext not installed')
class Pdf(unittest.TestCase):
    def test_parse_stored_pdfs(self):
        with tempfile.TemporaryDirectory() as tmp:
            ctx = ctx_for(Path(tmp), {'labels': {'02981SENA-1': 'Octubre - 2026'}})
            for n in (1, 2):
                shutil.copy(FIX/'senamhi_tiny_bulletin.pdf', ctx.paths.raw/f'02981SENA-{n}.pdf')
            summary = s.parse(ctx, {})
            b, st = ctx.tables['senamhi_bulletins'], ctx.tables['senamhi_stage_sentences']
            self.assertEqual(b.bulletin_id.tolist(), ['02981SENA-1', '02981SENA-2'])
            self.assertEqual(b.pages.tolist(), [2, 2])
            self.assertEqual(b.duplicate_of.tolist(), [None, '02981SENA-1'])
            self.assertEqual(b.listing_label.tolist(), ['Octubre - 2026', None])
            self.assertEqual(b.iloc[0].monitor_start, pd.Timestamp('2026-09-21'))
            self.assertIn('Década de setiembre', (Path(tmp)/'derived'/b.iloc[0].text_path).read_text(encoding='utf-8'))
            self.assertEqual(st[st.seq == 1][['section', 'sentence', 'stage_terms', 'localities', 'regions']].values.tolist(),
                             [['stages', 'En Cayaltí (Lambayeque) el cultivo atraviesa la fase de floración.', 'fases,floracion',
                               'Cayaltí', 'Lambayeque']])
            self.assertEqual((summary['bulletins'], summary['duplicates']), (2, 1))
            self.assertEqual(ctx.state['max_seq'], 2)

    def test_job_through_runner(self):
        with tempfile.TemporaryDirectory() as tmp:
            web = Path(tmp)/'web'; (web/'load/file').mkdir(parents=True)
            for n in (1, 2, 3):
                shutil.copy(FIX/'senamhi_tiny_bulletin.pdf', web/f'load/file/02981SENA-{n}.pdf')
            (web/'load/file/02981SENA-2.pdf').unlink()  # a withdrawn number must not fail the run
            httpd = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(web)))
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            self.addCleanup(httpd.server_close); self.addCleanup(httpd.shutdown)
            base = f'http://127.0.0.1:{httpd.server_address[1]}/'
            (web/'boletines.html').write_text(f'<a href="{base}load/file/02981SENA-3.pdf" title="Pronóstico Agrometeorológico '
                                              'para el Cultivo de Arándano" target="_blank">Octubre - 2026</a>', encoding='utf-8')
            root = Path(tmp)/'root'
            with mock.patch.object(runner, 'MIN_HOST_INTERVAL', 0), mock.patch.object(runner, '_sleep', lambda x: None), \
                    mock.patch.object(s, 'LISTING', base + 'boletines.html'), mock.patch.object(s, 'FILES', base + 'load/file/'):
                self.assertEqual(runner.run_job(s, root=root), 0)
                b = pd.read_parquet(root/'data/evidence/derived/senamhi-arandano/senamhi_bulletins.parquet')
                self.assertEqual(b.seq.tolist(), [1, 3])
                self.assertEqual(b.listing_label.tolist(), [None, 'Octubre - 2026'])
                state = json.loads((root/'state/evidence/senamhi-arandano.json').read_text())
                self.assertEqual(state['adapter']['max_seq'], 3)
                # Stored numbers are not requested again; only the withdrawn one is retried.
                ctx = SimpleNamespace(paths=SimpleNamespace(raw=root/'data/evidence/raw/senamhi-arandano'), state=state['adapter'],
                                      fetch=lambda r: SimpleNamespace(path=web/'boletines.html'))
                self.assertEqual([r.key for r in s.plan(ctx)], ['pdf_02981SENA-2'])


if __name__ == '__main__':
    unittest.main()
