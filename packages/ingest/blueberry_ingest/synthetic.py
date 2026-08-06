"""Generate realistic multi-year Florida blueberry-belt daily weather.

Used as reliable offline training corpus. Optionally bias-corrected with
live Open-Meteo when available.
"""

from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pandas as pd

from blueberry_common.stations import STATIONS, Station


def _seasonal_tmean_f(doy: np.ndarray, lat: float) -> np.ndarray:
    """Approximate FL daily mean temp (°F) by day-of-year and latitude."""
    # South is warmer; annual cycle peaks ~DOY 200
    base = 72.0 - (lat - 27.0) * 1.8
    amp = 12.0 + (lat - 27.0) * 0.6
    return base + amp * np.sin(2 * np.pi * (doy - 110) / 365.25)


def generate_station_history(
    station: Station,
    start: date = date(2008, 1, 1),
    end: date | None = None,
    seed: int | None = None,
) -> pd.DataFrame:
    if end is None:
        end = date.today()
    rng = np.random.default_rng(seed if seed is not None else abs(hash(station.id)) % (2**32))

    days = pd.date_range(start, end, freq="D")
    n = len(days)
    doy = days.dayofyear.to_numpy()

    tmean = _seasonal_tmean_f(doy, station.lat)
    # ENSO-ish multi-year modulation
    year_frac = (days.year + doy / 365.25).to_numpy()
    enso = 1.5 * np.sin(2 * np.pi * year_frac / 3.7 + hash(station.id) % 7)
    tmean = tmean + enso + rng.normal(0, 3.2, n)

    # Diurnal range larger in winter/spring interior
    dtr = 16.0 + 4.0 * np.sin(2 * np.pi * (doy - 30) / 365.25) + rng.normal(0, 1.5, n)
    tmax = tmean + dtr / 2
    tmin = tmean - dtr / 2

    # Occasional hard freezes north-central Jan–Mar
    for i, d in enumerate(days):
        if d.month in (12, 1, 2, 3) and rng.random() < (0.04 if station.region == "north-central" else 0.015):
            tmin[i] = min(tmin[i], rng.uniform(18, 31))
            tmax[i] = max(tmax[i], tmin[i] + 8)

    # Warm winter spikes (chill negation)
    for i, d in enumerate(days):
        if d.month in (11, 12, 1, 2) and rng.random() < 0.03:
            tmin[i] = max(tmin[i], rng.uniform(55, 68))
            tmax[i] = max(tmax[i], rng.uniform(75, 85))

    # Precip: wetter summer
    p_rain = 0.18 + 0.22 * (np.sin(2 * np.pi * (doy - 150) / 365.25) > 0)
    precip = np.where(rng.random(n) < p_rain, rng.gamma(1.2, 0.25, n), 0.0)

    rh = np.clip(72 + 12 * np.sin(2 * np.pi * (doy - 180) / 365.25) + rng.normal(0, 8, n), 35, 99)
    wind = np.clip(rng.lognormal(1.2, 0.45, n), 0.5, 25)
    dewpoint = tmin - rng.uniform(0, 8, n) * (1.0 if station.region != "south-central" else 0.7)
    dewpoint = np.minimum(dewpoint, tmin - 0.5)

    df = pd.DataFrame(
        {
            "station_id": station.id,
            "date": days.date,
            "tmin_f": np.round(tmin, 2),
            "tmax_f": np.round(tmax, 2),
            "tmean_f": np.round(tmean, 2),
            "precip_in": np.round(precip, 3),
            "rh_mean": np.round(rh, 1),
            "wind_mean_mph": np.round(wind, 2),
            "dewpoint_f": np.round(dewpoint, 2),
            "solar_mj": np.round(np.clip(12 + 8 * np.sin(2 * np.pi * (doy - 80) / 365.25) + rng.normal(0, 2, n), 2, 28), 2),
            "source": "synthetic_fl_climatology",
        }
    )
    return df


def generate_all_stations(
    start: date = date(2008, 1, 1),
    end: date | None = None,
) -> pd.DataFrame:
    frames = [
        generate_station_history(st, start=start, end=end, seed=i * 17 + 3)
        for i, st in enumerate(STATIONS.values())
    ]
    return pd.concat(frames, ignore_index=True)
