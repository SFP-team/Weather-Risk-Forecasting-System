# Open-field production packet

Updated 2026-09-22. Open `production_open_field.html` in a browser; `production_open_field.json` contains the calculations and provenance for Waldo, Citra and Papanduva. The coordinate dashboard in `dist/` contains 18 regenerated presets. Sources: `pipelines/weather/production.py`, `planting.py` and `location_api.py`.

Method `open-field-production-v2`; API `location-evidence-v4`; primary profile `stage_risks_v2`. Baseline: winters 2011–2025, existing NASA POWER archive, UTC. **These are provisional weather-exposure calculations, not validated phenology, disease incidence, crop-loss probabilities or cultivar advice.**

## Calendar and recurrence

The primary profile preserves the former `legacy_paul_v1` phenology: T < 7.2 °C chill, 50 h requirement, 7 °C forcing base, 150 °C·d to budbreak, flowering at budbreak +14…35 days, harvest at flowering start +70…110 days. Fruit development is flowering end +1 through harvest start −1. Existing four chill-definition/requirement profiles remain sensitivity comparisons.

An exposure is calculated inside **each winter's own stage**, not a median or p10–p90 envelope. The new primary whole-production dry-spell, radiation and GDD summaries cover budbreak through harvest end; legacy profiles retain their season-start totals. Establishment planting is a separate operation, not the beginning of this bearing-plant clock.

Headline eligibility requires:

- An applicable stage calendar and a defined event.
- At least **12 complete, assessable winters**.
- Event occurrence in **at least 50%** of those winters.

Risk records remain in `risks.by_id`; qualifying records appear in `ranked`, others in `demoted` with reasons. Equal frequencies receive equal competition ranks. Wilson 95% intervals show sampling uncertainty, not model accuracy. Missing weather and an unformed stage are not zero events. Evergreen-majority or unclassified primary calendars cannot support crop-stage or chill-shortfall headlines; calculated hypothetical exposures remain visible with that limitation.

Six event definitions are eligible for ranking: chill shortfall, flowering Tmin ≤ −2.2 °C, fruit-development Tmax ≥ 35 °C, harvest rain ≥ 10 mm, fruit-development Tmin ≤ 0 °C, and disease-favourable weather. Day-based events mean at least one qualifying day in the winter's susceptible stage. These are screening conventions, not equal-severity damage thresholds.

## Added exposure definitions

| Indicator | Calculation | Interpretation |
|---|---|---|
| Disease-favourable weather | Daily 15 ≤ Tmean ≤ 28 °C **and** RHmean ≥ 85% **and** rain ≥ 0.1 mm; separate flowering, fruit-development and harvest counts | Retains the existing expert-set proxy. One family headline: at least one proxy day across the three stages, with all three complete for the denominator. Not a pathogen-specific infection model. |
| Pollination-unfavourable weather | Flowering days with Tmax < 15 °C **or** rain ≥ 1 mm | Operational cold/wet proxy. Daily rain may occur outside bee-foraging hours. Does not include wind, bee species, hive strength or actual pollen transfer. |
| Supervisor cold-and-dry hypothesis | Flowering days with Tmax < 15 °C **and** rain < 1 mm | Separate comparison only. Reviewed guidance does not support treating cold rainy weather as favourable. |
| Warm midwinter | Hourly T > 21 °C, inclusive 15 Nov–15 Feb north or 15 May–15 Aug south | Independent of chill fulfilment. A warm-exposure count, not chill portions, hours of chill cancelled or injury. Missing-hourly API locations receive separately labelled complete-window **daily Tmax > 21 °C days**, never estimated hours. |
| Berry-stage frost exposure | Fruit-development days with Tmin ≤ 0 °C | Exposure, not confirmed tissue damage. Flowering and harvest are not silently included in the fruit-development window. |
| Flowering / fruit dry spells | Longest consecutive run of rain < 1 mm within each stage | Clipped to stage boundaries; missing or suspect rainfall invalidates only dependent metrics. Not root-zone drought, irrigation need or water balance. |

Pollination, warm-midwinter and dry-spell indicators have no calibrated adverse-season threshold. They remain descriptive exposures rather than receiving invented loss cutoffs or headline ranks. A backend metric catalogue supplies labels, units and definitions to both dashboard views.

Scientific basis and limits:

