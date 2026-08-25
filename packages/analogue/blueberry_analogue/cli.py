"""Command line for Blueberry Analogue."""

from __future__ import annotations

import argparse
import json

from blueberry_analogue.cards import list_classes, list_cultivars, load_cards
from blueberry_analogue.pipeline import build_all, build_features, build_truth_set, load_feature_cache
from blueberry_analogue.sites import load_sites


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Blueberry Analogue: shortlists, not plant-here.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("cards", help="Print cultivar class cards")
    sub.add_parser("sites", help="Write and count the truth set")
    p_build = sub.add_parser("build", help="Truth set + features + skill sheet")
    p_build.add_argument("--live", action="store_true", help="Call NASA POWER point climatology")
    p_build.add_argument("--refresh", action="store_true", help="Replace cached climatology")
    p_build.add_argument("--limit", type=int, default=None)
    p_feat = sub.add_parser("features", help="Rebuild features only")
    p_feat.add_argument("--live", action="store_true")
    p_feat.add_argument("--refresh", action="store_true")
    p_feat.add_argument("--limit", type=int, default=None)
    sub.add_parser("validate", help="Re-run skill sheet from the feature cache")
    sub.add_parser("serve", help="Run the shortlist API + MapLibre UI")
    args = parser.parse_args(argv)

    if args.cmd == "cards":
        cards = load_cards()
        print(f"version {cards.version}")
        for klass in list_classes():
            print(f"- {klass.id}: {klass.label}  hours {klass.chill_hours_min:.0f}-{klass.chill_hours_max:.0f}  CP {klass.chill_portions_min:.0f}-{klass.chill_portions_max:.0f}")
        print("cultivars:", ", ".join(c.id for c in list_cultivars()))
        return 0
    if args.cmd == "sites":
        n = build_truth_set()
        sites = load_sites()
        print(f"{n} sites  commercial={sum(s.outcome=='commercial_success' for s in sites)}  failures={sum(s.outcome=='known_failure' for s in sites)}")
        return 0
    if args.cmd == "features":
        feats = build_features(live=args.live, limit=args.limit, refresh=args.refresh)
        print(f"features for {len(feats)} sites")
        return 0
    if args.cmd == "build":
        out = build_all(live=args.live, limit=args.limit, refresh=args.refresh)
        print(json.dumps({"n_sites": out["n_sites"], "n_features": out["n_features"]}, indent=2))
        return 0
    if args.cmd == "validate":
        from blueberry_analogue.pipeline import climate_for_features
        from blueberry_analogue.validation.evaluate import run_validation

        feats = load_feature_cache()
        if feats is None:
            print("No feature cache. Run build first.")
            return 1
        sites = {s.site_id: s for s in load_sites()}
        run_validation(feats, climate_for_features(feats), sites)
        print("wrote docs/analogue/skill-sheet.md")
        return 0
    if args.cmd == "serve":
        if load_feature_cache() is None:
            print("No feature cache. Building offline features first...")
            build_all(live=False)
        from blueberry_analogue.api_app import run

        run()
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
