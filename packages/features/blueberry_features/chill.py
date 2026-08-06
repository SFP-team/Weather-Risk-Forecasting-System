"""Chill hour estimation from daily data.

MVP uses a daily approximation of hours between 32–45°F when only daily
Tmin/Tmax are available (sine-curve interpolation between min and max).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def chill_hours_from_daily(tmin_f: float, tmax_f: float, n_steps: int = 24) -> float:
    """Approximate chill hours (32–45°F) using sine diurnal curve."""
    if tmin_f is None or tmax_f is None or np.isnan(tmin_f) or np.isnan(tmax_f):
        return 0.0
    if tmax_f < tmin_f:
        tmin_f, tmax_f = tmax_f, tmin_f
    # Hours of day 0..1
    x = np.linspace(0, 1, n_steps, endpoint=False)
    # Min near sunrise (~hour 6 -> 0.25), max afternoon (~0.65)
    temps = tmin_f + (tmax_f - tmin_f) * (0.5 * (1 - np.cos(2 * np.pi * (x - 0.25))))
    # Simpler: linear half-day up/down is enough for MVP
    temps = np.concatenate(
        [
            np.linspace(tmin_f, tmax_f, n_steps // 2, endpoint=False),
            np.linspace(tmax_f, tmin_f, n_steps - n_steps // 2, endpoint=False),
        ]
    )
    in_band = (temps >= 32.0) & (temps <= 45.0)
    return float(in_band.sum() * (24.0 / n_steps))


def season_chill_to_date(
    df: pd.DataFrame,
    as_of: pd.Timestamp | None = None,
    season_start_month: int = 11,
    season_start_day: int = 1,
) -> float:
    """Sum chill hours from Nov 1 of current chill season through as_of."""
    if df.empty:
        return 0.0
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"])
    if as_of is None:
        as_of = work["date"].max()
    as_of = pd.Timestamp(as_of)
    # Chill season: Nov 1 year Y to Feb/Mar year Y+1
    if as_of.month >= season_start_month:
        start = pd.Timestamp(year=as_of.year, month=season_start_month, day=season_start_day)
    else:
        start = pd.Timestamp(year=as_of.year - 1, month=season_start_month, day=season_start_day)
    mask = (work["date"] >= start) & (work["date"] <= as_of)
    if "chill_hours" in work.columns:
        return float(work.loc[mask, "chill_hours"].fillna(0).sum())
    total = 0.0
    for _, row in work.loc[mask].iterrows():
        total += chill_hours_from_daily(row.get("tmin_f"), row.get("tmax_f"))
    return total
