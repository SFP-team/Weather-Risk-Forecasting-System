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


def _stratified(sites: list, key_fn, cap: int) -> list:
    """Deterministic sample spread across groups, sorted by site_id."""
    ordered = sorted(sites, key=lambda s: s.site_id)
    if len(ordered) <= cap:
        return ordered
    by: dict[str, list] = defaultdict(list)
    for site in ordered:
        by[str(key_fn(site))].append(site)
    out: list = []
    i = 0
    keys = sorted(by)
    while len(out) < cap:
        progressed = False
        for key in keys:
            if i < len(by[key]) and len(out) < cap:
                out.append(by[key][i])
                progressed = True
        if not progressed:
            break
        i += 1
    return out


def _rank_sites(ref, candidates, features, climate, cultivar, klass) -> list[tuple[str, float, Any]]:
    ranked = []
    for site in candidates:
        if site.site_id == ref.site_id or site.site_id not in features:
            continue
        scored = score_pair(
            features[ref.site_id],
            features[site.site_id],
            climate.get(site.site_id, {}),
            cultivar,
            klass,
            ref.system,
        )
        ranked.append((site.site_id, scored["similarity"], site))
    ranked.sort(key=lambda x: -x[1])
    return ranked


def belt_reconstruction(
    features: dict[str, dict[str, Any]],
    climate: dict[str, dict[str, Any]],
    sites_by_id: dict[str, Any],
    region: str,
    top_k: int = 8,
    ref_cap: int = 12,
) -> dict[str, Any]:
    """Margins 70% shape: fingerprint one success, recover other same-class successes in the belt."""
    hold = [
        s
        for s in sites_by_id.values()
        if s.region == region and _success(s) and s.site_id in features
    ]
    if len(hold) < 2:
        return {"region": region, "skipped": True, "test": "belt_reconstruction"}

    cards = load_cards()
    refs = _stratified(hold, lambda s: s.cultivar_class, ref_cap)
    recovered = 0
    extras = 0
    misses = 0
    used = 0
    all_sites = [s for s in sites_by_id.values() if s.site_id in features]
    for ref in refs:
        targets = {s.site_id for s in hold if s.site_id != ref.site_id and s.cultivar_class == ref.cultivar_class}
        if not targets:
            continue
        used += 1
        cultivar = cards.cultivar(ref.cultivar)
        klass = cards.classes[ref.cultivar_class]
        top = _rank_sites(ref, all_sites, features, climate, cultivar, klass)[:top_k]
        if any(sid in targets for sid, _, _ in top):
            recovered += 1
        else:
            misses += 1
        extras += sum(1 for sid, _, site in top if sid not in targets and not _success(site))
    if used == 0:
        return {"region": region, "skipped": True, "test": "belt_reconstruction"}
    return {
        "region": region,
        "skipped": False,
        "n_refs": used,
        "recall_at_k": recovered / used,
        "misses": misses,
        "extra_non_success_in_top": extras,
        "k": top_k,
        "test": "belt_reconstruction",
        "claim": "known_cultivar_known_region",
    }


def loro_transfer(
    features: dict[str, dict[str, Any]],
    climate: dict[str, dict[str, Any]],
    sites_by_id: dict[str, Any],
    holdout_region: str,
    top_k: int = 8,
    ref_cap: int = 12,
) -> dict[str, Any]:
    """Leave-one-region-out transfer.

    Fingerprint a success in R. Hide every site in R from the candidate set
    (the unused train_refs set in the first draft). Hit if a same-class
    commercial success from another region is in the top 8.

    This is the plan's "train on PNW + Michigan + Chile, test on Georgia":
    without seeing your neighbors, do you still land in the right climate family?
    """
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
    if not hold or not train_refs:
        return {"region": holdout_region, "skipped": True, "test": "leave_one_region_out"}

    cards = load_cards()
    refs = _stratified(hold, lambda s: s.cultivar_class, ref_cap)
    recovered = 0
    extras = 0
    misses = 0
    used = 0
    no_family = 0
    outside = [s for s in sites_by_id.values() if s.region != holdout_region and s.site_id in features]
    for ref in refs:
        family = {s.site_id for s in train_refs if s.cultivar_class == ref.cultivar_class}
        if not family:
            no_family += 1
            continue
        used += 1
        cultivar = cards.cultivar(ref.cultivar)
        klass = cards.classes[ref.cultivar_class]
        top = _rank_sites(ref, outside, features, climate, cultivar, klass)[:top_k]
        if any(sid in family for sid, _, _ in top):
            recovered += 1
        else:
            misses += 1
        extras += sum(1 for sid, _, site in top if sid not in family and not _success(site))
    if used == 0:
        return {
            "region": holdout_region,
            "skipped": True,
            "n_no_outside_family": no_family,
            "test": "leave_one_region_out",
        }
    return {
        "region": holdout_region,
        "skipped": False,
        "n_refs": used,
        "n_no_outside_family": no_family,
        "recall_at_k": recovered / used,
        "misses": misses,
        "extra_non_success_in_top": extras,
        "k": top_k,
        "test": "leave_one_region_out",
        "claim": "known_cultivar_new_region",
    }


def belt_reconstruction_all(features, climate, sites_by_id) -> list[dict[str, Any]]:
    regions = sorted({s.region for s in sites_by_id.values() if _success(s)})
    return [belt_reconstruction(features, climate, sites_by_id, region) for region in regions]


