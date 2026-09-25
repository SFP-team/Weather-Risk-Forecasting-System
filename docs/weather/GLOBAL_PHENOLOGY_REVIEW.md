# Blueberry budbreak, flowering and harvest windows: global evidence review

Date: 2026-09-24. Research and parameter recommendations only. No live model, snapshots, weather archive or risk results changed.

## Conclusions

**Location supplies weather, not a unique blueberry calendar.** A defensible calendar must also identify the cultivar or explicitly declared cultivar scenario, production regime, crop age, management history and developmental endpoint. A country-level harvest season is not a field prediction.

The present model needs a change in structure, not just a different universal harvest offset. The recommended direction is:

1. Separate flower-bud initiation, floral budbreak, vegetative budbreak, flowering progression, fruit ripening and commercial picking.
2. Model deciduous, evergreen/management-anchored, forced/protected and lowbush production separately.
3. Fit cultivar-specific bloom and fruit-development responses with their original thermal units, weather convention and start date. Compare chilling models rather than declaring a universal winner.
4. Estimate within-season stage windows separately from between-year timing uncertainty.
5. Use regional observations as calibration and checks, not as country-wide hard-coded dates.
6. Evaluate favorable weather only within biologically feasible cultivar/management scenarios. Do not shift a calendar until its risk score looks better.
7. Preserve an explicit unsupported or exploratory result when genotype, management or validation is missing.

A targeted review cannot establish a calibrated calendar for every place on Earth. This review combines primary papers, public cultivar trials, university extension, government monitoring and a separately identified set of secondary/industry leads. Full-text evidence, abstracts and proposals are distinguished below. Search-engine summaries were discovery aids, not accepted as parameter authority.

**Current season versus historical baseline:** the project archive contains 2010 padding and a 2011–2025 baseline. This report considers literature available by September 2026, but it does not compute a 2026 or 2026/27 forecast. Such a forecast needs current-season weather and observed crop stage or management dates, neither supplied by a historical map pin alone.

## 1. What the current program actually calculates

In `pipelines/weather/production.py`, `stage_risks_v2` inherits the following phenology from `legacy_paul_v1`:

| Component | Current implementation | Consequence |
|---|---|---|
| Season anchor | 1 November of previous year north; 1 April south | Hemisphere is being used as a production-cycle selector |
| Chilling window | Six months; hours with T < 7.2°C, without a lower bound | Neither a universal physiological response nor interchangeable with all published chill-hour conventions |
| Chilling requirement | 50 hours | Same threshold for every genotype and location |
| Budbreak | 150°C·days above 7°C, using source daily mean from the day chill is fulfilled | One unspecified budbreak endpoint; no separate floral/vegetative states |
| Flowering | Budbreak +14 through +35 days | Fixed progression after budbreak regardless of subsequent temperature |
| Harvest | Flowering start +70 through +110 days | Fixed 40-day elapsed span, 41 inclusive calendar days |
| Fruit development exposure | Day after flowering end through day before harvest start | Treats whole-plant stages as non-overlapping even though cohorts can overlap |
| Typical dates | Quantiles of offsets from the season anchor | Climate-year spread, not demonstrated forecast accuracy or full model uncertainty |

A read-only calculation across the **18 committed snapshots, 270 site-years**, found **235 rows with computed calendars**. Every one had the same offset tuple: **14, 35, 70, 110, 40**. These include hypothetical calendars; 235 is not a count of agronomically valid crop-years. Evidence and reconstruction method: [calendar audit JSON](phenology_calendar_audit_2026-09-24.json).

This explains why moving a location can shift the entire calendar while leaving flowering and harvest duration unchanged. It also means post-budbreak weather cannot accelerate or slow the current fruit-development period. No source reviewed establishes those constants as globally valid. This is a scientific limitation, not an acquisition failure.

## 2. Define the stages before fitting parameters

The phrase “flowering bud window” can mean two different processes. Both need representation.

| Stage | What to record | What not to substitute |
|---|---|---|
| Flower-bud initiation | First meristem transition to reproductive development, normally requiring dissection or a validated developmental assessment | The date a large bud becomes visible, spring bloom, or a chilling threshold |
| Flower-bud differentiation | Progression of floral organs within the bud | A fixed period after nursery planting |
| Floral budbreak | A specified external bud stage and percentage of sampled floral buds reaching it | Vegetative leaf emergence or 50% open flowers |
| Vegetative budbreak | A specified green-tip/leaf-emergence stage and percentage | Floral budbreak; flowers can open before adequate leafing |
| Flowering | First bloom, cumulative flowers opened, currently open flowers, full bloom and petal fall, explicitly distinguished | An undefined “peak” copied between papers |
| Ripening | First blue, or 10/50/90% of fruit meeting an explicit maturity criterion | Percentage of seasonal yield already picked |
| Commercial harvest | First pick and cumulative marketable harvested mass, with picking dates and end-of-picking reason | Exports, packhouse dispatches or a biological endpoint inferred from price-driven harvest cessation |

For the platform, use separate fields such as floral-budbreak B10/B50/B90, vegetative-budbreak V10/V50/V90, flowering F10/F50/F90, ripe-fruit R10/R50/R90 and harvested-mass H10/H50/H90. These labels are a **proposed data contract**, not a claim that every source measures those exact percentages. Record the source's own stage scale and crosswalk only when justified.

UGA C1293 describes flower-bud initiation and distinguishes floral from vegetative buds. Wichura et al. provide a blueberry-specific BBCH code covering highbush types and multiple pickings. The abstract and accepted-manuscript narrative were reviewed, but the full published coding table was not transcribed; do not invent BBCH numbers from a generic crop chart. The draft's field basis was four northern-highbush cultivars at three German fields in 2021, which is not itself global validation. [S1, S2]

The contrast is not academic. The Asturias trial defines flowering start as **10% flowers open**, harvest start as **25% harvestable fruit**, and harvest end as **more than 90% already harvested**. The Georgia release tables use **50% flowering to 50% ripening**. Those are different targets. [S8, S9]

## 3. Dormancy and flower-bud initiation

