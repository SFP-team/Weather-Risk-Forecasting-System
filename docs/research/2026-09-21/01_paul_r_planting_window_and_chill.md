<!-- Research scout report (PaulPlantingR), generated 2026-09-21 for the future plan. Read-only literature/code research; claims marked [unverified] are not confirmed. -->

## 1. Findings (R line ranges cited; file is 1,802 lines in the working tree)

### 1.1 Non-goal sections in one paragraph
§1–§7 build a WorldClim-normals municipality screen for PR/SC/RS, phase-align months (Florida Nov = Brazil Jun = phase 1, lines 67, 290–291), compute a weighted climate distance to Citra/Waldo/Central Florida (weights lines 95–111), and project with PCA/UMAP; §8 downloads NASA POWER daily (1991–) and hourly T2M (2001–, LST, line 730) for the top 60/25 municipalities plus references; §13, §14, §16 are maps/plots. None of this feeds the coordinate-level product except the choice of sites.

### 1.2 Planting window derivation (§11)
- Inputs: per-year `chill_fulfillment_date` from §10 (line 1088–1090) and daily `gdd` (line 928, `(tmin+tmax)/2 − 7`, floored at 0).
- Budbreak: first date in `[fulfilment, fulfilment+220 d]` where cumulative GDD (NA→0, line 1182) ≥ 150 (lines 1176–1188). No budbreak → whole season NA (1192–1211).
- Flowering = budbreak +14 .. +35; harvest = flowering_start +70 .. +110 (1214–1217).
- **Planting: `planting_end = budbreak − 30`, `planting_start = planting_end − 75`** (lines 1219–1220; constants 91–92, commented "Preliminary … offsets", no source). So planting is a fixed 75-day block ending 30 days before modelled budbreak; it is chained to chill only through budbreak, and to flowering/harvest only through the same budbreak date. Nothing in the window uses weather during planting.
- Site calendar: `median_month_day` (1275–1291) drops NAs, re-anchors month-day to year 2000 if month ≥ 4 else 2001, takes the numeric median, returns "MM-DD". It is applied **separately** to planting_start, planting_end, budbreak, flowering_*, harvest_* (1296–1303). §15 `month_day_to_anchor` (1642–1651) re-applies the same ≥ April rule before drawing `geom_segment(start→end)` (1679–1687).
- **Why some sites show multiple/odd planting windows [INFERENCE from code, not from a run]:** in the south, chill years are calendar years with May–Aug chill (1099, 1105). With 100 h the fulfilment date ranges from mid-May (cold sites) to August (warm) and budbreak from ~June to ~September, so `planting_start` (= budbreak − 105) falls in **late Feb–May**, straddling the 1 April anchor. Years with March starts anchor to 2001, years with April/May starts to 2000; the median of a bimodal 2000/2001 set can land anywhere, and `planting_end_md` is medianed independently. Result: start after end, or a start month-day that §15 maps to 2001-03 while the end maps to 2000-05, so the segment is drawn backwards across ~10 months and overlaps flowering and harvest — visually a second window. Same failure mode exists for budbreak/flowering in warm years but is rarer because those stay after April. Chill-fulfilment years that are NA are silently excluded from medians (1276), so the planting median can rest on 3–4 years at marginal sites while flowering rests on the same subset — consistent internally, but hides the sample size.
- A **single window aligned with flowering and harvest** requires: (a) computing one central budbreak (median offset from a fixed season anchor, not month-day medians), (b) deriving planting, flowering and harvest from that one date with the fixed offsets, and (c) reporting the year-to-year spread (p10–p90 of budbreak) as the uncertainty rather than as separate medians. production.py `calendar()` (lines 383–394) already does (a)–(c) for chill…harvest; it lacks the planting offsets.

