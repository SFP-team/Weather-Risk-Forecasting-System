"""Planting / flowering / harvest windows from weather.

Provisional until Gerardo and Patricia lock stage dates. The tool
recommends a window; it does not take a market week as a required input.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import numpy as np


def _doy_to_md(doy: float, year: int = 2024) -> str:
    if not np.isfinite(doy) or doy <= 0:
        return ""
    start = date(year, 1, 1)
    day = start + timedelta(days=int(max(0, min(365, doy)) - 1))
    return day.strftime("%m-%d")


def _shift_doy(doy: float, days: int) -> float:
    if not np.isfinite(doy) or doy <= 0:
        return float("nan")
    return float((doy + days - 1) % 365) + 1


def derive_windows(stats: dict[str, Any], lat: float, habit: str) -> dict[str, Any]:
    """Climate-driven planting, flowering, harvest.

    Deciduous: flower after last spring frost and after chill has accumulated.
    Evergreen: flower in the cool season; frost during bloom is the risk.
    Semi-evergreen sits between the two.
    """
    last_frost = float(stats.get("last_frost_doy_p50") or 0.0)
    if lat >= 0:
        evergreen_flower = 30.0  # late January
        deciduous_default = 80.0  # late March
        plant_lead = 90
    else:
        evergreen_flower = 212.0  # late July
        deciduous_default = 262.0
        plant_lead = 90

    if habit == "evergreen":
        flower = evergreen_flower
        ripe_days = 60
        harvest_span = 50
    elif habit == "semi_evergreen":
        flower = last_frost + 8.0 if last_frost > 10 else evergreen_flower + 25
        ripe_days = 62
        harvest_span = 45
    else:
        flower = last_frost + 14.0 if last_frost > 20 else deciduous_default
        ripe_days = 70
        harvest_span = 45

    harvest = _shift_doy(flower, ripe_days)
    harvest_end = _shift_doy(harvest, harvest_span)
    plant = _shift_doy(flower, -plant_lead)
    plant_end = _shift_doy(flower, -30)
    flower_end = _shift_doy(flower, 35)

    return {
        "habit": habit,
        "provisional": True,
        "planting": {
            "start": _doy_to_md(plant),
            "end": _doy_to_md(plant_end),
            "doy_start": plant,
        },
        "flowering": {
            "start": _doy_to_md(flower),
            "end": _doy_to_md(flower_end),
            "doy_start": flower,
        },
        "harvest": {
            "start": _doy_to_md(harvest),
            "end": _doy_to_md(harvest_end),
            "doy_start": harvest,
            "doy_end": harvest_end,
        },
        "notes": [
            "Windows are derived from last-frost and habit, not from a grower calendar.",
            "Tunnels can pull bloom earlier by about 30 days. That is applied in modifiers.",
        ],
    }


def harvest_mask_from_windows(dates, windows: dict[str, Any]) -> np.ndarray:
    """Boolean mask for harvest days, wrapping year-end if needed."""
    import pandas as pd

    doy = pd.to_datetime(dates).dt.dayofyear.to_numpy()
    start = windows["harvest"].get("doy_start")
    end = windows["harvest"].get("doy_end")
    if start is None or end is None or not np.isfinite(start) or not np.isfinite(end):
        return np.ones(len(doy), dtype=bool)
    if start <= end:
        return (doy >= start) & (doy <= end)
    return (doy >= start) | (doy <= end)