### 3.1 Chilling is cultivar-, endpoint- and protocol-dependent

A reported requirement must retain all of the following: temperature weighting, accumulation start, bud type, bud stage, required percentage, forcing temperature/duration, plant age and treatment. “200 chill hours” without that information is incomplete.

**Direct examples:**

- Olmstead et al. evaluated 23 advanced SHB selections plus Emerald and Primadonna at Citra and Windsor over 2011/12 and 2012/13. Shoots were collected at 50/100/150/200 hours at **0–7°C** and evaluated for floral buds at or beyond Spiers stage 5 after forcing. In the older-plant season, none met their 70%-budbreak criterion at 50 hours; three selections did at 100 hours. Windsor received hydrogen cyanamide; Citra did not. The authors explicitly call for separate vegetative-bud evaluation. This does not establish a universal 100-, 150- or 200-hour requirement. [S3]
- In Pinhais, Paraná, at **920 m**, Schuchovski and Biasi followed four rabbiteye cultivars in **one winter, 2016**. Single-node floral cuttings were forced at 25 ±2°C. Their endpoint was **50% of green-tip buds reaching opened-bud stage**. Climax and Powderblue reached this criterion after **44 hours ≤7.2°C**; Bluegem and Delite after **134 hours**. These are assay results under that climate, not whole-orchard flowering or yield guarantees. Negative Utah accumulation for Climax illustrates the problem with transferring chilling units without validation. [S4]
- Norvell and Moore's Bluecrop/Coville experiment found **1°C and 12°C effective but less effective than 6°C**. Its abstract rejects both the original Utah model and unweighted hours below 7.2°C as accurate descriptions for those experimental plants. That study predates the Dynamic Model and cannot validate or reject it. [S5]

**Correction to the earlier project review:** “no cultivar needs less than 150 hours” is not a defensible universal floor. The opposite claim, “SHB requires 0–100 hours,” is not a defensible universal range either. The meaning of the measured endpoint matters as much as the number.

### 3.2 Compare chilling models; do not convert requirements by a ratio

Compute an explicitly defined conventional chill-hour metric for comparability and consider Dynamic Model chill portions as a second candidate. The Dynamic Model is useful for representing temperature sequences and warm interruptions, but this review did **not establish global blueberry validation or a universal cultivar requirement in chill portions**.

UF/IFAS HS216, revised September 2026, describes both models, partial chilling contribution above 45°F, warm-temperature effects and leaf-retention effects. It describes below-freezing ineffectiveness as a physiological supposition, not a complete blueberry dose-response experiment. Its cited “best Dynamic Model” comparison is in pistachio. Do not turn that into a blueberry validation claim. [S6]

Never divide a published CH requirement by a site's mean CH/CP ratio to obtain a validated CP requirement. Those metrics respond differently to temperature sequences. Estimate the requirement against the same observed developmental endpoint under each model.

Likewise, the six-month computational window is not proof of the physiological dormancy period. The UF SHB study describes typical dormancy onset in December–January under its conditions. Starting in October or November may count temperatures before the relevant state; ending in May can include post-bloom weather. Use documented local anchors, compare plausible anchors during calibration, and never choose the best anchor using the eventual test years. [S3]

### 3.3 Initiation is not spring forcing

Kovaleski et al. observed the first signs of floral transition in **early August in Emerald** and **late September in Jewel** at the same Citra site. The frequency of initiated buds became distinguishable from zero in **late August** and **early October**, respectively. Microscopic initiation, visible enlargement and spring opening are not the same date. Shoots had ceased growth by initiation; most floral buds occurred on the newest growth flush. [S7]

Short-day and temperature experiments support including photoperiod, shoot maturity and canopy history in initiation models. They do not justify a global “daylength below 12 hours” switch or using daily Tmax ≥28°C as a calibrated initiation-failure rule. A constant-temperature chamber contrast at 21 versus 28°C is not equivalent to a brief hot afternoon in an orchard. [S17]

Until a local initiation model is validated, show a source-supported regional/management interval or an observed field stage. Do not manufacture an exact initiation date from the existing chilling threshold.

## 4. Flowering models and numerical parameter audit

### 4.1 A useful published SHB model, with important restrictions

Kovaleski et al. fitted cumulative flowering curves for **Emerald and Jewel at Citra, Florida**, with **two bloom seasons, 2012 and 2013**, mature plants, freeze protection and hydrogen cyanamide applied in late December. They used a **1 January accumulation anchor** and **7°C base**. [S7]

Writing their curve as a fraction rather than a percentage:

\[
F(G)=\frac{1}{1+\exp[-(\beta_0+\beta_1G)]},\qquad
G_p=\frac{\log[p/(1-p)]-\beta_0}{\beta_1}.
\]

| Cultivar | Published intercept | Published slope | Derived F10 | Derived F50 | Derived F90 |
|---|---:|---:|---:|---:|---:|
| Emerald | −3.3740 | 0.0150 | 78.5 | 224.9 | 371.4 |
| Jewel | −4.6172 | 0.0153 | 158.2 | 301.8 | 445.4 |

The text reports F50 rounded to **225 and 302 GDD**. The other values above were independently reconstructed from the fitted equations in this task. They are **derived curve quantiles**, not independent observations, and not parameters for all “early SHB” or “mid SHB.” The reported pseudo-R² values, 0.88 and 0.91, describe model fit, not global prediction accuracy.

**Implementation caveat:** the publisher HTML prints `[(Tmax − Tmin)/2] − Tbase` in its GDD definition. That is not the usual mean-temperature expression. The apparent sign error must not be silently copied or silently declared resolved. Confirm the accumulation algorithm, treatment of negative daily units and weather series with the original methods/code/authors before importing the fitted coefficients. The logistic arithmetic is internally consistent with the stated 225/302 values, but does not resolve this temperature-formula ambiguity.

### 4.2 Northern highbush evidence is not a universal 291-GDD rule

Kirk and Isaacs studied Duke, Bluecrop, Jersey, Elliott and Liberty in southwest Michigan. Field bloom was observed at three sites in each of **2009 and 2010**, with separate chamber/greenhouse and flower-viability experiments. This is **not a 15-year bloom study**. [S10]

