"""Open-field + ground production analysis for one coordinate.

Chill-triggered calendar, stage exposures and production-system hypothesis adapted from the
reviewed sections of Paul Adunola's R workflow (chill -> forcing -> fixed offsets -> stage weather).
Every constant is a provisional assumption for a UF-type low-chill southern highbush, not a
calibrated cultivar parameter. Outputs are exposures and frequencies, never yield or damage
probabilities, and never cultivar recommendations.

Behaviour changes relative to the R source are deliberate and listed in CHANGES.
"""
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from discover import write_json
from evidence_report import complete, dry_spell, table
from postprocess import ROOT, LandMask, extract

METHOD = 'open-field-production-v1'

PROFILES = {
    'legacy_paul_v1': {
        'chill_definition': 'below_7_2',      # executed R rule: T < 7.2 C, no lower bound
        'chill_requirement_hours': 50,
        'gdd_base_c': 7.0,
        'gdd_to_budbreak': 150.0,
        'flowering_after_budbreak_days': [14, 35],
        'harvest_after_flowering_start_days': [70, 110],
        'horizon_days': 450,
        'frost_threshold_c': 0.0,
        'damaging_flower_freeze_c': -2.2,
        'heat_threshold_c': 32.0,
        'severe_heat_threshold_c': 35.0,
        'heavy_rain_mm': 10.0,
        'dry_day_mm': 1.0,
        'disease_temp_min_c': 15.0,
        'disease_temp_max_c': 28.0,
        'disease_rh_threshold': 85.0,
        'disease_rain_threshold_mm': 0.1,
        'evergreen_chill_max': 100,
        'deciduous_chill_min': 300,
        'evergreen_winter_tmin_min': 7.2,
        'evergreen_winter_tavg_min': 12.8,
        'evergreen_freezing_hours_max': 1,
        'evergreen_freeze_risk_months_max': 0,
        'class_majority': 2 / 3,
    },
}
PROFILES['legacy_paul_100h_v1'] = {**PROFILES['legacy_paul_v1'], 'chill_requirement_hours': 100}
PROFILES['bounded_uf_v1'] = {**PROFILES['legacy_paul_v1'], 'chill_definition': 'bounded_0_7_2'}
PROFILES['bounded_uf_100h_v1'] = {**PROFILES['bounded_uf_v1'], 'chill_requirement_hours': 100}

CHANGES = [
    'Northern calendar dates are reconstructed from the same 1 November anchor used for the offsets; the R summary used 1 October (-31 days).',
    'Every site-year returns the same typed row with a status and per-metric issue reasons; incomplete years are never dropped or schema-split.',
    'Chill, forcing and every stage metric require a complete, unique, ordered window; missing values are never compressed, zero-filled or counted as safe.',
    'Suspect or out-of-range rainfall declines rain, dry-spell and disease-weather metrics for that window instead of contributing zero.',
    'A non-positive chill requirement is refused (anchor_required); zero chill never silently anchors on the first winter date.',
    'Risks are ranked by the frequency of years with an event under the profile thresholds, not by percentile against a query-dependent reference panel; no weighted total is produced.',
    'The production system is reported three ways: from multi-year means (R behaviour), per-year distribution, and a two-thirds majority vote with transitional otherwise.',
    'Winter-month features for the multi-feature rule come from our daily series (Jan-Mar north, Jul-Sep south of the winter year), not WorldClim monthly climatologies.',
]

LIMITATIONS = [
    'Constants encode a UF-type low-chill southern highbush under open field + ground; they are provisional assumptions Paul set by judgement, not measured genotype parameters.',
    'The calendar is a chill-triggered deciduous/semi-evergreen clock. Where the environment classifies as evergreen the production window is management-determined and this calendar does not apply.',
    'NASA POWER grid cells (0.5 x 0.625 degrees) showed warm minimum-temperature bias against stations in the 2020 pilot; chill hours and freeze counts are therefore likely undercounted. No correction is applied.',
    'UTC hours throughout. The original R requested local solar time; the difference affects window edges only.',
    'Frequencies come from at most 15 winters; 95% Wilson intervals are shown and are wide. Do not over-read differences between sites.',
    'Disease-favourable weather is a daily temperature/humidity/rain rule, not disease incidence. Longest dry spell is not a soil water balance.',
    'No cultivar ranking, no soil scoring, no tunnel or pot effects, no forecast, no independent phenology validation yet.',
]

