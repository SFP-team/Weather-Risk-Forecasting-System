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
from evidence_report import complete, table
from planting import planting_window
from postprocess import ROOT, LandMask, extract

METHOD = 'open-field-production-v3'
PRIMARY_PROFILE = 'stage_thermal_v3'

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
# stage_thermal_v3: temperature-driven stages after budbreak (daily Tmean base 7 C, mean capped at 30 C).
# - flowering start 85 GDD and harvest 633/1242 GDD after flowering start: medians over 2011-2025 winters of the
#   GDD accumulated across the legacy +14 d and +70/+110 d offsets at Waldo, FL (`production.py thermal-reference`,
#   reports/production/thermal_reference.json). 633 agrees with one Chilean season of on-farm SHB/NHB
#   flowering-to-maturity sums, 593 (O'Neal) and 665 (Brigitta), farm range 567-740 (Maule 2012-13, manual
#   Table 4). 1242 is the Waldo translation of the legacy 40-day harvest window; published harvest durations are
#   14-51 d (Campa & Ferreira 2018) and 21-48 d (Antunes et al. 2008). Rabbiteye and many northern-highbush
#   cultivars need much longer from flowering to harvest, so these sums describe low-chill SHB only.
# - flowering end = start + 290 GDD: the F10-F90 span of the Kovaleski et al. 2015 (JASHS 140:38) whole-plant
#   bloom curves at Citra, 293 (Emerald) and 287 (Jewel) GDD from 1 January with hydrogen cyanamide. Only the span
#   is used. The paper's printed daily formula (Tmax - Tmin)/2 is a typo for the mean.
# - 100 chill hours: the supervisor's later R workflow; the low end of the 100-400 h adaptation range Lyrene 2008
#   (HortScience 43:1606) gives for Emerald, not a measured flowering minimum. Chill definition unchanged.
# - base 7 C was derived for bloom (Kirk & Isaacs 2012); its use for fruit development and the 30 C cap (no rate
#   data above 26 C) are extrapolations that only limit hot-season behaviour.
# - disease weather uses hourly wetness: UF Blueberry Advisory System anthracnose index (Wilson et al. 1990;
#   moderate >=0.15, high >=0.50) and Strawberry Advisory System Botrytis flower-infection index (Bulger et al. 1987;
#   moderate >=0.50, high >=0.70), wet hour RH >=90% (Sentelhas et al. 2008; station-validated, uncalibrated for
#   grid RH), wet period ends after 4 dry hours (FLSAS). Wet hours are capped at the fitted range (51 h anthracnose,
#   32 h Botrytis). Anthracnose is zero below the 7 C cardinal minimum and above 35 C, and uses at least 10 C in
#   the polynomial, which turns upward below about 9.3 C although Wilson found no infection at 4 C.
PROFILES['stage_thermal_v3'] = {
    **PROFILES['stage_risks_v2'],
    'chill_requirement_hours': 100,
    'stage_clock': 'thermal',
    'stage_gdd_upper_c': 30.0,
    'stage_horizon_days': 300,
    'flowering_start_gdd': 85.0,
    'flowering_end_gdd': 375.0,
    'harvest_start_gdd': 633.0,
    'harvest_end_gdd': 1242.0,
    'managed_cycle_scan': True,
    'infection_model': 'bas_sas_hourly_rh90',
    'wet_rh_pct': 90.0,
    'wet_dry_gap_hours': 4,
    'anthracnose_temp_range_c': [7.0, 35.0],
    'anthracnose_floor_c': 10.0,
    'anthracnose_max_wet_hours': 51,
    'botrytis_max_wet_hours': 32,
    'anthracnose_moderate': 0.15,
    'anthracnose_high': 0.50,
    'botrytis_moderate': 0.50,
    'botrytis_high': 0.70,
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
    'stage_thermal_v3 (primary): flowering and fruit development accumulate daily GDD after budbreak instead of fixed day offsets; durations equal the legacy offsets at Waldo on median and shorten or lengthen with temperature elsewhere. Flowering spans 290 GDD (Kovaleski et al. 2015) instead of 21 days.',
    'stage_thermal_v3 uses the 100-hour chill requirement from the supervisor\'s later R workflow; stage_risks_v2 and the legacy profiles remain as comparisons.',
    'Dynamic Model chill portions are reported beside chill hours for every winter; the requirement and classification still use chill hours.',
    'stage_thermal_v3 replaces the daily disease proxy with hourly wetness: UF Blueberry Advisory System anthracnose and Strawberry Advisory System Botrytis indices from grid temperature and dewpoint.',
    'Where the chill-triggered calendar does not apply (tropics, evergreen or unknown majority, or fewer than 12 calendar winters), a managed-cycle scan of 24 cycle-start dates gives favourable flowering and harvest months instead of no window.',
]

LIMITATIONS = [
    'Constants encode a UF-type low-chill southern highbush under open field + ground; they are provisional assumptions, not measured genotype parameters. Northern-highbush and rabbiteye regions are modelled as if planted with this type.',
    'The chill-triggered calendar is a deciduous/semi-evergreen clock. Evergreen and tropical windows come from a managed-cycle scenario scan: management is assumed able to start a cycle on each date, and flower-bud induction is not modelled.',
    'NASA POWER grid cells (0.5 x 0.625 degrees) showed warm minimum-temperature bias against stations in the 2020 pilot; chill hours and freeze counts are therefore likely undercounted. No correction is applied. Highland farms can be much cooler than their grid cell.',
    'UTC hours for chill and daily windows; the infection model assigns wet periods to local solar days (UTC plus longitude/15 hours). The original R requested local solar time; the difference affects window edges only.',
    'Frequencies come from at most 15 winters; 95% Wilson intervals are shown and are wide. Do not over-read differences between sites.',
    'Infection-risk days are weather favourability from grid wetness (RH >=90%), not canopy wetness, inoculum or disease incidence. Longest dry spell is not a soil water balance.',
    'Pollination-unfavourable days are an operational cold-or-wet proxy, not measured bee inactivity. Cold-and-dry days are a separate supervisor hypothesis comparison.',
    'Fruit frost at or below 0 C is exposure, not a cultivar-specific injury threshold. Warm hours above 21 C are not measured chill negation.',
    'The 50% frequency and 12-winter evidence gates are an explicit reporting policy, not biological loss thresholds. Dry spells, pollination weather and warm winter have no defined loss event.',
    'Stage thermal requirements are a Waldo translation checked against published spans, not a fit to observed phenology; the literature benchmark compares months with regional practice, not field observations.',
    'No cultivar ranking, no soil scoring, no tunnel or pot effects, no forecast, no independent phenology validation yet.',
]

