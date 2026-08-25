"""Dual chill currencies plus negation.

Implements Luedeling chillR Dynamic_Model / DynModel_driver constants
(Erez, Fishman, Couvillon). Also Bennett/Weinberger hours 0-7.2 C,
UF 32-45 F, Utah units (not recommended in warm climates), and hours
above the negation threshold.

Do not convert hours to portions linearly.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


E0 = 4153.5
E1 = 12888.8
A0 = 139500.0
A1 = 2.567e18
SLOPE = 1.6
TF_K = 277.0


def dynamic_portions(hourly_c: np.ndarray, cumulative: bool = True) -> np.ndarray:
    """ChillR Dynamic_Model on hourly Celsius."""
    temps = np.asarray(hourly_c, dtype=float)
    n = len(temps)
    if n == 0:
        return np.array([])
    tk = temps + 273.0
    valid = np.isfinite(tk)
    tk = np.where(valid, tk, 273.0)
    aa = A0 / A1
    ee = E1 - E0
    sr = np.exp(SLOPE * TF_K * (tk - TF_K) / tk)
    xi = sr / (1.0 + sr)
    xs = aa * np.exp(ee / tk)
    eak1 = np.exp(-A1 * np.exp(-E1 / tk))

    x = np.zeros(n, dtype=float)
    for idx in range(1, n):
        if not valid[idx - 1]:
            x[idx] = x[idx - 1]
            continue
        s = x[idx - 1]
        if x[idx - 1] >= 1.0 and idx >= 2:
            s = s * (1.0 - xi[idx - 2])
        x[idx] = xs[idx - 1] - (xs[idx - 1] - s) * eak1[idx - 1]

    delta = np.zeros(n, dtype=float)
    over = np.where((x >= 1.0) & valid)[0]
    for i in over:
        if i >= 1:
            delta[i] = x[i] * xi[i - 1]
    return np.cumsum(delta) if cumulative else delta


def chill_hours_0_7p2(hourly_c: np.ndarray) -> np.ndarray:
    temps = np.asarray(hourly_c, dtype=float)
    return ((temps >= 0.0) & (temps <= 7.2)).astype(float)


def uf_hours_32_45f(hourly_c: np.ndarray) -> np.ndarray:
    f = np.asarray(hourly_c, dtype=float) * 9.0 / 5.0 + 32.0
    return ((f >= 32.0) & (f <= 45.0)).astype(float)


def utah_units(hourly_c: np.ndarray) -> np.ndarray:
    t = np.asarray(hourly_c, dtype=float)
    w = np.zeros_like(t)
    w[(t > 1.4) & (t <= 2.4)] = 0.5
    w[(t > 2.4) & (t <= 9.1)] = 1.0
    w[(t > 9.1) & (t <= 12.4)] = 0.5
    w[(t > 15.9) & (t <= 18.0)] = -0.5
    w[t > 18.0] = -1.0
    return w


def negation_hours(hourly_c: np.ndarray, threshold_c: float = 21.0) -> np.ndarray:
    t = np.asarray(hourly_c, dtype=float)
    return (t > threshold_c).astype(float)


def anderson_gdh(hourly_c: np.ndarray, tb: float = 4.0, tu: float = 25.0, tc: float = 36.0) -> np.ndarray:
    """Anderson et al. 1986 growing degree hours."""
    t = np.asarray(hourly_c, dtype=float)
    w = np.zeros_like(t)
    mid = (t >= tb) & (t <= tu)
    hot = (t > tu) & (t <= tc)
    w[mid] = (tu - tb) / 2.0 * (1.0 + np.cos(np.pi + np.pi * (t[mid] - tb) / (tu - tb)))
    w[hot] = (tu - tb) * (1.0 + np.cos(np.pi / 2.0 + np.pi / 2.0 * (t[hot] - tu) / (tc - tu)))
    return w


def season_mask(index: pd.DatetimeIndex, lat: float) -> np.ndarray:
    """Nov-Mar north, May-Sep south."""
    month = np.asarray(index.month)
    if lat < 0:
        return np.isin(month, [5, 6, 7, 8, 9])
    return np.isin(month, [11, 12, 1, 2, 3])


def summarize_chill(hourly: pd.DataFrame, lat: float, negation_c: float = 21.0) -> dict[str, float]:
    temps = hourly["temp_c"].to_numpy(dtype=float)
    idx = pd.DatetimeIndex(hourly["time"])
    mask = season_mask(idx, lat)
    winter = temps[mask]
    if winter.size == 0:
        winter = temps
    portions = dynamic_portions(temps, cumulative=True)
    winter_portions = dynamic_portions(winter, cumulative=True)
    return {
        "chill_portions": float(winter_portions[-1]) if winter_portions.size else 0.0,
        "chill_hours": float(chill_hours_0_7p2(winter).sum()),
        "uf_hours": float(uf_hours_32_45f(winter).sum()),
        "utah_units": float(utah_units(winter).sum()),
        "negation_hours": float(negation_hours(winter, negation_c).sum()),
        "gdh_after_winter": float(anderson_gdh(temps[~mask] if mask.any() else temps).sum()),
        "chill_portions_full_series": float(portions[-1]) if portions.size else 0.0,
    }