STAGE_METRICS = (
    'flower_tmin_min_c', 'flower_freeze_days', 'flowering_rain_mm', 'flowering_heavy_rain_days',
    'flowering_disease_days', 'flowering_vpd_mean_kpa',
    'fruit_heat_days', 'fruit_severe_heat_days', 'fruit_vpd_mean_kpa',
    'harvest_rain_mm', 'harvest_heavy_rain_days', 'harvest_disease_days', 'harvest_vpd_mean_kpa',
    'production_max_dry_days', 'production_radiation_mean_mj', 'production_gdd',
)
OFFSETS = ('chill', 'budbreak', 'flowering_start', 'flowering_end', 'harvest_start', 'harvest_end')
EVENTS = (   # name, numerator predicate field, denominator field, exposure field, label
    ('chill_shortfall', 'chill_hours', 'chill_hours', 'Winters below the chill requirement'),
    ('flowering_freeze', 'flower_freeze_days', 'flower_freeze_days', 'Modelled flowering with a day at or below the damaging freeze threshold'),
    ('fruit_severe_heat', 'fruit_severe_heat_days', 'fruit_severe_heat_days', 'Fruit development with a day at or above the severe heat threshold'),
    ('harvest_heavy_rain', 'harvest_heavy_rain_days', 'harvest_heavy_rain_days', 'Modelled harvest with a heavy-rain day'),
)
CLASSES = ('Evergreen', 'Semi-evergreen', 'Deciduous')


def profile(name):
    p = PROFILES[name]
    if p['chill_requirement_hours'] <= 0:
        raise ValueError('anchor_required: a zero-chill scenario needs an explicit forcing anchor')
    if p['chill_definition'] not in ('below_7_2', 'bounded_0_7_2'):
        raise ValueError('Unknown chill definition')
    return p


def hemisphere(lat):
    return 'south' if lat < 0 else 'north'


def window(year, hemi):
    """Six-month chill window; end is exclusive. North: 1 Nov (year-1) to 1 May (year). South: 1 Apr to 1 Oct (year)."""
    if hemi == 'south':
        return pd.Timestamp(f'{year}-04-01'), pd.Timestamp(f'{year}-10-01')
    return pd.Timestamp(f'{year-1}-11-01'), pd.Timestamp(f'{year}-05-01')


def winter_months(year, hemi):
    return [(year, m) for m in ((7, 8, 9) if hemi == 'south' else (1, 2, 3))]


def chill_flags(temps, definition):
    return (temps < 7.2) if definition == 'below_7_2' else ((temps >= 0) & (temps <= 7.2))


def runs(flags):
    flags = np.asarray(flags, dtype=bool)
    return int((flags & ~np.concatenate(([False], flags[:-1]))).sum())


def vpd_kpa(tmean, rh):
    es = 0.6108 * np.exp(17.27 * tmean / (tmean + 237.3))
    return np.maximum(es * (1 - rh / 100), 0)


def clean_rain(daily):
    rain = daily.precip_mm.astype(float).copy()
    if 'precip_suspect_extreme' in daily:
        rain = rain.mask(daily.precip_suspect_extreme.fillna(True).astype(bool))
    return rain.mask((rain < 0) | (rain > 1000))


def clean_rh(daily):
    rh = daily.rh_mean_pct.astype(float)
    return rh.mask((rh < 0) | (rh > 100))


def stage_days(series, start, end):
    """Complete daily values over the inclusive [start, end] window, else None."""
    if end < start:
        return None
    return complete(series, start, end + pd.Timedelta(days=1), 'D')


