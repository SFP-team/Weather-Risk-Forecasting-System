# Open-field production packet

Updated 2026-10-12. `production_open_field.html` and `.json` hold the Waldo, Citra and Papanduva calculations and provenance. `thermal_reference.json` holds the Waldo derivation of the stage thermal constants. The literature benchmark is in `../benchmark/`. The dashboard in `dist/` has 71 presets: 18 pilot and panel sites plus 53 benchmark sites. Code lives in `pipelines/weather/production.py`, `benchmark.py`, `planting.py` and `location_api.py`.

For breeders and other non-programmers, `model_formulas_for_breeder_review.html` explains every formula and setting in plain language. It works through one Waldo winter (2016–17) day by day and has comment boxes, a notes download and a print layout for sending suggestions back. Its day-by-day values and lookup tables were recomputed with the production code and reproduce the model's dates exactly. Regenerate it if a formula or constant changes.

Method `open-field-production-v3`, API `location-evidence-v5`, primary profile `stage_thermal_v3`. Baseline winters are 2011–2025 from the existing NASA POWER archive. **These are provisional weather-exposure calculations, not validated phenology, disease incidence, crop-loss probabilities or cultivar advice.**

## Why v3 replaced v2

The v2 calendar had four defects that a review of its outputs exposed.

1. Stage lengths ignored temperature. All 235 computed calendars in the 18 committed snapshots used flowering at budbreak +14 to +35 days and harvest at flowering start +70 to +110 days, so every site harvested for 40 days. In central Chile this put harvest between September and November; growers harvest November to January.
2. The chill requirement had no stated cultivar basis. Lyrene (2008) gives 100 to 400 hours for Emerald, and the supervisor's later R workflow uses 100. v3 used 100 hours from 2026-09-28. On 2026-10-12 the user set it to 50 hours, the legacy value. Neither number is a measured flowering minimum for a cultivar.
3. The daily disease rule (15–28 °C, RH ≥ 85%, rain ≥ 0.1 mm) had no published source. The UF Blueberry Advisory System works from hourly leaf wetness.
4. The chill clock returned no production window at 14 of 46 benchmark sites that grow southern highbush, including every site in Peru and Mexico. The product must give a window for any land coordinate.

v2 and the older profiles remain as sensitivity comparisons. With `stage_risks_v2` as primary, the API reproduces all 18 committed v2 snapshots exactly. Only method labels, change and limitation text, the metric catalogue and the sensitivity table gained v3 entries.

## Stage clock

Chill counts hours below 7.2 °C from 1 November in the north and 1 April in the south, until 50 hours. Dynamic Model chill portions are reported beside chill hours for every winter; they do not trigger anything yet. Budbreak follows at 150 growing degree-days, base 7 °C, as before.

**Decision, 2026-10-12: the chill requirement is 50 hours.** The user asked to make the minimum chill hours 50, not 100. `stage_thermal_v3` now uses `chill_requirement_hours: 50`, like the legacy profiles. `legacy_paul_100h_v1` and `bounded_uf_100h_v1` keep 100 hours and still appear in every sensitivity table. Nothing else changed: the chill definition, chill window, 150 GDD to budbreak, stage sums, classification thresholds and risk thresholds are as before. The production-system classes keep their own limits, under 100 chill hours for Evergreen and 300 or more for Deciduous. The chill-shortfall risk now counts winters below 50 hours.

After budbreak, stages follow daily degree-days with the daily mean capped at 30 °C:

| Stage | Requirement | Counted from |
|---|---|---|
| Flowering start | 85 GDD | budbreak |
| Flowering end | 375 GDD | budbreak |
| Harvest start | 633 GDD | flowering start |
| Harvest end | 1242 GDD | flowering start |

