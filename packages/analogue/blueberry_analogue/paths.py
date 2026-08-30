"""Repo and analogue data paths."""

from __future__ import annotations

from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
DATA_PKG = PACKAGE_DIR / "data"
REPO_ROOT = PACKAGE_DIR.parents[2]
ANALOGUE_DATA = REPO_ROOT / "data" / "analogue"
CLIM_CACHE = ANALOGUE_DATA / "climatology"
FEATURE_CACHE = ANALOGUE_DATA / "features"
LAND_CACHE = ANALOGUE_DATA / "land"
STATION_CACHE = ANALOGUE_DATA / "stations"
WEATHER_DIR = ANALOGUE_DATA / "weather"
WEATHER_DB = WEATHER_DIR / "daily.sqlite"
DOCS_ANALOGUE = REPO_ROOT / "docs" / "analogue"
CARDS_YAML = DATA_PKG / "variety_cards.yaml"
SELECTIONS_YAML = DATA_PKG / "advanced_selections.yaml"
SITES_CSV = DATA_PKG / "truth_set.csv"


def ensure_data_dirs() -> None:
    for path in (ANALOGUE_DATA, CLIM_CACHE, FEATURE_CACHE, LAND_CACHE, STATION_CACHE, WEATHER_DIR):
        path.mkdir(parents=True, exist_ok=True)
