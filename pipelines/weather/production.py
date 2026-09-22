"""Open-field + ground production analysis for one coordinate.

Chill-triggered calendar, stage exposures and production-system hypothesis adapted from the
reviewed sections of Paul Adunola's R workflow (chill -> forcing -> fixed offsets -> stage weather).
Every constant is a provisional assumption for a UF-type low-chill southern highbush, not a
calibrated cultivar parameter. Outputs are exposures and frequencies, never yield or damage
probabilities, and never cultivar recommendations.

Behaviour changes relative to the R source are deliberate and listed in CHANGES.
"""
import hashlib
import html
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from discover import write_json
from evidence_report import complete, dry_spell, table
from planting import planting_window
from postprocess import ROOT, LandMask, extract

METHOD = 'open-field-production-v2'

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
PROFILES['stage_risks_v2'] = {
    **PROFILES['legacy_paul_v1'],
    'risk_min_frequency': 0.5,
    'risk_min_valid_years': 12,
    'require_applicable_calendar': True,
    'pollination_cold_tmax_c': 15.0,
    'pollination_wet_mm': 1.0,
    'warm_midwinter_threshold_c': 21.0,
}

CHANGES = [
    'Northern calendar dates are reconstructed from the same 1 November anchor used for the offsets; the R summary used 1 October (-31 days).',
    'Every site-year returns the same typed row with a status and per-metric issue reasons; incomplete years are never dropped or schema-split.',
    'Chill, forcing and every stage metric require a complete, unique, ordered window; missing values are never compressed, zero-filled or counted as safe.',
    'Suspect or out-of-range rainfall declines rain, dry-spell and disease-weather metrics for that window instead of contributing zero.',
    'A non-positive chill requirement is refused (anchor_required); zero chill never silently anchors on the first winter date.',
    'Headline risks require an event in at least half of at least 12 complete winters. Equal frequencies share a competition rank; no weighted total is produced.',
    'The production system is reported three ways: from multi-year means (R behaviour), per-year distribution, and a two-thirds majority vote with transitional otherwise.',
    'Winter-month features for the multi-feature rule come from our daily series (Jan-Mar north, Jul-Sep south of the winter year), not WorldClim monthly climatologies.',
    'The stage_risks_v2 profile preserves the legacy chill and phenology constants. Crop exposures use each winter calendar, not the median calendar.',
    'Disease weather combines complete flowering, fruit-development and harvest windows into one event family.',
    'Warm midwinter hours use fixed hemisphere dates and remain available when the chill requirement fails.',
]

LIMITATIONS = [
    'Constants encode a UF-type low-chill southern highbush under open field + ground; they are provisional assumptions Paul set by judgement, not measured genotype parameters.',
    'The calendar is a chill-triggered deciduous/semi-evergreen clock. Where the environment classifies as evergreen the production window is management-determined and this calendar does not apply.',
    'NASA POWER grid cells (0.5 x 0.625 degrees) showed warm minimum-temperature bias against stations in the 2020 pilot; chill hours and freeze counts are therefore likely undercounted. No correction is applied.',
    'UTC hours throughout. The original R requested local solar time; the difference affects window edges only.',
    'Frequencies come from at most 15 winters; 95% Wilson intervals are shown and are wide. Do not over-read differences between sites.',
    'Disease-favourable weather is a daily temperature/humidity/rain rule, not disease incidence. Longest dry spell is not a soil water balance.',
    'Pollination-unfavourable days are an operational cold-or-wet proxy, not measured bee inactivity. Cold-and-dry days are a separate supervisor hypothesis comparison.',
    'Fruit frost at or below 0 C is exposure, not a cultivar-specific injury threshold. Warm hours above 21 C are not measured chill negation.',
    'The 50% frequency and 12-winter evidence gates are an explicit reporting policy, not biological loss thresholds. Dry spells, pollination weather and warm winter have no defined loss event.',
    'No cultivar ranking, no soil scoring, no tunnel or pot effects, no forecast, no independent phenology validation yet.',
]