Cultivar-specific lower developmental estimates ranged **7.14–7.96°C**. The paper reports pooled field peak percent bloom at **291 accumulated GDD**, versus **420** in greenhouse conditions. Bases, accumulation anchors and observation definitions must accompany those values. The authors explicitly warn that these bases are relevant to **bloom prediction, not full-season development**. Reduced chilling is one possible explanation of the greenhouse difference, alongside age, containers and light; it is not an isolated universal chill-deficit penalty.

A 7°C base is therefore a reasonable **candidate for a highbush bloom-model comparison**, not an established base for every blueberry species and every stage.

### 4.3 General computational form to compare

For a clearly declared daily method, an illustrative forcing calculation is:

\[
G_y(t)=\sum_{d=a_y}^{t}\max\left(0,\frac{T_{max,d}+T_{min,d}}{2}-T_b\right).
\]

This is a **proposed candidate convention**, not a retroactive claim about every paper's implementation. Compare it with the source's actual method when reproducing a study. Source daily mean temperature, mean of extrema, sine integration and hourly integration are not identical. Degree-hours and degree-days are different units; temperature clipping or an upper threshold requires recalibration.

Compare at least:

- a local cultivar-specific calendar baseline;
- forcing-only, where rest completion is supported;
- sequential chill/forcing with observed or fitted rest completion;
- a chill-dependent forcing requirement or partially overlapping model where observations support it.

Choose complexity by held-out performance and parameter identifiability. Do not fit many free thresholds to a handful of site-years.

## 5. Harvest cannot be one offset from first flower

### 5.1 Use the endpoint actually measured

The public UGA release dossier supplies five-year means at two Georgia sites. It identifies **50% flowering** and **50% ripening** explicitly. Selected examples: [S9]

| Cultivar/selection | Site | Mean 50% flowering | Mean 50% ripening | Reported FDP, days |
|---|---|---|---|---:|
| Star | Alapaha | 3 March | 8 May | 66 |
| Star | Griffin | 13 March | 25 May | 73 |
| Camellia | Alapaha | 11 March | 15 May | 65 |
| Camellia | Griffin | 25 March | 31 May | 67 |
| TH-948 | Alapaha | 17 March | 11 May | 55 |
| TH-948 | Griffin | 28 March | 21 May | 54 |

These are source observations, not prescriptions for another farm. The same location contains materially different cultivar FDPs; the same cultivar also differs by location. The late-flowering/short-FDP TH-948 example demonstrates why delaying bloom need not delay harvest by the same amount.

NeSmith's rabbiteye abstract reports mean FDPs **75.3–93.9 days** across seven cultivars at two Georgia locations, with heat units improving ripening prediction relative to elapsed days. Full heat-unit parameters were not recovered. The SHB 2012 paper's indexed abstract reports **56.2–82.8 days**, including Emerald at 82.8; its full methods were not recovered. These ranges describe selected cultivar means, not prediction intervals or first-to-last harvest spans. [S11, S12]

The Georgia Dawn release notes that its tables estimate 50% ripening and that 10% ripe commonly occurs 7–10 days earlier in that release context. That is useful for understanding endpoint differences, not a universal conversion for all cultivars and climates. [S13]

### 5.2 Separate three clocks

1. **Development of an individual fruit/cohort:** pollination or a specified flowering stage to a specified ripeness stage.
2. **Progression of the crop:** distribution of flowering, set and ripening across shoots and plants.
3. **Picking schedule:** maturity standards, picking frequency, marketability, labor and economic stopping date.

A preferred future model predicts ripening progression, then derives an explicitly defined harvest window. A simpler first comparison can predict R50 from observed/predicted F50 plus a cultivar/site FDP distribution, but must not label that date “first harvest.” Model start and end separately or fit a cumulative harvested-mass curve once suitable records exist.

Fruit load, leaf-to-fruit balance, pollination and management can alter FDP. Williamson et al. reported a **10–14-day harvest advance after hydrogen cyanamide in a low-chill Misty experiment without changing bloom date**. That does **not** validate the earlier project rule “add 10–14 days whenever chill is below 300 hours.” No such cutoff or universal delay was established. Chemical treatment is a trial-context variable here, not application advice. [S14]

The 2025 ripening review documents asynchronous ripening, variable maturity definitions and genotype/management effects. A single duration is not a physiological constant. [S15]

### 5.3 Do not force stage windows to be disjoint

A plant can have flowers, green fruit and ripe fruit concurrently, especially under evergreen management. The current `flowering_end + 1` fruit-window start excludes fruit developing while other flowers remain open. As field data improve, use stage prevalence or overlapping cohort windows. Initially, retain explicit overlap rather than pretending every whole-plant stage begins only after the previous one ends.

## 6. Regional evidence: useful priors, not country-wide defaults

The table uses observed trials or extension summaries unless otherwise marked. Dates refer to local calendar months. Missing stage dates are deliberately not filled by inference.

