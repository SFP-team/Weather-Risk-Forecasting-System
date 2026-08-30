"""SQLite point store for daily base weather.

The product is a queryable database, not a global hourly cube. Fetch a
point once, keep it, derive the rest on demand.
"""

from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from blueberry_analogue.climate.fetch import _read_json, _cache_path
from blueberry_analogue.paths import WEATHER_DB, ensure_data_dirs
from blueberry_analogue.weather.daily import (
    DEFAULT_END_YEAR,
    DEFAULT_START_YEAR,
    fallback_daily_years,
    fetch_nasa_power_daily,
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS points (
  point_id TEXT PRIMARY KEY,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  name TEXT,
  kind TEXT,
  source TEXT
);
CREATE TABLE IF NOT EXISTS daily (
  point_id TEXT NOT NULL,
  date TEXT NOT NULL,
  tmin_c REAL,
  tmax_c REAL,
  tmean_c REAL,
  precip_mm REAL,
  sw_mj REAL,
  rh REAL,
  wind_ms REAL,
  tdew_c REAL,
  PRIMARY KEY (point_id, date)
);
CREATE INDEX IF NOT EXISTS idx_points_latlon ON points(lat, lon);
"""


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def point_id_for(lat: float, lon: float) -> str:
    return f"pt_{lat:.3f}_{lon:.3f}"


@dataclass
class DailySeries:
    point_id: str
    lat: float
    lon: float
    frame: pd.DataFrame
    source: str
    name: str = ""
    nearest_km: float = 0.0
    trust_notes: list[str] | None = None

    @property
    def years(self) -> tuple[int, int]:
        if self.frame.empty:
            return (0, 0)
        dates = pd.to_datetime(self.frame["date"])
        return (int(dates.min().year), int(dates.max().year))

    @property
    def n_days(self) -> int:
        return int(len(self.frame))


class WeatherStore:
    def __init__(self, path: Path | None = None) -> None:
        ensure_data_dirs()
        self.path = path or WEATHER_DB
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as con:
            con.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def put_series(
        self,
        point_id: str,
        lat: float,
        lon: float,
        frame: pd.DataFrame,
        source: str,
        name: str = "",
        kind: str = "query",
    ) -> None:
        work = frame.copy()
        work["date"] = pd.to_datetime(work["date"]).dt.strftime("%Y-%m-%d")
        rows = [
            (
                point_id,
                row["date"],
                float(row.get("tmin_c", float("nan"))),
                float(row.get("tmax_c", float("nan"))),
                float(row.get("tmean_c", float("nan"))),
                float(row.get("precip_mm", float("nan"))),
                float(row.get("sw_mj", float("nan"))),
                float(row.get("rh", float("nan"))),
                float(row.get("wind_ms", float("nan"))),
                float(row.get("tdew_c", float("nan"))),
            )
            for row in work.to_dict(orient="records")
        ]
        with self._connect() as con:
            con.execute(
                "INSERT OR REPLACE INTO points(point_id, lat, lon, name, kind, source) VALUES (?,?,?,?,?,?)",
                (point_id, lat, lon, name, kind, source),
            )
            con.executemany(
                """INSERT OR REPLACE INTO daily(
                    point_id, date, tmin_c, tmax_c, tmean_c, precip_mm, sw_mj, rh, wind_ms, tdew_c
                ) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                rows,
            )
            con.commit()

    def get_series(self, point_id: str) -> DailySeries | None:
        with self._connect() as con:
            point = con.execute("SELECT * FROM points WHERE point_id = ?", (point_id,)).fetchone()
            if point is None:
                return None
            rows = con.execute(
                "SELECT date, tmin_c, tmax_c, tmean_c, precip_mm, sw_mj, rh, wind_ms, tdew_c "
                "FROM daily WHERE point_id = ? ORDER BY date",
                (point_id,),
            ).fetchall()
        if not rows:
            return None
        frame = pd.DataFrame([dict(r) for r in rows])
        frame["date"] = pd.to_datetime(frame["date"])
        return DailySeries(
            point_id=point["point_id"],
            lat=float(point["lat"]),
            lon=float(point["lon"]),
            frame=frame,
            source=str(point["source"] or ""),
            name=str(point["name"] or ""),
        )

    def nearest(self, lat: float, lon: float) -> tuple[str, float] | None:
        with self._connect() as con:
            points = con.execute("SELECT point_id, lat, lon FROM points").fetchall()
        if not points:
            return None
        best = None
        for row in points:
            km = _haversine_km(lat, lon, float(row["lat"]), float(row["lon"]))
            if best is None or km < best[1]:
                best = (row["point_id"], km)
        return best

    def point_count(self) -> int:
        with self._connect() as con:
            row = con.execute("SELECT COUNT(*) AS n FROM points").fetchone()
        return int(row["n"]) if row else 0

    def known_ids(self) -> set[str]:
        with self._connect() as con:
            rows = con.execute("SELECT point_id FROM points").fetchall()
        return {str(r["point_id"]) for r in rows}

    def complete_ids(self, min_days: int = 300) -> set[str]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT point_id, COUNT(*) AS n FROM daily GROUP BY point_id HAVING n >= ?",
                (min_days,),
            ).fetchall()
        return {str(r["point_id"]) for r in rows}


