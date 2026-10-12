"""Station truth: GHCNh station Tmin against NASA POWER daily Tmin, measurement only.

For every (station, pin) pair from ghcnh-stations, years with at least 80% hourly coverage give:
- daily Tmin on UTC days, the same day definition as the NASA POWER daily archive;
- a local-night minimum from 18:00 to 09:00 local time, with local time approximated as UTC plus
  round(longitude/15) hours, for frost detection.
Grid Tmin is read through postprocess.extract at the station coordinates and in the cell containing
the pin. Outputs are bias and contingency counts. Nothing here changes a model or applies a correction.
"""
import json
import math
import os
import numpy as np
import pandas as pd

SOURCE_JOB = 'ghcnh-stations'
MIN_YEAR_COVERAGE = 0.8
DAY_HOURS, NIGHT_HOURS = 24, 15
# Same 80% rule inside each day or night, so one gap cannot hide the coldest hours.
MIN_DAY_HOURS, MIN_NIGHT_HOURS = math.ceil(0.8*DAY_HOURS), math.ceil(0.8*NIGHT_HOURS)
NIGHT_START, NIGHT_END = 18, 9
THRESHOLDS = (0.0, -2.2)
# Fixed reporting window (late winter and spring), not a model input: Feb-May north, Aug-Nov south.
SPRING = {'north': (2, 3, 4, 5), 'south': (8, 9, 10, 11)}
KEYS = ['station_id', 'pin_id', 'grid_at', 'basis']

JOB = {'id': 'station-truth', 'source_ids': ['noaa-ghcnh'], 'schedule': 'monthly',
       'description': 'GHCNh station Tmin against NASA POWER daily Tmin: monthly bias and frost hit, miss and false-alarm counts',
       'max_bytes_per_run': 0, 'derived_only': True, 'inputs': ['ghcnh-stations']}


def plan(ctx):
    return []


def night_offset_hours(lon):
    """round(lon/15) with halves away from zero, so the date line maps to +12 east and -12 west."""
    x = lon/15
    return int(math.copysign(math.floor(abs(x)+0.5), x))


def year_coverage(times):
    """Share of the year's hours that hold at least one valid reading, per UTC year."""
    slots = pd.Series(times.dt.floor('h').unique())
    counts = slots.groupby(slots.dt.year).size()
    hours = pd.Series([(pd.Timestamp(y+1, 1, 1)-pd.Timestamp(y, 1, 1))/pd.Timedelta(hours=1) for y in counts.index],
                      index=counts.index)
    return pd.DataFrame({'hours': counts, 'coverage': counts/hours})


def utc_daily_min(obs):
    """Tmin per UTC day from valid readings; days with fewer than 20 distinct hours are dropped."""
    day = obs.time_utc.dt.floor('D').dt.tz_localize(None)
    g = obs.assign(day=day, slot=obs.time_utc.dt.floor('h')).groupby('day')
    out = pd.DataFrame({'station_tmin_c': g.temperature_c.min(), 'hours': g.slot.nunique()})
    out = out[out.hours >= MIN_DAY_HOURS]
    return out.assign(grid_date=out.index)


def local_night_min(obs, lon):
    """Minimum from 18:00 to 09:00 local (UTC + round(lon/15) h), dated by the morning it ends.
    grid_date is the UTC day that holds 01:30 local, the middle of the night."""
    offset = night_offset_hours(lon)
    local = (obs.time_utc+pd.Timedelta(hours=offset)).dt.tz_localize(None)
    inside = (local.dt.hour >= NIGHT_START) | (local.dt.hour < NIGHT_END)
    local, temps = local[inside], obs.temperature_c[inside]
    night = (local+pd.Timedelta(hours=24-NIGHT_START)).dt.floor('D')
    g = pd.DataFrame({'night': night, 'slot': local.dt.floor('h'), 't': temps}).groupby('night')
    out = pd.DataFrame({'station_tmin_c': g.t.min(), 'hours': g.slot.nunique()})
    out = out[out.hours >= MIN_NIGHT_HOURS]
    return out.assign(grid_date=(out.index+pd.Timedelta(hours=1.5-offset)).floor('D'))


