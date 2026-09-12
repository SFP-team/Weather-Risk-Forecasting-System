# Project progress log

## 2026-09-12 — Open-field production core and three-site packet

- Reviewed the 2026-09-12 supervisor transcript against the adaptation plan and R source. Decision: implement the reviewed chill → forcing → offsets → stage-exposure chain in Python (`pipelines/weather/production.py`) instead of an R subprocess runner; constants live in versioned profiles (`legacy_paul_v1`, 100 h and bounded 0–7.2 °C variants).
- Fixed while porting: one season anchor for offsets and reconstructed dates; fixed typed row per winter with status and per-metric reasons; complete-window refusal for chill, forcing and every stage; suspect/out-of-range rain declines rain, dry-spell and disease metrics; zero requirement refused as `anchor_required`; no query-dependent reference scaling or weighted total.
- Both of Paul's classifiers (chill-only; multi-feature with winter-month Tmin/Tmean and freezing) reported from multi-year means, per-year counts and a two-thirds majority. Risks ranked by frequency of winters with an event under his thresholds, with Wilson 95% intervals; other exposures reported unranked.
- Generated `docs/weather/production/` for Waldo, Citra and Papanduva from existing archives. Waldo/Citra Deciduous majority, median flowering 20/26 Jan and harvest from 31 Mar/6 Apr; Papanduva Semi-evergreen, flowering 6 Aug, harvest from 15 Oct. Citra flips to Transitional under the bounded chill definition. Heavy-rain event saturates at 15/15 everywhere; intensity must be compared instead.
- Verification: 18 new tests, 73 server tests passing; exact parity with all 90 existing 50/100 h scenario records; Papanduva mean chill 199.4 h matches the reconciliation; HTML inspected in headless Chrome. No downloads, soil restart, R execution, deployment or cultivar modelling.

## 2026-09-11 — Complete R source review

- Read all 5,759 private source lines sequentially, including superseded blocks and optional genotype processing; traced 332 expressions / 51 top-level functions. Added `docs/weather/R_FULL_CODE_REVIEW.md` with full inventory, output dependencies, code defects, scientific limitations and reuse gates.
- Confirmed single-reference-row suitability scoring, session-dependent analogue classification, incomplete-year schema/group splitting, undefined genotype metadata variable and positional master-answer lookup. Separated these from provisional calendar/system assumptions and uncalibrated relative scores. No original R edits or full workflow execution.
- Expanded `scripts/audit_paul_reference.R` to 22 passing local source-pinned checks (17 reviewed helpers plus syntax/scalar diagnostics); mismatched-source refusal verified. These characterize behavior, not corrected functionality or biological accuracy. Prior 55-test server suite not rerun; no package installation, download or deployment.
- Updated the handover/adaptation gates. Existing archives/UI preserved; next implementation remains the network-free R adapter and Waldo open-field calendar/risk packet. Raw source, transcripts, reports and breeding information remain unpublished.

## 2026-09-11 — Supervisor review and R adaptation plan

- Reviewed the latest supplied discussion; prioritize open field + ground production strategy, calendar and stage-specific risks, beginning at Waldo. Soil/tunnel scoring and genotype work remain later layers.
- Parsed the unchanged private 5,759-line R workflow (332 top-level expressions / 51 functions), audited the useful sections and mapped their actual weather inputs to existing archive fields. Identified two classifiers, provisional planting/phenology rules, missingness/score fallbacks and a northern summary-anchor shift of −31 days.
- Added `scripts/audit_paul_reference.R`; eight local characterization checks passed on synthetic inputs after source fingerprint verification. Only nine reviewed helper definitions evaluated; no workflow download/setup/report code executed. Prior 55 backend tests not rerun; no biological validation claimed.
- Added `docs/weather/R_ADAPTATION_PLAN.md` with modules, data contract, configuration, validation/acquisition/UI stages and acceptance gates. Updated requirements and existing plans to resolve priority/runtime conflicts. Production R modules and fixes remain next work; no acquisition or deployment this turn. Original R, transcripts and private reports remain unpublished.

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
