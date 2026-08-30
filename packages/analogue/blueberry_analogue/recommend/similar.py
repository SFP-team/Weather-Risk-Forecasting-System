"""Recommend similar environments — the other half of diagnose-this-land.

Two jobs from the briefing:
  1. This coordinate is Brazil. Which Florida / SE US operations look like it?
  2. Recommendation, not the pin: other places in the same country/region
     that sit closer to the known success belt than the exact coordinate.
"""

from __future__ import annotations

import math
from collections import defaultdict
from typing import Any

from blueberry_analogue.analogue.engine import shortlist_from_reference
from blueberry_analogue.sites import Site
from blueberry_analogue.systems import ProductionSystem


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def nearest_catalog_site(lat: float, lon: float, sites: dict[str, Site]) -> tuple[Site, float] | None:
    best = None
    for site in sites.values():
        km = _haversine_km(lat, lon, site.lat, site.lon)
        if best is None or km < best[1]:
            best = (site, km)
    return best


def region_pack(lat: float, lon: float, sites: dict[str, Site], radius_km: float = 80.0) -> dict[str, Any]:
    """Waldo is in Alachua County. Return the county, not only the pin."""
    near = nearest_catalog_site(lat, lon, sites)
    if near is None:
        return {"admin": None, "sites": [], "note": "No catalog sites loaded."}
    site, km = near
    members = [
        {
            "site_id": s.site_id,
            "name": s.name,
            "admin": s.admin,
            "region": s.region,
            "lat": s.lat,
            "lon": s.lon,
            "habit": s.habit,
            "cultivar": s.cultivar,
            "outcome": s.outcome,
            "km": round(_haversine_km(lat, lon, s.lat, s.lon), 1),
        }
        for s in sites.values()
        if s.admin and s.admin == site.admin
    ]
    # State-level admin (Florida, Chile, ...) is too wide. Prefer the local cluster.
    if len(members) < 2 or len(members) > 12 or site.admin in {"Florida", "California", "Chile", "Peru", "Mexico"}:
        members = [
            {
                "site_id": s.site_id,
                "name": s.name,
                "admin": s.admin,
                "region": s.region,
                "lat": s.lat,
                "lon": s.lon,
                "habit": s.habit,
                "cultivar": s.cultivar,
                "outcome": s.outcome,
                "km": round(_haversine_km(lat, lon, s.lat, s.lon), 1),
            }
            for s in sites.values()
            if _haversine_km(lat, lon, s.lat, s.lon) <= radius_km
        ]
        members.sort(key=lambda r: r["km"])
        note = (
            f"Nearest named operation is {site.name} ({km:.1f} km). "
            f"Showing operations within {radius_km:.0f} km, not only the pin."
        )
    else:
        members.sort(key=lambda r: r["km"])
        note = (
            f"{site.name} sits in {site.admin}. "
            "Here is the admin pack, not only the coordinate."
        )
    return {
        "nearest": {"site_id": site.site_id, "name": site.name, "admin": site.admin, "km": round(km, 1)},
        "admin": site.admin,
        "region": site.region,
        "sites": members[:20],
        "note": note,
    }


def similar_environments(
    query_id: str,
    query_site: Site,
    query_features: dict[str, Any],
    features: dict[str, dict[str, Any]],
    climate: dict[str, dict[str, Any]],
    sites: dict[str, Site],
    system: ProductionSystem,
    top_n: int = 12,
) -> dict[str, Any]:
    feats = dict(features)
    clim = dict(climate)
    all_sites = dict(sites)
    feats[query_id] = query_features
    clim[query_id] = {
        "source": query_features.get("source", "query"),
        "lat": query_site.lat,
        "trust_notes": query_features.get("trust_notes") or [],
        "chelsa": {"available": False},
        "land": {},
    }
    all_sites[query_id] = query_site
    result = shortlist_from_reference(
        query_id,
        feats,
        clim,
        all_sites,
        system=system,
        cultivar_id=query_site.cultivar,
        top_n=top_n,
    )
    # Cluster the shortlist by country / region so a Brazil pin becomes a region.
    by_region: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in result["shortlist"]:
        key = f"{row['country']} / {row['region']}"
        by_region[key].append(
            {
                "site_id": row["site_id"],
                "name": row["name"],
                "similarity": row["similarity"],
                "outcome": row["outcome"],
            }
        )
    clusters = [
        {
            "label": key,
            "n": len(rows),
            "best_similarity": max(r["similarity"] for r in rows),
            "sites": rows[:5],
        }
        for key, rows in by_region.items()
    ]
    clusters.sort(key=lambda c: -c["best_similarity"])

    se_us = [
        r
        for r in result["shortlist"]
        if r["country"] == "US" and r["lat"] < 37 and r["lat"] > 25 and r["lon"] > -92
    ]
    return {
        **result,
        "mode": "recommend",
        "region_clusters": clusters[:8],
        "southeast_us_matches": se_us[:6],
        "recommend_note": (
            "This is a recommendation of similar environments, not a claim that the "
            "exact pin is the best place. Walk the shortlist. Book the flight."
        ),
    }