- [UF/IFAS pollination guidance](https://ask.ifas.ufl.edu/publication/IN1237) identifies cool, cloudy and rainy weather as impediments, particularly for honey bees. The 15 °C / 1 mm daily screen is an operational approximation, not a validated pollination-failure model.
- [UF/IFAS Blueberry Advisory System](https://ask.ifas.ufl.edu/publication/PP366) uses temperature and **leaf-wetness duration**. Daily RH/rain cannot reproduce that validated anthracnose model. This implementation does not claim to implement BAS.
- [UF/IFAS freeze guidance](https://ask.ifas.ufl.edu/publication/HS216) discusses temperatures above 70 °F (about 21.1 °C) during mid-November–mid-February as potentially negating some chill. We retain the requested **>21 °C** operational threshold; the six-month southern shift is an explicit convention, not a Brazilian calibration.
- [NC State freeze guidance](https://content.ces.ncsu.edu/blueberry-freeze-damage-and-protection-measures) describes stage-dependent sensitivity. Neither 0 °C nor the legacy −2.2 °C value establishes universal southern-highbush injury.

## One establishment planting window

**Decision: use regional establishment guidance, not `budbreak −105…−30 days`.** The reviewed sources do not support that offset formula. Nursery planting and mature-plant flowering are different operations; a first-year harvest must not be inferred from this calendar.

| Registered region | Displayed window | Basis and precision |
|---|---|---|
| Florida, including Citra and Waldo | Mid-December to mid-February | [UF/IFAS CIR1192](https://ask.ifas.ufl.edu/publication/MG359), for bare-root or container-grown plants. “Mid” is approximate, not a day-specific safety threshold. Home-garden extension guidance, not an evergreen-specific commercial model. |
| Georgia | Winter, approximately December–February | [UGA Circular 946](https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/) says **winter transplanting**, without exact dates. The months are a meteorological-season display convention, not source-specified endpoints or a prohibition on autumn planting. |
| Santa Catarina | Winter while dormant, approximately June–August | [Embrapa-authored guidance in Revista Cultivar](https://revistacultivar.com.br/artigos/grande-potencial) says winter **while dormant**, without dates. June–August is a display convention; nursery dormancy and local practice take precedence. |

The formula is a transparent lookup, `window = regional_guidance[registered_region]`, with one window per covered location. Unknown-region coordinates receive an explicit unavailable result, not a Florida or hemisphere-only default. Shared weather-cell identity does not establish regional applicability.

Assumptions: suitable healthy nursery stock, prepared well-drained acidic root zone, irrigation and local confirmation of soil workability, freeze protection, cultivar and stock condition. UF and UGA recommend first-season flower removal for establishment. The regional window remains available at evergreen-class sites because it does not depend on the unsupported chill-triggered crop clock. No numerical pot/tunnel adjustment is made.

## Reproduction and verification

On the server, from `/media/fpt/fpt2/Weather_Claude`:

```sh
env/bin/python code/production.py
env/bin/python code/location_api.py --snapshots
```

Outputs: `reports/production/` and `reports/ui_snapshots.json`. Split the latter locally with `python3 scripts/split_snapshots.py <file>`. No weather acquisition is invoked.

2026-09-22 verification: **96 backend tests passed**. All 270 preset site-years retained their earlier chill/date/stage-exposure values, and all 18 annual summaries and weather-content hashes matched the prior snapshots. Independent reconstruction from raw daily/hourly inputs matched the new metrics in 29 complete River Valley/Papanduva crop-years; a real hourly-unavailable land coordinate returned 15 complete warm-weather seasons in **days**.

Browser verification covered all 18 presets, 135 selected winter/stage views and 855 displayed values, keyboard/state retention, real shared-cell/daily-only API requests and downloaded HTML/JSON reports. Planting and selected winter/stage/system/chart labels survived export. Desktop/mobile views were inspected; 320/390/768/1440 px checks found no page overflow. A missing production-method field found by the browser gate was fixed at the source; 39 production/API tests passed afterward.

River Valley still has modeled harvest **23 April–2 June**. Heavy harvest rain qualifies in **14/14** assessable winters; disease-weather qualifies in **12/14**. The supervisor's early-April harvest expectation remains an unresolved phenology discrepancy, not a reason to suppress those weather results. Warm grid minimum temperatures and missed station cold events remain uncorrected.
