"""7-day outlook builder using Open-Meteo forecast when available."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from blueberry_common.schemas import DayOutlook, SevenDayOutlook
from blueberry_ingest.open_meteo import fetch_forecast


def build_seven_day(farm: dict[str, Any], station: dict[str, Any]) -> SevenDayOutlook:
    st = type("S", (), station)()
    df = fetch_forecast(st, days=7)
    days: list[DayOutlook] = []
    sources = []
    if df is not None and not df.empty:
        sources.append("Open-Meteo forecast")
        for _, r in df.iterrows():
            tmin = r.get("tmin_f")
            precip = r.get("precip_in") or 0
            freeze = "low"
            if tmin is not None:
                if tmin <= 30:
                    freeze = "high"
                elif tmin <= 34:
                    freeze = "moderate"
            disease = "low"
            if precip and precip >= 0.25:
                disease = "moderate"
            if precip and precip >= 0.5:
                disease = "high"
            harvest = "high" if precip and precip >= 0.5 else ("moderate" if precip and precip >= 0.2 else "low")
            days.append(
                DayOutlook(
                    date=r["date"],
                    tmin_f=float(tmin) if tmin is not None else None,
                    tmax_f=float(r["tmax_f"]) if r.get("tmax_f") is not None else None,
                    precip_in=float(precip) if precip is not None else None,
                    freeze_risk=freeze,  # type: ignore[arg-type]
                    disease_wetness_risk=disease,  # type: ignore[arg-type]
                    harvest_rain_risk=harvest,  # type: ignore[arg-type]
                )
            )
    else:
        sources.append("climatology placeholder")
        from datetime import date, timedelta

        for i in range(7):
            d = date.today() + timedelta(days=i)
            days.append(
                DayOutlook(
                    date=d,
                    tmin_f=55,
                    tmax_f=82,
                    precip_in=0.05,
                    freeze_risk="low",
                    disease_wetness_risk="low",
                    harvest_rain_risk="low",
                    notes="Live forecast unavailable",
                )
            )

    return SevenDayOutlook(
        farm_id=farm["id"],
        days=days,
        sources=sources,
        generated_at=datetime.now(timezone.utc),
    )