def month_means(daily, year, hemi):
    """Lowest monthly mean of daily Tmin and Tmean over the winter months; None unless every month is complete."""
    tmin, tmean = [], []
    for y, m in winter_months(year, hemi):
        start = pd.Timestamp(year=y, month=m, day=1)
        a = complete(daily.tmin_c.astype(float), start, start + pd.offsets.MonthBegin(1), 'D')
        b = complete(daily.tmean_c.astype(float), start, start + pd.offsets.MonthBegin(1), 'D')
        if a is None or b is None:
            return None, None
        tmin.append(float(a.mean()))
        tmean.append(float(b.mean()))
    return min(tmin), min(tmean)


def freeze_risk_months(daily, start, end, frost):
    """Months inside the chill window whose mean daily Tmin is at or below the frost threshold; None if any month incomplete."""
    count = 0
    cursor = start
    while cursor < end:
        nxt = cursor + pd.offsets.MonthBegin(1)
        values = complete(daily.tmin_c.astype(float), cursor, min(nxt, end), 'D')
        if values is None:
            return None
        count += int(values.mean() <= frost)
        cursor = nxt
    return count


def empty_row(year, hemi, start, end):
    return {
        'winter_year': year, 'hemisphere': hemi,
        'season_start': str(start.date()), 'season_end_exclusive': str(end.date()),
        'status': 'incomplete_chill',
        'chill_hours': None, 'freeze_hours': None, 'freeze_events': None,
        'winter_month_tmin_lowest_c': None, 'winter_month_tmean_lowest_c': None, 'freeze_risk_months': None,
        'chill_date': None, 'budbreak_date': None, 'flowering': None, 'fruit': None, 'harvest': None,
        'offset_days': {k: None for k in OFFSETS},
        'metrics': {k: None for k in STAGE_METRICS},
        'issues': {},
    }


