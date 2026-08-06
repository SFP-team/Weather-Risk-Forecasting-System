from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterator

from blueberry_common.config import get_settings


def _db_path() -> Path:
    settings = get_settings()
    # sqlite:///./path or sqlite:////abs
    url = settings.database_url
    if url.startswith("sqlite:///"):
        path = url.replace("sqlite:///", "", 1)
        p = Path(path)
        if not p.is_absolute():
            p = settings.processed_dir.parent.parent / p  # unlikely
            # Prefer explicit processed path
            p = get_settings().processed_dir / "blueberry_risk.db"
        return p
    return get_settings().processed_dir / "blueberry_risk.db"


def get_db_path() -> Path:
    settings = get_settings()
    settings.ensure_dirs()
    return settings.processed_dir / "blueberry_risk.db"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    path = get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS stations (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  county TEXT NOT NULL,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  elev_m REAL,
  fawn_id TEXT,
  region TEXT
);

CREATE TABLE IF NOT EXISTS farms (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  county TEXT NOT NULL,
  lat REAL NOT NULL,
  lon REAL NOT NULL,
  nearest_station_id TEXT NOT NULL,
  cultivars_json TEXT NOT NULL,
  chill_requirement_hours INTEGER NOT NULL,
  production_system TEXT NOT NULL,
  phenology_stage TEXT NOT NULL,
  system_rate_in_per_hr REAL DEFAULT 0.2,
  cold_spot_bias_f REAL DEFAULT 0.0,
  irrigation_freeze_protection INTEGER DEFAULT 1,
  acres REAL DEFAULT 20.0,
  FOREIGN KEY (nearest_station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS observations_daily (
  station_id TEXT NOT NULL,
  date TEXT NOT NULL,
  tmin_f REAL,
  tmax_f REAL,
  tmean_f REAL,
  precip_in REAL,
  rh_mean REAL,
  wind_mean_mph REAL,
  dewpoint_f REAL,
  solar_mj REAL,
  source TEXT,
  PRIMARY KEY (station_id, date),
  FOREIGN KEY (station_id) REFERENCES stations(id)
);

CREATE TABLE IF NOT EXISTS features_daily (
  station_id TEXT NOT NULL,
  date TEXT NOT NULL,
  chill_hours REAL,
  freeze_le_32 INTEGER,
  freeze_le_28 INTEGER,
  freeze_le_24 INTEGER,
  gdd_base50 REAL,
  rh_hours_ge_90 REAL,
  precip_in REAL,
  tmin_f REAL,
  tmax_f REAL,
  PRIMARY KEY (station_id, date)
);

CREATE TABLE IF NOT EXISTS forecast_runs (
  id TEXT PRIMARY KEY,
  created_at TEXT NOT NULL,
  model_version TEXT NOT NULL,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS forecasts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  farm_id TEXT NOT NULL,
  valid_start TEXT NOT NULL,
  valid_end TEXT NOT NULL,
  variable TEXT NOT NULL,
  value REAL,
  p10 REAL,
  p50 REAL,
  p90 REAL,
  method TEXT,
  confidence TEXT,
  FOREIGN KEY (run_id) REFERENCES forecast_runs(id)
);

CREATE TABLE IF NOT EXISTS risk_events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  run_id TEXT NOT NULL,
  farm_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  window_start TEXT NOT NULL,
  window_end TEXT NOT NULL,
  probability REAL NOT NULL,
  severity INTEGER NOT NULL,
  advisory_text TEXT NOT NULL,
  drivers_json TEXT,
  FOREIGN KEY (run_id) REFERENCES forecast_runs(id)
);

CREATE TABLE IF NOT EXISTS tonight_cache (
  farm_id TEXT PRIMARY KEY,
  payload_json TEXT NOT NULL,
  generated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""


def init_db() -> Path:
    with connect() as conn:
        conn.executescript(SCHEMA_SQL)
    return get_db_path()


def upsert_station(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO stations (id, name, county, lat, lon, elev_m, fawn_id, region)
        VALUES (:id, :name, :county, :lat, :lon, :elev_m, :fawn_id, :region)
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name, county=excluded.county, lat=excluded.lat,
          lon=excluded.lon, elev_m=excluded.elev_m, fawn_id=excluded.fawn_id,
          region=excluded.region
        """,
        row,
    )


def upsert_farm(conn: sqlite3.Connection, row: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT INTO farms (
          id, name, county, lat, lon, nearest_station_id, cultivars_json,
          chill_requirement_hours, production_system, phenology_stage,
          system_rate_in_per_hr, cold_spot_bias_f, irrigation_freeze_protection, acres
        ) VALUES (
          :id, :name, :county, :lat, :lon, :nearest_station_id, :cultivars_json,
          :chill_requirement_hours, :production_system, :phenology_stage,
          :system_rate_in_per_hr, :cold_spot_bias_f, :irrigation_freeze_protection, :acres
        )
        ON CONFLICT(id) DO UPDATE SET
          name=excluded.name, county=excluded.county, lat=excluded.lat, lon=excluded.lon,
          nearest_station_id=excluded.nearest_station_id, cultivars_json=excluded.cultivars_json,
          chill_requirement_hours=excluded.chill_requirement_hours,
          production_system=excluded.production_system, phenology_stage=excluded.phenology_stage,
          system_rate_in_per_hr=excluded.system_rate_in_per_hr,
          cold_spot_bias_f=excluded.cold_spot_bias_f,
          irrigation_freeze_protection=excluded.irrigation_freeze_protection,
          acres=excluded.acres
        """,
        row,
    )


def set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    conn.execute(
        "INSERT INTO meta(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
        (key, value),
    )


def get_meta(conn: sqlite3.Connection, key: str, default: str | None = None) -> str | None:
    cur = conn.execute("SELECT value FROM meta WHERE key=?", (key,))
    row = cur.fetchone()
    return row["value"] if row else default


def json_dumps(obj: Any) -> str:
    def default(o: Any) -> Any:
        if isinstance(o, (datetime, date)):
            return o.isoformat()
        raise TypeError(type(o))

    return json.dumps(obj, default=default)
