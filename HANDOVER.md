# Project handover — start here

Last updated: 2026-09-11. Current phase: open-ground production analysis design following supervisor UI review. **Global daily weather acquisition is complete; soil acquisition, the core handoff and scientific validation are not complete.**

## Implemented and verified

- Latest supervisor-review audit: `docs/weather/R_ADAPTATION_PLAN.md` maps the R functions/data contract and sets the next milestone to open-ground production strategy, seasonal windows and stage risks at Waldo. Full private R parses (332 expressions / 51 function definitions); eight local, source-pinned characterization checks pass via `scripts/audit_paul_reference.R`. They reproduce source behavior, including a −31-day northern summary-anchor inconsistency; production fixes/library integration remain planned. Original R/transcript stay private and unchanged. No monolithic R run, download or deployment this revision.

- NASA POWER global daily archive: 2010–2025, with 2011–2025 baseline; all 7,257 planned tiles completed. Meteorology and solar remain on their native grids.
- Fourteen pilot locations: daily weather plus hourly temperature/dewpoint; 42 Parquet files and no missing pilot weather values in the acquisition audit.
- Resumable downloader, checksums, bounded retries/resources, atomic publication, worker locking and coordinate extraction with land/offshore handling.
- Ten global humidity gaps located. Eighty-nine rainfall cell-days above the 1,000 mm/day investigation threshold identified; original values preserved. Extractions expose a suspect-rain flag and admissibility warning.
- Station screening plus a 2020 FAWN Citra / INMET Major Vieira and Rio Negrinho pilot. Warm minimum-temperature biases and missed below-zero days are documented; no correction fitted.
- Last server suite: **55 tests passed**, including four location/API-summary and land-mask tests plus the prior 51 weather/soil/scenario/station tests.
- First UI implemented in `dist/`: coordinate/system inputs, six exposure cards, monthly/annual charts and table, soil profiles, qualitative management notes, provenance and HTML/JSON export controls. Monochrome design follows the user's supplied style reference. Three real derived snapshots: Papanduva, Citra, Waldo. The 225 shared annual indicator values match the previous report exactly. No cultivar rankings or calibrated tunnel effects.
- Connected prototype implemented in `pipelines/weather/location_api.py` plus `scripts/preview-ui.mjs`: loopback-only API and fixed SSH-forwarded local proxy; a new London coordinate returned 5,479 daily rows with unavailable chill/soil explicitly shown. Static hosting contains saved snapshots only, not private-network access. Startup, scope and remaining production work: `docs/UI_RUNBOOK.md`.
- UI checks: desktop inspection, 390px layout without page overflow, preset/system interactions, new-coordinate result and invalid WebMCP input. JavaScript syntax checks passed. Export interactions produced no browser console errors, but the embedded browser did not expose a download event; download-file compatibility/parity remains a QA item. This is not production or scientific validation.
- Found and excluded Natural Earth's explicitly labelled artificial “Null island” polygon; `land-mask-v2` records the exclusion in provenance. Regression includes null-labelled real land; remote snapshots regenerated from unchanged archives.
- Soil acquisition started: 157/630 records downloaded; Citra/Papanduva/Waldo complete at 45 each, Astin East 22. Five properties, three depths, mean/Q0.05/Q0.95. WCS timed out three times at Astin East sand 5–15 cm Q0.05; worker stopped `blocked_source`, no active soil worker. Do not reset attempts blindly. Raw/normalized soil stays on server. Returned WCS pixels are geographic/reprojected, not asserted native SoilGrids cells; scientific/native-grid validation pending.
- Consolidated inventory implemented: `pipelines/weather/data_inventory.py`, server `reports/data_inventory.json`; readable map in `docs/weather/DATA_CATALOG.md`. Soil runbook: `docs/weather/SOIL_DATA_RUNBOOK.md`. No weather redownload or bulk-data duplication.
- Exploratory 50/100-hour stage comparison implemented in `pipelines/weather/stage_scenarios.py`; offline HTML/JSON in `docs/weather/climate_evidence/stage_scenarios.*`. Paul-derived UTC assumptions, not calibrated cultivar predictions. Citra/Waldo have 15 paired winters; Papanduva has 13 because 2015/2023 do not reach 100 hours. Complete-window and suspect-rain refusal enforced; no downloads.
- Paul's method audit and controlled UTC chill sensitivity completed: `docs/weather/PAUL_RECONCILIATION.md`, companion JSON and `pipelines/weather/reconcile_methods.py`. Papanduva mean changes from 178.9 to 199.4 hours when matching the supplied R window/threshold on our data; this is not an exact reproduction of his 209.4-hour report. Time standard, historical period and generating configuration remain unresolved. No R workflow execution or cultivar modelling.
- Supervisor demonstration implemented: `docs/weather/climate_evidence/climate_evidence.html` and companion JSON. Papanduva/Citra/Waldo monthly climate, annual variability, reference-window chill, dry spells, threshold exposure, hemisphere-aligned seasons and limitations. Offline generation from existing server archives; no new weather download. Opening layout/charts visually inspected.