METRIC_CATALOG = [
    {'key': key, 'stage': stage, 'label': label, 'unit': unit, 'note': note}
    for key, stage, label, unit, note in (
        ('chill_hours', 'chill', 'Chill accumulation', 'hours', 'Profile-defined chill rule and six-month window; not chill portions.'),
        ('chill_portions', 'chill', 'Dynamic Model chill portions', 'portions', 'Fishman-Erez Dynamic Model with chillR constants over the same six-month window as chill hours. Reported for comparison; the chill requirement and classification still use chill hours.'),
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
        ('flowering_infection_days', 'flower', 'Flowering infection-risk days', 'days', 'Days at moderate or higher risk: anthracnose index >=0.15 (UF Blueberry Advisory System; Wilson et al. 1990) or Botrytis index >=0.50 (Strawberry Advisory System; Bulger et al. 1987). Wet hours are RH >=90% from hourly grid temperature and dewpoint. Hourly infection-model profiles only; not a field disease forecast.'),
        ('fruit_infection_days', 'fruit', 'Fruit-development infection-risk days', 'days', 'Days with anthracnose index >=0.15 (BAS moderate risk) from hourly wetness duration and wet-period temperature. Hourly infection-model profiles only.'),
        ('harvest_infection_days', 'harvest', 'Harvest infection-risk days', 'days', 'Days with anthracnose index >=0.15 (BAS moderate risk) from hourly wetness duration and wet-period temperature. Hourly infection-model profiles only.'),
        ('crop_high_infection_days', 'whole', 'High infection-risk days', 'days', 'Days from flowering start to harvest end with anthracnose index >=0.50, or during flowering Botrytis index >=0.70 (BAS/SAS high-risk classes). Hourly infection-model profiles only.'),
    )
]
ROW_METRICS = ('chill_hours', 'chill_portions', 'freeze_hours', 'warm_midwinter_hours')
STAGE_METRICS = tuple(m['key'] for m in METRIC_CATALOG if m['key'] not in ROW_METRICS)
OFFSETS = ('chill', 'budbreak', 'flowering_start', 'flowering_end', 'harvest_start', 'harvest_end')
DISEASE_METRICS = ('flowering_disease_days', 'fruit_disease_days', 'harvest_disease_days')
INFECTION_METRICS = ('crop_high_infection_days', 'flowering_infection_days', 'fruit_infection_days', 'harvest_infection_days')
CLASSES = ('Evergreen', 'Semi-evergreen', 'Deciduous')
THERMAL_STAGES = ('flowering_start_gdd', 'flowering_end_gdd', 'harvest_start_gdd', 'harvest_end_gdd')


def profile(name):
    p = PROFILES[name]
    if p['chill_requirement_hours'] <= 0:
        raise ValueError('anchor_required: a zero-chill scenario needs an explicit forcing anchor')
    if p['chill_definition'] not in ('below_7_2', 'bounded_0_7_2'):
        raise ValueError('Unknown chill definition')
    clock = p.get('stage_clock', 'days')
    if clock not in ('days', 'thermal'):
        raise ValueError('Unknown stage clock')
    if clock == 'thermal':
        req = [p.get(k) for k in THERMAL_STAGES]
        if not all(isinstance(v, (int, float)) and v > 0 for v in req) or req[0] >= req[1] or req[2] >= req[3]:
            raise ValueError('Thermal stage clock needs positive, ordered stage requirements')
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


E0, E1, A0, A1, SLP, TETMLT = 4153.5, 12888.8, 139500.0, 2.567e18, 1.6, 277.0


def chill_portions(temp_c):
    """Cumulative Dynamic Model chill portions for consecutive hourly temperatures.

    Fishman, Erez & Couvillon (1987) with the chillR constants and recursion (Kelvin = C + 273).
    """
    tk = np.asarray(temp_c, dtype=float) + 273.0
    sr = np.exp(SLP * TETMLT * (tk - TETMLT) / tk)
    xi = sr / (1 + sr)
    xs = (A0 / A1 * np.exp((E1 - E0) / tk)).tolist()
    decay = np.exp(-(A1 * np.exp(-E1 / tk))).tolist()
    share = xi.tolist()
    inter = [0.0] * len(xs)
    for i in range(1, len(xs)):
        prev = inter[i - 1]
        s = prev if prev < 1 else prev - prev * share[i - 1]
        inter[i] = xs[i] - (xs[i] - s) * decay[i]
    inter = np.asarray(inter)
    return np.cumsum(np.where(inter >= 1, inter * xi, 0.0))


def infection_risk(temperature, dewpoint, lon, p):
    """Daily maximum anthracnose and Botrytis infection indices from hourly air temperature and dewpoint (UTC index).

    UF Blueberry Advisory System anthracnose model (Wilson, Madden & Ellis 1990) and Strawberry Advisory System
    Botrytis model (Bulger, Ellis & Madden 1987): inverse-logit indices of wet-period duration W (h) and mean wet-hour
    temperature T (C). A wet hour has RH >= p['wet_rh_pct'] from temperature and dewpoint (Magnus; Sentelhas et al.
    2008); a period ends after p['wet_dry_gap_hours'] consecutive dry hours (FLSAS). W is capped at each model's fitted
    wetness range. Anthracnose is zero outside the p['anthracnose_temp_range_c'] cardinal range and uses
    max(T, p['anthracnose_floor_c']) because the fitted polynomial turns upward below about 9.3 C. A period counts on
    the local day (UTC + round(lon / 15) h) of its last wet hour; local days with fewer than 24 valid hours are NaN.
    """
    t = temperature.astype(float)
    tv, dv = t.to_numpy(), dewpoint.reindex(t.index).astype(float).to_numpy()
    valid = np.isfinite(tv) & np.isfinite(dv)
    with np.errstate(invalid='ignore'):
        rh = 100.0 * np.exp(17.625 * dv / (243.04 + dv) - 17.625 * tv / (243.04 + tv))
    day = (t.index + pd.Timedelta(hours=round(lon / 15))).normalize()
    counts = pd.Series(valid, index=day).groupby(level=0).sum()
    out = pd.DataFrame(0.0, index=counts.index, columns=['anthracnose', 'botrytis'])
    wet = np.flatnonzero(valid & (rh >= p['wet_rh_pct']))
    if wet.size:
        period = np.concatenate(([0], np.cumsum(np.diff(wet) > p['wet_dry_gap_hours'])))
        w = np.bincount(period).astype(float)
        temp = np.bincount(period, weights=tv[wet]) / w
        last = wet[np.concatenate((np.flatnonzero(np.diff(period)), [len(period) - 1]))]
        wa, ta = np.minimum(w, p['anthracnose_max_wet_hours']), np.maximum(temp, p['anthracnose_floor_c'])
        wb = np.minimum(w, p['botrytis_max_wet_hours'])
        fa = -3.7 + 0.33 * wa - 0.069 * wa * ta + 0.005 * wa * ta ** 2 - 9.3e-5 * wa * ta ** 3
        fb = -4.268 - 0.0901 * wb + 0.0294 * wb * temp - 2.35e-5 * wb * temp ** 3
        low, high = p['anthracnose_temp_range_c']
        with np.errstate(over='ignore'):
            anthracnose = np.where((temp >= low) & (temp <= high), 1 / (1 + np.exp(-fa)), 0.0)
            botrytis = 1 / (1 + np.exp(-fb))
        risk = pd.DataFrame({'anthracnose': anthracnose, 'botrytis': botrytis},
                            index=day[last]).groupby(level=0).max()
        out.loc[risk.index] = risk.to_numpy()
    out[(counts < 24).to_numpy()] = np.nan
    return out