| Region and production context | Reported timing or model evidence | Proper use and limitations |
|---|---|---|
| Citra, Florida, Emerald/Jewel SHB with documented treatment | Initiation late August versus early October by the study criterion; F50 225/302 GDD from 1 January | Cultivar-specific two-season flowering evidence, not harvest calibration [S7] |
| Central/south-central Florida, evergreen SHB | UF/IFAS describes an approximately March–May early market window and some cultivars beginning harvest in early March | Extension context; cultivar-dependent earlier/longer production exists. No fixed global evergreen budbreak date [S16] |
| Georgia SHB | Alapaha versus Griffin flowering/ripening means differ for the same cultivar; table above | Strong evidence against a statewide or species-wide fixed FDP [S9] |
| Georgia rabbiteye | Cultivar mean FDP 75.3–93.9 days; flowering can vary up to 24 days among years in the abstracted study | Need full methods/thermal targets before importing the model [S11] |
| Southwest Michigan NHB | Two-season field flowering model; 7.14–7.96°C bases; pooled 291-GDD peak metric | Preserve cultivar bases, stage measure and January anchor [S10] |
| Oregon/Washington NHB | OSU describes Oregon harvest from late June through September across cultivars; Washington starts early/mid-July and ends earlier; individual cultivar harvest 2–5 weeks | Regional extension and cultivar-order prior, not every-field endpoints [S18] |
| Fraser Valley, British Columbia | Provincial guide provides early-to-very-late cultivar ordering and warns Aurora can ripen too late | Relative ranking is evidence; exact dates need local records [S19] |
| Nova Scotia lowbush | White et al. use base 0°C from 1 April; first flowering ramets around 376–409 GDD, with cultivar-population and stage context | Preserve the two-year prune/crop cycle; do not substitute highbush budbreak [S20] |
| Asturias, northern Spain, 2012–2017 collection | Across 70 Vaccinium accessions, flowering duration 19–66 days and harvest duration 14–51 days; harvest-start means extend from late May into September | Weekly scoring, two plants/accession; mixture includes cranberry and non-commercial-type accessions. Filter taxa and stage definitions before calibration [S8] |
| Huelva, Spain, open-field trial 2000–2002 | Bloom late January/early February; SHB harvest second half of April to early July, rabbiteye second half of May to early August | Historical trial with named older cultivars; not today's protected-crop industry calendar [S21] |
| Liaodong/Shandong, China | Review chapter describes northern open-field harvest early July–late August and forced greenhouse Misty harvest in mid/late March | Heating and protection change the production clock; review-level evidence, not one national parameter set [S22] |
| Chao, coastal Peru, young Biloxi, 2015/16 | Early-March pruning; management aimed at April flowering; measured picking from 1 August to 15 January, with monthly yield distribution | Single-site pruning study, not a thermal model; the paper contains inconsistent 22/24-week and flower-removal-month descriptions, so use explicit methods dates and retain caveats [S23] |
| Guasca, Colombia, Biloxi/Sharpblue | Abstract describes weekly ripe-fruit harvest over 28 weeks, June–December 2014, on 20/36-month plants | Near-equatorial, establishment-age evidence; not a mature-orchard annual forecast [S24] |
| Mexico and Morocco | Public industry/government material describes changing supply windows and cultivar/protection systems | Trade availability is not budbreak/bloom truth. No defensible country-wide phenology constants established here |
| Pelotas, Rio Grande do Sul, Brazil, eight rabbiteye cultivars, 2003/04–2005/06 | Flowering generally began in August; observed picking ran December–January, with reported cultivar/season spans of 21–48 days | Primary three-season, one-site trial at 164 m; bloom start >5% open, end 90% open, first/last fully ripe picking. Not a Papanduva calibration [S28] |
| Piracicaba, São Paulo, Emerald/Jewel, 2014/15, open-sided cover and pots | Emerald flowering peak mid-June–late July and main harvest August–October, with another fruiting flush; Jewel flowering early October and harvest late October–January | Thirty three-year-old plants/cultivar at one site; 5 hours <7.2°C and 211 hours <12°C over the reported January 2014–May 2015 weather table. These are totals, not fitted requirements [S29] |
| Cerro Azul, Paraná, rabbiteye and two SHB cultivars, 2012/13–2014/15 | Flowering timing/duration varied substantially among seasons; harvest ranged from November/December into January | Three-season young-plant trial at 659 m; temperature/chilling context differed from Pelotas. Two SHB cultivars yielded poorly, so low chill alone is not suitability [S30] |
| Santa Catarina highlands/Papanduva context | Epagri provides chill/frost zoning and a synthetic average developmental schedule | Useful climate/altitude reference, **not observed cultivar phenology**. No local Papanduva cultivar-by-year calendar was established [S31] |
| Tafí del Valle, Argentina, 2,279 m, 15 cultivars, 2012–2016 | Bud swelling from September, flowering from October; cultivar harvests extended December–March | Five-season high-elevation trial; weekly fully-blue picking. Demonstrates why subtropical latitude does not imply a warm-site calendar [S32] |
| Maule, Chile, O'Neal/Brigitta, three orchards, 2012/13 | O'Neal flowering mid-August/early September; Brigitta October; reported harvest maturity later November–January depending on cultivar/site | One-season technical manual. Base-7 sums from 1 July differ by cultivar; its chill-to-bloom totals are **not chill requirements**, and stage percentages are unclear [S33] |
| Chile north-to-south production zones | Expert review reports harvest approximately October–November in northern zones, late November–January south-central, late January–early March in the south | Regional descriptive calendar, not a farm-level phenology dataset [S34] |
| Western Cape, South Africa, selections 8-42 and 9-02 at Hex River/Wolseley, 2020 | Abstract reports 8-42 flowering April–mid-October, harvest August–mid-November; 9-02 flowering peak early August at one site and late September at the other | One-season/two-site primary abstract, not a transferable seven-week adjustment; full management details require the paper [S35] |
| Corindi, northern NSW, Australia, evergreen Sharpblue | Research-program abstract describes autumn, winter and spring crops | Qualitative evergreen evidence; no verified cultivar-by-year dates recovered. Do not substitute a generic Australian summer window [S36] |
| Ruakura, New Zealand, Centra Blue rabbiteye | Breeder observations: bud swell 22 August 2007, vegetative burst 7 September, first flower 28 September, 50% flowering 3 October; 50% blue fruit 1 March 2007 and 15 February 2008 | Patent disclosure, few seasons, not independent model validation. Preserve the different years rather than subtracting unmatched flowering/ripening dates [S37] |

Northern and southern sites must be compared through their actual temperature, dormancy and management cycles. A six-month shift can be a clearly labelled scenario convention for an appropriate deciduous system; it is not a validated transfer rule. Low-latitude, protected and multi-flush systems especially violate that shortcut.

### What the southern evidence changes

