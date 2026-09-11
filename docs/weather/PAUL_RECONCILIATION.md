# Reconciliation with Paul's workflow

Date: 2026-09-08. Scope: source-code/report audit and controlled chill sensitivity on our stored NASA UTC data. **Not a rerun of the complete R workflow, not a reproduced historical report, and not a calibrated phenology model.** No new weather was downloaded. Original report files and R source remain local; only the analysis and derived summaries are published.

2026-09-11 follow-up: new supervisor discussion and a complete R parse informed `R_ADAPTATION_PLAN.md`. Eight local characterization checks now reproduce the northern calendar-anchor mismatch (October summary versus November calculation, −31 days), zero-chill first-date behavior, missing/constant-reference fallback, missing dry-flag behavior and other reviewed assumptions. Run `Rscript --vanilla scripts/audit_paul_reference.R` from repository root with the unchanged private R file present. These tests establish source behavior, not successful biological validation or corrected production modules. The full R workflow was not executed.

## Executive finding

Our initial climate report and Paul's reports do not calculate the same quantities under the same assumptions. Some discrepancies are now explained by actual executable code, rather than guesses. On identical data, changing the season and chill definition raises Papanduva's mean from 178.9 to 199.4 hours. Paul's report states 209.4 hours. The remaining 10.0-hour numerical difference is **unresolved**, not attributed conclusively to any one cause.

Do not compare our median of 168 hours directly with his mean of 209.4 hours. Our corresponding mean is 178.9 hours. Also do not equate 368 WorldClim proxy hours, hourly chill counts and 30 Dynamic Model Chill Portions.

## Controlled numerical comparison

Each column uses exactly the same stored UTC series and 15 aligned winters. Only window and threshold change. All values are arithmetic mean hours, rounded to one decimal.

| Site | Demo window, 0 ≤ T ≤ 7.2 | Demo window, T < 7.2 | Paul window, 0 ≤ T ≤ 7.2 | Paul window, T < 7.2 |
|---|---:|---:|---:|---:|
| Papanduva | 178.9 | 185.0 | 193.3 | 199.4 |
| Citra | 292.7 | 318.9 | 322.9 | 349.5 |
| Waldo | 342.2 | 380.5 | 381.2 | 420.3 |

Papanduva: widening the window adds 14.4 bounded hours; changing the definition on that long window adds 6.1 hours. Both effects together add 20.5 hours. This is a controlled sensitivity decomposition, **not proof that these factors explain the historical report difference in the same proportions**.

Demo windows: Florida Nov–Feb ending in the labelled year; Brazil May–Aug of the labelled year. Paul windows: Florida Nov–Apr; Brazil Apr–Sep. For Brazil we align actual winter dates, so our 2011–2025 winters map to Paul's crop labels 2012–2026. We do not claim Paul ran those labels. Full annual outputs: `method_reconciliation.json`.

## Audited mismatches

Line references below refer to the locally supplied `blueberry_climate_analog_workflow.R`, SHA-256 `5e8589db6b017e7e0b082639c6212df29a36da76a74b3a29e709979378c8ab55`. They are source snapshot identifiers, not links to a published R file.