def longest_run(flags):
    flags = np.asarray(flags, dtype=bool)
    if not flags.any():
        return 0
    edges = np.diff(np.concatenate(([0], flags.astype(np.int8), [0])))
    return int((np.flatnonzero(edges == -1) - np.flatnonzero(edges == 1)).max())


class Days:
    """Daily inputs on one contiguous calendar. Windows are inclusive and returned only when complete."""

    def __init__(self, daily, infection=None):
        if daily.index.has_duplicates:
            raise ValueError('Duplicate daily timestamps')
        dates = pd.date_range(daily.index.min(), daily.index.max(), freq='D')
        self.origin, self.last = dates[0], dates[-1]
        column = lambda s: s.astype(float).reindex(dates).to_numpy()
        self.values = {'tmean': column(daily.tmean_c), 'tmin': column(daily.tmin_c), 'tmax': column(daily.tmax_c),
                       'rain': column(clean_rain(daily)), 'rh': column(clean_rh(daily))}
        if 'shortwave_mj_m2_day' in daily:
            self.values['sun'] = column(daily.shortwave_mj_m2_day)
        if infection is not None:
            self.values['anthracnose'] = column(infection.anthracnose)
            self.values['botrytis'] = column(infection.botrytis)

    def get(self, name, first, last):
        values = self.values.get(name)
        if values is None or last < first:
            return None
        i, j = (first - self.origin).days, (last - self.origin).days
        if i < 0 or j >= len(values):
            return None
        out = values[i:j + 1]
        return out if np.isfinite(out).all() else None


def reach(days, first, last, requirement, base, upper=None):
    """First day in [first, last] on which cumulative daily GDD reaches `requirement`.

    Daily GDD = max(min(Tmean, upper) - base, 0); `upper=None` applies no cutoff.
    Returns (day, None) or (None, (kind, day)): 'missing' names the first gap (a gap past the archive
    end is the first day without data), 'horizon' means the requirement was not reached by `last`.
    """
    tmean = days.values['tmean']
    i, j = (first - days.origin).days, (last - days.origin).days
    if i < 0:
        return None, ('missing', first)
    segment = tmean[i:min(j, len(tmean) - 1) + 1]
    heat = np.maximum((segment if upper is None else np.minimum(segment, upper)) - base, 0.0)
    hit = np.flatnonzero(np.cumsum(heat) >= requirement)  # a gap turns every later sum into NaN
    if hit.size:
        return first + pd.Timedelta(days=int(hit[0])), None
    gap = np.flatnonzero(~np.isfinite(heat))
    if gap.size:
        return None, ('missing', first + pd.Timedelta(days=int(gap[0])))
    if j >= len(tmean):
        return None, ('missing', days.last + pd.Timedelta(days=1))
    return None, ('horizon', last)


def stage_dates(days, bud, p):
    """Flowering and harvest windows from budbreak: fixed day offsets or thermal time (`stage_clock`)."""
    d = pd.Timedelta
    if p.get('stage_clock', 'days') == 'days':
        fa, fb = p['flowering_after_budbreak_days']
        ha, hb = p['harvest_after_flowering_start_days']
        flowering = (bud + d(days=fa), bud + d(days=fb))
        return (flowering, (flowering[0] + d(days=ha), flowering[0] + d(days=hb))), None
    base, upper, limit = p['gdd_base_c'], p['stage_gdd_upper_c'], d(days=p['stage_horizon_days'])
    out = []
    for anchor, key in (('bud', 'flowering_start_gdd'), ('bud', 'flowering_end_gdd'),
                        ('flowering', 'harvest_start_gdd'), ('flowering', 'harvest_end_gdd')):
        origin = bud if anchor == 'bud' else out[0]
        day, why = reach(days, origin + d(days=1), origin + limit, p[key], base, upper)
        if day is None:
            return None, why
        out.append(day)
    return ((out[0], out[1]), (out[2], out[3])), None