Three constants are the Waldo medians of the degree-days that the old fixed offsets covered in 2011–2025, counted from the 50-hour chill date: 84.9, 632.9 and 1242.4 GDD (`thermal_reference.json`). With the 50-hour requirement, v3 matches that derivation. Waldo's median budbreak is 6 January, flowering starts 22 January and harvest runs 29 March to 10 May, within two days of the legacy profiles (flowering 20 January, harvest 31 March to 10 May). Under the 100-hour requirement used until 2026-10-12, flowering started 7 February and harvest ran 4 April to 12 May. Other sites stretch or shrink with their own temperatures. The flowering span of 290 GDD comes from the F10 to F90 span of the Kovaleski et al. (2015) bloom curves at Citra, 293 GDD for Emerald and 287 for Jewel. The 633 GDD to first harvest matches Chilean on-farm sums of 593 (O'Neal) and 665 (Brigitta). The 1242 GDD harvest end has no direct literature support. Published harvest spans run 14 to 51 days, and v3 gives 38 to 43 days at Waldo, Chillán and Grand Junction.

The chill requirement also decides which sites get a winter calendar. Of the 18 pilot and panel sites, 14 have one: Citra, Waldo, Clear Springs, Dole, Barben, River Valley, Wauchula, Sebring, Lake Placid, the Georgia/Alma pilot, Homerville, Valdosta, Folkston and Papanduva. The other 4 use the managed-cycle scan as their primary window. Astin East, Okeechobee and Arcadia are evergreen-majority. PF Berry has no two-thirds majority and gives a calendar in only 11 of 15 winters. Under 100 hours, 8 sites had a calendar and 10 used the scan. Across the 71 saved locations the calendar now applies at 50, up from 41.

Median dates count day offsets from the season start. Under `stage_thermal_v3` (profile flag `leap_day_offsets: corrected`), 29 February is left out of each offset before the median is taken, so winters that cross a leap day no longer push median dates one day late. The legacy profiles keep raw day counts. On the 71 presets this moved 27 median dates at 17 sites one day earlier.

These constants describe a UF-type low-chill southern highbush. Rabbiteye and many northern-highbush cultivars need longer from flowering to harvest, and the benchmark shows it.

## Where the chill clock applies

The chill-triggered calendar applies only when all three conditions hold:

- The site lies outside the tropics, |latitude| ≥ 23.44°.
- The multi-feature classification is not Evergreen and not unknown.
- At least 12 of 15 winters produce a complete calendar.

The result carries `chill_clock.applicable` and its reasons. Tropical, evergreen and unclassified sites are exempt from the chill-shortfall risk. A deciduous site with sparse calendars is not exempt, because failed chill is the shortfall.

## Managed-cycle scan

Where the chill clock does not apply, the scan gives the production window. Elsewhere it runs as a comparison labelled "if managed as an evergreen cycle". Each of 24 start dates, the 1st and 15th of every month, is treated as a managed budbreak and followed through the same thermal clock in every year (scan method `managed-cycle-scan-v4`).

Every start and year has exactly one outcome, counted per start in `outcomes`:

| Outcome | Meaning |
|---|---|
| `complete` | All four stage dates are reached within the stage horizon, flowering lasts at most 66 days, and the first harvest comes at most 150 days after flowering starts. |
| `stalled_slow` | The stage dates exist, but flowering lasts over 66 days or the first harvest comes over 150 days after flowering starts. 66 days is the longest published flowering season (Asturias); 150 days is beyond the longest published flowering-to-harvest intervals. |
| `stalled_horizon` | A stage requirement is not reached within the 300-day stage horizon. |
| `weather_incomplete` | The archive has a gap or ends before the cycle does. These cycles are left out of every count. |

