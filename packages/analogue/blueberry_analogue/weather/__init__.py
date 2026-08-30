"""Queryable base-weather layer.

Store daily temperature, rain, solar, humidity. Derive chill, freeze,
harvest rain, DLI, and production-system labels on the fly.
"""

from blueberry_analogue.weather.daily import (
    DEFAULT_END_YEAR,
    DEFAULT_START_YEAR,
    fallback_daily_years,
    fetch_nasa_power_daily,
)
from blueberry_analogue.weather.store import DailySeries, load_daily_series, weather_store

__all__ = [
    "DEFAULT_END_YEAR",
    "DEFAULT_START_YEAR",
    "DailySeries",
    "fallback_daily_years",
    "fetch_nasa_power_daily",
    "load_daily_series",
    "weather_store",
]