def stage_metrics(days, p, flowering, fruit, harvest, production_start):
    """Stage exposures from complete daily windows; an incomplete window yields None, never zero."""
    m = {k: None for k in STAGE_METRICS}
    get = days.get

    def disease(a, b):
        t, h, r = get('tmean', a, b), get('rh', a, b), get('rain', a, b)
        if t is None or h is None or r is None:
            return None
        return int(((t >= p['disease_temp_min_c']) & (t <= p['disease_temp_max_c'])
                    & (h >= p['disease_rh_threshold']) & (r >= p['disease_rain_threshold_mm'])).sum())

    def vpd(a, b):
        t, h = get('tmean', a, b), get('rh', a, b)
        return None if t is None or h is None else float(vpd_kpa(t, h).mean())

    def dry(a, b):
        r = get('rain', a, b)
        return None if r is None else longest_run(r < 1)

    cold = get('tmin', *flowering)
    if cold is not None:
        m['flower_tmin_min_c'] = float(cold.min())
        m['flower_freeze_days'] = int((cold <= p['damaging_flower_freeze_c']).sum())
    wet = get('rain', *flowering)
    if wet is not None:
        m['flowering_rain_mm'] = float(wet.sum())
        m['flowering_heavy_rain_days'] = int((wet >= p['heavy_rain_mm']).sum())
        m['flowering_max_dry_days'] = longest_run(wet < 1)
    flower_max = get('tmax', *flowering)
    if wet is not None and flower_max is not None:
        cold_day = flower_max < p.get('pollination_cold_tmax_c', 15.0)
        wet_day = wet >= p.get('pollination_wet_mm', 1.0)
        m['flowering_pollination_unfavourable_days'] = int((cold_day | wet_day).sum())
        m['flowering_cold_dry_days'] = int((cold_day & ~wet_day).sum())
    m['flowering_disease_days'] = disease(*flowering)
    m['flowering_vpd_mean_kpa'] = vpd(*flowering)
    hot = get('tmax', *fruit)
    if hot is not None:
        m['fruit_heat_days'] = int((hot >= p['heat_threshold_c']).sum())
        m['fruit_severe_heat_days'] = int((hot >= p['severe_heat_threshold_c']).sum())
    m['fruit_vpd_mean_kpa'] = vpd(*fruit)
    m['fruit_disease_days'] = disease(*fruit)
    fruit_cold = get('tmin', *fruit)
    if fruit_cold is not None:
        m['fruit_frost_days'] = int((fruit_cold <= 0.0).sum())
    m['fruit_max_dry_days'] = dry(*fruit)
    wet = get('rain', *harvest)
    if wet is not None:
        m['harvest_rain_mm'] = float(wet.sum())
        m['harvest_heavy_rain_days'] = int((wet >= p['heavy_rain_mm']).sum())
    m['harvest_disease_days'] = disease(*harvest)
    m['harvest_vpd_mean_kpa'] = vpd(*harvest)
    m['production_max_dry_days'] = dry(production_start, harvest[1])
    sun = get('sun', production_start, harvest[1])
    m['production_radiation_mean_mj'] = None if sun is None else float(sun.mean())
    heat = get('tmean', production_start, harvest[1])
    m['production_gdd'] = None if heat is None else float(np.maximum(heat - p['gdd_base_c'], 0).sum())
    if p.get('infection_model') and 'anthracnose' in days.values:
        anth, bot = get('anthracnose', *flowering), get('botrytis', *flowering)
        if anth is not None and bot is not None:
            m['flowering_infection_days'] = int(((anth >= p['anthracnose_moderate']) | (bot >= p['botrytis_moderate'])).sum())
        for key, window in (('fruit_infection_days', fruit), ('harvest_infection_days', harvest)):
            anth = get('anthracnose', *window)
            m[key] = None if anth is None else int((anth >= p['anthracnose_moderate']).sum())
        anth = get('anthracnose', flowering[0], harvest[1])
        if anth is not None and bot is not None:
            high = anth >= p['anthracnose_high']
            high[:len(bot)] |= bot >= p['botrytis_high']
            m['crop_high_infection_days'] = int(high.sum())
    return m


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
        'chill_hours': None, 'chill_portions': None, 'freeze_hours': None, 'freeze_events': None,
        'warm_midwinter_hours': None,
        'warm_midwinter_window': [str(day.date()) for day in midwinter_window(year, hemi)],
        'winter_month_tmin_lowest_c': None, 'winter_month_tmean_lowest_c': None, 'freeze_risk_months': None,
        'chill_date': None, 'budbreak_date': None, 'flowering': None, 'fruit': None, 'harvest': None,
        'offset_days': {k: None for k in OFFSETS},
        'metrics': {k: None for k in STAGE_METRICS},
        'issues': {},
    }


ISSUE_REASONS = {
    'tmin': 'missing/nonfinite daily minimum temperature in window',
    'tmax': 'missing/nonfinite daily maximum temperature in window',
    'rain': 'missing/nonfinite/negative/suspect rainfall in window',
    'rh_t': 'missing/nonfinite/out-of-range humidity or temperature in window',
    'disease': 'missing/nonfinite temperature, invalid humidity or missing/negative/suspect rainfall in window',
    'pollination': 'missing/nonfinite maximum temperature or missing/negative/suspect rainfall in flowering window',
    'sun': 'missing/nonfinite radiation in window',
    'gdd': 'missing/nonfinite daily mean temperature in window',
    'infection': 'missing hourly temperature or dewpoint for the infection model in window'}
METRIC_NEEDS = {
    'flower_tmin_min_c': 'tmin', 'flower_freeze_days': 'tmin', 'flowering_rain_mm': 'rain',
    'flowering_heavy_rain_days': 'rain', 'flowering_disease_days': 'disease', 'flowering_vpd_mean_kpa': 'rh_t',
    'fruit_heat_days': 'tmax', 'fruit_severe_heat_days': 'tmax', 'fruit_vpd_mean_kpa': 'rh_t',
    'flowering_pollination_unfavourable_days': 'pollination', 'flowering_cold_dry_days': 'pollination',
    'flowering_max_dry_days': 'rain', 'fruit_max_dry_days': 'rain',
    'fruit_disease_days': 'disease', 'fruit_frost_days': 'tmin',
    'harvest_rain_mm': 'rain', 'harvest_heavy_rain_days': 'rain', 'harvest_disease_days': 'disease',
    'harvest_vpd_mean_kpa': 'rh_t', 'production_max_dry_days': 'rain',
    'production_radiation_mean_mj': 'sun', 'production_gdd': 'gdd',
    **{key: 'infection' for key in INFECTION_METRICS}}


