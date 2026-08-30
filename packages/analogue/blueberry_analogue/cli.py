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
    p_weather = sub.add_parser("weather", help="Ingest last-decade daily weather for catalog sites")
    p_weather.add_argument("--live", action="store_true", help="NASA POWER daily (dated winters)")
    p_weather.add_argument("--limit", type=int, default=8)
    p_weather.add_argument("--ids", default="", help="Comma-separated site ids")
    p_diag = sub.add_parser("diagnose", help="Diagnose a lat/lon: system, risks, windows, genotypes")
    p_diag.add_argument("--lat", type=float, required=True)
    p_diag.add_argument("--lon", type=float, required=True)
    p_diag.add_argument("--live", action="store_true")
    p_diag.add_argument("--structure", default="open")
    p_diag.add_argument("--media", default="open_soil")
    p_diag.add_argument("--cover", default="none")
    p_dl = sub.add_parser(
        "download",
        help="Campus weather bot: NASA POWER daily for a named plan (run on the university machine)",
    )
    p_dl.add_argument("--plan", default="tonight", choices=["tonight", "future", "belts"])
    p_dl.add_argument("--workers", type=int, default=4)
    p_dl.add_argument("--dry-run", action="store_true")
    p_dl.add_argument("--live", action="store_true", default=True)
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
    if args.cmd == "weather":
        from blueberry_analogue.weather.daily import fetch_nasa_power_daily, fallback_daily_years
        from blueberry_analogue.weather.store import weather_store

        sites = load_sites()
        wanted = {x.strip() for x in args.ids.split(",") if x.strip()}
        use = [s for s in sites if not wanted or s.site_id in wanted][: args.limit]
        db = weather_store()
        n_ok = 0
        for site in use:
            frame = None
            source = "fallback_daily"
            if args.live:
                frame = fetch_nasa_power_daily(site.lat, site.lon)
                if frame is not None:
                    source = "nasa_power_daily"
            if frame is None:
                frame = fallback_daily_years(site.lat, site.lon)
            db.put_series(site.site_id, site.lat, site.lon, frame, source, name=site.name, kind="catalog")
            n_ok += 1
            print(f"{site.site_id:24} {source:28} {len(frame)} days")
        print(f"stored {n_ok} points in {db.path}")
        return 0
    if args.cmd == "diagnose":
        from blueberry_analogue.recommend.diagnose import diagnose_coordinate

        out = diagnose_coordinate(
            args.lat,
            args.lon,
            media=args.media,
            structure=args.structure,
            live=args.live,
            include_similar=False,
        )
        print(json.dumps(
            {
                "query": out["query"],
                "weather": out["weather"],
                "open_field_system": out["open_field_system"],
                "modified_system": {
                    k: out["modified_system"][k]
                    for k in ("open_field_habit", "recommended_habit", "allowed_habits", "notes")
                    if k in out["modified_system"]
                },
                "windows": out["windows"],
                "leading_risks": out["leading_risks"],
                "genotypes": out["genotypes"]["genotypes"][:5],
                "disclaimer": out["disclaimer"],
            },
            indent=2,
        ))
        return 0
    if args.cmd == "download":
        from blueberry_analogue.weather.campus_bot import run_campus_download

        out = run_campus_download(args.plan, live=True, workers=args.workers, dry_run=args.dry_run)
        print(json.dumps({k: out[k] for k in out if k != "estimate"} | {"estimate": out["estimate"]}, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