def contingency(station, grid, threshold):
    """hits, misses, false alarms and correct negatives for 'Tmin at or below threshold'."""
    s, g = station <= threshold+1e-9, grid <= threshold+1e-9
    return {'hits': int((s & g).sum()), 'misses': int((s & ~g).sum()),
            'false_alarms': int((~s & g).sum()), 'correct_negatives': int((~s & ~g).sum())}


def rates(c):
    """Hit rate (POD), false-alarm ratio fa/(hits+fa) and false-alarm rate fa/(fa+cn); None when undefined."""
    div = lambda a, b: round(a/b, 4) if b else None
    return {'hit_rate': div(c['hits'], c['hits']+c['misses']),
            'false_alarm_ratio': div(c['false_alarms'], c['hits']+c['false_alarms']),
            'false_alarm_rate': div(c['false_alarms'], c['false_alarms']+c['correct_negatives'])}


def pair(series, grid):
    """Station minima joined to grid Tmin on grid_date; rows without both values are dropped."""
    out = series.join(grid.rename('grid_tmin_c'), on='grid_date', how='inner').dropna(subset=['station_tmin_c', 'grid_tmin_c'])
    out = out.rename_axis('date').reset_index()
    return out.assign(bias_c=out.grid_tmin_c-out.station_tmin_c)


def station_pairs(hourly, rows, grid_for):
    """Paired daily rows for one station and all its pins, plus its coverage table.
    grid_for(lat, lon) -> Series of daily Tmin indexed by naive UTC date, or None."""
    st = rows.iloc[0]
    obs = hourly[hourly.temperature_qc_pass.astype(bool) & hourly.temperature_c.notna()]
    cov = year_coverage(obs.time_utc) if len(obs) else pd.DataFrame(columns=['hours', 'coverage'])
    years = set(cov.index[cov.coverage >= MIN_YEAR_COVERAGE])
    cov = cov.rename_axis('year').reset_index().assign(station_id=st.station_id, qualifies=lambda d: d.year.isin(years))
    if not years:
        return [], cov
    series = {'utc_day': utc_daily_min(obs), 'local_night': local_night_min(obs, float(st.lon))}
    series = {k: v[v.index.year.isin(years)] for k, v in series.items()}
    grids = {'station': grid_for(float(st.lat), float(st.lon))}
    out = []
    for _, r in rows.iterrows():
        grids['pin'] = grid_for(float(r.pin_lat), float(r.pin_lon))
        for grid_at, grid in grids.items():
            if grid is None:
                continue
            for basis, s in series.items():
                p = pair(s, grid)
                out.append(p.assign(station_id=r.station_id, pin_id=r.pin_id, grid_at=grid_at, basis=basis))
    return out, cov


def monthly_bias(pairs):
    g = pairs.assign(month=pairs.date.dt.month, year=pairs.date.dt.year).groupby(KEYS+['month'])
    return pd.DataFrame({'days': g.size(), 'years': g.year.nunique(), 'bias_mean_c': g.bias_c.mean(),
                         'bias_median_c': g.bias_c.median(), 'mae_c': g.bias_c.apply(lambda x: x.abs().mean()),
                         'station_tmin_mean_c': g.station_tmin_c.mean(), 'grid_tmin_mean_c': g.grid_tmin_c.mean()}).reset_index()


def counts(frame, threshold):
    c = contingency(frame.station_tmin_c, frame.grid_tmin_c, threshold)
    return {**c, **rates(c)}


def frost_by_month(pairs):
    rows = []
    for key, g in pairs.groupby(KEYS+[pairs.date.dt.month.rename('month')]):
        for t in THRESHOLDS:
            rows.append({**dict(zip(KEYS+['month'], key)), 'threshold_c': t, 'days': len(g), **counts(g, t)})
    return pd.DataFrame(rows)


def season_of(dates, lat):
    """(season label, in-window flag) for the fixed spring window of the pin's hemisphere."""
    months = SPRING['north' if lat >= 0 else 'south']
    return dates.dt.year, dates.dt.month.isin(months)