METRIC_CATALOG = [
    {'key': key, 'stage': stage, 'label': label, 'unit': unit, 'note': note}
    for key, stage, label, unit, note in (
        ('chill_hours', 'chill', 'Chill accumulation', 'hours', 'Profile-defined chill rule and six-month window; not chill portions.'),
        ('freeze_hours', 'chill', 'Winter freezing exposure', 'hours', 'Hourly temperature at or below the profile frost threshold during the chill window.'),
        ('warm_midwinter_hours', 'chill', 'Warm midwinter exposure', 'hours', 'T >21 C, 15 Nov to 15 Feb north, 15 May to 15 Aug south, inclusive UTC dates. Operational proxy, not measured chill negation.'),
        ('flower_tmin_min_c', 'flower', 'Lowest flowering temperature', '°C', 'Minimum daily Tmin within the modelled flowering window.'),
        ('flower_freeze_days', 'flower', 'Flowering freeze exposure', 'days', 'Daily Tmin <=-2.2 C under the legacy profile assumption; not an injury probability.'),
        ('flowering_rain_mm', 'flower', 'Flowering rainfall', 'mm', 'Total rain within flowering; suspect rainfall is excluded by declining the metric.'),
        ('flowering_heavy_rain_days', 'flower', 'Flowering heavy rain', 'days', 'Daily rain >=10 mm; operational exposure threshold.'),
        ('flowering_disease_days', 'flower', 'Flowering disease weather', 'days', 'Tmean 15–28 C inclusive, RH >=85%, rain >=0.1 mm. Provisional daily proxy, not infection or the Blueberry Advisory System.'),
        ('flowering_vpd_mean_kpa', 'flower', 'Flowering mean VPD', 'kPa', 'Calculated from daily mean temperature and RH, not hourly plant water stress.'),
        ('flowering_pollination_unfavourable_days', 'flower', 'Pollination-unfavourable weather', 'days', 'Tmax <15 C OR rain >=1 mm. Operational cold/wet proxy, not literal bee inactivity; the cutoffs are not validated by UF IN1237.'),
        ('flowering_cold_dry_days', 'flower', 'Cold-and-dry flowering weather', 'days', 'Tmax <15 C AND rain <1 mm. Supervisor hypothesis comparison only, not an established pollination or loss index.'),
        ('flowering_max_dry_days', 'flower', 'Longest flowering dry spell', 'days', 'Consecutive rain <1 mm, clipped to flowering. Not drought or soil water balance.'),
        ('fruit_heat_days', 'fruit', 'Fruit-development heat exposure', 'days', 'Daily Tmax >=32 C under the legacy assumption.'),
        ('fruit_severe_heat_days', 'fruit', 'Fruit-development severe heat exposure', 'days', 'Daily Tmax >=35 C under the legacy assumption, not fruit temperature or measured injury.'),
        ('fruit_vpd_mean_kpa', 'fruit', 'Fruit-development mean VPD', 'kPa', 'Calculated from daily mean temperature and RH, not hourly plant water stress.'),
        ('fruit_disease_days', 'fruit', 'Fruit-development disease weather', 'days', 'Tmean 15–28 C inclusive, RH >=85%, rain >=0.1 mm. Provisional daily proxy, not infection or the Blueberry Advisory System.'),
        ('fruit_frost_days', 'fruit', 'Fruit-stage frost exposure', 'days', 'Daily Tmin <=0 C. Generic exposure threshold, not stage-specific injury.'),
        ('fruit_max_dry_days', 'fruit', 'Longest fruit-development dry spell', 'days', 'Consecutive rain <1 mm, clipped to fruit development. Not drought or soil water balance.'),
        ('harvest_rain_mm', 'harvest', 'Harvest rainfall', 'mm', 'Total rain within the modelled harvest window.'),
        ('harvest_heavy_rain_days', 'harvest', 'Harvest heavy rain', 'days', 'Daily rain >=10 mm; operational exposure threshold.'),
        ('harvest_disease_days', 'harvest', 'Harvest disease weather', 'days', 'Tmean 15–28 C inclusive, RH >=85%, rain >=0.1 mm. Provisional daily proxy, not infection or the Blueberry Advisory System.'),
        ('harvest_vpd_mean_kpa', 'harvest', 'Harvest mean VPD', 'kPa', 'Calculated from daily mean temperature and RH, not hourly plant water stress.'),
        ('production_max_dry_days', 'whole', 'Longest production-window dry spell', 'days', 'Rain <1 mm. New primary uses budbreak through harvest end; legacy profiles retain season start through harvest end.'),
        ('production_radiation_mean_mj', 'whole', 'Production-window mean radiation', 'MJ/m²/day', 'New primary uses budbreak through harvest end; legacy profiles retain season start through harvest end.'),
        ('production_gdd', 'whole', 'Production-window growing degree days', '°C days', 'Sum of max(Tmean minus profile base, 0). New primary uses budbreak through harvest end; legacy profiles retain the season-start window.'),
    )
]
ROW_METRICS = ('chill_hours', 'freeze_hours', 'warm_midwinter_hours')
STAGE_METRICS = tuple(m['key'] for m in METRIC_CATALOG if m['key'] not in ROW_METRICS)
OFFSETS = ('chill', 'budbreak', 'flowering_start', 'flowering_end', 'harvest_start', 'harvest_end')
DISEASE_METRICS = ('flowering_disease_days', 'fruit_disease_days', 'harvest_disease_days')
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


