"""FastAPI shortlist service. Separate from the Florida farm demo."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from blueberry_analogue.analogue.engine import INVESTIGATION, shortlist_from_reference
from blueberry_analogue.cards import list_classes, list_cultivars, load_cards
from blueberry_analogue.pipeline import build_all, climate_for_features, load_feature_cache
from blueberry_analogue.sites import load_sites
from blueberry_analogue.systems import parse_system

WEB_DIR = Path(__file__).resolve().parents[3] / "apps" / "analogue-web"


class ShortlistRequest(BaseModel):
    reference_id: str
    cultivar_id: str | None = None
    media: str = "open_soil"
    structure: str = "open"
    cover: str = "none"
    habit: str = "deciduous"
    hcn: bool = False
    pollinator: str = "apis"
    market_start_week: int | None = None
    market_end_week: int | None = None
    top_n: int = Field(default=12, ge=3, le=40)


@lru_cache(maxsize=1)
def _state() -> dict[str, Any]:
    features = load_feature_cache()
    if features is None:
        build_all(live=False)
        features = load_feature_cache()
    assert features is not None
    sites = {s.site_id: s for s in load_sites()}
    return {
        "features": features,
        "sites": sites,
        "climate": climate_for_features(features),
        "cards": load_cards(),
    }


def create_app() -> FastAPI:
    app = FastAPI(
        title="Blueberry Analogue",
        description=(
            "Shortlist places worth testing for a blueberry variety and system. "
            "Not a plant-here button. Not a substitute for a field visit."
        ),
        version="0.1.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health():
        st = _state()
        return {
            "status": "ok",
            "product": "blueberry-analogue",
            "sites": len(st["sites"]),
            "features": len(st["features"]),
            "disclaimer": "Shortlist only. Book the flight. Do not plant 20 ha.",
        }

    @app.get("/api/cards")
    def cards():
        return {
            "classes": [c.model_dump() for c in list_classes()],
            "cultivars": [c.model_dump() for c in list_cultivars()],
            "stages": [s.model_dump() for s in load_cards().stages],
        }

    @app.get("/api/sites")
    def sites():
        st = _state()
        rows = []
        for site in st["sites"].values():
            feat = st["features"].get(site.site_id, {})
            rows.append(
                {
                    **site.model_dump(),
                    "chill_portions": feat.get("chill_portions"),
                    "chill_hours": feat.get("chill_hours"),
                    "source": feat.get("source"),
                }
            )
        return rows

    @app.get("/api/sites.geojson")
    def sites_geojson():
        st = _state()
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [s.lon, s.lat]},
                    "properties": {
                        "site_id": s.site_id,
                        "name": s.name,
                        "region": s.region,
                        "country": s.country,
                        "cultivar": s.cultivar,
                        "cultivar_class": s.cultivar_class,
                        "outcome": s.outcome,
                        "system": s.system.label,
                    },
                }
                for s in st["sites"].values()
            ],
        }

    @app.get("/api/investigation")
    def investigation():
        return {"steps": INVESTIGATION}

    @app.post("/api/shortlist")
    def shortlist(req: ShortlistRequest):
        st = _state()
        if req.reference_id not in st["features"]:
            raise HTTPException(404, f"Unknown reference {req.reference_id}")
        system = parse_system(
            media=req.media,
            structure=req.structure,
            cover=req.cover,
            habit=req.habit,
            hcn=req.hcn,
            pollinator=req.pollinator,
        )
        market = None
        if req.market_start_week is not None and req.market_end_week is not None:
            market = (req.market_start_week, req.market_end_week)
        result = shortlist_from_reference(
            req.reference_id,
            st["features"],
            st["climate"],
            st["sites"],
            system=system,
            cultivar_id=req.cultivar_id,
            market_weeks=market,
            top_n=req.top_n,
        )
        return result

    if WEB_DIR.exists():
        app.mount("/", StaticFiles(directory=str(WEB_DIR), html=True), name="web")

    return app


app = create_app()


def run() -> None:
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8010, reload=False)
