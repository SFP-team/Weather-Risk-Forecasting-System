# Full review of the supplied R workflow

2026-09-11. **Source review and bounded diagnostics; not a corrected workflow or scientific validation.**

## Scope and verdict

Read all **5,759 lines** of the local `blueberry_climate_analog_workflow.R` sequentially, including comments, superseded implementations, optional municipality context and the genotype tail. Traced the **332 parsed top-level expressions / 51 top-level function definitions** through their inputs and outputs. Source fingerprint: SHA-256 `5e8589db6b017e7e0b082639c6212df29a36da76a74b3a29e709979378c8ab55`; MD5 `6310a0da64316868fb465e86d85481d4`. All source line numbers below refer to that snapshot, not this document.

This is a substantial exploratory research workflow with useful building blocks. It is **not yet a reproducible, validated, arbitrary-coordinate recommendation engine**. Its strongest reusable part is the per-year chain from hourly chill to an assumed calendar to stage-specific weather exposure. Its final suitability/classification/ranking outputs should not be transferred into the app unchanged.

The original source remains unchanged and private. No whole-script execution, package installation, weather download, server job or deployment occurred. This review publishes descriptions, function identifiers and synthetic diagnostics, not supplied code blocks, transcripts, private site coordinates or breeding records. It does not establish which exact code/configuration generated the earlier HTML reports.

## 1. What the complete program does

| Section / lines | Executed role | Assessment |
|---|---|---|
| Preamble, 0–1 / 1–197 | Set a machine-specific working directory; install/load packages; configure assumptions, target and reference sites | A research-session setup, not a library or service entry point |
| 2 / 198–311 | Missing-value helpers, event runs, VPD, day length, month labels, risk scaling | Useful formulas; missingness and boundary semantics need hardening |
| 3 / 312–356 | Download US county boundaries and create a five-state 0.5° reference grid | Reference-domain construction, not global agronomic validation |
| 4 / 357–778 | Download WorldClim monthly rasters and derive hemisphere-aligned profiles and initial chill/freezing proxies | Screening features, with monthly approximations and mixed units that need explicit metadata |
| 4B / 779–1583 | Download hourly temperature for **all screening locations**, replace chill/freezing proxy columns | More acquisition than the later detailed-site shortlist suggests; must be bypassed for our adapter |
| 5 / 1584–3022 | Impute/standardize features, weight them, calculate four distance views and consensus similarity, rank sites/counties, plot | Useful exploratory analogue search; session-order defect and relative-score limitations |
| 6 / 3023–3354 | Infer evergreen/semi-evergreen/deciduous support and export evidence/maps | Rule-based hypothesis; happens too late for section 5 to use the newly calculated labels |
| 7 / 3355–3602 | Select eight county-distinct grid analogues and five UF sites plus target; heatmap/clustering | Target-dependent reference panel, unsuitable as a universal risk scale |
| 8 / 3603–3752 | Download/cache daily weather and hourly temperature for detailed sites | Separate cache from screening; not needed when adapting our archive |
| 9 / 3753–4030 | Per-year chill hours, Utah units, Chill Portions, threshold dates, GDD dates and stage exposures | Most useful science core; incomplete-window handling is unsafe |
| 10 / 4031–4115 | Summarize years and create planting/dormancy/flowering/harvest labels | Northern anchor error and unvalidated planting/calendar heuristics |
| 11 / 4116–4256 | Seven weighted risk components, total/class and dominant-risk plots | Mixture of empirical frequencies and relative indices, not a loss probability |
| 12 / 4257–5343 | Replace old centroid-style assessment with directional suitability and another system classifier | First-reference-row bug materially compromises scores; classification is inconsistent across outputs |
| 13 / 5344–5417 | Optionally import a precomputed municipality CSV and plot its leading 15 rows | Context imported from elsewhere; this script does not calculate that municipality dataset |
| 14 / 5418–5717 | Read external genotype predictions/preferences/metadata and combine ranking components | A ranking postprocessor, **not a fitted reaction-norm or cultivar model** |
| 15 / 5718–5759 | Export top analogues and a five-answer summary table | Production-system answer uses a hard-coded row position |