_STORE: WeatherStore | None = None


def weather_store(path: Path | None = None) -> WeatherStore:
    global _STORE
    if path is not None:
        return WeatherStore(path)
    if _STORE is None:
        _STORE = WeatherStore()
    return _STORE


def _climatology_for_nearby_site(lat: float, lon: float) -> tuple[dict[str, Any], Any] | None:
    try:
        from blueberry_analogue.sites import load_sites
    except Exception:
        return None
    best = None
    for site in load_sites():
        km = _haversine_km(lat, lon, site.lat, site.lon)
        if best is None or km < best[0]:
            best = (km, site)
    if best is None or best[0] > 25.0:
        return None
    site = best[1]
    cached = _read_json(_cache_path("climate", site.site_id))
    if not cached or not cached.get("climatology"):
        return None
    return cached, site


def load_daily_series(
    lat: float,
    lon: float,
    *,
    live: bool = False,
    start_year: int = DEFAULT_START_YEAR,
    end_year: int = DEFAULT_END_YEAR,
    store: WeatherStore | None = None,
    persist: bool = True,
    max_reuse_km: float = 15.0,
    name: str = "",
) -> DailySeries:
    """Return last-decade daily weather for a coordinate.

    Order: sqlite hit → live NASA POWER daily → nearby POWER monthly
    expanded to years → lat/lon fallback. Always returns a series.
    """
    db = store or weather_store()
    pid = point_id_for(lat, lon)
    cached = db.get_series(pid)
    if cached is not None and cached.n_days > 200:
        cached.nearest_km = 0.0
        return cached
    near = db.nearest(lat, lon)
    if near and near[1] <= max_reuse_km:
        reused = db.get_series(near[0])
        if reused is not None and reused.n_days > 200:
            reused.nearest_km = near[1]
            notes = list(reused.trust_notes or [])
            notes.append(f"Reused stored point {near[0]} at {near[1]:.1f} km.")
            reused.trust_notes = notes
            return reused

    notes: list[str] = []
    frame = None
    source = "fallback_daily"
    if live:
        frame = fetch_nasa_power_daily(lat, lon, start_year, end_year)
        if frame is not None and len(frame) > 200:
            source = "nasa_power_daily"
            notes.append(
                f"NASA POWER daily {start_year}–{end_year}. Dated winters, not a 30-year climatology mean."
            )

    if frame is None:
        nearby = _climatology_for_nearby_site(lat, lon)
        if nearby:
            payload, site = nearby
            frame = fallback_daily_years(
                lat, lon, start_year, end_year, climatology=payload["climatology"]
            )
            source = "nasa_power_climatology_expanded"
            notes.append(
                f"No dated daily archive yet. Expanded NASA POWER monthly climatology "
                f"from {site.site_id} ({site.name}) with seeded year noise. "
                f"Not a real 10-year winter record."
            )
            if not name:
                name = site.name
        else:
            frame = fallback_daily_years(lat, lon, start_year, end_year)
            source = "fallback_daily"
            notes.append(
                "Climate is a lat/lon fallback expanded to 10 years. Do not sell this number."
            )

    series = DailySeries(
        point_id=pid,
        lat=lat,
        lon=lon,
        frame=frame,
        source=source,
        name=name,
        nearest_km=0.0,
        trust_notes=notes,
    )
    if persist and source == "nasa_power_daily":
        db.put_series(pid, lat, lon, frame, source, name=name, kind="query")
    return series