def season(hourly, daily, lat, year, p):
    """One winter year: fixed-schema row. `hourly` is a Series of hourly T (C); `daily` a DataFrame indexed by date."""
    hemi = hemisphere(lat)
    start, end = window(year, hemi)
    row = empty_row(year, hemi, start, end)
    if daily.index.has_duplicates:
        raise ValueError('Duplicate daily timestamps')
    row['winter_month_tmin_lowest_c'], row['winter_month_tmean_lowest_c'] = month_means(daily, year, hemi)
    row['freeze_risk_months'] = freeze_risk_months(daily, start, end, p['frost_threshold_c'])

    winter = complete(hourly.astype(float), start, end, 'h')
    if winter is None:
        row['issues']['chill'] = 'missing/nonfinite hourly temperature in chill window'
        return row
    flags = chill_flags(winter.to_numpy(), p['chill_definition'])
    freezing = winter.to_numpy() <= p['frost_threshold_c']
    row.update(chill_hours=int(flags.sum()), freeze_hours=int(freezing.sum()), freeze_events=runs(freezing))
    reached = np.cumsum(flags) >= p['chill_requirement_hours']
    if not reached.any():
        row['status'] = 'chill_not_met'
        return row
    chill_date = winter.index[int(np.argmax(reached))].floor('D')
    row['chill_date'] = str(chill_date.date())

    tmean = daily.tmean_c.astype(float)
    total, bud = 0.0, None
    for day in pd.date_range(chill_date, start + pd.Timedelta(days=p['horizon_days'])):
        t = tmean.get(day, np.nan)
        if not np.isfinite(t):
            row['status'] = 'incomplete_gdd'
            row['issues']['budbreak'] = f'missing daily mean temperature at {day.date()}'
            return row
        total += max(float(t) - p['gdd_base_c'], 0.0)
        if total >= p['gdd_to_budbreak']:
            bud = day
            break
    if bud is None:
        row['status'] = 'gdd_not_met_within_horizon'
        return row
    fa, fb = p['flowering_after_budbreak_days']
    ha, hb = p['harvest_after_flowering_start_days']
    d = pd.Timedelta
    flowering = (bud + d(days=fa), bud + d(days=fb))
    harvest = (flowering[0] + d(days=ha), flowering[0] + d(days=hb))
    fruit = (flowering[1] + d(days=1), harvest[0] - d(days=1))
    row.update(budbreak_date=str(bud.date()),
               flowering=[str(x.date()) for x in flowering],
               fruit=[str(x.date()) for x in fruit],
               harvest=[str(x.date()) for x in harvest])
    dates = dict(chill=chill_date, budbreak=bud, flowering_start=flowering[0], flowering_end=flowering[1],
                 harvest_start=harvest[0], harvest_end=harvest[1])
    row['offset_days'] = {k: int((v - start).days) for k, v in dates.items()}

    rain, rh = clean_rain(daily), clean_rh(daily)
    tmin, tmax = daily.tmin_c.astype(float), daily.tmax_c.astype(float)
    m, issues = row['metrics'], row['issues']

    def disease_days(a, b):
        t, h, r = stage_days(tmean, a, b), stage_days(rh, a, b), stage_days(rain, a, b)
        if t is None or h is None or r is None:
            return None
        hit = ((t >= p['disease_temp_min_c']) & (t <= p['disease_temp_max_c'])
               & (h >= p['disease_rh_threshold']) & (r >= p['disease_rain_threshold_mm']))
        return int(hit.sum())

    def vpd_mean(a, b):
        t, h = stage_days(tmean, a, b), stage_days(rh, a, b)
        return None if t is None or h is None else float(vpd_kpa(t.to_numpy(), h.to_numpy()).mean())

    cold = stage_days(tmin, *flowering)
    if cold is not None:
        m['flower_tmin_min_c'] = float(cold.min())
        m['flower_freeze_days'] = int((cold <= p['damaging_flower_freeze_c']).sum())
    wet = stage_days(rain, *flowering)
    if wet is not None:
        m['flowering_rain_mm'] = float(wet.sum())
        m['flowering_heavy_rain_days'] = int((wet >= p['heavy_rain_mm']).sum())
    m['flowering_disease_days'] = disease_days(*flowering)
    m['flowering_vpd_mean_kpa'] = vpd_mean(*flowering)
    hot = stage_days(tmax, *fruit)
    if hot is not None:
        m['fruit_heat_days'] = int((hot >= p['heat_threshold_c']).sum())
        m['fruit_severe_heat_days'] = int((hot >= p['severe_heat_threshold_c']).sum())
    m['fruit_vpd_mean_kpa'] = vpd_mean(*fruit)
    wet = stage_days(rain, *harvest)
    if wet is not None:
        m['harvest_rain_mm'] = float(wet.sum())
        m['harvest_heavy_rain_days'] = int((wet >= p['heavy_rain_mm']).sum())
    m['harvest_disease_days'] = disease_days(*harvest)
    m['harvest_vpd_mean_kpa'] = vpd_mean(*harvest)
    m['production_max_dry_days'] = dry_spell(rain, start, harvest[1] + d(days=1))
    if 'shortwave_mj_m2_day' in daily:
        sun = stage_days(daily.shortwave_mj_m2_day.astype(float), start, harvest[1])
        m['production_radiation_mean_mj'] = None if sun is None else float(sun.mean())
    heat = stage_days(tmean, start, harvest[1])
    m['production_gdd'] = None if heat is None else float(np.maximum(heat.to_numpy() - p['gdd_base_c'], 0).sum())

    reasons = {'tmin': 'missing/nonfinite daily minimum temperature in window',
               'tmax': 'missing/nonfinite daily maximum temperature in window',
               'rain': 'missing/nonfinite/negative/suspect rainfall in window',
               'rh_t': 'missing/nonfinite humidity or temperature in window',
               'disease': 'missing/nonfinite temperature, humidity or rainfall in window',
               'sun': 'missing/nonfinite radiation in window',
               'gdd': 'missing/nonfinite daily mean temperature in window'}
    needs = {'flower_tmin_min_c': 'tmin', 'flower_freeze_days': 'tmin', 'flowering_rain_mm': 'rain',
             'flowering_heavy_rain_days': 'rain', 'flowering_disease_days': 'disease', 'flowering_vpd_mean_kpa': 'rh_t',
             'fruit_heat_days': 'tmax', 'fruit_severe_heat_days': 'tmax', 'fruit_vpd_mean_kpa': 'rh_t',
             'harvest_rain_mm': 'rain', 'harvest_heavy_rain_days': 'rain', 'harvest_disease_days': 'disease',
             'harvest_vpd_mean_kpa': 'rh_t', 'production_max_dry_days': 'rain',
             'production_radiation_mean_mj': 'sun', 'production_gdd': 'gdd'}
    for key, value in m.items():
        if value is None:
            issues[key] = reasons[needs[key]]
    row['status'] = 'complete' if not issues else 'incomplete_metrics'
    return row


