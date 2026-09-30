import math
import unittest
import numpy as np
import pandas as pd
from production import (analyse, bee_flight_hours, chill_clock, chill_portions, classification, CYCLE_STARTS, Days,
                        empty_row, infection_risk, longest_run, managed_cycles, months_between, profile, reach, risks,
                        season, SCAN_MEASURES, select_favourable, stage_dates, stage_metrics, window, winter_months,
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


def flat_daily(tmean=17., start='2010-01-01', end='2025-12-31', **columns):
    base = {'tmean_c': tmean, 'tmin_c': 10., 'tmax_c': 25., 'precip_mm': 0., 'rh_mean_pct': 70.,
            'shortwave_mj_m2_day': 15., 'precip_suspect_extreme': False}
    return pd.DataFrame({**base, **columns}, index=pd.date_range(start, end))


class ThermalClockTests(unittest.TestCase):
    def setUp(self):
        self.p = profile('stage_thermal_v3')
        self.day = pd.Timestamp

    def test_reach_counts_from_first_day_and_names_gaps(self):
        days = Days(flat_daily(start='2020-01-01', end='2020-03-31'))
        self.assertEqual(reach(days, self.day('2020-01-01'), self.day('2020-02-01'), 85, 7.), (self.day('2020-01-09'), None))
        self.assertEqual(reach(days, self.day('2020-01-01'), self.day('2020-01-05'), 85, 7.),
                         (None, ('horizon', self.day('2020-01-05'))))
        self.assertEqual(reach(days, self.day('2020-03-25'), self.day('2020-05-01'), 85, 7.),
                         (None, ('missing', self.day('2020-04-01'))))
        daily = flat_daily(start='2020-01-01', end='2020-03-31')
        daily.loc['2020-01-05', 'tmean_c'] = np.nan
        self.assertEqual(reach(Days(daily), self.day('2020-01-01'), self.day('2020-02-01'), 85, 7.),
                         (None, ('missing', self.day('2020-01-05'))))

    def test_upper_cutoff_caps_daily_heat(self):
        days = Days(flat_daily(tmean=35., start='2020-01-01', end='2020-03-31'))
        self.assertEqual(reach(days, self.day('2020-01-01'), self.day('2020-03-01'), 230, 7.)[0], self.day('2020-01-09'))
        self.assertEqual(reach(days, self.day('2020-01-01'), self.day('2020-03-01'), 230, 7., 30.)[0], self.day('2020-01-10'))

    def test_stage_durations_follow_temperature(self):
        bud = self.day('2020-01-01')
        (flowering, harvest), _ = stage_dates(Days(flat_daily()), bud, self.p)
        self.assertEqual([(d - bud).days for d in (*flowering, *harvest)], [9, 38, 73, 134])
        (flowering, harvest), _ = stage_dates(Days(flat_daily(tmean=22.)), bud, self.p)
        self.assertEqual([(d - bud).days for d in (*flowering, *harvest)], [6, 25, 49, 89])
        legacy, _ = stage_dates(Days(flat_daily(tmean=22.)), bud, profile('stage_risks_v2'))
        self.assertEqual([(d - bud).days for d in (*legacy[0], *legacy[1])], [14, 35, 84, 124])

    def test_unordered_or_missing_requirements_refused(self):
        PROFILES['_bad'] = {**PROFILES['stage_thermal_v3'], 'harvest_end_gdd': 600.}
        try:
            with self.assertRaisesRegex(ValueError, 'ordered'):
                profile('_bad')
        finally:
            del PROFILES['_bad']

    def test_right_censored_harvest_is_not_a_calendar(self):
        hourly = pd.Series(5., index=pd.date_range('2019-11-01', '2020-05-01', freq='h', inclusive='left'))
        row = season(hourly, flat_daily(end='2020-02-15'), 29.8, 2020, self.p)
        self.assertEqual(row['status'], 'incomplete_stage_dates')
        self.assertIsNotNone(row['budbreak_date'])
        self.assertIsNone(row['harvest'])
        self.assertIsNone(row['offset_days']['harvest_start'])


class ManagedCycleTests(unittest.TestCase):
    @staticmethod
    def scan(daily):
        """Scan with dry (zero-index) infection weather and full bee-flight days so tests isolate the start-date logic."""
        dry = pd.DataFrame(0., index=daily.index, columns=['anthracnose', 'botrytis'])
        bee = pd.Series(8., index=daily.index)
        return managed_cycles(Days(daily, dry, bee), profile('stage_thermal_v3'), range(2011, 2026))

    def test_favourable_starts_avoid_recurring_harvest_rain(self):
        daily = flat_daily()
        daily.loc[daily.index.month.isin([7, 8, 9]), 'precip_mm'] = 12.
        scan = self.scan(daily)
        favourable = scan['favourable']
        expected = ['01-01', '01-15', '02-01', '02-15'] + [f'{m:02d}-{d:02d}' for m in range(8, 13) for d in (1, 15)]
        self.assertEqual(favourable['budbreak'], expected)
        self.assertEqual(favourable['recurring'], [])
        self.assertFalse(favourable['unconstrained'])
        self.assertFalse({7, 8, 9} & set(favourable['harvest_months']))
        march = next(s for s in scan['starts'] if s['budbreak'] == '03-01')
        self.assertEqual(march['recurring'], ['harvest_heavy_rain'])
        self.assertEqual(march['events']['harvest_heavy_rain']['frequency'], 1.)
        self.assertEqual(march['dates']['harvest_start'], '05-13')
        december = next(s for s in scan['starts'] if s['budbreak'] == '12-15')
        self.assertEqual(december['events']['harvest_heavy_rain']['valid_years'], 14)

    def test_uniform_weather_is_unconstrained(self):
        scan = self.scan(flat_daily())
        self.assertTrue(scan['favourable']['unconstrained'])
        self.assertEqual(len(scan['favourable']['budbreak']), 24)

    def test_chill_clock_declines_tropics_evergreen_and_sparse_calendars(self):
        rows = []
        for i in range(12):
            row = empty_row(2011 + i, 'north', pd.Timestamp('2010-11-01'), pd.Timestamp('2011-05-01'))
            row.update(chill_hours=320, freeze_hours=0, freeze_risk_months=0, winter_month_tmin_lowest_c=9.,
                       winter_month_tmean_lowest_c=14., harvest=['2011-04-01', '2011-05-10'])
            rows.append(row)
        p = profile('stage_thermal_v3')
        deciduous = classification(rows, p)
        self.assertTrue(chill_clock(rows, deciduous, 30., p)['applicable'])
        tropical = chill_clock(rows, deciduous, -8., p)
        self.assertFalse(tropical['applicable'])
        self.assertIn('tropics', tropical['reasons'][0])
        rows[0]['harvest'] = None
        self.assertFalse(chill_clock(rows, deciduous, 30., p)['applicable'])

    def test_analysis_attaches_scan_and_uses_clock_for_risks(self):
        hourly = pd.Series(25., index=pd.date_range('2010-01-01', '2026-01-01', freq='h', inclusive='left'))
        # Dewpoint without longitude cannot place the local infection day: disease weather is unavailable, not zero.
        result = analyse(hourly, flat_daily(), -8., 'stage_thermal_v3', dewpoint=hourly - 1.)
        self.assertEqual(result['managed_cycle']['role'], 'primary')
        self.assertEqual(result['risks']['by_id']['flowering_freeze']['eligibility'], 'not_applicable')
        self.assertEqual(result['chill_portions']['mean'], 0.)
        self.assertTrue(all(s['measures']['disease_weather'] is None for s in result['managed_cycle']['starts']))
        self.assertEqual(result['managed_cycle']['favourable']['budbreak'], [])
        self.assertNotIn('managed_cycle', analyse(hourly, flat_daily(), -8., 'stage_risks_v2'))

    def test_recurring_crop_loss_excludes_starts_and_tiny_differences_tie(self):
        daily = flat_daily()
        daily.loc[daily.index.month == 1, 'tmin_c'] = -5.
        scan = self.scan(daily)
        self.assertEqual(scan['favourable']['budbreak'], list(CYCLE_STARTS[2:20]))
        loss = {s['budbreak']: s['recurring_crop_loss'] for s in scan['starts']}
        # January frost hits the late bud stage of the 1 and 15 January starts as well as their flowering.
        self.assertEqual((loss['01-15'], loss['11-15'], loss['06-01']),
                         (['bud_freeze', 'flowering_freeze'], ['fruit_frost'], []))
        daily = flat_daily()
        daily.loc['2015-06-01', 'precip_mm'] = 12.
        self.assertTrue(self.scan(daily)['favourable']['unconstrained'])

    def test_cycles_stalled_by_cold_count_as_crop_loss(self):
        daily = flat_daily()
        daily.loc[daily.index.month.isin([12, 1, 2]), 'tmean_c'] = 5.
        scan = self.scan(daily)
        november = next(s for s in scan['starts'] if s['budbreak'] == '11-15')
        self.assertEqual(november['stalled_cycles'], 14)
        self.assertEqual(november['events']['flowering_freeze']['frequency'], 1.)
        self.assertEqual(november['recurring_crop_loss'], ['bud_freeze', 'flowering_freeze', 'fruit_frost'])
        self.assertNotIn('11-15', scan['favourable']['budbreak'])

    def test_selection_survives_non_transitive_near_ties(self):
        keys = [key for key, _ in SCAN_MEASURES]
        start = lambda name, *shares: {'budbreak': name,
                                       'measures': {**dict.fromkeys(keys, 0.), **dict(zip(keys[-3:], shares))}}
        cyclic = [start('a', 0., .1, .2), start('b', .2, 0., .1), start('c', .1, .2, 0.)]
        tolerance = dict.fromkeys(keys, .1)
        self.assertEqual([s['budbreak'] for s in select_favourable(cyclic, tolerance)], ['a', 'b', 'c'])
        chosen = select_favourable([*cyclic, start('near', .05, .1, .2), start('far', .3, .3, .3)], tolerance)
        self.assertEqual([s['budbreak'] for s in chosen], ['a', 'b', 'c', 'near'])


class InfectionTests(unittest.TestCase):
    def setUp(self):
        self.p = profile('stage_thermal_v3')
        self.index = pd.date_range('2020-03-01', '2020-03-06', freq='h', inclusive='left')

    def weather(self, *wet, temp=25.):
        t = pd.Series(temp, index=self.index)
        d = t - 10.
        for hours in wet:
            d.iloc[list(hours)] = t.iloc[list(hours)]
        return t, d

    @staticmethod
    def indices(w, t):
        fa = -3.7 + 0.33 * w - 0.069 * w * t + 0.005 * w * t ** 2 - 9.3e-5 * w * t ** 3
        fb = -4.268 - 0.0901 * w + 0.0294 * w * t - 2.35e-5 * w * t ** 3
        return 1 / (1 + math.exp(-fa)), 1 / (1 + math.exp(-fb))

    def test_three_dry_hours_join_a_period_and_four_split_it(self):
        joined = infection_risk(*self.weather(range(30, 36), range(39, 45)), 0., self.p)
        self.assertAlmostEqual(joined.loc['2020-03-02', 'anthracnose'], self.indices(12, 25.)[0])
        self.assertAlmostEqual(joined.loc['2020-03-02', 'botrytis'], self.indices(12, 25.)[1])
        split = infection_risk(*self.weather(range(30, 36), range(40, 46)), 0., self.p)
        self.assertAlmostEqual(split.loc['2020-03-02', 'anthracnose'], self.indices(6, 25.)[0])
        self.assertEqual(split.loc['2020-03-03', 'anthracnose'], 0.)

    def test_period_counts_on_local_day_of_last_wet_hour(self):
        t, d = self.weather(range(48, 52))
        self.assertGreater(infection_risk(t, d, 0., self.p).loc['2020-03-03', 'anthracnose'], 0.)
        west = infection_risk(t, d, -82., self.p)
        self.assertGreater(west.loc['2020-03-02', 'anthracnose'], 0.)
        self.assertEqual(west.loc['2020-03-03', 'anthracnose'], 0.)

    def test_cold_wetness_is_botrytis_not_anthracnose_and_gaps_are_unavailable(self):
        t, d = self.weather(range(24, 48), temp=5.)
        risk = infection_risk(t, d, 0., self.p)
        self.assertEqual(risk.loc['2020-03-02', 'anthracnose'], 0.)
        self.assertAlmostEqual(risk.loc['2020-03-02', 'botrytis'], self.indices(24, 5.)[1])
        t.iloc[80] = np.nan
        self.assertTrue(np.isnan(infection_risk(t, d, 0., self.p).loc['2020-03-04', 'anthracnose']))

    def test_wetness_is_capped_at_fitted_range_and_cold_anthracnose_is_floored(self):
        long_warm = infection_risk(*self.weather(range(24, 84)), 0., self.p)
        self.assertAlmostEqual(long_warm.loc['2020-03-04', 'anthracnose'], self.indices(51, 25.)[0])
        self.assertAlmostEqual(long_warm.loc['2020-03-04', 'botrytis'], self.indices(32, 25.)[1])
        cool = infection_risk(*self.weather(range(24, 72), temp=8.), 0., self.p)
        self.assertAlmostEqual(cool.loc['2020-03-03', 'anthracnose'], self.indices(48, 10.)[0])
        self.assertLess(cool.loc['2020-03-03', 'anthracnose'], self.indices(48, 8.)[0])

    def test_stage_counts_use_moderate_and_high_classes(self):
        t, d = self.weather(range(30, 42), range(54, 78))
        daily = flat_daily(start='2020-03-01', end='2020-03-05')
        days = Days(daily, infection_risk(t, d, 0., self.p))
        flowering = (pd.Timestamp('2020-03-01'), pd.Timestamp('2020-03-02'))
        harvest = (pd.Timestamp('2020-03-04'), pd.Timestamp('2020-03-05'))
        m = stage_metrics(days, self.p, flowering, (pd.Timestamp('2020-03-03'),) * 2, harvest, flowering[0])
        self.assertEqual(m['flowering_infection_days'], 1)
        self.assertEqual(m['harvest_infection_days'], 1)
        self.assertEqual(m['crop_high_infection_days'], 1)
        legacy = stage_metrics(days, profile('stage_risks_v2'), flowering, (pd.Timestamp('2020-03-03'),) * 2, harvest, flowering[0])
        self.assertIsNone(legacy['crop_high_infection_days'])


class BudAndBeeTests(unittest.TestCase):
    def setUp(self):
        self.p = profile('stage_thermal_v3')

    def test_bee_flight_hours_count_warm_local_daytime_hours(self):
        t = pd.Series(10., index=pd.date_range('2020-03-01', '2020-03-04', freq='h', inclusive='left'))
        # At 82 W local solar time is UTC - 5 h: 09:00-11:00 local on 2 March is 14:00-16:00 UTC.
        t.loc['2020-03-02 14:00':'2020-03-02 16:00'] = [12.8, 20., 20.]
        t.loc['2020-03-02 22:00'] = 30.  # 17:00 local, after the daytime window
        hours = bee_flight_hours(t, -82., self.p)
        self.assertEqual((hours.loc['2020-03-01'], hours.loc['2020-03-02']), (0, 3))
        t.loc['2020-03-01 15:00'] = np.nan  # 10:00 local on 1 March
        self.assertTrue(np.isnan(bee_flight_hours(t, -82., self.p).loc['2020-03-01']))

    def test_pollination_gap_needs_a_run_of_days_without_flight(self):
        daily = flat_daily(start='2020-03-01', end='2020-03-12')
        bee = pd.Series([8, 0, 0, 0, 8, 0, 0, 0, 0, 8, 8, 8], index=daily.index, dtype=float)
        flowering = (pd.Timestamp('2020-03-01'), pd.Timestamp('2020-03-10'))
        m = stage_metrics(Days(daily, bee=bee), self.p, flowering, (pd.Timestamp('2020-03-11'),) * 2,
                          (pd.Timestamp('2020-03-12'),) * 2, flowering[0])
        self.assertEqual((m['flowering_no_flight_days'], m['flowering_longest_no_flight_run']), (7, 4))
        self.assertAlmostEqual(m['flowering_bee_flight_hours_mean'], 2.4)
        rows = []
        for i in range(12):
            row = empty_row(2011 + i, 'north', pd.Timestamp('2010-11-01'), pd.Timestamp('2011-05-01'))
            row.update(chill_hours=320, freeze_hours=0, freeze_risk_months=0, winter_month_tmin_lowest_c=9.,
                       winter_month_tmean_lowest_c=14.)
            row['metrics']['flowering_longest_no_flight_run'] = 4 if i < 6 else 3
            rows.append(row)
        gap = risks(rows, self.p)['by_id']['pollination_weather']
        self.assertEqual((gap['years_with_event'], gap['valid_years'], gap['eligibility']), (6, 12, 'ranked'))
        self.assertNotIn('bud_freeze', risks(rows, profile('stage_risks_v2'))['by_id'])

    def test_bud_freeze_uses_early_then_late_critical_temperature(self):
        daily = flat_daily(start='2020-01-01', end='2020-06-30')
        bud = pd.Timestamp('2020-01-01')
        (flowering, harvest), _ = stage_dates(Days(daily), bud, self.p)
        self.assertEqual(flowering[0], pd.Timestamp('2020-01-10'))  # 10 degree-days a day from 2 January
        fruit = (flowering[1] + pd.Timedelta(days=1), harvest[0] - pd.Timedelta(days=1))

        def freeze(day, tmin, p=self.p):
            weather = daily.copy()
            weather.loc[day, 'tmin_c'] = tmin
            return stage_metrics(Days(weather), p, flowering, fruit, harvest, bud, bud)['bud_freeze_days']
        self.assertEqual(freeze('2020-01-03', -5.), 0)   # 20 degree-days after budbreak: early stage, -6.7 C
        self.assertEqual(freeze('2020-01-03', -6.7), 1)
        self.assertEqual(freeze('2020-01-07', -5.), 1)   # 60 degree-days: late stage, -3.9 C
        self.assertEqual(freeze('2020-01-10', -9.), 0)   # flowering has started; the flowering rule applies
        self.assertIsNone(freeze('2020-01-07', -9., profile('stage_risks_v2')))




class HelperTests(unittest.TestCase):
    def test_months_between_wraps_year(self):
        self.assertEqual(months_between('11-20', '02-03'), [1, 2, 11, 12])
        self.assertEqual(months_between('03-01', '03-31'), [3])

    def test_longest_run(self):
        self.assertEqual(longest_run([True, True, False, True, True, True, False]), 3)
        self.assertEqual(longest_run([False, False]), 0)

    def test_chill_portions_follow_dynamic_model_temperature_response(self):
        final = {t: chill_portions(np.full(2000, t))[-1] for t in (6., 12., 25.)}
        self.assertEqual(final[25.], 0.)
        self.assertGreater(final[6.], final[12.])
        self.assertGreater(final[12.], 0.)
        self.assertTrue((np.diff(chill_portions(np.full(2000, 6.))) >= 0).all())


if __name__ == '__main__':
    unittest.main()
