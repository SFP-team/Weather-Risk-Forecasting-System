"""Small-first climate ingest.

Operational source for v0 is NASA POWER point climatology (CC-BY).
CHELSA / CHIRPS / ERA5-Land / AgERA5 are adapters: extract from local
rasters if present, otherwise record a pending request. SoilGrids and
Copernicus DEM are point REST extracts.

No global hourly cube is downloaded here.
"""

from __future__ import annotations

import calendar
import json
import math
import time
from pathlib import Path
from typing import Any

import httpx
import numpy as np
import pandas as pd

from blueberry_analogue.paths import CLIM_CACHE, LAND_CACHE, ensure_data_dirs

POWER_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
POWER_DAILY = "https://power.larc.nasa.gov/api/temporal/daily/point"
POWER_PARAMS = "T2M_MIN,T2M_MAX,T2M,RH2M,PRECTOTCORR,ALLSKY_SFC_SW_DWN,WS2M,T2MDEW"
SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
DEM_URL = "https://api.opentopodata.org/v1/copernicus-30m"
USER_AGENT = "BlueberryAnalogue/0.1 (site-selection research; not a farm decision)"

MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]


def _cache_path(kind: str, site_id: str) -> Path:
    ensure_data_dirs()
    folder = CLIM_CACHE if kind != "land" else LAND_CACHE
    return folder / f"{kind}_{site_id}.json"


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def fallback_climatology(lat: float, lon: float, elev_m: float = 50.0) -> dict[str, list[float]]:
    """Deterministic physics-ish monthly climate when APIs are offline.

    Used for tests and air-gapped builds. Labeled source=fallback, never sold as CHELSA.
    """
    lat_r = math.radians(lat)
    # rough annual mean
    t_ann = 26.0 * math.cos(lat_r) - 0.006 * elev_m + 2.0 * math.cos(math.radians(lon / 4.0))
    amp = 8.0 + 14.0 * abs(math.sin(lat_r))
    if lat < 0:
        phase = 6
    else:
        phase = 0
    tmin, tmax, rh, precip, sw, wind, tdew = [], [], [], [], [], [], []
    for m in range(12):
        ang = 2 * math.pi * ((m - phase) - 0.5) / 12.0
        t = t_ann - amp * math.cos(ang)
        dtr = 8.0 + 4.0 * abs(math.sin(lat_r))
        # Peru coast: dry, bright, muted DTR
        arid = 1.0 if (abs(lat) < 18 and -82 < lon < -70) else 0.0
        tmin.append(t - dtr / 2 - 2 * arid)
        tmax.append(t + dtr / 2 + 1 * arid)
        rh.append(max(35.0, 80.0 - 25.0 * arid - 8.0 * abs(math.sin(lat_r))))
        precip.append(max(0.0, (90.0 * math.cos(lat_r) ** 2) * (0.6 + 0.4 * math.cos(ang)) * (1 - 0.92 * arid)))
        sw.append(max(6.0, 12.0 + 10.0 * math.cos(lat_r) * (0.7 + 0.3 * math.cos(ang)) + 4 * arid))
        wind.append(2.4)
        tdew.append(tmin[-1] - 1.5)
    return {
        "tmin_c": tmin,
        "tmax_c": tmax,
        "tmean_c": [0.5 * (a + b) for a, b in zip(tmin, tmax)],
        "rh": rh,
        "precip_mm": precip,
        "sw_mj": sw,
        "wind_ms": wind,
        "tdew_c": tdew,
    }


def _power_month_map(block: dict[str, Any], key: str) -> list[float]:
    raw = block.get(key) or {}
    out = []
    for name in MONTHS:
        val = raw.get(name, raw.get(name.title()))
        out.append(float(val) if val is not None and val != -999 else float("nan"))
    return out


def fetch_nasa_power_climatology(lat: float, lon: float, timeout: float = 40.0) -> dict[str, Any] | None:
    params = {
        "parameters": POWER_PARAMS,
        "community": "AG",
        "longitude": f"{lon:.4f}",
        "latitude": f"{lat:.4f}",
        "format": "JSON",
    }
    headers = {"User-Agent": USER_AGENT}
    try:
        with httpx.Client(timeout=timeout, headers=headers, follow_redirects=True) as client:
            r = client.get(POWER_URL, params=params)
            r.raise_for_status()
            body = r.json()
    except Exception:
        return None
    props = body.get("properties", {}).get("parameter", {})
    if not props:
        return None
    return {
        "source": "nasa_power_climatology",
        "tmin_c": _power_month_map(props, "T2M_MIN"),
        "tmax_c": _power_month_map(props, "T2M_MAX"),
        "tmean_c": _power_month_map(props, "T2M"),
        "rh": _power_month_map(props, "RH2M"),
        "precip_mm": _power_month_map(props, "PRECTOTCORR"),
        "sw_mj": _power_month_map(props, "ALLSKY_SFC_SW_DWN"),
        "wind_ms": _power_month_map(props, "WS2M"),
        "tdew_c": _power_month_map(props, "T2MDEW"),
    }