def classify_chill_only(chill, p):
    if chill is None:
        return None
    if chill < p['evergreen_chill_max']:
        return 'Evergreen'
    if chill < p['deciduous_chill_min']:
        return 'Semi-evergreen'
    return 'Deciduous'


def classify_multi(chill, tmin_low, tmean_low, freeze_hours, freeze_months, p):
    if any(v is None for v in (chill, tmin_low, tmean_low, freeze_hours, freeze_months)):
        return None
    if chill >= p['deciduous_chill_min']:
        return 'Deciduous'
    if (chill < p['evergreen_chill_max'] and tmin_low > p['evergreen_winter_tmin_min']
            and tmean_low > p['evergreen_winter_tavg_min'] and freeze_hours <= p['evergreen_freezing_hours_max']
            and freeze_months <= p['evergreen_freeze_risk_months_max']):
        return 'Evergreen'
    return 'Semi-evergreen'


def wilson(k, n, z=1.959964):
    if not n:
        return None
    ph = k / n
    denom = 1 + z * z / n
    centre = (ph + z * z / (2 * n)) / denom
    half = z * math.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / denom
    return [round(centre - half, 4), round(centre + half, 4)]


def valid(rows, field, source='metrics'):
    out = []
    for r in rows:
        v = r[source][field] if source else r[field]
        if v is not None:
            out.append(v)
    return out


def stats(values):
    if not values:
        return {'n': 0}
    a = np.asarray(values, dtype=float)
    return {'n': int(len(a)), 'mean': float(a.mean()), 'sd': float(a.std(ddof=1)) if len(a) > 1 else None,
            'median': float(np.median(a)), 'p10': float(np.quantile(a, .1)), 'p90': float(np.quantile(a, .9)),
            'min': float(a.min()), 'max': float(a.max())}


def calendar(rows, hemi):
    """Offsets from the season anchor across years, reconstructed on the same anchor (fixes the R -31 day shift)."""
    anchor = pd.Timestamp('2001-04-01') if hemi == 'south' else pd.Timestamp('2000-11-01')  # both non-leap spans
    out = {'anchor': 'season start (1 Nov north, 1 Apr south)'}
    for key in OFFSETS:
        values = [r['offset_days'][key] for r in rows if r['offset_days'][key] is not None]
        s = stats(values)
        if s['n']:
            for q in ('median', 'p10', 'p90'):
                s[q + '_date'] = (anchor + pd.Timedelta(days=round(s[q]))).strftime('%m-%d')
        out[key] = s
    return out


def classification(rows, p):
    chill = valid(rows, 'chill_hours', None)
    n = len(chill)
    per_year = {r['winter_year']: {'chill_only': classify_chill_only(r['chill_hours'], p),
                                   'multi_feature': classify_multi(r['chill_hours'], r['winter_month_tmin_lowest_c'],
                                                                   r['winter_month_tmean_lowest_c'], r['freeze_hours'],
                                                                   r['freeze_risk_months'], p)} for r in rows}
    out = {'valid_years': n, 'per_year': per_year}
    means = {k: (float(np.mean(v)) if v else None) for k, v in (
        ('chill_hours', chill), ('winter_month_tmin_lowest_c', valid(rows, 'winter_month_tmin_lowest_c', None)),
        ('winter_month_tmean_lowest_c', valid(rows, 'winter_month_tmean_lowest_c', None)),
        ('freeze_hours', valid(rows, 'freeze_hours', None)), ('freeze_risk_months', valid(rows, 'freeze_risk_months', None)))}
    out['multi_year_means'] = means
    out['mean_based'] = {'chill_only': classify_chill_only(means['chill_hours'], p),
                         'multi_feature': classify_multi(means['chill_hours'], means['winter_month_tmin_lowest_c'],
                                                         means['winter_month_tmean_lowest_c'], means['freeze_hours'],
                                                         means['freeze_risk_months'], p)}
    for rule in ('chill_only', 'multi_feature'):
        labels = [v[rule] for v in per_year.values() if v[rule] is not None]
        counts = {c: labels.count(c) for c in CLASSES}
        top = max(CLASSES, key=lambda c: counts[c]) if labels else None
        majority = top if labels and counts[top] / len(labels) >= p['class_majority'] else ('Transitional' if labels else None)
        out[rule] = {'year_counts': counts, 'valid_years': len(labels), 'majority': majority,
                     'majority_share': (counts[top] / len(labels)) if labels else None}
    return out


