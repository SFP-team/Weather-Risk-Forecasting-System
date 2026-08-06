"""Demo farm profiles for Florida blueberry regions."""

from __future__ import annotations

import json
from typing import Any

from blueberry_common.db import connect, init_db, upsert_farm
from blueberry_common.schemas import PhenologyStage, ProductionSystem

DEMO_FARMS: list[dict[str, Any]] = [
    {
        "id": "farm-alachua-emerald",
        "name": "North Florida Emerald Block",
        "county": "Alachua",
        "lat": 29.65,
        "lon": -82.35,
        "nearest_station_id": "ALACHUA",
        "cultivars": ["Emerald", "Jewel", "Farthing"],
        "chill_requirement_hours": 300,
        "production_system": ProductionSystem.DECIDUOUS.value,
        "phenology_stage": PhenologyStage.OPEN_BLOOM.value,
        "system_rate_in_per_hr": 0.2,
        "cold_spot_bias_f": -2.0,
        "irrigation_freeze_protection": 1,
        "acres": 40.0,
    },
    {
        "id": "farm-polk-star",
        "name": "Central Florida Star & Avanti",
        "county": "Polk",
        "lat": 28.05,
        "lon": -81.72,
        "nearest_station_id": "LAKE_ALFRED",
        "cultivars": ["Star", "Avanti", "Optimus"],
        "chill_requirement_hours": 200,
        "production_system": ProductionSystem.EVERGREEN.value,
        "phenology_stage": PhenologyStage.GREEN_FRUIT.value,
        "system_rate_in_per_hr": 0.25,
        "cold_spot_bias_f": -1.0,
        "irrigation_freeze_protection": 1,
        "acres": 85.0,
    },
    {
        "id": "farm-highlands-snowchaser",
        "name": "Highlands Early Evergreen",
        "county": "Highlands",
        "lat": 27.48,
        "lon": -81.44,
        "nearest_station_id": "SEBRING",
        "cultivars": ["Snowchaser", "Kestrel", "Chickadee"],
        "chill_requirement_hours": 150,
        "production_system": ProductionSystem.EVERGREEN.value,
        "phenology_stage": PhenologyStage.HARVEST.value,
        "system_rate_in_per_hr": 0.2,
        "cold_spot_bias_f": 0.0,
        "irrigation_freeze_protection": 1,
        "acres": 25.0,
    },
]


def seed_farms() -> int:
    init_db()
    with connect() as conn:
        for f in DEMO_FARMS:
            row = {
                **f,
                "cultivars_json": json.dumps(f["cultivars"]),
            }
            del row["cultivars"]
            upsert_farm(conn, row)
    return len(DEMO_FARMS)


def list_farms() -> list[dict[str, Any]]:
    init_db()
    with connect() as conn:
        rows = conn.execute("SELECT * FROM farms ORDER BY name").fetchall()
    out = []
    for r in rows:
        d = dict(r)
        d["cultivars"] = json.loads(d.pop("cultivars_json"))
        d["irrigation_freeze_protection"] = bool(d["irrigation_freeze_protection"])
        out.append(d)
    return out


def get_farm(farm_id: str) -> dict[str, Any] | None:
    init_db()
    with connect() as conn:
        row = conn.execute("SELECT * FROM farms WHERE id=?", (farm_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    d["cultivars"] = json.loads(d.pop("cultivars_json"))
    d["irrigation_freeze_protection"] = bool(d["irrigation_freeze_protection"])
    return d


def update_farm(farm_id: str, **fields: Any) -> dict[str, Any] | None:
    farm = get_farm(farm_id)
    if not farm:
        return None
    allowed = {
        "phenology_stage",
        "cold_spot_bias_f",
        "chill_requirement_hours",
        "cultivars",
        "system_rate_in_per_hr",
    }
    for k, v in fields.items():
        if k in allowed and v is not None:
            farm[k] = v.value if hasattr(v, "value") else v
    row = {
        **farm,
        "cultivars_json": json.dumps(farm["cultivars"]),
        "irrigation_freeze_protection": int(farm["irrigation_freeze_protection"]),
    }
    del row["cultivars"]
    with connect() as conn:
        upsert_farm(conn, row)
    return get_farm(farm_id)
