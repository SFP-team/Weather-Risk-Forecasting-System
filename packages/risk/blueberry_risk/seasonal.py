"""Seasonal risk cards from climatology + model outputs."""

from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any

import pandas as pd

from blueberry_common.schemas import Confidence, SeasonOutlook, SeasonalCard
from blueberry_features.chill import season_chill_to_date


DISCLAIMER = (
    "Seasonal outlooks are probabilistic risk guidance, not daily weather forecasts. "
    "Beyond ~10–14 days, skill is for monthly tilts and event odds vs climatology. "
    "Decision support only — not a substitute for NWS warnings or UF/IFAS advice."
)


def chill_status(chill: float, requirement: int) -> str:
    # Progress expected roughly linear Nov–Feb (~120 days)
    today = date.today()
    if today.month >= 11:
        elapsed = (today - date(today.year, 11, 1)).days
    elif today.month <= 3:
        elapsed = (today - date(today.year - 1, 11, 1)).days
    else:
        # Off season
        return "on_track" if chill >= requirement * 0.9 else "behind"
    expected_frac = min(1.0, max(0.0, elapsed / 120.0))
    expected = requirement * expected_frac
    if chill < expected * 0.85:
        return "behind"
    if chill > expected * 1.15:
        return "ahead"
    return "on_track"


def build_season_outlook(
    farm: dict[str, Any],
    features: pd.DataFrame,
    model_cards: list[dict[str, Any]] | None = None,
) -> SeasonOutlook:
    req = int(farm["chill_requirement_hours"])
    chill = 0.0
    if not features.empty:
        chill = season_chill_to_date(features)
    status = chill_status(chill, req)

    cards: list[SeasonalCard] = []
    if model_cards:
        for c in model_cards:
            cards.append(SeasonalCard(**c))
    else:
        cards = _fallback_cards(farm, features, chill, req)

    return SeasonOutlook(
        farm_id=farm["id"],
        chill_to_date_hours=round(chill, 1),
        chill_requirement_hours=req,
        chill_status=status,  # type: ignore[arg-type]
        cards=cards,
        disclaimer=DISCLAIMER,
        generated_at=datetime.now(timezone.utc),
        sources=["FAWN-style station history (local DB)", "climatology", "ML seasonal head"],
    )


def _fallback_cards(
    farm: dict[str, Any],
    features: pd.DataFrame,
    chill: float,
    req: int,
) -> list[SeasonalCard]:
    today = date.today()
    cards = []
    # Historical freeze rate by month from features
    freeze_rates = {}
    if not features.empty:
        f = features.copy()
        f["date"] = pd.to_datetime(f["date"])
        f["month"] = f["date"].dt.month
        for m, g in f.groupby("month"):
            freeze_rates[int(m)] = float(g["freeze_le_32"].mean()) if "freeze_le_32" in g else 0.1

    for lead in (0, 1, 2):
        # Month ahead
        m = today.month + lead
        y = today.year
        while m > 12:
            m -= 12
            y += 1
        start = date(y, m, 1)
        if m == 12:
            end = date(y, 12, 31)
        else:
            end = date(y, m + 1, 1).fromordinal(date(y, m + 1, 1).toordinal() - 1)

        p_freeze = freeze_rates.get(m, 0.12)
        # Winter months higher
        if m in (12, 1, 2, 3):
            p_freeze = max(p_freeze, 0.15)
        expected_nights = p_freeze * 30 * 0.35

        remaining = max(0.0, req - chill)
        # Rough chill remaining potential by month
        month_chill_potential = {11: 80, 12: 100, 1: 110, 2: 70, 3: 30}.get(m, 10)
        chill_p50 = chill + month_chill_potential * (1 if lead == 0 else 0.6)
        p_short = max(0.05, min(0.9, remaining / max(req, 1) * (0.5 + lead * 0.1)))

        if m in (6, 7, 8, 9):
            narrative = (
                f"Summer period: focus on heat, wet canopy disease, and tropical readiness — "
                f"not chill. Historical wet-day pressure elevated for {start.strftime('%B')}."
            )
            p_freeze = min(p_freeze, 0.02)
            expected_nights = 0.1
            p_short = 0.0
        else:
            narrative = (
                f"{start.strftime('%B %Y')}: historical freeze-night rate suggests "
                f"~{p_freeze*100:.0f}% of days at/under 32°F class risk context; "
                f"chill trajectory {'behind' if chill < req * 0.5 and m <= 2 else 'tracked'} "
                f"vs {req}h cultivar target. Probabilities are climatology-tilted guidance."
            )

        cards.append(
            SeasonalCard(
                period_label=start.strftime("%b %Y"),
                valid_start=start,
                valid_end=end,
                tmean_anomaly_f=0.0,
                tmean_anomaly_range=(-1.5, 1.5),
                precip_tercile={"below": 0.33, "near": 0.34, "above": 0.33},
                p_freeze_window=round(min(0.95, p_freeze * 8), 3),
                expected_freeze_nights=round(expected_nights, 2),
                chill_hours_p10=round(max(0, chill_p50 - 40), 1),
                chill_hours_p50=round(chill_p50, 1),
                chill_hours_p90=round(chill_p50 + 40, 1),
                p_chill_shortfall=round(p_short, 3),
                confidence=Confidence.MED if m in (12, 1, 2) else Confidence.LOW,
                narrative=narrative,
                method="climatology-baseline",
            )
        )
    return cards
