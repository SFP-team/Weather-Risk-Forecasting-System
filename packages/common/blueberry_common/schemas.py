from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class PhenologyStage(str, Enum):
    DORMANT = "DORMANT"
    SWELL = "SWELL"
    PINK = "PINK"
    OPEN_BLOOM = "OPEN_BLOOM"
    PETAL_FALL = "PETAL_FALL"
    GREEN_FRUIT = "GREEN_FRUIT"
    HARVEST = "HARVEST"


class ProductionSystem(str, Enum):
    DECIDUOUS = "deciduous"
    EVERGREEN = "evergreen"


class TonightStatus(str, Enum):
    LOW = "LOW"
    WATCH = "WATCH"
    PROTECT = "PROTECT"
    BEYOND_SYSTEM = "BEYOND_SYSTEM"


class Confidence(str, Enum):
    LOW = "low"
    MED = "med"
    HIGH = "high"


class StationOut(BaseModel):
    id: str
    name: str
    county: str
    lat: float
    lon: float
    elev_m: float
    region: str
    fawn_id: str | None = None


class FarmOut(BaseModel):
    id: str
    name: str
    county: str
    lat: float
    lon: float
    nearest_station_id: str
    cultivars: list[str]
    chill_requirement_hours: int
    production_system: ProductionSystem
    phenology_stage: PhenologyStage
    system_rate_in_per_hr: float = 0.2
    cold_spot_bias_f: float = 0.0
    irrigation_freeze_protection: bool = True
    acres: float = 20.0


class FarmUpdate(BaseModel):
    phenology_stage: PhenologyStage | None = None
    cold_spot_bias_f: float | None = None
    chill_requirement_hours: int | None = None
    cultivars: list[str] | None = None


class TonightRisk(BaseModel):
    farm_id: str
    status: TonightStatus
    headline: str
    weather_fact: str
    crop_meaning: str
    suggested_action: str
    forecast_tmin_f: float | None = None
    dewpoint_f: float | None = None
    wind_mph: float | None = None
    coldest_hour_local: str | None = None
    start_threshold_f: float | None = None
    confidence: Confidence = Confidence.MED
    sources: list[str] = Field(default_factory=list)
    checklist: list[str] = Field(default_factory=list)
    generated_at: datetime


class DayOutlook(BaseModel):
    date: date
    tmin_f: float | None = None
    tmax_f: float | None = None
    precip_in: float | None = None
    freeze_risk: Literal["low", "moderate", "high"] = "low"
    disease_wetness_risk: Literal["low", "moderate", "high"] = "low"
    harvest_rain_risk: Literal["low", "moderate", "high"] = "low"
    notes: str | None = None


class SevenDayOutlook(BaseModel):
    farm_id: str
    days: list[DayOutlook]
    sources: list[str] = Field(default_factory=list)
    generated_at: datetime


class SeasonalCard(BaseModel):
    period_label: str
    valid_start: date
    valid_end: date
    tmean_anomaly_f: float | None = None
    tmean_anomaly_range: tuple[float, float] | None = None
    precip_tercile: dict[str, float] | None = None  # below/near/above
    p_freeze_window: float | None = None
    expected_freeze_nights: float | None = None
    chill_hours_p10: float | None = None
    chill_hours_p50: float | None = None
    chill_hours_p90: float | None = None
    p_chill_shortfall: float | None = None
    confidence: Confidence = Confidence.MED
    narrative: str
    method: str = "climatology+ml"


class SeasonOutlook(BaseModel):
    farm_id: str
    chill_to_date_hours: float
    chill_requirement_hours: int
    chill_status: Literal["behind", "on_track", "ahead"]
    cards: list[SeasonalCard]
    disclaimer: str
    generated_at: datetime
    sources: list[str] = Field(default_factory=list)


class RiskEventOut(BaseModel):
    event_type: str
    window_start: date
    window_end: date
    probability: float
    severity: int
    advisory_text: str
    drivers: dict[str, Any] = Field(default_factory=dict)


class ChillProgress(BaseModel):
    farm_id: str
    station_id: str
    as_of: date
    chill_hours: float
    requirement_hours: int
    pct_complete: float
    status: Literal["behind", "on_track", "ahead"]


class ObservationSummary(BaseModel):
    station_id: str
    date: date
    tmin_f: float | None
    tmax_f: float | None
    precip_in: float | None
    rh_mean: float | None
    wind_mean_mph: float | None
    chill_hours: float | None
    freeze_le_32: bool | None


class HealthOut(BaseModel):
    status: str
    version: str
    database: str
    stations: int
    farms: int
