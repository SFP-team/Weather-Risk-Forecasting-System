from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "analogue"))

from blueberry_analogue.weather.campus_bot import run_campus_download
from blueberry_analogue.weather.grid import (
    probably_land,
    plan_estimate,
    plan_points,
)
from blueberry_analogue.weather.store import WeatherStore


def test_probably_land_keeps_florida_drops_mid_atlantic():
    assert probably_land(29.8, -82.2)
    assert probably_land(-28.5, -50.9)
    assert not probably_land(0.0, -150.0)


def test_tonight_plan_is_the_catalog():
    pts = plan_points("tonight")
    assert len(pts) >= 300
    assert any(p.point_id == "us-fl-waldo" for p in pts)


def test_future_plan_is_larger_than_catalog_but_not_a_tb_cube():
    est = plan_estimate("future")
    assert est["points"] > 400
    # Daily POWER pack. If this ever looks like TBs, the grid is wrong.
    assert est["disk_mb"] < 50_000


def test_dry_run_writes_progress_without_network(tmp_path, monkeypatch):
    from blueberry_analogue import paths

    monkeypatch.setattr(paths, "WEATHER_DIR", tmp_path)
    monkeypatch.setattr(paths, "WEATHER_DB", tmp_path / "daily.sqlite")
    monkeypatch.setattr(paths, "WEATHER_PROGRESS", tmp_path / "download_progress.json")
    monkeypatch.setattr(paths, "CDS_JOBS", tmp_path / "cds_jobs")
    from blueberry_analogue.weather import campus_bot

    monkeypatch.setattr(campus_bot, "WEATHER_PROGRESS", tmp_path / "download_progress.json")
    monkeypatch.setattr(campus_bot, "CDS_JOBS", tmp_path / "cds_jobs")
    db = WeatherStore(tmp_path / "daily.sqlite")
    report = run_campus_download("tonight", dry_run=True, store=db)
    assert report["points_total"] >= 300
    assert report["ok"] == 0
    assert (tmp_path / "download_progress.json").exists()
    assert (tmp_path / "cds_jobs").exists()