- The Piracicaba paper is a direct counterexample to a single narrow SHB winter-to-spring calendar. It also corrects the previous project statement of **zero** hours below 7.2°C: its own table totals **five**. The article title/conclusions use “no-chill” more loosely than the numerical table. Its weather station was 7 km away from covered plants, so it is not a controlled proof that 211 hours below 12°C is the requirement. [S29]
- Epagri's Santa Catarina paper is a **2017 zoning analysis**, not a 2020/21 cultivar evaluation. Its assumed stage durations and frost-probability convention cannot validate the same kind of fixed offsets we want to replace. Obtain the field trials/theses behind the zoning and local observations for Papanduva. [S31]
- Southern flowering observations range from autumn in some low-chill systems to October in high-elevation deciduous systems. Neither a fixed six-month shift nor a fixed ±three-week allowance has been validated across these cases.
- South Africa's abstract concerns **2020 observations**, not two independently observed seasons. Different studies and abstracts should not be silently merged into a longer dataset. [S35]
- Australia, Morocco, several Asian regions and much of tropical production still lack accessible stage-defined, multi-year trial records in this review. The gap is data, not a reason to fill every map cell with a confident date.

## 7. Evergreen, low-latitude and forced systems

**Production regime is not determined by latitude or a chill-hour class alone.** The same cultivar can be managed differently. UF/IFAS defines evergreen production through leaf retention and management that avoids winter dormancy; it is not simply a plant accumulating fewer than a chosen number of hours. [S16]

For a management-anchored model, request:

- cultivar and plant age;
- pruning/hedging or forcing-start date, method and severity;
- leaf retention/defoliation history and crop load where available;
- open field, net, passive tunnel or heated greenhouse, including covering/heating dates;
- observed floral and vegetative stages;
- whether the crop is continuous, one flush or multiple overlapping flushes.

Predict the response conditional on these inputs. Do not assume every pruning operation resets development to the same biological state. A model trained on an established bearing block cannot automatically use planting date as the equivalent anchor.

The Peru trial is direct evidence that pruning severity redistributes harvest over months. It does not supply a validated global pruning-to-bloom coefficient. The existence of flower/fruit cohorts over many months also means the end of picking may be economic or management-driven rather than physiological. [S23]

The review found no sufficiently documented, validated global evergreen model to recommend as an immediate replacement. In unsupported evergreen cases, retain “management information required” or explicitly compare user-supplied scenarios. Do not invent a 1 November budbreak date, a fixed February bloom date, a six-month Brazilian shift or a one-hour-at-0°C dormancy trigger. No reviewed evidence validates those project-wide rules.

## 8. From usual windows to a location-specific recommendation

### 8.1 Usual windows are distributions, not single dates

For each independent season or management cycle, estimate the same endpoints with the same definition. Then summarize:

- median onset and end dates;
- between-year 10th/90th percentiles of each endpoint;
- number of eligible seasons and frequency of a stage failing to occur;
- parameter uncertainty, weather-input uncertainty and residual prediction error separately.

Do not confuse **F10/F90**, percentages within one crop's flowering progression, with **P10/P90 of F50 dates across years**. Do not label 15-year spread as a validated 80% prediction interval. Use unwrapped seasonal offsets for seasons crossing New Year; management cycles need their own cycle identifiers. Right-censor cycles extending beyond the weather archive, rather than treating them as complete.

### 8.2 Select a model by applicability, not nearest city

Proposed selection order:

1. Validate requested coordinate and weather coverage, including source-grid displacement and elevation mismatch.
2. Identify the actual production regime and cultivar, or let the user choose a clearly labelled cultivar scenario.
3. Match local/regional trials with compatible cultivar, management, stage definitions and weather conventions.
4. Evaluate whether the target climate is within the calibration domain. Country membership or similar latitude is not sufficient.
5. Fit or apply an eligible model and validate on held-out locations/years. Fall back to a regional observed range or exploratory scenario when evidence is insufficient.
6. Run the full historical sequence year by year and compute exposures inside each year's stages.

A weather grid shared by nearby pins cannot resolve slope, cold-air drainage, canopy temperature or irrigation protection. Do not fit crop parameters to absorb a known station/grid mismatch and then assume they transfer to a new weather product. Existing project station comparisons establish concerns, not universal correction coefficients.

### 8.3 “Ideal” is a constrained decision, not a biological constant

A usual harvest date tells us what happened. An ideal window asks what outcome the grower values and what cultivar/management actions can actually achieve it.

Evaluate feasible scenarios against separate outcomes: frost exposure during susceptible stages, pollination conditions and compatible bloom overlap, fruit heat exposure, harvest rainfall/disease-weather exposure, water availability, fruit quality, yield, protection capacity, labor and market objective. Keep exposure distinct from expected damage until the loss response is calibrated.

UF/IFAS describes the Florida tradeoff directly: later flowering can reduce freeze exposure, but often shifts ripening beyond a valuable early market; unheated protection does not guarantee safety. [S6] The Georgia release dossier illustrates a different lever, late flowering with short FDP, rather than simply shifting every stage by the same number of days. [S9]

The appropriate output is a set of feasible tradeoffs or Pareto-ranked scenarios, not a universal weighted suitability score. A grower-defined risk tolerance or market target is an input, not something to infer from latitude. Never shift flowering or harvest solely to reduce the reported adverse-weather count.

### 8.4 A forecast for the upcoming harvest season

A current-season forecast needs observations to date, current-season weather, a calibrated state estimate and future-weather uncertainty. Report the issue date, observed stage, weather cutoff, forecast horizon and uncertainty. Compare forecast errors by lead time. Keep historical climatology and a current-season forecast visually distinct.

Shope et al.'s **2026 preprint abstract**, verified through DOI metadata, describes 22 years of Duke observations at Hammonton, New Jersey and leave-one-out assessment of chill-plus-forcing models. It reports R² above 0.85 for T3 at about 20-day lead, above 0.75 for bloom onset at about 30-day lead, and 0.57–0.60 for harvest start at about 20-day lead. This supports investigating joint chilling/forcing and different stage skill. It supplies neither a global accuracy claim nor coefficients that can be imported from its abstract. R² is not an error in days. [S25]

## 9. Calibration and validation contract

### Required record

`site_id`, coordinates/elevation, cultivar/species, plant age, production regime, protection, management dates/treatments, crop-year/cycle ID, observed stage and scale, numerator/denominator or harvested mass, last-not-yet/first-observed dates, observer/sampling frequency, weather station/product and time convention, source/license, quality flags.

