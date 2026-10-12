"""Station-truth maths: coverage rules, local-night windows across the date line, bias and contingency counts."""
import datetime as dt
import unittest
import numpy as np
import pandas as pd
from evidence.adapters import station_truth as s


def hourly(times, temps):
    times = pd.DatetimeIndex(pd.to_datetime(times, utc=True))
    return pd.DataFrame({'station_id': 'X', 'time_utc': times, 'temperature_c': np.asarray(temps, float),
                         'temperature_qc_pass': True})


class LocalNight(unittest.TestCase):
    def test_offsets(self):
        got = [s.night_offset_hours(x) for x in (0, 7.5, -7.5, 7.4, 175.3, 179.9, 180, -179.9, -180, 146.43, -71.6, -82.46)]
        self.assertEqual(got, [0, 1, -1, 0, 12, 12, 12, -12, -12, 10, -5, -5])

    def test_window_edges(self):
        # lon 0: local == UTC. 17:59 and 09:00 fall outside; 18:00 and 08:59 inside; all dated by the morning.
        times = ['2022-10-05 17:59', '2022-10-05 18:00', '2022-10-06 08:59', '2022-10-06 09:00']
        obs = hourly(times, [-9, 5, 4, -9])
        local = (obs.time_utc).dt.tz_localize(None)
        inside = (local.dt.hour >= s.NIGHT_START) | (local.dt.hour < s.NIGHT_END)
        self.assertEqual(inside.tolist(), [False, True, True, False])
        full = hourly(pd.date_range('2022-10-05 18:00', '2022-10-06 08:00', freq='h'), np.arange(15))
        full = pd.concat([full, obs], ignore_index=True)
        night = s.local_night_min(full, 0.)
        self.assertEqual(night.index.tolist(), [pd.Timestamp('2022-10-06')])
        self.assertEqual(night.station_tmin_c.iloc[0], 0)
        self.assertEqual(night.hours.iloc[0], 15)
        self.assertEqual(night.grid_date.iloc[0], pd.Timestamp('2022-10-06'))

    def test_date_line(self):
        # The same UTC hours are an evening at lon +179.9 (UTC+12) and a morning at lon -179.9 (UTC-12).
        utc = pd.date_range('2022-10-06 06:00', '2022-10-06 20:00', freq='h', tz='UTC')
        obs = hourly(utc, np.linspace(5, -3, len(utc)))
        east, west = s.local_night_min(obs, 179.9), s.local_night_min(obs, -179.9)
        self.assertEqual(east.index.tolist(), [pd.Timestamp('2022-10-07')])
        self.assertEqual(east.hours.iloc[0], 15)
        self.assertEqual(east.grid_date.iloc[0], pd.Timestamp('2022-10-06'))
        # West: local 18:00 Oct 5 to 08:00 Oct 6 covers UTC 06:00-20:00 Oct 6; 09:00-... is outside.
        self.assertEqual(west.index.tolist(), [pd.Timestamp('2022-10-06')])
        self.assertEqual(west.grid_date.iloc[0], pd.Timestamp('2022-10-06'))
        self.assertEqual(east.station_tmin_c.iloc[0], -3)

    def test_grid_day_for_us_and_nz(self):
        # Night ending 7 Oct: NZ (UTC+12) 01:30 local is 13:30 UTC on 6 Oct; Georgia (UTC-5) is 06:30 UTC on 7 Oct.
        nz = hourly(pd.date_range('2022-10-06 06:00', periods=15, freq='h'), np.zeros(15))
        us = hourly(pd.date_range('2022-10-06 23:00', periods=15, freq='h'), np.zeros(15))
        self.assertEqual(s.local_night_min(nz, 175.33).grid_date.iloc[0], pd.Timestamp('2022-10-06'))
        self.assertEqual(s.local_night_min(us, -82.46).grid_date.iloc[0], pd.Timestamp('2022-10-07'))

    def test_night_needs_twelve_hours(self):
        obs = hourly(pd.date_range('2022-10-05 18:00', periods=11, freq='h'), np.zeros(11))
        self.assertTrue(s.local_night_min(obs, 0.).empty)
        obs = hourly(pd.date_range('2022-10-05 18:00', periods=12, freq='h'), np.zeros(12))
        self.assertEqual(len(s.local_night_min(obs, 0.)), 1)


