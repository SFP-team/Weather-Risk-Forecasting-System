from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "analogue"))

from blueberry_analogue.pipeline import build_all
from blueberry_analogue.validation.baselines import baseline1_ecocrop, baseline2_nz_landcare


def test_ecocrop_and_nz_baselines():
    cool = {
        "monthly_tmin_mean": 4.0,
        "monthly_tmax_mean": 18.0,
        "monthly_tmin": [-8, -6, -2, 3, 8, 12, 14, 13, 9, 4, -1, -6],
        "monthly_precip_sum": 900,
        "chill_hours": 900,
        "frost_nights_full_bloom": 2,
    }
    desert = {
        "monthly_tmin_mean": 18.0,
        "monthly_tmax_mean": 30.0,
        "monthly_tmin": [16] * 12,
        "monthly_precip_sum": 40,
        "chill_hours": 20,
        "frost_nights_full_bloom": 0,
    }
    assert baseline1_ecocrop(cool, irrigated=True) > 0.4
    assert baseline1_ecocrop(desert, irrigated=False) == 0.0
    assert baseline1_ecocrop(desert, irrigated=True) > 0.0
    assert baseline2_nz_landcare(cool) > baseline2_nz_landcare(desert)


def test_loro_hides_same_region_neighbors():
    from blueberry_analogue.validation.evaluate import loro_transfer
    from blueberry_analogue.sites import Site

    def feat(tmin, tmax, precip, chill_p, chill_h, frost=1.0, heat=0.0):
        return {
            "monthly_tmin": tmin,
            "monthly_tmax": tmax,
            "monthly_precip": precip,
            "monthly_vpd": [0.6] * 12,
            "monthly_rsds": [15.0] * 12,
            "chill_portions": chill_p,
            "chill_hours": chill_h,
            "frost_nights_full_bloom": frost,
            "heat_hours_proxy": heat,
            "dtr": 10.0,
            "dli_bloom": 20.0,
            "vpd_fruit": 0.8,
            "harvest_rain_days": 2.0,
            "days_berry_gt_42": 0.0,
            "igp_fog_events": 0.0,
            "lat": 42.0,
        }

    cool = [-6, -5, 0, 6, 12, 16, 19, 18, 13, 7, 1, -4]
    warm = [12] * 12
    tmax_c = [0, 2, 8, 16, 22, 27, 29, 28, 23, 16, 8, 2]
    tmax_w = [28] * 12
    rain = [50] * 12

    def site(sid, region, cultivar, klass, lat=42.0):
        return Site(
            site_id=sid,
            name=sid,
            country="US",
            region=region,
            admin="",
            lat=lat,
            lon=-86.0,
            cultivar_class=klass,
            cultivar=cultivar,
            media="open_soil",
            structure="open",
            cover="none",
            habit="deciduous",
            outcome="commercial_success",
            source="test",
            geocode_precision="district",
            notes="",
        )

    sites = {
        "mi-a": site("mi-a", "US-MI", "duke", "nhb"),
        "mi-b": site("mi-b", "US-MI", "duke", "nhb"),
        "pnw-a": site("pnw-a", "US-PNW", "duke", "nhb", lat=45.0),
        "fl-a": site("fl-a", "US-SE", "snowchaser", "low_chill_shb", lat=29.0),
    }
    features = {
        "mi-a": feat(cool, tmax_c, rain, 70, 900),
        "mi-b": feat(cool, tmax_c, rain, 68, 880),
        "pnw-a": feat(cool, tmax_c, rain, 72, 920),
        "fl-a": feat(warm, tmax_w, rain, 5, 200),
    }
    row = loro_transfer(features, {}, sites, "US-MI", top_k=2, ref_cap=2)
    assert row["skipped"] is False
    # Neighbors in US-MI are hidden, so the NHB hit has to be PNW.
    assert row["recall_at_k"] == 1.0


def test_offline_build_and_skill_sheet(tmp_path, monkeypatch):
    # Isolate caches so this test cannot overwrite the NASA POWER feature lake.
    from blueberry_analogue import paths, pipeline
    from blueberry_analogue.validation import evaluate

    monkeypatch.setattr(paths, "FEATURE_CACHE", tmp_path / "features")
    monkeypatch.setattr(paths, "CLIM_CACHE", tmp_path / "clim")
    monkeypatch.setattr(paths, "LAND_CACHE", tmp_path / "land")
    monkeypatch.setattr(paths, "DOCS_ANALOGUE", tmp_path / "docs")
    monkeypatch.setattr(pipeline, "FEATURE_CACHE", tmp_path / "features")
    monkeypatch.setattr(evaluate, "DOCS_ANALOGUE", tmp_path / "docs")
    (tmp_path / "features").mkdir()
    (tmp_path / "clim").mkdir()
    (tmp_path / "docs").mkdir()

    result = pipeline.build_all(live=False, limit=40)
    assert result["n_features"] == 40
    assert result["n_sites"] >= 200
    sheet = tmp_path / "docs" / "skill-sheet.md"
    assert sheet.exists()
    text = sheet.read_text()
    assert "may not say" in text
    assert "Leave-one-region-out" in text