def risks(rows, p):
    """Frequency of years with an event under the profile thresholds. Ranked by frequency, ties in declared order."""
    ranked = []
    for name, field, denom_field, label in EVENTS:
        if name == 'chill_shortfall':
            values = valid(rows, 'chill_hours', None)
            k = sum(v < p['chill_requirement_hours'] for v in values)
            exposure = {'chill_hours': stats(values)}
        else:
            values = valid(rows, field)
            k = sum(v >= 1 for v in values)
            exposure = {field: stats(values)}
            if name == 'harvest_heavy_rain':
                exposure['harvest_rain_mm'] = stats(valid(rows, 'harvest_rain_mm'))
            if name == 'flowering_freeze':
                exposure['flower_tmin_min_c'] = stats(valid(rows, 'flower_tmin_min_c'))
            if name == 'fruit_severe_heat':
                exposure['fruit_heat_days'] = stats(valid(rows, 'fruit_heat_days'))
        n = len(values)
        ranked.append({'risk': name, 'label': label, 'years_with_event': k, 'valid_years': n,
                       'frequency': (k / n) if n else None, 'ci95': wilson(k, n), 'exposure': exposure})
    ranked.sort(key=lambda r: -(r['frequency'] if r['frequency'] is not None else -1))
    for i, r in enumerate(ranked, 1):
        r['rank'] = i
    unranked = {k: stats(valid(rows, k)) for k in ('production_max_dry_days', 'flowering_disease_days', 'harvest_disease_days',
                                                    'flowering_rain_mm', 'flowering_vpd_mean_kpa', 'fruit_vpd_mean_kpa',
                                                    'harvest_vpd_mean_kpa', 'production_radiation_mean_mj', 'production_gdd')}
    return {'ranked': ranked, 'unranked_exposures': unranked,
            'note': 'Ranked by frequency of winters with at least one event day; ties keep declared order. A single heavy-rain day in a six-week harvest window is near-certain at humid sites, so compare harvest_heavy_rain_days and harvest_rain_mm exposure across sites rather than that frequency alone. No event threshold is defined for the unranked exposures.'}


def analyse(hourly, daily, lat, profile_name, years=range(2011, 2026)):
    p = profile(profile_name)
    rows = [season(hourly, daily, lat, y, p) for y in years]
    hemi = hemisphere(lat)
    statuses = {}
    for r in rows:
        statuses[r['status']] = statuses.get(r['status'], 0) + 1
    return {'profile': profile_name, 'assumptions': p, 'hemisphere': hemi,
            'years': [years[0], years[-1]], 'status_counts': statuses,
            'chill_hours': stats(valid(rows, 'chill_hours', None)),
            'freeze_hours': stats(valid(rows, 'freeze_hours', None)),
            'classification': classification(rows, p),
            'calendar': calendar(rows, hemi),
            'risks': risks(rows, p),
            'seasons': rows}


def sensitivity(hourly, daily, lat, names):
    out = {}
    for name in names:
        a = analyse(hourly, daily, lat, name)
        c = a['classification']
        out[name] = {'chill_definition': a['assumptions']['chill_definition'],
                     'chill_requirement_hours': a['assumptions']['chill_requirement_hours'],
                     'chill_hours_mean': a['chill_hours'].get('mean'),
                     'status_counts': a['status_counts'],
                     'majority_chill_only': c['chill_only']['majority'],
                     'majority_multi_feature': c['multi_feature']['majority'],
                     'mean_based_multi_feature': c['mean_based']['multi_feature'],
                     'flowering_start_median': a['calendar']['flowering_start'].get('median_date'),
                     'harvest_start_median': a['calendar']['harvest_start'].get('median_date'),
                     'flowering_freeze_frequency': next(r['frequency'] for r in a['risks']['ranked'] if r['risk'] == 'flowering_freeze')}
    return out


