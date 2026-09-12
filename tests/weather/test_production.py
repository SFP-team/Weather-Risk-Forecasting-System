import unittest
import numpy as np
import pandas as pd
from production import (analyse, classification, empty_row, profile, risks, season, window, winter_months,
                        wilson, PROFILES)


def synthetic(hourly_temp=5., tmin=-2.2, tmax=36., rain=10., rh=90.):
    hourly = pd.Series(hourly_temp, index=pd.date_range('2019-11-01', '2020-05-01', freq='h', inclusive='left'))
    daily = pd.DataFrame({'tmean_c': 17., 'tmin_c': tmin, 'tmax_c': tmax, 'precip_mm': rain, 'rh_mean_pct': rh,
                          'shortwave_mj_m2_day': 15., 'precip_suspect_extreme': False},
                         index=pd.date_range('2019-01-01', '2021-06-01'))
    return hourly, daily


class SeasonTests(unittest.TestCase):
    def setUp(self):
        self.hourly, self.daily = synthetic()
        self.p = profile('legacy_paul_v1')

    def calc(self, **kw):
        p = {**self.p, **kw}
        return season(self.hourly, self.daily, 29.8, 2020, p)

    def test_known_chain_and_same_anchor_offsets(self):
        r = self.calc()
        self.assertEqual(r['status'], 'complete')
        self.assertEqual(r['season_start'], '2019-11-01')
        self.assertEqual(r['chill_date'], '2019-11-03')            # 50th hour at 5 C
        self.assertEqual(r['budbreak_date'], '2019-11-17')         # 15 days x 10 GDD from the chill day inclusive
        self.assertEqual(r['flowering'], ['2019-12-01', '2019-12-22'])
        self.assertEqual(r['fruit'], ['2019-12-23', '2020-02-08'])
        self.assertEqual(r['harvest'], ['2020-02-09', '2020-03-20'])
        self.assertEqual(r['offset_days']['chill'], 2)             # measured from 1 November, not 1 October
        self.assertEqual(r['offset_days']['harvest_start'], 100)
        self.assertEqual(r['chill_hours'], 4368)
        self.assertEqual(r['metrics']['flower_freeze_days'], 22)
        self.assertEqual(r['metrics']['fruit_severe_heat_days'], 48)
        self.assertEqual(r['metrics']['harvest_heavy_rain_days'], 41)
        self.assertEqual(r['metrics']['harvest_rain_mm'], 410.)
        self.assertEqual(r['metrics']['flowering_disease_days'], 22)
        self.assertEqual(r['metrics']['production_max_dry_days'], 0)
        self.assertAlmostEqual(r['metrics']['production_gdd'], 10. * 141)
        self.assertAlmostEqual(r['winter_month_tmin_lowest_c'], -2.2)
        self.assertEqual(r['freeze_risk_months'], 6)

    def test_chill_definition_boundaries(self):
        for temp, below, bounded in ((7.2, 0, 4368), (0., 4368, 4368), (-1., 4368, 0), (7.19, 4368, 4368)):
            self.hourly[:] = temp
            self.assertEqual(self.calc()['chill_hours'], below, temp)
            self.assertEqual(self.calc(chill_definition='bounded_0_7_2')['chill_hours'], bounded, temp)

    def test_freeze_hours_and_events(self):
        self.hourly[:] = 3.
        self.hourly.iloc[10:13] = -1.
        self.hourly.iloc[20] = 0.
        r = self.calc()
        self.assertEqual(r['freeze_hours'], 4)
        self.assertEqual(r['freeze_events'], 2)

    def test_missing_hour_keeps_schema_and_declines(self):
        self.hourly.iloc[100] = np.nan
        r = self.calc()
        self.assertEqual(r['status'], 'incomplete_chill')
        self.assertIsNone(r['chill_hours'])
        self.assertEqual(set(r['metrics']), set(self.calc()['metrics']))
        self.assertIn('chill', r['issues'])

    def test_chill_not_met_still_reports_hours(self):
        self.hourly[:] = 10.
        self.hourly.iloc[:20] = 5.
        r = self.calc()
        self.assertEqual(r['status'], 'chill_not_met')
        self.assertEqual(r['chill_hours'], 20)
        self.assertIsNone(r['budbreak_date'])

    def test_missing_gdd_not_zero_filled(self):
        self.daily.loc['2019-11-10', 'tmean_c'] = np.nan
        self.assertEqual(self.calc()['status'], 'incomplete_gdd')

    def test_suspect_rain_declines_rain_metrics_only(self):
        self.daily.loc['2020-03-01', 'precip_suspect_extreme'] = True
        r = self.calc()
        for key in ('harvest_rain_mm', 'harvest_heavy_rain_days', 'harvest_disease_days', 'production_max_dry_days'):
            self.assertIsNone(r['metrics'][key], key)
        self.assertEqual(r['metrics']['flowering_rain_mm'], 220.)
        self.assertEqual(r['metrics']['flower_freeze_days'], 22)
        self.assertEqual(r['status'], 'incomplete_metrics')

    def test_invalid_humidity_declines_vpd_and_disease(self):
        self.daily.loc['2019-12-05', 'rh_mean_pct'] = 120.
        r = self.calc()
        self.assertIsNone(r['metrics']['flowering_vpd_mean_kpa'])
        self.assertIsNone(r['metrics']['flowering_disease_days'])
        self.assertIsNotNone(r['metrics']['harvest_vpd_mean_kpa'])

    def test_south_window_and_winter_months(self):
        self.assertEqual([str(d.date()) for d in window(2020, 'south')], ['2020-04-01', '2020-10-01'])
        self.assertEqual([str(d.date()) for d in window(2020, 'north')], ['2019-11-01', '2020-05-01'])
        self.assertEqual(winter_months(2020, 'south'), [(2020, 7), (2020, 8), (2020, 9)])
        self.assertEqual(winter_months(2020, 'north'), [(2020, 1), (2020, 2), (2020, 3)])

    def test_zero_requirement_refused(self):
        PROFILES['_zero'] = {**PROFILES['legacy_paul_v1'], 'chill_requirement_hours': 0}
        try:
            with self.assertRaisesRegex(ValueError, 'anchor_required'):
                profile('_zero')
        finally:
            del PROFILES['_zero']