- `cycles` is the number of complete cycles. `stalled_cycles` is `stalled_slow` plus `stalled_horizon`.
- Bud-stage freeze, flowering freeze and fruit frost count threshold crossings in complete cycles only. A stall is never counted as a freeze.
- Cycle failure (`cycle_failure`) is a separate family: stalled cycles divided by complete plus stalled cycles.
- A start needs at least 12 cycles with evidence for every family, which in practice means 12 complete cycles. If bud-stage freeze, flowering freeze, fruit frost or cycle failure recurs in at least half of its cycles, the start is not favourable. A start whose cycles mostly stall has too few complete cycles to judge freezes, but enough cycles to judge cycle failure, so it shows as recurring cycle failure.
- The remaining starts are compared on eight measures: the bud-freeze, flowering-freeze, fruit-frost and cycle-failure shares of cycles, and the share of stage days with fruit heat, harvest heavy rain, moderate-or-higher infection risk or no honey bee flight. Favourable starts are the Pareto front, meaning no other start is at least as good on every measure and better on one. Starts within one affected cycle (freezes and cycle failure) or one affected day per cycle (the other measures) of a front start on every measure are added as near ties.
- The favourable flowering and harvest months are the union over favourable starts. `unconstrained` means weather does not separate the start dates, so timing is a market or management choice.
- If no start qualifies, there is no production window. Live checks on 2026-10-05 found this where the warm season is too short for the stage constants. In a Cascade Range cell near Yakima, WA and at Naantali, Finland, a stage missed its heat requirement within the 300-day stage horizon in 14 of 15 winters, and no start completed 12 cycles. Nearby valley pins (Yakima city, Prosser) keep a chill-triggered calendar. Cool sites in between fall back to scan windows: Lynden, WA (11/15 calendars), Cherryfield, ME (6/15) and Lac-Saint-Jean, QC (3/15). Cycles that miss a stage within the horizon used to be dropped as incomplete; they are now `stalled_horizon` and count as cycle failure.

Until 2026-10-12, stalled cycles were added to the three freeze families, and cycles that missed the horizon were dropped. Paul approved the correction. Its effect on the 71 presets (stage_thermal_v3, deployed code against the new code):

- Of 25,560 start-years, 23,287 are complete, 1,354 stalled slow, 372 stalled at the horizon and 547 weather incomplete.
- The 30 sites where the scan is the primary window keep their favourable starts and months.
- Favourable starts change at three comparison sites. Grand Junction, MI goes from one start (1 July) to eight (15 March to 1 July), because spring cycles that stalled had counted as freezes. Odemira adds 15 November and Pelotas adds 15 May.
- Harvest months change at six comparison sites: Grand Junction from the new starts, and Waldo, Homerville (two presets each) and Poplarville by one boundary month from the leap-day correction.
- 121 starts at 30 sites no longer show a recurring freeze, because the stalled cycles that had counted as freezes now count only as cycle failure. 116 starts at 24 sites now show recurring cycle failure. No start gains a recurring freeze.

The scan assumes management can start a cycle on any date. Flower-bud induction and market timing are not modelled.

## Disease weather

`stage_thermal_v3` replaces the daily proxy with an hourly infection model. An hour is wet when grid relative humidity from temperature and dewpoint reaches 90%. A wet period ends after four dry hours and is assigned to the local solar day of its last wet hour. The anthracnose index is the UF Blueberry Advisory System equation (Wilson et al. 1990): moderate at 0.15, high at 0.50, zero outside 7–35 °C, with temperatures below 10 °C evaluated at 10 °C. The Botrytis index is the Strawberry Advisory System flower-infection equation (Bulger et al. 1987): moderate at 0.50, high at 0.70. Wetness is capped at the fitted ranges, 51 hours for anthracnose and 32 hours for Botrytis.

Flowering days count when either index reaches moderate. Fruit-development and harvest days use anthracnose only, because the Botrytis equation describes flower infection. The disease-weather risk event needs at least one high-risk day between flowering start and harvest end. The 90% threshold was validated against station sensors, not grid humidity, so these counts are weather favourability and not disease incidence.

## Bud-stage freeze and pollination gap

Both were added on 30 September 2026 after reviewing innov8.ag's Market Insights, which tracks frost at bud break and bee-flight hours in bloom (`docs/research/2026-09-30/innov8_market_insights_review.md`). Our versions follow published thresholds and use the hourly archive directly.

- **Bud-stage freeze.** The bud stage runs from budbreak to the day before flowering, a window the model previously did not check. NC State Extension gives damage below 20 °F (−6.7 °C) once flowers protrude from the bud and below 25 to 26 °F at half corolla length. The model uses −6.7 °C until the stage degree-days reach half of the 85 needed for flowering, then −3.9 °C (25 °F). An event is one bud-stage day at or below its critical temperature.
- **Honey bee flight hours.** A flight hour is an hour from 09:00 to 17:00 local solar time at or above 12.8 °C (55 °F), the foraging threshold in Thorp (1996) also used by the University of Maine honeybee flight index. Rain, wind and cloud are not in the hourly archive, so counts are an upper bound, and bumble bees fly at lower temperatures.
- **Pollination gap.** At least 4 consecutive flowering days without a flight hour. Blueberry flowers are receptive for 3 to 5 days (UF/IFAS IN1237), and DeVetter et al. (2022) give at least 4. This defines the pollination family in v3; the older cold-or-wet day counts stay as descriptive exposures.

