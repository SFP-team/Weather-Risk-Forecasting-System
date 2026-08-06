"""National Weather Service API (api.weather.gov) helpers."""

from __future__ import annotations

from typing import Any

import httpx

from blueberry_common.config import get_settings
from blueberry_common.stations import Station


def _headers() -> dict[str, str]:
    return {
        "User-Agent": get_settings().nws_user_agent,
        "Accept": "application/geo+json",
    }


def fetch_point_forecast(station: Station) -> dict[str, Any] | None:
    settings = get_settings()
    if not settings.use_live_nws:
        return None
    try:
        with httpx.Client(timeout=20.0, headers=_headers(), follow_redirects=True) as client:
            pt = client.get(f"https://api.weather.gov/points/{station.lat},{station.lon}")
            pt.raise_for_status()
            props = pt.json()["properties"]
            forecast_url = props.get("forecast")
            hourly_url = props.get("forecastHourly")
            out: dict[str, Any] = {
                "gridId": props.get("gridId"),
                "forecast": None,
                "hourly": None,
                "alerts": [],
            }
            if forecast_url:
                fr = client.get(forecast_url)
                if fr.status_code == 200:
                    out["forecast"] = fr.json()
            if hourly_url:
                hr = client.get(hourly_url)
                if hr.status_code == 200:
                    out["hourly"] = hr.json()
            # Active alerts
            al = client.get(
                "https://api.weather.gov/alerts/active",
                params={"point": f"{station.lat},{station.lon}"},
            )
            if al.status_code == 200:
                out["alerts"] = al.json().get("features") or []
            return out
    except Exception:
        return None


def summarize_nws_for_tonight(nws: dict[str, Any] | None) -> dict[str, Any]:
    """Extract rough tonight Tmin, wind, dewpoint-ish from NWS hourly if present."""
    if not nws or not nws.get("hourly"):
        return {}
    periods = (nws["hourly"].get("properties") or {}).get("periods") or []
    if not periods:
        return {}
    # Next 18 hours overnight-ish
    temps = []
    winds = []
    for p in periods[:18]:
        t = p.get("temperature")
        if t is not None:
            temps.append(float(t))
        w = p.get("windSpeed") or ""
        # e.g. "5 mph"
        try:
            winds.append(float(str(w).split()[0]))
        except Exception:
            pass
    alerts = []
    for a in nws.get("alerts") or []:
        props = a.get("properties") or {}
        event = props.get("event") or ""
        if any(k in event.lower() for k in ("freeze", "frost", "cold", "winter")):
            alerts.append(event)
    return {
        "tmin_f": min(temps) if temps else None,
        "tmax_f": max(temps) if temps else None,
        "wind_mph": (sum(winds) / len(winds)) if winds else None,
        "alerts": alerts,
        "source": "NWS",
    }
