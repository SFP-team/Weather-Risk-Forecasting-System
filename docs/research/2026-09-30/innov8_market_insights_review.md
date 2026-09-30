# innov8.ag Market Insights: review and what we adopted

Reviewed 30 September 2026 from the public page https://www.innov8.ag/market-insights/, its sitemap and the public JavaScript bundles that render it (`MarketInsights`, `useForecastRisk`, `dataSourceLabels`). No account, paid service or data download was used.

## What the platform does

innov8.ag is a commercial blueberry market and crop-stage service for growers and marketers. It covers 18 regions, including Peru and Mexico. Weather comes from Open-Meteo (ERA5 reanalysis plus GFS and ECMWF forecasts). Market data comes from USDA NASS, FAS and AMS.

| Feature | Method found in the page code |
|---|---|
| Crop stage | Growing degree-days, base 45 °F, from daily (Tmax + Tmin) / 2, summed from 1 January. Fixed stage thresholds with defaults of 250 (bud break), 500 (bloom), 800 (fruit set) and 1500 (ripening) °F·days. |
| Season pace | Days ahead of or behind the 10-year average for the same GDD total. |
| Bee flight | Hourly temperature interpolated from daily Tmax and Tmin with a sine curve. Flight hours are hours from 09:00 to 17:00 at or above 12.8 °C. Under 4 hours is a poor day, and 2 or more poor days in a row is a cold stretch. |
| Frost | Frost events tagged by the current stage, with a kill estimate in percent. |
| Rain | Daily rain severity bands starting at more than 5 mm (moderate). |
| Chill | Percent of a target, as simple chill hours and Utah units, with risk flagged below 90% and 70%. |
| Market | An Overlap Pressure Index built from USDA supply weights, and analog years matched by RMSE on the season pattern. |
| Other | Scout votes on the current stage that override the model; photo stage recognition; weekly AI audio briefs; action recommendations. |

The site reports its own weaknesses. It cites METER Group finding that 74% of sites had a "bad year" with more than 5 days of error at 375 GDD. For 2026 it says its "GDD models are lagging behind" and asks growers to report stages.

## Adopted

Both additions apply to the primary profile `stage_thermal_v3` only. Legacy profiles are unchanged (18 of 18 committed v2 snapshots reproduced exactly).

1. **Bud-stage freeze.** innov8 checks frost by stage. Our model had checked freezes at flowering and fruit only, so the budbreak-to-flowering window went unchecked. We use the NC State Extension critical temperatures (Cline and Fernandez, rev. 2024): −6.7 °C (20 °F) for early bud stages and −3.9 °C (25 °F) once half the heat to flowering has accumulated. It is a ranked family and a scan crop-loss measure.
2. **Honey bee flight hours and a pollination gap.** We keep innov8's 12.8 °C daytime threshold (Thorp 1996; University of Maine flight index) but use the recorded hourly temperatures instead of a sine curve. We define the event from flower receptivity rather than a 2-day stretch: 4 or more flowering days in a row without a flight hour, since flowers are receptive for 3 to 5 days (UF/IFAS IN1237) or at least 4 (DeVetter et al. 2022). The pollination family now uses this event. The scan also ranks starts by the share of flowering days without flight.

Effect across the 71 presets: only Burgaw, NC gains a ranked risk (bud-stage freeze, 8 of 15 winters). Georgia, Loris and Tallahassee show 2 to 4 winters of each event. Florida, Peru, Chile and Mexico are unchanged. Managed-cycle recall of published harvest months rose from 0.79 to 0.81; chill-clock scores did not change.

## Not adopted

| Feature | Reason |
|---|---|
| Fixed GDD stage thresholds from 1 January | This is the fixed-calendar problem v3 removed. Low-chill southern highbush budbreak depends on chill completion, and 1 January is wrong for the southern hemisphere and for evergreen cycles. |
| Frost kill percentage | No published dose-response curve for daily grid minimum temperature. NC State notes that fields run 10 to 12 °F colder than airports, so a percentage would overstate precision. |
| Sine-interpolated hours | We have recorded hourly temperature for every land point. |
| 2-day cold stretch | Shorter than flower receptivity; would flag gaps that do not cost pollination. |
| Market overlap index, pricing, analog market years | Outside the weather-risk scope. |
| Audio briefs, photo stage AI | Product features, not model science; paid services are out of scope. |

## Future candidates

- **Grower and breeder stage reports.** innov8's scout votes are the strongest idea on the site. Observed budbreak, bloom and harvest dates would validate our stage clock and are the main gap named in `HANDOVER.md`.
- **In-season pace.** Days ahead or behind the historical median for the current season, once forecasts or current-year data are in scope.
- **Utah chill beside chill hours and portions**, as a reported comparison only.
- **Action notes per risk**, such as frost protection when bud-stage freeze is forecast, after breeder review of the wording.

## Sources

- innov8.ag Market Insights: https://www.innov8.ag/market-insights/
- NC State Extension, Blueberry freeze damage and protection measures: https://content.ces.ncsu.edu/blueberry-freeze-damage-and-protection-measures
- UF/IFAS IN1237: https://ask.ifas.ufl.edu/publication/IN1237
- University of Maine, Background: honeybee flight activity index: https://extension.umaine.edu/ipm/background-honeybee-flight-activity-index/
- DeVetter et al. (2022), Frontiers in Sustainable Food Systems 6:1006201: https://doi.org/10.3389/fsufs.2022.1006201
