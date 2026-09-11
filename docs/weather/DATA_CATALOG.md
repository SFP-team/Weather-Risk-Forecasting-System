# Consolidated project data catalog

2026-09-11. Server root: `/media/fpt/fpt2/Weather_Claude`. This catalog organizes existing assets without copying bulk data to GitHub or flattening incompatible grids. Runtime inventory: `reports/data_inventory.json`; refresh with `env/bin/python code/data_inventory.py`.

| Dataset | What is available | Where on server | Limitation |
|---|---|---|---|
| NASA POWER global daily | 2010–2025; all 7,257 planned tiles complete | `data/normalized/global/` | Meteorology and solar have different native grids; not farm measurements |
| Pilot daily and hourly | 14 sites; 2010–2025; daily weather and hourly temperature/dewpoint | `data/normalized/pilot/pilot/` | Hourly is pilot-only, not global |
| Geographic weather probes | Source/extraction engineering checks across diverse coordinates | `data/normalized/pilot/probes/` | Not crop trials or independent weather observations |
| Weather source cache | Checksummed bulk chunks and point API responses | `data/raw/zarr/`, `data/raw/api/` | Preserve for reproducibility; not additional independent weather sources |
| Station observations | Flag-preserving GHCN/FAWN/INMET pilot products; regional comparison focuses on 2020 | `data/normalized/stations/`, `data/reference/` | Unequal coverage and rainfall-convention caveats; multi-year validation pending |
| SoilGrids pilot | New acquisition: five properties × three depths × three statistics for up to 14 sites | `data/raw/soilgrids/`, `data/normalized/soilgrids/` | Read current `state/soil_pilot.json`; static estimates and returned WCS grid, not measured field soil |
| Climate/seasonal analyses | Papanduva/Citra/Waldo report, Paul-method sensitivity, 50/100-hour scenarios | `reports/climate_evidence/`, `reports/stage_scenarios/`, `reports/method_reconciliation.json` | Provisional stage assumptions, not cultivar predictions |
| Data-quality evidence | Coverage, anomalies, extraction checks, station comparisons, new soil audit | `reports/` | Acquisition checks are not scientific sign-off |

## Variables and join rules

Daily weather: minimum/maximum/mean temperature, precipitation, relative humidity, wind, dewpoint and shortwave radiation. Use 2011–2025 for baseline analyses; 2010 is boundary padding. Keep units, UTC convention, source cell, suspect-rain flags and missingness.

Soil: pH, organic carbon, sand, silt and clay. Preserve 0–5/5–15/15–30 cm depths and mean/Q0.05/Q0.95 separately. Join to weather through the existing site ID and requested coordinate, retaining the different source grids. Do not pretend soil was observed on each weather date or that the returned soil raster is a native 250 m pixel.

No new bulk-data copy is needed. Build derived location records referencing existing paths and provenance. Never merge raw station archives, private supervisor materials or future breeding records into a public artifact. Raw and normalized soil values remain on the designated server.

## Still unavailable or unfinished

- Measured field soil/drainage, container substrate and irrigation-water quality/supply.
- Calibrated tunnel microclimate effects, root-zone water balance, cultivar parameters and outcome data.
- Global hourly weather (not part of this acquisition), conditional Copernicus comparison and final weather-core sign-off.
- Global weather contains ten humidity gaps and 89 suspect extreme-rain cell-days; these remain flagged, not silently corrected.

See `SOIL_DATA_RUNBOOK.md` for the bounded soil workflow and `HANDOVER.md` at repository root for the latest verified completion state. The inventory is a snapshot, not a promise that every optional dataset is complete.
