"""Station spine for data-trust, not for the globe screen.

If CHELSA / ERA5-Land / POWER and the nearest 10-year station disagree
on chill or harvest rain, the pixel is untrusted.

Networks we will attach per first-geography country:
  US: FAWN, AgWeatherNet, CIMIS, SCAN, GHCN-Daily
  Chile: DMC / INIA
  Spain: SIAR
  Peru: SENAMHI
  Morocco: DMN
  Australia: SILO
  New Zealand: NIWA VCSN
  Global: GHCN-Daily + ISD hourly
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StationNetwork:
    country: str
    name: str
    role: str


NETWORKS = [
    StationNetwork("US", "FAWN", "Florida ag 15-min, multi-height T"),
    StationNetwork("US", "AgWeatherNet", "Washington blueberry belt"),
    StationNetwork("US", "CIMIS", "California check"),
    StationNetwork("US", "GHCN-Daily", "Long Tmin/Tmax/precip spine"),
    StationNetwork("CL", "INIA / DMC", "Chile south and central"),
    StationNetwork("ES", "SIAR", "Andalucía irrigation network"),
    StationNetwork("PE", "SENAMHI", "Coastal desert check"),
    StationNetwork("MA", "DMN", "Loukkos and Souss"),
    StationNetwork("AU", "SILO", "Gridded station blend"),
    StationNetwork("NZ", "NIWA VCSN", "Landcare comparison"),
]


def trust_band(grid_value: float, station_value: float, rel: float = 0.25, abs_tol: float = 5.0) -> bool:
    """True if the grid and station are close enough to sell a number."""
    if station_value is None or grid_value is None:
        return False
    return abs(grid_value - station_value) <= max(abs_tol, rel * abs(station_value))