Intended dependency chain: location/data → features → production hypothesis/analogues → selected weather histories → yearly calendar/exposures → summaries → risk/suitability → optional genotype ranking → master answers. The actual ordering breaks that chain at production-system assignment, and different outputs subsequently use different classification rules.

## 2. Highest-priority confirmed defects

### A. Suitability uses one reference row instead of the population

**Source 4809 and 4814; reproduced with synthetic inputs.** Both all-reference and system-matched values select row 1 and one feature. Therefore the following means/quantiles are computed from one number, not the reference distribution.

- Lower-/higher-is-better scores collapse to binary comparisons.
- The reference-range score becomes 1 only at exact equality with that single value, otherwise 0.
- Reordering references can change suitability without changing any weather or membership.
- Feature-contribution means, percentage differences, envelope membership, component scores and the final class inherit the problem.
- The separate envelope CSV at 5326–5341 uses the full reference columns, so it need not agree with the feature-contribution table.

Synthetic example: target exposure 30, references 10/20/30/40. The full-population lower-is-better score is about 0.5833; selecting first row 10 yields 0; placing 40 first yields 1. Proposed correction: use complete named columns and test permutation invariance. **Not fixed in this review.**

### B. Analogue labels depend on session history

**Source 1604–1653 versus 3056 onward; syntax-order check passes.** Section 5 checks whether `system_assignment` already exists, and otherwise inserts missing classification fields. The current script only constructs that object later in section 6.

In a fresh session the categorical agreement penalty is disabled by missing labels. In an interactive rerun it can use an earlier target/configuration's assignment. Later construction does not recalculate previously generated analogue scores, rankings or plots. This is a hidden-state dependency, not merely a display problem. Proposed correction: explicit arguments and classification before its consumers; clean-session and changed-config regression tests.

### C. Northern summary dates are reconstructed 31 days early

**Source 3757–3771 versus 4034–4038; reproduced.** Northern offsets are measured from November 1 but displayed relative to October 1. The per-year dates and median calendar labels therefore disagree. Southern anchors match. Proposed correction: one authoritative season anchor used for offsets and reconstruction, with leap/cross-year tests. Do not shift weather timestamps to repair this summary error.

### D. An incomplete year has a different output schema

**Source 3817–3825 versus 3931–3979 and 4041–4042; source/synthetic check passes.** The early return omits `point_type` and metric fields. When mixed with successful years, row binding creates missing `point_type` values; grouping by that field splits one location into separate valid/incomplete summary rows. If every year fails, later grouping/metric columns can be absent altogether. Proposed correction: a fixed typed row schema for every site-year, explicit status/reasons, and one location identity regardless of completeness.

### E. Missing weather can become apparently safe exposure or a misleading class

**Source 238–249, 295–300, 3817–3881, 3920–3978, 4146–4151 and 4220–4234.**

- Only 720 rows are required for an approximately six-month winter. Row count is not complete, unique hourly coverage.
- Nonfinite hourly temperatures are removed before stateful chill calculations and freeze-event counting; missing time is compressed and events can be joined across gaps.
- Missing GDD is replaced by zero. Missing rain/temperature inside a nonempty stage can sum to zero; all-missing flowering Tmin can yield “no freeze”.
- Missing dry flags break runs; entirely absent dates are not inserted, so adjacency need not mean consecutive days.
- Degenerate risk reference ranges produce 0.5 even for a missing target.
- Missing total risk falls through to “Very high”; missing/degenerate deviation can be labelled “Typical”. Missing directional effects can also fall through to “Neutral” or “Transitional”.

The synthetic audit reproduces the scalar missing-data behaviors; no claim is made about their frequency in prior report inputs. Proposed correction: expected timestamps, variable-specific coverage, complete-window policies and explicit unavailable states before classification. Preserve our existing suspect-rain refusal.

