"""Production-system transfer functions.

System is a required input:
  media: open_soil | pine_bark | substrate
  structure: open | tunnel | greenhouse
  cover: none | net | woven | ldpe
  habit: deciduous | evergreen

Covers from Matamala et al. 2023 (Top Shelf and Legacy, Chile):
  seasonal UV about 53% net / 42% woven / 10% LDPE
  woven yield +18 to +31% vs open/net
  netting cut yield about 19-21% but raised firmness
  LDPE fruit softer (-6 to -9%)
  neither restores chill

Tunnels: SHB about 1 month earlier; freeze water about 0.1× field;
honey bees stall (need Bombus); Botrytis up; rain-crack down.
Substrate: pH and drainage drop out of GIS.
Pine bark: cools roots, eases pH/OM. Does not change chill or bloom freeze.
HCN: chemical rewrite of the chill envelope. Injures Jewel and others
if the winter is already low-chill.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Media = Literal["open_soil", "pine_bark", "substrate"]
Structure = Literal["open", "tunnel", "greenhouse"]
Cover = Literal["none", "net", "woven", "ldpe"]
Habit = Literal["deciduous", "evergreen"]

COVER_UV = {"none": 1.00, "net": 0.53, "woven": 0.42, "ldpe": 0.10}
COVER_PAR = {"none": 1.00, "net": 0.82, "woven": 0.70, "ldpe": 0.62}
COVER_YIELD = {"none": 1.00, "net": 0.80, "woven": 1.24, "ldpe": 1.05}
COVER_FIRMNESS = {"none": 1.00, "net": 1.12, "woven": 1.00, "ldpe": 0.93}
COVER_RAIN_EXCLUSION = {"none": 0.00, "net": 0.35, "woven": 0.85, "ldpe": 0.95}
COVER_GDD_BOOST = {"none": 1.00, "net": 1.04, "woven": 1.08, "ldpe": 1.12}


class ProductionSystem(BaseModel):
    media: Media = "open_soil"
    structure: Structure = "open"
    cover: Cover = "none"
    habit: Habit = "deciduous"
    hcn: bool = False
    pollinator: Literal["apis", "bombus", "mixed", "none"] = "apis"

    @property
    def label(self) -> str:
        bits = [self.media, self.structure, self.cover, self.habit]
        if self.hcn:
            bits.append("hcn")
        return "|".join(bits)

    @property
    def soilless(self) -> bool:
        return self.media == "substrate"

    @property
    def soil_ph_weight(self) -> float:
        if self.soilless:
            return 0.0
        if self.media == "pine_bark":
            return 0.35
        return 1.0

    @property
    def drainage_weight(self) -> float:
        return 0.0 if self.soilless else 1.0

    @property
    def freeze_water_factor(self) -> float:
        if self.structure == "greenhouse":
            return 0.02
        if self.structure == "tunnel":
            return 0.10
        return 1.0

    @property
    def bloom_advance_days(self) -> int:
        if self.structure == "greenhouse":
            return 40
        if self.structure == "tunnel":
            return 30
        if self.cover == "ldpe":
            return 14
        if self.cover == "woven":
            return 7
        return 0

    @property
    def uv_fraction(self) -> float:
        uv = COVER_UV[self.cover]
        if self.structure == "greenhouse":
            uv *= 0.55
        return uv

    @property
    def par_fraction(self) -> float:
        par = COVER_PAR[self.cover]
        if self.structure == "greenhouse":
            par *= 0.70
        elif self.structure == "tunnel":
            par *= 0.85
        return par

    @property
    def rain_exclusion(self) -> float:
        if self.structure in {"tunnel", "greenhouse"}:
            return 0.97
        return COVER_RAIN_EXCLUSION[self.cover]

    @property
    def gdd_multiplier(self) -> float:
        g = COVER_GDD_BOOST[self.cover]
        if self.structure == "tunnel":
            g *= 1.08
        if self.structure == "greenhouse":
            g *= 1.15
        return g

    @property
    def botrytis_multiplier(self) -> float:
        if self.structure == "tunnel":
            return 1.6
        if self.structure == "greenhouse":
            return 1.3
        if self.cover in {"woven", "ldpe"}:
            return 1.25
        return 1.0

    @property
    def rain_crack_multiplier(self) -> float:
        return max(0.05, 1.0 - self.rain_exclusion)

    @property
    def apis_ok(self) -> bool:
        if self.structure in {"tunnel", "greenhouse"}:
            return self.pollinator in {"bombus", "mixed"}
        return self.pollinator != "none"

    @property
    def chill_relevance(self) -> float:
        if self.habit == "evergreen":
            return 0.05
        if self.hcn:
            return 0.45
        return 1.0

    @property
    def wind_failure_kph(self) -> float | None:
        if self.structure == "tunnel":
            return 110.0
        return None


class SystemEffect(BaseModel):
    """Edits applied to a phenology feature vector before matching."""

    soil_ph_weight: float
    drainage_weight: float
    freeze_water_factor: float
    bloom_advance_days: int
    uv_fraction: float
    par_fraction: float
    dli_multiplier: float
    rain_exclusion: float
    gdd_multiplier: float
    botrytis_multiplier: float
    rain_crack_multiplier: float
    apis_ok: bool
    chill_relevance: float
    wind_failure_kph: float | None = None
    yield_index: float = 1.0
    firmness_index: float = 1.0
    notes: list[str] = Field(default_factory=list)


def system_effects(system: ProductionSystem) -> SystemEffect:
    notes: list[str] = []
    if system.soilless:
        notes.append("Soil pH and drainage weight are 0 under substrate.")
    if system.media == "pine_bark":
        notes.append("Pine bark eases pH and OM. It does not change chill or bloom freeze.")
    if system.structure == "tunnel":
        notes.append("Tunnels advance bloom about 30 days and cut freeze water about 10x.")
        notes.append("Closed tunnels without Bombus fail even if GDD looks perfect.")
    if system.cover != "none":
        notes.append("Covers change UV, PAR, GDD, and rain-crack. They do not restore chill.")
    if system.habit == "evergreen":
        notes.append("Evergreen clock. Chill hours are nearly irrelevant. Winter DLI leads.")
    if system.hcn:
        notes.append("HCN rewrites the chill envelope. Jewel and others can be injured.")
    if system.structure == "greenhouse":
        notes.append("Glasshouse fingerprint includes heating-degree days and winter DLI, not outdoor climate alone.")

    return SystemEffect(
        soil_ph_weight=system.soil_ph_weight,
        drainage_weight=system.drainage_weight,
        freeze_water_factor=system.freeze_water_factor,
        bloom_advance_days=system.bloom_advance_days,
        uv_fraction=system.uv_fraction,
        par_fraction=system.par_fraction,
        dli_multiplier=system.par_fraction,
        rain_exclusion=system.rain_exclusion,
        gdd_multiplier=system.gdd_multiplier,
        botrytis_multiplier=system.botrytis_multiplier,
        rain_crack_multiplier=system.rain_crack_multiplier,
        apis_ok=system.apis_ok,
        chill_relevance=system.chill_relevance,
        wind_failure_kph=system.wind_failure_kph,
        yield_index=COVER_YIELD[system.cover],
        firmness_index=COVER_FIRMNESS[system.cover],
        notes=notes,
    )


def parse_system(
    media: str = "open_soil",
    structure: str = "open",
    cover: str = "none",
    habit: str = "deciduous",
    hcn: bool = False,
    pollinator: str = "apis",
) -> ProductionSystem:
    return ProductionSystem(
        media=media,  # type: ignore[arg-type]
        structure=structure,  # type: ignore[arg-type]
        cover=cover,  # type: ignore[arg-type]
        habit=habit,  # type: ignore[arg-type]
        hcn=hcn,
        pollinator=pollinator,  # type: ignore[arg-type]
    )
