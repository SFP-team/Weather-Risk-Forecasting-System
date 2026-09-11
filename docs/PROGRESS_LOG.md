# Project progress log

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
