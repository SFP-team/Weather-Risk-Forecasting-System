from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "analogue"))

from blueberry_analogue.analogue.engine import ccafs_monthly_distance, score_pair
from blueberry_analogue.cards import load_cards
from blueberry_analogue.climate.fetch import fallback_climatology, monthly_to_daily
from blueberry_analogue.climate.hourly import hourly_curve
from blueberry_analogue.features.chill import chill_hours_0_7p2, dynamic_portions, negation_hours
from blueberry_analogue.features.cube import features_from_daily
from blueberry_analogue.features.physics import berry_surface_c, stull_wet_bulb
from blueberry_analogue.systems import parse_system


def test_dynamic_model_cool_vs_hot():
    cool = np.full(24 * 40, 6.0)
    hot = np.full(24 * 40, 25.0)
    assert dynamic_portions(cool)[-1] > 8
    assert dynamic_portions(hot)[-1] < 1
    assert chill_hours_0_7p2(cool).sum() == 24 * 40
    assert negation_hours(hot, 21.0).sum() == 24 * 40


def test_hourly_curve_peaks_afternoon():
    temps = hourly_curve(4.0, 18.0, 43.0, 15)
    assert temps[14] > temps[5]
    assert temps.min() >= 3.0
    assert temps.max() <= 18.5


def test_wet_bulb_and_berry():
    tw = stull_wet_bulb(np.array([0.0]), np.array([90.0]))[0]
    assert -2 < tw < 1
    berry = berry_surface_c(np.array([36.0]))[0]
    assert berry >= 43.0


def test_feature_cube_michigan_vs_florida_shape():
    cards = load_cards()
    duke = cards.cultivar("duke")
    nhb = cards.classes["nhb"]
    mi = monthly_to_daily(fallback_climatology(42.4, -86.1))
    fl = monthly_to_daily(fallback_climatology(27.5, -81.4))
    sys = parse_system()
    mi_f = features_from_daily(mi, 42.4, duke, nhb, sys, region="US-MI")
    fl_f = features_from_daily(fl, 27.5, duke, nhb, sys, region="US-SE")
    assert mi_f["chill_portions"] > fl_f["chill_portions"]
    assert mi_f["dtr"] > 0


def test_seasonal_lag_prefers_six_months_for_opposite_hemisphere():
    ref = {
        "monthly_tmin": [ -6, -5, 0, 6, 12, 16, 19, 18, 13, 7, 1, -4],
        "monthly_tmax": [ 0, 2, 8, 16, 22, 27, 29, 28, 23, 16, 8, 2],
        "monthly_precip": [50] * 12,
        "monthly_vpd": [0.4, 0.4, 0.6, 0.8, 1.1, 1.3, 1.4, 1.3, 1.0, 0.7, 0.5, 0.4],
        "monthly_rsds": [6, 8, 12, 16, 20, 22, 21, 18, 14, 10, 7, 5],
    }
    chile = {k: v[6:] + v[:6] for k, v in ref.items()}
    best = ccafs_monthly_distance(ref, chile, {k: 1.0 for k in ref})
    assert best["lag"] in {5, 6, 7}


def test_gates_kill_warm_winter_for_nhb():
    cards = load_cards()
    duke = cards.cultivar("duke")
    nhb = cards.classes["nhb"]
    ref = features_from_daily(monthly_to_daily(fallback_climatology(42.4, -86.1)), 42.4, duke, nhb, parse_system(), "US-MI")
    warm = features_from_daily(monthly_to_daily(fallback_climatology(6.0, -79.8)), 6.0, duke, nhb, parse_system(), "PE-NORTH")
    scored = score_pair(ref, warm, {"source": "fallback", "trust_notes": [], "land": {}, "lat": 6.0}, duke, nhb, parse_system())
    assert scored["hard_fail_count"] >= 1
    assert any(t["variable"] == "chill_portions" for t in scored["trouble"])
