from datetime import date
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
import zipfile

import pandas as pd

CODE = Path(__file__).resolve().parents[2] / 'pipelines'
if not (CODE / 'evidence').exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
from evidence.adapters import rma_col, rma_sobtpu  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def zipped(folder, name, member, data):
    path = folder / name
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(member, data)
    return path


class Ctx:
    def __init__(self, today=date(2026, 10, 12)):
        self.today, self.tables, self.logs = today, {}, []

    def write_table(self, name, frame):
        self.tables[name] = frame

    def log(self, event, **fields):
        self.logs.append((event, fields))


class RmaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_colsom_parser_types_and_crosswalk(self):
        path = zipped(self.tmp, 'colsom_2022.zip', 'colsom_2022.txt', (FIXTURES / 'rma_colsom_sample.txt').read_bytes())
        frame = rma_col.parse_file(path)
        self.assertEqual(len(frame), 5)  # the cotton row is dropped
        self.assertTrue((frame.commodity_code == '0012').all())
        first = frame.iloc[0]
        self.assertEqual((first.state_abbr, first.county_name, first.fips), ('CA', 'Fresno', '06019'))
        self.assertEqual((int(first.cause_code), first.cause_description, int(first.month_of_loss)), (21, 'Hail', 3))
        self.assertAlmostEqual(first.liability, 610053.4)
        self.assertEqual(frame.indemnity.dtype, 'float64')
        self.assertEqual(str(frame.cause_code.dtype), 'Int64')
        self.assertEqual(dict(zip(frame.cause_code.astype(int), frame.cause_family)),
                         {21: 'hail', 31: 'excess_moisture', 41: 'freeze', 42: 'freeze', 44: 'cold'})
        self.assertEqual(frame.source_file.unique().tolist(), ['colsom_2022.zip'])

    def test_old_layout_with_blank_fields_and_other_cause(self):
        line = ('1990|12|FL|001|Alachua                       |0012|BLUEBERRIES                   |90|| |UH|51||00|   '
                '||4|2|10.5000000000|.0000000000|25000.0000000000|1500.0000000000|1000.0000000000|500.0000000000|'
                '.0000000000|.0000000000|.0000000000|3.2000000000|4100.0000000000|2.73\r\n')
        path = zipped(self.tmp, 'colsom_1990.zip', 'colsom90.txt', line.encode('latin-1'))
        frame = rma_col.parse_file(path)
        self.assertEqual(len(frame), 1)
        self.assertTrue(pd.isna(frame.year_of_loss.iloc[0]))
        self.assertEqual(frame.cause_family.iloc[0], 'other')
        self.assertEqual(int(frame.month_of_loss.iloc[0]), 0)

    def test_wrong_field_count_fails_loudly(self):
        path = zipped(self.tmp, 'colsom_2030.zip', 'x.txt', b'2030|12|FL|001|X|0012|Blueberries|90\n')
        with self.assertRaisesRegex(ValueError, 'expected 30 fields'):
            rma_col.parse_file(path)

    def test_sobtpu_parser_cr_lines_and_coverage_level(self):
        new = zipped(self.tmp, 'sobtpu_2022.zip', 'SOBSCCTPU22.TXT', (FIXTURES / 'rma_sobtpu_2022_sample.txt').read_bytes())
        old = zipped(self.tmp, 'sobtpu_1999.zip', 'sobtpu_1999.txt', (FIXTURES / 'rma_sobtpu_1999_sample.txt').read_bytes())
        frame_new, frame_old = rma_sobtpu.parse_file(new), rma_sobtpu.parse_file(old)
        self.assertEqual((len(frame_new), len(frame_old)), (3, 2))
        row = frame_new.iloc[0]
        self.assertEqual((row.state_abbr, row.type_code, row.type_name, row.practice_code, row.practice_name),
                         ('CA', '002', 'Highbush', '002', 'Irrigated'))
        self.assertAlmostEqual(row.coverage_level, .6)
        self.assertAlmostEqual(frame_old.coverage_level.iloc[0], .5)
        self.assertEqual(frame_old.type_name.iloc[0], 'LOWBUSH')
        self.assertTrue(frame_new.insured_acres.notna().all())
        for column in ('liability', 'total_premium', 'indemnity', 'insured_acres'):
            self.assertEqual(frame_new[column].dtype, 'float64')

    def test_plans_cover_years_and_mark_recent_optional(self):
        ctx = Ctx()
        col = rma_col.plan(ctx)
        self.assertEqual((col[0].key, col[-1].key, len(col)), ('colsom_1989', 'colsom_2026', 38))
        self.assertEqual([r.key for r in col if r.optional], ['colsom_2026'])
        tpu = rma_sobtpu.plan(ctx)
        self.assertEqual((tpu[0].key, tpu[-1].key), ('sobtpu_1999', 'sobtpu_2027'))
        self.assertEqual([r.key for r in tpu if r.optional], ['sobtpu_2026', 'sobtpu_2027'])
        self.assertTrue(col[0].url.endswith('/cause_of_loss/colsom_1989.zip'))

    def test_parse_builds_one_table_from_all_available_assets(self):
        path = zipped(self.tmp, 'colsom_2022.zip', 'colsom_2022.txt', (FIXTURES / 'rma_colsom_sample.txt').read_bytes())
        assets = {'colsom_2022': types.SimpleNamespace(path=path, status='unchanged'),
                  'colsom_2026': types.SimpleNamespace(path=None, status='missing')}
        ctx = Ctx()
        summary = rma_col.parse(ctx, assets)
        self.assertEqual(summary['rows'], 5)
        self.assertEqual(len(ctx.tables['rma_col_blueberry']), 5)


if __name__ == '__main__':
    unittest.main()
