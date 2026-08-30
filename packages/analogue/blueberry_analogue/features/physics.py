"""Stage-aware freeze, berry heat, DLI, VPD, bees, disease, rain-crack, fog."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from blueberry_analogue.cards import FloralStage


def saturation_kpa(temp_c: np.ndarray | float) -> np.ndarray:
    t = np.asarray(temp_c, dtype=float)
    return 0.6108 * np.exp(17.27 * t / (t + 237.3))


def vpd_kpa(temp_c: np.ndarray, rh: np.ndarray) -> np.ndarray:
    es = saturation_kpa(temp_c)
    return np.maximum(0.0, es * (1.0 - np.asarray(rh, dtype=float) / 100.0))


def stull_wet_bulb(temp_c: np.ndarray, rh: np.ndarray) -> np.ndarray:
    """Stull 2011 wet-bulb approximation, Celsius."""
    t = np.asarray(temp_c, dtype=float)
    rh = np.clip(np.asarray(rh, dtype=float), 1.0, 100.0)
    return (
        t * np.arctan(0.151977 * (rh + 8.313659) ** 0.5)
        + np.arctan(t + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * rh**1.5 * np.arctan(0.023101 * rh)
        - 4.686035
    )


def berry_surface_c(air_tmax: np.ndarray) -> np.ndarray:
    """Yang, Bryla, Strik 2019: sun-side berries 7-11 C hotter when air > 35 C."""
    t = np.asarray(air_tmax, dtype=float)
    extra = np.where(t > 35.0, 7.0 + np.clip((t - 35.0) / 5.0, 0, 1) * 4.0, 0.0)
    extra = np.where((t > 32.0) & (t <= 35.0), 3.0 + (t - 32.0), extra)
    return t + extra


def dli_mol(sw_mj: np.ndarray) -> np.ndarray:
    """Daily light integral from shortwave MJ m-2 d-1. About 2.07 mol per MJ sunlight."""
    return np.asarray(sw_mj, dtype=float) * 2.07


def ppfd_hours_from_daily_sw(sw_mj: float, daylen_h: float, thresholds=(400.0, 600.0)) -> dict[str, float]:
    """Rough hours above PPFD thresholds assuming a sine-daylight field."""
    if sw_mj <= 0 or daylen_h <= 0:
        return {f"hours_ppfd_gt_{int(t)}": 0.0 for t in thresholds}
    # mean PPFD µmol m-2 s-1 ≈ SW_W * 2.07
    mean_w = sw_mj * 1e6 / (daylen_h * 3600.0)
    peak = mean_w * math.pi / 2.0
    peak_ppfd = peak * 2.07
    out = {}
    for thr in thresholds:
        if peak_ppfd <= thr:
            out[f"hours_ppfd_gt_{int(thr)}"] = 0.0
        else:
            # sine day: duration where peak*sin(pi t / L) > thr
            frac = 1.0 - (2.0 / math.pi) * math.asin(min(1.0, thr / peak_ppfd))
            out[f"hours_ppfd_gt_{int(thr)}"] = max(0.0, frac * daylen_h)
    return out


def bee_hours(hourly: pd.DataFrame, pollinator: str = "apis") -> dict[str, float]:
    t = hourly["temp_c"].to_numpy(dtype=float)
    rh = hourly["rh"].to_numpy(dtype=float)
    rain = hourly["precip_mm"].to_numpy(dtype=float)
    if pollinator == "bombus":
        ok = (t >= 10.0) & (t <= 32.0) & (rh < 95) & (rain < 0.2)
    elif pollinator == "none":
        ok = np.zeros_like(t, dtype=bool)
    else:
        ok = (t >= 16.0) & (t <= 32.0) & (rh < 90) & (rain < 0.05)
    pollen_collapse = float((t > 35.0).sum())
    warm_nights = float(((t > 21.0) & (hourly["time"].dt.hour < 6)).sum()) if hasattr(hourly["time"], "dt") else 0.0
    return {
        "bee_hours": float(ok.sum()),
        "pollen_collapse_hours": pollen_collapse,
        "warm_night_hours": warm_nights,
    }


def disease_hours(hourly: pd.DataFrame) -> dict[str, float]:
    t = hourly["temp_c"].to_numpy(dtype=float)
    rh = hourly["rh"].to_numpy(dtype=float)
    rain = hourly["precip_mm"].to_numpy(dtype=float)
    wet = (rh >= 90.0) | (rain > 0.05)
    anthracnose = (t >= 15.0) & (t <= 27.0) & wet
    botrytis = (t >= 15.0) & (t <= 20.0) & wet
    # consecutive wet hours proxy: rolling 12
    wet_s = pd.Series(wet.astype(int))
    streak12 = float((wet_s.rolling(12, min_periods=12).sum() >= 12).sum())
    phyto = float(((rh >= 95) & (rain > 0.1)).sum())
    return {
        "anthracnose_hours": float(anthracnose.sum()),
        "botrytis_hours": float(botrytis.sum()),
        "wet_streak_12h": streak12,
        "phytophthora_hours": phyto,
    }


STAGE_MONTHS_NORTH = {
    "dormant": [11, 12, 1, 2],
    "tight_cluster": [3, 4],
    "pink": [3, 4],
    "full_bloom": [4, 5],
    "petal_fall": [4, 5],
    "green_fruit": [5, 6, 7],
    "harvest": [6, 7, 8],
}
STAGE_MONTHS_SOUTH = {
    "dormant": [5, 6, 7, 8],
    "tight_cluster": [9, 10],
    "pink": [9, 10],
    "full_bloom": [10, 11],
    "petal_fall": [10, 11],
    "green_fruit": [11, 12, 1],
    "harvest": [12, 1, 2],
}


def frost_by_stage(hourly: pd.DataFrame, stages: list[FloralStage], lat: float = 40.0) -> dict[str, float]:
    """Count wet-bulb hours below stage LTs only in that stage's months.

    Counting the whole year as bloom frost is how you get 200 'bloom nights' in Michigan.
    """
    tw = stull_wet_bulb(hourly["temp_c"].to_numpy(dtype=float), hourly["rh"].to_numpy(dtype=float))
    tmin_hours = hourly["temp_c"].to_numpy(dtype=float)
    months = pd.to_datetime(hourly["time"]).dt.month.to_numpy()
    table = STAGE_MONTHS_SOUTH if lat < 0 else STAGE_MONTHS_NORTH
    nights = {}
    for stage in stages:
        month_ok = np.isin(months, table.get(stage.id, list(range(1, 13))))
        hit = month_ok & ((tw <= stage.lt_c) | (tmin_hours <= stage.lt_c))
        nights[f"frost_nights_{stage.id}"] = float(hit.sum() / 8.0)
        nights[f"wetbulb_hours_below_{stage.id}"] = float((month_ok & (tw <= stage.lt_c)).sum())
    nights["frost_nights_0c"] = float((tmin_hours <= 0).sum() / 8.0)
    nights["advective_hint"] = float(
        ((hourly["temp_c"] <= 0) & (hourly["wind_ms"] >= 2.5)).sum()
    )
    return nights


def heat_metrics(daily: pd.DataFrame) -> dict[str, float]:
    tmax = daily["tmax_c"].to_numpy(dtype=float)
    berry = berry_surface_c(tmax)
    return {
        "heat_hours_proxy": float(np.clip(tmax - 32.0, 0, None).sum() * 4.0),
        "days_tmax_gt_32": float((tmax > 32).sum()),
        "days_tmax_gt_35": float((tmax > 35).sum()),
        "days_berry_gt_42": float((berry >= 42).sum()),
        "days_berry_gt_48": float((berry >= 48).sum()),
        "max_berry_c": float(np.nanmax(berry)) if berry.size else float("nan"),
    }


def rain_crack_metrics(daily: pd.DataFrame, harvest_mask: np.ndarray | None = None) -> dict[str, float]:
    rain = daily["precip_mm"].to_numpy(dtype=float)
    if harvest_mask is None:
        harvest_mask = np.ones(len(rain), dtype=bool)
    harvest_rain = rain[harvest_mask]
    dry = 0
    events = 0
    for mm in harvest_rain:
        if mm < 1.0:
            dry += 1
        elif dry >= 5 and mm >= 8.0:
            events += 1
            dry = 0
        else:
            dry = 0
    return {
        "harvest_rain_days": float((harvest_rain >= 5.0).sum()),
        "harvest_rain_mm": float(harvest_rain.sum()),
        "rain_crack_events": float(events),
    }


def fog_metrics(daily: pd.DataFrame, region: str = "") -> dict[str, float]:
    """Two fogs. IGP winter radiation fog is a DLI crash. Marine summer fog can help."""
    rh = daily["rh"].to_numpy(dtype=float) if "rh" in daily else np.full(len(daily), 70.0)
    sw = daily["sw_mj"].to_numpy(dtype=float) if "sw_mj" in daily else np.full(len(daily), 15.0)
    months = pd.to_datetime(daily["date"]).dt.month.to_numpy()
    winter = np.isin(months, [11, 12, 1, 2]) if float(daily.get("lat", [20])[0] if False else 1) else np.isin(months, [11, 12, 1, 2])
    igp = region.startswith("IN-") or "IGP" in region
    marine = region in {"US-CA", "CL-SOUTH", "MX-BCN", "MA-NORTH"} or region.endswith("CA")
    low_sw = sw < 8.0
    high_rh = rh > 88
    cloudy_winter = float((winter & low_sw & high_rh).sum())
    igp_events = cloudy_winter if igp else 0.0
    marine_events = float((~winter & high_rh & (sw < 12)).sum()) if marine else 0.0
    kind = "igp_winter" if igp else ("marine_summer" if marine else "unknown")
    dli_loss = float(((15.0 - sw).clip(0) * (high_rh & winter)).sum())
    return {
        "fog_kind": 1.0 if kind == "igp_winter" else (0.0 if kind == "marine_summer" else 0.5),
        "fog_events": igp_events + marine_events,
        "igp_fog_events": igp_events,
        "marine_fog_events": marine_events,
        "fog_dli_loss": dli_loss,
        "fog_helps": 1.0 if kind == "marine_summer" else 0.0,
    }


def harvest_window_mask(dates: pd.Series, lat: float, start_week: int, end_week: int) -> np.ndarray:
    iso = pd.to_datetime(dates).dt.isocalendar().week.astype(int).to_numpy()
    if start_week <= end_week:
        return (iso >= start_week) & (iso <= end_week)
    return (iso >= start_week) | (iso <= end_week)