def season(hourly, daily, lat, year, p, days=None):
    """One winter year: fixed-schema row. `hourly` is a Series of hourly T (C); `daily` a DataFrame indexed by date."""
    hemi = hemisphere(lat)
    start, end = window(year, hemi)
    row = empty_row(year, hemi, start, end)
    days = Days(daily) if days is None else days
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
    hours = winter.to_numpy()
    flags = chill_flags(hours, p['chill_definition'])
    freezing = hours <= p['frost_threshold_c']
    row.update(chill_hours=int(flags.sum()), chill_portions=round(float(chill_portions(hours)[-1]), 2),
               freeze_hours=int(freezing.sum()), freeze_events=runs(freezing))
    reached = np.cumsum(flags) >= p['chill_requirement_hours']
    if not reached.any():
        row['status'] = 'chill_not_met'
        row['issues']['crop_stages'] = 'No crop windows: the chill requirement was not reached.'
        return row
    chill_date = winter.index[int(np.argmax(reached))].floor('D')
    row['chill_date'] = str(chill_date.date())

    d = pd.Timedelta
    bud, why = reach(days, chill_date, start + d(days=p['horizon_days']), p['gdd_to_budbreak'], p['gdd_base_c'])
    if bud is None:
        if why[0] == 'horizon':
            row['status'] = 'gdd_not_met_within_horizon'
            row['issues']['crop_stages'] = 'No crop windows: forcing did not reach budbreak within the model horizon.'
        else:
            row['status'] = 'incomplete_gdd'
            row['issues']['budbreak'] = f'missing daily mean temperature at {why[1].date()}'
            row['issues']['crop_stages'] = 'No crop windows: forcing temperature is incomplete.'
        return row
    row['budbreak_date'] = str(bud.date())
    stages, why = stage_dates(days, bud, p)
    if stages is None:
        if why[0] == 'horizon':
            row['status'] = 'stage_gdd_not_met'
            row['issues']['crop_stages'] = 'No crop windows: a stage did not reach its thermal requirement within the stage horizon.'
        else:
            row['status'] = 'incomplete_stage_dates'
            row['issues']['crop_stages'] = f'No crop windows: daily mean temperature is unavailable at {why[1].date()}.'
        return row
    flowering, harvest = stages
    fruit = (flowering[1] + d(days=1), harvest[0] - d(days=1))
    row.update(flowering=[str(x.date()) for x in flowering],
               fruit=[str(x.date()) for x in fruit],
               harvest=[str(x.date()) for x in harvest])
    dates = dict(chill=chill_date, budbreak=bud, flowering_start=flowering[0], flowering_end=flowering[1],
                 harvest_start=harvest[0], harvest_end=harvest[1])
    row['offset_days'] = {k: int((v - start).days) for k, v in dates.items()}
    production_start = bud if p.get('require_applicable_calendar') else start
    row['metrics'] = stage_metrics(days, p, flowering, fruit, harvest, production_start)
    for key, value in row['metrics'].items():
        if value is None and (key not in INFECTION_METRICS or p.get('infection_model')):
            row['issues'][key] = ISSUE_REASONS[METRIC_NEEDS[key]]
    row['status'] = 'complete' if not row['issues'] else 'incomplete_metrics'
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


def event_values(rows, name, key, p):
    """Per-cycle values of one event family. The legacy disease proxy sums three complete stage counts;
    the hourly infection model counts high-risk days from flowering start to harvest end."""
    if name == 'disease_weather' and not p.get('infection_model'):
        return [sum(r['metrics'][k] for k in DISEASE_METRICS) for r in rows
                if all(r['metrics'][k] is not None for k in DISEASE_METRICS)]
    if name == 'disease_weather':
        key = 'crop_high_infection_days'
    return valid(rows, key, None if key in ROW_METRICS else 'metrics')


def risks(rows, p, classes=None, clock=None):
    """Assess each event family using complete per-winter windows, then apply reporting gates.

    `clock` (managed-cycle profiles) states whether the chill-triggered calendar applies; legacy profiles use the
    evergreen/unknown classification rule only.
    """
    policy = {'min_frequency': p.get('risk_min_frequency', 0.5),
              'min_valid_years': p.get('risk_min_valid_years', 12)}
    classes = classification(rows, p) if classes is None else classes
    majority = classes['multi_feature']['majority']
    if clock is None:
        unsupported = p.get('require_applicable_calendar', False) and majority in (None, 'Evergreen')
        calendar_reason = (
            'The evergreen-majority system needs a management-defined crop calendar; the chill-triggered calendar and chill requirement do not apply.'
            if majority == 'Evergreen' else
            'The production-system classification is unknown; applicability of the chill-triggered calendar and chill requirement is not established.'
        )
    else:
        unsupported = not clock['applicable']
        calendar_reason = ' '.join(clock['reasons'])
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
        ('disease_weather', 'Disease-favourable weather', 'whole', INFECTION_METRICS,
         f"At least one day from flowering start to harvest end at high infection risk: anthracnose index >={p['anthracnose_high']} (UF Blueberry Advisory System; Wilson et al. 1990) or, during flowering, Botrytis index >={p['botrytis_high']} (Strawberry Advisory System; Bulger et al. 1987). Wet hours are RH >={p['wet_rh_pct']}% from hourly grid temperature and dewpoint; a wet period ends after {p['wet_dry_gap_hours']} dry hours. Grid wetness is not canopy wetness, so this is weather favourability, not a disease forecast.",
         [{'title': 'UF/IFAS PP366: Blueberry Advisory System', 'url': 'https://ask.ifas.ufl.edu/publication/PP366'},
          {'title': 'NC State: anthracnose and Botrytis strawberry fruit infection risk models',
           'url': 'https://ipm.ces.ncsu.edu/development-of-anthacnose-and-botrytis-strawberry-fruit-infection-risk-models/'},
          {'title': 'Sentelhas et al. 2008: leaf wetness from relative humidity',
           'url': 'http://www.leb.esalq.usp.br/agmfacil/artigos/artigos_sentelhas_2008/2008-A&FMeteor_148(2-4)_392-400_LWD-RH.pdf'}])
        if p.get('infection_model') else
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
        values = event_values(rows, name, fields[0], p)
        n = len(values)
        defined = name not in exposure_only
        k = (sum(v < p['chill_requirement_hours'] for v in values) if name == 'chill_shortfall'
             else sum(v >= 1 for v in values)) if defined and n else None
        frequency = k / n if k is not None else None
        if unsupported and name != 'warm_midwinter' and not (
                name == 'chill_shortfall' and clock and clock['chill_requirement_applies']):
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


CYCLE_STARTS = tuple(f'{month:02d}-{day:02d}' for month in range(1, 13) for day in (1, 15))
CYCLE_EVENTS = (('flowering_freeze', 'flower_freeze_days'), ('fruit_frost', 'fruit_frost_days'),
                ('fruit_severe_heat', 'fruit_severe_heat_days'), ('harvest_heavy_rain', 'harvest_heavy_rain_days'),
                ('disease_weather', None))