def fmt(v, digits=1):
    if v is None:
        return 'unavailable'
    if isinstance(v, float):
        return f'{v:.{digits}f}'
    return str(v)


def render(report):
    parts = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Open-field production analysis</title>',
             '<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px;color:#173a3a}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border-bottom:1px solid #ccd;text-align:left;vertical-align:top}.scroll{overflow:auto}li{margin:8px 0}h1,h2{color:#176b65}h3{margin-top:28px}.k{font-size:13px;color:#555}</style>',
             '<h1>Open field + ground: production system, seasonal calendar, stage risks</h1>',
             f'<p class="k">Method {report["method"]} · primary profile {report["primary_profile"]} · winters {report["years"][0]}–{report["years"][1]} · existing NASA POWER archive, UTC · <strong>assumption-based, not validated, not cultivar advice</strong></p>',
             '<h2>Assumptions carried from the R workflow</h2>' + table(['Constant', 'Value'], [[k, fmt(v)] for k, v in report['sites'][next(iter(report['sites']))]['analysis']['assumptions'].items()]),
             '<h2>Deliberate changes from the R source</h2><ul>' + ''.join(f'<li>{x}</li>' for x in CHANGES) + '</ul>',
             '<h2>Limitations</h2><ul>' + ''.join(f'<li>{x}</li>' for x in LIMITATIONS) + '</ul>']
    for name, site in report['sites'].items():
        a = site['analysis']
        c, cal, rk = a['classification'], a['calendar'], a['risks']
        parts.append(f'<h2>{name}</h2><p class="k">{site["latitude"]:.4f}, {site["longitude"]:.4f} · {a["hemisphere"]}ern hemisphere · valid chill winters {a["chill_hours"]["n"]}/15 · season status: {json.dumps(a["status_counts"])}</p>')
        parts.append('<h3>1. Production-system hypothesis</h3>')
        parts.append(table(['Rule', 'From multi-year means (R behaviour)', 'Per-year counts E / S / D', 'Two-thirds majority'],
                           [[rule, c['mean_based'][rule], ' / '.join(str(c[rule]['year_counts'][k]) for k in CLASSES),
                             f"{c[rule]['majority']} ({fmt(c[rule]['majority_share'], 2)})"] for rule in ('chill_only', 'multi_feature')]))
        ch = a['chill_hours']
        parts.append(f'<p>Chill hours ({a["assumptions"]["chill_definition"]}): mean {fmt(ch.get("mean"))}, median {fmt(ch.get("median"))}, p10–p90 {fmt(ch.get("p10"))}–{fmt(ch.get("p90"))}, range {fmt(ch.get("min"))}–{fmt(ch.get("max"))} over {ch["n"]} winters. Winter-month lowest mean Tmin {fmt(c["multi_year_means"]["winter_month_tmin_lowest_c"])} °C; freezing hours mean {fmt(c["multi_year_means"]["freeze_hours"])}.</p>')
        parts.append('<h3>2. Assumption-based seasonal calendar</h3>')
        parts.append(table(['Stage', 'Valid winters', 'Median date', 'p10 date', 'p90 date', 'Median offset (days from season start)'],
                           [[k, cal[k]['n'], cal[k].get('median_date'), cal[k].get('p10_date'), cal[k].get('p90_date'), fmt(cal[k].get('median'))] for k in OFFSETS]))
        parts.append('<h3>3. Stage risks ranked by frequency of winters with an event</h3>')
        parts.append(table(['Rank', 'Risk', 'Winters with event / valid', 'Frequency', '95% CI', 'Exposure (mean, median, p90)'],
                           [[r['rank'], r['label'], f"{r['years_with_event']} / {r['valid_years']}", fmt(r['frequency'], 2),
                             '–'.join(fmt(x, 2) for x in r['ci95']) if r['ci95'] else 'unavailable',
                             '; '.join(f"{k}: {fmt(v.get('mean'))}, {fmt(v.get('median'))}, {fmt(v.get('p90'))}" for k, v in r['exposure'].items())] for r in rk['ranked']]))
        parts.append('<p class="k">Unranked exposures (n, mean, median, p90): ' + '; '.join(f"{k} ({v['n']}, {fmt(v.get('mean'))}, {fmt(v.get('median'))}, {fmt(v.get('p90'))})" for k, v in rk['unranked_exposures'].items()) + '</p>')
        parts.append(f'<p class="k">{rk["note"]}</p>')
        parts.append('<h3>Sensitivity to chill definition and requirement</h3>')
        parts.append(table(['Profile', 'Definition', 'Requirement h', 'Mean chill h', 'Majority (chill-only)', 'Majority (multi-feature)', 'Mean-based (multi)', 'Flowering start', 'Harvest start', 'Flowering-freeze frequency'],
                           [[k, v['chill_definition'], v['chill_requirement_hours'], fmt(v['chill_hours_mean']), v['majority_chill_only'], v['majority_multi_feature'], v['mean_based_multi_feature'], v['flowering_start_median'], v['harvest_start_median'], fmt(v['flowering_freeze_frequency'], 2)] for k, v in site['sensitivity'].items()]))
        parts.append('<h3>Per-winter record (primary profile)</h3>')
        parts.append(table(['Winter', 'Status', 'Chill h', 'Freeze h', 'Class (chill-only / multi)', 'Chill date', 'Budbreak', 'Flowering', 'Harvest', 'Flower Tmin', 'Freeze days', 'Fruit ≥35 days', 'Harvest rain mm', 'Heavy days', 'Dry spell'],
                           [[r['winter_year'], r['status'], r['chill_hours'], r['freeze_hours'],
                             f"{c['per_year'][r['winter_year']]['chill_only']} / {c['per_year'][r['winter_year']]['multi_feature']}",
                             r['chill_date'], r['budbreak_date'], ' → '.join(r['flowering'] or []) or None, ' → '.join(r['harvest'] or []) or None,
                             r['metrics']['flower_tmin_min_c'], r['metrics']['flower_freeze_days'], r['metrics']['fruit_severe_heat_days'],
                             r['metrics']['harvest_rain_mm'], r['metrics']['harvest_heavy_rain_days'], r['metrics']['production_max_dry_days']] for r in a['seasons']]))
    return '\n'.join(parts) + '</html>'