def fetch_soilgrids(lat: float, lon: float, timeout: float = 30.0) -> dict[str, Any]:
    params = {
        "lon": lon,
        "lat": lat,
        "property": ["phh2o", "soc", "clay", "bdod"],
        "depth": "0-5cm",
        "value": "mean",
    }
    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
            r = client.get(SOILGRIDS_URL, params=params)
            r.raise_for_status()
            layers = r.json().get("properties", {}).get("layers", [])
    except Exception:
        return {"source": "soilgrids_unavailable", "ph": None, "soc": None, "clay": None, "bdod": None}
    out: dict[str, Any] = {"source": "soilgrids_rest"}
    for layer in layers:
        name = layer.get("name")
        depths = layer.get("depths") or []
        if not depths:
            continue
        values = depths[0].get("values") or {}
        mean = values.get("mean")
        if name == "phh2o" and mean is not None:
            out["ph"] = mean / 10.0  # SoilGrids pH is pH*10
        elif name == "soc":
            out["soc"] = mean
        elif name == "clay":
            out["clay"] = mean / 10.0 if mean is not None else None
        elif name == "bdod":
            out["bdod"] = mean
    return out


def fetch_dem(lat: float, lon: float, timeout: float = 20.0) -> dict[str, Any]:
    try:
        with httpx.Client(timeout=timeout, headers={"User-Agent": USER_AGENT}, follow_redirects=True) as client:
            r = client.get(DEM_URL, params={"locations": f"{lat},{lon}"})
            r.raise_for_status()
            results = r.json().get("results") or []
    except Exception:
        return {"source": "dem_unavailable", "elev_m": None}
    if not results or results[0].get("elevation") is None:
        return {"source": "dem_unavailable", "elev_m": None}
    return {"source": "opentopodata_copernicus30", "elev_m": float(results[0]["elevation"])}


def chelsa_local_extract(_lat: float, _lon: float) -> dict[str, Any]:
    """Read local CHELSA GeoTIFFs if an operator has staged them.

    Staging path: data/analogue/chelsa/*.tif
    We never download the global 1 km cube from this function.
    """
    root = LAND_CACHE.parent / "chelsa"
    return {
        "source": "chelsa_local_missing" if not root.exists() else "chelsa_local_present",
        "available": root.exists(),
        "note": "Place CHELSA v2.1 monthly GeoTIFFs under data/analogue/chelsa to enable 1 km extracts.",
    }


def chirps_local_extract(_lat: float, _lon: float) -> dict[str, Any]:
    root = LAND_CACHE.parent / "chirps"
    return {
        "source": "chirps_local_missing" if not root.exists() else "chirps_local_present",
        "available": root.exists(),
        "note": "Place CHIRPS v3 monthly files under data/analogue/chirps for the rain fingerprint.",
    }


def era5land_request_payload(points: list[tuple[float, float]], years: tuple[int, int] = (2014, 2024)) -> dict[str, Any]:
    """CDS request skeleton for hourly ERA5-Land at shortlisted cells only."""
    lats = [p[0] for p in points]
    lons = [p[1] for p in points]
    pad = 0.15
    return {
        "dataset": "reanalysis-era5-land",
        "variable": [
            "2m_temperature",
            "2m_dewpoint_temperature",
            "surface_solar_radiation_downwards",
            "10m_u_component_of_wind",
            "10m_v_component_of_wind",
        ],
        "year": list(range(years[0], years[1] + 1)),
        "area": [
            max(lats) + pad,
            min(lons) - pad,
            min(lats) - pad,
            max(lons) + pad,
        ],
        "note": "De-accumulate solar from 00 UTC. Do not use ERA5-Land precip as the rain fingerprint. Bias-correct Tmin to stations before selling a number.",
    }


