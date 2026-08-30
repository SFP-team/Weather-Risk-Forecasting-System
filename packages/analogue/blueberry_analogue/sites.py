"""Load the commercial blueberry truth set."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from pydantic import BaseModel

from blueberry_analogue.data.site_catalog import all_sites, write_csv
from blueberry_analogue.paths import SITES_CSV
from blueberry_analogue.systems import ProductionSystem


class Site(BaseModel):
    site_id: str
    name: str
    country: str
    region: str
    admin: str
    lat: float
    lon: float
    cultivar_class: str
    cultivar: str
    media: str
    structure: str
    cover: str
    habit: str
    outcome: str
    source: str
    geocode_precision: str
    notes: str = ""

    @property
    def system(self) -> ProductionSystem:
        return ProductionSystem(
            media=self.media,  # type: ignore[arg-type]
            structure=self.structure,  # type: ignore[arg-type]
            cover=self.cover,  # type: ignore[arg-type]
            habit=self.habit,  # type: ignore[arg-type]
        )

    @property
    def is_presence(self) -> bool:
        return self.outcome in {"commercial_success", "commercial_caution"}

    @property
    def hemisphere(self) -> str:
        return "S" if self.lat < 0 else "N"


def ensure_sites_csv(path: Path = SITES_CSV) -> Path:
    write_csv(path)
    return path


@lru_cache(maxsize=1)
def load_sites(refresh: bool = False) -> list[Site]:
    if refresh or not SITES_CSV.exists():
        ensure_sites_csv()
    df = pd.read_csv(SITES_CSV)
    df = df.fillna("")
    return [Site(**{k: r[k] for k in Site.model_fields}) for r in df.to_dict(orient="records")]


def sites_frame() -> pd.DataFrame:
    return pd.DataFrame([s.model_dump() for s in load_sites()])


def get_site(site_id: str) -> Site:
    for site in load_sites():
        if site.site_id == site_id:
            return site
    raise KeyError(site_id)


def commercial_sites() -> list[Site]:
    return [s for s in load_sites() if s.outcome == "commercial_success"]


def presence_sites() -> list[Site]:
    return [s for s in load_sites() if s.is_presence]
