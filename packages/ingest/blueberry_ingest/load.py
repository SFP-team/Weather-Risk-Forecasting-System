"""Load observations into SQLite."""

from __future__ import annotations

from datetime import date

import pandas as pd

from blueberry_common.db import connect, init_db, upsert_station
from blueberry_common.stations import STATIONS
from blueberry_ingest.synthetic import generate_all_stations
from blueberry_ingest.open_meteo import fetch_recent_history


def seed_stations() -> None:
    init_db()
    with connect() as conn:
        for st in STATIONS.values():
            upsert_station(
                conn,
                {
                    "id": st.id,
                    "name": st.name,
                    "county": st.county,
                    "lat": st.lat,
                    "lon": st.lon,
                    "elev_m": st.elev_m,
                    "fawn_id": st.fawn_id,
                    "region": st.region,
                },
            )


def write_observations(df: pd.DataFrame) -> int:
    init_db()
    if df.empty:
        return 0
    cols = [
        "station_id",
        "date",
        "tmin_f",
        "tmax_f",
        "tmean_f",
        "precip_in",
        "rh_mean",
        "wind_mean_mph",
        "dewpoint_f",
        "solar_mj",
        "source",
    ]
    for c in cols:
        if c not in df.columns:
            df[c] = None
    rows = df[cols].copy()
    rows["date"] = rows["date"].astype(str)
    with connect() as conn:
        conn.executemany(
            """
            INSERT INTO observations_daily (
              station_id, date, tmin_f, tmax_f, tmean_f, precip_in,
              rh_mean, wind_mean_mph, dewpoint_f, solar_mj, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(station_id, date) DO UPDATE SET
              tmin_f=excluded.tmin_f, tmax_f=excluded.tmax_f, tmean_f=excluded.tmean_f,
              precip_in=excluded.precip_in, rh_mean=excluded.rh_mean,
              wind_mean_mph=excluded.wind_mean_mph, dewpoint_f=excluded.dewpoint_f,
              solar_mj=excluded.solar_mj, source=excluded.source
            """,
            list(rows.itertuples(index=False, name=None)),
        )
    return len(rows)


def load_synthetic_history(start: date = date(2008, 1, 1), end: date | None = None) -> int:
    seed_stations()
    df = generate_all_stations(start=start, end=end)
    # Persist sample parquet for inspection
    from blueberry_common.config import get_settings

    settings = get_settings()
    settings.ensure_dirs()
    df.to_csv(settings.sample_dir / "observations_daily.csv", index=False)
    return write_observations(df)


def merge_live_recent(days: int = 60) -> int:
    """Overlay recent Open-Meteo archive onto synthetic where available."""
    seed_stations()
    frames = []
    for st in STATIONS.values():
        df = fetch_recent_history(st, days=days)
        if df is not None and not df.empty:
            frames.append(df)
    if not frames:
        return 0
    return write_observations(pd.concat(frames, ignore_index=True))


def read_observations(station_id: str | None = None) -> pd.DataFrame:
    init_db()
    with connect() as conn:
        if station_id:
            rows = conn.execute(
                "SELECT * FROM observations_daily WHERE station_id=? ORDER BY date",
                (station_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM observations_daily ORDER BY station_id, date").fetchall()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df