class Coverage(unittest.TestCase):
    def test_year_coverage_counts_hours_once(self):
        hours = pd.date_range('2021-01-01', '2022-01-01', freq='h', inclusive='left', tz='UTC')
        keep = hours[: int(0.8*len(hours))]
        extra = keep[:100]+pd.Timedelta(minutes=53)  # sub-hourly reports inside already-counted hours
        cov = s.year_coverage(pd.Series(keep.append(extra)))
        self.assertEqual(int(cov.loc[2021, 'hours']), 7008)
        self.assertGreaterEqual(cov.loc[2021, 'coverage'], s.MIN_YEAR_COVERAGE)
        cov = s.year_coverage(pd.Series(keep[:-1]))
        self.assertLess(cov.loc[2021, 'coverage'], s.MIN_YEAR_COVERAGE)

    def test_leap_year_denominator(self):
        hours = pd.Series(pd.date_range('2020-01-01', periods=10, freq='h', tz='UTC'))
        self.assertAlmostEqual(s.year_coverage(hours).loc[2020, 'coverage'], 10/8784)

    def test_daily_min_needs_twenty_hours(self):
        t = pd.date_range('2022-01-01', periods=20, freq='h', tz='UTC').append(
            pd.date_range('2022-01-02', periods=19, freq='h', tz='UTC'))
        daily = s.utc_daily_min(hourly(t, np.r_[np.arange(20), np.zeros(19)-5]))
        self.assertEqual(daily.index.tolist(), [pd.Timestamp('2022-01-01')])
        self.assertEqual(daily.station_tmin_c.iloc[0], 0)


class Counts(unittest.TestCase):
    def test_contingency_and_rates(self):
        station = pd.Series([-1, 0, 1, -3, 2.])
        grid = pd.Series([-0.5, 1, -1, -2.5, 3.])
        c = s.contingency(station, grid, 0.)
        self.assertEqual(c, {'hits': 2, 'misses': 1, 'false_alarms': 1, 'correct_negatives': 1})
        self.assertEqual(s.rates(c), {'hit_rate': 0.6667, 'false_alarm_ratio': 0.3333, 'false_alarm_rate': 0.5})
        c = s.contingency(station, grid, -2.2)
        self.assertEqual(c, {'hits': 1, 'misses': 0, 'false_alarms': 0, 'correct_negatives': 4})
        self.assertEqual(s.rates({'hits': 0, 'misses': 0, 'false_alarms': 0, 'correct_negatives': 3})['hit_rate'], None)

    def test_threshold_is_inclusive(self):
        self.assertEqual(s.contingency(pd.Series([-2.2]), pd.Series([-2.2]), -2.2)['hits'], 1)