def frost_seasons(pairs, pin_lat):
    rows = []
    for key, g in pairs.groupby(KEYS):
        year, inside = season_of(g.date, pin_lat[key[1]])
        for season, s in g[inside].groupby(year[inside]):
            for t in THRESHOLDS:
                sf, gf = s[s.station_tmin_c <= t+1e-9], s[s.grid_tmin_c <= t+1e-9]
                rows.append({**dict(zip(KEYS, key)), 'season': int(season),
                             'months': '-'.join(str(m) for m in SPRING['north' if pin_lat[key[1]] >= 0 else 'south']),
                             'threshold_c': t, 'days': len(s), **counts(s, t),
                             'station_min_c': float(s.station_tmin_c.min()), 'grid_min_c': float(s.grid_tmin_c.min()),
                             'last_station_frost': sf.date.max().date().isoformat() if len(sf) else None,
                             'last_grid_frost': gf.date.max().date().isoformat() if len(gf) else None})
    return pd.DataFrame(rows)


def pin_summary(pairs, meta):
    first = meta.drop_duplicates(['station_id', 'pin_id']).set_index(['station_id', 'pin_id'])
    rows = []
    for key, g in pairs.groupby(KEYS):
        m = first.loc[(key[0], key[1])]
        row = {**dict(zip(KEYS, key)), 'pin_name': m.pin_name, 'pin_source': m.pin_source, 'station_name': m['name'],
               'distance_km': round(float(m.distance_km), 2), 'rule': m.rule, 'event_station': bool(m.event_station),
               'years_used': ','.join(str(y) for y in sorted(g.date.dt.year.unique())), 'days': len(g),
               'bias_mean_c': round(float(g.bias_c.mean()), 3), 'mae_c': round(float(g.bias_c.abs().mean()), 3)}
        for t in THRESHOLDS:
            tag = f'{t:g}'.replace('-', 'm').replace('.', '_')
            row.update({f'{k}_{tag}': v for k, v in counts(g, t).items()})
        rows.append(row)
    return pd.DataFrame(rows)


def entry(summary, station_id, pin_id):
    """summary.json block for one pair from the pin_summary table."""
    s = summary[(summary.station_id == station_id) & (summary.pin_id == pin_id)]
    if s.empty:
        return None
    base = s.iloc[0]
    out = {'station_id': station_id, 'station_name': base.station_name, 'distance_km': base.distance_km,
           'rule': base.rule, 'event_station': bool(base.event_station),
           'years_used': [int(y) for y in base.years_used.split(',')] if base.years_used else []}
    for _, r in s.iterrows():
        block = {'days': int(r.days), 'mean_tmin_bias_c': r.bias_mean_c, 'mae_c': r.mae_c}
        for t in THRESHOLDS:
            tag = f'{t:g}'.replace('-', 'm').replace('.', '_')
            block[f'frost_le_{t:g}c'] = {k: (None if pd.isna(r[f'{k}_{tag}']) else (int(r[f'{k}_{tag}']) if k in ('hits', 'misses', 'false_alarms', 'correct_negatives') else float(r[f'{k}_{tag}'])))
                                         for k in ('hits', 'misses', 'false_alarms', 'correct_negatives', 'hit_rate', 'false_alarm_ratio', 'false_alarm_rate')}
        out.setdefault(f'grid_at_{r.grid_at}', {})[r.basis] = block
    return out


def build_summary(meta, summary, today):
    """Per benchmark pin: the nearest station with qualifying years; event stations listed separately."""
    pins, events = [], []
    for pin_id, rows in meta[meta.pin_source == 'benchmark'].groupby('pin_id', sort=True):
        rows = rows.sort_values('distance_km')
        block = next((e for e in (entry(summary, s, pin_id) for s in rows.station_id) if e), None)
        pins.append({'pin_id': pin_id, 'pin_name': rows.pin_name.iloc[0], 'nearest_station': block,
                     'note': None if block else 'No selected station has a year with 80% hourly coverage that overlaps the grid archive.'})
    for _, r in meta[meta.event_station].drop_duplicates(['station_id', 'pin_id']).iterrows():
        events.append({'pin_id': r.pin_id, 'pin_name': r.pin_name, 'station_id': r.station_id, 'station_name': r['name'],
                       'distance_km': round(float(r.distance_km), 2),
                       'result': entry(summary, r.station_id, r.pin_id) or 'no year with 80% hourly coverage in 2010-2025'})
    return {'generated_on': today.isoformat(), 'method': 'station-truth-v1',
            'definitions': {'bias': 'grid Tmin minus station Tmin, mean over paired days (deg C)',
                            'utc_day': 'station minimum over the UTC day, days with at least 20 distinct hours',
                            'local_night': 'station minimum 18:00 to 09:00 local (UTC + round(lon/15) h), nights with at least 12 of 15 hours, paired with the grid UTC day holding 01:30 local',
                            'grid_at_pin': 'NASA POWER cell containing the pin (the cell the app uses)',
                            'grid_at_station': 'NASA POWER cell containing the station',
                            'hit_rate': 'hits / (hits + misses)', 'false_alarm_ratio': 'false alarms / (hits + false alarms)',
                            'false_alarm_rate': 'false alarms / (false alarms + correct negatives)',
                            'years_used': f'UTC years with at least {MIN_YEAR_COVERAGE:.0%} of hours holding a QC-passed temperature, within the grid archive'},
            'limitations': ['Measurement only: no model, threshold or correction was changed.',
                            'Airport and synoptic stations are not orchard canopy sites.',
                            'The grid daily minimum covers a whole UTC day; the local-night minimum covers 15 hours.'],
            'benchmark_pins': pins, 'event_stations': events}


