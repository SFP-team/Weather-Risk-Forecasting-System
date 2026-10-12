import csv
from datetime import date
import gzip
import io
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

import pandas as pd

CODE = Path(__file__).resolve().parents[2] / 'pipelines'
if not (CODE / 'evidence').exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
from evidence.adapters import storm_events  # noqa: E402

FIXTURES = Path(__file__).resolve().parent / 'fixtures'


def details_file(folder, extra_rows=()):
    """Real rows from the 1996 and 2022 files plus synthetic rows for cases the sample lacks."""
    rows = list(csv.DictReader(io.StringIO((FIXTURES / 'storm_details_sample.csv').read_text())))
    fields = list(rows[0])
    for change in extra_rows:
        rows.append({**rows[4], **change})
    text = io.StringIO()
    writer = csv.DictWriter(text, fields)
    writer.writeheader()
    writer.writerows(rows)
    path = folder / 'StormEvents_details-ftp_v1.0_d2022_c20260625.csv.gz'
    path.write_bytes(gzip.compress(text.getvalue().encode()))
    return path


class Ctx:
    def __init__(self, listing):
        self.today, self.state, self.tables, self.logs = date(2026, 10, 12), {}, {}, []
        self.listing = listing

    def fetch(self, request):
        return types.SimpleNamespace(path=self.listing, status='unchanged')

    def write_table(self, name, frame):
        self.tables[name] = frame

    def log(self, event, **fields):
        self.logs.append((event, fields))


class StormEventsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_damage_parser(self):
        values = pd.Series(['18.9M', '0.00K', '20K', '', '2B', '0', 'T', '.5K', None, '1.5H'])
        result = storm_events.damage(values).tolist()
        expected = [18.9e6, 0., 20e3, None, 2e9, 0., None, 500., None, 150.]
        for got, want in zip(result, expected):
            if want is None:
                self.assertTrue(pd.isna(got))
            else:
                self.assertAlmostEqual(got, want)

    def test_timezone_offsets_old_and_new_forms(self):
        offsets = storm_events.utc_offset(pd.Series(['CST-6', 'EST', 'PDT-7', 'AKST-9', 'GST10', 'XYZ', ''])).tolist()
        self.assertEqual(offsets[:5], [-6., -5., -7., -9., 10.])
        self.assertTrue(pd.isna(offsets[5]) and pd.isna(offsets[6]))

    def test_parse_filters_states_and_event_types(self):
        path = details_file(self.tmp, [{'EVENT_ID': '9000001', 'DAMAGE_CROPS': '1.5M', 'EVENT_TYPE': 'Frost/Freeze',
                                        'EVENT_NARRATIVE': 'Synthetic: freeze damaged Blueberries near Alma.'}])
        frame = storm_events.parse_file(path)
        # Kept: GA hail 2022, FL frost/freeze 1996 (zone), synthetic GA frost/freeze. Dropped: MS and GA tornado,
        # FL thunderstorm wind (which mentions "Blueberry Road"), TX hail.
        self.assertEqual(sorted(frame.event_id.astype(int).tolist()), [1023867, 5575182, 9000001])
        self.assertTrue(set(frame.state_abbr) <= set(storm_events.STATES))
        hail = frame[frame.event_id == 1023867].iloc[0]
        self.assertEqual((hail.state, hail.state_abbr, hail.cz_type, hail.county_fips), ('GEORGIA', 'GA', 'C', '13183'))
        self.assertEqual(hail.begin_local, pd.Timestamp('2022-05-15 14:30'))
        self.assertEqual(hail.begin_utc, pd.Timestamp('2022-05-15 19:30', tz='UTC'))
        self.assertEqual(hail.damage_crops_usd, 0.)
        self.assertTrue(pd.isna(hail.damage_property_usd))
        frost = frame[frame.event_id == 5575182].iloc[0]
        self.assertEqual((frost.cz_type, frost.cz_timezone, frost.utc_offset_hours), ('Z', 'EST', -5.))
        self.assertTrue(pd.isna(frost.county_fips))
        self.assertEqual(frost.begin_local, pd.Timestamp('1996-01-09 01:00'))
        synthetic = frame[frame.event_id == 9000001].iloc[0]
        self.assertEqual(synthetic.damage_crops_usd, 1.5e6)
        self.assertTrue(synthetic.mentions_blueberry)
        self.assertEqual(int(frame.mentions_blueberry.sum()), 1)
        self.assertEqual(str(frame.begin_utc.dtype), 'datetime64[ns, UTC]')

    def test_listing_picks_latest_version_and_plan_logs_gaps(self):
        listing = self.tmp / 'listing.html'
        listing.write_text(''.join(
            f'<a href="StormEvents_details-ftp_v1.0_d{year}_c{stamp}.csv.gz">x</a>\n'
            for year, stamp in [(1996, '20250101'), (1996, '20260323'), (1998, '20260323'), (2026, '20260918')])
            + '<a href="StormEvents_fatalities-ftp_v1.0_d1996_c20260323.csv.gz">f</a>')
        self.assertEqual(storm_events.latest_files(listing.read_text())[1996],
                         'StormEvents_details-ftp_v1.0_d1996_c20260323.csv.gz')
        ctx = Ctx(listing)
        requests = storm_events.plan(ctx)
        self.assertEqual([r.key for r in requests], ['details_1996', 'details_1998', 'details_2026'])
        self.assertTrue(requests[0].url.endswith('d1996_c20260323.csv.gz'))
        self.assertIn(1997, ctx.state['years_not_listed'])
        self.assertEqual(ctx.logs[0][0], 'years_not_listed')

    def test_parse_writes_table_from_details_assets_only(self):
        path = details_file(self.tmp)
        ctx = Ctx(None)
        assets = {'listing': types.SimpleNamespace(path=self.tmp / 'listing.html', status='unchanged'),
                  'details_2022': types.SimpleNamespace(path=path, status='fetched')}
        summary = storm_events.parse(ctx, assets)
        self.assertEqual(summary['rows'], 2)
        self.assertIn('storm_events_selected', ctx.tables)


if __name__ == '__main__':
    unittest.main()
