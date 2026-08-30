"""Year-by-year climate stats from a daily series.

These are the numbers the risk and production-system formulas consume.
Chill is counted on a synthetic hourly curve from dated daily Tmin/Tmax —
real winters if the daily source is POWER daily, not a single climatology year.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from blueberry_analogue.climate.hourly import expand_daily_to_hourly
from blueberry_analogue.features.chill import chill_hours_0_7p2, summarize_chill
from blueberry_analogue.features.physics import dli_mol, heat_metrics, rain_crack_metrics


def winter_mask(dates: pd.Series, lat: float) -> np.ndarray:
    months = pd.to_datetime(dates).dt.month.to_numpy()
    if lat >= 0:
        return np.isin(months, [11, 12, 1, 2, 3])
    return np.isin(months, [5, 6, 7, 8, 9])


def winter_season_year(dates: pd.Series, lat: float) -> np.ndarray:
    """Label a winter by the year of its January (NH) or July (SH)."""
    dt = pd.to_datetime(dates)
    year = dt.dt.year.to_numpy()
    month = dt.dt.month.to_numpy()
    if lat >= 0:
        return np.where(month >= 11, year + 1, year)
    return year


def _percentiles(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"p10": float("nan"), "p50": float("nan"), "p90": float("nan"), "mean": float("nan")}
    return {
        "p10": float(np.quantile(arr, 0.10)),
        "p50": float(np.quantile(arr, 0.50)),
        "p90": float(np.quantile(arr, 0.90)),
        "mean": float(np.mean(arr)),
    }


def _chill_hours_for_winter(winter_daily: pd.DataFrame, lat: float) -> float:
    if winter_daily.empty:
        return float("nan")
    hourly = expand_daily_to_hourly(winter_daily, lat)
    return float(chill_hours_0_7p2(hourly["temp_c"].to_numpy(dtype=float)).sum())


def climate_stats(
    daily: pd.DataFrame,
    lat: float,
    harvest_mask: np.ndarray | None = None,
) -> dict[str, Any]:
    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"])
    work = work.sort_values("date").reset_index(drop=True)
    dates = work["date"]
    winter = winter_mask(dates, lat)
    seasons = winter_season_year(dates, lat)
    tmin = work["tmin_c"].to_numpy(dtype=float)
    tmax = work["tmax_c"].to_numpy(dtype=float)
    precip = work["precip_mm"].to_numpy(dtype=float) if "precip_mm" in work else np.zeros(len(work))
    sw = work["sw_mj"].to_numpy(dtype=float) if "sw_mj" in work else np.full(len(work), 15.0)

    chill_years: list[float] = []
    frost_years: list[float] = []
    hard_freeze_years: list[float] = []
    winter_tmin_years: list[float] = []
    year_ids = sorted({int(y) for y, w in zip(seasons, winter) if w})
    for year in year_ids:
        sel = (seasons == year) & winter
        if sel.sum() < 40:
            continue
        block = work.loc[sel]
        chill_years.append(_chill_hours_for_winter(block, lat))
        ytmin = tmin[sel]
        frost_years.append(float((ytmin <= 0.0).sum()))
        hard_freeze_years.append(float((ytmin <= -2.2).sum()))
        winter_tmin_years.append(float(np.nanmin(ytmin)))

    if harvest_mask is None:
        harvest_mask = ~winter
    harvest_mask = np.asarray(harvest_mask, dtype=bool)
    if harvest_mask.shape[0] != len(work):
        harvest_mask = ~winter

    rain = rain_crack_metrics(work, harvest_mask)
    heat = heat_metrics(work.loc[harvest_mask] if harvest_mask.any() else work)
    dli = dli_mol(sw)
    fruit_dli = dli[harvest_mask] if harvest_mask.any() else dli

    # drought: share of 30-day windows in the warm half with < 15 mm
    dry_events = 0
    if len(work) >= 30:
        rain_roll = pd.Series(precip).rolling(30, min_periods=30).sum()
        warm = ~winter
        dry_events = int(((rain_roll < 15.0) & warm).sum() / 15.0)

    last_frost_doys: list[float] = []
    for year in year_ids:
        sel = seasons == year
        block = work.loc[sel]
        if block.empty:
            continue
        if lat >= 0:
            spring = block[block["date"].dt.month.isin([1, 2, 3, 4, 5])]
        else:
            spring = block[block["date"].dt.month.isin([7, 8, 9, 10, 11])]
        hits = spring[spring["tmin_c"] <= 0.0]
        if len(hits):
            last_frost_doys.append(float(hits["date"].dt.dayofyear.max()))
        else:
            last_frost_doys.append(0.0)

    # typical-year chill portions on the median-ish year (middle of the archive)
    mid_year = year_ids[len(year_ids) // 2] if year_ids else int(dates.dt.year.median() or 2018)
    typical = work[dates.dt.year == mid_year]
    if typical.empty:
        typical = work
    hourly = expand_daily_to_hourly(typical, lat)
    chill = summarize_chill(hourly, lat)

    monthly = work.copy()
    monthly["month"] = monthly["date"].dt.month
    grp = monthly.groupby("month")
    monthly_tmin = [float(grp["tmin_c"].mean().get(m, float("nan"))) for m in range(1, 13)]
    monthly_tmax = [float(grp["tmax_c"].mean().get(m, float("nan"))) for m in range(1, 13)]
    monthly_precip = [float(grp["precip_mm"].sum().get(m, 0.0) / max(1, len(year_ids))) for m in range(1, 13)]
    monthly_sw = [float(grp["sw_mj"].mean().get(m, float("nan"))) for m in range(1, 13)]

    chill_p = _percentiles(chill_years)
    frost_p = _percentiles(frost_years)
    hard_p = _percentiles(hard_freeze_years)
    tmin_p = _percentiles(winter_tmin_years)
    frost_doy = _percentiles(last_frost_doys)

    return {
        "n_years": float(len(chill_years) or max(1, work["date"].dt.year.nunique())),
        "chill_hours_p10": chill_p["p10"],
        "chill_hours_p50": chill_p["p50"],
        "chill_hours_p90": chill_p["p90"],
        "chill_hours": chill_p["p50"],
        "chill_portions": float(chill["chill_portions"]),
        "uf_hours": float(chill["uf_hours"]),
        "negation_hours": float(chill["negation_hours"]),
        "frost_days_p50": frost_p["p50"],
        "frost_days_p90": frost_p["p90"],
        "hard_freeze_days_p50": hard_p["p50"],
        "winter_tmin_p10": tmin_p["p10"],
        "winter_tmin_min": tmin_p["p10"],
        "last_frost_doy_p50": frost_doy["p50"],
        "harvest_rain_days": float(rain["harvest_rain_days"] / max(1.0, len(year_ids) or 1.0)),
        "harvest_rain_mm": float(rain["harvest_rain_mm"] / max(1.0, len(year_ids) or 1.0)),
        "rain_crack_events": float(rain["rain_crack_events"] / max(1.0, len(year_ids) or 1.0)),
        "dli_fruit": float(np.nanmean(fruit_dli)) if fruit_dli.size else float("nan"),
        "dli_winter": float(np.nanmean(dli[winter])) if winter.any() else float("nan"),
        "days_tmax_gt_35": float(heat["days_tmax_gt_35"] / max(1.0, len(year_ids) or 1.0)),
        "days_berry_gt_42": float(heat["days_berry_gt_42"] / max(1.0, len(year_ids) or 1.0)),
        "heat_hours_proxy": float(heat["heat_hours_proxy"] / max(1.0, len(year_ids) or 1.0)),
        "annual_precip_mm": float(precip.sum() / max(1.0, work["date"].dt.year.nunique())),
        "drought_events_p50": float(dry_events / max(1.0, work["date"].dt.year.nunique())),
        "dtr": float(np.nanmean(tmax - tmin)),
        "monthly_tmin": monthly_tmin,
        "monthly_tmax": monthly_tmax,
        "monthly_precip": monthly_precip,
        "monthly_rsds": monthly_sw,
        "year_chill_hours": chill_years,
        "year_frost_days": frost_years,
    }