def power_grid(root):
    """Cached grid_for(lat, lon) over postprocess.extract (read-only), or None off the land mask."""
    from postprocess import LandMask, extract
    land, cache = LandMask(root), {}

    def grid_for(lat, lon):
        if (lat, lon) not in cache:
            frame, _ = extract(root, lat, lon, land, padding=True)
            cache[(lat, lon)] = None if frame is None else pd.Series(frame.tmin_c.to_numpy(), index=pd.DatetimeIndex(frame.time))
        return cache[(lat, lon)]
    return grid_for


def run(meta, hourly_for, grid_for, today):
    """All tables and summary.json content; hourly_for(station_id) -> tidy hourly table or None."""
    pairs, coverage = [], []
    for sid, rows in meta.groupby('station_id', sort=True):
        hourly = hourly_for(sid)
        if hourly is None or hourly.empty:
            continue
        p, cov = station_pairs(hourly, rows, grid_for)
        pairs += p
        coverage.append(cov)
    cols = ['date', 'station_tmin_c', 'hours', 'grid_date', 'grid_tmin_c', 'bias_c', *KEYS]
    pairs = pd.concat(pairs, ignore_index=True) if pairs else pd.DataFrame(columns=cols)
    pairs['date'] = pd.to_datetime(pairs.date)
    pin_lat = dict(zip(meta.pin_id, meta.pin_lat))
    summary = pin_summary(pairs, meta) if len(pairs) else pd.DataFrame(columns=KEYS)
    tables = {'daily_pairs': pairs[cols],
              'station_coverage': pd.concat(coverage, ignore_index=True) if coverage else pd.DataFrame(),
              'monthly_bias': monthly_bias(pairs) if len(pairs) else pd.DataFrame(),
              'frost_contingency': frost_by_month(pairs) if len(pairs) else pd.DataFrame(),
              'frost_season': frost_seasons(pairs, pin_lat) if len(pairs) else pd.DataFrame(),
              'pin_summary': summary}
    return tables, build_summary(meta, summary, today)


def parse(ctx, assets):
    meta = ctx.read_table(SOURCE_JOB, 'station_meta')

    def hourly_for(sid):
        if not int(meta.loc[meta.station_id == sid, 'rows'].iloc[0]):
            return None
        return ctx.read_table(SOURCE_JOB, f'hourly_{sid}')
    tables, summary = run(meta, hourly_for, power_grid(ctx.weather_root()), ctx.today)
    for name, table in tables.items():
        ctx.write_table(name, table)
    target = ctx.paths.derived/'summary.json'
    partial = target.with_name(target.name+'.partial')
    partial.write_text(json.dumps(summary, indent=1, allow_nan=False, default=str))
    os.replace(partial, target)
    pairs = tables['daily_pairs']
    result = {'pairs': int(len(tables['pin_summary'])), 'paired_days': int(len(pairs)),
              'stations_used': int(pairs.station_id.nunique()) if len(pairs) else 0,
              'benchmark_pins_with_station': sum(p['nearest_station'] is not None for p in summary['benchmark_pins'])}
    ctx.log('station_truth', **result)
    return result
