"""On-the-fly formulas: climate stats, windows, risk, production system."""

from blueberry_analogue.derive.production_system import classify_production_system, apply_structure_modifiers
from blueberry_analogue.derive.risk_factors import assess_risk_factors
from blueberry_analogue.derive.stats import climate_stats
from blueberry_analogue.derive.windows import derive_windows

__all__ = [
    "apply_structure_modifiers",
    "assess_risk_factors",
    "classify_production_system",
    "climate_stats",
    "derive_windows",
]