class EndToEnd(unittest.TestCase):
    def test_synthetic_station(self):
        # 2021 fully covered; 2022 only 70% covered and therefore excluded.
        h21 = pd.date_range('2021-01-01', '2022-01-01', freq='h', inclusive='left', tz='UTC')
        h22 = pd.date_range('2022-01-01', '2022-12-31', freq='h', inclusive='left', tz='UTC')[: int(0.7*8760)]
        times = h21.append(h22)
        doy = times.dayofyear.to_numpy()
        temps = 10*np.cos(2*np.pi*(doy-15)/365)-5+3*np.cos(2*np.pi*times.hour.to_numpy()/24)
        obs = hourly(times, temps)
        obs.loc[obs.index[5], 'temperature_qc_pass'] = False
        obs.loc[obs.index[5], 'temperature_c'] = -60.  # failed QC; must not set the minimum
        daily = s.utc_daily_min(obs[obs.temperature_qc_pass])
        days = pd.date_range('2010-01-01', '2025-12-31')
        grid = (daily.station_tmin_c+1.5).reindex(days)
        meta = pd.DataFrame([{'station_id': 'X', 'name': 'Synthetic', 'lat': 0., 'lon': 0., 'pin_id': 'p', 'pin_name': 'Pin',
                              'pin_source': 'benchmark', 'pin_lat': 0.1, 'pin_lon': 0., 'distance_km': 11.1,
                              'rule': 'within_25km', 'event_station': False, 'rows': len(obs)}])
        tables, summary = s.run(meta, lambda sid: obs, lambda lat, lon: grid, dt.date(2026, 10, 12))
        utc = tables['daily_pairs'].query("basis == 'utc_day' and grid_at == 'pin'")
        self.assertEqual(sorted(utc.date.dt.year.unique()), [2021])
        self.assertEqual(len(utc), 365)
        self.assertGreater(utc.station_tmin_c.min(), -60)
        mb = tables['monthly_bias'].query("basis == 'utc_day' and grid_at == 'pin'")
        self.assertEqual(len(mb), 12)
        self.assertTrue(np.allclose(mb.bias_mean_c, 1.5))
        fc = tables['frost_contingency'].query("basis == 'utc_day' and grid_at == 'pin' and threshold_c == 0")
        expect = s.contingency(utc.station_tmin_c, utc.grid_tmin_c, 0.)
        self.assertEqual(int(fc.hits.sum()), expect['hits'])
        self.assertEqual(int(fc.hits.sum()), int((utc.station_tmin_c <= -1.5).sum()))
        # The grid is 1.5 C warmer, so it misses every station frost in (-1.5, 0] and never false-alarms.
        self.assertEqual(int(fc.misses.sum()), int(utc.station_tmin_c.between(-1.5, 0, inclusive='right').sum()))
        self.assertGreater(int(fc.misses.sum()), 0)
        self.assertEqual(int(fc.false_alarms.sum()), 0)
        self.assertEqual(int(fc[['hits', 'misses', 'false_alarms', 'correct_negatives']].sum().sum()), 365)
        cov = tables['station_coverage'].set_index('year')
        self.assertEqual(cov.qualifies.to_dict(), {2021: True, 2022: False})
        pin = summary['benchmark_pins'][0]['nearest_station']
        self.assertEqual(pin['years_used'], [2021])
        self.assertAlmostEqual(pin['grid_at_pin']['utc_day']['mean_tmin_bias_c'], 1.5)
        self.assertIn('local_night', pin['grid_at_station'])
        season = tables['frost_season'].query("basis == 'utc_day' and grid_at == 'pin' and threshold_c == 0")
        self.assertEqual(season.season.tolist(), [2021])
        self.assertEqual(int(season.days.iloc[0]), 31+28+31+30)

    def test_station_without_coverage_reports_note(self):
        obs = hourly(pd.date_range('2021-01-01', periods=100, freq='h'), np.zeros(100))
        meta = pd.DataFrame([{'station_id': 'X', 'name': 'Short', 'lat': 0., 'lon': 0., 'pin_id': 'p', 'pin_name': 'Pin',
                              'pin_source': 'benchmark', 'pin_lat': 0., 'pin_lon': 0., 'distance_km': 1.,
                              'rule': 'within_25km', 'event_station': True, 'rows': 100}])
        tables, summary = s.run(meta, lambda sid: obs, lambda lat, lon: None, dt.date(2026, 10, 12))
        self.assertTrue(tables['daily_pairs'].empty)
        self.assertIsNone(summary['benchmark_pins'][0]['nearest_station'])
        self.assertIsInstance(summary['event_stations'][0]['result'], str)


if __name__ == '__main__':
    unittest.main()
