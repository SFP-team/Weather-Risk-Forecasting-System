"""Diagnose THIS coordinate: weather → system → risks → windows → genotypes.

The specific-land path from the briefing. Recommendation of similar
places is attached so the two modes share one call.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from blueberry_analogue.derive.production_system import apply_structure_modifiers, classify_production_system
from blueberry_analogue.derive.risk_factors import assess_risk_factors
from blueberry_analogue.derive.stats import climate_stats
from blueberry_analogue.derive.windows import derive_windows, harvest_mask_from_windows
from blueberry_analogue.features.cube import features_from_daily
from blueberry_analogue.features.physics import heat_metrics, rain_crack_metrics
from blueberry_analogue.recommend.genotypes import card_as_probe, rank_genotypes
from blueberry_analogue.recommend.similar import region_pack, similar_environments
from blueberry_analogue.sites import Site, load_sites
from blueberry_analogue.systems import ProductionSystem, parse_system
from blueberry_analogue.weather.store import DailySeries, load_daily_series


def _query_site(lat: float, lon: float, habit: str, cultivar_id: str, name: str = "") -> Site:
    return Site(
        site_id="query",
        name=name or f"Query {lat:.3f},{lon:.3f}",
        country="",
        region="query",
        admin="",
        lat=lat,
        lon=lon,
        cultivar_class="low_chill_shb",
        cultivar=cultivar_id,
        media="open_soil",
        structure="open",
        cover="none",
        habit=habit if habit in {"deciduous", "semi_evergreen", "evergreen"} else "deciduous",
        outcome="query",
        source="coordinate",
        geocode_precision="point",
        notes="Ad-hoc coordinate. Not a catalog operation.",
    )


def _typical_year(daily: pd.DataFrame) -> pd.DataFrame:
    work = daily.copy()
    work["date"] = pd.to_datetime(work["date"])
    years = sorted(work["date"].dt.year.unique())
    mid = years[len(years) // 2]
    block = work[work["date"].dt.year == mid]
    return block if len(block) > 200 else work


def diagnose_coordinate(
    lat: float,
    lon: float,
    *,
    media: str = "open_soil",
    structure: str = "open",
    cover: str = "none",
    habit_override: str | None = None,
    hcn: bool = False,
    pollinator: str = "apis",
    live: bool = False,
    include_similar: bool = True,
    features: dict[str, dict[str, Any]] | None = None,
    climate: dict[str, dict[str, Any]] | None = None,
    sites: dict[str, Site] | None = None,
    series: DailySeries | None = None,
    top_n: int = 10,
) -> dict[str, Any]:
    system = parse_system(media, structure, cover, habit_override or "deciduous", hcn, pollinator)
    weather = series or load_daily_series(lat, lon, live=live)
    stats = climate_stats(weather.frame, lat)
    open_field = classify_production_system(stats)
    field_habit = habit_override or open_field["habit"]
    windows = derive_windows(stats, lat, field_habit)
    mask = harvest_mask_from_windows(weather.frame["date"], windows)
    rain = rain_crack_metrics(weather.frame, mask)
    n_years = max(1.0, stats.get("n_years") or 1.0)
    stats["harvest_rain_days"] = float(rain["harvest_rain_days"] / n_years)
    stats["harvest_rain_mm"] = float(rain["harvest_rain_mm"] / n_years)
    stats["rain_crack_events"] = float(rain["rain_crack_events"] / n_years)
    harvest_days = weather.frame.loc[mask] if mask.any() else weather.frame
    heat = heat_metrics(harvest_days)
    stats["days_berry_gt_42"] = float(heat["days_berry_gt_42"] / n_years)
    stats["days_tmax_gt_35"] = float(heat["days_tmax_gt_35"] / n_years)
    stats["heat_hours_proxy"] = float(heat["heat_hours_proxy"] / n_years)

    modified = apply_structure_modifiers(open_field, system)
    recommended_habit = habit_override or modified["recommended_habit"]
    allowed = modified["allowed_habits"]
    if habit_override:
        allowed = list({*allowed, habit_override})

    scoring_system = ProductionSystem(
        media=system.media,
        structure=system.structure,
        cover=system.cover,
        habit=recommended_habit,  # type: ignore[arg-type]
        hcn=system.hcn,
        pollinator=system.pollinator,
    )
    risks = assess_risk_factors(stats, scoring_system, recommended_habit)
    genotypes = rank_genotypes(stats, risks, allowed, recommended_habit, top_n=8)

    probe, klass = card_as_probe(recommended_habit)
    typical = _typical_year(weather.frame)
    feat = features_from_daily(typical, lat, probe, klass, scoring_system, region="")
    feat["lat"] = lat
    feat["lon"] = lon
    feat["source"] = weather.source
    feat["chill_hours"] = stats["chill_hours_p50"]
    feat["chill_hours_p50"] = stats["chill_hours_p50"]
    feat["chill_hours_p10"] = stats["chill_hours_p10"]
    feat["chill_hours_p90"] = stats["chill_hours_p90"]
    feat["n_years"] = stats["n_years"]
    feat["trust_notes"] = list(weather.trust_notes or [])
    if isinstance(feat.get("monthly_vpd"), list) is False:
        feat["monthly_vpd"] = [0.8] * 12

    site_map = sites if sites is not None else {s.site_id: s for s in load_sites()}
    pack = region_pack(lat, lon, site_map)
    similar = None
    if include_similar and features is not None and climate is not None:
        query_site = _query_site(lat, lon, recommended_habit, probe.id, weather.name)
        similar = similar_environments(
            "query",
            query_site,
            feat,
            features,
            climate,
            site_map,
            scoring_system,
            top_n=top_n,
        )

    leading = [r for r in risks if r["status"] in {"extreme", "concerning", "borderline"}]
    return {
        "mode": "diagnose",
        "query": {
            "lat": lat,
            "lon": lon,
            "label": weather.name or pack.get("nearest", {}).get("name") or f"{lat:.3f}, {lon:.3f}",
        },
        "weather": {
            "source": weather.source,
            "point_id": weather.point_id,
            "years": list(weather.years),
            "n_days": weather.n_days,
            "nearest_km": weather.nearest_km,
            "variables": ["tmin_c", "tmax_c", "precip_mm", "sw_mj", "rh", "wind_ms", "tdew_c"],
            "trust_notes": weather.trust_notes or [],
        },
        "open_field_system": open_field,
        "modified_system": modified,
        "windows": windows,
        "risk_factors": risks,
        "leading_risks": leading,
        "genotypes": genotypes,
        "region_pack": pack,
        "similar": similar,
        "stats": {
            k: stats[k]
            for k in (
                "n_years",
                "chill_hours_p10",
                "chill_hours_p50",
                "chill_hours_p90",
                "chill_portions",
                "frost_days_p50",
                "hard_freeze_days_p50",
                "winter_tmin_p10",
                "harvest_rain_days",
                "dli_fruit",
                "days_berry_gt_42",
                "annual_precip_mm",
                "drought_events_p50",
            )
            if k in stats
        },
        "disclaimer": (
            "Recommendation, not a plant-here button. Thresholds are provisional "
            "until Patricia and Gerardo lock them. Book the flight. Walk the land."
        ),
        "claim": "weather_derived_system_and_risk",
    }
