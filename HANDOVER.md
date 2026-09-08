# Project handover — start here

Last updated: 2026-09-08. Current phase: weather-data foundation. **Acquisition is complete; the core handoff and scientific validation are not complete.**

## Implemented and verified

- NASA POWER global daily archive: 2010–2025, with 2011–2025 baseline; all 7,257 planned tiles completed. Meteorology and solar remain on their native grids.
- Fourteen pilot locations: daily weather plus hourly temperature/dewpoint; 42 Parquet files and no missing pilot weather values in the acquisition audit.
- Resumable downloader, checksums, bounded retries/resources, atomic publication, worker locking and coordinate extraction with land/offshore handling.
- Ten global humidity gaps located. Eighty-nine rainfall cell-days above the 1,000 mm/day investigation threshold identified; original values preserved. Extractions expose a suspect-rain flag and admissibility warning.
- Station screening plus a 2020 FAWN Citra / INMET Major Vieira and Rio Negrinho pilot. Warm minimum-temperature biases and missed below-zero days are documented; no correction fitted.
- Last server suite: **35 tests passed**, including six new climate-indicator tests plus downloader and station tests.
- Supervisor demonstration implemented: `docs/weather/climate_evidence/climate_evidence.html` and companion JSON. Papanduva/Citra/Waldo monthly climate, annual variability, reference-window chill, dry spells, threshold exposure, hemisphere-aligned seasons and limitations. Offline generation from existing server archives; no new weather download. Opening layout/charts visually inspected.

## Next actions, in order

Supervisor direction relayed by the user on 2026-09-08: defer cultivar/breeder data to Part 3. Immediate priority is a supervisor-ready demonstration of the downloaded weather and reproducible insights, not cultivar recommendations. Prepare a climate evidence report for Papanduva, Citra and Waldo: acquisition/coverage proof, monthly climate, year-to-year variation, tested chill and cold/heat exposure, dry spells, exploratory seasonal comparisons and station-validation limitations. This is a proposed next deliverable, not yet implemented. Finish the weather core gates alongside it; do not block this work on cultivar data or build the full app yet.

1. Finish corrupted compressed-source response tests.
2. Extend the implemented three-site indicator demonstration to diverse global probes. No invented phenology or cultivar rankings. The supervisor's initial HTML evidence report is ready; broader scientific validation remains pending.
3. Ensure derived calculations honor suspect/missing rainfall and incomplete windows.
4. Audit versions, resource accounting, provenance and completion criteria; write final weather handoff and pause the existing monitor only when those criteria pass.

Multi-year station validation and rainfall measurement-convention checks remain research work. Copernicus comparison requires user credentials and accepted terms; do not expose credentials. Soil is optional. No current cultivar recommendation model or application has been built.

## Where things live

- Code: `pipelines/weather/`; tests: `tests/weather/`.
- Server project: `/media/fpt/fpt2/Weather_Claude`; deployed scripts in `code/`; Python in `env/bin/python`.
- Weather arrays: server `data/normalized/global/`; pilot and station files under `data/normalized/`.
- Operational access and commands: `docs/weather/SERVER_RUNBOOK.md`. Credentials are not included.
- Full scope and completion gates: `DATA_ACQUISITION_HANDOFF.md`.
- Research architecture: `IMPLEMENTATION_PLAN.md`.
- Findings: `docs/weather/VALIDATION_FINDINGS.md` and `REGIONAL_STATION_PILOT.md`.
- Progress history: `docs/PROGRESS_LOG.md`.

## Continuity and publication

Follow `AGENTS.md` after every completed request: update this file when facts change, commit reviewed code/tests/docs and push to the existing GitHub branch. Verify the push and report failures honestly. No empty commits for unchanged checks.

The source reports, supervisor materials and original R script remain local reference inputs and are not part of this publication. Existing absolute local links in older documents may not work on GitHub; use repository-relative paths listed here.

Latest action: generated and tested the supervisor's three-site climate evidence report. Publication result is reported in the task response, not assumed here.