Keep observation, fitted prediction and derived value separate. Missing and frost-destroyed crops are not zero-day intervals. Weekly observations are interval-censored; do not pretend the transition date is known to one day. A publication's SE, SD, fitted confidence interval and between-year spread are different quantities.

### Candidate comparisons

Start with a local cultivar calendar baseline, then test simple thermal models and only add chilling/photoperiod/management terms if they improve held-out predictions. Separate floral and vegetative outputs. Do not tune frost thresholds or risk recurrence gates to compensate for an inaccurate calendar.

Validation must hold out whole seasons and whole sites, and, where relevant, cultivars. Avoid splitting individual bushes from one field-year into train/test sets and calling that geographic validation. Optimize temperature bases, start dates and model choice inside the training partition, not once across all years before cross-validation.

Report stage-date MAE and bias in days, large-error frequency, onset/end and duration errors, interval coverage/width, and stage-occurrence discrimination. Report by cultivar, regime, region and forecast lead. Compare with the calendar baseline. A high in-sample R² does not demonstrate transfer to a new country.

Suggested evidence labels are **observed regional**, **locally validated model**, **transferred exploratory model**, **management scenario**, and **insufficient evidence**. These are proposed product labels, not existing validation claims. Any numerical acceptance tolerance should be chosen with the intended operational decision before evaluating the final holdout.

### Useful public data already identified

- UGA release tables provide stage-labelled cultivar/site means, but not a complete independent year-level validation set. [S9]
- Campa and Ferreira provide six-year phenology and supporting information; filter the mixed Vaccinium taxa and retain their F10/harvest25/>90-harvest definitions. [S8]
- Babiker et al. provide 187 SHB genotypes at Poplarville, Mississippi, with four plant replicates. Fruit-quality observations span 2020–2023, but **flowering/ripening phenology is 2021–2022**, using 50% endpoints. Do not misdescribe this as four years of phenology. Public availability must be assessed at the individual supplemental-field level. [S26]
- UMaine's field tracker has public historical records and 2026 stage observations. Its August 2026 fruit-state percentages are not percentages of yield harvested. [S27]
- USDA NASS weekly crop progress can check a state-level crop's aggregate harvest progression, not cultivar budbreak. Shipments and customs exports add storage/logistics/market effects and cannot serve as field flowering labels.
- USA-NPN explicitly records breaking **leaf** buds, open flowers and blue/blue-black ripe fruit, using status and intensity bins. Its open-flower denominator includes fresh buds/unopened/open flowers and excludes faded flowers, so it is not automatically a cumulative-flowering curve. Cultivar and management often need separate identification. Protocol verified; record counts around our sites were not retrieved. [S38]
- Nagasaka et al.'s Poplarville study adds genotype-specific chilling and 50%-flowering/ripening evidence. Its forcing criterion and sampling resolution differ from Olmstead's; do not pool the thresholds without harmonization. [S39]
- Carlson and Hancock's **15-year, 13-cultivar Michigan first-picking** study is the long series previously misattributed to Kirk and Isaacs. Its abstract reports a 22–69% reduction in prediction-error standard deviation relative to calendar dates after model selection; no independent holdout is described in that abstract. [S40]
- State-level NASS records are available as dated PDFs; for example, the 12 May 2025 Southern Region issue has a Georgia blueberry-harvested row, but no Florida blueberry-progress row in that issue. AMS's old `WA_FV408` release was paused from May 2025, with datasets continuing through MyMarketNews/API. Archive access and API requirements must be checked before planning ingestion. [S42, S43]

### Practical calibration priorities

1. **Florida/Georgia:** request existing cultivar-by-year field records with treatment flags; use public stage-labelled trials to specify endpoints and reproduce literature calculations. River Valley's expected early-April harvest is a diagnostic observation to investigate, not a date the model must be tuned to reproduce at any cost.
2. **Papanduva and southern Brazil:** seek local cultivar/system/altitude records, with Epagri/Embrapa weather and trials as leads. Pelotas, Cerro Azul and Piracicaba represent different biological and management settings; none is an automatic substitute for Papanduva.
3. **Temperate NHB:** compare Michigan/NJ and appropriate European or southern temperate trials with cultivar identity and actual weather. Validate transfer separately from fitting.
4. **Evergreen/protected:** collect pruning/leaf-retention/heating histories and repeated flowering/harvest fractions. Do not calibrate a winter-based model and relabel it evergreen.
5. **Lowbush:** preserve crop/prune-year status and population-level observations; its GDD models cannot be substituted for cultivated highbush simply because both are blueberry.

Use blocked validation appropriate to the deployment question; general guidance for structured ecological data also supports that choice. [S41] No reviewed evidence warrants promising the earlier proposed **7–12-day bloom MAE** or **±10–14-day harvest accuracy** for this platform. Measure those errors on independent relevant data.

## 10. Parameter decisions for this project

| Parameter or practice | Decision from this review |
|---|---|
| Universal 50 CH | Do not treat as a global cultivar requirement. Retain only as the explicitly provisional legacy comparator until a calibrated replacement is approved. |
| Universal 150 GDD to budbreak | No matching source established; replace through stage-defined calibration, not by relabelling a bloom target. |
| Budbreak +14/+35 flowering | Replace with measured/fitted flowering progression where supported. |
| Flowering-start +70/+110 harvest | Replace with endpoint-specific cultivar/site ripening and harvest progression. Do not substitute an F50→R50 duration into this formula. |
| Base 7°C | Candidate for highbush flowering; not automatically for every species or fruit-development stage. |
| Emerald/Jewel 225/302 | Published local treated-plant bloom results; usable as literature comparisons only with context and resolved accumulation-method ambiguity. |
| Emerald/Jewel 80/225/370 and 160/300/445 | Rounded derivations from fitted curves, not observed general cultivar-class thresholds. |
| Fixed SHB first-ripe 55–65 days | Too broad a transfer claim. Stage, genotype and site must be retained; Emerald is an important counterexample to a universal short FDP. |
| Add 10–14 days below 300 CH | Unsupported rule. The cited 10–14 days is a treatment response, not a universal chilling penalty. |
| Fixed harvest-end +35/+45 days | Not established by the sources reviewed. Fit harvest progression or retain observed ranges. |
| CH-to-CP conversion | Do not convert by a global or local mean ratio; calibrate the requirement in the actual model's units. |
| Dynamic Model globally best | Not established for blueberry. Compare as a candidate with transparent validation. |
| Fixed evergreen calendar and one-hour freeze trigger | Unsupported. Require management/field-state inputs and separately model exposure. |
| Six-month global shift | Scenario convention at most; not a calibration or low-latitude production rule. |
| Regime inferred solely from latitude/chill class | Do not equate the climate classifier with actual deciduous/evergreen management. Obtain regime information; do not introduce an unsupported latitude cutoff. |
| Flower-initiation daily Tmax ≥28°C rule | Chamber evidence supports a temperature effect, not that field event definition. Keep as an uncalibrated research hypothesis if examined. |
| “No-chill” Brazilian trial = zero hours below 7.2°C | Correct to the reported five hours over the stated table period; do not replace a measured total with a categorical label. |