| Item | Supplied executable R / reports | Our implementation | Consequence |
|---|---|---|---|
| Baseline | Config lines 77–80: daily/hourly 2001–2025; common crop years at 3982: 2002–2025 | Daily baseline 2011–2025 plus 2010 buffer | Different samples. The technical HTML instead describes daily starting 1991: report/code version mismatch. |
| Chill threshold | `is_chill_hour`, line 798: finite T <7.2, no lower bound | Inclusive 0 ≤ T ≤7.2 | Freezing hours count only in Paul's definition; exact 7.2 hours count only in ours. Comments describing a bounded band do not override executed code. |
| Chill window | `chill_window_dates`, 3757: south Apr–Sep of prior crop year; north Nov–Apr | South May–Aug; north Nov–Feb | Longer windows and different southern year labels. |
| Time | `get_power_cached`, 3680 onward: requests `LST`; `normalise_power_datetime`, 3606, assigns returned hour fields a UTC timezone without an explicit solar-to-UTC conversion | Verified UTC product | Relabeling LST fields as UTC does not convert their time meaning. Exact request/cached response metadata must be checked before judging date alignment. |
| Aggregation | Report: 209.4 mean hours | Demo headline: 168 median hours at Papanduva; mean 178.9 | Statistic mismatch in addition to method differences. |
| Chill gate | Config 88: 50 h; HTML narrative: 100-hour benchmark met in 22/24 years | No cultivar requirement imposed | 100 h can be a separate fulfillment-curve benchmark, but cannot establish the phenology trigger used to produce that report. |
| Dynamic Model | Calls `ChillModels::dynamic_model` on finite temperatures (3843) | Not implemented | Chill Portions are a distinct model/unit; no conversion from chill hours is valid here. |
| Missing weather | Detailed path accepts ≥720 rows then drops nonfinite temperatures before model calls; sums use `na.rm`; screening path has a separate 95% monthly rule (1241) | Complete expected windows required | Detailed stateful models can concatenate across gaps; partial stage sums can appear valid. Retain our stricter gap checks. |
| Dry spell | `production_max_dry_spell`, 3973: chill start through modelled harvest end | Within calendar year | Our 33-day maximum over years is not comparable with a mean modelled production-window dry spell around 19 days. Same <1 mm dry-day threshold, different interval/statistic. |
| Rain | `harvest_rain_mm`, 3969: sum within modelled harvest | Annual/monthly summaries | Annual ~1,447 mm must not be compared as if it were harvest rain of 206.1 or 173.6 mm. |
| Cold | Flower freeze: any Tmin ≤−2.2°C during modelled flowering (3961); general frost threshold ≤0°C | Annual Tmin <0°C counts | Different threshold, stage, units and denominator. A year-level probability is not a daily count. |
| Heat | Fruit-stage ≥32°C, severe ≥35°C | Annual ≥35°C | Only severe threshold matches, not the window. |
| Risk score | Reference p10–p90 clipped scaling (`scale_high_risk`, 295), weighted indices | No composite score | Must reconstruct exact reference membership and configuration before comparison. |
| Production system | Detailed classifier (4337): <100 evergreen, <300 semi, otherwise deciduous; broad classifier at 3041 also uses winter rules and 150 boundary | Not classified | Distinct classifiers within one script; confirm which output/report is authoritative. |

## Phenology chain that controls Paul's risk windows

The supplied configuration drives the following hypothetical chain:

1. Reach 50 hours under its below-7.2°C rule (not the 100-hour narrative benchmark).
2. Starting on that fulfillment date, accumulate max(Tmean−7°C, 0) daily until 150 GDD; this is modelled budbreak.
3. Flowering: budbreak +14 through +35 days.
4. Harvest: flowering **start** +70 through +110 days, inclusive.
5. Sum rain within harvest, evaluate freeze within flowering and dry spells from chill-window start through harvest end.

These are configuration assumptions, not cultivar-independent biological truths. A changed chill trigger can shift every later weather window and therefore change rain/freeze scores even on identical weather. The difference between 206.1 and 173.6 harvest mm is not yet causally explained: no matching per-year outputs/configuration snapshots were supplied for both HTML versions.

## Report provenance warnings

- Original and revised diagnose reports both state 209.4 mean hourly chill and 30 portions, with 22/24 years satisfying a 100-hour benchmark.
- The original narrative simultaneously mentions 2021–2025 and 24 years; five calendar years cannot contain 24 annual observations. Confirm the intended period.
- Revised report uses a 368-hour WorldClim proxy for deciduous classification while retaining 209.4 hourly chill in the narrative. These products must remain separately labelled.
- The supplied R includes later replacement of screening chill proxies by hourly-derived features while retaining proxy-style column names (1449 onward). Column names alone cannot identify source provenance.
- The technical report describes daily data from 1991 and hourly data from 2001, whereas this script starts both in 2001. We cannot assume this exact source snapshot generated all four HTML reports.

## What can be reused safely?

Reuse the explicit event/window structure, dry-day threshold, degree-day arithmetic, stage-wise summaries and reference-relative comparison pattern, with unit and boundary tests. Preserve our separate provenance, complete-window checks and suspect-rain handling. Retain Paul-style settings as a named **exploratory scenario**, not an approved production calendar.

Do not yet reproduce Dynamic Model results, classifier labels, weighted risk scores or genotype outputs as validated results. We have not run the R script or verified its package versions, cached input revisions or historical model artifacts.

## Three questions for Paul

1. Which script/configuration and cached inputs generated each diagnose HTML? Please include per-year metric outputs and package versions if available.
2. Which chill definition/window is intended for this phase: below-only or bounded; six-month or four-month; hours or Dynamic Model portions? What time standard should the inputs use?
3. Is the phenology trigger 50 or 100 hours, and are 150 GDD plus the fixed offsets approved only as an exploratory reference scenario?

No cultivar list is required for this clarification. These are methods questions for Parts 1–2.

## Reproduce and verify

Deploy `pipelines/weather/reconcile_methods.py` to server `code/`, then from the project root:

```sh
env/bin/python code/reconcile_methods.py
```

Output: `reports/method_reconciliation.json`. Controlled experiment: three sites ×15 winters ×four definitions/windows. Full expected-hour coverage is required. The decomposition identity is checked for all 45 site-winters. Three additional known-answer tests cover freezing and exact-upper-boundary behavior. Full server test result is recorded in the progress log.