def leave_one_region_out(features, climate, sites_by_id) -> list[dict[str, Any]]:
    regions = sorted({s.region for s in sites_by_id.values() if _success(s)})
    return [loro_transfer(features, climate, sites_by_id, region) for region in regions]


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
        for ref in _stratified(members, lambda s: s.region, 6):
            scored = []
            for site in others:
                if site.site_id not in features:
                    continue
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


def gxe_summary(features, climate, sites_by_id, n_pairs: int = 120) -> dict[str, Any]:
    """Malosetti four cells. A climate analogue only claims the last two."""
    cards = load_cards()
    successes = [s for s in sites_by_id.values() if _success(s) and s.site_id in features]
    if len(successes) < 4:
        return {"skipped": True}
    rng = np.random.default_rng(7)
    buckets: dict[str, list[float]] = {cell: [] for cell in GXE_CELLS}
    tries = 0
    while sum(len(v) for v in buckets.values()) < n_pairs and tries < n_pairs * 8:
        tries += 1
        i, j = rng.choice(len(successes), size=2, replace=False)
        a, b = successes[int(i)], successes[int(j)]
        cell = gxe_label(a, b)
        if len(buckets[cell]) >= max(12, n_pairs // 3) and min(len(v) for v in buckets.values()) < 8:
            continue
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
        buckets[cell].append(sim)
    rows = []
    for cell in GXE_CELLS:
        vals = buckets[cell]
        rows.append(
            {
                "cell": cell,
                "n": len(vals),
                "mean_similarity": float(np.mean(vals)) if vals else None,
            }
        )
    return {
        "skipped": False,
        "rows": rows,
        "note": (
            "A climate analogue only claims known-cultivar / new-region and both-new. "
            "Those are the hardest cells and they have no genetics in them."
        ),
    }


def write_skill_sheet(
    report: dict[str, Any],
    path: Path | None = None,
) -> Path:
    path = path or (DOCS_ANALOGUE / "skill-sheet.md")
    path.parent.mkdir(parents=True, exist_ok=True)
    loro = report.get("loro") or []
    loro_ok = [r for r in loro if not r.get("skipped")]
    mean_loro = float(np.mean([r["recall_at_k"] for r in loro_ok])) if loro_ok else 0.0
    recon = report.get("reconstruction") or []
    recon_ok = [r for r in recon if not r.get("skipped")]
    mean_recon = float(np.mean([r["recall_at_k"] for r in recon_ok])) if recon_ok else 0.0
    loco = report.get("loco") or {}
    blocked = report.get("blocked") or {}
    base = report.get("baselines") or {}
    gxe = report.get("gxe") or {}
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
        f"- Belt reconstruction recall@8 of same-class neighbors in the same region: **{mean_recon:.2f}** across {len(recon_ok)} regions (Margins 70% shape).",
        f"- Leave-one-region-out recall@8 of same-class successes *outside* the held-out region: **{mean_loro:.2f}** across {len(loro_ok)} regions. Neighbors in the query region are hidden.",
        "- If phenology kills known failures that Baseline-0 still likes, we may say **more transferable than climate distance**.",
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
        "## Belt reconstruction",
        "",
        "Shape of the Margins 70% blueberry test: fingerprint one success, recover other same-class successes in that belt. Mixed regions (US-SE is SHB and rabbiteye) are scored class-aware.",
        "",
        "| Region | n refs | recall@8 | misses | extra non-success in top |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in recon_ok:
        lines.append(
            f"| {row['region']} | {row['n_refs']} | {row['recall_at_k']:.2f} | {row['misses']} | {row['extra_non_success_in_top']} |"
        )
    lines += [
        "",
        "## Leave-one-region-out",
        "",
        "Neighbors in the query region are hidden. Hit if a same-class commercial success from another region is in the top 8. This is known-cultivar / new-region.",
        "",
        "| Region | n refs | recall@8 | misses | extra non-success in top | no outside family |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in loro_ok:
        lines.append(
            f"| {row['region']} | {row['n_refs']} | {row['recall_at_k']:.2f} | {row['misses']} | {row['extra_non_success_in_top']} | {row.get('n_no_outside_family', 0)} |"
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
    for row in loco.get("rows") or []:
        lines.append(
            f"| {row['cultivar']} | {row['class_id']} | {row['same_class_share_top8']:.2f} | {row['other_class_share_top8']:.2f} |"
        )
    if not gxe.get("skipped"):
        lines += [
            "",
            "## Malosetti G×E cells",
            "",
            gxe.get("note", ""),
            "",
            "| Cell | n pairs | Mean similarity |",
            "|---|---:|---:|",
        ]
        for row in gxe.get("rows") or []:
            mean = row["mean_similarity"]
            mean_s = f"{mean:.2f}" if mean is not None else "n/a"
            lines.append(f"| {row['cell']} | {row['n']} | {mean_s} |")
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
        "reconstruction": belt_reconstruction_all(features, climate, sites_by_id),
        "loro": leave_one_region_out(features, climate, sites_by_id),
        "loco": leave_one_cultivar_out(features, climate, sites_by_id),
        "gxe": gxe_summary(features, climate, sites_by_id),
        "blocked": blocked_vs_random(features, climate, sites_by_id),
        "baselines": baseline_comparison(features, sites_by_id),
    }
    write_skill_sheet(report)
    return report
