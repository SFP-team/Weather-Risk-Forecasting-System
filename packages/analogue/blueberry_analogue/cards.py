"""Load and query cultivar × class climate cards."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

import yaml
from pydantic import BaseModel, Field

from blueberry_analogue.paths import CARDS_YAML

CLASS_IDS = (
    "nhb",
    "low_chill_shb",
    "high_chill_shb",
    "rabbiteye",
    "evergreen_zero_chill",
)

HEAT_RANK = {"low": 0.7, "moderate": 1.0, "high": 1.35, "very_high": 1.6}
CRACK_RANK = {"low": 0.6, "moderate": 1.0, "high": 1.4, "very_high": 1.8}


class FloralStage(BaseModel):
    id: str
    msu_uga: int
    bbch: str
    lt_c_low: float
    lt_c_high: float
    notes: str = ""

    @property
    def lt_c(self) -> float:
        return 0.5 * (self.lt_c_low + self.lt_c_high)


class VarietyClass(BaseModel):
    id: str
    label: str
    species: str
    chill_hours_min: float
    chill_hours_max: float
    chill_portions_min: float
    chill_portions_max: float
    uf_hours_min: float
    uf_hours_max: float
    flower_vs_leaf_ratio: float
    negation_c: float
    heat_sensitivity: str
    optimal_t_c: tuple[float, float]
    berry_air_offset_gt_35c: tuple[float, float]
    green_berry_damage_c: tuple[float, float]
    heat_hours_gate: float
    bloom_to_ripe_days: tuple[int, int]
    rain_crack_risk: str
    pollenizer_required: bool
    hcn_typical: bool
    default_habit: str
    analogue_weights: dict[str, float]
    notes: str = ""

    @property
    def chill_hours_target(self) -> float:
        return 0.5 * (self.chill_hours_min + self.chill_hours_max)

    @property
    def chill_portions_target(self) -> float:
        return 0.5 * (self.chill_portions_min + self.chill_portions_max)

    @property
    def chill_relevant(self) -> bool:
        return self.id != "evergreen_zero_chill"


class CultivarCard(BaseModel):
    id: str
    class_id: str
    label: str
    chill_hours: float
    chill_portions: float
    flower_hours: float
    leaf_hours: float
    heat_sensitivity: str
    heat_pn_drop_35c: float
    rain_crack_risk: str
    hcn_ok: bool
    market_window: tuple[int, int] = Field(description="ISO week start, end inclusive")
    notes: str = ""

    @property
    def flower_leaf_mismatch(self) -> float:
        if self.leaf_hours <= 0:
            return 0.0
        return self.flower_hours / self.leaf_hours


class CardLibrary(BaseModel):
    version: int
    stages: list[FloralStage]
    classes: dict[str, VarietyClass]
    cultivars: dict[str, CultivarCard]

    def cultivar(self, cultivar_id: str) -> CultivarCard:
        key = cultivar_id.lower().replace(" ", "_").replace("'", "")
        aliases = {"o_neal": "oneal", "o'neal": "oneal"}
        key = aliases.get(key, key)
        if key not in self.cultivars:
            raise KeyError(f"Unknown cultivar '{cultivar_id}'. Known: {sorted(self.cultivars)}")
        return self.cultivars[key]

    def class_for(self, cultivar_id: str) -> VarietyClass:
        return self.classes[self.cultivar(cultivar_id).class_id]

    def stage(self, stage_id: str) -> FloralStage:
        for stage in self.stages:
            if stage.id == stage_id:
                return stage
        raise KeyError(stage_id)

    def resolved_weights(self, cultivar_id: str) -> dict[str, float]:
        card = self.cultivar(cultivar_id)
        klass = self.classes[card.class_id]
        weights = dict(klass.analogue_weights)
        weights["heat_hours"] = weights.get("heat_hours", 1.0) * HEAT_RANK[card.heat_sensitivity]
        weights["harvest_rain_days"] = (
            weights.get("harvest_rain_days", 1.0) * CRACK_RANK[card.rain_crack_risk]
        )
        return weights


def _load_yaml(path=CARDS_YAML) -> dict[str, Any]:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@lru_cache(maxsize=1)
def load_cards() -> CardLibrary:
    raw = _load_yaml()
    classes = {k: VarietyClass(**v) for k, v in raw["classes"].items()}
    cultivars = {k: CultivarCard(**v) for k, v in raw["cultivars"].items()}
    if set(classes) != set(CLASS_IDS):
        missing = set(CLASS_IDS) - set(classes)
        extra = set(classes) - set(CLASS_IDS)
        raise ValueError(f"Class card mismatch missing={missing} extra={extra}")
    for cultivar in cultivars.values():
        if cultivar.class_id not in classes:
            raise ValueError(f"{cultivar.id} points at unknown class {cultivar.class_id}")
    return CardLibrary(
        version=int(raw["meta"]["version"]),
        stages=[FloralStage(**s) for s in raw["floral_stages"]],
        classes=classes,
        cultivars=cultivars,
    )


def list_cultivars() -> list[CultivarCard]:
    return list(load_cards().cultivars.values())


def list_classes() -> list[VarietyClass]:
    return [load_cards().classes[k] for k in CLASS_IDS]
