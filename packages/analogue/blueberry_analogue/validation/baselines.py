"""Baselines the product must beat: CCAFS T/P, EcoCrop, NZ Landcare-style."""

from __future__ import annotations

from typing import Any

import numpy as np


def baseline0_ccafs_tp(ref: dict[str, Any], cand: dict[str, Any]) -> float:
    """Weighted Euclidean on monthly T and P only, best seasonal lag."""
    best = 1e9
    for lag in range(12):
        acc = 0.0
        for key, w in (("monthly_tmin", 1.0), ("monthly_tmax", 1.0), ("monthly_precip", 1.0)):
            rv = np.asarray(ref[key], dtype=float)
            cv = np.asarray([cand[key][(i + lag) % 12] for i in range(12)], dtype=float)
            pool = np.concatenate([rv, cv])
            sd = float(np.nanstd(pool)) or 1.0
            acc += w * float(np.mean(((rv - cv) / sd) ** 2))
        best = min(best, float(np.sqrt(acc / 3.0)))
    return float(np.exp(-(best**2) / (2 * 1.15**2)))


def _trapezoid(x: float, mn: float, opmn: float, opmx: float, mx: float) -> float:
    if x <= mn or x >= mx:
        return 0.0
    if opmn <= x <= opmx:
        return 1.0
    if x < opmn:
        return (x - mn) / max(1e-6, opmn - mn)
    return (mx - x) / max(1e-6, mx - opmx)


def baseline1_ecocrop(cand: dict[str, Any], irrigated: bool = True) -> float:
    """FAO EcoCrop-style limiting factor for Vaccinium corymbosum.

    Calibrated on published envelopes, not on blueberry packout.
    Irrigated run ignores precip. Rainfed uses monthly precip sum.
    """
    tmean = 0.5 * (float(cand["monthly_tmin_mean"]) + float(cand["monthly_tmax_mean"]))
    tmin_abs = float(min(cand["monthly_tmin"]))
    rain = float(cand["monthly_precip_sum"])
    t_score = _trapezoid(tmean, 6.0, 18.0, 26.0, 32.0)
    kill = 0.0 if tmin_abs < -22.0 else 1.0
    if irrigated:
        p_score = 1.0
    else:
        p_score = _trapezoid(rain, 400.0, 700.0, 1600.0, 2500.0)
    # Peru existence proof: rainfed EcoCrop kills a working evergreen desert.
    return float(min(t_score, kill, p_score))


def baseline2_nz_landcare(cand: dict[str, Any], soil_ok: float = 0.8, slope_ok: float = 0.9) -> float:
    """Vetharaniam / Landcare 2024 geometric mean: one chill curve, frost window, drainage, slope.

    One curve for all classes is the published limitation we are here to beat.
    """
    chill = float(cand.get("chill_hours", 0.0))
    # Single NHB-ish curve
    chill_s = _trapezoid(chill, 200.0, 700.0, 1400.0, 2500.0)
    frost = float(cand.get("frost_nights_full_bloom", 0.0))
    frost_s = _trapezoid(frost, -1.0, 0.0, 4.0, 20.0)
    parts = np.array([chill_s, frost_s, soil_ok, slope_ok], dtype=float)
    parts = np.clip(parts, 1e-6, 1.0)
    return float(np.exp(np.mean(np.log(parts))))