# Scan dimensions. Freezes are crop-loss events, so they count cycles with any event; recurring weather is
# counted as the share of stage days affected, so faster (shorter) cycles do not look safer by construction.
SCAN_MEASURES = (
    ('flowering_freeze', 'share of cycles with a flowering day at or below the damaging freeze threshold, or stalled by cold'),
    ('fruit_frost', 'share of cycles with a fruit-development day with Tmin at or below 0 C, or stalled by cold'),
    ('fruit_heat', 'share of fruit-development days with Tmax at or above the heat threshold'),
    ('harvest_heavy_rain', 'share of harvest days with heavy rain'),
    ('disease_weather', 'share of flowering-to-harvest days at moderate or higher infection risk (hourly model) or meeting the daily disease rule (legacy profiles)'))


def month_day(start, offset):
    """Month-day reached `offset` days after a MM-DD start, on a non-leap reference year."""
    return (pd.Timestamp(f'2001-{start}') + pd.Timedelta(days=round(offset))).strftime('%m-%d')


def months_between(first, last):
    """Calendar months touched by the inclusive MM-DD span, wrapping across the year end."""
    a, b = pd.Timestamp(f'2001-{first}'), pd.Timestamp(f'2001-{last}')
    if b < a:
        b += pd.DateOffset(years=1)
    return sorted({day.month for day in pd.date_range(a, b)})


# Longest published flowering season (66 d, Campa & Ferreira 2018, Asturias) and a flowering-to-first-harvest
# interval beyond published maxima (116 d cool-spring rabbiteye, Pelotas; ~120 d Peru): a scanned cycle exceeding
# either has stalled through a cold season and is not a production cycle.
SCAN_MAX_FLOWERING_DAYS = 66
SCAN_MAX_FRUIT_DAYS = 150


def select_favourable(candidates, tolerance):
    """Strict Pareto front on SCAN_MEASURES (acyclic, never empty when candidates exist), plus near-ties: candidates
    within `tolerance` of a front member on every measure. Lower is better on every measure."""
    keys = [name for name, _ in SCAN_MEASURES]
    vector = lambda s: [s['measures'][k] for k in keys]
    front = [s for s in candidates
             if not any(all(x <= y for x, y in zip(vector(o), vector(s))) and vector(o) != vector(s) for o in candidates)]
    return [s for s in candidates
            if s in front or any(all(abs(s['measures'][k] - f['measures'][k]) <= tolerance[k] for k in keys) for f in front)]


def managed_cycles(days, p, years):
    """Scenario scan: start the fruiting cycle (budbreak) on fixed dates and follow the profile stage clock.

    Assumes management (pruning, defoliation, dormancy breaking) can start a cycle on each date; flower-bud
    induction, chill and market timing are not modelled. Stalled cycles count as failed cycles for flowering freeze
    and fruit frost. Starts whose flowering freeze or fruit frost recurs in at least the policy share of cycles are not
    favourable; the rest are selected by select_favourable() on SCAN_MEASURES. No cross-family weights.
    """
    d = pd.Timedelta
    policy = {'min_frequency': p.get('risk_min_frequency', 0.5), 'min_valid_years': p.get('risk_min_valid_years', 12)}
    disease_keys = INFECTION_METRICS[1:] if p.get('infection_model') else DISEASE_METRICS
    starts, lengths = [], {'fruit_heat': [], 'harvest_heavy_rain': [], 'disease_weather': []}
    for start in CYCLE_STARTS:
        rows, offsets, stalled = [], {key: [] for key in OFFSETS[2:]}, 0
        shares = {'fruit_heat': [], 'harvest_heavy_rain': [], 'disease_weather': []}
        for year in years:
            bud = pd.Timestamp(f'{year}-{start}')
            stages, _ = stage_dates(days, bud, p)
            if stages is not None and ((stages[0][1] - stages[0][0]).days > SCAN_MAX_FLOWERING_DAYS
                                       or (stages[1][0] - stages[0][0]).days > SCAN_MAX_FRUIT_DAYS):
                stages, stalled = None, stalled + 1
            if stages is None:
                rows.append({'metrics': {k: None for k in STAGE_METRICS}})
                continue
            flowering, harvest = stages
            fruit = (flowering[1] + d(days=1), harvest[0] - d(days=1))
            m = stage_metrics(days, p, flowering, fruit, harvest, bud)
            rows.append({'metrics': m})
            for key, day in zip(OFFSETS[2:], (*flowering, *harvest)):
                offsets[key].append((day - bud).days)
            length = {'fruit_heat': (harvest[0] - flowering[1]).days - 1,
                      'harvest_heavy_rain': (harvest[1] - harvest[0]).days + 1,
                      'disease_weather': (harvest[1] - flowering[0]).days + 1}
            counts = {'fruit_heat': m['fruit_heat_days'], 'harvest_heavy_rain': m['harvest_heavy_rain_days'],
                      'disease_weather': None if any(m[k] is None for k in disease_keys) else sum(m[k] for k in disease_keys)}
            for key, count in counts.items():
                if count is not None and length[key] > 0:
                    shares[key].append(count / length[key])
                    lengths[key].append(length[key])
        events = {}
        for name, key in CYCLE_EVENTS:
            values = event_values(rows, name, key, p)
            k = int(sum(v >= 1 for v in values))
            # A stalled cycle ran into prolonged cold: count it as a failed cycle for the crop-loss families.
            extra = stalled if name in ('flowering_freeze', 'fruit_frost') else 0
            events[name] = {'years_with_event': k + extra, 'valid_years': len(values) + extra,
                            'frequency': (k + extra) / (len(values) + extra) if values or extra else None}
        # Stalled cycles are evidence for the crop-loss families, so a start that stalls most years is reported as
        # recurring crop loss rather than silently dropped; the recurring-weather shares need complete cycles.
        evidence = {name: e['valid_years'] >= policy['min_valid_years'] for name, e in events.items()}
        rankable = all(evidence.values()) and all(len(v) >= policy['min_valid_years'] for v in shares.values())
        recurring = [name for name, e in events.items() if evidence[name] and e['frequency'] >= policy['min_frequency']]
        measures = {'flowering_freeze': events['flowering_freeze']['frequency'],
                    'fruit_frost': events['fruit_frost']['frequency'],
                    **{k: float(np.mean(v)) if v else None for k, v in shares.items()}}
        dates = {key: month_day(start, np.median(v)) if v else None for key, v in offsets.items()}
        crop_loss = [name for name in ('flowering_freeze', 'fruit_frost') if name in recurring]
        starts.append({
            'budbreak': start, 'cycles': len(offsets['harvest_end']), 'stalled_cycles': stalled, 'dates': dates,
            'flowering_months': months_between(dates['flowering_start'], dates['flowering_end']) if offsets['flowering_end'] else [],
            'harvest_months': months_between(dates['harvest_start'], dates['harvest_end']) if offsets['harvest_end'] else [],
            'events': events, 'measures': measures, 'rankable': rankable, 'recurring_crop_loss': crop_loss,
            'recurring': recurring})
    candidates = [s for s in starts if s['rankable'] and not s['recurring_crop_loss']]
    cycles = min((min(e['valid_years'] for e in s['events'].values()) for s in candidates), default=1)
    tolerance = {'flowering_freeze': 1 / cycles, 'fruit_frost': 1 / cycles,
                 **{k: 1 / float(np.median(v)) if v else 0.0 for k, v in lengths.items()}}
    chosen = select_favourable(candidates, tolerance)
    favourable = {
        'budbreak': [s['budbreak'] for s in chosen],
        'recurring': sorted({name for s in chosen for name in s['recurring']}),
        'flowering_months': sorted({m for s in chosen for m in s['flowering_months']}),
        'harvest_months': sorted({m for s in chosen for m in s['harvest_months']}),
        'unconstrained': bool(chosen) and len(chosen) == len(starts)}
    return {'method': 'managed-cycle-scan-v3', 'policy': policy, 'starts': starts, 'favourable': favourable,
            'measures': [{'key': k, 'definition': text, 'tolerance': tolerance[k]} for k, text in SCAN_MEASURES],
            'rule': ('Each start date is a management scenario for budbreak of the fruiting cycle; stages follow the profile '
                     f'stage clock. Cycles whose flowering lasts over {SCAN_MAX_FLOWERING_DAYS} days or whose first harvest '
                     f'comes over {SCAN_MAX_FRUIT_DAYS} days after flowering starts have stalled; they count as failed cycles '
                     f"for flowering freeze and fruit frost. Starts need at least {policy['min_valid_years']} complete cycles. "
                     f"A start whose flowering freeze or fruit frost recurs in at least {policy['min_frequency']:.0%} of cycles "
                     'is not favourable. Favourable starts are the Pareto front of the rest (no other start is at least as good '
                     'on every measure and better on one) plus starts within one affected cycle (freezes) or one affected day '
                     'per cycle (fruit heat, harvest heavy rain, disease weather) of a front start on every measure.'),
            'limitations': [
                'Management feasibility is assumed: pruning, defoliation, dormancy-breaking agents or cover must be able to start the cycle on the chosen date.',
                'Flower-bud induction (short days, shoot maturity), chill and cultivar differences are not modelled; a favourable weather window is not proof that plants will flower then.',
                'Market price, labour and water supply are not considered. Favourable means fewer adverse-weather days, not higher yield or profit.',
                'Weather is the uncorrected grid archive; exposure frequencies are not loss probabilities.']}


