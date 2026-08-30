from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "analogue"))

from blueberry_analogue.derive.production_system import (
    apply_structure_modifiers,
    classify_production_system,
)
from blueberry_analogue.derive.risk_factors import assess_risk_factors
from blueberry_analogue.derive.stats import climate_stats
from blueberry_analogue.recommend.diagnose import diagnose_coordinate
from blueberry_analogue.recommend.genotypes import rank_genotypes
from blueberry_analogue.recommend.similar import region_pack
from blueberry_analogue.sites import load_sites
from blueberry_analogue.systems import parse_system
from blueberry_analogue.weather.daily import fallback_daily_years
from blueberry_analogue.weather.store import DailySeries, WeatherStore, load_daily_series


def _daily(tmin_w, tmax_w, tmin_s, tmax_s, precip_harvest=1.0, years=(2018, 2019, 2020)):
    """Build a 3-year NH series with a controlled winter and harvest."""
    rows = []
    for year in years:
        for month in range(1, 13):
            days = 28 if month == 2 else 30
            winter = month in {11, 12, 1, 2, 3}
            harvest = month in {4, 5}
            for day in range(1, days + 1):
                tmin = tmin_w if winter else tmin_s
                tmax = tmax_w if winter else tmax_s
                rain = precip_harvest if harvest else 0.4
                rows.append(
                    {
                        "date": pd.Timestamp(year=year, month=month, day=min(day, 28 if month == 2 else day)),
                        "tmin_c": tmin,
                        "tmax_c": tmax,
                        "tmean_c": 0.5 * (tmin + tmax),
                        "precip_mm": rain,
                        "sw_mj": 12.0 if winter else 22.0,
                        "rh": 75.0,
                        "wind_ms": 2.0,
                        "tdew_c": tmin - 1.0,
                    }
                )
    return pd.DataFrame(rows)


def test_classifier_cold_is_deciduous():
    daily = _daily(tmin_w=-4.0, tmax_w=6.0, tmin_s=12.0, tmax_s=26.0)
    stats = climate_stats(daily, 43.0)
    out = classify_production_system(stats)
    assert out["habit"] == "deciduous"
    assert stats["chill_hours_p50"] > 400


def test_classifier_warm_is_evergreen():
    daily = _daily(tmin_w=16.0, tmax_w=26.0, tmin_s=22.0, tmax_s=32.0)
    stats = climate_stats(daily, 26.0)
    out = classify_production_system(stats)
    assert out["habit"] == "evergreen"
    assert stats["frost_days_p50"] <= 1


def test_classifier_mid_is_semi_evergreen():
    out = classify_production_system(
        {
            "chill_hours_p50": 280.0,
            "frost_days_p50": 3.0,
            "hard_freeze_days_p50": 0.0,
            "winter_tmin_p10": 1.0,
        }
    )
    assert out["habit"] == "semi_evergreen"


def test_tunnels_open_evergreen_in_deciduous_climate():
    open_field = {"habit": "deciduous", "confidence": 0.8, "reasons": []}
    system = parse_system(structure="tunnel", media="substrate")
    mod = apply_structure_modifiers(open_field, system)
    assert "evergreen" in mod["allowed_habits"]
    assert mod["flexible"] is True
    assert mod["rain_crack_multiplier"] < 0.2


def test_harvest_rain_flags_when_wet():
    daily = _daily(tmin_w=6.0, tmax_w=18.0, tmin_s=18.0, tmax_s=30.0, precip_harvest=12.0)
    stats = climate_stats(daily, 29.5)
    stats["harvest_rain_days"] = 18.0
    risks = assess_risk_factors(stats, parse_system(), "deciduous")
    rain = next(r for r in risks if r["id"] == "harvest_rain")
    assert rain["status"] in {"concerning", "extreme", "borderline"}


def test_low_chill_ranks_low_chill_or_evergreen_above_nhb():
    stats = {
        "chill_hours_p50": 120.0,
        "harvest_rain_days": 4.0,
        "dli_fruit": 28.0,
        "frost_days_p50": 0.0,
        "days_berry_gt_42": 1.0,
        "drought_events_p50": 1.0,
    }
    risks = assess_risk_factors(stats, parse_system(), "evergreen")
    ranked = rank_genotypes(stats, risks, ["evergreen", "semi_evergreen"], "evergreen")
    top = ranked["genotypes"][0]
    assert top["class_id"] in {"evergreen_zero_chill", "low_chill_shb"}
    assert all(g["class_id"] != "nhb" for g in ranked["genotypes"][:3])


def test_high_chill_prefers_nhb_or_high_chill_shb():
    stats = {
        "chill_hours_p50": 950.0,
        "harvest_rain_days": 4.0,
        "dli_fruit": 28.0,
        "frost_days_p50": 20.0,
        "days_berry_gt_42": 1.0,
        "drought_events_p50": 1.0,
    }
    risks = assess_risk_factors(stats, parse_system(), "deciduous")
    ranked = rank_genotypes(stats, risks, ["deciduous"], "deciduous")
    assert ranked["genotypes"][0]["class_id"] in {"nhb", "high_chill_shb"}


def test_region_pack_waldo_is_local_cluster():
    sites = {s.site_id: s for s in load_sites()}
    pack = region_pack(29.79, -82.17, sites, radius_km=50)
    ids = {row["site_id"] for row in pack["sites"]}
    assert "us-fl-waldo" in ids
    assert "us-fl-alachua" in ids
    assert pack["nearest"]["site_id"] == "us-fl-waldo"


def test_weather_store_roundtrip(tmp_path):
    db = WeatherStore(tmp_path / "daily.sqlite")
    frame = fallback_daily_years(29.79, -82.17, 2018, 2019)
    db.put_series("us-fl-waldo", 29.79, -82.17, frame, "fallback_daily", name="Waldo")
    got = db.get_series("us-fl-waldo")
    assert got is not None
    assert got.n_days > 600
    near = db.nearest(29.80, -82.16)
    assert near is not None
    assert near[1] < 5


def test_load_daily_series_fallback_offline(tmp_path):
    db = WeatherStore(tmp_path / "empty.sqlite")
    series = load_daily_series(27.5, -81.4, live=False, store=db, persist=False)
    assert series.n_days > 300
    assert series.source in {"fallback_daily", "nasa_power_climatology_expanded"}


def test_diagnose_waldo_offline():
    daily = fallback_daily_years(29.79, -82.17, 2016, 2018)
    series = DailySeries(
        point_id="pt_test",
        lat=29.79,
        lon=-82.17,
        frame=daily,
        source="fallback_daily",
        name="Waldo",
        trust_notes=["test"],
    )
    out = diagnose_coordinate(
        29.79,
        -82.17,
        live=False,
        include_similar=False,
        series=series,
    )
    assert out["mode"] == "diagnose"
    assert out["open_field_system"]["habit"] in {"deciduous", "semi_evergreen", "evergreen"}
    assert out["windows"]["harvest"]["start"]
    assert out["genotypes"]["genotypes"]
    assert any(r["id"] == "harvest_rain" for r in out["risk_factors"])
