"""Train seasonal event models on station-month aggregates.

Uses sklearn HistGradientBoosting (portable; no native LightGBM/OpenMP dependency).

Targets:
- monthly mean Tmin
- freeze day count (Tmin <= 32)
- monthly chill hours sum
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error

from blueberry_common.config import get_settings
from blueberry_features.daily import read_features


def _station_month_table(feat: pd.DataFrame) -> pd.DataFrame:
    if feat.empty:
        return pd.DataFrame()
    f = feat.copy()
    f["date"] = pd.to_datetime(f["date"])
    f["year"] = f["date"].dt.year
    f["month"] = f["date"].dt.month
    g = f.groupby(["station_id", "year", "month"], as_index=False).agg(
        tmin_mean=("tmin_f", "mean"),
        tmax_mean=("tmax_f", "mean"),
        freeze_days=("freeze_le_32", "sum"),
        chill_hours=("chill_hours", "sum"),
        precip=("precip_in", "sum"),
    )
    g = g.sort_values(["station_id", "year", "month"])
    g["tmin_lag1"] = g.groupby("station_id")["tmin_mean"].shift(1)
    g["tmin_lag2"] = g.groupby("station_id")["tmin_mean"].shift(2)
    g["freeze_lag1"] = g.groupby("station_id")["freeze_days"].shift(1)
    g["chill_lag1"] = g.groupby("station_id")["chill_hours"].shift(1)
    g["month_sin"] = np.sin(2 * np.pi * g["month"] / 12)
    g["month_cos"] = np.cos(2 * np.pi * g["month"] / 12)
    stations = sorted(g["station_id"].unique())
    smap = {s: i for i, s in enumerate(stations)}
    g["station_code"] = g["station_id"].map(smap)
    return g.dropna()


FEATURE_COLS = [
    "month",
    "month_sin",
    "month_cos",
    "station_code",
    "tmin_lag1",
    "tmin_lag2",
    "freeze_lag1",
    "chill_lag1",
]


def train_models() -> dict:
    settings = get_settings()
    settings.ensure_dirs()
    feat = read_features()
    table = _station_month_table(feat)
    if table.empty or len(table) < 50:
        raise RuntimeError("Not enough feature data to train. Run feature pipeline first.")

    max_year = int(table["year"].max())
    train = table[table["year"] <= max_year - 2]
    test = table[table["year"] > max_year - 2]
    if train.empty or test.empty:
        train = table.sample(frac=0.8, random_state=42)
        test = table.drop(train.index)

    metrics = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_train": len(train),
        "n_test": len(test),
        "backend": "sklearn.HistGradientBoostingRegressor",
    }
    models = {}
    targets = {
        "tmin_mean": "tmin_mean",
        "freeze_days": "freeze_days",
        "chill_hours": "chill_hours",
    }

    for name, col in targets.items():
        model = HistGradientBoostingRegressor(
            max_depth=6,
            learning_rate=0.08,
            max_iter=150,
            random_state=42,
        )
        model.fit(train[FEATURE_COLS], train[col])
        pred = model.predict(test[FEATURE_COLS])
        mae = float(mean_absolute_error(test[col], pred))
        clim = train.groupby("month")[col].mean()
        clim_pred = test["month"].map(clim).astype(float)
        clim_mae = float(mean_absolute_error(test[col], clim_pred))
        skill = 1.0 - (mae / clim_mae) if clim_mae > 0 else 0.0
        metrics[name] = {"mae": mae, "climatology_mae": clim_mae, "skill_vs_clim": skill}
        models[name] = model
        joblib.dump(model, settings.models_dir / f"{name}.joblib")

    stations = sorted(table["station_id"].unique())
    meta = {"stations": stations, "feature_cols": FEATURE_COLS}
    (settings.models_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    (settings.metrics_dir / "seasonal_metrics.json").write_text(json.dumps(metrics, indent=2))
    joblib.dump(models, settings.models_dir / "seasonal_bundle.joblib")
    return metrics


def load_models() -> dict | None:
    path = get_settings().models_dir / "seasonal_bundle.joblib"
    if not path.exists():
        return None
    return joblib.load(path)


def predict_next_months(station_id: str, n_months: int = 3) -> list[dict]:
    models = load_models()
    settings = get_settings()
    meta_path = settings.models_dir / "meta.json"
    if models is None or not meta_path.exists():
        return []

    meta = json.loads(meta_path.read_text())
    stations = meta["stations"]
    station_code = stations.index(station_id) if station_id in stations else 0

    feat = read_features(station_id)
    table = _station_month_table(feat)
    if table.empty:
        return []

    last = table.iloc[-1]
    tmin_lag1 = float(last["tmin_mean"])
    tmin_lag2 = float(last["tmin_lag1"]) if pd.notna(last.get("tmin_lag1")) else tmin_lag1
    freeze_lag1 = float(last["freeze_days"])
    chill_lag1 = float(last["chill_hours"])
    year = int(last["year"])
    month = int(last["month"])

    out = []
    for _ in range(n_months):
        month += 1
        if month > 12:
            month = 1
            year += 1
        row = pd.DataFrame(
            [
                {
                    "month": month,
                    "month_sin": np.sin(2 * np.pi * month / 12),
                    "month_cos": np.cos(2 * np.pi * month / 12),
                    "station_code": station_code,
                    "tmin_lag1": tmin_lag1,
                    "tmin_lag2": tmin_lag2,
                    "freeze_lag1": freeze_lag1,
                    "chill_lag1": chill_lag1,
                }
            ]
        )
        tmin_hat = float(models["tmin_mean"].predict(row[FEATURE_COLS])[0])
        freeze_hat = max(0.0, float(models["freeze_days"].predict(row[FEATURE_COLS])[0]))
        chill_hat = max(0.0, float(models["chill_hours"].predict(row[FEATURE_COLS])[0]))
        p_freeze = float(min(0.95, max(0.02, 1.0 - np.exp(-freeze_hat / 4.0))))

        start = date_for(year, month, 1)
        end = month_end(year, month)
        out.append(
            {
                "period_label": start.strftime("%b %Y"),
                "valid_start": start,
                "valid_end": end,
                "tmean_anomaly_f": round(tmin_hat - 50.0, 2),
                "tmean_anomaly_range": (round(tmin_hat - 53, 1), round(tmin_hat - 47, 1)),
                "precip_tercile": {"below": 0.3, "near": 0.4, "above": 0.3},
                "p_freeze_window": round(p_freeze, 3),
                "expected_freeze_nights": round(freeze_hat, 2),
                "chill_hours_p10": round(chill_hat * 0.7, 1),
                "chill_hours_p50": round(chill_hat, 1),
                "chill_hours_p90": round(chill_hat * 1.3, 1),
                "p_chill_shortfall": None,
                "confidence": "med",
                "narrative": (
                    f"ML seasonal head for {start.strftime('%B %Y')}: "
                    f"expected ~{freeze_hat:.1f} freeze-class nights, "
                    f"~{chill_hat:.0f} chill hours contribution. "
                    f"Mean Tmin ~{tmin_hat:.1f}°F. Not a daily forecast."
                ),
                "method": "sklearn-histgradient-seasonal",
            }
        )
        tmin_lag2 = tmin_lag1
        tmin_lag1 = tmin_hat
        freeze_lag1 = freeze_hat
        chill_lag1 = chill_hat

    return out


def date_for(y: int, m: int, d: int):
    from datetime import date

    return date(y, m, d)


def month_end(y: int, m: int):
    import calendar
    from datetime import date

    return date(y, m, calendar.monthrange(y, m)[1])