def run(root=ROOT, names=('Waldo', 'Citra', 'Papanduva'), primary='legacy_paul_v1'):
    report = {'method': METHOD, 'primary_profile': primary, 'years': [2011, 2025], 'changes': CHANGES, 'limitations': LIMITATIONS,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sites': {}}
    land = LandMask(root)
    for site in json.loads((root / 'config/sites.json').read_text()):
        if site['name'] not in names:
            continue
        daily, provenance = extract(root, site['lat'], site['lon'], land, padding=True)
        if daily is None:
            raise ValueError('Unsupported site')
        daily = daily.set_index('time')
        source = root / 'data/normalized/pilot/pilot' / site['id'] / 'met_hourly.parquet'
        hourly = pd.read_parquet(source).set_index('time').tmean_c
        report['sites'][site['name']] = {
            'latitude': site['lat'], 'longitude': site['lon'],
            'analysis': analyse(hourly, daily, site['lat'], primary),
            'sensitivity': sensitivity(hourly, daily, site['lat'], list(PROFILES)),
            'daily_provenance': provenance, 'hourly_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
    out = root / 'reports/production'
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / 'production_open_field.json', report)
    (out / 'production_open_field.html').write_text(render(report))
    print(json.dumps({n: {'majority_multi': s['analysis']['classification']['multi_feature']['majority'],
                          'mean_chill': s['analysis']['chill_hours'].get('mean'),
                          'flowering_start': s['analysis']['calendar']['flowering_start'].get('median_date'),
                          'top_risk': s['analysis']['risks']['ranked'][0]['risk']} for n, s in report['sites'].items()}))


if __name__ == '__main__':
    run()
