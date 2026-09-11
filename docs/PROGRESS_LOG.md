# Project progress log

## 2026-09-11 — First connected climate/soil UI

- Built the monochrome coordinate-first dashboard from the supplied style reference: six exposure cards, monthly/annual charts and table, soil uncertainty, four-system qualitative notes, provenance and HTML/JSON export controls.
- Published-source candidates contain three real derived snapshots only. Private loopback Python API and fixed local SSH proxy support new coordinates without acquisition; London returned daily data with chill/soil correctly unavailable. Hosted static mode supports the presets, not arbitrary-coordinate private-network access.
- All 55 server tests pass. The 225 shared annual values match the prior reports exactly. Desktop/mobile layout and primary controls checked; invalid input leaves no fabricated output. Export click had no console errors, but embedded-browser download event/file verification remains incomplete.
- Geographic negative control exposed the source's artificial “Null island” polygon. Excluded only the labelled placeholder, added checksum-backed fixture coverage including null labels, and regenerated summaries. Original mask/weather/soil bytes preserved.
- Added `docs/UI_RUNBOOK.md`; production connectivity, durable jobs/cache, finer availability states, stage overlays, export compatibility and scientific validation remain next-stage work. No new downloads or cultivar modelling. Deployment/publication is verified separately, not assumed by this entry.

## 2026-09-11 — Coordinate dashboard implementation design

- Added `docs/UI_IMPLEMENTATION_PLAN.md`: coordinate/system inputs, six exposure cards, historical evidence, soil context, conditional management comparison and consistent on-page/export report.
- Defined partial-result states, separate evidence/availability labels, durable jobs, versioned cache and private-server access boundary. Reuse existing Python science for the interim slice rather than the earlier unimplemented R-first architecture.
- Plan only: no frontend, API, deployment, download or new runtime tests. Existing 51-test result unchanged; cultivar work remains deferred.

## 2026-09-11 — Soil acquisition and consolidated catalog

- Verified server mount and completed global weather state; preserved existing data and unrelated server work.
- Implemented bounded WCS soil downloader for 630 property/depth/statistic subsets across 14 sites. Downloaded 157 records (Citra/Papanduva/Waldo 45 each; Astin East 22) before three source timeouts stopped acquisition. Remaining 473 records not completed; no duplicate weather workers or downloads.
- Readback/checksum audit passed all 157, with 52 ordered quantile pairs and no source no-data values. WCS output is geographic/reprojected; native-grid parity and field validation remain pending.
- Added catalog/inventory, soil audit and six unit tests. Full server suite 51 passing tests. Rasterio installed in project virtual environment only. Raw soil and weather stay on server.

## 2026-09-11 — Location × growing-system research plan

- Reviewed original architecture and used three parallel research reviews for six weather hazards, protected growing systems and soil/root-zone constraints.
- Added `docs/weather/LOCATION_MANAGEMENT_PLAN.md`: implementation sequence, evidence registry, conditional four-system output, targeted soil acquisition and validation gates.
- Separated direct fruit rain from root-zone water balance; no automatic tunnel freeze protection, pot drought immunity or field drainage inference from soil maps.
- Planning/documentation only: no downloads, runtime changes, new tests or calibrated management recommendations. Prior 45-test result unchanged.

## 2026-09-08 — Exploratory seasonal exposure scenarios

- Implemented and ran 50/100-hour Paul-derived UTC scenarios across three sites and 15 winters, with annual assumed flowering/harvest dates, cold exposure, harvest rainfall and production dry spells.
- Paired harvest rain differences: Citra +44.4 mm, Waldo +35.7 mm (15 winters), Papanduva −12.9 mm (13 winters). Papanduva 2015/2023 never reach 100 hours; no zero-risk substitution.
- Added seven tests; full server suite 45 passing tests. Existing archives only, no new downloads or calibrated cultivar claims.
- Delivered offline HTML/JSON in `docs/weather/climate_evidence/stage_scenarios.*`; broader core gates and independent scientific validation remain unfinished.

## 2026-09-08 — Paul method reconciliation

- Audited executable R definitions and local HTML narrative; original private/reference files remain unpublished.
- Identified below-only vs bounded chill, six- vs four-month seasons, LST vs UTC, crop-year labels, historical baseline and 50-hour configuration vs 100-hour narrative benchmark differences.
- Ran controlled sensitivity on three sites ×15 winters. Papanduva mean 178.9 →199.4 h under changed season/definition on identical UTC data; residual relative to reported 209.4 h remains unresolved.
- Added three known-answer tests; full server suite now 38 passing tests. No downloads, original-data changes, R execution or phenology calibration.
- Deliverable: `docs/weather/PAUL_RECONCILIATION.md` plus derived JSON and reproducible script.

## 2026-09-08 — Supervisor climate evidence report implemented

- Generated self-contained HTML and derived JSON for Papanduva, Citra and Waldo from existing daily/global and hourly/pilot archives. Added six charts, seasonal comparison, 15-year tables, coverage and station limitations.
- Tested complete-window chill (inclusive 0–7.2°C), missingness, cross-year/leap boundaries, dry spells and suspect rain refusal. Server suite: 35 passing tests.
- Reference-window chill medians: Papanduva 168 h, Citra 288 h, Waldo 348 h. These are descriptive estimates under documented UTC windows, not cultivar requirements. No new weather downloads or model fitting.
- Reviewed the opening HTML layout and charts in a Chrome screenshot. Final core audit and broader probes remain pending.

## 2026-09-08 — Supervisor demonstration priority

- User relayed supervisor guidance to complete the first part before requesting cultivar data for Part 3.
- Recorded the immediate deliverable as a reproducible climate evidence report using downloaded data, initially Papanduva versus Citra and Waldo. No cultivar rankings, calibrated phenology, or full application implied.
- This turn plans the demonstration only; no indicator implementation or new scientific tests were performed.

## 2026-09-08 — Continuity baseline

- Added `HANDOVER.md` and `AGENTS.md` to make project state and end-of-request publication expectations explicit.
- Prepared the existing weather pipeline, tests, plans and validation reports for version control; excluded bulk data, credentials, machine caches and supplied private/reference artifacts.
- Recorded the existing 29-test server result; no new weather acquisition or scientific validation performed in this documentation task.
- Core remains incomplete: indicator demonstrations, compressed-source failure tests and final audit outstanding.