Across the 71 presets, Burgaw, NC was the only site where bud-stage freeze ranked. With the 50-hour requirement no site ranks it: at Burgaw it occurs in 6 of 15 winters, below the 50% rule, and the coldest bud-stage night was −10.9 °C in winter 2016–17. The model breaks buds early there (median 29 December) because 50 chill hours come by mid-November, weeks before the March to April bloom growers report. The result describes a low-chill southern highbush planted that far north. Burgaw's ranked risks are disease weather (15 of 15), harvest heavy rain (14 of 15), flowering freeze (11 of 15) and pollination gap (9 of 15). Pollination gaps also rank at Elizabethtown (9 of 15) and Loris (8 of 15). Along the transect, bud freeze occurs in 0 of 15 winters at Waldo, 4 at Tallahassee, 6 at Alma and 5 at Loris, and pollination gaps in 0, 5, 3 and 8. Under the 100-hour requirement, Burgaw's budbreak was 4 January, its bud freeze ranked in 8 of 15 winters, and the transect counts were 0, 3, 3 and 4 for bud freeze and 0, 3, 2 and 4 for pollination gaps. Tropical and evergreen sites show neither.

## Risks

A risk headlines only when its event occurs in at least 50% of at least 12 complete winters. Complete records stay in `risks.by_id`; qualifying records go to `ranked` and the rest to `demoted` with reasons. Wilson 95% intervals show sampling uncertainty. Eight families can rank: chill shortfall, bud-stage freeze, flowering Tmin ≤ −2.2 °C, fruit-development Tmax ≥ 35 °C, harvest rain ≥ 10 mm, disease weather, fruit-development Tmin ≤ 0 °C, and pollination gap. These are screening conventions, not equal-severity damage thresholds. Where the scan is primary, the dashboard reports the risks that recur at the favourable starts.

## Literature benchmark

`pipelines/weather/benchmark_sites.json` lists 53 sites with published system, bloom, harvest and planting months. One research pass drafted each record from sources and a second pass checked it against those sources, without looking at model output. The groups are a US transect from Homestead to Burgaw with Mississippi, New Jersey and Michigan references (17), Peru, Chile and Mexico (11), other Latin America (8), and the rest of the world (17). The full report is `../benchmark/benchmark.html`.

Results for the 46 sites that grow southern highbush:

| Measure | v2 | v3 |
|---|---|---|
| Sites with no production window | 14 | 0 |
| Chill-clock harvest midpoint inside published months | 19/32 | 26/30 |
| Chill-clock bloom midpoint inside published months | 6/20 | 14/20 |
| Managed-cycle sites, harvest months recall and precision | none | 0.78 and 0.76 over 16 sites |
| Production-system class, exact match | 35/46 | 35/46 |

By region, the chill-clock harvest midpoint landed in published months at 14/15 US transect sites (v2 10/15), 4/5 Chilean sites (v2 1/5), 4/6 other Latin American sites (v2 2/6) and 8/10 rest-of-world sites (v2 10/12). The misses are Tallahassee, Ovalle, Tafí del Valle, Pelotas, Wolseley and Tzaneen; Ovalle and Tzaneen joined the winter calendar with the 50-hour requirement. Peru and Mexico had no v2 window. In the Peru, Chile and Mexico group, the six scan sites cover 78% of their published harvest months on average. At Chao, Peru, the scan gives harvest August to December against published August to January.

Where v3 still misses:

