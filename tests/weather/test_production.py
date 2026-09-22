import unittest
import numpy as np
import pandas as pd
from production import (analyse, classification, empty_row, profile, risks, season, window, winter_months,
                        warm_midwinter_daily, wilson, PROFILES)


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
        self.assertEqual(r['warm_midwinter_hours'], 0)
        self.assertIsNone(r['metrics']['fruit_frost_days'])
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

    def test_risk_frequency_excludes_missing_windows(self):
        rows = self.rows([40, 60, 60])
        for r, freeze, heat in zip(rows, (1, 0, None), (0, 0, 0)):
            r['metrics'].update(flower_freeze_days=freeze, fruit_severe_heat_days=heat, harvest_heavy_rain_days=None)
        out = risks(rows, profile('legacy_paul_v1'))
        by = out['by_id']
        self.assertEqual((by['flowering_freeze']['years_with_event'], by['flowering_freeze']['valid_years']), (1, 2))
        self.assertEqual((by['chill_shortfall']['years_with_event'], by['chill_shortfall']['valid_years']), (1, 3))
        self.assertIsNone(by['harvest_heavy_rain']['frequency'])
        self.assertIsNone(by['harvest_heavy_rain']['years_with_event'])
        self.assertEqual(by['fruit_severe_heat']['frequency'], 0)
        self.assertEqual(out['ranked'], [])
        self.assertEqual(by['flowering_freeze']['eligibility'], 'insufficient_data')

    def test_wilson_interval(self):
        lo, hi = wilson(6, 15)
        self.assertLess(lo, 0.4)
        self.assertGreater(hi, 0.4)
        self.assertAlmostEqual(lo, 0.1982, places=3)
        self.assertAlmostEqual(hi, 0.6425, places=3)
        self.assertIsNone(wilson(0, 0))

    def test_twelve_winters_half_frequency_and_competition_ties(self):
        rows = self.rows([320] * 12)
        for i, row in enumerate(rows):
            row['metrics'].update(flower_freeze_days=int(i < 6), fruit_frost_days=int(i < 6),
                                  fruit_severe_heat_days=1, harvest_heavy_rain_days=int(i < 5))
        result = risks(rows, profile('stage_risks_v2'))
        self.assertEqual([(r['risk'], r['rank']) for r in result['ranked']],
                         [('fruit_severe_heat', 1), ('flowering_freeze', 2), ('fruit_frost', 2)])
        self.assertEqual(result['by_id']['harvest_heavy_rain']['eligibility'], 'below_frequency')
        self.assertEqual(result['by_id']['flowering_freeze']['frequency'], .5)
        result = risks(rows[:11], profile('stage_risks_v2'))
        self.assertEqual(result['ranked'], [])
        self.assertEqual(result['by_id']['fruit_severe_heat']['eligibility'], 'insufficient_data')
        rows[-1]['metrics']['flower_freeze_days'] = None
        result = risks(rows, profile('stage_risks_v2'))
        self.assertEqual(result['by_id']['flowering_freeze']['valid_years'], 11)
        self.assertEqual(result['by_id']['flowering_freeze']['eligibility'], 'insufficient_data')

    def test_combined_disease_requires_all_three_complete_stages(self):
        rows = self.rows([320] * 4)
        for row, values in zip(rows, ((1, 0, 0), (0, 0, 0), (1, None, 0), (0, 0, None))):
            row['metrics'].update(zip(('flowering_disease_days', 'fruit_disease_days', 'harvest_disease_days'), values))
        result = risks(rows, profile('stage_risks_v2'))
        disease = result['by_id']['disease_weather']
        self.assertEqual((disease['years_with_event'], disease['valid_years'], disease['frequency']), (1, 2, .5))
        self.assertEqual(disease['exposure']['flowering_disease_days']['n'], 4)
        self.assertEqual(disease['exposure']['fruit_disease_days']['n'], 3)
        self.assertEqual(sum('disease' in key for key in result['by_id']), 1)

    def test_descriptive_metrics_never_fabricate_event_frequency(self):
        rows = self.rows([320] * 12)
        for row in rows:
            row['warm_midwinter_hours'] = 100
            row['metrics'].update(flowering_pollination_unfavourable_days=20, flowering_cold_dry_days=5,
                                  flowering_max_dry_days=20, fruit_max_dry_days=40)
        result = risks(rows, profile('stage_risks_v2'))
        for key in ('pollination_weather', 'warm_midwinter', 'flowering_dry_spell', 'fruit_dry_spell'):
            item = result['by_id'][key]
            self.assertEqual(item['eligibility'], 'definition_pending')
            self.assertEqual(item['valid_years'], 12)
            self.assertIsNone(item['frequency'])
            self.assertIsNone(item['years_with_event'])
            self.assertIsNone(item['ci95'])
            self.assertIsNone(item['rank'])

    def test_evergreen_and_unknown_do_not_headline_hypothetical_crop_risks(self):
        for chills, missing_classification in (([40] * 12, False), ([320] * 12, True)):
            rows = self.rows(chills)
            for row in rows:
                row['warm_midwinter_hours'] = 100
                row['metrics'].update(flower_freeze_days=2, fruit_frost_days=1)
                if missing_classification:
                    row['freeze_risk_months'] = None
            result = risks(rows, profile('stage_risks_v2'))
            self.assertEqual(result['ranked'], [])
            for key, item in result['by_id'].items():
                self.assertEqual(item['eligibility'], 'definition_pending' if key == 'warm_midwinter' else 'not_applicable')
            self.assertEqual(result['by_id']['flowering_freeze']['exposure']['flower_freeze_days']['mean'], 2)
            self.assertEqual(result['exposures']['warm_midwinter_hours']['n'], 12)


