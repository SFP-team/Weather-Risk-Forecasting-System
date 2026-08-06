#!/usr/bin/env python3
"""End-to-end pipeline: seed data → features → train → ready for API."""

from __future__ import annotations

import json
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

# Ensure repo root on path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
for p in (
    ROOT / "packages" / "common",
    ROOT / "packages" / "ingest",
    ROOT / "packages" / "features",
    ROOT / "packages" / "risk",
    ROOT / "packages" / "models",
):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def main() -> int:
    from blueberry_common.config import get_settings
    from blueberry_common.db import init_db, connect, set_meta
    from blueberry_common.farms import seed_farms
    from blueberry_ingest.load import load_synthetic_history, merge_live_recent, seed_stations
    from blueberry_features.daily import build_and_store_features
    from blueberry_models.train import train_models

    settings = get_settings()
    settings.ensure_dirs()
    print("== Blueberry Weather Risk pipeline ==")
    print(f"Root: {ROOT}")
    print(f"DB: {settings.processed_dir / 'blueberry_risk.db'}")

    init_db()
    seed_stations()
    n_farms = seed_farms()
    print(f"Seeded {n_farms} demo farms")

    print("Loading synthetic multi-year history (FL blueberry belt)...")
    n_obs = load_synthetic_history()
    print(f"Wrote {n_obs} daily observations")

    print("Attempting live Open-Meteo recent overlay...")
    try:
        n_live = merge_live_recent(days=45)
        print(f"Overlayed {n_live} live archive rows")
    except Exception as e:
        print(f"Live overlay skipped: {e}")

    print("Building features (chill, freeze flags)...")
    n_feat = build_and_store_features()
    print(f"Wrote {n_feat} feature rows")

    print("Training seasonal HistGradientBoosting models...")
    try:
        metrics = train_models()
        print(json.dumps(metrics, indent=2))
    except Exception:
        traceback.print_exc()
        print("Training failed — API can still use climatology fallbacks")
        metrics = {"error": "train_failed"}

    with connect() as conn:
        set_meta(conn, "last_pipeline_run", datetime.now(timezone.utc).isoformat())
        set_meta(conn, "last_metrics", json.dumps(metrics))

    print("Pipeline complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