def chill_clock(rows, classes, lat, p):
    """Whether the hemisphere-anchored chill-triggered calendar applies at this location (managed-cycle profiles).

    `chill_requirement_applies` is separate: sparse calendars caused by unmet chill are themselves the chill
    shortfall evidence, so only tropical or evergreen/unknown sites exempt the chill requirement.
    """
    reasons = []
    majority = classes['multi_feature']['majority']
    calendars = sum(r['harvest'] is not None for r in rows)
    tropical = abs(lat) < 23.44
    if tropical:
        reasons.append('Between the tropics the hemisphere-fixed winter window does not define a dormancy season; production cycles are managed.')
    if majority == 'Evergreen':
        reasons.append('The evergreen-majority system needs a management-defined crop calendar; the chill-triggered calendar and chill requirement do not apply.')
    elif majority is None:
        reasons.append('The production-system classification is unknown; applicability of the chill-triggered calendar is not established.')
    if calendars < p.get('risk_min_valid_years', 12):
        reasons.append(f'Only {calendars}/{len(rows)} winters produce a chill-triggered calendar.')
    return {'applicable': not reasons, 'reasons': reasons,
            'chill_requirement_applies': not tropical and majority not in (None, 'Evergreen')}


def analyse(hourly, daily, lat, profile_name, years=range(2011, 2026), dewpoint=None, lon=None):
    """`hourly`: hourly air temperature (C, UTC). `dewpoint` and `lon` feed the hourly infection model of
    infection-model profiles; without them those metrics are unavailable, never zero."""
    p = profile(profile_name)
    use = p.get('infection_model') and dewpoint is not None and lon is not None
    infection = infection_risk(hourly, dewpoint, lon, p) if use else None
    days = Days(daily, infection)
    rows = [season(hourly, daily, lat, y, p, days) for y in years]
    hemi = hemisphere(lat)
    statuses = {}
    for r in rows:
        statuses[r['status']] = statuses.get(r['status'], 0) + 1
    classes = classification(rows, p)
    clock = chill_clock(rows, classes, lat, p) if p.get('managed_cycle_scan') else None
    result = {'profile': profile_name, 'assumptions': p, 'hemisphere': hemi,
              'method': METHOD,
              'years': [years[0], years[-1]], 'status_counts': statuses,
              'chill_hours': stats(valid(rows, 'chill_hours', None)),
              'chill_portions': stats(valid(rows, 'chill_portions', None)),
              'freeze_hours': stats(valid(rows, 'freeze_hours', None)),
              'warm_midwinter_hours': stats(valid(rows, 'warm_midwinter_hours', None)),
              'metric_catalog': METRIC_CATALOG,
              'classification': classes,
              'calendar': calendar(rows, hemi),
              'risks': risks(rows, p, classes, clock),
              'seasons': rows}
    if clock is not None:
        result['chill_clock'] = clock
        result['managed_cycle'] = {**managed_cycles(days, p, years),
                                   'role': 'comparison' if clock['applicable'] else 'primary'}
    return result


