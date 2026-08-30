"""Build the analogue truth set, features, and skill sheet."""

from __future__ import annotations

import argparse

from blueberry_analogue.pipeline import build_all


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    out = build_all(live=args.live, limit=args.limit)
    print(f"sites={out['n_sites']} features={out['n_features']}")


if __name__ == "__main__":
    main()
