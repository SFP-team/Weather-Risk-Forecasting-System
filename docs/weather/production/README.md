# Open-field production packet

Updated 2026-09-28. `production_open_field.html` and `.json` hold the Waldo, Citra and Papanduva calculations and provenance. `thermal_reference.json` holds the Waldo derivation of the stage thermal constants. The literature benchmark is in `../benchmark/`. The dashboard in `dist/` has 71 presets: 18 pilot and panel sites plus 53 benchmark sites. Code lives in `pipelines/weather/production.py`, `benchmark.py`, `planting.py` and `location_api.py`.

Method `open-field-production-v3`, API `location-evidence-v5`, primary profile `stage_thermal_v3`. Baseline winters are 2011–2025 from the existing NASA POWER archive. **These are provisional weather-exposure calculations, not validated phenology, disease incidence, crop-loss probabilities or cultivar advice.**

## Why v3 replaced v2

The v2 calendar had four defects that a review of its outputs exposed.

1. Stage lengths ignored temperature. All 235 computed calendars in the 18 committed snapshots used flowering at budbreak +14 to +35 days and harvest at flowering start +70 to +110 days, so every site harvested for 40 days. In central Chile this put harvest between September and November; growers harvest November to January.
2. The 50-hour chill requirement sits below the 100 to 400 hour range Lyrene (2008) gives for Emerald. v3 uses 100 hours, the value in the supervisor's later R workflow.
3. The daily disease rule (15–28 °C, RH ≥ 85%, rain ≥ 0.1 mm) had no published source. The UF Blueberry Advisory System works from hourly leaf wetness.
4. The chill clock returned no production window at 14 of 46 benchmark sites that grow southern highbush, including every site in Peru and Mexico. The product must give a window for any land coordinate.

v2 and the older profiles remain as sensitivity comparisons. With `stage_risks_v2` as primary, the API reproduces all 18 committed v2 snapshots exactly. Only method labels, change and limitation text, the metric catalogue and the sensitivity table gained v3 entries.

## Stage clock

Chill counts hours below 7.2 °C from 1 November in the north and 1 April in the south, until 100 hours. Dynamic Model chill portions are reported beside chill hours for every winter; they do not trigger anything yet. Budbreak follows at 150 growing degree-days, base 7 °C, as before.

After budbreak, stages follow daily degree-days with the daily mean capped at 30 °C:

| Stage | Requirement | Counted from |
|---|---|---|
| Flowering start | 85 GDD | budbreak |
| Flowering end | 375 GDD | budbreak |
| Harvest start | 633 GDD | flowering start |
| Harvest end | 1242 GDD | flowering start |

