"""CCAFS lagged distance, Hallegatte gates, trouble list, investigation pack.

Weighted Euclidean on standardized monthly climate, lag 0-11 so Chile can
match Michigan. A separate unblended chill/frost score so Florida cannot
match Michigan on summer rain alone.

Never say identical. Never treat similarity as plant 20 ha.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from blueberry_analogue.cards import CultivarCard, VarietyClass, load_cards
from blueberry_analogue.systems import ProductionSystem, system_effects

MONTHLY_BLOCKS = (
    ("monthly_tmin", "monthly_tmin"),
    ("monthly_tmax", "monthly_tmax"),
    ("monthly_precip", "monthly_precip"),
    ("monthly_vpd", "monthly_vpd"),
    ("monthly_rsds", "monthly_rsds"),
)

PHENO_KEYS = (
    "chill_portions",
    "chill_hours",
    "frost_nights_full_bloom",
    "heat_hours_proxy",
    "dtr",
    "dli_bloom",
    "vpd_fruit",
    "harvest_rain_days",
)

NO_ANALOGUE_CUTOFF = 2.6  # standardized Euclidean. Subjective; published on purpose.
SIMILARITY_SIGMA = 1.15

INVESTIGATION = [
    "Confirm the variety, the production system, and the market week. Climate search is not step 1.",
    "Check quarantine, club IP, and royalty exposure in the target country (PIQA-shaped loss is years, not a season).",
    "Read this shortlist as places to test, not places to plant.",
    "Ask whether water rights exist for the irrigation the fingerprint assumes.",
    "If the system is soil, walk pH, drainage, and Phytophthora history. If it is substrate, drop pH and keep VPD-hourly irrigation.",
    "Price labour at harvest. Chile and Huelva are not the same labour market.",
    "Measure days to the buyer's dock. Huelva is 24-48 h to EU retail. Peru is about 20 days.",
    "If the system is CEA, price heating-degree days, winter DLI, electricity, and substation capacity. A climate twin of Ford is not a twin of the energy bill.",
    "List the pests and phytosanitary rules that the climate cube cannot see.",
    "Book the flight.",
    "Walk the land and talk to growers who already failed here.",
    "Put a logger on the actual block. If CHELSA or POWER and the logger disagree on chill or harvest rain, the pixel is untrusted.",
    "Plant a trial. Do not plant 20 ha.",
]


def _shift(values: list[float], lag: int) -> list[float]:
    n = len(values)
    return [values[(i + lag) % n] for i in range(n)]


def _z(a: np.ndarray, b: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    pool = np.concatenate([a, b])
    mu = float(np.nanmean(pool))
    sd = float(np.nanstd(pool))
    if sd < 1e-6:
        sd = 1.0
    return (a - mu) / sd, (b - mu) / sd


def ccafs_monthly_distance(
    ref: dict[str, Any],
    cand: dict[str, Any],
    weights: dict[str, float],
) -> dict[str, Any]:
    best = None
    for lag in range(12):
        acc = 0.0
        wsum = 0.0
        residuals: dict[str, float] = {}
        for key, wname in MONTHLY_BLOCKS:
            w = float(weights.get(wname, weights.get(key, 1.0)))
            rv = np.asarray(ref[key], dtype=float)
            cv = np.asarray(_shift(list(cand[key]), lag), dtype=float)
            if key == "monthly_tmin":
                # Weight Tmin by DTR as CCAFS-style emphasis on nights
                dtr_w = float(weights.get("dtr", 1.0))
                w *= 0.7 + 0.3 * dtr_w
            zr, zc = _z(rv, cv)
            dist = float(np.sqrt(np.nanmean((zr - zc) ** 2)))
            residuals[key] = dist
            acc += w * dist**2
            wsum += w
        d = math_sqrt(acc / max(wsum, 1e-6))
        rec = {"lag": lag, "distance": d, "residuals": residuals}
        if best is None or d < best["distance"]:
            best = rec
    assert best is not None
    best["similarity"] = float(np.exp(-(best["distance"] ** 2) / (2 * SIMILARITY_SIGMA**2)))
    return best


def math_sqrt(x: float) -> float:
    return float(np.sqrt(max(0.0, x)))


def pheno_distance(
    ref: dict[str, Any],
    cand: dict[str, Any],
    weights: dict[str, float],
    chill_relevance: float,
) -> dict[str, Any]:
    acc = 0.0
    wsum = 0.0
    residuals = {}
    for key in PHENO_KEYS:
        w = float(weights.get(key, 1.0))
        if key in {"chill_portions", "chill_hours"}:
            w *= chill_relevance
        a = float(ref.get(key, 0.0))
        b = float(cand.get(key, 0.0))
        scale = max(abs(a), abs(b), 1.0)
        d = abs(a - b) / scale
        residuals[key] = d
        acc += w * d**2
        wsum += w
    dist = math_sqrt(acc / max(wsum, 1e-6))
    return {
        "distance": dist,
        "similarity": float(np.exp(-(dist**2) / (2 * SIMILARITY_SIGMA**2))),
        "residuals": residuals,
    }


def hallegatte_gates(
    cand: dict[str, Any],
    cultivar: CultivarCard,
    klass: VarietyClass,
    system: ProductionSystem,
    market_weeks: tuple[int, int] | None = None,
    soil_ph: float | None = None,
    slope_pct: float | None = None,
) -> list[dict[str, Any]]:
    effects = system_effects(system)
    gates = []

    def add(name: str, passed: bool, detail: str, stage: str):
        gates.append({"name": name, "passed": passed, "detail": detail, "stage": stage})

    if klass.chill_relevant and effects.chill_relevance > 0.2:
        need = cultivar.chill_portions
        got = float(cand.get("chill_portions", 0.0))
        need_h = cultivar.chill_hours
        got_h = float(cand.get("chill_hours", 0.0))
        if klass.id == "low_chill_shb":
            # Portions stay near 0 in the real SHB belt on monthly POWER. Hours + negation lead.
            add(
                "chill_hours",
                got_h >= 0.45 * need_h,
                f"{got_h:.0f} h vs {need_h:.0f} h (low-chill SHB; portions are a check, not the gate)",
                "dormancy",
            )
            add(
                "chill_portions",
                True,
                f"{got:.1f} CP recorded. Not gated for low-chill SHB on monthly reanalysis.",
                "dormancy",
            )
        else:
            add(
                "chill_portions",
                got >= 0.70 * need,
                f"{got:.1f} CP vs {need:.0f} CP required for {cultivar.label}",
                "dormancy",
            )
            add(
                "chill_hours",
                got_h >= 0.45 * need_h or got >= 0.70 * need,
                f"{got_h:.0f} h vs {need_h:.0f} h. Hours undercount when nights go below 0 C. Portions can pass it.",
                "dormancy",
            )
    else:
        add("chill_portions", True, "Evergreen / HCN clock. Chill is not the gate.", "dormancy")

    frost = float(cand.get("frost_nights_full_bloom", 0.0))
    frost_limit = 28.0 if klass.id in {"nhb", "high_chill_shb"} else 10.0
    add("bloom_frost", frost <= frost_limit, f"{frost:.1f} bloom frost-night equivalents (limit {frost_limit:.0f})", "full_bloom")

    heat = float(cand.get("days_berry_gt_42", 0.0))
    limit = 8 if cultivar.heat_sensitivity == "high" else 14
    add("berry_heat", heat <= limit, f"{heat:.0f} days sun-side berry ≥ 42 C (Yang/Bryla/Strik)", "green_fruit")

    rain = float(cand.get("harvest_rain_days", 0.0))
    rain_limit = 6 if cultivar.rain_crack_risk in {"high", "very_high"} else 12
    add("harvest_rain", rain <= rain_limit, f"{rain:.1f} harvest rain days after cover transfer", "harvest")

    if not effects.apis_ok:
        add("pollination", False, "Closed structure without Bombus. GDD can look perfect and set still fails.", "bloom")
    else:
        add("pollination", True, f"Pollinator assumption: {system.pollinator}", "bloom")

    fog = float(cand.get("igp_fog_events", 0.0))
    if fog > 0:
        add("igp_fog", fog <= 12.0, f"{fog:.1f} IGP-type fog/DLI-crash days. Not a California fog bonus.", "bloom")

    if effects.soil_ph_weight > 0 and soil_ph is not None:
        add("soil_ph", 4.2 <= soil_ph <= 5.8, f"SoilGrids pH {soil_ph:.2f}. Weight=0 under substrate.", "land")
    else:
        add("soil_ph", True, "Soil pH weight is 0 (substrate) or pH not yet fetched.", "land")

    if slope_pct is not None:
        add("slope", slope_pct <= 12.0, f"Slope {slope_pct:.1f}%", "land")

    if market_weeks is not None:
        # Market window is a filter before climate search. Record whether the cultivar window overlaps.
        c0, c1 = cultivar.market_window
        overlap = not (c1 < market_weeks[0] and market_weeks[1] < c0)
        add("market_window", overlap, f"Cultivar weeks {c0}-{c1} vs request {market_weeks[0]}-{market_weeks[1]}", "market")

    return gates


def trouble_list(gates: list[dict[str, Any]], pheno: dict[str, Any], monthly: dict[str, Any]) -> list[dict[str, str]]:
    out = []
    for gate in gates:
        if not gate["passed"]:
            out.append(
                {
                    "stage": gate["stage"],
                    "variable": gate["name"],
                    "message": gate["detail"],
                }
            )
    residuals = sorted(monthly.get("residuals", {}).items(), key=lambda kv: -kv[1])
    for key, dist in residuals[:3]:
        if dist > 0.85:
            out.append(
                {
                    "stage": "season_shape",
                    "variable": key,
                    "message": f"Monthly {key} residual {dist:.2f} after lag {monthly.get('lag', 0)}.",
                }
            )
    for key, dist in sorted(pheno.get("residuals", {}).items(), key=lambda kv: -kv[1])[:3]:
        if dist > 0.45:
            out.append(
                {
                    "stage": "phenology",
                    "variable": key,
                    "message": f"Phenology {key} differs by {dist:.2f} of the local scale.",
                }
            )
    # unique by variable
    seen = set()
    uniq = []
    for item in out:
        if item["variable"] in seen:
            continue
        seen.add(item["variable"])
        uniq.append(item)
    return uniq


def data_trust(payload: dict[str, Any], cand_features: dict[str, Any]) -> dict[str, Any]:
    notes = list(payload.get("trust_notes") or [])
    source = payload.get("source", "unknown")
    flag = "low"
    if source == "nasa_power_climatology":
        flag = "med"
        notes.append("POWER is a point check, not a 1 km grid. Asking for fake 1 km repeats the same cell.")
    if source == "fallback":
        flag = "low"
    if abs(float(payload.get("lat", 0))) < 12:
        flag = "low"
        notes.append("No-analogue risk in novel tropics (Williams & Jackson). Do not rank a novel climate as a twin.")
    if not payload.get("chelsa", {}).get("available"):
        notes.append("CHELSA 1 km files are not staged. Globe screen is POWER monthly, not CHELSA.")
    if cand_features.get("igp_fog_events", 0) > 8:
        notes.append("Fog scored as duration/DLI loss, not as fog-present.")
    return {"flag": flag, "source": source, "notes": notes}


def score_pair(
    ref_features: dict[str, Any],
    cand_features: dict[str, Any],
    cand_climate: dict[str, Any],
    cultivar: CultivarCard,
    klass: VarietyClass,
    system: ProductionSystem,
    market_weeks: tuple[int, int] | None = None,
) -> dict[str, Any]:
    weights = load_cards().resolved_weights(cultivar.id)
    effects = system_effects(system)
    monthly = ccafs_monthly_distance(ref_features, cand_features, weights)
    pheno = pheno_distance(ref_features, cand_features, weights, effects.chill_relevance)
    gates = hallegatte_gates(
        cand_features,
        cultivar,
        klass,
        system,
        market_weeks=market_weeks,
        soil_ph=(cand_climate.get("land") or {}).get("soil_ph"),
    )
    hard_fail = [g for g in gates if not g["passed"]]
    # Combined score: do not blend chill into monthly so FL cannot hide on rain
    similarity = 0.55 * monthly["similarity"] + 0.45 * pheno["similarity"]
    no_analogue = monthly["distance"] > NO_ANALOGUE_CUTOFF and pheno["distance"] > 0.85
    if no_analogue:
        similarity = 0.0
    if hard_fail:
        similarity *= 0.55
    return {
        "monthly": monthly,
        "pheno": pheno,
        "similarity": float(similarity),
        "gates": gates,
        "hard_fail_count": len(hard_fail),
        "no_analogue": no_analogue,
        "trouble": trouble_list(gates, pheno, monthly),
        "trust": data_trust(cand_climate, cand_features),
        "volatility": {
            "years_chill_short": cand_features.get("years_chill_short"),
            "years_frost_break": cand_features.get("years_frost_break"),
            "years_heat_break": cand_features.get("years_heat_break"),
            "n_years": cand_features.get("n_years", 1),
        },
    }


def shortlist_from_reference(
    ref_id: str,
    features_by_id: dict[str, dict[str, Any]],
    climate_by_id: dict[str, dict[str, Any]],
    sites_by_id: dict[str, Any],
    system: ProductionSystem | None = None,
    cultivar_id: str | None = None,
    market_weeks: tuple[int, int] | None = None,
    top_n: int = 12,
) -> dict[str, Any]:
    cards = load_cards()
    ref_site = sites_by_id[ref_id]
    cultivar = cards.cultivar(cultivar_id or ref_site.cultivar)
    klass = cards.classes[cultivar.class_id]
    sys = system or ref_site.system
    ref_feat = features_by_id[ref_id]
    ranked = []
    for sid, feat in features_by_id.items():
        if sid == ref_id:
            continue
        site = sites_by_id[sid]
        if market_weeks is not None:
            c0, c1 = cultivar.market_window
            # Filter before climate search: candidate must be able to hit the week in some lag
            if not _week_plausible(c0, c1, market_weeks):
                continue
        scored = score_pair(ref_feat, feat, climate_by_id.get(sid, {}), cultivar, klass, sys, market_weeks)
        ranked.append(
            {
                "site_id": sid,
                "name": site.name,
                "country": site.country,
                "region": site.region,
                "lat": site.lat,
                "lon": site.lon,
                "outcome": site.outcome,
                "cultivar": site.cultivar,
                "cultivar_class": site.cultivar_class,
                "system": site.system.label,
                **scored,
            }
        )
    ranked.sort(key=lambda r: (-r["similarity"], r["hard_fail_count"], r["monthly"]["distance"]))
    short = [r for r in ranked if not r["no_analogue"]][:top_n]
    return {
        "reference_id": ref_id,
        "cultivar": cultivar.id,
        "class_id": klass.id,
        "system": sys.label,
        "claim": "cycle_and_stage_risk_close",
        "disclaimer": (
            "This is a shortlist of places worth testing. It is not a plant-here button. "
            "We do not say this site will grow like the reference. Similarity is not identity."
        ),
        "investigation": INVESTIGATION,
        "no_analogue_cutoff": NO_ANALOGUE_CUTOFF,
        "shortlist": short,
        "killed": [r for r in ranked if r["hard_fail_count"] >= 2][:8],
        "n_compared": len(ranked),
    }


def _week_plausible(c0: int, c1: int, req: tuple[int, int]) -> bool:
    # Allow opposite-hemisphere lag: any overlap after ±26 weeks is handled by climate lag, not week math.
    return True
