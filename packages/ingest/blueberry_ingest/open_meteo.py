"""Open-Meteo historical + forecast helpers (optional live)."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

import httpx
import pandas as pd

from blueberry_common.config import get_settings
from blueberry_common.stations import Station


def fetch_forecast(station: Station, days: int = 7) -> pd.DataFrame | None:
    settings = get_settings()
    if not settings.use_live_open_meteo:
        return None
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": station.lat,
        "longitude": station.lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/New_York",
        "forecast_days": min(days, 16),
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    daily = data.get("daily") or {}
    if not daily.get("time"):
        return None

    df = pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]).date,
            "tmax_f": daily.get("temperature_2m_max"),
            "tmin_f": daily.get("temperature_2m_min"),
            "precip_in": daily.get("precipitation_sum"),
            "wind_mean_mph": daily.get("windspeed_10m_max"),
            "rh_mean": daily.get("relative_humidity_2m_mean"),
            "station_id": station.id,
            "source": "open-meteo-forecast",
        }
    )
    return df


def fetch_recent_history(station: Station, days: int = 90) -> pd.DataFrame | None:
    settings = get_settings()
    if not settings.use_live_open_meteo:
        return None
    end = date.today()
    start = end - timedelta(days=days)
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": station.lat,
        "longitude": station.lon,
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max,relative_humidity_2m_mean",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "America/New_York",
    }
    try:
        with httpx.Client(timeout=30.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    daily = data.get("daily") or {}
    if not daily.get("time"):
        return None

    tmin = daily.get("temperature_2m_min")
    tmax = daily.get("temperature_2m_max")
    tmean = None
    if tmin and tmax:
        tmean = [(a + b) / 2 if a is not None and b is not None else None for a, b in zip(tmin, tmax)]

    return pd.DataFrame(
        {
            "date": pd.to_datetime(daily["time"]).date,
            "tmin_f": tmin,
            "tmax_f": tmax,
            "tmean_f": tmean,
            "precip_in": daily.get("precipitation_sum"),
            "wind_mean_mph": daily.get("windspeed_10m_max"),
            "rh_mean": daily.get("relative_humidity_2m_mean"),
            "dewpoint_f": None,
            "solar_mj": None,
            "station_id": station.id,
            "source": "open-meteo-archive",
        }
    )


def fetch_hourly_tonight(station: Station) -> list[dict[str, Any]] | None:
    """Hourly next ~48h for freeze decision support."""
    settings = get_settings()
    if not settings.use_live_open_meteo:
        return None
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": station.lat,
        "longitude": station.lon,
        "hourly": "temperature_2m,dewpoint_2m,windspeed_10m,relative_humidity_2m",
        "temperature_unit": "fahrenheit",
        "windspeed_unit": "mph",
        "timezone": "America/New_York",
        "forecast_days": 2,
    }
    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
    except Exception:
        return None

    hourly = data.get("hourly") or {}
    times = hourly.get("time") or []
    out = []
    for i, t in enumerate(times):
        out.append(
            {
                "time": t,
                "temp_f": (hourly.get("temperature_2m") or [None])[i],
                "dewpoint_f": (hourly.get("dewpoint_2m") or [None])[i],
                "wind_mph": (hourly.get("windspeed_10m") or [None])[i],
                "rh": (hourly.get("relative_humidity_2m") or [None])[i],
            }
        )
    return out