- Wolseley, South Africa is managed evergreen in a climate the model calls deciduous. Weather cannot see that management choice.
- Tafí del Valle sits at 2000 m inside a warmer grid cell, so harvest starts about two months early.
- At Chao, Peru the model needs 41 to 51 days from flowering to first harvest; the trial reports flowering from April and harvest from August. Harvest months match because the scan selects winter-flowering starts, not because stage timing is right.
- Pelotas grows rabbiteye only; the southern-highbush clock harvests too early there.
- Huelva, Morocco and the Chinese greenhouse regions harvest under tunnels, months ahead of open-field weather.
- Lublin and Vechta, both northern highbush, bloom about two weeks later in the model than in practice.
- Penguin, Tasmania shows 58 mean chill hours, which is implausible for 41°S. The coastal grid cell appears dominated by sea temperatures.
- Classification matches 8 of 17 rest-of-world sites. Some misses are managed evergreen or mixed practice in climates the model reads otherwise: Wolseley, Mengzi, Marondera, Huelva and Morocco. Others are mild maritime deciduous regions the model calls transitional or semi-evergreen: George, Penguin and Waikato.

The supervisor's R planting rule, budbreak minus 105 to 30 days, recovers 22% of published planting months with 21% precision on 17 sites. On the US transect, 15 sites, recall is 0.28 and precision 0.23. Under the 100-hour requirement the scores were 0.38 and 0.33 on 15 sites, and 0.48 and 0.37 on 14 transect sites. The rule's months start 1 to 6 months before the published months at 19 of 21 scored sites, and Osorno's overlap is 0. The app adopted the rule on 2026-10-12; see the planting window section below.

## Added exposure definitions

| Indicator | Calculation | Interpretation |
|---|---|---|
| Infection-risk days (v3) | Flowering days with anthracnose or Botrytis at moderate or higher; fruit-development and harvest days with anthracnose at moderate or higher; high-risk days from flowering start to harvest end | Hourly grid wetness, not canopy wetness, inoculum or incidence. |
| Disease-favourable weather (v2 and legacy) | Daily 15 ≤ Tmean ≤ 28 °C **and** RHmean ≥ 85% **and** rain ≥ 0.1 mm | Kept for comparison profiles only. Not a pathogen model. |
| Honey bee flight hours (v3) | Hours from 09:00 to 17:00 local solar time at or above 12.8 °C in each flowering day; days with none; longest run of such days | Temperature only, an upper bound. Feeds the pollination gap. |
| Pollination-unfavourable weather | Flowering days with Tmax < 15 °C **or** rain ≥ 1 mm | Older cold or wet proxy, kept as a descriptive exposure. Daily rain may fall outside bee-foraging hours. |
| Supervisor cold-and-dry hypothesis | Flowering days with Tmax < 15 °C **and** rain < 1 mm | Separate comparison only. |
| Warm midwinter | Hourly T > 21 °C, 15 Nov–15 Feb north or 15 May–15 Aug south | A warm-exposure count, not chill cancelled. Locations without hourly data get complete-window daily Tmax > 21 °C **days**. |
| Berry-stage frost exposure | Fruit-development days with Tmin ≤ 0 °C | Exposure, not confirmed tissue damage. |
| Flowering and fruit dry spells | Longest run of rain < 1 mm within each stage | Not root-zone drought or irrigation need. |

Pollination, warm-midwinter and dry-spell indicators have no calibrated adverse-season threshold, so they stay descriptive. A backend metric catalogue supplies labels, units and definitions to the dashboard.

Sources and limits:

