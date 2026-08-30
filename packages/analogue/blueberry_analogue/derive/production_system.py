"""Classify open-field habit from weather, then apply tunnel/pot modifiers.

Thresholds are provisional. Patricia and Gerardo lock the numbers.
Semi-evergreen is a gradient, not a third species.
"""

from __future__ import annotations

from typing import Any

from blueberry_analogue.systems import ProductionSystem, system_effects


# Open-field rules. Documented so a meeting can change one place.
EVERGREEN_CHILL_MAX = 180.0
EVERGREEN_FROST_MAX = 2.0
EVERGREEN_TMIN_P10_MIN = 1.5
DECIDUOUS_CHILL_MIN = 420.0
DECIDUOUS_TMIN_P10_MAX = -1.2
DECIDUOUS_HARD_FREEZE_MIN = 6.0


def classify_production_system(stats: dict[str, Any]) -> dict[str, Any]:
    chill = float(stats.get("chill_hours_p50") or 0.0)
    frost = float(stats.get("frost_days_p50") or 0.0)
    hard = float(stats.get("hard_freeze_days_p50") or 0.0)
    tmin_p10 = float(stats.get("winter_tmin_p10") if stats.get("winter_tmin_p10") is not None else 99.0)

    reasons: list[str] = []
    evergreen_ok = chill < EVERGREEN_CHILL_MAX and frost <= EVERGREEN_FROST_MAX and tmin_p10 >= EVERGREEN_TMIN_P10_MIN
    deciduous_ok = chill >= DECIDUOUS_CHILL_MIN or tmin_p10 < DECIDUOUS_TMIN_P10_MAX or hard >= DECIDUOUS_HARD_FREEZE_MIN

    if evergreen_ok and not deciduous_ok:
        habit = "evergreen"
        confidence = 0.82 if chill < 80 else 0.7
        reasons.append(f"Median winter chill {chill:.0f} h is below the evergreen gate ({EVERGREEN_CHILL_MAX:.0f} h).")
        reasons.append(f"Winter frost days {frost:.1f}; winter tmin p10 {tmin_p10:.1f} °C.")
    elif deciduous_ok:
        habit = "deciduous"
        confidence = 0.84 if chill >= 600 or tmin_p10 < -4 else 0.72
        reasons.append(f"Median winter chill {chill:.0f} h and/or winter tmin p10 {tmin_p10:.1f} °C.")
        if hard >= DECIDUOUS_HARD_FREEZE_MIN:
            reasons.append(f"Hard freezes ({hard:.1f} days ≤ −2.2 °C) push the clock toward deciduous.")
    else:
        habit = "semi_evergreen"
        confidence = 0.62
        reasons.append(
            f"Between the Florida evergreen and deciduous gates "
            f"(chill {chill:.0f} h, frost {frost:.1f} d, tmin p10 {tmin_p10:.1f} °C)."
        )
        reasons.append("This is a gradient. North-central Florida to Ocala is the mental model.")

    return {
        "habit": habit,
        "confidence": confidence,
        "open_field": True,
        "chill_hours_p50": chill,
        "frost_days_p50": frost,
        "hard_freeze_days_p50": hard,
        "winter_tmin_p10": tmin_p10,
        "reasons": reasons,
        "thresholds": {
            "evergreen_chill_max": EVERGREEN_CHILL_MAX,
            "deciduous_chill_min": DECIDUOUS_CHILL_MIN,
            "note": "Provisional. Sit with Patricia and Gerardo before treating these as law.",
        },
    }


def apply_structure_modifiers(
    open_field: dict[str, Any],
    system: ProductionSystem,
) -> dict[str, Any]:
    """Tunnels and pots do not rewrite the weather. They change what you can grow.

    Tunnel: bloom freeze and harvest rain collapse. Evergreen or semi-evergreen
    becomes viable in a deciduous climate if the grower wants that clock.
    Pots / substrate: drainage risk drops; fruit-split rain still hits unless
    the structure also excludes rain.
    """
    effects = system_effects(system)
    field_habit = open_field["habit"]
    allowed = [field_habit]
    notes = list(effects.notes)

    if system.structure in {"tunnel", "greenhouse"}:
        if field_habit == "deciduous":
            allowed = ["deciduous", "semi_evergreen", "evergreen"]
            notes.append(
                "Tunnels protect early bloom. An evergreen or semi-evergreen genotype "
                "can run here even though the open field is deciduous (Waldo-style)."
            )
        elif field_habit == "semi_evergreen":
            allowed = ["semi_evergreen", "evergreen", "deciduous"]
            notes.append("Tunnels open the evergreen clock and still allow deciduous.")
        else:
            allowed = ["evergreen", "semi_evergreen"]
            notes.append("Open field is already evergreen. Tunnels mainly buy heat and rain control.")
        notes.append("Tunnels do not restore chill. They hide freeze and harvest rain.")
    elif system.media == "substrate":
        notes.append(
            "Pots drain. Heavy rain is less of a root problem. Berries can still split "
            "if fruit is exposed. Pair pots with a cover if harvest rain is the issue."
        )
        if field_habit == "deciduous":
            allowed = ["deciduous", "semi_evergreen"]

    recommended = field_habit
    if system.structure in {"tunnel", "greenhouse"} and field_habit == "deciduous":
        recommended = "semi_evergreen"

    return {
        "open_field_habit": field_habit,
        "recommended_habit": recommended,
        "allowed_habits": allowed,
        "structure": system.structure,
        "media": system.media,
        "cover": system.cover,
        "freeze_water_factor": effects.freeze_water_factor,
        "rain_crack_multiplier": effects.rain_crack_multiplier,
        "chill_relevance": effects.chill_relevance,
        "bloom_advance_days": effects.bloom_advance_days,
        "notes": notes,
        "flexible": system.structure in {"tunnel", "greenhouse"} or system.media == "substrate",
    }
