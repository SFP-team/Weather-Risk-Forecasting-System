"""Rule-based genotype ranking from variety cards.

This is not the genomic × weather model. That waits for Patricia's
recommendable list, Diego's pedigree/genomics, and a precomputed
selection index on sampled environments. Until then we match chill
envelopes and risk flags so the product can already say "low-chill
SHB, watch harvest rain."
"""

from __future__ import annotations

from typing import Any

import yaml

from blueberry_analogue.cards import CultivarCard, VarietyClass, load_cards
from blueberry_analogue.paths import SELECTIONS_YAML

CRACK_SCORE = {"low": 1.0, "moderate": 0.75, "high": 0.4, "very_high": 0.2}
HEAT_SCORE = {"low": 1.0, "moderate": 0.8, "high": 0.45, "very_high": 0.2}


def load_advanced_selections() -> dict[str, Any]:
    if not SELECTIONS_YAML.exists():
        return {"meta": {"status": "missing"}, "selections": []}
    with open(SELECTIONS_YAML, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {"meta": {}, "selections": []}


def _chill_fit(site_chill: float, lo: float, hi: float, evergreen: bool) -> tuple[float, str, str]:
    """Return (score 0-1, status, why). 51 vs 90 lives here."""
    if evergreen:
        if site_chill < 200:
            return 0.92, "comfortable", "Zero/low-chill genetics. Site chill is low enough."
        if site_chill < 400:
            return 0.55, "borderline", "Site has more winter than a typical evergreen clock."
        return 0.2, "concerning", "Too much winter for evergreen-zero-chill."

    if hi <= 0:
        hi = lo + 50
    # Cards mix UF 32–45 °F and 0–7.2 °C hours. 0–7.2 counts more hours than UF.
    hi = hi * 1.35
    target = 0.5 * (lo + hi)
    if site_chill < 0.45 * lo:
        return 0.05, "extreme", f"Chill {site_chill:.0f} h is well below the {lo:.0f}–{hi:.0f} h need."
    if site_chill < 0.70 * lo:
        return 0.28, "concerning", f"Chill {site_chill:.0f} h is short of {lo:.0f}–{hi:.0f} h. Borderline fail."
    if site_chill < lo:
        return 0.48, "borderline", (
            f"Inside a wide window but only {site_chill:.0f} h vs {lo:.0f}–{hi:.0f} h. "
            "A 51 next to a 90. Treat as critical, not fine."
        )
    if lo <= site_chill <= hi:
        closeness = 1.0 - abs(site_chill - target) / max(1.0, hi - lo)
        return 0.7 + 0.25 * closeness, "comfortable", f"Chill {site_chill:.0f} h sits in {lo:.0f}–{hi:.0f} h."
    if site_chill <= hi * 1.25:
        return 0.62, "borderline", f"More chill than this cultivar wants ({site_chill:.0f} vs {hi:.0f} h)."
    return 0.3, "concerning", f"Much more chill than {lo:.0f}–{hi:.0f} h. Wrong class."


def _habit_ok(class_id: str, default_habit: str, allowed: list[str]) -> bool:
    if class_id == "evergreen_zero_chill":
        return "evergreen" in allowed or "semi_evergreen" in allowed
    if default_habit in allowed:
        return True
    # high-chill types can still run deciduous under tunnels
    return "deciduous" in allowed and class_id in {"nhb", "high_chill_shb", "rabbiteye", "low_chill_shb"}


def rank_genotypes(
    stats: dict[str, Any],
    risks: list[dict[str, Any]],
    allowed_habits: list[str],
    recommended_habit: str,
    top_n: int = 8,
) -> dict[str, Any]:
    cards = load_cards()
    site_chill = float(stats.get("chill_hours_p50") or 0.0)
    rain = next((r for r in risks if r["id"] == "harvest_rain"), None)
    heat = next((r for r in risks if r["id"] == "heat"), None)
    rain_bad = bool(rain and rain["status"] in {"borderline", "concerning", "extreme"})
    heat_bad = bool(heat and heat["status"] in {"borderline", "concerning", "extreme"})

    ranked: list[dict[str, Any]] = []
    for cultivar in cards.cultivars.values():
        klass: VarietyClass = cards.classes[cultivar.class_id]
        evergreen = cultivar.class_id == "evergreen_zero_chill"
        if not _habit_ok(cultivar.class_id, klass.default_habit, allowed_habits):
            continue
        score, chill_status, chill_why = _chill_fit(
            site_chill, klass.chill_hours_min, klass.chill_hours_max, evergreen
        )
        why = [chill_why]
        if rain_bad:
            crack = CRACK_SCORE.get(cultivar.rain_crack_risk, 0.6)
            score *= 0.55 + 0.45 * crack
            if cultivar.rain_crack_risk in {"high", "very_high"}:
                why.append("Harvest rain is a problem and this cultivar cracks easily.")
            else:
                why.append("Harvest rain is elevated; crack risk on this card is manageable.")
        if heat_bad:
            hs = HEAT_SCORE.get(cultivar.heat_sensitivity, 0.7)
            score *= 0.55 + 0.45 * hs
            if cultivar.heat_sensitivity in {"high", "very_high"}:
                why.append("Berry heat is up and this cultivar is heat-sensitive.")
        habit_bonus = 0.08 if (
            (evergreen and recommended_habit == "evergreen")
            or (not evergreen and recommended_habit == "deciduous")
            or (recommended_habit == "semi_evergreen" and cultivar.class_id in {"low_chill_shb", "high_chill_shb"})
        ) else 0.0
        # Florida deciduous belt: 150–450 h is SHB country, not rabbiteye/NHB first.
        if 150 <= site_chill <= 450 and recommended_habit in {"deciduous", "semi_evergreen"}:
            if cultivar.class_id == "low_chill_shb":
                habit_bonus += 0.14
            elif cultivar.class_id == "high_chill_shb" and site_chill >= 300:
                habit_bonus += 0.08
            elif cultivar.class_id == "rabbiteye":
                habit_bonus -= 0.10
        score = min(1.0, max(0.0, score + habit_bonus))
        ranked.append(
            {
                "id": cultivar.id,
                "label": cultivar.label,
                "class_id": cultivar.class_id,
                "kind": "cultivar",
                "score": round(float(score), 3),
                "chill_status": chill_status,
                "chill_hours_need": [klass.chill_hours_min, klass.chill_hours_max],
                "rain_crack_risk": cultivar.rain_crack_risk,
                "heat_sensitivity": cultivar.heat_sensitivity,
                "market_window": list(cultivar.market_window),
                "why": why,
            }
        )

    ranked.sort(key=lambda r: r["score"], reverse=True)
    selections = load_advanced_selections()
    return {
        "genotypes": ranked[:top_n],
        "n_considered": len(ranked),
        "method": "rule_based_variety_cards",
        "note": (
            "Interim ranking from published variety cards. Not a genomic selection index. "
            "Patricia's recommendable cultivars and Stage 4s are not loaded yet "
            f"({selections.get('meta', {}).get('status', 'missing')})."
        ),
        "advanced_selections": selections.get("selections") or [],
    }


def card_as_probe(habit: str) -> tuple[CultivarCard, VarietyClass]:
    """A cultivar used only to build a feature vector for analogue search."""
    cards = load_cards()
    pick = {
        "evergreen": "ventura",
        "semi_evergreen": "emerald",
        "deciduous": "star",
    }.get(habit, "emerald")
    if pick not in cards.cultivars:
        pick = next(iter(cards.cultivars))
    cultivar = cards.cultivars[pick]
    return cultivar, cards.classes[cultivar.class_id]