Three constants are the Waldo medians of the degree-days that the old fixed offsets covered in 2011–2025, counted from the old 50-hour chill date: 84.9, 632.9 and 1242.4 GDD (`thermal_reference.json`). They do not keep Waldo's old calendar, because v3 also raises the chill requirement to 100 hours. Waldo's median budbreak moves from 6 January to 24 January and flowering start from 20 January to 7 February. The fruit then develops in warmer weather, so harvest lands on 4 April to 12 May, close to the old 31 March to 10 May. Other sites stretch or shrink with their own temperatures. The flowering span of 290 GDD comes from the F10 to F90 span of the Kovaleski et al. (2015) bloom curves at Citra, 293 GDD for Emerald and 287 for Jewel. The 633 GDD to first harvest matches Chilean on-farm sums of 593 (O'Neal) and 665 (Brigitta). The 1242 GDD harvest end has no direct literature support. Published harvest spans run 14 to 51 days, and v3 gives 38 to 43 days at Waldo, Chillán and Grand Junction.

The 100-hour requirement also changes which sites get a winter calendar. Of the 18 pilot and panel sites, 8 keep it: Waldo, Citra, Clear Springs, the Georgia sites and Papanduva. The other 10, all in central and south Florida, use the managed-cycle scan as their primary window. Astin East, Okeechobee and Arcadia are evergreen-majority; the other seven reach 100 chill hours in only 4 to 10 of 15 winters.

These constants describe a UF-type low-chill southern highbush. Rabbiteye and many northern-highbush cultivars need longer from flowering to harvest, and the benchmark shows it.

## Where the chill clock applies

The chill-triggered calendar applies only when all three conditions hold:

- The site lies outside the tropics, |latitude| ≥ 23.44°.
- The multi-feature classification is not Evergreen and not unknown.
- At least 12 of 15 winters produce a complete calendar.

The result carries `chill_clock.applicable` and its reasons. Tropical, evergreen and unclassified sites are exempt from the chill-shortfall risk. A deciduous site with sparse calendars is not exempt, because failed chill is the shortfall.

## Managed-cycle scan

Where the chill clock does not apply, the scan gives the production window. Elsewhere it runs as a comparison labelled "if managed as an evergreen cycle". Each of 24 start dates, the 1st and 15th of every month, is treated as a managed budbreak and followed through the same thermal clock in every year.

- A cycle whose flowering lasts over 66 days, or whose first harvest comes over 150 days after flowering starts, has stalled in cold weather. Stalled cycles count as failed cycles for flowering freeze and fruit frost.
- A start needs at least 12 complete cycles. If flowering freeze or fruit frost hits at least half of its cycles, it is recurring crop loss and not favourable.
- The remaining starts are compared on five measures: flowering-freeze share of cycles, fruit-frost share of cycles, and the share of stage days with fruit heat, harvest heavy rain or moderate-or-higher infection risk. Favourable starts are the Pareto front, meaning no other start is at least as good on every measure and better on one. Starts within one affected cycle or one affected day per cycle of a front start on every measure are added as near ties.
- The favourable flowering and harvest months are the union over favourable starts. `unconstrained` means weather does not separate the start dates, so timing is a market or management choice.

The scan assumes management can start a cycle on any date. Flower-bud induction and market timing are not modelled.

## Disease weather

`stage_thermal_v3` replaces the daily proxy with an hourly infection model. An hour is wet when grid relative humidity from temperature and dewpoint reaches 90%. A wet period ends after four dry hours and is assigned to the local solar day of its last wet hour. The anthracnose index is the UF Blueberry Advisory System equation (Wilson et al. 1990): moderate at 0.15, high at 0.50, zero outside 7–35 °C, with temperatures below 10 °C evaluated at 10 °C. The Botrytis index is the Strawberry Advisory System flower-infection equation (Bulger et al. 1987): moderate at 0.50, high at 0.70. Wetness is capped at the fitted ranges, 51 hours for anthracnose and 32 hours for Botrytis.

Flowering days count when either index reaches moderate. Fruit-development and harvest days use anthracnose only, because the Botrytis equation describes flower infection. The disease-weather risk event needs at least one high-risk day between flowering start and harvest end. The 90% threshold was validated against station sensors, not grid humidity, so these counts are weather favourability and not disease incidence.

## Risks

A risk headlines only when its event occurs in at least 50% of at least 12 complete winters. Complete records stay in `risks.by_id`; qualifying records go to `ranked` and the rest to `demoted` with reasons. Wilson 95% intervals show sampling uncertainty. Six families can rank: chill shortfall, flowering Tmin ≤ −2.2 °C, fruit-development Tmax ≥ 35 °C, harvest rain ≥ 10 mm, fruit-development Tmin ≤ 0 °C, and disease weather. These are screening conventions, not equal-severity damage thresholds. Where the scan is primary, the dashboard reports the risks that recur at the favourable starts.

## Literature benchmark

`pipelines/weather/benchmark_sites.json` lists 53 sites with published system, bloom, harvest and planting months. One research pass drafted each record from sources and a second pass checked it against those sources, without looking at model output. The groups are a US transect from Homestead to Burgaw with Mississippi, New Jersey and Michigan references (17), Peru, Chile and Mexico (11), other Latin America (8), and the rest of the world (17). The full report is `../benchmark/benchmark.html`.

Results for the 46 sites that grow southern highbush:

| Measure | v2 | v3 |
|---|---|---|
| Sites with no production window | 14 | 0 |
| Chill-clock harvest midpoint inside published months | 19/32 | 25/27 |
| Chill-clock bloom midpoint inside published months | 6/20 | 13/19 |
| Managed-cycle sites, mean recall of published harvest months | none | 0.79 over 19 sites |
| Production-system class, exact match | 35/46 | 35/46 |

By region, the chill-clock harvest midpoint landed in published months at 14/14 US transect sites (v2 10/15), 4/4 Chilean sites (v2 1/5), 4/6 other Latin American sites (v2 2/6) and 8/9 rest-of-world sites (v2 10/12). Peru and Mexico had no v2 window. In the Peru, Chile and Mexico group, the seven scan sites cover 81% of their published harvest months on average. At Chao, Peru, the scan gives harvest August to December against published August to January.

Where v3 still misses:

- Wolseley, South Africa is managed evergreen in a climate the model calls deciduous. Weather cannot see that management choice.
- Tafí del Valle sits at 2000 m inside a warmer grid cell, so harvest starts about two months early.
- At Chao, Peru the model needs 41 to 51 days from flowering to first harvest; the trial reports flowering from April and harvest from August. Harvest months match because the scan selects winter-flowering starts, not because stage timing is right.
- Pelotas grows rabbiteye only; the southern-highbush clock harvests too early there.
- Huelva, Morocco and the Chinese greenhouse regions harvest under tunnels, months ahead of open-field weather.
- Lublin and Vechta, both northern highbush, bloom about two weeks later in the model than in practice.
- Penguin, Tasmania shows 58 mean chill hours, which is implausible for 41°S. The coastal grid cell appears dominated by sea temperatures.
- Classification matches 8 of 17 rest-of-world sites. Some misses are managed evergreen or mixed practice in climates the model reads otherwise: Wolseley, Mengzi, Marondera, Huelva and Morocco. Others are mild maritime deciduous regions the model calls transitional or semi-evergreen: George, Penguin and Waikato.

The supervisor's R planting rule, budbreak minus 105 to 30 days, recovers 38% of published planting months with 33% precision on 15 sites. It is still not adopted.

## Added exposure definitions

| Indicator | Calculation | Interpretation |
|---|---|---|
| Infection-risk days (v3) | Flowering days with anthracnose or Botrytis at moderate or higher; fruit-development and harvest days with anthracnose at moderate or higher; high-risk days from flowering start to harvest end | Hourly grid wetness, not canopy wetness, inoculum or incidence. |
| Disease-favourable weather (v2 and legacy) | Daily 15 ≤ Tmean ≤ 28 °C **and** RHmean ≥ 85% **and** rain ≥ 0.1 mm | Kept for comparison profiles only. Not a pathogen model. |
| Pollination-unfavourable weather | Flowering days with Tmax < 15 °C **or** rain ≥ 1 mm | Operational cold or wet proxy. Daily rain may fall outside bee-foraging hours. |
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

## One establishment planting window

**Decision: use regional establishment guidance, not budbreak minus 105 to 30 days.** The reviewed sources do not support the offset rule, and the benchmark result above does not rescue it. Nursery planting and mature-plant flowering are different operations.

| Registered region | Displayed window | Basis and precision |
|---|---|---|
| Florida | Mid-December to mid-February | [UF/IFAS CIR1192](https://ask.ifas.ufl.edu/publication/MG359), bare-root or container plants. "Mid" is approximate. Home-garden guidance, not an evergreen commercial model. |
| Georgia | Winter, approximately December–February | [UGA Circular 946](https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/) says winter transplanting without dates. The months are a display convention. |
| Santa Catarina | Winter while dormant, approximately June–August | [Embrapa-authored guidance in Revista Cultivar](https://revistacultivar.com.br/artigos/grande-potencial) gives no dates. June–August is a display convention. |

Coordinates outside a registered region get an explicit unavailable result. Assumptions are healthy nursery stock, a prepared well-drained acidic root zone, irrigation, and local confirmation of soil workability and freeze protection. No pot or tunnel adjustment is made.

## Reproduction and verification

On the server, from `/media/fpt/fpt2/Weather_Claude/code`:

```sh
../env/bin/python production.py                    # three-site packet -> reports/production/
../env/bin/python production.py thermal-reference  # Waldo constants -> reports/production/thermal_reference.json
../env/bin/python benchmark.py                     # 53-site benchmark -> reports/benchmark/
../env/bin/python location_api.py --snapshots      # 71 presets -> reports/ui_snapshots.json
```

Split the snapshots locally with `python3 scripts/split_snapshots.py <file>`. No weather acquisition runs.

2026-09-28 verification: the server suite passed 127 tests. With `stage_risks_v2` as primary, the API reproduced all 18 committed v2 snapshots exactly. Browser checks covered Arcadia, Chao and a live Clinton, NC coordinate, all five views at 390 px without page overflow, and the benchmark page.