### 1.3 Chill implementations (§10, lines 1050–1145)
- Data: hourly T2M, `time_standard = "LST"` (730), 2001–2025 (70–71). NAs removed before any model (1064–1067), so gaps are compressed, not flagged; a year needs only **24 valid hours** to produce numbers (1069).
- Window: south → months 5–8 of the calendar year; north → Nov–Feb, Nov/Dec assigned to next year (1094–1109). Four months, not our six.
- Chill hours: `sum(temp <= 7.2)` (1083), no lower bound, inclusive.
- Fulfilment: first hour where `cumsum(temp <= 7.2) ≥ chill_requirement_hours` (100, line 76) → its date (1078–1079, 1088–1090).
- Utah: `ChillModels::utah_model(temp, total=TRUE)` (1084). Package weights: (1.4,2.4]→0.5, (2.4,9.1]→1, (9.1,12.4]→0.5, (12.4,15.9]→0, (15.9,18]→−0.5, >18→−1 (Richardson 1974; https://rdrr.io/cran/ChillModels/man/utah_model.html).
- Dynamic Model: `ChillModels::dynamic_model(temp, total=TRUE)` (1085). Source (https://rdrr.io/cran/ChillModels/src/R/dynamic_model.R) uses E0 4153.5, E1 12888.8, A0 139500, A1 2.567e18, slope 1.6, Tf 277 K, TK = T + 273 — **identical constants to chillR `Dynamic_Model`** (https://github.com/cran/chillR/blob/master/R/temp_models.R) and Fishman/Erez 1987. Indexing differs by one hour from current chillR (ChillModels uses `xs[l]`, `ak1[l]`, `xi[l-1]`; chillR uses `[l-1]`, `[l-2]`); totals differ negligibly. Our `chill_comparison.py::chill_portions` reproduces the ChillModels form. Neither CP nor Utah drives phenology or risk; only `chill_portions_mean`/`utah_units_mean` are summarised (1125–1126) and mapped.
- Freeze: `freeze_hours = sum(temp ≤ 0)`; `freeze_events` counts run starts, a new run also when the hourly gap exceeds 1.5 h (1052–1060).
- Summary (1117–1132): mean/sd/CV/p10/p90 of hours; `insufficient_chill_probability = mean(chill_hours < 100)`; `chill_fulfillment_probability`.

### 1.4 Constants and thresholds: R vs `legacy_paul_v1` (production.py lines 24–51)
| Item | R (line) | legacy_paul_v1 | Diff |
|---|---|---|---|
| Chill test | T ≤ 7.2, no lower bound (1083) | T < 7.2 | boundary only |
| Chill window S | May–Aug, calendar year (1105) | 1 Apr–1 Oct | **6 vs 4 months** |
| Chill window N | Nov–Feb, year+1 (1100–1106) | 1 Nov–1 May | **6 vs 4** |
| Requirement | 100 h (76) | 50 h | **2×** |
| Min data | ≥24 valid hours, NAs dropped (1064–1069) | complete window | R lax |
| Time standard | LST (730) | UTC | edge hours |
| Hourly years | 2001–2025 | 2011–2025 | |
| Daily GDD | ((tmin+tmax)/2 − 7)+ (928) | tmean_c − 7 | **different input** |
| GDD trigger | 150 (77) | 150 | = |
| GDD horizon | fulfilment + 220 d (1178) | season start + 450 d | |
| GDD NA | zero-filled (1182) | fail (`incomplete_gdd`) | |
| Flower offsets | 14 / 35 (87–88) | 14 / 35 | = |
| Harvest offsets | 70 / 110 from flowering start (89–90) | same | = |
| Fruit window | flowering_start..harvest_end (1224–1225) | flowering_end+1..harvest_start−1 | **R counts bloom+harvest heat** |
| Dry-spell window | budbreak..harvest_end (1228–1229) | season start..harvest_end | |
| Planting | budbreak−105..budbreak−30 (91–92, 1219–1220) | none | **missing** |
| Frost / flower freeze | 0 / −2.2 (81–82) | 0 / −2.2 | = |
| Heat / severe | 32 / 35 (79–80) | 32 / 35 | = |
| Heavy rain, dry day | ≥10 mm, <1 mm (83–84) | same | = |
| Disease day | RH≥85 & 15≤tmean≤28 & rain **>** 0.1 (937) | rain ≥ 0.1 | boundary |
| tmean | coalesce(T2M, (min+max)/2) (917) | tmean_c | ~= |
| Flower freeze | any(tmin ≤ −2.2) per year (1242) | days ≥1 per year | = |
| Freeze events | run starts, gap>1.5 h splits (1052–1060) | contiguous runs | ~= |
| Crop year (daily) | Jul–Jun (940) vs chill year = calendar (1099) | winter_year | R inconsistent |
| Risk score §12 | normalisers: heat days/20, harvest rain mm/250, dry spell/21, disease days/30, chill CV/0.30, precip CV/0.25; weights .25/.20/.15/.15/.10/.10/.05; Low<25, Moderate<50; final = 0.7 similarity + 0.3(100−risk) (1361–1400) | frequency of winters with event + Wilson CI, no weights | **different paradigm** |
| System classifier | none in this file | 100/300 h + multi-feature | R dropped it |

### 1.5 Defects / fragile logic
1. Month-day medians with a 1-April wrap (1275–1291, 1642–1651): reversed/phantom planting windows (§1.2); medians of endpoints are not a window.
2. NA compression before Utah/Dynamic Model (1064–1067): stateful models concatenate across gaps; 24 valid hours suffice for a "year" (1069).
3. `chill_year` = calendar year in the south but daily `crop_year_south` = Jul–Jun (940): §12 joins chill and frost/daily metrics by unit only, so per-year alignment is never checked.
4. GDD NA→0 (1182) delays budbreak silently; 220-day cap then yields NA seasons that vanish from all medians and probabilities except `insufficient_chill_probability`.
5. `risk_disease_weather` uses **harvest** disease days only (1366); flowering disease days computed (1245) but unused in the score.
6. Fruit window includes flowering and harvest (1224), double-counting heat with flower and harvest windows.
7. Freeze-event gap logic uses `datetime` after NA filtering; `time_gap` recomputed on the filtered vector, so a removed NA hour creates an artificial event boundary.
8. Northern units: chill computed (1100–1106) but §11 filters `hemisphere == "south"` (1255–1256); no northern phenology, so the north-window rule is untested in this file.
9. Weights and normalisers in §12 are declared heuristic (1373) and mix probabilities with scaled means.
10. `median_month_day` returns a string; the CSV loses year and the sample size per stage.

## 2. Recommendations (production.py)
1. **New profile `paul_analogs_v2`** in `PROFILES`: `chill_requirement_hours: 100`, `chill_definition: 'at_or_below_7_2'`, `chill_window: 'four_month'` (May–Aug / Nov–Feb; add a `window()` variant keyed by profile), `gdd_input: 'tmin_tmax_mean'`, `gdd_horizon_from: 'chill_date', horizon_days: 220`, `fruit_window: 'flowering_start_to_harvest_end'`, `dry_spell_from: 'budbreak'`, `planting_end_before_budbreak_days: 30`, `planting_window_length_days: 75`. Keep `legacy_paul_v1` untouched for comparability. Keep our complete-window guards and fail-fast GDD (do not port defects 2, 4).
2. **Planting window, single-window rule**: add `planting_start`/`planting_end` to `OFFSETS` and to `season()` (offsets from the season anchor, per year, for the per-winter table). In `calendar()`, derive the reported window from the **median budbreak offset**: `planting_end = median_budbreak − 30`, `planting_start = planting_end − 75`, and report p10/p90 budbreak as the spread. Assert `planting_end + 30 + 14 ≤ flowering_start` by construction. Never take medians of month-days. Expose in `location_api.py` and `dist/cycle.js` ruler as a fourth stage.
3. **Chill portions as a profile option**: move `chill_portions()` from `chill_comparison.py` into production.py (or a `chill.py` module), add `chill_definition: 'chill_portions'` with `chill_requirement_cp` (e.g. 14/21/28 sensitivity) so the same chain can be anchored on CP once Paul decides. Evergreen class → planting window "management-determined" (needs decision, §4).
4. **Skip**: Utah (negative totals in warm winters; chillR author advises against), §12 weighted score/normalisers, §13–§16 maps, municipality screening. Keep our frequency-ranking; add supervisor's ≥50 % overlap gate separately (cross-topic: risk-ranking scout).
5. Fix the four-month north window only if northern sites use `paul_analogs_v2`; note the R never ran northern phenology.
6. Add a `docs/weather/PAUL_R_V2_DIFF.md` recording the table above; update CHANGES list in production.py.

## 3. Effort (one builder with AI assistance)
| Rec | Days |
|---|---|
| 1 Profile + window/GDD/fruit/dry-spell knobs, tests for each knob | 1.5 |
| 2 Planting offsets + single-window calendar + API/UI ruler | 1.0 |
| 3 Chill-portions definition + CP requirement sensitivity | 1.0 |
| 4 Skips | 0 |
| 5 Northern four-month window validation on 5 SE cells | 0.5 |
| 6 Diff doc + CHANGES | 0.5 |
| **Total** | **4.5** |

## 4. Risks, unknowns, decisions
- Multiple-window mechanism is inferred from code; confirm with Paul's plot for one offending site (ask which municipalities). [unverified]
- Planting offsets 30/75 have no citation (line 86); Gerardo should confirm autumn planting before dormancy is the intended agronomy for Brazil and whether spring planting applies in the SE US.
- Chill method (hours vs CP) and CP requirement remain open (decision 7); profile knobs let both run, but the product must pick one primary.
- Evergreen sites have no chill-triggered budbreak → no planting window under this rule; needs a management-defined fallback or an explicit "not applicable".
- Four-month window + ≤7.2 with 100 h on grid data with warm night bias will mark more winters `chill_not_met` than R (which drops NA years silently); expect lower valid-year counts.
- LST vs UTC: R uses LST; our hourly store is UTC; shifts window edges only.
- GDD from (tmin+tmax)/2 vs daily mean changes budbreak by days at humid sites; quantify on the 19 cells before choosing.
