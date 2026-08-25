"""Leave-one-region-out, leave-one-cultivar-out, blocked vs random CV, skill sheet."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import numpy as np

from blueberry_analogue.analogue.engine import score_pair
from blueberry_analogue.cards import load_cards
from blueberry_analogue.paths import DOCS_ANALOGUE
from blueberry_analogue.validation.baselines import (
    baseline0_ccafs_tp,
    baseline1_ecocrop,
    baseline2_nz_landcare,
)

GXE_CELLS = (
    "known_cultivar_known_region",
    "new_cultivar_known_region",
    "known_cultivar_new_region",
    "both_new",
)


def _same_class(a, b) -> bool:
    return a.cultivar_class == b.cultivar_class


def _success(site) -> bool:
    return site.outcome == "commercial_success"


def reconstruction_recall(
    features: dict[str, dict[str, Any]],
    climate: dict[str, dict[str, Any]],
    sites_by_id: dict[str, Any],
    holdout_region: str,
    top_k: int = 8,
) -> dict[str, Any]:
    """Margins-shaped test: feed one success in a held-out region, recover the others."""
    hold = [
        s
        for s in sites_by_id.values()
        if s.region == holdout_region and _success(s) and s.site_id in features
    ]
    train_refs = [
        s
        for s in sites_by_id.values()
        if s.region != holdout_region and _success(s) and s.site_id in features
    ]
    if len(hold) < 2 or not train_refs:
        return {"region": holdout_region, "skipped": True}

    cards = load_cards()
    recovered = 0
    extras = 0
    misses = 0
    used = 0
    hold = sorted(hold, key=lambda s: s.site_id)[:8]
    for ref in hold:
        if ref.site_id not in features:
            continue
        used += 1
        cultivar = cards.cultivar(ref.cultivar)
        klass = cards.classes[ref.cultivar_class]
        ranked = []
        for sid, feat in features.items():
            if sid == ref.site_id:
                continue
            site = sites_by_id[sid]
            scored = score_pair(features[ref.site_id], feat, climate.get(sid, {}), cultivar, klass, ref.system)
            ranked.append((sid, scored["similarity"], site))
        ranked.sort(key=lambda x: -x[1])
        top = ranked[:top_k]
        hold_ids = {s.site_id for s in hold if s.site_id != ref.site_id}
        hit = sum(1 for sid, _, _ in top if sid in hold_ids)
        extra = sum(1 for sid, _, site in top if sid not in hold_ids and not _success(site))
        if hit > 0:
            recovered += 1
        else:
            misses += 1
        extras += extra
    return {
        "region": holdout_region,
        "skipped": False,
        "n_refs": used,
        "recall_at_k": recovered / used if used else 0.0,
        "misses": misses,
        "extra_non_success_in_top": extras,
        "k": top_k,
        "claim": "known_cultivar_new_region",
    }


def leave_one_region_out(features, climate, sites_by_id) -> list[dict[str, Any]]:
    regions = sorted({s.region for s in sites_by_id.values() if _success(s)})
    return [reconstruction_recall(features, climate, sites_by_id, region) for region in regions]


def leave_one_cultivar_out(features, climate, sites_by_id) -> dict[str, Any]:
    """Duke is not Ochlockonee. Score known-class vs held-out cultivar."""
    cards = load_cards()
    by_cultivar = defaultdict(list)
    for site in sites_by_id.values():
        if _success(site) and site.site_id in features:
            by_cultivar[site.cultivar].append(site)
    rows = []
    for cultivar_id, members in by_cultivar.items():
        others = [s for s in sites_by_id.values() if s.cultivar != cultivar_id and s.site_id in features]
        if not members or not others:
            continue
        klass = cards.classes[members[0].cultivar_class]
        cultivar = cards.cultivar(cultivar_id)
        same_class_ranks = []
        other_class_ranks = []
        for ref in members:
            scored = []
            for site in others:
                sim = score_pair(
                    features[ref.site_id],
                    features[site.site_id],
                    climate.get(site.site_id, {}),
                    cultivar,
                    klass,
                    ref.system,
                )["similarity"]
                scored.append((site, sim))
            scored.sort(key=lambda x: -x[1])
            top = scored[:8]
            same_class_ranks.append(sum(1 for s, _ in top if s.cultivar_class == ref.cultivar_class) / 8)
            other_class_ranks.append(sum(1 for s, _ in top if s.cultivar_class != ref.cultivar_class) / 8)
        rows.append(
            {
                "cultivar": cultivar_id,
                "class_id": members[0].cultivar_class,
                "same_class_share_top8": float(np.mean(same_class_ranks)),
                "other_class_share_top8": float(np.mean(other_class_ranks)),
            }
        )
    return {"rows": rows, "claim": "new_cultivar_known_or_new_region"}


def blocked_vs_random(features, climate, sites_by_id, block_deg: float = 5.0) -> dict[str, Any]:
    """Same model, random pairs vs 5-degree spatial blocks. Believe the blocked number."""
    cards = load_cards()
    successes = [s for s in sites_by_id.values() if _success(s) and s.site_id in features]
    if len(successes) < 8:
        return {"skipped": True}

    def pair_skill(pairs: list[tuple[Any, Any]]) -> float:
        scores = []
        for a, b in pairs:
            cultivar = cards.cultivar(a.cultivar)
            klass = cards.classes[a.cultivar_class]
            sim = score_pair(
                features[a.site_id],
                features[b.site_id],
                climate.get(b.site_id, {}),
                cultivar,
                klass,
                a.system,
            )["similarity"]
            scores.append(sim if _same_class(a, b) else 1.0 - sim)
        return float(np.mean(scores)) if scores else 0.0

    rng = np.random.default_rng(7)
    random_pairs = []
    for _ in range(min(80, len(successes) * 3)):
        i, j = rng.choice(len(successes), size=2, replace=False)
        random_pairs.append((successes[int(i)], successes[int(j)]))

    def block_id(site) -> tuple[int, int]:
        return (int(np.floor(site.lat / block_deg)), int(np.floor(site.lon / block_deg)))

    blocked_pairs = []
    for i, a in enumerate(successes):
        for b in successes[i + 1 :]:
            if block_id(a) != block_id(b):
                blocked_pairs.append((a, b))
    if len(blocked_pairs) > 80:
        idx = rng.choice(len(blocked_pairs), size=80, replace=False)
        blocked_pairs = [blocked_pairs[int(k)] for k in idx]

    return {
        "skipped": False,
        "random_pair_skill": pair_skill(random_pairs),
        "blocked_pair_skill": pair_skill(blocked_pairs),
        "block_deg": block_deg,
        "note": "Large spatial blocks also hold out climate (Roberts Box 4). Believe blocked.",
    }


def baseline_comparison(features, sites_by_id) -> dict[str, Any]:
    """Does phenology separate same-class successes from EcoCrop/T-P lookalikes that fail?"""
    successes = [s for s in sites_by_id.values() if _success(s) and s.site_id in features]
    failures = [s for s in sites_by_id.values() if s.outcome == "known_failure" and s.site_id in features]
    if not successes or not failures:
        return {"skipped": True}
    rows = []
    for fail in failures:
        # nearest T/P success vs phenology score
        tp = []
        for suc in successes:
            tp.append((suc, baseline0_ccafs_tp(features[suc.site_id], features[fail.site_id])))
        tp.sort(key=lambda x: -x[1])
        nearest = tp[0][0]
        eco = baseline1_ecocrop(features[fail.site_id], irrigated=True)
        nz = baseline2_nz_landcare(features[fail.site_id])
        cards = load_cards()
        cultivar = cards.cultivar(nearest.cultivar)
        klass = cards.classes[nearest.cultivar_class]
        pheno = score_pair(
            features[nearest.site_id],
            features[fail.site_id],
            {},
            cultivar,
            klass,
            nearest.system,
        )
        rows.append(
            {
                "failure_id": fail.site_id,
                "failure_name": fail.name,
                "nearest_tp_success": nearest.site_id,
                "baseline0_similarity": tp[0][1],
                "ecocrop_irrigated": eco,
                "nz_landcare": nz,
                "pheno_similarity": pheno["similarity"],
                "pheno_hard_fails": pheno["hard_fail_count"],
                "pheno_kills": pheno["hard_fail_count"] >= 1 or pheno["similarity"] < 0.45,
            }
        )
    kill_rate = float(np.mean([r["pheno_kills"] for r in rows])) if rows else 0.0
    eco_false = float(np.mean([r["ecocrop_irrigated"] > 0.5 for r in rows])) if rows else 0.0
    return {
        "skipped": False,
        "n_failures": len(rows),
        "pheno_kill_rate_on_known_failures": kill_rate,
        "ecocrop_false_positive_rate": eco_false,
        "rows": rows,
        "win_rule": "Phenology wins if it kills known failures that T/P or EcoCrop still like.",
    }


def gxe_label(ref_site, cand_site) -> str:
    same_c = ref_site.cultivar == cand_site.cultivar
    same_r = ref_site.region == cand_site.region
    if same_c and same_r:
        return GXE_CELLS[0]
    if (not same_c) and same_r:
        return GXE_CELLS[1]
    if same_c and (not same_r):
        return GXE_CELLS[2]
    return GXE_CELLS[3]


def write_skill_sheet(
    report: dict[str, Any],
    path: Path | None = None,
) -> Path:
    path = path or (DOCS_ANALOGUE / "skill-sheet.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    loro = report.get("loro") or []
    loro_ok = [r for r in loro if not r.get("skipped")]
    mean_recall = float(np.mean([r["recall_at_k"] for r in loro_ok])) if loro_ok else 0.0
    loco = report.get("loco") or {}
    blocked = report.get("blocked") or {}
    base = report.get("baselines") or {}
    lines = [
        "# Blueberry Analogue skill sheet",
        "",
        "## Claim",
        "",
        "The claim under test is **cycle can complete and stage risk is close**, not yield or packout, and not \"this site will grow like Michigan.\"",
        "",
        "Presence of blueberries only tests the first claim, and weakly.",
        "",
        "## What we may say",
        "",
        f"- Leave-one-region-out recall@8 of same-region commercial successes: **{mean_recall:.2f}** across {len(loro_ok)} regions.",
        "- If that number beats Baseline-0 (monthly T/P only) on known failures, we may say **more transferable than climate distance**.",
        "- If we only have presence inside the training continent, we may say **describes where blueberries are grown in this dataset**.",
        "- We may not say this site will grow like the reference.",
        "- We may not quote Wang & Dong 0.94. That paper is 17 staple crops with no blueberry and no suitability ground truth.",
        "",
        "## Baselines",
        "",
        "- Baseline-0: CCAFS Analogues-style weighted Euclidean on monthly T/P, seasonal lag.",
        "- Baseline-1: EcoCrop trapezoid for Vaccinium, irrigated and rainfed. Irrigated EcoCrop likes Peru. That is a known lie if the clock is NHB.",
        "- Baseline-2: NZ Landcare-style geometric mean (one chill curve, frost, drainage, slope).",
        "",
    ]
    if not base.get("skipped"):
        lines += [
            f"- Known failures scored: {base.get('n_failures')}",
            f"- Phenology kill rate on known failures: **{base.get('pheno_kill_rate_on_known_failures', 0):.2f}**",
            f"- EcoCrop irrigated false-positive rate on those failures: **{base.get('ecocrop_false_positive_rate', 0):.2f}**",
            "",
            "| Failure | Nearest T/P success | B0 T/P | EcoCrop | NZ | Pheno sim | Hard fails | Kills |",
            "|---|---|---:|---:|---:|---:|---:|---|",
        ]
        for row in (base.get("rows") or [])[:20]:
            lines.append(
                f"| {row['failure_name']} | {row['nearest_tp_success']} | {row['baseline0_similarity']:.2f} | "
                f"{row['ecocrop_irrigated']:.2f} | {row['nz_landcare']:.2f} | {row['pheno_similarity']:.2f} | "
                f"{row['pheno_hard_fails']} | {'yes' if row['pheno_kills'] else 'no'} |"
            )
        lines.append("")
    lines += [
        "## Leave-one-region-out",
        "",
        "Shape of the Margins 70% blueberry reconstruction, but leave-one-region-out, with precision on extras.",
        "",
        "| Region | n refs | recall@8 | misses | extra non-success in top |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in loro_ok:
        lines.append(
            f"| {row['region']} | {row['n_refs']} | {row['recall_at_k']:.2f} | {row['misses']} | {row['extra_non_success_in_top']} |"
        )
    lines += [
        "",
        "## Leave-one-cultivar-out",
        "",
        "Duke is not Ochlockonee. Report the share of top-8 analogues that stay in class.",
        "",
        "| Cultivar | Class | Same-class share@8 | Other-class share@8 |",
        "|---|---|---:|---:|",
    ]
    for row in (loco.get("rows") or [])[:20]:
        lines.append(
            f"| {row['cultivar']} | {row['class_id']} | {row['same_class_share_top8']:.2f} | {row['other_class_share_top8']:.2f} |"
        )
    if not blocked.get("skipped"):
        lines += [
            "",
            "## Blocked vs random pairs",
            "",
            f"- Random pair skill: **{blocked.get('random_pair_skill', 0):.2f}**",
            f"- {blocked.get('block_deg')}° blocked pair skill: **{blocked.get('blocked_pair_skill', 0):.2f}**",
            f"- {blocked.get('note')}",
            "",
        ]
    lines += [
        "## No-analogue mask",
        "",
        "Williams & Jackson 2007. Novel climates are not ranked. The cutoff is published and subjective (CCAFS authors already say so).",
        "",
        "## Human panel (qualitative)",
        "",
        "If the model loves a site growers already abandoned, that is a bug. Seed panel:",
        "",
        "- Willamette Emerald / Biloxi / Snowchaser (OSU: do not plant).",
        "- Star south of Ocala.",
        "- Inland Michigan Legacy fruit buds.",
        "- IGP Delhi / Lucknow / Patna winter fog.",
        "- Olmos deciduous Duke.",
        "- Ica Ventura 2023/24 heat.",
        "- Santiago basin Legacy vs Osorno.",
        "- Miami Star.",
        "",
        "## Hindcast questions we still owe",
        "",
        "- Would we have flagged Peru 2005, Morocco 2010, Mexico 2015 before the industry did?",
        "- Report misses in public when those reconstructions are run on dated climate.",
        "",
        "## Data trust",
        "",
        "This sheet is only as good as the climate at the points. NASA POWER monthly climatology is the current operational source. CHELSA 1 km and hourly ERA5-Land on the shortlist still need to be staged. If a 10-year station disagrees on chill or harvest rain, the pixel is untrusted.",
        "",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path = path.with_suffix(".json")
    json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return path


def run_validation(features, climate, sites_by_id) -> dict[str, Any]:
    report = {
        "loro": leave_one_region_out(features, climate, sites_by_id),
        "loco": leave_one_cultivar_out(features, climate, sites_by_id),
        "blocked": blocked_vs_random(features, climate, sites_by_id),
        "baselines": baseline_comparison(features, sites_by_id),
    }
    write_skill_sheet(report)
    return report