## Next actions, in order

**Next implementation:** follow `docs/weather/R_ADAPTATION_PLAN.md` milestones A–B: isolate reviewed R science, adapt existing point data, and produce the Waldo open-ground strategy/calendar/stage-risk packet, then Citra/Papanduva. Fix calendar anchors/missingness, distinguish both classifiers and require an explicit anchor for a zero-chill scenario. Do not make cultivar data, additional soil or tunnel models prerequisites. Expanded hourly evaluation needs a finite registry before acquisition; no global hourly download.

UI/serving work: surface those three production outputs once evaluated; authenticated hosted archive connectivity, durable jobs/cache, granular missing-data states and export compatibility remain needed. The first connected slice exists; full architecture in `docs/UI_IMPLEMENTATION_PLAN.md` remains staged work. "Live" is historical analysis, not a forecast. The initial owner-private snapshot UI was successfully published through Sites from commit `b9cb0ff`; registration is in `.openai/hosting.json`. This audit does not redeploy it.

2026-09-11 management refinement: `docs/weather/LOCATION_MANAGEMENT_PLAN.md` specifies subsequent soil/cover/root-zone layers. Preserve completed soil records and source-blocked attempts; do not let the soil outage block the new open-ground calendar/risk milestone. ET0 and tunnel models are not implemented. Cultivar work remains deferred. Continue the weather-core gates below alongside this work.

Supervisor direction relayed by the user on 2026-09-08: defer cultivar/breeder data to Part 3. The three-site climate evidence report and exploratory seasonal comparison are implemented. The user subsequently requested this initial UI. Finish the weather core gates alongside supervisor review; do not block this work on cultivar data or imply the full app is complete.

1. Finish corrupted compressed-source response tests.
2. Extend the implemented three-site indicator demonstration to diverse global probes. No invented phenology or cultivar rankings. The supervisor's initial HTML evidence report is ready; broader scientific validation remains pending.
3. Ensure derived calculations honor suspect/missing rainfall and incomplete windows.
4. Audit versions, resource accounting, provenance and completion criteria; write final weather handoff and pause the existing monitor only when those criteria pass.

Multi-year station validation and rainfall measurement-convention checks remain research work. Copernicus comparison requires user credentials and accepted terms; do not expose credentials. Soil is optional. A research UI exists; no cultivar recommendation model has been built.

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

Latest action: reviewed new supervisor transcript and private R code, added eight passing local characterization checks and revised the execution plans. The prior 55-test server suite was not rerun this turn. Locally R 4.6.1 exists; lubridate/ChillModels are not installed; server R has not been checked. No new acquisition, scientific model or deployment. Publication result is reported in the task response, not assumed here.