def agera5_request_payload(points: list[tuple[float, float]]) -> dict[str, Any]:
    return {
        "dataset": "sis-agrometeorological-indicators",
        "variable": ["2m_temperature_min", "2m_temperature_max", "vapour_pressure", "solar_radiation_flux", "et0"],
        "points": len(points),
        "note": "Daily AgERA5 is the cheap feature table. Not a chill substitute.",
    }


def monthly_to_daily(clim: dict[str, list[float]], year: int = 2018) -> pd.DataFrame:
    rows = []
    for month in range(1, 13):
        days = calendar.monthrange(year, month)[1]
        i = month - 1
        for day in range(1, days + 1):
            rows.append(
                {
                    "date": pd.Timestamp(year=year, month=month, day=day),
                    "tmin_c": clim["tmin_c"][i],
                    "tmax_c": clim["tmax_c"][i],
                    "rh": clim["rh"][i],
                    "precip_mm": clim["precip_mm"][i] / days,
                    "sw_mj": clim["sw_mj"][i],
                    "wind_ms": clim.get("wind_ms", [2.4] * 12)[i],
                    "tdew_c": clim.get("tdew_c", clim["tmin_c"])[i],
                }
            )
    return pd.DataFrame(rows)


def fetch_site_climate(
    site_id: str,
    lat: float,
    lon: float,
    live: bool = True,
    sleep_s: float = 0.35,
    land_live: bool = False,
    refresh: bool = False,
) -> dict[str, Any]:
    cached = None if refresh else _read_json(_cache_path("climate", site_id))
    if cached and cached.get("climatology") and not refresh:
        return cached

    clim = None
    source = "fallback"
    if live:
        clim = fetch_nasa_power_climatology(lat, lon)
        if clim:
            source = "nasa_power_climatology"
        if sleep_s:
            time.sleep(sleep_s)
    if clim is None:
        clim = fallback_climatology(lat, lon)
        clim["source"] = "fallback"
        source = "fallback"

    land = _read_json(_cache_path("land", site_id)) or {}
    if land_live and not land:
        dem = fetch_dem(lat, lon)
        soil = fetch_soilgrids(lat, lon)
        land = {**dem, **{f"soil_{k}": v for k, v in soil.items()}}
        _write_json(_cache_path("land", site_id), land)
        time.sleep(sleep_s)

    payload = {
        "site_id": site_id,
        "lat": lat,
        "lon": lon,
        "source": source,
        "climatology": {k: v for k, v in clim.items() if k != "source"},
        "chelsa": chelsa_local_extract(lat, lon),
        "chirps": chirps_local_extract(lat, lon),
        "land": land,
        "trust_notes": _trust_notes(source, land, lat),
    }
    _write_json(_cache_path("climate", site_id), payload)
    return payload


def _trust_notes(source: str, land: dict[str, Any], lat: float) -> list[str]:
    notes = []
    if source == "fallback":
        notes.append("Climate is a lat/lon fallback, not NASA POWER or CHELSA. Do not sell this number.")
    elif source == "nasa_power_climatology":
        notes.append("NASA POWER monthly climatology. Solar is ~1 degree. Not a 1 km farm climate.")
    if abs(lat) < 15:
        notes.append("Tropical or equatorial pixel. Mountain rain and fog drip are untrusted (Hemp 2024).")
    if not land.get("elev_m"):
        notes.append("No DEM yet. Frost-pocket / TWI not scored.")
    if land.get("soil_ph") is None:
        notes.append("No SoilGrids pH. Soil gate is skipped unless the system is substrate.")
    notes.append("If a 10-year station disagrees on chill or harvest rain, this pixel is untrusted.")
    return notes


def load_or_build_climatology(
    sites,
    live: bool = True,
    limit: int | None = None,
    refresh: bool = False,
) -> dict[str, dict[str, Any]]:
    out = {}
    use = list(sites) if limit is None else list(sites)[:limit]
    if live and len(use) > 4:
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def one(site):
            return site.site_id, fetch_site_climate(
                site.site_id,
                site.lat,
                site.lon,
                live=True,
                sleep_s=0.0,
                land_live=False,
                refresh=refresh,
            )

        with ThreadPoolExecutor(max_workers=6) as pool:
            futs = [pool.submit(one, site) for site in use]
            for fut in as_completed(futs):
                sid, payload = fut.result()
                out[sid] = payload
        return out
    for site in use:
        out[site.site_id] = fetch_site_climate(
            site.site_id, site.lat, site.lon, live=live, refresh=refresh
        )
    return out


def climate_daily(payload: dict[str, Any], year: int = 2018) -> pd.DataFrame:
    return monthly_to_daily(payload["climatology"], year=year)