def thermal_reference(hourly, daily, lat, base, upper=None, years=range(2011, 2026), reference='legacy_paul_v1'):
    """GDD accumulated over each fixed legacy stage offset, per winter with a budbreak date, at one site.

    Translates the legacy day offsets into thermal requirements at a reference location. The result reproduces
    the legacy durations there on median; it is not an independent phenology fit.
    """
    p = profile(reference)
    days = Days(daily)
    d = pd.Timedelta
    fa, fb = p['flowering_after_budbreak_days']
    ha, hb = p['harvest_after_flowering_start_days']
    spans = {'flowering_start_gdd': (0, fa), 'flowering_end_gdd': (0, fb),
             'harvest_start_gdd': (fa, ha), 'harvest_end_gdd': (fa, hb)}
    values = {key: [] for key in spans}
    for year in years:
        row = season(hourly, daily, lat, year, p, days)
        if row['budbreak_date'] is None:
            continue
        bud = pd.Timestamp(row['budbreak_date'])
        for key, (lead, length) in spans.items():
            origin = bud + d(days=lead)
            t = days.get('tmean', origin + d(days=1), origin + d(days=length))
            if t is not None:
                values[key].append(float(np.maximum((t if upper is None else np.minimum(t, upper)) - base, 0).sum()))
    return {key: {'median': float(np.median(v)) if v else None, 'n': len(v),
                  'p10': float(np.quantile(v, .1)) if v else None, 'p90': float(np.quantile(v, .9)) if v else None,
                  'values': [round(x, 1) for x in v]} for key, v in values.items()}


def sensitivity(hourly, daily, lat, names, dewpoint=None, lon=None):
    out = {}
    for name in names:
        a = analyse(hourly, daily, lat, name, dewpoint=dewpoint, lon=lon)
        c = a['classification']
        out[name] = {'chill_definition': a['assumptions']['chill_definition'],
                     'chill_requirement_hours': a['assumptions']['chill_requirement_hours'],
                     'stage_clock': a['assumptions'].get('stage_clock', 'days'),
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
        clock = a.get('chill_clock')
        hypothetical = (not clock['applicable'] if clock
                        else rk['by_id']['chill_shortfall']['eligibility'] == 'not_applicable')
        if hypothetical:
            reason = ' '.join(clock['reasons']) if clock else rk['by_id']['chill_shortfall']['reason']
            parts.append('<p><strong>Hypothetical dates and crop exposures only.</strong> ' + html.escape(reason) + '</p>')
        parts.append(table(['Stage', 'Valid winters', 'Median date', 'p10 date', 'p90 date', 'Median offset from season start'],
                           [[k, cal[k]['n'], cal[k].get('median_date'), cal[k].get('p10_date'),
                             cal[k].get('p90_date'), fmt(cal[k].get('median'))] for k in OFFSETS]))
        cycle = a.get('managed_cycle')
        if cycle:
            fav = cycle['favourable']
            months = lambda values: ', '.join(pd.Timestamp(2001, m, 1).strftime('%b') for m in values) or 'none'
            parts.append('<h3>' + ('Managed-cycle production window (primary)' if cycle['role'] == 'primary'
                                   else 'If managed as an evergreen cycle (comparison)') + '</h3>')
            parts.append(f'<p>Favourable cycle starts (budbreak): {html.escape(", ".join(fav["budbreak"]) or "none")}. '
                         f'Flowering months: {months(fav["flowering_months"])}. Harvest months: {months(fav["harvest_months"])}. '
                         f'Recurring risks at these starts: {html.escape(", ".join(fav["recurring"]) or "none")}.'
                         + (' Weather does not separate start dates.' if fav['unconstrained'] else '') + '</p>')
            parts.append(f'<p class="k">{html.escape(cycle["rule"])}</p>')
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
        if hypothetical:
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


def run(root=ROOT, names=('Waldo', 'Citra', 'Papanduva'), primary=PRIMARY_PROFILE):
    report = {'method': METHOD, 'primary_profile': primary, 'years': [2011, 2025], 'changes': CHANGES, 'limitations': LIMITATIONS,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'sites': {}}
    land = LandMask(root)
    for name in names:
        site, daily, hourly, provenance, hourly_sha = site_inputs(root, name, land)
        weather = dict(dewpoint=hourly.dewpoint_mean_c, lon=site['lon'])
        report['sites'][name] = {
            'latitude': site['lat'], 'longitude': site['lon'],
            'planting': planting_window(site),
            'analysis': analyse(hourly.tmean_c, daily, site['lat'], primary, **weather),
            'sensitivity': sensitivity(hourly.tmean_c, daily, site['lat'], list(PROFILES), **weather),
            'daily_provenance': provenance, 'hourly_sha256': hourly_sha}
    out = root / 'reports/production'
    out.mkdir(parents=True, exist_ok=True)
    write_json(out / 'production_open_field.json', report)
    (out / 'production_open_field.html').write_text(render(report))
    print(json.dumps({n: {'majority_multi': s['analysis']['classification']['multi_feature']['majority'],
                          'mean_chill': s['analysis']['chill_hours'].get('mean'),
                          'flowering_start': s['analysis']['calendar']['flowering_start'].get('median_date'),
                          'top_risk': next((r['risk'] for r in s['analysis']['risks']['ranked']), None)}
                      for n, s in report['sites'].items()}))


def site_inputs(root, name, land=None):
    """Registered pilot site with padded daily weather and its stored hourly temperature/dewpoint frame."""
    site = next(s for s in json.loads((root / 'config/sites.json').read_text()) if s['name'] == name)
    daily, provenance = extract(root, site['lat'], site['lon'], land or LandMask(root), padding=True)
    if daily is None:
        raise ValueError('Unsupported site')
    source = root / 'data/normalized/pilot/pilot' / site['id'] / 'met_hourly.parquet'
    hourly = pd.read_parquet(source).set_index('time')[['tmean_c', 'dewpoint_mean_c']]
    return site, daily.set_index('time'), hourly, provenance, hashlib.sha256(source.read_bytes()).hexdigest()


def thermal_reference_run(root=ROOT, name='Waldo', base=7.0, uppers=(None, 30.0)):
    site, daily, hourly, provenance, hourly_sha = site_inputs(root, name)
    record = {'method': 'legacy-offset-thermal-reference-v1', 'site': name, 'latitude': site['lat'],
              'longitude': site['lon'], 'base_c': base, 'reference_profile': 'legacy_paul_v1', 'winters': [2011, 2025],
              'hourly_sha256': hourly_sha, 'daily_provenance': provenance,
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'cutoffs': {str(u): thermal_reference(hourly.tmean_c, daily, site['lat'], base, u) for u in uppers}}
    write_json(root / 'reports/production/thermal_reference.json', record)
    print(json.dumps({u: {k: v['median'] for k, v in r.items()} for u, r in record['cutoffs'].items()}))


if __name__ == '__main__':
    import sys
    thermal_reference_run() if sys.argv[1:] == ['thermal-reference'] else run()
