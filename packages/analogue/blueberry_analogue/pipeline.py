"""Build cards, truth set, point climate, features, and the skill sheet."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd

from blueberry_analogue.cards import load_cards
from blueberry_analogue.climate.fetch import _cache_path, _read_json, climate_daily, load_or_build_climatology
from blueberry_analogue.features.cube import features_from_daily, flatten_for_table
from blueberry_analogue.paths import FEATURE_CACHE, SITES_CSV, ensure_data_dirs
from blueberry_analogue.sites import ensure_sites_csv, load_sites
from blueberry_analogue.validation.evaluate import run_validation


def build_truth_set() -> int:
    ensure_sites_csv(SITES_CSV)
    return len(load_sites(refresh=True))


def build_features(live: bool = False, limit: int | None = None, refresh: bool = False) -> dict[str, dict[str, Any]]:
    ensure_data_dirs()
    cards = load_cards()
    sites = load_sites(refresh=True)
    climate = load_or_build_climatology(sites, live=live, limit=limit, refresh=refresh)
    features: dict[str, dict[str, Any]] = {}
    use = sites if limit is None else sites[:limit]
    for site in use:
        payload = climate[site.site_id]
        daily = climate_daily(payload)
        cultivar = cards.cultivar(site.cultivar)
        klass = cards.classes[site.cultivar_class]
        vec = features_from_daily(daily, site.lat, cultivar, klass, site.system, region=site.region)
        vec["site_id"] = site.site_id
        vec["lat"] = site.lat
        vec["lon"] = site.lon
        vec["source"] = payload.get("source")
        features[site.site_id] = vec
    table = pd.DataFrame([flatten_for_table(v) for v in features.values()])
    FEATURE_CACHE.mkdir(parents=True, exist_ok=True)
    table.to_csv(FEATURE_CACHE / "site_features.csv", index=False)
    (FEATURE_CACHE / "site_features.json").write_text(
        json.dumps(features, indent=2, default=str), encoding="utf-8"
    )
    return features


def load_feature_cache() -> dict[str, dict[str, Any]] | None:
    path = FEATURE_CACHE / "site_features.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def climate_for_features(features: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    climate: dict[str, dict[str, Any]] = {}
    for sid in features:
        climate[sid] = _read_json(_cache_path("climate", sid)) or {
            "source": features[sid].get("source"),
            "trust_notes": [],
            "land": {},
            "lat": features[sid].get("lat"),
        }
    return climate


def build_all(live: bool = False, limit: int | None = None, refresh: bool = False) -> dict[str, Any]:
    n_sites = build_truth_set()
    features = build_features(live=live, limit=limit, refresh=refresh)
    sites = {s.site_id: s for s in load_sites()}
    climate = climate_for_features(features)
    report = run_validation(features, climate, sites)
    return {"n_sites": n_sites, "n_features": len(features), "validation": report}
