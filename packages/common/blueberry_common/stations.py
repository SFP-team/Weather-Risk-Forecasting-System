"""Florida FAWN / demo station metadata for blueberry belt."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Station:
    id: str
    name: str
    county: str
    lat: float
    lon: float
    elev_m: float
    fawn_id: str | None
    region: str  # north-central | central | south-central


# Priority blueberry-belt stations (approx coords; FAWN IDs where known)
STATIONS: dict[str, Station] = {
    "ALACHUA": Station(
        id="ALACHUA",
        name="Alachua",
        county="Alachua",
        lat=29.8028,
        lon=-82.4111,
        elev_m=45.0,
        fawn_id="260",
        region="north-central",
    ),
    "PUTNAM_HALL": Station(
        id="PUTNAM_HALL",
        name="Putnam Hall",
        county="Putnam",
        lat=29.6947,
        lon=-81.9806,
        elev_m=30.0,
        fawn_id="240",
        region="north-central",
    ),
    "CITRA": Station(
        id="CITRA",
        name="Citra",
        county="Marion",
        lat=29.4119,
        lon=-82.1714,
        elev_m=22.0,
        fawn_id="250",
        region="north-central",
    ),
    "OCKLAWAHA": Station(
        id="OCKLAWAHA",
        name="Ocklawaha",
        county="Marion",
        lat=29.0431,
        lon=-81.9097,
        elev_m=20.0,
        fawn_id="280",
        region="north-central",
    ),
    "LAKE_ALFRED": Station(
        id="LAKE_ALFRED",
        name="Lake Alfred",
        county="Polk",
        lat=28.1022,
        lon=-81.7128,
        elev_m=42.0,
        fawn_id="330",
        region="central",
    ),
    "SEBRING": Station(
        id="SEBRING",
        name="Sebring",
        county="Highlands",
        lat=27.4564,
        lon=-81.4169,
        elev_m=40.0,
        fawn_id="470",
        region="south-central",
    ),
}


def list_stations() -> list[Station]:
    return list(STATIONS.values())


def get_station(station_id: str) -> Station:
    key = station_id.upper().replace(" ", "_").replace("-", "_")
    if key not in STATIONS:
        raise KeyError(f"Unknown station: {station_id}")
    return STATIONS[key]


def nearest_station(lat: float, lon: float) -> Station:
    best = None
    best_d = float("inf")
    for st in STATIONS.values():
        d = (st.lat - lat) ** 2 + (st.lon - lon) ** 2
        if d < best_d:
            best_d = d
            best = st
    assert best is not None
    return best