class SummaryTests(unittest.TestCase):
    def rows(self, chills, **extra):
        out = []
        for i, c in enumerate(chills):
            r = empty_row(2011 + i, 'north', pd.Timestamp('2010-11-01'), pd.Timestamp('2011-05-01'))
            r.update(chill_hours=c, freeze_hours=0, freeze_risk_months=0,
                     winter_month_tmin_lowest_c=9., winter_month_tmean_lowest_c=14., **extra)
            out.append(r)
        return out

    def test_majority_differs_from_mean_based(self):
        c = classification(self.rows([320, 320, 100]), profile('legacy_paul_v1'))
        self.assertEqual(c['mean_based']['chill_only'], 'Semi-evergreen')
        self.assertEqual(c['chill_only']['majority'], 'Deciduous')
        self.assertEqual(c['chill_only']['year_counts'], {'Evergreen': 0, 'Semi-evergreen': 1, 'Deciduous': 2})

    def test_no_majority_is_transitional(self):
        c = classification(self.rows([50, 200, 350]), profile('legacy_paul_v1'))
        self.assertEqual(c['chill_only']['majority'], 'Transitional')
        self.assertEqual(c['multi_feature']['majority'], 'Transitional')

    def test_multi_feature_requires_every_input(self):
        rows = self.rows([50, 50, 50])
        c = classification(rows, profile('legacy_paul_v1'))
        self.assertEqual(c['multi_feature']['majority'], 'Evergreen')
        for r in rows:
            r['freeze_risk_months'] = None
        c = classification(rows, profile('legacy_paul_v1'))
        self.assertIsNone(c['multi_feature']['majority'])
        self.assertEqual(c['chill_only']['majority'], 'Evergreen')

    def test_missing_years_are_excluded_from_classification(self):
        rows = self.rows([320, 320, None])
        c = classification(rows, profile('legacy_paul_v1'))
        self.assertEqual(c['valid_years'], 2)
        self.assertEqual(c['chill_only']['valid_years'], 2)
        self.assertIsNone(c['per_year'][2013]['chill_only'])

    def test_risk_frequency_denominators_and_order(self):
        rows = self.rows([40, 60, 60])
        for r, freeze, heat in zip(rows, (1, 0, None), (0, 0, 0)):
            r['metrics'].update(flower_freeze_days=freeze, fruit_severe_heat_days=heat, harvest_heavy_rain_days=None)
        out = risks(rows, profile('legacy_paul_v1'))
        by = {r['risk']: r for r in out['ranked']}
        self.assertEqual((by['flowering_freeze']['years_with_event'], by['flowering_freeze']['valid_years']), (1, 2))
        self.assertEqual((by['chill_shortfall']['years_with_event'], by['chill_shortfall']['valid_years']), (1, 3))
        self.assertIsNone(by['harvest_heavy_rain']['frequency'])
        self.assertEqual([r['risk'] for r in out['ranked']][:2], ['flowering_freeze', 'chill_shortfall'])
        self.assertEqual(out['ranked'][-1]['risk'], 'harvest_heavy_rain')

    def test_wilson_interval(self):
        lo, hi = wilson(6, 15)
        self.assertLess(lo, 0.4)
        self.assertGreater(hi, 0.4)
        self.assertAlmostEqual(lo, 0.1982, places=3)
        self.assertAlmostEqual(hi, 0.6425, places=3)
        self.assertIsNone(wilson(0, 0))


class AnalyseTests(unittest.TestCase):
    def test_single_complete_year_end_to_end(self):
        hourly, daily = synthetic()
        a = analyse(hourly, daily, 29.8, 'legacy_paul_v1', years=range(2020, 2021))
        self.assertEqual(a['status_counts'], {'complete': 1})
        self.assertEqual(a['calendar']['chill']['median_date'], '11-03')
        self.assertEqual(a['calendar']['harvest_start']['median_date'], '02-09')
        self.assertEqual(a['classification']['multi_feature']['majority'], 'Deciduous')
        self.assertEqual(a['risks']['ranked'][0]['frequency'], 1.0)
        self.assertEqual(a['risks']['ranked'][-1]['risk'], 'chill_shortfall')

    def test_truncated_archive_year_is_declined_not_dropped(self):
        hourly, daily = synthetic()
        a = analyse(hourly, daily, 29.8, 'legacy_paul_v1', years=range(2020, 2022))
        self.assertEqual(a['status_counts'], {'complete': 1, 'incomplete_chill': 1})
        self.assertEqual(len(a['seasons']), 2)
        self.assertEqual(a['classification']['valid_years'], 1)


if __name__ == '__main__':
    unittest.main()