- [UF/IFAS pollination guidance](https://ask.ifas.ufl.edu/publication/IN1237) names cool, cloudy and rainy weather as impediments. The 15 °C and 1 mm screen approximates that guidance and has not been validated.
- [UF/IFAS Blueberry Advisory System](https://ask.ifas.ufl.edu/publication/PP366) uses temperature and leaf-wetness duration. v3 applies its equation to grid humidity, which the system was not calibrated on.
- [UF/IFAS freeze guidance](https://ask.ifas.ufl.edu/publication/HS216) says temperatures above 70 °F, about 21.1 °C, between mid-November and mid-February may negate some chill. The six-month southern shift is a convention.
- [NC State freeze guidance](https://content.ces.ncsu.edu/blueberry-freeze-damage-and-protection-measures) describes stage-dependent sensitivity. Neither 0 °C nor −2.2 °C is a universal southern-highbush injury threshold.

## Planting window

**Decision, 2026-10-12: the app's planting window is the supervisor's R rule.** The user approved making Paul's rule the planting window, as his 2026-09-21 River Valley review asked. This reverses the 2026-09-22 change that had replaced the rule with regional home-garden guides because the offsets had no source. The regional guides stay as a published season comparison. Nursery planting and mature-plant flowering are still different operations.

The rule ends planting 30 days before modelled budbreak and lasts 75 days, so planting runs from 105 to 30 days before budbreak. The source is Paul's private R workflow `southern_brazil_blueberry_climate_analogs.R`, lines 91-92 and 1219-1220. The R labels the offsets preliminary and cites no source, and nobody has validated them. Only the primary profile `stage_thermal_v3` carries the rule, as `planting_end_before_budbreak_days: 30` and `planting_window_length_days: 75`. `stage_risks_v2` and `legacy_paul_v1` have no planting rule.

Each winter gets its own window, from that winter's modelled budbreak minus 105 days to minus 30 days. Season rows carry `planting: [start, end]` and `offset_days.planting_start/end`; the offsets can be negative because planting often starts before the season anchor. The typical window is one window counted back from the median budbreak. Its earliest start is the 10th-percentile budbreak minus 105 days, and its latest end is the 90th-percentile budbreak minus 30 days. The R took medians of planting month-days separately, which can give reversed or phantom windows, such as several windows with an April wrap. Deriving one window from the median budbreak fixes that.

The planting block uses method `budbreak-planting-v1` and one of three statuses:

- `available`: a window, its spread, the budbreak median, p10, p90 and winter count, the rule, basis and precision. Example: Waldo, 23 Sep to 7 Dec from a median budbreak of 6 Jan over 15 winters, spread 1 Sep to 24 Dec. Papanduva gets 9 Apr to 23 Jun from a median budbreak of 23 Jul.
- `not_applicable`: the chill-triggered calendar does not apply. The label is "Set by management" where the chill requirement does not apply, and "No calculated window" where it applies but too few winters produce a chill-triggered calendar, as at PF Berry with 11 of 15.
- `unavailable`: the point has no hourly crop calendar. The label is "Planting window unavailable".

Across the 71 saved locations, 50 get a calculated window and 21 do not: 18 are "Set by management" and 3 show "No calculated window" (PF Berry 11 of 15, Penguin 8 of 15 and George 0 of 15 calendar winters). Four windows cross the year end.

Registered saved locations in Florida, Georgia or Santa Catarina also carry a `published` season, method `regional-establishment-v1`, shown even where the calculated window does not apply. 30 locations carry one: 22 Florida, 6 Georgia and 2 Santa Catarina.

| Registered region | Published season | Basis and precision |
|---|---|---|
| Florida | Mid-December to mid-February | [UF/IFAS CIR1192](https://ask.ifas.ufl.edu/publication/MG359) (now MG359), bare-root or container plants. "Mid" is approximate. This is home-garden guidance, not a commercial or evergreen model. Commercial guidance differs: [UF/IFAS HS1525](https://journals.flvc.org/edis/article/view/140453) (July 2026) advises planting in the early-spring and fall root-growth periods, and reports that newer UF southern highbush cultivars can produce a marketable crop within 12 months of planting. The app no longer tells Florida growers to remove first-season flowers. |
| Georgia | Winter, approximately December–February | [UGA Circular 946](https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/) says winter transplanting without dates. The months are a display convention. |
| Santa Catarina | Winter while dormant, approximately June–August | [Embrapa-authored guidance in Revista Cultivar](https://revistacultivar.com.br/artigos/grande-potencial) gives no dates. June–August is a display convention. |

A dropped pin gets a calculated window from its own budbreak but never a published season. The app never infers a region from a place name or a shared weather cell. The window comes from modelled budbreak, not observed dates, and the app does not check frost, heat or rain inside it. Growers still need to confirm soil workability, nursery stock, cultivar, plant condition and freeze protection. It is a one-time establishment window, not annual replanting or a first-year harvest forecast. No pot or tunnel adjustment is made.

In the literature benchmark the rule covers 22% of published planting months on 17 southern-highbush sites, with 21% precision. Published December to February in Florida and Georgia compares with the rule's September or October to December. Paul has not supplied a source for the offsets, and no one has checked them against planting records.

## Reproduction and verification

On the server, from `/media/fpt/fpt2/Weather_Claude/code`:

```sh
../env/bin/python production.py                    # three-site packet -> reports/production/
../env/bin/python production.py thermal-reference  # Waldo constants -> reports/production/thermal_reference.json
../env/bin/python benchmark.py                     # 53-site benchmark -> reports/benchmark/
../env/bin/python location_api.py --snapshots      # 71 registered sites -> reports/ui_snapshots.json, for before/after comparisons
```

No weather acquisition runs. Since 2026-10-14 the app does not ship these results.

The location API caches successful (200) analyses: an in-memory LRU of 64 results and JSON files in `cache/location_api/`, pruned to the 2,000 most recently used. The key covers the API method, the primary profile, a hash of the code files that shape a result and the coordinates. It does not cover the weather archives or the site registries, so delete `cache/location_api/*.json` after any archive or `config/` update. `--snapshots` never uses the cache. `/api/health` reports `busy_since`, `busy_seconds` and cache counters, and every request adds one line without coordinates to `logs/location_api_access.jsonl` (rotated at 10 MiB, five older files kept). The API answers 403 unless the Host header is `127.0.0.1:8787` or `localhost:8787`, and refuses cross-site requests by `Origin` or `Sec-Fetch-Site`.

2026-09-28 verification: the server suite passed 127 tests. With `stage_risks_v2` as primary, the API reproduced all 18 committed v2 snapshots exactly. Browser checks covered Arcadia, Chao and a live Clinton, NC coordinate, all five views at 390 px without page overflow, and the benchmark page.

2026-09-30 verification after the bud-freeze and bee-flight additions: 130 server tests passed, and v2 again reproduced all 18 committed v2 snapshots exactly. The benchmark's chill-clock scores are unchanged; managed-cycle recall of published harvest months rose from 0.79 to 0.81 and precision from 0.70 to 0.72. Burgaw's overview, bud-development lane and scan table were checked in the browser with no page errors and no overflow at 390 px.

2026-10-12 verification after the scan accounting change, the leap-day correction, the API hardening and the planting text update: 160 server tests passed in a staging copy. With `stage_risks_v2` as primary, all 18 committed v2 snapshots matched apart from two fields outside the profile output: the land-mask version label, which the deployed code already reports differently, and the Florida planting text. Every committed sensitivity entry, including the reused primary, matched exactly.

2026-10-12 verification after the planting window change: 251 server tests passed in a staging copy, 8 more than before: 4 planting-rule tests in `tests/weather/test_production.py` and 4 in the new `tests/weather/test_planting.py`. Legacy parity with `stage_risks_v2` held on 18 sites with 0 differences. All 71 saved snapshots differ from the previous commit only in planting fields, one new `production.changes` entry and `analysis_id`; no weather, calendar or risk number changed, and the benchmark scores are unchanged. The snapshots, this packet and the benchmark were regenerated. The code was deployed to `code/` with matching SHA-256 hashes, only `blueberry-ui-api` was restarted, and the live API returned 30 Sep to 14 Dec for an Alma coordinate. Browser checks at 1440 and 390 px covered Waldo, Alma, Papanduva, Burgaw, Arcadia, River Valley, the live Clinton pin and Waldo winter 2011 with no page errors, no CSP violations and no page overflow.

2026-10-12 verification after the 50-hour chill requirement: 251 server tests passed in staging. One test pinned the 100-hour chill date of a synthetic 5 °C winter; it now expects 3 November instead of 5 November. Legacy parity with `stage_risks_v2` held on 18 sites with 0 differences. The code was deployed to `code/` with matching SHA-256 hashes, the pre-change files are in `tmp/opus_stage/code_backup_20261012_chill50/`, and only `blueberry-ui-api` was restarted. The snapshots, this packet and the benchmark were regenerated. All 71 snapshots differ only inside the production and planting blocks and `analysis_id`; daily weather, climate and soil are unchanged. Browser checks at 1440 and 390 px showed the new results and the badge "50 h chill requirement" for River Valley, Waldo, Papanduva and Arcadia, with no page errors, CSP violations or overflow, and 34 UI tests passed.
