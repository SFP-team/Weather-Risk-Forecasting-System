"""Daily Tmin/Tmax to hourly air temperature.

Daytime uses a sine from sunrise Tmin to afternoon Tmax.
Nighttime uses a logarithmic decay toward the next Tmin, as in
Linsley-Noakes / chillR stack_hourly_temps. Good enough for chill
portions at a point. Not a canopy model.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


def _day_length_hours(lat: float, doy: int) -> float:
    lat_r = math.radians(lat)
    decl = 0.409 * math.sin(2 * math.pi / 365 * doy - 1.39)
    arg = max(-1.0, min(1.0, -math.tan(lat_r) * math.tan(decl)))
    ws = math.acos(arg)
    return 24.0 * ws / math.pi


def hourly_curve(tmin: float, tmax: float, lat: float, doy: int) -> np.ndarray:
    if any(map(lambda x: x is None or (isinstance(x, float) and math.isnan(x)), (tmin, tmax))):
        return np.full(24, np.nan)
    if tmax < tmin:
        tmin, tmax = tmax, tmin
    daylen = max(6.0, min(18.0, _day_length_hours(lat, doy)))
    sunrise = 12.0 - daylen / 2.0
    sunset = 12.0 + daylen / 2.0
    t_peak = sunrise + 0.75 * daylen
    hours = np.arange(24, dtype=float)
    out = np.empty(24, dtype=float)
    for h in hours.astype(int):
        if sunrise <= h <= sunset:
            # sine 0 at sunrise, 1 at peak, back toward sunset
            if h <= t_peak:
                frac = (h - sunrise) / max(1e-6, t_peak - sunrise)
                out[h] = tmin + (tmax - tmin) * math.sin(math.pi / 2 * frac)
            else:
                frac = (h - t_peak) / max(1e-6, sunset - t_peak)
                out[h] = tmax - (tmax - tmin) * 0.35 * frac
        else:
            # night decay toward tmin
            if h > sunset:
                night_pos = h - sunset
                night_len = (24 - sunset) + sunrise
            else:
                night_pos = (24 - sunset) + h
                night_len = (24 - sunset) + sunrise
            frac = min(1.0, night_pos / max(1e-6, night_len))
            # log-like: fast drop then flatten
            out[h] = tmax * 0.65 + tmin * 0.35 + (tmin - (tmax * 0.65 + tmin * 0.35)) * math.log1p(5 * frac) / math.log1p(5)
    return out


def expand_daily_to_hourly(daily: pd.DataFrame, lat: float) -> pd.DataFrame:
    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"])
    n = len(work)
    temps = np.empty((n, 24), dtype=float)
    doys = work["date"].dt.dayofyear.to_numpy()
    tmin = work["tmin_c"].to_numpy(dtype=float)
    tmax = work["tmax_c"].to_numpy(dtype=float)
    for i in range(n):
        temps[i] = hourly_curve(float(tmin[i]), float(tmax[i]), lat, int(doys[i]))
    rh = work["rh"].to_numpy(dtype=float) if "rh" in work else np.full(n, 70.0)
    rain = work["precip_mm"].to_numpy(dtype=float) if "precip_mm" in work else np.zeros(n)
    sw = work["sw_mj"].to_numpy(dtype=float) if "sw_mj" in work else np.full(n, 15.0)
    wind = work["wind_ms"].to_numpy(dtype=float) if "wind_ms" in work else np.full(n, 2.0)
    dew = work["tdew_c"].to_numpy(dtype=float) if "tdew_c" in work else tmin
    dates = work["date"].to_numpy()
    hours = np.tile(np.arange(24), n)
    day_idx = np.repeat(np.arange(n), 24)
    return pd.DataFrame(
        {
            "time": pd.to_datetime(dates[day_idx]) + pd.to_timedelta(hours, unit="h"),
            "temp_c": temps.ravel(),
            "rh": np.repeat(rh, 24),
            "precip_mm": np.repeat(rain / 24.0, 24),
            "sw_mj_hour": np.repeat(sw / 24.0, 24),
            "wind_ms": np.repeat(wind, 24),
            "tdew_c": np.repeat(dew, 24),
        }
    )
