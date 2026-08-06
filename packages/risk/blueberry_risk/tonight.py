"""Tonight freeze decision engine for Florida blueberries.

Rules grounded in UF/IFAS practice (HS216 / FAWN cold protection concepts).
Decision support only — not a substitute for NWS or field thermometers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from blueberry_common.schemas import (
    Confidence,
    PhenologyStage,
    TonightRisk,
    TonightStatus,
)
from blueberry_ingest.nws import fetch_point_forecast, summarize_nws_for_tonight
from blueberry_ingest.open_meteo import fetch_hourly_tonight


# Approximate stage critical temps (°F) — guidance ranges for SHB
STAGE_CRITICAL_F = {
    PhenologyStage.DORMANT: 20.0,
    PhenologyStage.SWELL: 24.0,
    PhenologyStage.PINK: 26.0,
    PhenologyStage.OPEN_BLOOM: 28.0,
    PhenologyStage.PETAL_FALL: 28.0,
    PhenologyStage.GREEN_FRUIT: 28.0,
    PhenologyStage.HARVEST: 30.0,
}


def start_threshold_f(dewpoint_f: float | None, stage: PhenologyStage) -> float:
    """Open-sky start guidance: earlier when air is very dry."""
    base = 32.0
    if dewpoint_f is not None and dewpoint_f < 25:
        base = 34.0
    elif dewpoint_f is not None and dewpoint_f < 28:
        base = 33.0
    # Dormant: rarely protect
    if stage == PhenologyStage.DORMANT:
        return 28.0
    return base


def evaluate_tonight(
    farm: dict[str, Any],
    station: dict[str, Any],
    live: bool = True,
) -> TonightRisk:
    stage = PhenologyStage(farm["phenology_stage"])
    bias = float(farm.get("cold_spot_bias_f") or 0.0)
    system_rate = float(farm.get("system_rate_in_per_hr") or 0.2)

    tmin = None
    dewpoint = None
    wind = None
    coldest_hour = None
    sources: list[str] = []

    if live:
        hourly = fetch_hourly_tonight(
            type("S", (), {"lat": station["lat"], "lon": station["lon"], "id": station["id"]})()
        )
        if hourly:
            sources.append("Open-Meteo hourly")
            # Night window: 18:00–08:00 local-ish by parsing hours
            night = []
            for h in hourly:
                try:
                    hour = int(str(h["time"])[11:13])
                except Exception:
                    hour = 0
                if hour >= 18 or hour <= 8:
                    night.append(h)
            use = night or hourly
            temps = [h["temp_f"] for h in use if h.get("temp_f") is not None]
            dps = [h["dewpoint_f"] for h in use if h.get("dewpoint_f") is not None]
            winds = [h["wind_mph"] for h in use if h.get("wind_mph") is not None]
            if temps:
                idx = min(range(len(use)), key=lambda i: use[i].get("temp_f") or 999)
                tmin = min(temps)
                coldest_hour = str(use[idx].get("time"))
            if dps:
                dewpoint = sum(dps) / len(dps)
            if winds:
                wind = sum(winds) / len(winds)

        nws = fetch_point_forecast(
            type("S", (), {"lat": station["lat"], "lon": station["lon"], "id": station["id"]})()
        )
        summary = summarize_nws_for_tonight(nws)
        if summary:
            sources.append("NWS")
            if summary.get("tmin_f") is not None:
                if tmin is None:
                    tmin = summary["tmin_f"]
                else:
                    tmin = min(tmin, summary["tmin_f"])
            if summary.get("wind_mph") is not None and wind is None:
                wind = summary["wind_mph"]
            if summary.get("alerts"):
                sources.append("NWS alerts: " + ", ".join(summary["alerts"][:2]))

    # Fallback synthetic mild night if no live data
    if tmin is None:
        tmin = 48.0
        dewpoint = dewpoint if dewpoint is not None else 42.0
        wind = wind if wind is not None else 4.0
        sources.append("fallback climatology (live fetch unavailable)")
        confidence = Confidence.LOW
    else:
        confidence = Confidence.HIGH if "NWS" in " ".join(sources) else Confidence.MED

    # Apply cold-spot bias (negative means farm colder)
    effective_tmin = tmin + bias

    critical = STAGE_CRITICAL_F.get(stage, 28.0)
    start_thr = start_threshold_f(dewpoint, stage)
    wind_mph = wind or 0.0

    # Beyond system: cold + windy relative to typical 0.2 in/hr systems
    beyond = (
        farm.get("irrigation_freeze_protection")
        and effective_tmin <= 26
        and wind_mph >= 8
        and stage not in (PhenologyStage.DORMANT,)
    )
    if beyond and system_rate < 0.35 and effective_tmin <= 24 and wind_mph >= 10:
        beyond = True

    status = TonightStatus.LOW
    if stage == PhenologyStage.DORMANT and effective_tmin > 22:
        status = TonightStatus.LOW
    elif beyond:
        status = TonightStatus.BEYOND_SYSTEM
    elif effective_tmin <= critical or effective_tmin <= 30 and stage in (
        PhenologyStage.OPEN_BLOOM,
        PhenologyStage.PETAL_FALL,
        PhenologyStage.GREEN_FRUIT,
        PhenologyStage.PINK,
        PhenologyStage.HARVEST,
    ):
        status = TonightStatus.PROTECT
    elif effective_tmin <= 34 and stage != PhenologyStage.DORMANT:
        status = TonightStatus.WATCH
    elif effective_tmin <= 36 and stage in (PhenologyStage.OPEN_BLOOM, PhenologyStage.GREEN_FRUIT):
        status = TonightStatus.WATCH

    headlines = {
        TonightStatus.LOW: "Low freeze risk — no protection expected tonight.",
        TonightStatus.WATCH: "Watch — cold spots may approach critical temps.",
        TonightStatus.PROTECT: "Protect — plan to run overhead irrigation.",
        TonightStatus.BEYOND_SYSTEM: "Beyond system — wind + cold may exceed typical irrigation design.",
    }

    weather_fact = (
        f"Forecast low ~{effective_tmin:.0f}°F at farm "
        f"(model {tmin:.0f}°F, bias {bias:+.0f}°F); "
        f"dew point ~{(dewpoint if dewpoint is not None else float('nan')):.0f}°F; "
        f"wind ~{wind_mph:.0f} mph."
    )
    crop_meaning = (
        f"Stage {stage.value.replace('_', ' ').title()}: "
        f"guidance critical ~{critical:.0f}°F. "
        "Open flowers and young fruit are most vulnerable; "
        "dry air and calm winds increase radiational freeze risk."
    )

    actions = {
        TonightStatus.LOW: "No freeze run expected. Keep system ready for mid-season surprises; recheck at 9 pm.",
        TonightStatus.WATCH: (
            f"Set alarms; wet ground optional this afternoon. "
            f"Start if cold-spot thermometer reaches ~{start_thr:.0f}°F. Recheck 9 pm and 1 am."
        ),
        TonightStatus.PROTECT: (
            f"Assign pump person; fuel check by 5 pm. "
            f"Start when open-sky thermometer in coldest spot hits ~{start_thr:.0f}°F. "
            "Do not shut off until ice is melting hard."
        ),
        TonightStatus.BEYOND_SYSTEM: (
            "Wind + cold may exceed 0.2 in/hr protection. "
            "Choose which blocks to save; do not assume full acreage save. "
            "Follow IFAS tables for your system design."
        ),
    }

    checklist = [
        "Inspect diesel fuel and pump readiness",
        "Check nozzles / risers / drains",
        "Place calibrated thermometer in coldest block at flower height",
        f"Start guidance ~{start_thr:.0f}°F open-sky (adjust for dew point)",
        "Do not shut off before ice is melting vigorously",
        "After protect night: scout for Botrytis / wetness disease risk",
    ]

    return TonightRisk(
        farm_id=farm["id"],
        status=status,
        headline=headlines[status],
        weather_fact=weather_fact,
        crop_meaning=crop_meaning,
        suggested_action=actions[status],
        forecast_tmin_f=round(effective_tmin, 1),
        dewpoint_f=round(dewpoint, 1) if dewpoint is not None else None,
        wind_mph=round(wind_mph, 1),
        coldest_hour_local=coldest_hour,
        start_threshold_f=start_thr,
        confidence=confidence,
        sources=sources or ["local rules"],
        checklist=checklist,
        generated_at=datetime.now(timezone.utc),
    )