**Recommended next implementation order, not implemented here:** stage/observation schema → provenance-bearing parameter registry → local cultivar/calendar baselines → reproductions of accessible published models → held-out site/year comparison using compatible weather → explicit applicability/uncertainty outputs → recomputation of stage-specific exposures. Nursery establishment and genotype recommendation remain separate tasks.

The parameter registry should store `cultivar`, `bud_type`, `production_regime`, `stage_definition`, `temperature_metric`, `units`, `start_anchor`, `negative_unit_rule`, `upper_temperature_rule`, `source_weather`, `treatment`, `trial_site`, `trial_years`, `estimate`, `uncertainty_type`, `source_url`, `access_status`, and `validation_domain`. An unresolved field is a reason not to activate a profile, not permission to invent a default.

For a season where chilling is insufficient or the stage does not occur, retain that outcome in the denominator. Report both timing conditional on stage occurrence and frequency of no/irregular stage; dropping unsuccessful years would make a marginal site appear more suitable.

## Source register

Access status describes what was read, not automatic endorsement of a study's methods or global transferability.

- **S1.** Rubio Ames, 2024. UGA C1293, *Recognizing Flower and Vegetative Buds in Blueberries*. Full extension text. https://fieldreport.caes.uga.edu/publications/C1293/recognizing-flower-and-vegetative-buds-in-blueberries-blueberry-phenology/
- **S2.** Wichura et al., 2024. Blueberry BBCH scale. DOI metadata/abstract and accepted-manuscript narrative reviewed; complete published code table not transcribed. https://doi.org/10.1139/cjb-2024-0036 ; accepted manuscript: https://utoronto.scholaris.ca/server/api/core/bitstreams/1373b56f-7db3-486f-b610-154a107a10bd/content
- **S3.** Olmstead et al., 2015. *Floral Bud Chill Requirement of Low-Chill Southern Highbush Blueberry Germplasm*. Full primary PDF. https://journal.americanpomological.org/index.php/jofaps/article/download/2867/2871
- **S4.** Schuchovski & Biasi, 2021. *Dormancy of Floral Buds of Rabbiteye Blueberry in a Mild Winter Climate*. Full primary text. https://doi.org/10.1590/1678-4324-2021190755
- **S5.** Norvell & Moore, 1982. Chilling-model experiment, Bluecrop/Coville. Primary abstract. https://doi.org/10.21273/JASHS.107.1.54
- **S6.** Williamson, Harmon & Phillips, revised September 2026. UF/IFAS *Protecting Blueberries from Freezes in Florida*. Full extension text. https://ask.ifas.ufl.edu/publication/HS216
- **S7.** Kovaleski et al., 2015. *Inflorescence Bud Initiation, Development, and Bloom in Two Southern Highbush Blueberry Cultivars*. Full publisher HTML, Figure 4 coefficients and methods verified. https://journals.ashs.org/view/journals/jashs/140/1/article-p38.xml
- **S8.** Campa & Ferreira, 2018. Six-year Asturias phenology collection. Full primary text and supplement availability statement. https://doi.org/10.1371/journal.pone.0206361
- **S9.** NeSmith, 2014. Public UGA TH-917/921/948 cultivar-release dossier, five-year site means. Full PDF. The HTTPS host had a certificate mismatch; the public HTTP document was readable. http://georgiacultivars.com/images/uploads/documents/NeSmith_Blueberry_TH921_TH917_TH948.pdf
- **S10.** Kirk & Isaacs, 2012. *Predicting Flower Phenology and Viability of Highbush Blueberry*. Full publisher text; image-only parameter tables not transcribed. https://journals.ashs.org/view/journals/hortsci/47/9/article-p1291.xml
- **S11.** NeSmith, 2006. Rabbiteye flowering/ripening and heat units. Primary abstract; detailed HU parameters unavailable. https://doi.org/10.17660/ActaHortic.2006.715.19
- **S12.** NeSmith, 2012. *Fruit Development Period of Several Southern Highbush Blueberry Cultivars*. Metadata and indexed abstract; full methods unavailable. https://doi.org/10.1080/15538362.2011.619430
- **S13.** NeSmith, 2014. Georgia Dawn cultivar release. Primary publisher text. https://journals.ashs.org/view/journals/hortsci/49/5/article-p674.xml
- **S14.** Williamson et al., 2002. *Hydrogen Cyanamide Accelerates Vegetative Budbreak and Shortens Fruit Development Period of Blueberry*. Primary paper read through mirrored PDF by the research review. https://doi.org/10.21273/HORTSCI.37.3.539
- **S15.** Zapien-Macias, Liu & Nunez, 2025. *Blueberry ripening mechanism: a systematic review of physiological and molecular evidence*. Full review. https://pmc.ncbi.nlm.nih.gov/articles/PMC12261913/
- **S16.** Phillips, Williamson & Munoz, revised April 2026. UF/IFAS evergreen production. Full extension text. https://ask.ifas.ufl.edu/publication/HS1362
- **S17.** Spann, Williamson & Darnell, 2004. Photoperiod/temperature effects on Misty initiation. Primary abstract; constant-temperature treatments, not a field daily-Tmax rule. https://doi.org/10.21273/JASHS.129.3.294
- **S18.** Finn, Strik & Moore. PNW 656, *Blueberry Cultivars for the Pacific Northwest*. Full extension text reviewed; figure's detailed cultivar bars not digitized. https://extension.oregonstate.edu/catalog/pnw-656-blueberry-cultivars-pacific-northwest
- **S19.** British Columbia provincial blueberry variety guide. Public PDF, relative seasons not absolute dates. https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/agriculture-and-seafood/agriservicebc/production-guides/berries/blueberries/blueberry_varieties_table.pdf
- **S20.** White, Boyd & Van Acker, 2012. Lowbush growth stages and GDD. Full primary text reviewed. https://doi.org/10.21273/HORTSCI.47.8.1014
- **S21.** Barrau et al., 2006. Huelva cultivar field trial. Primary abstract. https://doi.org/10.17660/ActaHortic.2006.715.36
- **S22.** Jiang et al., 2019. Chinese production systems and regional calendars. Review chapter. https://doi.org/10.5772/intechopen.88225
- **S23.** Maticorena Quispe & Escobedo Álvarez, 2024, reporting 2015/16. Chao Biloxi pruning trial. Full primary PDF; single-season and internal reporting caveats noted above. https://dialnet.unirioja.es/descarga/articulo/9610568.pdf
- **S24.** Cortés-Rojas et al., 2016. Guasca Biloxi/Sharpblue study. Primary abstract. https://doi.org/10.15446/agron.colomb.v34n1.54897
- **S25.** Shope et al., 2026. *Improving Prediction of Highbush Blueberry Bud Break, Bloom, and Harvest Timing Using Optimized Chilling and Heat Accumulation Models*. Posted-content/preprint abstract through Crossref, not full-paper verification. https://doi.org/10.2139/ssrn.7217434
- **S26.** Babiker et al., 2025. *Phenological variation associates with the stability of fruit quality traits in cultivated tetraploid blueberry*. Full primary text. https://pmc.ncbi.nlm.nih.gov/articles/PMC12239625/
- **S27.** University of Maine Wild Blueberry Phenology Tracker. Public observational monitoring with links to historical annual records. https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/
- **S28.** Antunes et al., 2008. Pelotas rabbiteye phenology, three seasons. Primary paper/PDF reviewed. https://doi.org/10.1590/S0100-204X2008000800009 ; PDF: https://apct.sede.embrapa.br/pab/article/download/382/5609
- **S29.** Medina et al., 2018. *Performance of Emerald and Jewel blueberry cultivars under no-chill incidence*. Full primary PDF, weather table and calendar text verified. https://revistas.ufg.br/pat/article/download/52093/25717
- **S30.** Medeiros et al., 2018. Cerro Azul low-chill cultivar trial. Full primary text reviewed. https://doi.org/10.1590/0100-29452018520
- **S31.** Pandolfo et al., 2017. Santa Catarina blueberry climatic zoning. Full published paper reviewed; modeled zoning, not cultivar-date observations. https://ciram.epagri.sc.gov.br/ciram_arquivos/site/boletins_culturas/risco_climatico/SC_Mirtilo_Zoneamento.pdf
- **S32.** Lobo Zavalía et al., 2018. Tafí del Valle high-elevation cultivar trial, 2012–2016. Primary full text reviewed; detailed figures not digitized. https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1851-30182018000200002
- **S33.** Maule blueberry technical-production manual, 2014, reporting 2012/13 observations. Full technical manual, not peer-reviewed model validation. https://portalberries.com/wp-content/uploads/2025/04/Manual-Especificaciones-Tecnica-Economica.pdf
- **S34.** Retamales et al., 2014. Chilean production zones and harvest timing. Full review text, regional descriptive evidence. https://doi.org/10.1590/0100-2945-446/13
- **S35.** Steyn, Lötze & Hoffman, 2023, online 2022. Western Cape reproductive phenology in 2020. Primary abstract via AGRIS, full paper unavailable. https://doi.org/10.1016/j.scienta.2022.111493 ; abstract: https://agris.fao.org/search/fr/records/65e01dd963b8185d9cb16f1c
- **S36.** Scalzo, Wright & Boettiger, 2016. Corindi evergreen breeding/production context. Primary conference abstract. https://doi.org/10.17660/ActaHortic.2016.1117.8
- **S37.** Patel/HortResearch, Centra Blue, USPP20515P3. Full public breeder patent disclosure, not independent validation. https://patents.google.com/patent/USPP20515P3/en
- **S38.** USA-NPN, highbush blueberry observation protocol. Full protocol read; site-year data not acquired or counted. https://mynpn.usanpn.org/npnapps/species/Vaccinium/corymbosum
- **S39.** Nagasaka et al., 2022. Phenology-related traits in a highbush collection, Poplarville. Primary full text reviewed. https://doi.org/10.3389/fpls.2021.793679
- **S40.** Carlson & Hancock, 1991. Michigan first-pick heat-unit methodology. Primary abstract. https://doi.org/10.21273/JASHS.116.5.774
- **S41.** Roberts et al., 2017. Cross-validation for structured data. General methodological source, abstract verified; not blueberry accuracy evidence. https://doi.org/10.1111/ecog.02881
- **S42.** USDA NASS Southern Region crop progress, 12 May 2025. Public administrative PDF, not field phenology. https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/2025/SOR-CropProgress-5-12-25.pdf
- **S43.** USDA AMS weekly blueberry shipments, legacy report and successor portal. Administrative proxy and access-status evidence, not crop-stage observations. https://www.ams.usda.gov/mnreports/wa_fv408.pdf ; https://mymarketnews.ams.usda.gov/viewReport/3251

### Scope and remaining evidence limits

This is a research synthesis, not field calibration. Some papers were accessible only as abstracts, some parameter tables were images, and many commercially important regions lack open cultivar-by-year field records. No coefficients were estimated from shipment curves, country averages, unsupported snippets or the current model's own outputs. Original supervisor materials, private breeding records and raw weather archives are not reproduced here.