### F. Genotype metadata references an undefined production-system variable

**Source 5651; active assignment inventory checked.** `target_system` is used in the metadata branch, but its only assignment in the supplied file is commented out at 3313. A fresh run reaching this branch without an externally supplied object cannot resolve it; an interactive session could supply a stale value. The later `target_system_detailed` is a different variable. This defect is conditional on entering the optional genotype metadata branch; it does **not** imply that the weather-only path always fails here.

### G. Master answer chooses the 32nd system row

**Source 5744; syntax check passes.** `production_system_result` contains all locations sorted by system/chill, yet the master answer chooses row 32 instead of filtering the target key. That position is not guaranteed to be the target and can change with the grid, input sites or sorting. The directional-suitability result separately uses the detailed target classifier. Proposed correction: key-based, exactly-one-row lookup and cross-output identity tests.

## 3. Scientific interpretation and modelling limitations

These are distinct from coding defects. Correct execution alone cannot validate the assumptions.

### Climate sources, seasons and feature meaning

- WorldClim monthly profiles and requested 2001–2025 POWER histories are different source/temporal products. Compare periods and units explicitly; do not imply all predictors were measured over one common baseline.
- Monthly temperature scaling uses a data-magnitude heuristic rather than authoritative units (section 4). Monthly GDD from a mean temperature is not the same computation as summing daily positive heat increments. Monthly sinusoidal chill/freezing estimates are approximations, not observed hourly records.
- Section 4B replaces the old proxy columns outright, including on failed acquisition; there is no reliable automatic WorldClim fallback. Names ending in `_proxy` are retained, but “annual” chill/freezing now means a **six-month chill-season mean**, not all 12 months. Monthly climatologies and crop-season summaries also cover differently aligned years.
- The executed chill rule counts finite temperatures **below 7.2°C, including freezing**, and excludes exactly 7.2°C. Comments and an unused local minimum suggest a different bounded rule. Maintain separate named methods, not an undocumented correction.
- Northern windows are November–April; southern windows April–September in the previous R-labelled crop year. A separate crop-year helper switches northern years in October. Actual dates, not the label alone, are required to reconcile results.
- Both POWER downloaders request LST and construct UTC-labelled timestamps. This is a metadata/time-basis mismatch; it does not by itself quantify a numeric bias. Our archive is UTC, so comparisons must identify that difference. [NASA hourly API time standards](https://power.larc.nasa.gov/docs/services/api/temporal/hourly/)

### Production-system inference is provisional and inconsistent

The broad classifier combines chill with winter minimum/mean temperature and freezing criteria. The detailed classifier uses only mean chill: below 100, 100–below 300, or at least 300 hours. Only the target is overwritten by the detailed rule in the suitability dataset; reference labels remain broad-rule labels. System matching therefore compares labels generated by different criteria.

The broad-rule missingness guard omits a freezing-month input used in its predicate; some unknown cases can fall through to semi-evergreen. Its “High/Moderate confidence” labels are rule labels, not measured accuracy or calibrated uncertainty. Grouping sites by these same rules and reporting their climate means is descriptive evidence, not independent validation.

There is also partial circularity: classifying a target by its own chill and then scoring chill against that assigned class produces a full chill-hours alignment score throughout 0–800 hours under these functions. The audit checks representative boundaries. That score cannot independently establish crop suitability. Other components and the separate 50-hour fulfilment test can still penalize the site, so this does not mean the **entire** suitability result is always favourable.

### Calendar is an assumed recurring-season scenario

The active chain uses 50 chill hours by default, then 150 **°C-days above 7°C**, flowering at budbreak +14 to +35 days, and harvest at flowering **start** +70 to +110 days. Chill Portions/Utah are also calculated, but the active calendar uses chill hours, not the portions fulfilment date.

The package author's documentation describes Dynamic Model `total=FALSE` outputs per temperature; summing them is therefore not, on that evidence, an identified double-cumulation bug. Installed-version known-answer tests remain necessary before integrating this optional model. No ChillModels package execution occurred in this audit. [ChillModels author documentation](https://rpertille.github.io/ChillModels/reference/dynamic_model.html)

The 450-day daily slice is not checked for complete coverage or guaranteed to include all derived stages. A no-frost year returns no frost-free duration when either seasonal endpoint is absent; distinguish “no event observed with complete data” from missing data. Per-year and per-metric denominators are essential: flowering risk among years with a modelled flowering window is not unconditional annual failure risk.

Zero chill triggers the first available date and does not implement an independently validated evergreen calendar. The planting rule starts 30 days after the chill anchor and clamps its end to at least day 60; for early budbreak it can extend beyond budbreak. It does not optimize planting dates or distinguish establishment of a young plant from the calendar of a bearing plant. Both issues already have characterization checks.

### Analogue similarity is relative, not probability of success

Good design choices include reference-only imputation/scaling, removing nonvarying features, square-root weighting before Euclidean distance, exporting feature weights and retaining multiple distance views. However:

- Missing target features are imputed with reference medians, potentially making unknown conditions look ordinary. Require minimum critical-feature availability and expose imputation.
- Monthly and derived summaries repeatedly encode related temperature/chill/freezing information. The weights are expert assumptions, not fitted effect sizes. Multiple correlated distance methods do not establish independent predictive validation.
- The kernel bandwidth is the median positive distance for the **current query**. Multiplying every distance by 100 gives identical similarity values (reproduced). Values cannot be read as absolute agronomic compatibility or compared across queries without a fixed calibration.
- PCA retention aims at 90% variance but also caps retained dimensions at 20; report achieved variance, not an unconditional 90% guarantee.
- Counties rank by their best grid point; that is not average county suitability. County/grid resolution and shared POWER source cells limit effective spatial precision. Rounding selected coordinates to 0.001° does not deduplicate native weather cells.
- Optional UMAP/heatmaps are exploratory visualizations, not additional independent evidence of performance.

### Risk and directional suitability need explicit semantics

The seven risk components are insufficient chill, flowering freeze, fruit-stage heat, harvest rain, longest dry spell, disease-favourable weather and variability. Radiation is an input/exposure and later suitability component, not a separate calibrated risk probability here.

Chill failure and flowering freeze are historical frequencies; other components use reference percentile scaling. The weighted total mixes those meanings and assigns unvalidated class cutoffs. The detailed reference panel is selected as closest to the target, so adding/changing a query can change the denominator. Freeze a comparison panel if scores must be comparable. Quantile type 8 is used in risk/envelope helpers and type 7 in directional helpers; preserve/version conventions.

The “dominant risk” is the largest raw component index, not necessarily the largest weighted contribution to total risk. The disease rule uses daily temperature/RH/rain thresholds; it is not measured disease incidence or hourly leaf wetness. Longest dry spell is not a soil-water-balance drought calculation. Daily VPD requires humidity as well as temperature; it is not a heat-only quantity.

Directional suitability treats lower rain/dry spell as favourable and higher GDD/radiation as favourable up to a score plateau. These are modelling choices, not universal monotonic crop responses. Missing feature scores are dropped and the remaining weights renormalized; a high total can then be based on a different evidence set. Show coverage and withhold unsupported conclusions rather than letting missingness silently redefine the score.

### Genotype ranking is a later, separate project layer

The code reads predicted trait values, standard errors, preferences and optional genotype metadata from CSVs. It **does not fit** a reaction-norm, genomic, G×E or yield model. Without supplied predictions it writes templates and skips ranking.

- It checks only a subset of the prediction schema. Preference directions, positive finite weights, unique genotype/trait/environment keys, sensitivity bounds and metadata completeness need validation.
- A regex chooses target environments; several matching environments/duplicate rows can enter the target calculation without an explicit aggregation policy. Missing traits are effectively reweighted through weighted means.
- Missing SE is replaced by within-trait median, then zero if all are missing; missing standardized/rescaled scores can become neutral values. These fallbacks are not evidence of precision.
- Across-environment raw trait SDs are combined without a demonstrated common unit scale; this is not validated yield stability or environmental responsiveness.
- Climate fit defaults to 100 without a metadata file, but to 70 for a missing genotype after a metadata join. Those are arbitrary defaults, not observations. Duplicate metadata can multiply rows.
- The 55/20/15/10 performance/stability/climate-fit/data-support weights are hand-set. The final positive environmental-support multiplier is common to every genotype and cannot change their order; the synthetic test confirms that algebra. Genotype-specific metadata **can** affect ranking, so the whole climate adjustment is not necessarily constant.
- The closest reference site is used as support without checking that it belongs to the actual training environments for every prediction. Do not present this as calibrated extrapolation confidence.

Soil acidity/drainage, irrigation water, tunnels, pots, management costs and experimentally validated cultivar responses are explicitly outside the implemented weather workflow. Nothing in these functions quantifies tunnel/pot risk reduction. The original preamble itself acknowledges important climate-only and phenology limitations.

## 4. Reproducibility and operating boundaries

- Hard-coded working directory and automatic unpinned package installation make `source()` an unsafe integration entry point. Setup/downloads/maps/report writes are top-level side effects; `set.seed()` does not pin data or dependencies.
- Target name/coordinates are partly configurable but ID, hemisphere, labels and lookups remain hard-coded throughout. Changing latitude/longitude alone does not produce a reliable arbitrary-coordinate run.
- Cache identities use site ID/year chunks without a full coordinate/parameter/time-standard/version signature. A changed site configuration can reuse stale data. Cache reads lack comprehensive schema/coverage/checksum validation and writes are not atomic; request failures warn/continue without our bounded retry/manifest discipline.
- Two independent hourly caches can duplicate requests. Section 4B loops over all screening points before the detailed shortlist; do not inadvertently launch that acquisition by trying to reuse a helper.
- The detailed chunk builder expands requested dates to calendar-year boundaries, unlike the screening chunk builder's bounded dates. The default full-year configuration masks that difference.
- Source metadata often describes the requested history/provider without proving all requested periods arrived. Persist actual coverage and per-variable provenance, not just configuration strings.
- Superseded blocks remain commented out (old cluster classifier, old heatmap/clustering, old centroid suitability). `softmax_negative_distance()` and `annual_chill_requirement_curve()` have no active call sites in this snapshot. The exported chill curve comes from `site_year_metrics`, not the latter helper. Comments must not be mistaken for executed logic.

## 5. What to reuse and the next implementation order

Keep the existing archive, QC pipeline, dashboard and Python scenario comparisons. Follow [R adaptation plan](R_ADAPTATION_PLAN.md), with these additional gates:

1. **Extract a network-free core, with no hidden session variables.** Version inputs, assumptions and output schemas. Separately review any extracted source for publication/attribution; do not commit the private monolith.
2. **Fix time, identity and missingness before scoring.** One anchor convention; keyed target lookups; fixed site-year schema; complete expected timestamps; explicit unmet-chill/unavailable statuses; no invented zero-risk results.
3. **Deliver the Waldo open-field/ground packet**, then Citra/Papanduva: both named production hypotheses, per-year assumed calendar, raw stage exposures, valid-year counts and sensitivity. Use existing weather; no new API or cultivar dataset is needed to start.
4. **Evaluate against independent observations.** Ask for known management strategy and approximate flowering/harvest periods at a few sites, plus the intended default chill/forcing assumptions. Agreement with the source code is engineering parity, not biological accuracy.
5. **Only then add optional analogue/suitability comparison.** Correct whole-column reference selection, freeze the reference registry/calibration, unify classification provenance, test row-order and target-insertion invariance, and report uncertainty/coverage. Do not hold the raw calendar/risk packet hostage to these later composite scores.
6. **Leave genotype and management-effect models deferred.** They need approved external data and separate validation. The supplied ranking template is useful interface guidance, not the missing trained model.

For the app, evergreen/semi-evergreen/deciduous is a **production-strategy hypothesis**; open field/tunnel and ground/pots are **growing-setup choices**. Preserve that distinction.

## 6. Verification actually performed

`Rscript --vanilla scripts/audit_paul_reference.R` passed **22 source-pinned characterization checks** locally under R 4.6.1. The audit parses the complete file, evaluates only **17 reviewed helper declarations** in an isolated environment and examines the syntax tree without evaluating workflow pipelines. Additional embedded-rule tests use tiny synthetic scalar/table inputs. Base/recommended R and the already installed dplyr namespace suffice; no new dependency was installed.

Checks cover parse counts; chill boundaries; north/south anchors; zero requirement; degenerate risk scaling; missing dry flags; VPD humidity dependence; planting ordering; query-distance rescaling; both first-row selectors; binary/order-sensitive directional scores; classification ordering; undefined genotype variable; positional master lookup; incomplete-year schema/group splitting; missing exposure/class fallthrough; self-classified chill alignment; neutral missing genotype scores; and invariance of ranking under a common multiplier.

The wrong-source fingerprint negative control also exited with the intended refusal before loading helpers. The prior **55-test server suite was not rerun**: this request changed only audit code/documentation, not production analysis. These passing tests deliberately reproduce several defects; they do **not** say the source is correct. Full end-to-end execution, numerical parity with the supplied HTML and scientific validation remain unperformed.

## Appendix: complete top-level function inventory

Grouped below for navigation; ranges are from R's parsed source references. Nested closures in feature/scenario/ranking functions were also read but are not included in the count of 51 top-level definitions.

| Group | Functions and source lines |
|---|---|
| General data helpers | `safe_file_name` 201–207; `replace_power_fill` 209–214; `safe_cv` 216–221; `safe_mean` 223–226; `safe_sd` 228–231; `safe_quantile` 233–236 |
| Events and atmosphere | `max_consecutive_true` 238–243; `count_continuous_events` 245–249; `saturation_vapor_pressure` 251–253; `vpd_from_t_rh` 255–258; `daylength_hours` 260–266 |
| Calendar labels / scaling | `month_midpoint_doy` 268–270; `calendar_months_for_biological_year` 272–274; `month_day_label` 276–278; `month_window_label` 280–293; `scale_high_risk` 295–300; `softmax_negative_distance` 302–309 |
| WorldClim | `hours_in_temperature_band` 375–402; `get_worldclim_raster` 404–417; `extract_worldclim` 432–452; `build_biological_features` 457–773 |
| Hourly screening definitions | `is_chill_hour` 798–801; `is_optimal_chill_hour` 803–807; `is_freezing_hour` 809–812; `calendar_to_biological_month` 819–828; `screen_chill_window_dates` 831–866 |
| Hourly screening acquisition / features | `split_screen_hourly_chunks` 869–913; `normalise_screen_hourly_datetime` 915–974; `get_screen_hourly_cached` 990–1105; `sum_or_na` 1107–1116; `calculate_screen_hourly_chill_features` 1146–1500 |
| Analogue distances | `distance_to_target` 2073–2089; `safe_kernel_similarity` 2091–2110 |
| Detailed acquisition | `normalise_power_datetime` 3606–3639; `split_year_chunks` 3641–3651; `get_power_cached` 3653–3713 |
| Chill / annual calculation | `chill_window_dates` 3757–3771; `crop_year_from_date` 3773–3781; `first_date_reaching` 3783–3787; `annual_chill_requirement_curve` 3789–3807; `calculate_one_site_year` 3809–3980; `median_offset_date` 4034–4038 |
| Directional suitability | `classify_detailed_production_system` 4337–4344; `safe_quantile_value` 4354–4370; `score_lower_is_better` 4372–4411; `score_higher_is_better` 4413–4452; `score_reference_range` 4454–4511; `score_system_chill` 4516–4603 |
| Genotype postprocessing | `write_genotype_templates` 5421–5461; `rescale_safe` 5469–5479; `risk_adjusted_genotype_ranking` 5481–5713 |