def midwinter_window(year, hemi):
    """Fixed inclusive UTC dates, separate from the chill-model window."""
    if hemi == 'south':
        return pd.Timestamp(f'{year}-05-15'), pd.Timestamp(f'{year}-08-15')
    return pd.Timestamp(f'{year-1}-11-15'), pd.Timestamp(f'{year}-02-15')


def warm_midwinter_daily(daily, lat, years=range(2011, 2026)):
    """Daily-Tmax fallback only; never convert or combine these counts with hours."""
    seasons = []
    temperatures = daily.tmax_c.astype(float)
    for year in years:
        start, end = midwinter_window(year, hemisphere(lat))
        values = stage_days(temperatures, start, end)
        seasons.append({'winter_year': year, 'window': [str(start.date()), str(end.date())],
                        'value': int((values > 21.0).sum()) if values is not None else None})
    return {'metric': 'warm_midwinter_days', 'label': 'Warm midwinter days (daily Tmax proxy)',
            'unit': 'days', 'threshold_c': 21,
            'note': 'Daily Tmax >21 C over fixed inclusive midwinter dates. Complete daily windows only. This fallback counts warm days, not estimated warm hours or measured chill negation; it is never mixed with hourly statistics or risk ranking.',
            'summary': stats([s['value'] for s in seasons if s['value'] is not None]),
            'seasons': seasons}


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
        'warm_midwinter_hours': None,
        'warm_midwinter_window': [str(day.date()) for day in midwinter_window(year, hemi)],
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
    warm_start, warm_end = map(pd.Timestamp, row['warm_midwinter_window'])
    temperatures = hourly.astype(float)
    midwinter = complete(temperatures, warm_start, warm_end + pd.Timedelta(days=1), 'h')
    if midwinter is None:
        row['issues']['warm_midwinter_hours'] = 'missing/nonfinite hourly temperature in fixed midwinter window'
    else:
        row['warm_midwinter_hours'] = int((midwinter > p.get('warm_midwinter_threshold_c', 21.0)).sum())

    winter = complete(temperatures, start, end, 'h')
    if winter is None:
        row['issues']['chill'] = 'missing/nonfinite hourly temperature in chill window'
        row['issues']['crop_stages'] = 'No crop windows: the chill window is incomplete.'
        return row
    flags = chill_flags(winter.to_numpy(), p['chill_definition'])
    freezing = winter.to_numpy() <= p['frost_threshold_c']
    row.update(chill_hours=int(flags.sum()), freeze_hours=int(freezing.sum()), freeze_events=runs(freezing))
    reached = np.cumsum(flags) >= p['chill_requirement_hours']
    if not reached.any():
        row['status'] = 'chill_not_met'
        row['issues']['crop_stages'] = 'No crop windows: the chill requirement was not reached.'
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
            row['issues']['crop_stages'] = 'No crop windows: forcing temperature is incomplete.'
            return row
        total += max(float(t) - p['gdd_base_c'], 0.0)
        if total >= p['gdd_to_budbreak']:
            bud = day
            break
    if bud is None:
        row['status'] = 'gdd_not_met_within_horizon'
        row['issues']['crop_stages'] = 'No crop windows: forcing did not reach budbreak within the model horizon.'
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
        m['flowering_max_dry_days'] = dry_spell(rain, flowering[0], flowering[1] + d(days=1))
    flower_max = stage_days(tmax, *flowering)
    if wet is not None and flower_max is not None:
        cold_day = flower_max < p.get('pollination_cold_tmax_c', 15.0)
        wet_day = wet >= p.get('pollination_wet_mm', 1.0)
        m['flowering_pollination_unfavourable_days'] = int((cold_day | wet_day).sum())
        m['flowering_cold_dry_days'] = int((cold_day & ~wet_day).sum())
    m['flowering_disease_days'] = disease_days(*flowering)
    m['flowering_vpd_mean_kpa'] = vpd_mean(*flowering)
    hot = stage_days(tmax, *fruit)
    if hot is not None:
        m['fruit_heat_days'] = int((hot >= p['heat_threshold_c']).sum())
        m['fruit_severe_heat_days'] = int((hot >= p['severe_heat_threshold_c']).sum())
    m['fruit_vpd_mean_kpa'] = vpd_mean(*fruit)
    m['fruit_disease_days'] = disease_days(*fruit)
    fruit_cold = stage_days(tmin, *fruit)
    if fruit_cold is not None:
        m['fruit_frost_days'] = int((fruit_cold <= 0.0).sum())
    m['fruit_max_dry_days'] = dry_spell(rain, fruit[0], fruit[1] + d(days=1))
    wet = stage_days(rain, *harvest)
    if wet is not None:
        m['harvest_rain_mm'] = float(wet.sum())
        m['harvest_heavy_rain_days'] = int((wet >= p['heavy_rain_mm']).sum())
    m['harvest_disease_days'] = disease_days(*harvest)
    m['harvest_vpd_mean_kpa'] = vpd_mean(*harvest)
    production_start = bud if p.get('require_applicable_calendar') else start
    m['production_max_dry_days'] = dry_spell(rain, production_start, harvest[1] + d(days=1))
    if 'shortwave_mj_m2_day' in daily:
        sun = stage_days(daily.shortwave_mj_m2_day.astype(float), production_start, harvest[1])
        m['production_radiation_mean_mj'] = None if sun is None else float(sun.mean())
    heat = stage_days(tmean, production_start, harvest[1])
    m['production_gdd'] = None if heat is None else float(np.maximum(heat.to_numpy() - p['gdd_base_c'], 0).sum())

    reasons = {'tmin': 'missing/nonfinite daily minimum temperature in window',
               'tmax': 'missing/nonfinite daily maximum temperature in window',
               'rain': 'missing/nonfinite/negative/suspect rainfall in window',
               'rh_t': 'missing/nonfinite/out-of-range humidity or temperature in window',
               'disease': 'missing/nonfinite temperature, invalid humidity or missing/negative/suspect rainfall in window',
               'pollination': 'missing/nonfinite maximum temperature or missing/negative/suspect rainfall in flowering window',
               'sun': 'missing/nonfinite radiation in window',
               'gdd': 'missing/nonfinite daily mean temperature in window'}
    needs = {'flower_tmin_min_c': 'tmin', 'flower_freeze_days': 'tmin', 'flowering_rain_mm': 'rain',
             'flowering_heavy_rain_days': 'rain', 'flowering_disease_days': 'disease', 'flowering_vpd_mean_kpa': 'rh_t',
             'fruit_heat_days': 'tmax', 'fruit_severe_heat_days': 'tmax', 'fruit_vpd_mean_kpa': 'rh_t',
             'flowering_pollination_unfavourable_days': 'pollination', 'flowering_cold_dry_days': 'pollination',
             'flowering_max_dry_days': 'rain', 'fruit_max_dry_days': 'rain',
             'fruit_disease_days': 'disease', 'fruit_frost_days': 'tmin',
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


def risks(rows, p, classes=None):
    """Assess each event family using complete per-winter windows, then apply reporting gates."""
    policy = {'min_frequency': p.get('risk_min_frequency', 0.5),
              'min_valid_years': p.get('risk_min_valid_years', 12)}
    classes = classification(rows, p) if classes is None else classes
    majority = classes['multi_feature']['majority']
    unsupported = p.get('require_applicable_calendar', False) and majority in (None, 'Evergreen')
    calendar_reason = (
        'The evergreen-majority system needs a management-defined crop calendar; the chill-triggered calendar and chill requirement do not apply.'
        if majority == 'Evergreen' else
        'The production-system classification is unknown; applicability of the chill-triggered calendar and chill requirement is not established.'
    )
    exposures = {key: stats(valid(rows, key, None if key in ROW_METRICS else 'metrics'))
                 for key in (*ROW_METRICS, *STAGE_METRICS)}
    frost_source = [{'title': 'NC State: Blueberry freeze damage and protection measures',
                     'url': 'https://content.ces.ncsu.edu/blueberry-freeze-damage-and-protection-measures'}]
    winter_source = [{'title': 'UF/IFAS: Protecting blueberries from freezes in Florida',
                      'url': 'https://ask.ifas.ufl.edu/publication/HS216'}]
    # One entry per family. Additional fields describe exposure, not extra headline risks.
    definitions = (
        ('chill_shortfall', 'Winters below the assumed chill requirement', 'chill', ('chill_hours',),
         f"Winter chill hours <{p['chill_requirement_hours']}. This is a profile assumption, not a measured crop loss threshold.", winter_source),
        ('flowering_freeze', 'Flowering freeze exposure', 'flower', ('flower_freeze_days', 'flower_tmin_min_c'),
         f"At least one flowering day with Tmin <={p['damaging_flower_freeze_c']} C. Provisional legacy threshold, not predicted injury.", frost_source),
        ('fruit_severe_heat', 'Fruit-development severe heat exposure', 'fruit', ('fruit_severe_heat_days', 'fruit_heat_days'),
         f"At least one fruit-development day with Tmax >={p['severe_heat_threshold_c']} C. Provisional legacy threshold, not measured injury.", []),
        ('harvest_heavy_rain', 'Harvest heavy-rain exposure', 'harvest', ('harvest_heavy_rain_days', 'harvest_rain_mm'),
         f"At least one harvest day with rain >={p['heavy_rain_mm']} mm. Operational exposure threshold.", []),
        ('disease_weather', 'Disease-favourable weather', 'whole', DISEASE_METRICS,
         f"At least one day across flowering, fruit development and harvest with Tmean {p['disease_temp_min_c']}–{p['disease_temp_max_c']} C inclusive, RH >={p['disease_rh_threshold']}% and rain >={p['disease_rain_threshold_mm']} mm. All three windows must be complete. This daily proxy is provisional, not infection or BAS; UF PP366 requires wetness-duration information.",
         [{'title': 'UF/IFAS: Blueberry Advisory System', 'url': 'https://ask.ifas.ufl.edu/publication/PP366'}]),
        ('fruit_frost', 'Fruit-stage frost exposure', 'fruit', ('fruit_frost_days',),
         'At least one fruit-development day with Tmin <=0 C. Generic exposure, not a berry injury threshold.', frost_source),
        ('pollination_weather', 'Pollination-unfavourable weather', 'flower',
         ('flowering_pollination_unfavourable_days', 'flowering_cold_dry_days'),
         'No risk event or loss threshold defined. Count Tmax <15 C OR rain >=1 mm days as an operational cold/wet proxy, not bee inactivity. Cold-and-dry days are a separate supervisor hypothesis comparison. UF IN1237 supports weather sensitivity, not these numerical cutoffs.',
         [{'title': 'UF/IFAS: Pollination best practices in southern highbush blueberry in Florida',
           'url': 'https://ask.ifas.ufl.edu/publication/IN1237'}]),
        ('warm_midwinter', 'Warm midwinter exposure', 'chill', ('warm_midwinter_hours',),
         'No risk event or loss threshold defined. Count hours >21 C within the fixed midwinter window, independently of chill success. This operational proxy is not measured chill negation.', winter_source),
        ('flowering_dry_spell', 'Flowering dry-spell exposure', 'flower', ('flowering_max_dry_days',),
         'No risk event or loss threshold defined. Longest consecutive rain <1 mm run, clipped to flowering; not soil water deficit.', []),
        ('fruit_dry_spell', 'Fruit-development dry-spell exposure', 'fruit', ('fruit_max_dry_days',),
         'No risk event or loss threshold defined. Longest consecutive rain <1 mm run, clipped to fruit development; not soil water deficit.', []),
    )
    exposure_only = {'pollination_weather', 'warm_midwinter', 'flowering_dry_spell', 'fruit_dry_spell'}
    by_id = {}
    for name, label, stage, fields, event_definition, evidence in definitions:
        if name == 'disease_weather':
            values = [sum(r['metrics'][key] for key in DISEASE_METRICS) for r in rows
                      if all(r['metrics'][key] is not None for key in DISEASE_METRICS)]
        else:
            key = fields[0]
            values = valid(rows, key, None if key in ROW_METRICS else 'metrics')
        n = len(values)
        defined = name not in exposure_only
        k = (sum(v < p['chill_requirement_hours'] for v in values) if name == 'chill_shortfall'
             else sum(v >= 1 for v in values)) if defined and n else None
        frequency = k / n if k is not None else None
        if unsupported and name != 'warm_midwinter':
            eligibility = 'not_applicable'
            reason = calendar_reason + ' Calculated exposures are hypothetical only, not applicable crop risks.'
        elif not defined:
            eligibility = 'definition_pending'
            reason = f'Exposure only: no defensible event or loss threshold has been defined. Complete weather windows: {n}/{len(rows)}.'
        elif n < policy['min_valid_years']:
            eligibility = 'insufficient_data'
            reason = f"Only {n}/{len(rows)} complete winters; at least {policy['min_valid_years']} are required."
            if name == 'disease_weather':
                reason += ' Every included winter requires complete flowering, fruit and harvest disease weather.'
            elif name != 'chill_shortfall':
                reason += ' Missing crop dates or weather are excluded, never counted as zero.'
        elif frequency < policy['min_frequency']:
            eligibility = 'below_frequency'
            reason = f"Event frequency {k}/{n} is below the {policy['min_frequency']:.0%} reporting gate."
        else:
            eligibility = 'ranked'
            reason = f"Event frequency {k}/{n} meets the {policy['min_frequency']:.0%} gate with at least {policy['min_valid_years']} complete winters."
        by_id[name] = {
            'risk': name, 'label': label, 'stage': stage, 'years_with_event': k,
            'valid_years': n, 'total_years': len(rows), 'frequency': frequency,
            'ci95': wilson(k, n) if k is not None else None,
            'exposure': {key: exposures[key] for key in fields},
            'eligibility': eligibility, 'reason': reason, 'rank': None,
            'event_definition': event_definition, 'evidence': evidence,
        }
    ranked = sorted((r for r in by_id.values() if r['eligibility'] == 'ranked'),
                    key=lambda r: -r['frequency'])
    previous_frequency, rank = None, None
    for position, assessment in enumerate(ranked, 1):
        if assessment['frequency'] != previous_frequency:
            rank = position
            previous_frequency = assessment['frequency']
        assessment['rank'] = rank
    note = ('Each winter uses its own stage dates. Ranked entries alone meet both reporting gates; '
            'equal frequencies share a competition rank and keep declared order. Missing windows are not safe years. '
            'Disease weather is one family with three complete stage windows. Frequent heavy rain is not a severity score; '
            'compare counts and totals. Dry spells, pollination weather and warm winter remain descriptive exposures.')
    if unsupported:
        note += ' ' + calendar_reason + ' Crop-stage exposures and derived event frequencies are hypothetical only.'
    return {'policy': policy, 'by_id': by_id, 'ranked': ranked,
            'demoted': [r for r in by_id.values() if r['eligibility'] != 'ranked'],
            'exposures': exposures, 'note': note}


def analyse(hourly, daily, lat, profile_name, years=range(2011, 2026)):
    p = profile(profile_name)
    rows = [season(hourly, daily, lat, y, p) for y in years]
    hemi = hemisphere(lat)
    statuses = {}
    for r in rows:
        statuses[r['status']] = statuses.get(r['status'], 0) + 1
    classes = classification(rows, p)
    return {'profile': profile_name, 'assumptions': p, 'hemisphere': hemi,
            'method': METHOD,
            'years': [years[0], years[-1]], 'status_counts': statuses,
            'chill_hours': stats(valid(rows, 'chill_hours', None)),
            'freeze_hours': stats(valid(rows, 'freeze_hours', None)),
            'warm_midwinter_hours': stats(valid(rows, 'warm_midwinter_hours', None)),
            'metric_catalog': METRIC_CATALOG,
            'classification': classes,
            'calendar': calendar(rows, hemi),
            'risks': risks(rows, p, classes),
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
                     'flowering_freeze_frequency': a['risks']['by_id']['flowering_freeze']['frequency']}
    return out


def fmt(v, digits=1):
    if v is None:
        return 'unavailable'
    if isinstance(v, float):
        return f'{v:.{digits}f}'
    return str(v)


def render(report):
    def sources(items):
        return '<ul>' + ''.join(
            f'<li><a href="{html.escape(s["url"], quote=True)}">{html.escape(s["title"])}</a></li>'
            for s in items) + '</ul>' if items else ''

    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Open-field production analysis</title>',
             '<style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px;color:#222}table{border-collapse:collapse;width:100%;font-size:14px}td,th{padding:8px;border-bottom:1px solid #ccc;text-align:left;vertical-align:top}.scroll{overflow:auto}li{margin:8px 0}h3{margin-top:28px}.k{font-size:13px;color:#555}summary{cursor:pointer}</style></head><body>',
             '<h1>Open field + ground: establishment, bearing calendar and stage risks</h1>',
             f'<p class="k">Method {html.escape(report["method"])} · primary profile {html.escape(report["primary_profile"])} · winters {report["years"][0]}–{report["years"][1]} · existing NASA POWER archive, UTC · <strong>assumption-based, not validated, not cultivar advice</strong></p>',
             '<h2>Deliberate changes from the R source</h2><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in CHANGES) + '</ul>',
             '<h2>Limitations</h2><ul>' + ''.join(f'<li>{html.escape(x)}</li>' for x in LIMITATIONS) + '</ul>']
    for name, site in report['sites'].items():
        parts.append(f'<h2>{html.escape(name)}</h2>')
        planting = site['planting']
        parts.append('<h3>Regional establishment guidance</h3>')
        parts.append(f'<p>{html.escape(planting["label"])}</p>')
        if planting['window']:
            w = planting['window']
            parts.append(f'<p>{html.escape(w["start"])} to {html.escape(w["end"])}'
                         + (' across the year boundary' if w['crosses_year'] else '') + '.</p>')
        else:
            parts.append(f'<p>{html.escape(planting["reason"])}</p>')
        parts.extend(f'<p>{html.escape(planting[key])}</p>' for key in ('precision', 'basis'))
        parts.append('<ul>' + ''.join(f'<li>{html.escape(x)}</li>'
                                     for x in planting['assumptions'] + planting['limitations']) + '</ul>')
        parts.append(sources(planting['sources']))
        a = site['analysis']
        c, cal, rk = a['classification'], a['calendar'], a['risks']
        catalog = a['metric_catalog']
        parts.append(f'<p class="k">{site["latitude"]:.4f}, {site["longitude"]:.4f} · {a["hemisphere"]}ern hemisphere · valid chill winters {a["chill_hours"]["n"]}/{len(a["seasons"])} · season status: {html.escape(json.dumps(a["status_counts"]))}</p>')
        parts.append('<details><summary>Profile assumptions</summary>'
                     + table(['Constant', 'Value'], [[k, fmt(v)] for k, v in a['assumptions'].items()]) + '</details>')
        parts.append('<h3>Production-system hypothesis</h3>')
        parts.append(table(['Rule', 'From multi-year means', 'Per-year counts E / S / D', 'Two-thirds majority'],
                           [[rule, c['mean_based'][rule], ' / '.join(str(c[rule]['year_counts'][k]) for k in CLASSES),
                             f"{c[rule]['majority']} ({fmt(c[rule]['majority_share'], 2)})"] for rule in ('chill_only', 'multi_feature')]))
        parts.append('<h3>Winter weather context</h3>')
        parts.append('<p>Fixed midwinter exposure is independent of crop dates and chill success. Hours above 21 C do not measure lost chill.</p>')
        parts.append(table(['Metric', 'Valid winters', 'Mean', 'Median', 'p90', 'Interpretation'],
                           [[m['label'] + ' (' + m['unit'] + ')', rk['exposures'][m['key']]['n'],
                             fmt(rk['exposures'][m['key']].get('mean')), fmt(rk['exposures'][m['key']].get('median')),
                             fmt(rk['exposures'][m['key']].get('p90')), m['note']]
                            for m in catalog if m['key'] in ROW_METRICS]))
        parts.append('<h3>Assumption-based bearing calendar</h3>')
        applicability = rk['by_id']['chill_shortfall']
        if applicability['eligibility'] == 'not_applicable':
            parts.append('<p><strong>Hypothetical dates and crop exposures only.</strong> '
                         + html.escape(applicability['reason']) + '</p>')
        parts.append(table(['Stage', 'Valid winters', 'Median date', 'p10 date', 'p90 date', 'Median offset from season start'],
                           [[k, cal[k]['n'], cal[k].get('median_date'), cal[k].get('p10_date'),
                             cal[k].get('p90_date'), fmt(cal[k].get('median'))] for k in OFFSETS]))
        parts.append('<h3>Recurring stage risks</h3>')
        parts.append(f'<p>Reporting policy: event frequency at least {rk["policy"]["min_frequency"]:.0%} in at least {rk["policy"]["min_valid_years"]} complete winters. Exposure frequency is not loss probability.</p>')
        if rk['ranked']:
            parts.append(table(['Rank', 'Risk', 'Stage', 'Event winters / valid / total', 'Frequency', '95% CI'],
                               [[r['rank'], r['label'], r['stage'],
                                 f"{r['years_with_event']} / {r['valid_years']} / {r['total_years']}",
                                 fmt(r['frequency'], 2), '–'.join(fmt(x, 2) for x in r['ci95'])]
                                for r in rk['ranked']]))
        else:
            parts.append('<p>No risk qualifies for the recurring-risk list. This does not mean no exposure or no risk. See the assessment reasons below.</p>')
        parts.append('<h3>All checked risks and descriptive exposures</h3>')
        for assessment in rk['by_id'].values():
            parts.append(f'<details><summary>{html.escape(assessment["label"])}: {html.escape(assessment["eligibility"])}</summary>'
                         + f'<p>{html.escape(assessment["reason"])}</p><p>{html.escape(assessment["event_definition"])}</p>')
            parts.append(table(['Stage', 'Event winters', 'Valid / total winters', 'Frequency', '95% CI'],
                               [[assessment['stage'], assessment['years_with_event'],
                                 f"{assessment['valid_years']} / {assessment['total_years']}",
                                 fmt(assessment['frequency'], 2),
                                 '–'.join(fmt(x, 2) for x in assessment['ci95']) if assessment['ci95'] else None]]))
            parts.append(sources(assessment['evidence']) + '</details>')
        parts.append(f'<p class="k">{html.escape(rk["note"])}</p>')
        parts.append('<h3>Crop-stage exposure record</h3>')
        if applicability['eligibility'] == 'not_applicable':
            parts.append('<p>All crop-stage values below are descriptive results from a hypothetical calendar, not applicable crop-risk estimates.</p>')
        parts.append(table(['Metric', 'Stage', 'Valid winters', 'Mean', 'Median', 'p90', 'Interpretation'],
                           [[m['label'] + ' (' + m['unit'] + ')', m['stage'], rk['exposures'][m['key']]['n'],
                             fmt(rk['exposures'][m['key']].get('mean')), fmt(rk['exposures'][m['key']].get('median')),
                             fmt(rk['exposures'][m['key']].get('p90')), m['note']]
                            for m in catalog if m['key'] not in ROW_METRICS]))
        parts.append('<h3>Sensitivity to chill definition and requirement</h3>')
        parts.append(table(['Profile', 'Definition', 'Requirement h', 'Mean chill h', 'Majority (chill-only)', 'Majority (multi-feature)', 'Mean-based (multi)', 'Flowering start', 'Harvest start', 'Flowering-freeze frequency'],
                           [[k, v['chill_definition'], v['chill_requirement_hours'], fmt(v['chill_hours_mean']),
                             v['majority_chill_only'], v['majority_multi_feature'], v['mean_based_multi_feature'],
                             v['flowering_start_median'], v['harvest_start_median'], fmt(v['flowering_freeze_frequency'], 2)]
                            for k, v in site['sensitivity'].items()]))
        parts.append('<h3>Per-winter record</h3>')
        for row in a['seasons']:
            parts.append(f'<details><summary>Winter {row["winter_year"]}: {html.escape(row["status"])}</summary>')
            parts.append(table(['Chill date', 'Budbreak', 'Flowering', 'Fruit development', 'Harvest', 'Fixed midwinter window'],
                               [[row['chill_date'], row['budbreak_date'], ' to '.join(row['flowering'] or []) or None,
                                 ' to '.join(row['fruit'] or []) or None, ' to '.join(row['harvest'] or []) or None,
                                 ' to '.join(row['warm_midwinter_window'])]]))
            parts.append(table(['Metric', 'Stage', 'Value', 'Missingness reason'],
                               [[m['label'] + ' (' + m['unit'] + ')', m['stage'],
                                 row[m['key']] if m['key'] in ROW_METRICS else row['metrics'][m['key']],
                                 row['issues'].get(m['key'], row['issues'].get('chill', '')
                                                  if m['key'] in ('chill_hours', 'freeze_hours')
                                                  else row['issues'].get('crop_stages', '') if m['key'] not in ROW_METRICS else '')]
                                for m in catalog]))
            parts.append('</details>')
    return '\n'.join(parts) + '</body></html>'


def run(root=ROOT, names=('Waldo', 'Citra', 'Papanduva'), primary='stage_risks_v2'):
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
            'planting': planting_window(site),
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
                          'top_risk': next((r['risk'] for r in s['analysis']['risks']['ranked']), None)}
                      for n, s in report['sites'].items()}))


if __name__ == '__main__':
    run()
