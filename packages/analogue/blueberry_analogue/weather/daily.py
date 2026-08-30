"""Last-decade daily base weather.

NASA POWER daily is the live source. A physics-ish fallback keeps tests
and air-gapped diagnose runs honest: labeled fallback, never sold as ERA5.
"""

from __future__ import annotations

from typing import Any

import httpx
import numpy as np
import pandas as pd

from blueberry_analogue.climate.fetch import (
    POWER_DAILY,
    POWER_PARAMS,
    USER_AGENT,
    fallback_climatology,
    monthly_to_daily,
)

DEFAULT_START_YEAR = 2015
DEFAULT_END_YEAR = 2024

BASE_VARS = ("tmin_c", "tmax_c", "tmean_c", "precip_mm", "sw_mj", "rh", "wind_ms", "tdew_c")


def _power_daily_series(block: dict[str, Any], key: str) -> dict[str, float]:
    raw = block.get(key) or {}
    out: dict[str, float] = {}
    for day, val in raw.items():
        if val is None or val == -999:
            continue
        out[str(day)] = float(val)
    return out


def fetch_nasa_power_daily(
    lat: float,
    lon: float,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    timeout: float = 90.0,
) -> pd.DataFrame | None:
    """Dated daily series at a point. This is the base data, not climatology."""
    params = {
        "parameters": POWER_PARAMS,
        "community": "AG",
        "longitude": f"{lon:.4f}",
        "latitude": f"{lat:.4f}",
        "start": f"{start_year}0101",
        "end": f"{end_year}1231",
        "format": "JSON",
    }
    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
            r = client.get(POWER_DAILY, params=params)
            r.raise_for_status()
            body = r.json()
    except Exception:
        return None
    props = body.get("properties", {}).get("parameter", {})
    if not props:
        return None
    tmin = _power_daily_series(props, "T2M_MIN")
    if not tmin:
        return None
    tmax = _power_daily_series(props, "T2M_MAX")
    tmean = _power_daily_series(props, "T2M")
    rh = _power_daily_series(props, "RH2M")
    precip = _power_daily_series(props, "PRECTOTCORR")
    sw = _power_daily_series(props, "ALLSKY_SFC_SW_DWN")
    wind = _power_daily_series(props, "WS2M")
    tdew = _power_daily_series(props, "T2MDEW")
    rows = []
    for day, tmin_c in sorted(tmin.items()):
        stamp = pd.Timestamp(str(day))
        rows.append(
            {
                "date": stamp,
                "tmin_c": tmin_c,
                "tmax_c": tmax.get(day, tmin_c + 8.0),
                "tmean_c": tmean.get(day, tmin_c + 4.0),
                "rh": rh.get(day, 70.0),
                "precip_mm": precip.get(day, 0.0),
                "sw_mj": sw.get(day, 15.0),
                "wind_ms": wind.get(day, 2.4),
                "tdew_c": tdew.get(day, tmin_c - 1.0),
            }
        )
    return pd.DataFrame(rows)


def fallback_daily_years(
    lat: float,
    lon: float,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    climatology: dict[str, list[float]] | None = None,
) -> pd.DataFrame:
    """Expand a monthly climatology into dated years with small interannual noise.

    Used when POWER daily is offline. Every year is the same seasonal shape
    plus a seeded anomaly. Not a real winter archive.
    """
    clim = climatology or fallback_climatology(lat, lon)
    seed = abs(int(lat * 1000) + int(lon * 1000)) % (2**32 - 1)
    rng = np.random.default_rng(seed)
    frames = []
    for year in range(start_year, end_year + 1):
        daily = monthly_to_daily(clim, year=year)
        anomaly = float(rng.normal(0.0, 1.1))
        rain_scale = float(max(0.35, rng.normal(1.0, 0.18)))
        daily["tmin_c"] = daily["tmin_c"] + anomaly
        daily["tmax_c"] = daily["tmax_c"] + anomaly
        if "tmean_c" in daily:
            daily["tmean_c"] = daily["tmean_c"] + anomaly
        else:
            daily["tmean_c"] = 0.5 * (daily["tmin_c"] + daily["tmax_c"])
        daily["precip_mm"] = daily["precip_mm"] * rain_scale
        frames.append(daily)
    return pd.concat(frames, ignore_index=True)
