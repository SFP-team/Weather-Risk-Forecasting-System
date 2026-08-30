"""Targeted risk factors from weather, scored against the SE US gradient.

Within-window is not the same as comfortable. A 51 next to a 90 is a watch.
Harvest rain is the headline factor from the breeding-program briefing.
"""

from __future__ import annotations

from typing import Any

from blueberry_analogue.systems import ProductionSystem, system_effects


# Southeast US success belt (Miami evergreen → North Carolina deciduous).
# Used as the "where we already grow SHB" window, not a global optimum.
SE_US_WINDOW = {
    "chill_hours": (80.0, 900.0),
    "frost_days": (0.0, 18.0),
    "harvest_rain_days": (2.0, 14.0),
    "dli_fruit": (18.0, 42.0),
    "days_berry_gt_42": (0.0, 10.0),
    "drought_events_p50": (0.0, 8.0),
}

# Comfortable interior of that window. Borderline if inside window but outside this.
SE_US_COMFORT = {
    "chill_hours": (150.0, 700.0),
    "frost_days": (0.0, 8.0),
    "harvest_rain_days": (2.0, 8.0),
    "dli_fruit": (22.0, 38.0),
    "days_berry_gt_42": (0.0, 4.0),
    "drought_events_p50": (0.0, 4.0),
}


def _status(value: float, window: tuple[float, float], comfort: tuple[float, float], high_is_bad: bool) -> str:
    if value != value:  # NaN
        return "unknown"
    lo, hi = window
    clo, chi = comfort
    if high_is_bad:
        if value > hi * 1.35:
            return "extreme"
        if value > hi:
            return "concerning"
        if value > chi:
            return "borderline"
        return "comfortable"
    # low is bad (chill too low, DLI too low)
    if value < lo * 0.55:
        return "extreme"
    if value < lo:
        return "concerning"
    if value < clo:
        return "borderline"
    if value > hi:
        return "concerning"
    if value > chi:
        return "borderline"
    return "comfortable"


def _band(value: float, window: tuple[float, float]) -> dict[str, float | str]:
    lo, hi = window
    if value != value:
        return {"value": value, "window_lo": lo, "window_hi": hi, "position": "unknown"}
    if value < lo:
        return {"value": value, "window_lo": lo, "window_hi": hi, "position": "below"}
    if value > hi:
        return {"value": value, "window_lo": lo, "window_hi": hi, "position": "above"}
    span = max(1e-6, hi - lo)
    return {"value": value, "window_lo": lo, "window_hi": hi, "position": "inside", "pct": (value - lo) / span}


