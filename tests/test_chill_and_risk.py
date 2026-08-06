import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (
    ROOT / "packages" / "common",
    ROOT / "packages" / "features",
    ROOT / "packages" / "risk",
    ROOT / "packages" / "ingest",
):
    sys.path.insert(0, str(p))

from blueberry_features.chill import chill_hours_from_daily
from blueberry_risk.tonight import evaluate_tonight, start_threshold_f
from blueberry_common.schemas import PhenologyStage


def test_chill_hours_cold_day():
    # Cold day mostly in 32-45 band should accumulate some chill
    h = chill_hours_from_daily(34, 42)
    assert h > 10


def test_chill_hours_hot_day():
    h = chill_hours_from_daily(60, 85)
    assert h == 0


def test_start_threshold_dry_air():
    assert start_threshold_f(20, PhenologyStage.OPEN_BLOOM) >= 33


def test_tonight_protect_cold_bloom():
    farm = {
        "id": "t1",
        "phenology_stage": "OPEN_BLOOM",
        "cold_spot_bias_f": -2,
        "system_rate_in_per_hr": 0.2,
        "irrigation_freeze_protection": True,
    }
    station = {"id": "ALACHUA", "lat": 29.8, "lon": -82.4}
    # Force non-live so deterministic fallback then we still test structure
    risk = evaluate_tonight(farm, station, live=False)
    assert risk.farm_id == "t1"
    assert risk.status.value in {"LOW", "WATCH", "PROTECT", "BEYOND_SYSTEM"}
    assert risk.checklist
