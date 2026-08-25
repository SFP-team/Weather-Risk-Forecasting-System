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
