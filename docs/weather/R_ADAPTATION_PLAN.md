# Open-field production analysis — R adaptation and execution plan

2026-09-11. **Audit and implementation plan, not an implemented production classifier/calendar.** This revision follows the latest supervisor discussion. It supersedes the earlier priority of expanding soil/tunnel analysis before establishing the open-field baseline. Keep the existing dashboard and downloaded data.

Follow-up: [complete source review](R_FULL_CODE_REVIEW.md) now covers every line and all 51 top-level functions, with 22 passing characterization checks. The original targeted audit below remains historical evidence; additional implementation gates are recorded in section 3.

**Revision 2026-09-12.** Milestones A and B are implemented in Python, not R: `pipelines/weather/production.py` carries the reviewed science with the section 3 corrections applied and the constants in versioned profiles; the R subprocess runner, JSON contract and isolated R library in section 6A are no longer planned. `scripts/audit_paul_reference.R` remains the characterization oracle for the R helpers. The three-site packet is in `production/`. Milestones C (frozen reference panel), D (bounded hourly registry, after a validated daily-to-hourly chill interpolation) and E–F stand, with the supervisor decisions listed in `../../HANDOVER.md` as prerequisites for the sweep.

## 1. Next deliverable

For **one coordinate, open field + ground**, return three linked outputs:

1. A provisional **production-system hypothesis**: evergreen, semi-evergreen or deciduous, with the rule, evidence and disagreements visible.
2. An **assumption-based seasonal calendar**: chill fulfilment, budbreak, flowering and harvest, with establishment shown separately and only where supported.
3. **Risks within those stages**: flowering freeze, fruit-stage heat, harvest rain, production dry spells and supporting weather indicators.

Annual climate cards remain useful context, but do not answer these questions alone. Start with **Waldo**, then Citra and Papanduva. Soil scoring, tunnel/pot adjustments and cultivar ranking follow the open-field evaluation. Soil already downloaded can remain visible as context; it does not block this milestone.

The supplied transcript has unreliable speaker labels and some speech-recognition errors. This plan uses it as project evidence, not executable instructions. Unrelated discussion about imaging and other field work is excluded. Its broad threshold examples are research assumptions, not universal agronomic facts.

## 2. Source audit and what is reusable

Local reference: `blueberry_climate_analog_workflow.R`, 5,759 lines, SHA-256 `5e8589db6b017e7e0b082639c6212df29a36da76a74b3a29e709979378c8ab55`. R parsed all **332 top-level expressions and 51 function definitions**. The original is unchanged and excluded from Git. The line references below identify that specific snapshot.

| Component | R source | Reuse decision / current gap |
|---|---|---|
| Named constants | 87–119 | Move reviewed assumptions into versioned configuration; separate chill *threshold*, chill *requirement*, GDD and day offsets. Do not tune silently. |
| VPD, day length, run lengths | 238–266 | Reuse formulas with explicit input units and stricter missingness. VPD needs humidity/dewpoint as well as temperature; day length needs latitude/date. |
| Hemisphere and winter features | 457–776, 819–866, 1146–1518 | Reuse explicit biological-month and winter mappings. Recompute monthly means from our daily series; do not rename NASA features as WorldClim observations. |
| Hourly chill/freezing | 798–813, 3757–3888 | Reuse event definitions and hourly accumulations; keep alternative chill models/definitions separate. Require complete, unique, ordered timestamps. |
| Production-system rules | 3039–3158 and 4337–4344 | Implement both as named alternatives. The script contains **two different classifiers**, not one consistent universal rule. |
| Stage calendar | 3814–3919 | Highest-value reusable chain: chill fulfilment → heat accumulation → flowering/harvest offsets. Our Python 50/100-hour scenario already implements much of this for three sites. |
| Stage exposures | 3920–3978 | Extend beyond our four existing scenario metrics to heat, freeze events, flowering rain, VPD, weather favourable to disease, radiation and GDD. |
| Historical summaries and planting heuristic | 4034–4111 | Reuse per-year summaries, but correct the northern summary anchor and guard impossible establishment windows. It is a heuristic, not an optimized planting model. |
| Relative risk indices | 4119–4246 | Reuse only with a frozen reference panel, defined quantiles, coverage checks and visible weights. A relative index is not a damage probability. |
| Directional suitability | 4325–5338 | Later diagnostic; not necessary for the next three outputs. Do not conflate similarity, weighted suitability and risk. |
| Downloads, target-specific maps, analogue selection, genotype ranking | Sections 3–5, 7–8, 13–15 | Bypass for the first adapter. Do not run the monolith, redownload data, install all its packages or produce genotype outputs. |