class AnalyseTests(unittest.TestCase):
    def test_single_complete_year_end_to_end(self):
        hourly, daily = synthetic()
        a = analyse(hourly, daily, 29.8, 'legacy_paul_v1', years=range(2020, 2021))
        self.assertEqual(a['status_counts'], {'complete': 1})
        self.assertEqual(a['calendar']['chill']['median_date'], '11-03')
        self.assertEqual(a['calendar']['harvest_start']['median_date'], '02-09')
        self.assertEqual(a['classification']['multi_feature']['majority'], 'Deciduous')
        self.assertEqual(a['risks']['by_id']['flowering_freeze']['frequency'], 1.0)
        self.assertEqual(a['risks']['by_id']['chill_shortfall']['frequency'], 0)
        self.assertEqual(a['risks']['ranked'], [])

    def test_truncated_archive_year_is_declined_not_dropped(self):
        hourly, daily = synthetic()
        a = analyse(hourly, daily, 29.8, 'legacy_paul_v1', years=range(2020, 2022))
        self.assertEqual(a['status_counts'], {'complete': 1, 'incomplete_chill': 1})
        self.assertEqual(len(a['seasons']), 2)
        self.assertEqual(a['classification']['valid_years'], 1)


class StageExposureTests(unittest.TestCase):
    def setUp(self):
        self.hourly, self.daily = synthetic(tmin=1., tmax=20., rain=0.)
        self.p = profile('stage_risks_v2')

    def calc(self):
        return season(self.hourly, self.daily, 29.8, 2020, self.p)

    def test_primary_preserves_chill_and_stage_dates(self):
        old = season(self.hourly, self.daily, 29.8, 2020, profile('legacy_paul_v1'))
        new = self.calc()
        for key in ('chill_hours', 'chill_date', 'budbreak_date', 'flowering', 'fruit', 'harvest', 'offset_days'):
            self.assertEqual(new[key], old[key], key)
        self.assertEqual(new['metrics']['production_gdd'], 1250.)
        self.assertEqual(old['metrics']['production_gdd'], 1410.)

    def test_fruit_frost_and_heat_are_clipped_and_inclusive(self):
        self.daily['tmax_c'] = 31.99
        for day, value in [('2019-12-22', -4.), ('2019-12-23', 0.), ('2020-02-08', -.01), ('2020-02-09', -4.)]:
            self.daily.loc[day, 'tmin_c'] = value
        for day, value in [('2019-12-22', 40.), ('2019-12-23', 32.), ('2020-02-08', 35.), ('2020-02-09', 40.)]:
            self.daily.loc[day, 'tmax_c'] = value
        metrics = self.calc()['metrics']
        self.assertEqual(metrics['fruit_frost_days'], 2)
        self.assertEqual(metrics['fruit_heat_days'], 2)
        self.assertEqual(metrics['fruit_severe_heat_days'], 1)

    def test_pollination_or_is_not_cold_and_dry(self):
        for day, tmax, rain in [('2019-11-30', 5., 5.), ('2019-12-01', 15., 0.),
                                ('2019-12-02', 14.99, 0.), ('2019-12-03', 15., 1.),
                                ('2019-12-22', 14.99, 1.), ('2019-12-23', 5., 5.)]:
            self.daily.loc[day, ['tmax_c', 'precip_mm']] = [tmax, rain]
        metrics = self.calc()['metrics']
        self.assertEqual(metrics['flowering_pollination_unfavourable_days'], 3)
        self.assertEqual(metrics['flowering_cold_dry_days'], 1)

    def test_dry_runs_reset_at_stage_edges_and_one_mm(self):
        self.daily.loc['2019-12-10', 'precip_mm'] = 1.
        self.daily.loc['2020-01-05', 'precip_mm'] = 1.
        metrics = self.calc()['metrics']
        self.assertEqual(metrics['flowering_max_dry_days'], 12)
        self.assertEqual(metrics['fruit_max_dry_days'], 34)

    def test_disease_thresholds_include_endpoints_only_in_stage(self):
        self.daily['rh_mean_pct'] = 84.99
        for day, temp, rh, rain in [('2019-12-22', 20., 90., 5.), ('2019-12-23', 15., 85., .1),
                                   ('2019-12-24', 14.99, 85., .1), ('2019-12-25', 28.01, 85., .1),
                                   ('2019-12-26', 20., 84.99, .1), ('2019-12-27', 20., 85., .099),
                                   ('2020-02-08', 28., 85., .1), ('2020-02-09', 20., 90., 5.)]:
            self.daily.loc[day, ['tmean_c', 'rh_mean_pct', 'precip_mm']] = [temp, rh, rain]
        metrics = self.calc()['metrics']
        self.assertEqual(metrics['fruit_disease_days'], 2)
        self.assertEqual(metrics['flowering_disease_days'], 1)
        self.assertEqual(metrics['harvest_disease_days'], 1)

    def test_missing_weather_declines_only_dependent_stage_metrics(self):
        self.daily.loc['2019-12-01', 'precip_suspect_extreme'] = True
        self.daily.loc['2020-01-01', 'rh_mean_pct'] = 101.
        self.daily.loc['2020-01-02', 'tmax_c'] = np.nan
        metrics = self.calc()['metrics']
        for key in ('flowering_pollination_unfavourable_days', 'flowering_cold_dry_days',
                    'flowering_max_dry_days', 'flowering_disease_days', 'fruit_disease_days',
                    'fruit_vpd_mean_kpa', 'fruit_heat_days'):
            self.assertIsNone(metrics[key], key)
        self.assertEqual(metrics['fruit_frost_days'], 0)
        self.assertEqual(metrics['fruit_max_dry_days'], 48)
        self.assertEqual(metrics['harvest_disease_days'], 0)

    def test_each_winter_uses_own_stage_not_shared_calendar(self):
        delayed = self.hourly.copy()
        delayed.loc[:'2019-12-01 23:00'] = 10.
        self.daily.loc['2019-12-23', 'tmin_c'] = 0.
        early = self.calc()
        late = season(delayed, self.daily, 29.8, 2020, self.p)
        self.assertEqual(early['metrics']['fruit_frost_days'], 1)
        self.assertEqual(late['metrics']['fruit_frost_days'], 0)
        self.assertNotEqual(early['fruit'], late['fruit'])

    def test_northern_midwinter_exact_hours_despite_failed_chill(self):
        self.hourly[:] = 21.
        for time in ('2019-11-14 23:00', '2019-11-15 00:00', '2020-02-15 23:00', '2020-02-16 00:00'):
            self.hourly.loc[time] = 21.01
        row = self.calc()
        self.assertEqual(row['status'], 'chill_not_met')
        self.assertEqual(row['warm_midwinter_window'], ['2019-11-15', '2020-02-15'])
        self.assertEqual(row['warm_midwinter_hours'], 2)
        self.assertIsNone(row['fruit'])
        self.hourly.loc['2019-11-01'] = np.nan
        self.assertEqual(self.calc()['warm_midwinter_hours'], 2)
        self.hourly.loc['2019-12-01 12:00'] = np.nan
        self.assertIsNone(self.calc()['warm_midwinter_hours'])

    def test_southern_midwinter_starts_may15_not_shifted_northern_window(self):
        hourly = pd.Series(21., index=pd.date_range('2020-04-01', '2020-10-01', freq='h', inclusive='left'))
        for time in ('2020-05-14 23:00', '2020-05-15 00:00', '2020-08-15 23:00', '2020-08-16 00:00'):
            hourly.loc[time] = 22.
        row = season(hourly, self.daily, -26., 2020, self.p)
        self.assertEqual(row['warm_midwinter_window'], ['2020-05-15', '2020-08-15'])
        self.assertEqual(row['warm_midwinter_hours'], 2)
        self.assertEqual(row['status'], 'chill_not_met')

    def test_daily_fallback_is_complete_day_count_not_hours(self):
        self.daily['tmax_c'] = 21.
        for lat, dates in ((29.8, ['2019-11-14', '2019-11-15', '2020-02-15', '2020-02-16']),
                           (-26., ['2020-05-14', '2020-05-15', '2020-08-15', '2020-08-16'])):
            with self.subTest(lat=lat):
                daily = self.daily.copy()
                daily.loc[dates, 'tmax_c'] = 21.01
                result = warm_midwinter_daily(daily, lat, range(2020, 2021))
                self.assertEqual(result['seasons'][0]['value'], 2)
                self.assertEqual(result['seasons'][0]['window'], dates[1:3])
                self.assertEqual(result['summary']['mean'], 2)
                daily.loc[dates[1], 'tmax_c'] = np.nan
                result = warm_midwinter_daily(daily, lat, range(2020, 2021))
                self.assertIsNone(result['seasons'][0]['value'])
                self.assertEqual(result['summary']['n'], 0)



if __name__ == '__main__':
    unittest.main()