def assess_risk_factors(
    stats: dict[str, Any],
    system: ProductionSystem,
    habit: str,
) -> list[dict[str, Any]]:
    effects = system_effects(system)
    rain_days = float(stats.get("harvest_rain_days") or 0.0) * effects.rain_crack_multiplier
    frost_days = float(stats.get("frost_days_p50") or 0.0) * effects.freeze_water_factor
    chill = float(stats.get("chill_hours_p50") or 0.0)
    dli = float(stats.get("dli_fruit") or 0.0) * effects.dli_multiplier
    heat = float(stats.get("days_berry_gt_42") or 0.0)
    drought = float(stats.get("drought_events_p50") or 0.0)

    items: list[dict[str, Any]] = []

    chill_status = _status(chill, SE_US_WINDOW["chill_hours"], SE_US_COMFORT["chill_hours"], high_is_bad=False)
    if habit == "evergreen":
        chill_status = "comfortable" if chill < 250 else "borderline"
        chill_msg = (
            "Evergreen clock. Low chill is expected. Do not chase a high-chill genotype."
            if chill < 250
            else "Chill is high for an evergreen recommendation. A deciduous or semi-evergreen clock may fit better."
        )
    elif chill_status in {"concerning", "extreme", "borderline"} and chill < SE_US_COMFORT["chill_hours"][0]:
        chill_msg = (
            "Chill is low. Recommend a genotype that does not need a lot of cold to flower. "
            "If it is only barely inside the SE US window, treat it as critical, not fine."
        )
    elif chill > SE_US_COMFORT["chill_hours"][1]:
        chill_msg = "Chill is high. High-chill SHB or northern highbush will use this winter."
    else:
        chill_msg = "Winter chill sits inside the Florida-to-Carolina belt."
    items.append(
        {
            "id": "chill",
            "label": "Winter chill hours",
            "status": chill_status,
            "unit": "hours 0–7.2 °C",
            **_band(chill, SE_US_WINDOW["chill_hours"]),
            "message": chill_msg,
            "mitigation": "HCN rewrites the envelope. Tunnels do not restore chill.",
        }
    )

    frost_status = _status(frost_days, SE_US_WINDOW["frost_days"], SE_US_COMFORT["frost_days"], high_is_bad=True)
    if effects.freeze_water_factor < 0.2:
        frost_status = "comfortable"
        frost_msg = "Tunnels or a greenhouse hide bloom freeze. The open field may still be a freeze site."
    elif frost_days <= 1:
        frost_msg = "Freezes are rare. That is fine. It also means high-chill deciduous types may not get the winter they want."
    else:
        frost_msg = "Bloom freeze is a real risk. Evergreen genotypes flower early and lose the crop if unprotected."
    items.append(
        {
            "id": "freeze",
            "label": "Winter / bloom freeze days",
            "status": frost_status,
            "unit": "days tmin ≤ 0 °C",
            **_band(frost_days, SE_US_WINDOW["frost_days"]),
            "message": frost_msg,
            "mitigation": "Tunnels, overhead, or a later-bloom deciduous genotype.",
        }
    )

    rain_status = _status(
        rain_days, SE_US_WINDOW["harvest_rain_days"], SE_US_COMFORT["harvest_rain_days"], high_is_bad=True
    )
    if rain_days > SE_US_COMFORT["harvest_rain_days"][1]:
        rain_msg = (
            "Rainfall during harvest is the headline risk. Fruit can split. "
            "Need a crack-tolerant genotype, or a system that drains and/or excludes rain."
        )
    else:
        rain_msg = "Harvest rain is inside the SE US comfort band."
    items.append(
        {
            "id": "harvest_rain",
            "label": "Rain during harvest",
            "status": rain_status,
            "unit": "days ≥ 5 mm in harvest window / year",
            **_band(rain_days, SE_US_WINDOW["harvest_rain_days"]),
            "message": rain_msg,
            "mitigation": "Tunnels exclude rain. Pots drain the root zone but do not stop fruit split.",
            "priority": "high",
        }
    )

    if dli != dli:
        dli_status = "unknown"
    elif dli < SE_US_WINDOW["dli_fruit"][0]:
        dli_status = "concerning" if dli >= SE_US_WINDOW["dli_fruit"][0] * 0.55 else "extreme"
    elif dli < SE_US_COMFORT["dli_fruit"][0]:
        dli_status = "borderline"
    else:
        dli_status = "comfortable"
    if dli < SE_US_COMFORT["dli_fruit"][0]:
        dli_msg = (
            "Solar radiation during fruit fill is low (cloudy). Sugars and color can suffer. "
            "Look for genotypes that finish under lower light, or open the cover."
        )
    else:
        dli_msg = "Fruit-fill light is adequate versus the SE US belt."
    items.append(
        {
            "id": "low_solar",
            "label": "Fruit-fill solar / DLI",
            "status": dli_status,
            "unit": "mol m⁻² d⁻¹",
            **_band(dli, SE_US_WINDOW["dli_fruit"]),
            "message": dli_msg,
            "mitigation": "Covers cut PAR. LDPE and tunnels make a dim site dimmer.",
        }
    )

    heat_status = _status(
        heat, SE_US_WINDOW["days_berry_gt_42"], SE_US_COMFORT["days_berry_gt_42"], high_is_bad=True
    )
    items.append(
        {
            "id": "heat",
            "label": "Berry-surface heat",
            "status": heat_status,
            "unit": "days sun-side ≥ 42 °C",
            **_band(heat, SE_US_WINDOW["days_berry_gt_42"]),
            "message": (
                "Heat during fruit is a quality risk. Soft fruit and sunburn."
                if heat_status in {"borderline", "concerning", "extreme"}
                else "Berry heat is not the leading problem here."
            ),
            "mitigation": "Shade net trades DLI for cooler berries. Nets do not restore chill.",
        }
    )

    drought_status = _status(
        drought, SE_US_WINDOW["drought_events_p50"], SE_US_COMFORT["drought_events_p50"], high_is_bad=True
    )
    items.append(
        {
            "id": "drought",
            "label": "Dry spells in the warm season",
            "status": drought_status,
            "unit": "30-day < 15 mm events / year",
            **_band(drought, SE_US_WINDOW["drought_events_p50"]),
            "message": (
                "Drought incidence is elevated. Irrigation and pine-bark or substrate matter."
                if drought_status in {"borderline", "concerning", "extreme"}
                else "Warm-season dry spells look ordinary versus the SE US belt."
            ),
            "mitigation": "This tool does not check water rights.",
        }
    )

    order = {"extreme": 0, "concerning": 1, "borderline": 2, "comfortable": 3, "unknown": 4}
    items.sort(key=lambda r: (0 if r.get("priority") == "high" else 1, order.get(r["status"], 9)))
    return items
