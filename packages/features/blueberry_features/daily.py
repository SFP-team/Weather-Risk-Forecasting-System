from __future__ import annotations

import pandas as pd

from blueberry_common.db import connect, init_db
from blueberry_features.chill import chill_hours_from_daily
from blueberry_ingest.load import read_observations


def build_features_from_obs(obs: pd.DataFrame) -> pd.DataFrame:
    if obs.empty:
        return pd.DataFrame()
    rows = []
    for _, r in obs.iterrows():
        tmin = r.get("tmin_f")
        tmax = r.get("tmax_f")
        chill = chill_hours_from_daily(
            float(tmin) if tmin is not None and pd.notna(tmin) else float("nan"),
            float(tmax) if tmax is not None and pd.notna(tmax) else float("nan"),
        )
        gdd = 0.0
        if tmin is not None and tmax is not None and pd.notna(tmin) and pd.notna(tmax):
            tmean = (float(tmin) + float(tmax)) / 2.0
            gdd = max(0.0, tmean - 50.0)
        rh = r.get("rh_mean")
        # proxy: if RH mean high, approximate hours >= 90
        rh_hours = 0.0
        if rh is not None and pd.notna(rh):
            rh_hours = max(0.0, min(24.0, (float(rh) - 70.0) * 0.8))
        precip = r.get("precip_in") or 0.0
        rows.append(
            {
                "station_id": r["station_id"],
                "date": r["date"],
                "chill_hours": round(chill, 2),
                "freeze_le_32": int(tmin is not None and pd.notna(tmin) and float(tmin) <= 32),
                "freeze_le_28": int(tmin is not None and pd.notna(tmin) and float(tmin) <= 28),
                "freeze_le_24": int(tmin is not None and pd.notna(tmin) and float(tmin) <= 24),
                "gdd_base50": round(gdd, 2),
                "rh_hours_ge_90": round(rh_hours, 2),
                "precip_in": float(precip) if precip is not None and pd.notna(precip) else 0.0,
                "tmin_f": float(tmin) if tmin is not None and pd.notna(tmin) else None,
                "tmax_f": float(tmax) if tmax is not None and pd.notna(tmax) else None,
            }
        )
    return pd.DataFrame(rows)


def write_features(feat: pd.DataFrame) -> int:
    init_db()
    if feat.empty:
        return 0
    rows = feat.copy()
    rows["date"] = rows["date"].astype(str)
    with connect() as conn:
        conn.executemany(
            """
            INSERT INTO features_daily (
              station_id, date, chill_hours, freeze_le_32, freeze_le_28, freeze_le_24,
              gdd_base50, rh_hours_ge_90, precip_in, tmin_f, tmax_f
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(station_id, date) DO UPDATE SET
              chill_hours=excluded.chill_hours,
              freeze_le_32=excluded.freeze_le_32,
              freeze_le_28=excluded.freeze_le_28,
              freeze_le_24=excluded.freeze_le_24,
              gdd_base50=excluded.gdd_base50,
              rh_hours_ge_90=excluded.rh_hours_ge_90,
              precip_in=excluded.precip_in,
              tmin_f=excluded.tmin_f,
              tmax_f=excluded.tmax_f
            """,
            list(
                rows[
                    [
                        "station_id",
                        "date",
                        "chill_hours",
                        "freeze_le_32",
                        "freeze_le_28",
                        "freeze_le_24",
                        "gdd_base50",
                        "rh_hours_ge_90",
                        "precip_in",
                        "tmin_f",
                        "tmax_f",
                    ]
                ].itertuples(index=False, name=None)
            ),
        )
    return len(rows)


def build_and_store_features(station_id: str | None = None) -> int:
    obs = read_observations(station_id)
    feat = build_features_from_obs(obs)
    return write_features(feat)


def read_features(station_id: str | None = None) -> pd.DataFrame:
    init_db()
    with connect() as conn:
        if station_id:
            rows = conn.execute(
                "SELECT * FROM features_daily WHERE station_id=? ORDER BY date",
                (station_id,),
            ).fetchall()
        else:
            rows = conn.execute("SELECT * FROM features_daily ORDER BY station_id, date").fetchall()
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame([dict(r) for r in rows])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df