The code chooses dates under specified assumptions; it **does not search all possible planting dates and discover an objectively optimal window**. A future date-search optimizer needs its own objective, feasible strategies and held-out evaluation. It is not part of the first adaptation.

## 3. Corrections required before reuse

### Additional gates from the complete source review

- **Stable schema and keyed identities:** incomplete site-year returns omit `point_type`, splitting summary groups after row binding; emit a fixed typed row with status/reasons for every year. Master answers must select the target by key, never the source's hard-coded 32nd row. Require one summary per location/scenario.
- **Explicit classification dependencies:** analogue scoring reads `system_assignment` before this script creates it, allowing missing or stale labels. Do not inherit global R session objects; compute/pass current labels before their consumers. The optional genotype metadata branch also references an unassigned `target_system`; keep genotype execution deferred.
- **Correct reference population:** directional suitability currently selects only the first reference row, making scores binary/order-dependent. Later adaptation must use whole named columns and pass row-permutation tests. Its separate envelope table currently uses full columns and can disagree with the contribution output.
- **Separate inference from validation:** detailed chill classification followed by scoring against that same inferred class gives full chill-hours alignment across 0–800 hours; this is not independent evidence of feasibility. Preserve disagreements between broad/detailed classifiers and avoid treating rule-derived confidence as calibrated accuracy.
- **Do not overinterpret similarity:** query-specific median-distance scaling gives identical kernel scores when all distances grow proportionally. Freeze/calibrate comparison scales before comparing different targets. These analogue/suitability repairs do not block the first raw calendar/stage-risk packet.

### Calendar and phenology

- **150 is °C-days, not days or chill hours.** The source sums `max(Tmean − 7, 0)` from chill fulfilment until 150. Flowering is budbreak +14 to +35 days; harvest is flowering **start** +70 to +110 days. These are provisional constants, not measured genotype parameters.
- **Northern summary dates are inconsistent:** `chill_window_dates()` starts on November 1, but `median_offset_date()` reconstructs offsets from October 1. The audit reproduces a **−31-day shift**. Derive all displayed dates from the same season anchor as the calculation. Do not change source weather timestamps to repair a presentation error.
- Keep explicit season start/end and actual dates. Use the existing `winter_year` convention: northern winter ending in that year, southern winter occurring in that year. Also retain the legacy R crop-year label where needed for comparison. Do not compare southern labels without aligning the actual dates.
- Keep **2011–2025** as the analysis baseline and 2010 as padding. A 450-day horizon can run beyond the available archive; mark incomplete seasons rather than shrink the horizon or count missing days as safe. Report valid/expected years per metric.
- **Zero chill is not a complete evergreen model.** In the source it triggers on the first available winter date even if no chill accumulated. Support a separate `no_chill_scenario` only with an explicit forcing anchor; otherwise return `anchor_required`. Do not silently make 0 hours the default or infer it from a class label.
- The source establishment rule uses start +30 days and `max(60, budbreak_offset −45)` for the end. For an early budbreak this can end after budbreak. Preserve it as legacy evidence; the proposed corrected heuristic uses the stated pre-budbreak constraint and returns `no_valid_establishment_window` if the interval is empty. Keep planting a young plant distinct from recurring flowering/harvest of a bearing plant.

### Definitions, missingness and comparison

- The executed R chill rule is **T <7.2°C without a lower bound**, despite an unused `chill_hour_min_c = 0`. Our dashboard uses **0 ≤ T ≤7.2°C** over a shorter winter. Preserve `paul_below_7_2` and `bounded_0_7_2` as separate named methods; no silent replacement of the current card.
- Source R requests LST then labels timestamps UTC. Our archive is UTC. Keep UTC for the adapted baseline and identify it as a changed input convention, not exact reproduction of old HTML. NASA explicitly distinguishes UTC and LST and documents the API conversion. [NASA time standards](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)
- The source's 720-hour minimum is not full-season coverage; removing nonfinite temperatures compresses time for stateful models. Missing GDD is replaced with zero, some stage sums drop missing values, and missing dry flags break runs. Retain our complete-window and suspect-rain refusal instead.
- `scale_high_risk()` returns 0.5 when the reference range is absent/constant—even for a missing target. Replace with `not_comparable`, never invented medium risk. Explicitly test NA before any risk class; the source's final catch-all can otherwise label an unavailable score “Very high”.
- The source mixes quantile types 8 and 7 in different sections. Use type 8 for the legacy risk-index comparison; name/version any other convention. Do not silently normalize scores by whichever features happen to be available.
- Normalized score, historical event frequency, exposure amount and evidence quality must be separate fields. Freeze frequency is conditional on valid modelled flowering windows; display how many years had no window/unmet chill as well.

