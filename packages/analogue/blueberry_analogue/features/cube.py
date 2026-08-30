"""Phenology feature cube: hourly series to seasonal p10/p50/p90 plus a typical-year vector."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from blueberry_analogue.cards import CultivarCard, VarietyClass, load_cards
from blueberry_analogue.climate.hourly import expand_daily_to_hourly
from blueberry_analogue.features.chill import summarize_chill
from blueberry_analogue.features.physics import (
    bee_hours,
    dli_mol,
    disease_hours,
    fog_metrics,
    frost_by_stage,
    harvest_window_mask,
    heat_metrics,
    rain_crack_metrics,
    vpd_kpa,
)
from blueberry_analogue.systems import ProductionSystem, system_effects


FEATURE_KEYS = [
    "chill_portions",
    "chill_hours",
    "uf_hours",
    "negation_hours",
    "frost_nights_full_bloom",
    "frost_nights_green_fruit",
    "heat_hours_proxy",
    "days_tmax_gt_35",
    "days_berry_gt_42",
    "dli_bloom",
    "dli_winter",
    "vpd_fruit",
    "dtr",
    "bee_hours",
    "anthracnose_hours",
    "botrytis_hours",
    "harvest_rain_days",
    "rain_crack_events",
    "igp_fog_events",
    "monthly_tmin_mean",
    "monthly_tmax_mean",
    "monthly_precip_sum",
    "monthly_vpd_mean",
    "monthly_rsds_mean",
]


def _monthly_vector(daily: pd.DataFrame) -> dict[str, list[float]]:
    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["month"] = work["date"].dt.month
    grp = work.groupby("month")
    months = list(range(1, 13))

    def col(name, default=np.nan):
        if name not in work:
            return [default] * 12
        s = grp[name].mean()
        return [float(s.get(m, default)) for m in months]

    tmin = col("tmin_c")
    tmax = col("tmax_c")
    precip = []
    if "precip_mm" in work:
        s = grp["precip_mm"].sum()
        precip = [float(s.get(m, 0.0)) for m in months]
    else:
        precip = [0.0] * 12
    rh = col("rh", 70.0)
    vpd = [float(vpd_kpa(0.5 * (a + b), r)) for a, b, r in zip(tmin, tmax, rh)]
    sw = col("sw_mj", 15.0)
    return {
        "monthly_tmin": tmin,
        "monthly_tmax": tmax,
        "monthly_precip": precip,
        "monthly_vpd": vpd,
        "monthly_rsds": sw,
        "monthly_dtr": [float(b - a) for a, b in zip(tmin, tmax)],
    }


def features_from_daily(
    daily: pd.DataFrame,
    lat: float,
    cultivar: CultivarCard,
    klass: VarietyClass,
    system: ProductionSystem,
    region: str = "",
) -> dict[str, Any]:
    effects = system_effects(system)
    hourly = expand_daily_to_hourly(daily, lat)
    hourly["time"] = pd.to_datetime(hourly["time"])
    chill = summarize_chill(hourly, lat, negation_c=klass.negation_c)
    cards = load_cards()
    frost = frost_by_stage(hourly, cards.stages, lat=lat)
    fruit_months = [5, 6, 7, 8] if lat >= 0 else [11, 12, 1, 2]
    month = pd.to_datetime(daily["date"]).dt.month.to_numpy()
    fruit_daily = daily.loc[np.isin(month, fruit_months)].copy() if len(daily) else daily
    heat = heat_metrics(fruit_daily if len(fruit_daily) else daily)
    dates = pd.to_datetime(daily["date"])
    harvest = harvest_window_mask(dates, lat, cultivar.market_window[0], cultivar.market_window[1])
    rain = rain_crack_metrics(daily, harvest)
    bees = bee_hours(hourly, system.pollinator)
    disease = disease_hours(hourly)
    fog = fog_metrics(daily, region=region)
    monthly = _monthly_vector(daily)
    sw = daily["sw_mj"].to_numpy(dtype=float) if "sw_mj" in daily else np.full(len(daily), 15.0)
    dli = dli_mol(sw)
    months = dates.dt.month.to_numpy()
    winter = np.isin(months, [11, 12, 1, 2, 3] if lat >= 0 else [5, 6, 7, 8, 9])
    bloom = harvest  # market window as a first harvest/bloom proxy
    tmin = daily["tmin_c"].to_numpy(dtype=float)
    tmax = daily["tmax_c"].to_numpy(dtype=float)
    rh = daily["rh"].to_numpy(dtype=float) if "rh" in daily else np.full(len(daily), 70.0)
    vpd_fruit = float(np.nanmean(vpd_kpa(tmax[bloom] if bloom.any() else tmax, rh[bloom] if bloom.any() else rh)))

    chill_portions = chill["chill_portions"] * effects.chill_relevance
    if system.hcn:
        chill_portions *= 1.15
    dli_bloom = float(np.nanmean(dli[bloom] if bloom.any() else dli)) * effects.dli_multiplier
    dli_winter = float(np.nanmean(dli[winter] if winter.any() else dli)) * effects.dli_multiplier
    harvest_rain = rain["harvest_rain_days"] * effects.rain_crack_multiplier
    botrytis = disease["botrytis_hours"] * effects.botrytis_multiplier

    flower_hours = chill["chill_hours"] * (cultivar.flower_hours / max(cultivar.chill_hours, 1.0))
    leaf_hours = chill["chill_hours"] * (cultivar.leaf_hours / max(cultivar.chill_hours, 1.0))

    vec = {
        "chill_portions": chill_portions,
        "chill_hours": chill["chill_hours"] * effects.chill_relevance,
        "uf_hours": chill["uf_hours"] * effects.chill_relevance,
        "utah_units": chill["utah_units"],
        "negation_hours": chill["negation_hours"],
        "flower_chill_hours": flower_hours,
        "leaf_chill_hours": leaf_hours,
        "frost_nights_full_bloom": frost.get("frost_nights_full_bloom", 0.0) * effects.freeze_water_factor,
        "frost_nights_green_fruit": frost.get("frost_nights_green_fruit", 0.0) * effects.freeze_water_factor,
        "frost_nights_pink": frost.get("frost_nights_pink", 0.0) * effects.freeze_water_factor,
        "heat_hours_proxy": heat["heat_hours_proxy"],
        "days_tmax_gt_32": heat["days_tmax_gt_32"],
        "days_tmax_gt_35": heat["days_tmax_gt_35"],
        "days_berry_gt_42": heat["days_berry_gt_42"],
        "days_berry_gt_48": heat["days_berry_gt_48"],
        "max_berry_c": heat["max_berry_c"],
        "dli_bloom": dli_bloom,
        "dli_winter": dli_winter,
        "vpd_fruit": vpd_fruit,
        "dtr": float(np.nanmean(tmax - tmin)),
        "bee_hours": bees["bee_hours"],
        "pollen_collapse_hours": bees["pollen_collapse_hours"],
        "anthracnose_hours": disease["anthracnose_hours"],
        "botrytis_hours": botrytis,
        "phytophthora_hours": disease["phytophthora_hours"],
        "harvest_rain_days": harvest_rain,
        "harvest_rain_mm": rain["harvest_rain_mm"] * effects.rain_crack_multiplier,
        "rain_crack_events": rain["rain_crack_events"] * effects.rain_crack_multiplier,
        "igp_fog_events": fog["igp_fog_events"],
        "marine_fog_events": fog["marine_fog_events"],
        "fog_dli_loss": fog["fog_dli_loss"],
        "fog_helps": fog["fog_helps"],
        "monthly_tmin_mean": float(np.nanmean(monthly["monthly_tmin"])),
        "monthly_tmax_mean": float(np.nanmean(monthly["monthly_tmax"])),
        "monthly_precip_sum": float(np.nansum(monthly["monthly_precip"])),
        "monthly_vpd_mean": float(np.nanmean(monthly["monthly_vpd"])),
        "monthly_rsds_mean": float(np.nanmean(monthly["monthly_rsds"])),
        "monthly_tmin": monthly["monthly_tmin"],
        "monthly_tmax": monthly["monthly_tmax"],
        "monthly_precip": monthly["monthly_precip"],
        "monthly_vpd": monthly["monthly_vpd"],
        "monthly_rsds": monthly["monthly_rsds"],
        "monthly_dtr": monthly["monthly_dtr"],
        "system_label": system.label,
        "chill_relevance": effects.chill_relevance,
        "soil_ph_weight": effects.soil_ph_weight,
        "par_fraction": effects.par_fraction,
        "uv_fraction": effects.uv_fraction,
        "bloom_advance_days": float(effects.bloom_advance_days),
        "apis_ok": 1.0 if effects.apis_ok else 0.0,
    }
    return vec


def percentiles_from_years(year_rows: list[dict[str, Any]]) -> dict[str, float]:
    out: dict[str, float] = {}
    if not year_rows:
        return out
    keys = [k for k in FEATURE_KEYS if k in year_rows[0]]
    frame = pd.DataFrame([{k: r[k] for k in keys} for r in year_rows])
    for key in keys:
        series = frame[key].astype(float)
        out[f"{key}_p10"] = float(series.quantile(0.10))
        out[f"{key}_p50"] = float(series.quantile(0.50))
        out[f"{key}_p90"] = float(series.quantile(0.90))
    n = len(year_rows)
    # volatility: share of years that would break a generic window
    if "chill_portions" in frame:
        out["years_chill_short"] = float((frame["chill_portions"] < frame["chill_portions"].median() * 0.75).mean())
    if "frost_nights_full_bloom" in frame:
        out["years_frost_break"] = float((frame["frost_nights_full_bloom"] > frame["frost_nights_full_bloom"].quantile(0.8)).mean())
    if "days_berry_gt_42" in frame:
        out["years_heat_break"] = float((frame["days_berry_gt_42"] > 3).mean())
    out["n_years"] = float(n)
    return out


def flatten_for_table(vec: dict[str, Any]) -> dict[str, float | str]:
    flat: dict[str, float | str] = {}
    for key, value in vec.items():
        if isinstance(value, list):
            for i, item in enumerate(value, start=1):
                flat[f"{key}_{i:02d}"] = float(item)
        elif isinstance(value, (int, float, np.floating)):
            flat[key] = float(value)
        else:
            flat[key] = value
    return flat
