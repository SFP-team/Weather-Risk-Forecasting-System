# Project progress log

## 2026-09-21 — Supervisor review recorded, direction research, future plan

- Recorded Paul's River Valley review as decisions only in `docs/weather/SUPERVISOR_REVIEW_RIVER_VALLEY.md`: risks count only when their stage overlaps the production window and they recur often enough; disease must be ranked; add pollination-unfavourable days, warm mid-winter hours, berry-stage freeze, stage-specific dry spell and a single planting window from his R code; frost-at-every-stage, protection feasibility, post-harvest and wet-picking items deprioritised; management layer after field risks.
- Eight parallel research scouts (Paul's new R file, code audit, crop-modelling second opinion, validation data, genotype layer, management layer, weather inputs, product/deployment); reports saved under `docs/research/2026-09-21/`. Findings: planting = budbreak −105…−30 d and the "multiple windows" are a month-day median artefact; Paul's R already computes Dynamic Model chill portions (chillR constants) but never uses them; ten constants differ from `legacy_paul_v1`; metric definitions are spread over seven code locations; UF trial logs are the highest-value validation data; a cited 40-cultivar attribute table can drive a rule-based shortlist; tunnel/pot effects have published parameters; keep NASA POWER with daily→hourly reconstruction and on-demand hourly; deploy behind token auth over Tailscale.
- `docs/FUTURE_PLAN.md`: six phases with de-duplicated builder-day estimates (14 / 18 / 12 / 8 / 6 / 11), milestones (team-usable ≈ 37 days, v1 four outputs ≈ 51 days ≈ 3 months, validated ≈ 69 days gated on UF data), decisions and data requests by person, critical path and risks.
- Plain-language HTML of the risk-factor review (`docs/weather/RISK_FACTOR_RESEARCH.html`, source `RISK_FACTOR_RESEARCH_PLAIN.md`) added from the 2026-09-15 session. Paul's new R file added to `.gitignore` as a private input. No code, formula, acquisition or deployment change.

## 2026-09-15 — Risk-factor research review and chill-model data check

- Eight parallel literature scouts (chill models, forcing/phenology, freeze, heat/VPD/radiation, rain/disease, water balance, pollination/pests, production-system classification) with primary sources; synthesised in `docs/weather/RISK_FACTOR_RESEARCH.md`: one-page verdict, formula scorecard (keep/change/add with sources), ~35 new computable metrics by stage with inputs, thresholds and confidence, implementation order, open uncertainties.
- Data check `pipelines/weather/chill_comparison.py` on all 18 hourly cells (`docs/weather/chill_comparison.json`): current rule inflates Georgia chill by 60–200 h versus the standard 0–7.2 °C Oct–Feb band; band reproduces FAWN Sebring (104 vs 108 h) and undercounts Gainesville (346/296 vs 503 h) consistent with the +1 °C grid warm bias; CH/CP ratio 12–13.5 in Georgia/north Florida but 4.5–11 in south Florida and 7.0 at Papanduva; Papanduva 183 h but 26 chill portions ≈ Waldo. Negation hours (>21.1 °C mid-winter) 170–940 across the panel.
- Conclusions: chill definition, 50 h anchor, 150 GDD budbreak, single harvest offset, disease-day rule, bloom-only freeze threshold, VPD mean and whole-season dry spell all need revision; pollination weather, stage-aware freeze, bloom heat, leaf-wetness disease rules, stage water balance, evergreen calendar, SWD and post-harvest heat are missing. No formula changed; `legacy_paul_v1` remains the executed profile.

## 2026-09-15 — Southeastern evaluation panel and cell-keyed hourly lookup

- User selected a 15-site panel: 4 Georgia (Georgia/Alma pilot, Homerville, Valdosta, Folkston) and 11 central/south Florida (Dole, Clear Springs, Astin East, Barben, River Valley, PF Berry pilots; Wauchula, Sebring, Lake Placid, Okeechobee, Arcadia towns) and authorized hourly acquisition for cells without a series. Registry and cell index in `pipelines/weather/evaluation_sites.py`; server `config/evaluation_sites.json`, `config/hourly_index.json`, `state/evaluation.json`.
- Acquired five hourly series (Homerville, Valdosta, Folkston, Okeechobee, Arcadia; 140,256 rows each, pilot QC and checksums) through the existing checksummed path under the post-global 200 GiB/500 GiB limits. Transfer counter unchanged at 18,824,365,917 bytes: the cells lay inside 5×5-cell zarr chunks cached for the pilots. Ten panel sites reused stored cells. No global hourly, no daily re-download.
- `location_api.py` → `location-evidence-v3`: hourly resolved by MERRA-2 cell for any pin, with `hourly_source` provenance and a checksum refusal on tampering. Four new tests (cell keys against recorded pilot cells, shared-cell reuse, incomplete series excluded, tampered file refused); server suite 79 passing. API session restarted; unrelated yield jobs untouched.
- UI: 18 snapshots split per site with an index (`scripts/split_snapshots.py`), grouped presets, hourly-cell line in the availability strip. Chromium checks: Arcadia Evergreen → ruler declines, Wauchula "shared with River Valley · 8.2 km", Homerville Deciduous with flowering-freeze 8/15, live pin in Barben's cell gets the packet, live non-cell pin daily-only, no page errors, 390 px no overflow.
- Interpretation limits: town pins are city centres; one series per 0.5°×0.625° cell; assumption-based calendar, not validated phenology; no supervisor pre-registered labels yet. Hosted snapshot not redeployed.

## 2026-09-15 — Growing-cycle ruler and stage exposures

- Built a custom monochrome timeline in `dist/cycle.js`, integrated into `dist/app.js`, `index.html` and `style.css`. Six aligned lanes show winter chill, bud development, flowering, fruit development, harvest and whole-cycle context. The selected stage shows existing freeze, heat, rain, disease-weather, VPD, dry-spell, radiation or heat-unit values as applicable. Detailed tables remain expandable.
- Typical-cycle bars use median boundaries with labelled p10-start to p90-end timing spans. Individual winters show their own dates and exposures. Missing data stays unavailable, event frequency is not presented as crop-loss probability, and evergreen-majority results do not receive a new chill-triggered ruler. No scientific constants, calculations, snapshots or API changed.
- Browser verification: 135 flowering/fruit/harvest windows and exposure values matched the saved records across three sites and 45 winters; all 18 typical stage views checked. Keyboard activation, mouse lane selection, growing-setup note and four synthetic unavailable/incomplete states passed. No page errors during the main smoke sweep. Desktop and 390 px screenshots inspected; 320/390/768 px checks found no page overflow. The scale itself scrolls on narrow screens.
- Downloaded real Chromium HTML and JSON reports. JSON production content matched the original snapshot exactly and retained cycle-view metadata. Found and fixed cloned-select labels reverting to defaults in HTML; confirmed the downloaded report retained winter 2014, Harvest, and selected monthly/annual metric labels. Static HTML removes stage buttons and expands evidence tables. Both frontend scripts passed `node --check`; no new permanent tests or backend test run.
- Updated runbook and handover, removed temporary QA downloads. Local preview only; no hosted redeployment, server-code change, new acquisition or scientific validation. The supplied image was design guidance, not a published asset.

## 2026-09-12 — Open-field production core and three-site packet

- Reviewed the 2026-09-12 supervisor transcript against the adaptation plan and R source. Decision: implement the reviewed chill → forcing → offsets → stage-exposure chain in Python (`pipelines/weather/production.py`) instead of an R subprocess runner; constants live in versioned profiles (`legacy_paul_v1`, 100 h and bounded 0–7.2 °C variants).
- Fixed while porting: one season anchor for offsets and reconstructed dates; fixed typed row per winter with status and per-metric reasons; complete-window refusal for chill, forcing and every stage; suspect/out-of-range rain declines rain, dry-spell and disease metrics; zero requirement refused as `anchor_required`; no query-dependent reference scaling or weighted total.
- Both of Paul's classifiers (chill-only; multi-feature with winter-month Tmin/Tmean and freezing) reported from multi-year means, per-year counts and a two-thirds majority. Risks ranked by frequency of winters with an event under his thresholds, with Wilson 95% intervals; other exposures reported unranked.
- Generated `docs/weather/production/` for Waldo, Citra and Papanduva from existing archives. Waldo/Citra Deciduous majority, median flowering 20/26 Jan and harvest from 31 Mar/6 Apr; Papanduva Semi-evergreen, flowering 6 Aug, harvest from 15 Oct. Citra flips to Transitional under the bounded chill definition. Heavy-rain event saturates at 15/15 everywhere; intensity must be compared instead.
- Verification: 18 new tests, 73 server tests passing; exact parity with all 90 existing 50/100 h scenario records; Papanduva mean chill 199.4 h matches the reconciliation; HTML inspected in headless Chrome. No downloads, soil restart, R execution, deployment or cultivar modelling.
- Same day, UI integration: `location_api.py` now returns `production` (method `location-evidence-v2`), available for pilot coordinates with hourly data and explicitly unavailable elsewhere; `dist/` shows the three outputs as section `00` above the annual cards with per-winter, sensitivity and change lists. Snapshots regenerated; 75 server tests; presets, live-API pilot and non-pilot coordinates, setup note and mobile layout checked in headless Chrome. Hosted snapshot not redeployed.

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