## 4. Data contract: what we already have

This mapping is verified against `pipelines/weather/pilot.py` and the existing data catalog. No new API key or weather download is needed to start at Waldo.

| Existing archive field | R-facing field | Unit / use |
|---|---|---|
| Daily `time` | `date` | UTC date; exact daily coverage |
| Daily `tmean_c` | `T2M` | °C; daily GDD and legacy daily VPD |
| Daily `tmin_c`, `tmax_c` | `T2M_MIN`, `T2M_MAX` | °C; flowering freeze and fruit heat |
| Daily `precip_mm` | `PRECTOTCORR` | mm/day total; stage rainfall and dry spells |
| Daily `rh_mean_pct` | `RH2M` | %; daily VPD / disease-weather proxy |
| Daily `shortwave_mj_m2_day` | `ALLSKY_SFC_SW_DWN` | MJ/m²/day; **already converted**, do not multiply by 0.0864 again |
| Hourly `time`, `tmean_c` | `datetime`, `T2M` | UTC / °C; chill, freezing duration and event continuity |
| Hourly `dewpoint_mean_c` | Separate derived-humidity input | °C; optional humidity/VPD enhancement, not required by the legacy core |
| `precip_suspect_extreme` | QC sidecar / masked stage input | Preserve original measurement and exclusion reason separately |
| Requested pin, source cells, hashes | Site/manifest metadata | Requested geometry is not the source pixel; preserve each variable's grid |

Daily mean RH supports the existing **daily** disease-weather proxy; it does not reveal hours of leaf wetness. VPD cannot be obtained from temperature alone. The source's `es(Tmean)*(1−RHmean/100)` is a daily proxy; optional hourly temperature/dewpoint derivation is a separately labelled calculation, not automatically the same daily quantity. [FAO humidity and VPD methods](https://www.fao.org/4/X0490E/x0490e07.htm)

Global daily data exist; hourly temperature/dewpoint exist at 14 pilot sites. Full hourly weather is not necessary to reproduce these particular R daily-stage indicators. Conversely, hourly temperature alone cannot reconstruct measured rainfall, radiation, soil moisture or irrigation.

## 5. Scientific configuration

Use immutable, versioned profiles; expose only reviewed controls in an “Assumptions” panel.

- **Legacy comparison:** source 50-hour requirement, T <7.2°C, six-month winter, 7°C base/150 GDD, +14/+35 flowering and +70/+110 harvest offsets. Use our UTC baseline, with that difference explicit.
- **Sensitivity:** 50 and 100 hours first (already comparable with Python). Add other requirements after boundary tests. Bounded chill is a separate definition, not merely another requirement value.
- **Default classifier proposal:** multi-feature open-field climate-support rules: evergreen requires mean season chill <100 h, lowest winter-month mean daily Tmin >7.2°C, lowest winter-month mean temperature >12.8°C, mean season freezing hours ≤1 and freeze-risk months ≤0; deciduous requires mean season chill ≥300 h; remaining complete cases are transitional/semi-evergreen. All required features must be present. Winter months are explicitly Jan–Mar north / Jul–Sep south for legacy compatibility.
- **Audit comparator:** detailed chill-only rule <100 / [100,300) / ≥300, applied identically to targets and references. Show disagreement with the multi-feature rule; do not let source execution order choose which label appears. The 150-hour value in the broad script is a transitional-confidence sub-band, not another mandatory class boundary.
- Replace source “High confidence” with “rule-consistent” plus sensitivity/coverage information until empirical calibration. Report the distribution across years as supporting variability, separate from the class of the multi-year mean.
- Source risk weights are 0.20 chill, 0.20 flowering freeze, 0.15 heat, 0.15 harvest rain, 0.10 dry spell, 0.10 disease weather and 0.10 variability. Retain as an **expert-assumption profile**, disabled as a default recommendation until reference and missingness gates pass. Distinguish raw-index rank (source behavior) from weighted contribution rank.

