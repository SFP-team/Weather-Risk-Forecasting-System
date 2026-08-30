from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "analogue"))

from blueberry_analogue.cards import CLASS_IDS, load_cards
from blueberry_analogue.sites import load_sites
from blueberry_analogue.climate.stations import trust_band
from blueberry_analogue.systems import parse_system, system_effects


def test_five_class_cards():
    cards = load_cards()
    assert set(cards.classes) == set(CLASS_IDS)
    nhb = cards.classes["nhb"]
    assert nhb.chill_hours_min >= 800
    ev = cards.classes["evergreen_zero_chill"]
    assert ev.chill_relevant is False
    assert ev.analogue_weights["dli_bloom"] > ev.analogue_weights["chill_hours"]


def test_flower_leaf_mismatch_oneal():
    cards = load_cards()
    oneal = cards.cultivar("oneal")
    assert oneal.flower_hours == 400
    assert oneal.leaf_hours == 700
    assert oneal.flower_leaf_mismatch < 0.7


def test_stage_lethal_temps():
    cards = load_cards()
    bloom = cards.stage("full_bloom")
    green = cards.stage("green_fruit")
    assert bloom.lt_c == -2.2
    assert green.lt_c == 0.0


def test_system_switches():
    soil = system_effects(parse_system())
    bags = system_effects(parse_system(media="substrate"))
    tunnel = system_effects(parse_system(structure="tunnel", pollinator="apis"))
    assert bags.soil_ph_weight == 0.0
    assert soil.soil_ph_weight == 1.0
    assert tunnel.freeze_water_factor == 0.1
    assert tunnel.bloom_advance_days == 30
    assert tunnel.apis_ok is False
    cover = system_effects(parse_system(cover="woven"))
    assert cover.uv_fraction == 0.42
    assert cover.rain_exclusion > 0.8


def test_truth_set_size_and_map():
    sites = load_sites(refresh=True)
    assert len(sites) >= 200
    regions = {s.region for s in sites}
    for needed in ("US-SE", "US-MI", "US-PNW", "CA-BC", "CL-SOUTH", "PE-NORTH", "ES-HUELVA", "MA-NORTH", "AU-TAS", "NZ-NORTH"):
        assert needed in regions
    outcomes = {s.outcome for s in sites}
    assert "commercial_success" in outcomes
    assert "known_failure" in outcomes
    assert "horticultural_absence" in outcomes
    assert any(s.site_id == "us-or-willamette-emerald" for s in sites)
    assert any(s.site_id == "in-delhi" for s in sites)
    assert any(s.media == "substrate" and s.country == "PE" for s in sites)
    assert trust_band(100.0, 110.0)
    assert not trust_band(20.0, 80.0)
