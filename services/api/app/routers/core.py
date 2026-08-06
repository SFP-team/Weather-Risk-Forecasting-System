from __future__ import annotations

from datetime import date

from fastapi import APIRouter, HTTPException

from blueberry_common.db import connect, get_db_path, init_db
from blueberry_common.farms import get_farm, list_farms, seed_farms, update_farm
from blueberry_common.schemas import (
    ChillProgress,
    FarmOut,
    FarmUpdate,
    HealthOut,
    ObservationSummary,
    PhenologyStage,
    SeasonOutlook,
    SevenDayOutlook,
    StationOut,
    TonightRisk,
)
from blueberry_common.stations import STATIONS, list_stations
from blueberry_features.chill import season_chill_to_date
from blueberry_features.daily import read_features
from blueberry_ingest.load import seed_stations
from blueberry_models.seven_day import build_seven_day
from blueberry_models.train import predict_next_months
from blueberry_risk.seasonal import build_season_outlook
from blueberry_risk.tonight import evaluate_tonight

router = APIRouter()


def _ensure_seed() -> None:
    init_db()
    seed_stations()
    if not list_farms():
        seed_farms()


@router.get("/health", response_model=HealthOut)
def health():
    _ensure_seed()
    farms = list_farms()
    return HealthOut(
        status="ok",
        version="0.1.0",
        database=str(get_db_path()),
        stations=len(STATIONS),
        farms=len(farms),
    )


@router.get("/stations", response_model=list[StationOut])
def stations():
    _ensure_seed()
    return [
        StationOut(
            id=s.id,
            name=s.name,
            county=s.county,
            lat=s.lat,
            lon=s.lon,
            elev_m=s.elev_m,
            region=s.region,
            fawn_id=s.fawn_id,
        )
        for s in list_stations()
    ]


@router.get("/farms", response_model=list[FarmOut])
def farms():
    _ensure_seed()
    out = []
    for f in list_farms():
        out.append(FarmOut(**{k: f[k] for k in FarmOut.model_fields.keys()}))
    return out


@router.get("/farms/{farm_id}", response_model=FarmOut)
def farm_detail(farm_id: str):
    _ensure_seed()
    f = get_farm(farm_id)
    if not f:
        raise HTTPException(404, "Farm not found")
    return FarmOut(**{k: f[k] for k in FarmOut.model_fields.keys()})


@router.patch("/farms/{farm_id}", response_model=FarmOut)
def farm_patch(farm_id: str, body: FarmUpdate):
    _ensure_seed()
    f = update_farm(farm_id, **body.model_dump(exclude_unset=True))
    if not f:
        raise HTTPException(404, "Farm not found")
    return FarmOut(**{k: f[k] for k in FarmOut.model_fields.keys()})


def _station_dict(station_id: str) -> dict:
    st = STATIONS[station_id]
    return {
        "id": st.id,
        "name": st.name,
        "county": st.county,
        "lat": st.lat,
        "lon": st.lon,
        "elev_m": st.elev_m,
        "region": st.region,
        "fawn_id": st.fawn_id,
    }


@router.get("/farms/{farm_id}/tonight", response_model=TonightRisk)
def tonight(farm_id: str, live: bool = True):
    _ensure_seed()
    f = get_farm(farm_id)
    if not f:
        raise HTTPException(404, "Farm not found")
    st = _station_dict(f["nearest_station_id"])
    return evaluate_tonight(f, st, live=live)


@router.get("/farms/{farm_id}/seven-day", response_model=SevenDayOutlook)
def seven_day(farm_id: str):
    _ensure_seed()
    f = get_farm(farm_id)
    if not f:
        raise HTTPException(404, "Farm not found")
    st = _station_dict(f["nearest_station_id"])
    return build_seven_day(f, st)


@router.get("/farms/{farm_id}/season", response_model=SeasonOutlook)
def season(farm_id: str):
    _ensure_seed()
    f = get_farm(farm_id)
    if not f:
        raise HTTPException(404, "Farm not found")
    feat = read_features(f["nearest_station_id"])
    model_cards = predict_next_months(f["nearest_station_id"], n_months=3)
    # Fill chill shortfall using requirement
    req = int(f["chill_requirement_hours"])
    chill = season_chill_to_date(feat) if not feat.empty else 0.0
    for c in model_cards:
        p50 = c.get("chill_hours_p50") or 0
        # cumulative-ish shortfall probability heuristic
        c["p_chill_shortfall"] = round(
            max(0.05, min(0.9, (req - (chill + float(p50))) / max(req, 1) * 0.8 + 0.1)),
            3,
        )
    return build_season_outlook(f, feat, model_cards=model_cards or None)


@router.get("/farms/{farm_id}/chill", response_model=ChillProgress)
def chill(farm_id: str):
    _ensure_seed()
    f = get_farm(farm_id)
    if not f:
        raise HTTPException(404, "Farm not found")
    feat = read_features(f["nearest_station_id"])
    hours = season_chill_to_date(feat) if not feat.empty else 0.0
    req = int(f["chill_requirement_hours"])
    pct = min(100.0, 100.0 * hours / req) if req else 0.0
    from blueberry_risk.seasonal import chill_status

    return ChillProgress(
        farm_id=farm_id,
        station_id=f["nearest_station_id"],
        as_of=date.today(),
        chill_hours=round(hours, 1),
        requirement_hours=req,
        pct_complete=round(pct, 1),
        status=chill_status(hours, req),  # type: ignore[arg-type]
    )


@router.get("/stations/{station_id}/observations", response_model=list[ObservationSummary])
def observations(station_id: str, limit: int = 30):
    _ensure_seed()
    if station_id not in STATIONS:
        raise HTTPException(404, "Station not found")
    feat = read_features(station_id)
    if feat.empty:
        return []
    feat = feat.sort_values("date", ascending=False).head(limit)
    out = []
    for _, r in feat.iterrows():
        out.append(
            ObservationSummary(
                station_id=station_id,
                date=r["date"],
                tmin_f=r.get("tmin_f"),
                tmax_f=r.get("tmax_f"),
                precip_in=r.get("precip_in"),
                rh_mean=None,
                wind_mean_mph=None,
                chill_hours=r.get("chill_hours"),
                freeze_le_32=bool(r.get("freeze_le_32")),
            )
        )
    return out


@router.get("/meta/metrics")
def metrics():
    from blueberry_common.config import get_settings
    import json

    path = get_settings().metrics_dir / "seasonal_metrics.json"
    if not path.exists():
        return {"status": "no_metrics", "hint": "Run: python pipelines/run_all.py"}
    return json.loads(path.read_text())


@router.post("/admin/reseed")
def reseed():
    """Dev helper: ensure stations + farms exist."""
    seed_stations()
    n = seed_farms()
    return {"farms": n, "stations": len(STATIONS)}