These numerical thresholds are hypotheses to review, not proof that evergreen cultivation is impossible above a universal chill count. UF/IFAS describes climate, cultivar choice and management jointly, including evergreen management under tunnels in north-central Florida. [UF/IFAS evergreen production](https://ask.ifas.ufl.edu/publication/HS1362)

## 6. Implementation sequence with acceptance gates

### A — Isolate R science and connect existing data

Create planned modules under `science/r/`: `input_contract.R`, `chill.R`, `calendar.R`, `systems.R`, `stage_risks.R`, `summaries.R`, and `run_location.R`. Preserve attribution, source fingerprint and a behavior-change ledger. Do not copy the private monolith into Git; review the extracted module contents for publication separately.

Python remains responsible for archive extraction, QC, API/jobs and daily climate context. An adapter exports **one point** to a bounded server job directory with `manifest.json`, daily and hourly series, units and source/QC hashes. R reads that contract and emits one atomic JSON result; NA/NaN become null with a reason, not zero. Use JSON initially to avoid an unneeded R Arrow dependency. Preserve full precision and an explicit timestamp format.

Invoke a fixed `Rscript --vanilla` runner, not a shell command assembled from user input. Install only reviewed dependencies in an isolated project R library, lock versions, and make runtime analysis network-free. The adapter accepts validated coordinates/config only; no browser-supplied paths or R expressions. Bound input size, subprocess runtime and concurrency. Do not invoke the R download/setup sections.

**Gate:** contract round trips, units/timestamps, no download calls, three-site annual parity and exact 50/100-hour dates/metrics against existing `stage_scenarios.py`. The R module becomes the source for the new production outputs; Python scenarios remain regression references, not an independently diverging production implementation.

### B — Deliver the Waldo reference packet

Generate all 15 season records, both classifier results, dated flowering/harvest windows, conditional stage metrics and failure reasons. Include corrected date reconstruction, coverage and assumption sensitivity. Produce Citra/Papanduva alongside Waldo to test the opposite hemisphere and unmet-chill years.

**Gate:** reviewed rule explanations, no zero-risk result for a missing stage, no impossible planting interval and no claim of exact historical HTML reproduction. Report medians/ranges using anchored offsets and per-year dates, not averages of month numbers across New Year. Do not start with a new globe-wide acquisition.

### C — Complete stage risks and comparison

First show raw metrics: flowering Tmin/≤−2.2°C days and years with an event; fruit Tmax ≥32/35°C days; harvest total/≥10 mm days; longest <1 mm production dry spell; daily weather meeting 15–28°C, RH≥85% and rain≥0.1 mm; stage VPD, radiation and GDD. Label the last proxy “disease-favourable weather”, not predicted disease incidence. Radiation remains its own exposure, not a fabricated probability or an unreviewed extra weight.

Freeze a **versioned southeastern US reference panel** independent of the queried target. The existing pilot subset is a provisional panel, not representative global truth. Exclude the target; record source cells to avoid treating duplicate grid cells as independent evidence. Publish valid reference count and p10/p90 for every comparison. Require the preregistered panel to have complete required features and nondegenerate ranges; otherwise leave comparison/total unavailable. Do not auto-select a different set of “closest analogues” for each query and call its percentiles globally comparable.

**Gate:** exact raw-metric tests; stable scores under target insertion/order changes; no median imputation, missing-weight renormalization or 0.5 fallback in the default score; every rank explains its denominator/reference and sensitivity to weights.

### D — Evaluate the geographic gradient, then extend hourly coverage

Use existing sites first. Prepare a bounded registry of **up to 12 additional public evaluation coordinates** covering warm southern Florida, central/northern Florida, Georgia and the Carolinas. Choose multiple climate/elevation settings, not one point per latitude. Resolve exact coordinates, native cells and station/production evidence before acquisition. Reuse any already-cached hourly cells.

When execution is authorized, acquire only the missing **hourly temperature/dewpoint** needed by that registry for 2010–2025. Run the normal server resource preflight, manifest, checksum and retry limits. Reuse daily data; no global hourly cube, new weather provider, private keys or soil restart. This planning turn does not start those downloads.

**Gate:** compute every site's outputs under identical methods. Ask the supervisor for known management strategy, approximate recurring flowering/harvest periods and confidence/source—not a genotype list. Agreement with the R rules themselves is not independent validation.

### E — Put the production analysis at the top of the UI

Add three result sections above annual climate context: **Production-system hypothesis**, **Seasonal calendar**, **Stage-specific risks**. Keep *production strategy* (evergreen/semi/deciduous) distinct from *growing setup* (cover/root zone). Default the evaluated scope to open field + ground; other setup choices retain qualitative context only.

Display the profile, calendar convention, annual coverage and unmet-chill years. Expert controls change named assumptions and trigger a new analysis ID; reset restores the versioned default. Page and exports must consume the same immutable result. Show unsupported hourly/anchor states while keeping daily climate useful.

**Gate:** snapshot/report parity, stale-request protection, mobile/keyboard behavior, private access and no production label calculated only in browser code. Hosted new-coordinate support requires the already-planned authenticated archive bridge and durable jobs; the current hosted site has three snapshots only. Research packets can be evaluated before that connectivity work is complete.

### F — Scientific validation and later layers

Separate engineering parity, weather-source accuracy and biological validation. Freeze parameters on an initial site/year set; reserve geographic sites and later years before tuning (candidate temporal split: 2011–2020 development, 2021–2025 held out). Specify classification agreement, flowering/harvest date error, window overlap and failed-season rate before evaluation. Have the supervisor agree acceptable errors using actual observations; no acceptance threshold has yet been measured.

Use station evidence to quantify weather bias and event misses separately from calendar error. Compare the adapted model against the existing fixed-window baseline. Report parameter-sensitivity ranges as sensitivity, not calibrated confidence intervals. Add a second independent regional evaluation in Peru, Chile or Mexico before claiming transfer there. Unknown tropical/equatorial strategy must be able to abstain; latitude alone cannot validate a dormancy calendar.

Only after that baseline is useful: layer soil constraints, then parameterized tunnel/pot effects, then cultivar-specific models with approved data. Do not train ML to reproduce the heuristic risk score as if it were an observed outcome.

## 7. Minimum tests for the implementation

1. Threshold boundaries: −1, 0, 7.2°C; 100/150/300 h; ≤−2.2°C; ≥32/35°C; 1/10 mm.
2. North/south leap years, year-crossing stages, corrected summary anchor and full-window expected counts.
3. Zero-requirement missing anchor; unmet chill; GDD not met; truncated archive; missing/duplicate/out-of-order hours and days.
4. Positive-requirement R/Python parity; constant-temperature synthetic dates; inclusive stage endpoints and non-overlapping fruit window.
5. Flagged/missing rainfall, missing RH, missing radiation and invalid humidity do not become low risk; stateful chill never compresses gaps.
6. Establishment interval ordering; planting is not labelled a first-crop harvest forecast.
7. Flat/small/incomplete reference panel, missing target, target exclusion, frozen quantiles and weight sensitivity.
8. Reproducible result hashes, no private paths in responses, cancelled/duplicate requests, restart recovery and exact export snapshot identity.

Dynamic Model/Utah are optional comparison modules until their installed versions and hourly-increment/total behavior pass known-answer tests. The package documents `total=FALSE` as per-temperature outputs; never treat Chill Portions as chill hours. [ChillModels documentation](https://cran.r-project.org/web/packages/ChillModels/ChillModels.pdf)

## 8. Completed in this revision versus next work

**Completed:** transcript review; complete R parse and subsequently full sequential source read; data-field mapping; updated priorities; [full review](R_FULL_CODE_REVIEW.md); source-pinned `scripts/audit_paul_reference.R` expanded from eight to **22 passing characterization checks**. The current audit loads only 17 reviewed helper definitions from the unchanged local reference, inspects syntax and runs synthetic inputs. It does not source the monolith or establish biological accuracy. Wrong-source fingerprint refusal was also verified.

**Not completed:** extracted production R library, live R/API connection, corrected production-calendar module, new risk/classifier UI, expanded hourly acquisition or new deployment. The prior 55 backend tests were not rerun in this planning revision. Locally R 4.6.1 is available; dplyr/jsonlite are installed, lubridate/ChillModels are not. Server R dependencies have not been checked this turn.

**Immediate next implementation:** milestone A, followed by the Waldo packet in B. No new supervisor dataset or API key is required to start. Needed for scientific sign-off: confirmation of the default rule profile, how to anchor a genuine zero-chill/evergreen scenario, and independent site calendars/management labels. These do not prevent positive-chill adapter development.
