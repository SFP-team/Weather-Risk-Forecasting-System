# Weather app: project status and user guide

Status date: 5 October 2026.

This guide describes the current code and saved results. It does not describe a future version.

The text uses short sentences, defined technical terms, and direct instructions. It follows ASD-STE100 writing principles. Formal compliance with the ASD-STE100 dictionary and all rules has not been certified. Screen labels and code names retain their exact spelling.

## Contents

1. [The present project stage](#1-the-present-project-stage)
2. [Recent changes](#2-recent-changes)
3. [The three types of information](#3-the-three-types-of-information)
4. [How to use the app](#4-how-to-use-the-app)
5. [The four Overview cards](#5-the-four-overview-cards)
6. [The six tabs](#6-the-six-tabs)
7. [How the calendar works](#7-how-the-calendar-works)
8. [Minimum data requirements](#8-minimum-data-requirements)
9. [How to read weather risks](#9-how-to-read-weather-risks)
10. [Your Near Yakima screenshot](#10-your-near-yakima-screenshot)
11. [Missing results and error messages](#11-missing-results-and-error-messages)
12. [How breeders can use the results](#12-how-breeders-can-use-the-results)
13. [Known limits and approved work](#13-known-limits-and-approved-work)
14. [What has been checked](#14-what-has-been-checked)
15. [Terms and units](#15-terms-and-units)
16. [Project records and technical details](#16-project-records-and-technical-details)

## 1. The present project stage

**The app is a working research prototype for historical weather assessment. It is not a validated cultivar calendar or a weather forecast service.**

A prototype is working software that still needs further checks before operational use.

The app helps you ask:

- What weather occurred at this location?
- What crop dates does the current model calculate from that weather?
- What weather events overlap those calculated crop stages?
- What do published reports say about production in the region?
- What evidence is missing?

The app cannot yet tell you which cultivar will perform best at a farm.

| Component | Current state | Important limit |
|---|---|---|
| Daily weather archive | The planned global download is complete. | Data are grid estimates, not measurements at every farm. |
| Hourly weather archive | The planned land-block download is complete. | Some islands and other unsupported cells have no installed hourly data. |
| Weather analysis | Works for supported land coordinates through the private server. | The server and local connection must operate. |
| Saved locations | 71 saved assessments are available. | Saved assessments do not require a new server calculation. |
| Crop calendar | Temperature-based version 3 is implemented. | Parameters describe a provisional low-chill southern-highbush scenario. |
| Weather risks | Events, frequencies, and exclusions are displayed. | Exposure is not crop damage or expected yield loss. |
| Regional evidence | 91 reviewed records from three IBO report editions are available. | Coverage is partial. Reports are not field observations at the pin. |
| Soil | Some pilot-site records are available. | Collection stopped after source failures. Most arbitrary pins have no soil records. |
| Planting guidance | Selected registered regions have source-based guidance. | It does not cover every coordinate. |
| Scientific validation | Regional literature comparisons and limited station checks exist. | Independent cultivar-by-site-by-year validation is not complete. |
| Public deployment | The current code is on GitHub. | The older hosted app has not received the current changes. |

The current local app is different from the older hosted app.

At the last requested service operation, the local UI, tunnel, and private API were stopped. This guide does not restart them.

### What the app does not provide

- A forecast for the next growing season.
- A recommended cultivar or breeding parent.
- A measured probability of crop loss.
- A yield or profit prediction.
- A parcel-level suitability verdict.
- A calculated tunnel climate or irrigation schedule.
- A validated calendar for every blueberry type.
- An automated breeder brief or report question-answering service.

## 2. Recent changes

Dates below refer to completed project work. They do not imply scientific validation.

| Date | Before | Improvement now present |
|---|---|---|
| 12 to 22 September | The work was mainly scripts and research reports. | Python production analysis, stage views, regional planting guidance, and saved assessments were connected to a web interface. |
| 22 September | Hourly access was limited to selected stored cells. | The API began reading the completed land-hourly archive for other supported cells. |
| 22 to 23 September | Location selection and report inspection were less complete. | Map selection, local place search, keyboard controls, phone layouts, and HTML/JSON exports were improved. |
| 24 September | Global calendar assumptions needed review. | A source review identified separate crop systems and major parameter limits. This was research, not a new global cultivar model. |
| 28 September | Fixed day offsets gave every complete calendar the same harvest duration. | Version 3 uses accumulated heat after budbreak. Warm and cool conditions can change stage duration. |
| 28 September | Tropical or evergreen sites could lack a usable window. | A scan now compares 24 possible cycle start dates. It provides a management scenario when the winter calendar does not apply. |
| 28 September | Calendar outputs had limited regional comparison. | A 53-site literature comparison and 71 saved locations were added. |
| 30 September | Bud-stage freezing and a defined pollination gap were absent from the primary model. | Bud-freeze checks, temperature-based honey bee flight hours, and a pollination-gap event were added. |
| 30 September | Model formulas were difficult to review without code. | An HTML formula guide with reviewer notes was added. |
| 2 October | Some islands failed the whole request when hourly data were absent. | Supported daily weather can now remain visible while crop analysis is unavailable. Input and coastal-location handling also improved. |
| 5 October | Regional report findings were separate research files. | A Regional evidence tab now shows reviewed claims with sources and limits. |
| 5 October | Empty scan results showed bare "Unavailable" dates and misleading "None recurring" text. | Overview and Season views now explain why a window is absent. |
| 5 October | Cool-climate settings and scan-accounting changes required approval. | The user reported Paul's approval. The approval is recorded. These changes are not implemented yet. |

Some earlier statements were corrected during review.

- The version 3 calendar did change Waldo's flowering dates.
- A hypothetical winter calendar is not the main result where the scan applies.
- A window at every saved location does not establish global coverage or accuracy.
- Better wording for an empty calendar does not fix the underlying crop model.

## 3. The three types of information

### 3.1 Historical weather

The main assessment period is 2011 through 2025. Earlier data from 2010 support calculations for the first winter.

The app uses daily and hourly weather estimates from existing archives. It does not collect new weather when you move the pin.

The main weather grid is 0.5 degrees latitude by 0.625 degrees longitude. Solar data use a 1 degree grid.

A grid cell covers a large area. Two nearby pins can use the same weather values.

A mountain, valley, coast, and farm can have different conditions inside one cell. The app does not correct these local differences.

### 3.2 Modelled crop stages

A model is a set of calculation rules.

The crop model uses weather and assumed crop settings to calculate dates. It does not observe buds, flowers, or fruit.

A modelled flowering date is therefore an estimate under stated assumptions. It is not a field record.

### 3.3 Regional reports

The Regional evidence tab contains reviewed statements from International Blueberry Organization reports.

These statements describe events, production practices, harvest periods, and resource constraints.

A regional freeze report does not prove that your selected field froze. A regional harvest period does not provide your cultivar's calendar.

**Agreement between the model and a report supports further investigation. It does not validate a cultivar model by itself.**

## 4. How to use the app

### Procedure: assess a location

1. Start the connected app through the documented preview service.
2. Search for a place, select a saved location, or enter coordinates.
3. Check the pin coordinates. Do not use the nearby town name as proof of the exact location.
4. Select **Analyze location**.
5. Check the result location and the data-availability labels.
6. Read the Production window card before you interpret crop-stage risks.
7. Open **Season & exposures** to inspect individual years and assumptions.
8. Open **Methods & data** to check the source cell, coverage, and exclusion reasons.
9. Read **Regional evidence** as separate context.
10. Save the report if you need a record of the result.

Moving the pin does not immediately replace the old assessment. The app displays a notice until you run the new analysis.

A saved location uses a saved result. A new coordinate uses the private API, which is the server program that calculates results.

### The nearby place name

"Near Yakima" is a map label. It does not mean the pin is at Yakima city or a blueberry farm.

The place reference can name a settlement within 100 km. Always check coordinates and the source-cell information.

### Growing setup

The interface offers open field or tunnel, with ground or pots.

These choices change explanatory notes. They do not change outdoor temperatures, rainfall, stage dates, or risk frequencies.

Do not interpret the tunnel option as a calculation of frost protection or rain exclusion.

### Save report and JSON

**Save report** produces a separate HTML report. You can open it without the running analysis server.

The report includes the selected views and expanded explanations. The map itself is not included.

**JSON** saves the structured calculation result and metadata. It is intended for technical review or reuse.

Both exports include all matched regional records, even when the visible tab has a category filter.

## 5. The four Overview cards

### 5.1 Production system

The app classifies the historical climate with fixed rules.

| Label | Meaning in this app | What it does not prove |
|---|---|---|
| Deciduous | The climate meets the model's cold-season classification rule. | That a particular cultivar loses its leaves, grows well, or completes harvest. |
| Evergreen | The climate meets low-chill, warm-winter, and low-freezing rules. | That a grower can maintain any cultivar in an evergreen system. |
| Semi-evergreen | The climate falls between the other classifications under these rules. | A measured plant response. |
| No two-thirds majority | No class reaches the required share of valid years. | No production system is possible. |
| Unclassified or Not assessed | The model cannot supply this classification. | The site is unsuitable. |

The main card uses the multi-feature classification. The detailed view also shows a chill-only classification.

At least 300 production chill hours gives a Deciduous year under the current multi-feature rule.

An Evergreen year needs fewer than 100 chill hours and additional warm-winter and low-freezing conditions. Other complete cases are Semi-evergreen.

The summary class needs at least two-thirds of valid years. With 15 valid years, this means at least 10 years.

"Deciduous in 15 of 15 winters" means all 15 weather years received that class. It is not a 100% crop-success probability.

### 5.2 Production window

This card gives one of two types of result:

- Typical flowering and harvest dates from the chill-triggered calendar.
- Flowering and harvest months from the managed-cycle scan.

A date range and a scan month range have different meanings. Section 7 explains the difference.

### 5.3 Top risks

This card lists recurring weather events under the applicable calculation.

For a chill-triggered calendar, it uses each winter's own modelled crop stages.

For a primary managed-cycle scan, it summarizes selected start-date scenarios.

The lower winter-risk cards and the scan can therefore show different results. Check which calculation each section describes.

The ranking measures frequency, not damage severity. A frequent rain event can rank above a less frequent but destructive freeze.

### 5.4 Planting guidance

This card concerns the establishment of nursery plants. It does not describe budbreak, flowering, or harvest on mature plants.

Current guidance covers selected registered locations in Florida, Georgia, and Santa Catarina.

An arbitrary pin can lack planting guidance even inside one of those regions. Place-name matching does not automatically assign planting guidance.

"No regional window" means the app has no supported planting recommendation for this result. It does not mean planting is impossible.

## 6. The six tabs

| Tab | Information shown | How to use it |
|---|---|---|
| Overview | System class, crop window, top risks, planting guidance, and additional weather measures. | Read this first. Then check the basis of each result. |
| Season & exposures | Stage timeline, individual winters, weather measures by stage, and cycle-start scan. | Check when exposure occurs and which years support the result. |
| Climate history | Annual and monthly weather summaries. | Examine weather independently of a successful crop calendar. |
| Soil & setup | Available soil estimates and growing-setup notes. | Identify information that needs local soil and management checks. |
| Regional evidence | Report statements, dates, crop context, sources, and limitations. | Compare regional experience with the model without treating either as field validation. |
| Methods & data | Definitions, source cells, coverage, excluded risks, versions, and analysis identity. | Investigate a missing or unexpected result. |

### 6.1 Season & exposures

The timeline separates winter chill, bud development, flowering, fruit development, harvest, and whole-cycle context.

Stage colours identify stages. They do not indicate safety.

The typical timeline combines results across valid years. Select a winter to inspect that year's calculation.

The displayed spread of dates shows variation between modelled years. It is not a confidence interval for the true flowering date.

### 6.2 Climate history

The six main measures are:

- Reference chill hours.
- Cold days with daily minimum temperature below 0 °C.
- Annual rainfall.
- Hot days with daily maximum temperature at least 35 °C.
- The longest within-year dry run, using daily rainfall below 1 mm.
- Mean daily solar energy.

Annual rainfall is not harvest rainfall. Cold days are not necessarily flowering-freeze days.

Monthly charts require complete source periods. A date row can exist while one variable is missing or rejected.

**Important: there are two chill-hour definitions in the app.**

| Display | Temperature rule | Counting period |
|---|---|---|
| Production model | Temperature below 7.2 °C, including below-zero temperatures. | November through April in the north; April through September in the south. |
| Climate history reference chill | Temperature from 0 through 7.2 °C. | November through February in the north; May through August in the south. |

These values can differ without a software error. Their thresholds and periods differ.

The production rule is inherited from the earlier workflow. It is not interchangeable with every published cultivar chill requirement.

### 6.3 Soil & setup

The available properties are soil pH, organic carbon, sand, silt, and clay.

The three depth bands are 0 to 5 cm, 5 to 15 cm, and 15 to 30 cm.

Each property and depth has a mean estimate and two uncertainty estimates. Thus, 5 properties × 3 depths × 3 statistics equals 45 records.

"Soil 0/45 records" means no such records are attached to this pin. It does not mean zero soil quality.

"Soil 45/45 records" means the records exist. It does not mean that a field soil test is complete or that the soil is suitable.

The app does not calculate a soil suitability score. Local drainage, irrigation water, and root-zone conditions still need assessment.

### 6.4 Regional evidence

The library contains 91 records from the complete IBO 2023, 2025, and 2026 reports.

It covers 51 geographic scopes across 23 countries. It is not an exhaustive global library.

Cards distinguish:

- Reported events.
- Reported practices.
- Reported constraints.

Filters group harvest, management, weather, and resource information.

Read the geographic scope and crop context before you use a claim. Several reports repeating one event are not several independent events.

A 2026 report can describe an event beyond the weather baseline. The app labels known date ranges outside that baseline.

No matching report means no reviewed match in this library. It does not mean no crop, no weather risk, or no published evidence anywhere.

## 7. How the calendar works

### 7.1 Terms used in the calculation

**Budbreak** is the opening of buds. In this app, the date is calculated rather than observed.

**Growing degree-days**, or GDD, measure accumulated heat above a selected base temperature.

A daily mean of 17 °C supplies 10 degree-days above a 7 °C base. A daily mean below 7 °C supplies zero.

For stages after budbreak, the model caps daily mean temperature at 30 °C before calculating GDD.

These degree-days are not calendar days.

### 7.2 The chill-triggered calendar

The current sequence is:

1. Start the fixed winter counting period.
2. Find when accumulated chill reaches 100 hours.
3. Accumulate 150 GDD above 7 °C from the chill date to estimate budbreak.
4. Accumulate heat after budbreak to estimate flowering.
5. Accumulate heat after flowering starts to estimate harvest.

| Endpoint | Current heat requirement | Starting point |
|---|---:|---|
| Budbreak | 150 GDD | Date the 100-hour chill requirement is reached |
| Flowering start | 85 GDD | Budbreak |
| Flowering end | 375 GDD | Budbreak |
| Harvest start | 633 GDD | Flowering start |
| Harvest end | 1,242 GDD | Flowering start |

These are current assumptions, not universal blueberry requirements.

The harvest-end requirement is especially uncertain. It was derived from an older Waldo calendar, not fitted directly to observed harvest-end dates.

The budbreak search stops 450 days after the winter start. Later stage searches have a 300-day limit from their relevant anchor.

A search limit prevents indefinite calculation. It is not a biological deadline or a proven crop-death threshold.

**The current date calculation requires the full set of stage endpoints.** If a later endpoint fails, both flowering and harvest windows can be absent.

Thus, blank flowering dates do not necessarily mean that the model could not reach flowering start. They can result from a later-stage failure.

### 7.3 When the winter calendar becomes the main result

All three conditions must hold:

1. Absolute latitude is at least 23.44 degrees, outside the tropics.
2. The model classification is known and is not Evergreen.
3. At least 12 of the 15 winters have a calculated calendar through harvest.

A calendar can exist while an individual rain or disease measure is unavailable. Calendar dates and complete risk evidence are separate checks.

Typical dates are medians across the calculated years. They are not a prediction for next season.

A result marked tentative has additional classification uncertainty.

### 7.4 The managed-cycle scan

The scan asks a different question:

> If a crop cycle began on this date, what weather would overlap its calculated stages?

It tries the 1st and 15th of every month. This gives 24 possible budbreak dates.

It applies each start date to the historical years. It follows the same temperature-based stage rules.

The scan does not prove that pruning or another treatment can cause budbreak on the chosen date.

A start needs enough complete evidence for all required measures, normally at least 12 cycles.

The current rule excludes starts with recurring bud-freeze, flowering-freeze, or fruit-frost classifications at the 50% threshold.

Among the remaining starts, the scan retains weather trade-offs and close alternatives. It does not calculate one weighted suitability score.

The flowering and harvest months combine the months reached by the selected starts.

For example, August through December does not mean every plant bears fruit continuously for five months. Different start scenarios can contribute different months.

"Weather does not separate start dates" means all starts remain selected under the comparison rule. It does not mean there is no risk.

The scan can appear at a cold deciduous location because its winter calendar failed. That label does not establish an evergreen production system there.

### 7.5 Known scan-accounting problem

Current code handles two failure types differently:

- A computed cycle with flowering over 66 days, or first harvest over 150 days after flowering starts, counts as stalled.
- A cycle that cannot reach a stage before the search limit has no stage result. The scan does not add it to the stalled count.

The scan also adds existing stalled cases to the freeze-related exclusion families.

Therefore, those scan frequencies are not always counts of observed threshold-crossing freezes alone.

Paul approved correction of this accounting. The correction is not implemented in the current app.

Until then, inspect the complete and stalled counts. Do not interpret the scan's "Recurring crop loss" label as measured crop damage.

## 8. Minimum data requirements

There is no single minimum dataset for every output. A daily weather summary needs less information than a defensible cultivar forecast.

### 8.1 What you enter now

For an existing saved result, select the saved location.

For a new result, enter a valid land coordinate and use the connected analysis service.

You do not need to upload 15 years of weather. The server reads the installed archive.

The current interface does not ask for cultivar-specific stage settings. It uses the default model assumptions.

### 8.2 What the current software needs

| Requested output | Minimum usable evidence or conditions |
|---|---|
| Daily climate summary | Complete daily records for each reported variable and period. Hourly weather is not required for daily-only measures. |
| One modelled winter calendar | Complete hourly temperatures for the six-month chill window; the chill requirement must be reached. Daily mean temperatures must remain usable through every required stage endpoint. |
| Main chill-triggered calendar | At least 12 calculated calendars out of 15, plus the latitude and classification conditions in section 7.3. |
| Stage freeze, rain, heat, or dry-spell measure | Valid stage dates and complete relevant daily variables across that stage. |
| Disease-weather measure | Valid stage dates, hourly temperature and dewpoint for the wetness model, and the required complete evidence windows. |
| Honey bee temperature measure | Valid flowering dates, longitude, and complete required daytime hourly temperatures. |
| Ranked winter risk | A defined event, applicable calculation, at least 12 valid winters, and event frequency of at least 50%. |
| Selected managed-cycle window | At least one start passes the scan's complete-evidence, exclusion, and comparison rules. Daily-only fallback does not run production analysis. |
| Planting guide | An applicable registered region and source-supported establishment guidance. |
| Soil section | Stored soil records for the selected coordinates. |
| Regional evidence | A loaded report library and a supported country/region boundary match. A crop calendar is not required. |

Risk variables include daily minimum and maximum temperature, rainfall, and other relevant weather fields.

Missing humidity can prevent disease assessment without preventing a temperature-based calendar. Missing soil does not prevent a crop calendar.

The current production adapter requires the installed hourly series. It does not synthesize hourly weather from daily temperatures.

Twelve winters is the current reporting policy. It is not a universal minimum for all phenology models or a guarantee of accuracy.

### 8.3 What a scientifically defensible cultivar calendar needs

The current software can calculate dates without knowing the real cultivar. That does not make those dates reliable for that cultivar.

A stronger model needs:

- Crop type and cultivar identity.
- Site coordinates and relevant field conditions.
- Production system and plant age or maturity context.
- Relevant pruning, dormancy-breaking, or protection treatments.
- Weather that represents the site.
- Clearly defined observed stages and dates.
- Several site-years where possible.
- Observations reserved for an independent accuracy check.

Examples of different endpoints include first bloom, 50% bloom, first ripe fruit, and first commercial pick. Do not mix them without justification.

No universal number of trial years guarantees a valid model. The required evidence depends on the crop, model, environments, and expected accuracy.

### 8.4 What a forecast for the coming season would need

A current-season forecast would additionally need:

- Current-season weather up to the calculation date.
- Current crop stage or a justified season start.
- Current management information.
- Future weather scenarios or forecasts.
- A validated cultivar model and an uncertainty estimate.

The app does not currently provide this forecast service. A historical median must not be labelled as next year's predicted date.

## 9. How to read weather risks

### 9.1 Frequency is not damage

Suppose harvest heavy rain occurred in 14 of 15 valid winters.

The frequency is 14 divided by 15, approximately 93%.

This means the defined rain event occurred during modelled harvest in those winters.

It does not mean:

- 93% of fruit was lost.
- 93% of harvest days were wet.
- There is a validated 93% loss probability next year.

One qualifying day can make a winter an event winter.

The scan also shows percentages of affected stage days. Always read the denominator: days, cycles, or winters.

### 9.2 Main event definitions

| Event | Current calculation | Limit |
|---|---|---|
| Chill shortfall | Winter chill below the assumed 100 hours where that requirement applies. | Not a universal cultivar requirement. |
| Bud-stage freeze | Daily minimum at or below −6.7 °C early, then −3.9 °C after half the modelled heat to flowering. | Bud stage is estimated; plant damage is not measured. |
| Flowering freeze | At least one flowering day at or below −2.2 °C. | Not a universal flower-kill temperature. |
| Fruit-stage frost | At least one fruit-development day at or below 0 °C. | Exposure is not confirmed injury. |
| Severe fruit-stage heat | At least one fruit-development day at or above 35 °C. | Air temperature is not fruit temperature. The separate heat measure uses 32 °C. |
| Harvest heavy rain | At least one harvest day with 10 mm or more rain. | Does not measure fruit cracking or marketable yield. |
| Disease-favourable weather | At least one day reaches a high infection-model index during the relevant stages. | Grid humidity estimates wetness. Pathogen presence and disease incidence are not measured. |
| Pollination gap | At least four flowering days in succession with no qualifying honey bee flight hour. | This is a temperature screen, not observed pollination failure. |

Honey bee flight hours use temperatures of at least 12.8 °C during the model's daytime interval, 09:00 to 17:00 local solar time.

Wind, rain, and cloud do not enter this hourly flight estimate. Other pollinators can behave differently.

The disease model uses anthracnose and Botrytis equations. Moderate-risk days and high-risk event days have different thresholds.

The app retains some older daily disease and cold/wet measures for comparison. Read the active method and definition before comparing numbers.

### 9.3 Other useful measures

- Warm midwinter exposure counts hours above 21 °C. It does not calculate chill cancellation.
- Daily-only fallback counts days whose maximum exceeds 21 °C. Days cannot be compared directly with hours.
- A dry spell counts successive days with less than 1 mm rain. It does not measure root-zone water deficit.
- VPD describes atmospheric drying demand. It is not a measurement of plant stress.
- Rain totals, stage minimum temperatures, and solar energy add context. They are not combined into a suitability score.

### 9.4 Uncertainty and missing years

A valid winter has the evidence required for the particular measure.

If only 12 of 15 winters are valid, the frequency denominator is 12. Missing years are not safe years.

The 95% Wilson interval describes uncertainty due to the number of observed event years. It does not include all model or weather-grid error.

Rank 1 means highest qualifying recurrence. Tied frequencies share a rank.

## 10. Your Near Yakima screenshot

This interpretation uses the earlier verified response for 46.738354, −121.456108. It is not a new live-server run.

### What each item means

| Screenshot item | Meaning |
|---|---|
| Near Yakima | Nearby settlement label. The coordinate is not Yakima city. |
| 2011 through 2025 | Historical years used for the assessment. |
| Daily weather: 5,479 rows | There is one row per day in this 15-year span. Row count alone does not prove every variable is valid. |
| Hourly analysis available | The hourly production analysis could run. It does not promise a complete crop calendar. |
| Managed-cycle scenario | The winter calendar did not qualify, so the alternative start-date scan is shown. |
| Deciduous in 15 of 15 winters | Every winter met the cold-climate classification rule. |
| Mean 4,095 chill hours | Mean production-model chill count under its six-month, below-7.2 °C rule. Below-zero hours count too. |
| 77.8 chill portions | An alternative Dynamic Model chill measure. It does not currently trigger budbreak or classification. |
| Flowering and harvest unavailable | The model did not produce a qualifying complete calendar or selected scan window. |
| Planting guide unavailable | No applicable registered planting guidance is attached. This is independent of calendar failure. |
| Soil 0/45 records | No stored soil records are attached to this point. This did not cause the calendar failure. |
| Open field + ground | The outdoor assessment context. It is not a recommendation to establish a farm there. |

### Why the calendar failed

The hourly weather cell is centred at 46.5, −121.25. Its centre is about 31 km from the pin.

The earlier analysis found:

1. The assumed chill requirement was reached in early November.
2. Calculated budbreak occurred between 26 May and 7 July across the years.
3. In 14 winters, a later stage did not reach its heat requirement within the stage-search limit.
4. The remaining winter required weather beyond the archive end at 1 January 2026.
5. Zero winters produced a complete chill-triggered calendar.
6. None of the 24 scan start dates produced a complete cycle.

More chill does not supply more summer heat. A cold-classification result and a failed crop calendar can therefore occur together.

These results concern this grid cell under the current model. They do not prove that every cultivar cannot fruit at the actual pin.

### What was wrong with the old display

The screenshot said "None recurring" when no favourable start existed. That was misleading.

The updated Overview shows a reason for the absent window. Top risks shows "Not assessed" in this case.

The underlying weather and crop parameters were not changed by that display fix.

### A wording limit that remains

The current title "No complete crop cycle" can also appear when a few cycles complete but too few qualify.

For example, the earlier Naantali check found at most two complete cycles for a start date. The required minimum is 12.

Read the explanation below the title. Do not treat the title alone as proof that zero cycles completed.

The general empty-window explanation can also combine different heat-search failures. Budbreak uses a 450-day search, while later stages use 300-day searches.

The exact per-winter status is more precise than a short summary label. These wording limits remain in the current code.

## 11. Missing results and error messages

**An empty value is not automatically a software error. It is never automatically zero.**

### 11.1 Missing or limited results

| Message or situation | Meaning | What to do |
|---|---|---|
| Unavailable | No usable value is supplied for that field. Several causes are possible. | Read its reason and inspect Methods & data. |
| Hourly analysis unavailable | The required hourly series is absent or unavailable. | Use supported daily climate measures. Do not infer a crop calendar. |
| No supported calendar | Calendar conditions or inputs do not qualify. | Inspect winter status and the model assumptions. |
| Chill requirement not reached | Available temperatures did not meet the selected chill threshold. | Check crop suitability of the threshold. Do not fill in dates manually. |
| Heat requirement not reached | The model did not reach a stage within its search limit. | Check crop settings and whether the grid represents the field. |
| Incomplete stage dates | Needed temperature data are missing, including beyond the archive end. | Identify the missing date. Separate archive limits from cold-limited development. |
| No favourable start | No scan candidate survives the evidence and selection rules. | Inspect complete cycles, stalled cycles, and recurring exclusions. |
| Not assessed or Not ranked | Evidence or applicability does not support that result. | Do not read this as low risk. |
| None ranked | No winter-risk assessment passes all reporting gates. | Read the excluded assessments. A rare severe event may still matter. |
| None recurring | No defined event meets the recurrence gate among the selected starts. | Confirm that selected starts exist. This is not a safety guarantee. |
| Hypothetical | Dates or exposures belong to a scenario that does not apply as the main calendar. | Use only as a labelled comparison. |
| Suspect rainfall | Source screening flagged rainfall as unsuitable for dependent calculations. | Do not replace the missing rainfall-derived value with zero. |
| No regional evidence | The reviewed library has no supported match, or matching failed. | Read whether the cause is no records, missing boundaries, or library failure. |
| Soil unavailable | No applicable stored soil records. | Obtain local soil information separately. |
| Planting guide unavailable | No applicable planting guidance in the current registry. | Request local establishment guidance. |
| A displayed zero | The calculation returned zero in its valid source window. | Check the source and limitations. Grid zero does not establish field safety. |

A failed disease measure does not mean there was no disease.

A failed calendar does not remove the value of the available daily weather history.

### 11.2 Service and software errors

| Message or situation | Meaning | What to do |
|---|---|---|
| The page does not open | The local preview may be stopped. | Start it through the UI runbook. |
| Archive disconnected or unavailable | The local proxy, SSH tunnel, or server API is unavailable. | Check those services. Saved assessments can still work if the page is served. |
| Another analysis is running | The private API handles one calculation at a time. | Wait, then retry. |
| Invalid coordinates, HTTP 400 | The request has invalid or missing input. | Correct latitude and longitude. |
| Unsupported location, HTTP 422 | The land check does not accept the point. | Check the pin against mapped land. A coastal map error is possible. |
| Analysis failed, HTTP 500 | The server could not complete the request. | Preserve the coordinate and error. Inspect server logs; do not infer a biological cause. |
| Older analysis method | The interface and saved/server result versions do not match. | Update the matching software and result files together. |
| Library or map reference failed | A browser resource could not load or its identity did not match. | Reload or investigate the resource. Do not substitute a nearby region's claims. |
| Old location remains on screen | A new pin is selected but not analysed, or a new request failed. | Check the displayed assessment name and draft-location notice. |
| Request cancelled | The browser stopped waiting for that request. | The server can still be busy briefly. |

Do not restart completed weather downloads to fix a UI connection error.

## 12. How breeders can use the results

Use the app to select questions and trials. Do not use it as an automatic cultivar recommendation.

### Example: recurring flowering cold

At the saved Burgaw location, the current winter calculation reports flowering-freeze exposure in 10 of 15 valid winters.

Regional reports also describe spring freezes and a shift away from early-blooming cultivars.

A useful research question is:

> Can later flowering reduce cold exposure without an unacceptable change in harvest timing?

That is a hypothesis to test. The app has not measured the answer for a named cultivar.

The scan can show weather trade-offs for shifted start dates. It cannot prove that a cultivar can achieve those dates.

### Example: harvest rain

The saved Waldo result has a typical harvest from 4 April to 12 May.

It reports heavy rain during modelled harvest in 14 of 15 winters.

This supports examination of rain-related fruit-quality problems in field trials.

It does not demonstrate genetic resistance, fruit cracking, or loss in any particular variety.

### Example: management changes

Peru reports describe pruning decisions that changed the season start.

A temperature-only calendar cannot identify an unrecorded pruning decision.

Use this evidence to request management dates before fitting a model to observed harvest shifts.

### Read agreement and disagreement correctly

- Model and report agree: a useful reason to investigate that mechanism.
- Model only: inspect local weather, crop assumptions, and report coverage.
- Report only: inspect event dates, management, crop type, and the model's measured variables.
- Neither provides evidence: do not conclude there is no risk.

Repeated industry accounts are not independent field validation. An empty report category is not a negative observation.

## 13. Known limits and approved work

### 13.1 Approved, but not implemented

Paul's approval covers progress on these two items:

1. Correct scan accounting for missing weather, thermal non-completion, and freeze exposure.
2. Research and implement justified cool-climate crop settings.

The app still uses the previous rules. No new coefficients were introduced by the approval.

The intended blueberry type must be explicit. Northern highbush, half-high, lowbush, southern highbush, and rabbiteye are not one interchangeable model.

Maine, Quebec, or Finland must not automatically receive northern-highbush settings based on location alone.

### 13.2 Other remaining work

- Validate stage dates with cultivar-specific field observations.
- Separate model error from weather-grid bias, especially near mountains and coasts.
- Expand planting guidance for arbitrary pins where sources support it.
- Resolve soil-data source failures without repeating completed downloads.
- Decide whether to acquire the separately identified island hourly gaps.
- Improve the cold-climate classification rule, which can label very cold or polar locations Deciduous without establishing suitability.
- Test more browsers and operational failure cases.
- Provide durable analysis jobs, authentication, and a deployment plan for broader use.
- Build the proposed breeder brief only as a separate implementation. It is not present today.

The app must retain an honest unsupported result where evidence is insufficient. The goal is not to make every map point show a calendar.

### 13.3 Useful information from the breeding team

The team can help by providing:

- Priority crops and cultivar names.
- Priority trial locations.
- Open-field, protected, deciduous, evergreen, or lowbush management details.
- Existing records of budbreak, bloom, ripening, and harvest.
- Original definitions of each recorded stage.
- Treatment and pruning dates where relevant.

Original spreadsheets are acceptable. Private breeding records must not be published with project code.

This information supports calibration and validation. It is not needed to begin the scan-accounting correction.

## 14. What has been checked

This guide distinguishes software checks from scientific validation.

### Existing recorded checks

- The last recorded full server suite passed 140 tests on 2 October 2026.
- Earlier browser checks covered saved and live locations, errors, mobile layouts, and exports.
- The regional-evidence change preserved the weather results in all 71 saved assessments.
- The no-window explanation was checked on the reported pin, Naantali, Lynden, Arcadia, Waldo, and a modified freeze-case payload.
- A 53-site benchmark compares the model with published regional production information.
- Limited station comparisons found weather-grid bias and missed cold events.

These checks do not establish cultivar prediction accuracy.

A correct screen can display a scientifically uncertain model result.

### Checks for this guide

The current code, project records, and saved JSON results were inspected.

A local script read all 71 saved assessments. Each had an applicable winter calendar or a selected managed-cycle window.

The script also checked the Waldo and Burgaw risk counts and the regional-library record counts.

The UI and private API were not started. The weather model was not changed. Earlier live-pin results are identified as earlier evidence.

This is a simplified-English guide, not a certified ASD-STE100 compliance report.

## 15. Terms and units

| Term | Meaning |
|---|---|
| Assessment | One result for a selected location and analysis method. |
| Baseline | The historical period used for comparison, mainly 2011 through 2025 here. |
| Calendar | Estimated crop-stage dates under a selected model. |
| Chill hour | One hour that meets a specified temperature rule. Always check that rule and its counting period. |
| Chill portion | A unit from the Dynamic Model of chill accumulation. It is not a fixed number of chill hours. |
| Cultivar | A named cultivated variety. |
| Cycle | One modelled sequence from its start through harvest. |
| Dewpoint | The temperature at which air becomes saturated when cooled. The app uses it to estimate humidity. |
| Exposure | Weather that occurred during a specified period or modelled stage. |
| Favourable | Selected by the app's comparison rule. It does not mean safe, profitable, or biologically feasible. |
| Forecast | A statement about future conditions. The current app does not provide a crop forecast service. |
| GDD | Growing degree-days, a sum of temperature above a selected base. |
| Grid cell | One area represented by a weather dataset value. It is not a farm boundary. |
| Harvest | Here, a modelled picking period. Source reports can use different endpoints. |
| Horizon | A limit on how far a calculation searches for a stage. |
| Median | The middle value of an ordered set. It is not necessarily the date observed in any one field year. |
| Mean | The arithmetic average. |
| p10 and p90 | Values near the lower and upper ends of the middle 80% of the calculated distribution. |
| Phenology | The timing of plant development stages. |
| Provisional | Implemented with assumptions that still need confirmation. |
| Recurrence | How often a defined event occurs among valid periods. |
| RH | Relative humidity, expressed as a percentage. |
| Scenario | A result calculated under stated assumptions, not a claim that those assumptions occur at the field. |
| Snapshot | A saved assessment that the browser can load without a new archive calculation. |
| Source-checked | A statement was checked against its cited document. It was not necessarily checked against field observations. |
| UTC | The common time reference used for most archive dates and hours. |
| Valid winter | A winter with the inputs required for the specific calculation. Different measures can have different valid-year counts. |
| VPD | Vapour pressure deficit, a measure of atmospheric drying demand. |
| °C | Degrees Celsius. |
| °C·day | The unit used for accumulated growing degree-days. |
| mm | Millimetres of rainfall. |
| kPa | Kilopascals, used for VPD. |
| MJ/m²/day | Solar energy per square metre per day. |
| Analysis ID | An identifier for a calculation result. It does not establish scientific correctness. |
| Checksum | A value used to check file identity or detect changes. It is not a data-quality certificate. |

## 16. Project records and technical details

The primary model is `stage_thermal_v3`.

The production method is `open-field-production-v3`. The API result method is `location-evidence-v5`.

These identifiers are software versions. They are not accuracy grades.

Use these files for more detail:

- [Project handover](../HANDOVER.md): current status, decisions, and unresolved work.
- [Progress log](PROGRESS_LOG.md): dated changes and recorded verification.
- [UI runbook](UI_RUNBOOK.md): start and stop procedures and operating limits.
- [UI design contract](UI_IMPLEMENTATION_PLAN.md): intended interface behaviour.
- [Production methods](weather/production/README.md): formulas, parameter sources, and model limits.
- [Breeder formula review](weather/production/model_formulas_for_breeder_review.html): detailed formula explanation and review notes.
- [Global phenology review](weather/GLOBAL_PHENOLOGY_REVIEW.md): evidence for crop-specific modelling and observed-stage definitions.
- [Literature benchmark](weather/benchmark/benchmark.html): comparison with published regional practice, not farm-level accuracy.
- [IBO integration review](research/2026-10-05/ibo_integration_review.md): report coverage, interpretation, and integration decisions.
- [Calendar and risk code](../pipelines/weather/production.py): calculation rules used for this guide.
- [Location API code](../pipelines/weather/location_api.py): data requirements, fallback behaviour, and server errors.
- [Overview display code](../dist/app.js): card labels and empty-result explanations.

**Read every result as a combination of weather evidence, crop assumptions, and known limits. A number on the screen is not a recommendation by itself.**
