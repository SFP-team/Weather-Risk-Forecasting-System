"""Download grids for the campus weather bot.

These are the points we actually need for diagnose + recommend-where.
They are not a global hourly cube.
"""

from __future__ import annotations

from dataclasses import dataclass

from blueberry_analogue.sites import load_sites
from blueberry_analogue.weather.store import point_id_for

# Coarse continent boxes. Used only to skip mid-ocean 1° cells.
_CONTINENTS = (
    (7.0, 72.0, -168.0, -52.0),  # North America
    (-56.0, 15.0, -82.0, -34.0),  # South America
    (34.0, 72.0, -12.0, 40.0),  # Europe
    (-35.0, 38.0, -18.0, 52.0),  # Africa
    (5.0, 77.0, 26.0, 180.0),  # Asia
    (5.0, 77.0, -180.0, -168.0),  # far-east wrap
    (-47.0, -10.0, 112.0, 180.0),  # Australia / NZ
)

# Blueberry belts we will query a lot. Denser than the 1° globe.
BELTS: dict[str, tuple[float, float, float, float, float]] = {
    "se_us": (25.0, 37.0, -92.0, -75.0, 0.25),
    "chile": (-42.0, -30.0, -74.0, -69.0, 0.25),
    "brazil_south": (-32.0, -20.0, -55.0, -42.0, 0.25),
    "peru": (-18.0, -5.0, -80.0, -70.0, 0.5),
    "mexico": (18.0, 32.0, -110.0, -96.0, 0.5),
    "iberia": (36.0, 44.0, -10.0, 0.0, 0.5),
    "morocco": (30.0, 36.0, -10.0, -4.0, 0.5),
    "australia": (-44.0, -27.0, 114.0, 154.0, 0.5),
    "nz": (-47.0, -34.0, 166.0, 179.0, 0.5),
}


@dataclass(frozen=True)
class GridPoint:
    point_id: str
    lat: float
    lon: float
    name: str
    kind: str


def probably_land(lat: float, lon: float) -> bool:
    for lat0, lat1, lon0, lon1 in _CONTINENTS:
        if lat0 <= lat <= lat1 and lon0 <= lon <= lon1:
            return True
    return False


def _box_points(lat0: float, lat1: float, lon0: float, lon1: float, step: float, kind: str) -> list[GridPoint]:
    out: list[GridPoint] = []
    lat = lat0
    while lat <= lat1 + 1e-9:
        lon = lon0
        while lon <= lon1 + 1e-9:
            la = round(float(lat), 3)
            lo = round(float(lon), 3)
            out.append(
                GridPoint(
                    point_id=point_id_for(la, lo),
                    lat=la,
                    lon=lo,
                    name=f"{kind} {la:.2f},{lo:.2f}",
                    kind=kind,
                )
            )
            lon += step
        lat += step
    return out


def catalog_points() -> list[GridPoint]:
    return [
        GridPoint(
            point_id=site.site_id,
            lat=site.lat,
            lon=site.lon,
            name=site.name,
            kind="catalog",
        )
        for site in load_sites()
    ]


def global_1deg_points() -> list[GridPoint]:
    return [
        p
        for p in _box_points(-55.0, 60.0, -180.0, 179.0, 1.0, "global_1")
        if probably_land(p.lat, p.lon)
    ]


def belt_points(name: str) -> list[GridPoint]:
    lat0, lat1, lon0, lon1, step = BELTS[name]
    return _box_points(lat0, lat1, lon0, lon1, step, name)


def dedupe(points: list[GridPoint]) -> list[GridPoint]:
    seen: set[str] = set()
    out: list[GridPoint] = []
    for point in points:
        if point.point_id in seen:
            continue
        seen.add(point.point_id)
        out.append(point)
    return out


PLANS: dict[str, tuple[str, ...]] = {
    "tonight": ("catalog",),
    "future": ("catalog", "global_1", *BELTS.keys()),
    "belts": tuple(BELTS.keys()),
}


def plan_points(plan: str) -> list[GridPoint]:
    if plan not in PLANS:
        raise KeyError(f"Unknown plan {plan}. Known: {sorted(PLANS)}")
    chunks: list[GridPoint] = []
    for part in PLANS[plan]:
        if part == "catalog":
            chunks.extend(catalog_points())
        elif part == "global_1":
            chunks.extend(global_1deg_points())
        else:
            chunks.extend(belt_points(part))
    return dedupe(chunks)


def plan_estimate(plan: str) -> dict[str, float | int | str]:
    """Rough disk and time. POWER daily ~200 KB stored per point after SQLite."""
    n = len(plan_points(plan))
    mb = n * 0.22
    hours_serial = n * 2.0 / 3600.0
    return {
        "plan": plan,
        "points": n,
        "disk_mb": round(mb, 1),
        "disk_note": "SQLite daily 10-year series, not ERA5 hourly.",
        "hours_at_4_workers": round(hours_serial / 4.0, 1),
        "hours_note": "NASA POWER point API. Rate limits can stretch this.",
    }
