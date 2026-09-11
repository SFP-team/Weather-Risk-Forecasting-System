# Global Blueberry Recommendation — research and implementation plan

**Prepared:** 5 September 2026

**Status:** proposed implementation design; no application or trained model is delivered by this document.

**Product:** coordinate × management → cultivar/selection shortlist, production calendar, principal risks, production clock.

**Scope:** build a new product on `main`; do not resume the old Florida risk or analogue application.

**Current execution priority (2026-09-11):** the archive and first UI are implemented. Follow `docs/weather/R_ADAPTATION_PLAN.md` next: isolate reviewed R methods, consume the existing archive, and demonstrate open-ground production strategy, seasonal windows and stage risks at Waldo before expanding soil/tunnel or genotype modelling. The long-term architecture below does not override that milestone or authorize new downloads by itself.

## 1. Executive recommendation

Build an evidence-aware **genotype × environment × management decision-support system**, not a climate-similarity map with cultivar names attached.

The application should accept any valid land coordinate. Its ability to recommend a particular blueberry genotype must depend on the evidence available for that environment, genotype, and management system. Global climate coverage does not imply globally validated cultivar recommendations.

The initial catalog is **UF southern highbush material approved by the breeding program**, not every blueberry species or cultivar in the world. A user asking about an unsuitable or unsupported location must be able to receive an honest explanation and no cultivar recommendation. Where evidence is exploratory, recommend a local trial, not commercial planting.

The recommended sequence is:

1. Deliver a reproducible climate diagnosis for one coordinate, then a small stratified set of coordinates.
2. Add the four management scenarios, an explicit assumption set, and an approved rule-based genotype shortlist.
3. Fit and validate baseline and reaction-norm models using properly linked breeding records.
4. Publish versioned, uncertainty-aware trait predictions and rankings to a fast application.
5. Expand the validated domain through deliberately designed field trials.

Start with interpretable statistical models. Treat deep learning as a later challenger that must earn deployment on independent environments. Start collecting the data needed for both now.

The most important constraint is not compute. It is whether we have trustworthy genotype–site–year–management observations, usable phenology records, permission to use them, and independent environments on which to test transfer.

## 2. Evidence reviewed and what it establishes

### 2.1 Project sources

The review covers:

- [REQUIREMENTS.md](/Users/whiterose/Documents/Weather_Claude/REQUIREMENTS.md).
- [First meeting transcript](/Users/whiterose/.codex/attachments/7ce417d9-747f-4d3a-b968-e9b2a4aea239/pasted-text.txt) and [second meeting transcript](/Users/whiterose/.codex/attachments/6e7bf322-76e3-420e-8a57-3f372db9a80f/pasted-text.txt).
- [First handwritten page](/Users/whiterose/Downloads/IMG_2736.HEIC) and [second handwritten page](/Users/whiterose/Downloads/IMG_2737.HEIC).
- [Original Papanduva report](/Users/whiterose/Documents/Weather_Claude/Blueberry_Expansion_Southern_Brazil2.html), [revised Papanduva report](/Users/whiterose/Documents/Weather_Claude/Blueberry_Expansion_Southern_Brazil_Revised2.html), [southern Brazil summary](/Users/whiterose/Documents/Weather_Claude/Southern_Brazil_Blueberry_Summary_Report.html), and [technical report](/Users/whiterose/Documents/Weather_Claude/Southern_Brazil_Blueberry_Technical_Report.html).
- [Paul's R workflow](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R).

The handwritten architecture supports four connected layers: historical weather, management, genotype adaptation, and target-environment prediction. It explicitly mentions reaction norms and **deep learning**; the transcript's ambiguous “dependent model” should not become a separate invented method.

The meetings establish product intent, including the simple two-input interaction, practical trial recommendations, and reuse of Paul's work. They also contain provisional assumptions, examples, and research hypotheses. These are evidence to interpret, not instructions to execute blindly or scientific facts to hard-code.

The fourth report and R workflow are now present. The statements in `REQUIREMENTS.md` that they are missing are outdated. The underlying phenotypes, genomic/pedigree data, fitted models, and full report-generation project are still not supplied in the reviewed files.

### 2.2 Requirement reconciliation before implementation

`REQUIREMENTS.md` remains the product source of truth. The following are **proposed corrections**, not silent changes to it. Incorporate accepted decisions into that file when implementation starts; do not maintain two conflicting specifications.

| Existing statement or assumption | Recommended implementation decision | Reason / decision owner |
|---|---|---|
| Breeder/collaborator first; latest request says anyone can ask | Public climate diagnosis and approved public cultivar output; authenticated breeder view for restricted material | Supports the latest request without publishing Stage 4 data; Patricio approves visibility |
| Top 3–5 genotypes | Return up to five; allow fewer or none with an explanation | Never fill the list with unsupported candidates |
| County/municipality as weather identity | Native source grid cells are the weather identity; administrative names are context or explicit aggregates | Counties can span substantial climate/elevation variation |
| Tunnel ≈ greenhouse; freeze mostly controlled | Keep one UI choice, but define a conservative reference structure: unheated, ventilated rain-excluding tunnel; no guaranteed freeze control | Structure/heating cannot be inferred from one option; Gerardo signs off |
| Pots/tunnels permit anything the model ranks highly | Relax only constraints the management demonstrably changes | Dormancy, light, heat, pollination and establishment limits remain |
| Evergreen/semi/deciduous is a temperature classification | Report climate support for a managed production clock, genotype compatibility, and uncertainty separately | Leaf retention and cropping strategy also depend on management and genotype |
| Chill hours and UF 32–45°F are separate currencies | 32–45°F is approximately the same 0–7.2°C band; distinguish this band from all-hours-below-7.2°C and from Dynamic Model portions | Avoid false agreement and incompatible thresholds |
| “Production GDD / sunshine” | Separate thermal time from radiation; DLI requires an explicit shortwave-to-PAR conversion assumption | They measure different physical quantities |
| Train and serve only the current shortlist | Request permission to train on all relevant authorized historical observations; serve only the approved shortlist | More informative training need not imply recommending retired lines; Patricio/Diego approval required |
| Look up nearest region's top five | Cache all eligible candidate trait summaries; validate climate-space approximation; abstain or enqueue exact inference when unsupported | Geographic proximity and post-filtered top-five lists can produce wrong results |
| Three calendar outputs | Distinguish establishment planting window from recurring flowering/harvest windows of bearing plants | Perennial plants do not promise a full crop in the planting year |
| Reports are the numerical gold standard | Preserve them as historical benchmarks and reconcile differences; use reviewed, independently tested formulas as scientific truth | Reports and script contain contradictory methods and incomplete lineage |

Public release and any expanded training access remain separately approved decisions. They need not block climate-pipeline development.

## 3. What to reuse from Paul's work

### 3.1 High-value components

Reuse the biological problem framing, reference-site catalog, dated-weather retrieval concepts, phase-specific risk definitions, multi-year summaries, report layout, and the distinction between target diagnosis and geography search. The emphasis on harvest rain rather than annual rain is particularly useful.

Extract useful functions into a tested package. Preserve original inputs, outputs, thresholds and report examples as an audit fixture before changing behavior. Prefer reviewed functions over casually reimplementing them in another language.

The technical report is valuable because it describes environmental kernels, trait predictions, and candidate prioritization. However, descriptions and rendered tables are not a recoverable fitted model. The supplied script reads genotype predictions from external CSV files; it does not contain the complete training procedure needed to recreate those panels.

### 3.2 What cannot be promoted directly into production

| Finding in the supplied material | Consequence | Required action |
|---|---|---|
| Hard-coded working directory and runtime dependency installation | Results depend on a personal machine and changing packages | Configuration, lockfiles, explicit setup, clean-session execution |
| Multiple generations of classifiers and season definitions | The same pin can change class for methodological reasons | One versioned primary method; alternatives become labeled sensitivity analyses |
| `system_assignment` is checked before its later creation; another path uses `target_system` without an active definition | Behavior can depend on objects left in an interactive R session | Pure functions with explicit inputs; fresh-process tests |
| Climate envelope code indexes `reference_suitability[1, feature_name]` | A reference distribution can become a single reference row | Test reference aggregation and feature orientation explicitly |
| Missing weather can be removed before a stateful chill calculation; stage sums use missing-value removal | Gaps can become apparent continuity or zero rain/risk | Full time grid, coverage masks, stateful gap rules, nullable results |
| POWER local-solar timestamps are treated as UTC in parts of the script | Misaligned dates and stage events | Source-specific time semantics and boundary tests |
| Early and detailed classifiers, WorldClim proxies and hourly calculations differ | Classifier confidence is not a validated probability | Separate data product, chill definition, threshold and model version |
| Selection-index defaults reward missing uncertainty/metadata, use candidate-dependent scaling and raw across-trait dispersion | Unknown lines can be favored; ranks change when the candidate list changes | Rebuild index and missing-data policy |
| No fitted management response model or soil module | Tunnel/pot efficacy is not established by this code | Add explicit assumptions and calibration data |

Concrete code entry points include the [working-directory setup](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:28), [chill helper](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:798), [early system lookup](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:1605), [stage aggregation](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:3929), [reference-row lookup](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:4809), and [external genotype prediction input](/Users/whiterose/Documents/Weather_Claude/blueberry_climate_analog_workflow.R:5490).

### 3.3 Reproducibility deliverable

Create a Papanduva reconciliation table containing, for each report: data period, source/resolution, season boundaries, chill definition, phenology rules, reference panel, risk scaling, index weights, code revision and output.

Examples requiring reconciliation are approximately 209 hourly chill hours versus 368 proxy hours, semi-evergreen versus deciduous, harvest rain around 206 versus 174 mm, and flower-freeze frequency around 4.2% versus zero. These are not interchangeable measurements. Do not average them or select the most convenient result.

The summary/technical work uses a broader Brazilian geography scan and a different genotype-index configuration from the supplied R ranker. Reproduce their lineage separately. Municipalities sharing identical climate values may share a grid cell; verify this before interpreting them as independent observations.

Do not make exact recreation of every historical report a gate for the first usable climate slice. Reconcile the functions used by that slice first and keep unresolved historical discrepancies in an audit register.

## 4. Product behavior and scientific contract

The screen has two inputs only:

1. Map pin or latitude/longitude.
2. One management choice: `open_ground`, `open_pots`, `tunnel_ground`, `tunnel_pots`.

The default is `open_ground`. Authentication controls access but is not an additional agronomic input. Do not ask for a desired market week or a detailed cover specification in v1.

The four main outputs are:

- **Candidate shortlist:** up to five eligible genotypes, reasons, limitations, evidence level, and a trial recommendation where appropriate.
- **Calendar:** establishment planting guidance and bearing-plant flowering/harvest distributions, separately labeled.
- **Principal risks:** roughly three prioritized hazards with raw quantities, historical frequencies when meaningful, management assumptions, and unresolved hazards.
- **Production clock:** one or more supported strategies, with uncertainty and genotype compatibility.

Source detail, nearest named reference environments, soil context, model versions and technical diagnostics belong in expandable detail and a reproducible downloadable report. They need not become extra headline widgets.

Every result has an evidence status:

| Status | Meaning | Allowed presentation |
|---|---|---|
| `supported` | Within a tested applicability domain with sufficient data and appropriate management evidence | Ranked candidates and calibrated uncertainty for the evaluated use case |
| `exploratory` | Climate can be analyzed, but genotype transfer or management effects are weakly supported | Provisional trial priorities; explicit extrapolation notice |
| `insufficient_evidence` | Missing data, no eligible material, unvalidated conditions, or an essential unsupported model component | Climate facts where valid; no fabricated ranking or calendar |

These are product states with testable rules, not percentages. Preserve separate diagnostics for weather completeness, environmental novelty, genetic support, management evidence, and validation geography. A single averaged “confidence score” would hide different failure modes.

If no public cultivar is eligible, the public result must not expose the private candidates that were removed. Recompute the public shortlist within its permitted catalog.

## 5. Climate data strategy

### 5.1 Recommended source architecture

Implement source adapters rather than coupling all science to a vendor column name.

| Source | Role in the build | Main limitation |
|---|---|---|
| NASA POWER | First reference-site/Papanduva reproduction adapter and explicit fallback | Coarser and variable-dependent native support; point queries are not field measurements |
| AgERA5 daily point time series | Preferred production candidate for daily agricultural variables | Daily rather than hourly; derived from ERA5 |
| ERA5-Land hourly point time series | Preferred candidate for temperature/dewpoint histories, chill and subdaily hazards | Grid-scale reanalysis, not canopy or cold-pocket observations |
| FAWN and appropriate independent station archives | Source benchmarking and local calibration where available | Coverage, instrument context and quality flags vary |
| SoilGrids, optionally better regional soil sources | Ground-system context with depth and uncertainty | Not a substitute for field soil, drainage or irrigation-water assessment |

AgERA5 now offers daily, 0.1° point time series from 1979 onward, including agriculture-oriented humidity, radiation and precipitation variables. ERA5-Land offers hourly, 0.1° point time series from 1950 onward. Both support efficient point extraction, so a global cube is unnecessary for v1. These products share the ERA5 family and must not be described as independent ensemble members. Sources: [AgERA5 time-series catalog](https://cds.climate.copernicus.eu/datasets/sis-agrometeorological-indicators-timeseries?tab=overview), [ERA5-Land time-series catalog](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview).

POWER's meteorological and solar fields have different native resolutions. Store this distinction rather than attaching one universal precision to every variable. Respect request limits and deduplicate by source grid identity. Sources: [POWER data documentation](https://power.larc.nasa.gov/docs/faqs/data/), [POWER request guidance](https://power.larc.nasa.gov/docs/tutorials/service-data-request/api/).

Run a bounded two-week benchmark over the UF reference panel, Papanduva and approximately 30–50 stratified sites, using stations where available. Compare daily temperature bias, cold/heat tails, wet-day detection, seasonal rain, radiation, missingness, response time, transfer size, and reproducibility. Select and freeze a **data profile** before broad deployment. Higher nominal resolution alone is not proof of better extreme-event estimates.

Initial proposed production profile: AgERA5 daily variables plus ERA5-Land hourly temperature/dewpoint. Check alignment and inconsistencies between these products. If unacceptable, use a coherent ERA5-Land-derived daily/hourly profile instead. POWER fallback must carry a changed profile and support flag, never silently masquerade as the primary source.

### 5.2 Time, space and archive policy

- For a 2026 release, use **2011–2025** as the initial 15-complete-calendar-year baseline. Download boundary padding needed for crop seasons crossing years; only include complete evaluable crop seasons in seasonal summaries.
- Label season start, season end and the convention for naming a season. Fifteen calendar years do not automatically equal fifteen complete cross-year crop seasons.
- Compare the latest ten years and, where useful, a longer extreme-event history as separate sensitivity views. Do not claim fifteen years captures every rare freeze or future trend.
- Store canonical timestamps and original time convention. Derive biological local days with a documented convention; account explicitly for POWER local solar time and AgERA5 local-day aggregation.
- Save requested coordinate, actual source cell/coordinate, elevation information where available, and displacement. Coastal/mountainous mismatches must be visible.
- Resolve county/municipality names for interpretation. Use a documented area aggregate only when deliberately requested by the product, not as an accidental nearest-county substitution.
- Fetch trial/reference cells first, then demand-driven cells and selected climate-cluster anchors. Do not crawl the globe before evaluating the prototype.
- Archive raw responses, normalized weather, quality masks and manifests. Derived features are reproducible, versioned caches, not new raw observations.

### 5.3 Quality control is part of the scientific model

Construct the complete expected time grid before calculating anything. Validate units, ranges, duplicates, missing-value sentinels, leap days and source revision. Distinguish raw accumulated ERA5 fields from already processed time-series variables; do not blindly difference precipitation or radiation without inspecting the chosen product's conventions.

Measure coverage per variable and biological window. Missing rain is not zero rain; no observed freeze in an incomplete window is not evidence of no freeze. Stateful chill calculations must not concatenate separated observations across gaps. Any reconstruction needs an explicit validated method, an imputed-data flag and a tested maximum gap policy.

A provisional screening threshold such as 95% coverage can trigger review, but it does not make missing extreme-event hours harmless. Establish variable- and hazard-specific admissibility rules with station-based masking experiments. Missing essential windows should return `null` with a reason.

FAWN provides historical archives useful for Florida evaluation. Some products are gap-filled; retain those flags and distinguish measured observations from imputed values when judging weather-source accuracy. Source: [FAWN data access](https://fawn.ifas.ufl.edu/data/).

## 6. Soil and management modeling

### 6.1 Ground versus pots

For ground systems, obtain soil pH, texture, organic carbon and other available attributes at relevant depths, including uncertainty and source resolution. SoilGrids provides 250 m predictions, six standard depth intervals and uncertainty information. It does **not** directly establish field drainage, pathogen presence, irrigation-water chemistry or amended bed properties. Its documented REST service is currently paused; implement a tested WCS/WebDAV subset-and-cache path rather than depending on that endpoint. Source: [ISRIC SoilGrids documentation](https://docs.isric.org/globaldata/soilgrids/).

Use soil to identify constraints and local checks, not to turn a coarse pH prediction into an unconditional veto. Native soil differs from pine-bark-amended beds. For pots, skip native-soil suitability but state the assumed suitable acidic substrate, drainage and irrigation management. Containers reduce some root-zone constraints; they do not make root disease or poor water management impossible.

### 6.2 Treat management as a change in exposure

Represent management between ambient weather and biological response:

`ambient weather → canopy/root-zone exposure under management → phenology and trait response`

This is preferable to subtracting arbitrary percentages from all risk scores.

| Scenario | Defensible initial change | Remaining uncertainty / hazard |
|---|---|---|
| Open ground | Ambient canopy exposure; native/amended soil context | Rain on fruit, cold, heat, drainage, irrigation demand |
| Open pots | Different substrate/root-zone assumptions | Rain on fruit remains; pot temperature and watering may matter |
| Tunnel ground | Rain interception scenario and altered canopy climate | Freeze can remain; ventilation, humidity, heat and light may worsen; native soil constraints remain |
| Tunnel pots | Both preceding changes | Neither guaranteed dormancy compatibility nor universal climate control |

Keep separate variables for rainfall reaching fruit, rainfall reaching the root zone, canopy temperature, humidity and radiation transmission. Parameterize these only from measurements or defensible external experiments. Until calibrated, report qualitative mitigation and bounded sensitivity scenarios, not numerical claims such as “freeze risk reduced by 90%.”

No universal 30-day advancement should be applied to tunnel flowering. A protected system can change phenology, which can expose earlier flowers to a different cold-risk period. Model this interaction when data exist.

UF describes evergreen production as a managed, genotype-dependent system involving leaf retention and continued plant care; it is not simply a chill-hour label. Freeze protection remains a separate consideration. Sources: [UF evergreen production guidance](https://ask.ifas.ufl.edu/publication/HS1362), [UF freeze-protection guidance](https://ask.ifas.ufl.edu/publication/HS216).

## 7. Phenology, production clocks and risk engine

### 7.1 Production clock

Estimate **climatic support** for evergreen, semi-evergreen and deciduous strategies using winter conditions, chill distributions, cold events, light and observed reference behavior. Combine this with verified genotype adaptation and management evidence.

Use Gerardo/Patricio-reviewed rules as the initial baseline. Preserve the report thresholds as provisional parameter sets for sensitivity testing. Do not fit a sophisticated classifier to labels generated by those same thresholds and call it independent biological validation.

Allow transitional or unresolved outcomes. Where adaptation is established, apply incompatibility constraints. Near a threshold or with uncertain labels, propagate uncertainty or mark the candidate provisional rather than discarding it with false certainty. Pots do not remove dormancy constraints.

### 7.2 Phenology model hierarchy

1. **Reference-stage baseline:** location/system-specific seasonal windows with clearly provisional parameters. Suitable for climate diagnosis before genotype data arrive.
2. **Genotype-aware model:** chill requirement and forcing response, with site/year/management effects and observed budbreak, flowering and harvest dates.
3. **Validated management extension:** protected-system parameters supported by paired/crossed observations.

For deciduous/semi-evergreen material, compare biologically plausible sequential or overlapping chill/forcing models. Estimate genotype parameters with partial pooling where observations are sparse. Keep chill-band hours and Dynamic Model portions separate; do not linearly convert requirements between them.

For evergreen production, use a separately justified calendar model that can incorporate leaf retention, pruning and flower-bud development. A dormant-tree chill clock is not automatically appropriate. Previous-season conditions and plant age may matter; reserve data fields for them now.

Represent dates on a seasonal/circular calendar, not as ordinary day-of-year averages that break at New Year. Southern-hemisphere processing must use actual seasons rather than blindly shifting a Florida calendar by six months. Mark multi-cropping or poorly supported tropical regimes as outside the initial phenology domain.

Calculate stage windows per genotype and historical season where supported. Summarize distributions, not one exact date. Flowering/harvest estimates for established plants must not imply first-year yield. An establishment planting window is an agronomic recommendation requiring assumptions about plant material and irrigation; with insufficient evidence it remains provisional or unavailable.

### 7.3 Risk definitions

| Risk | Computation | Interpretation limit |
|---|---|---|
| Chill shortfall | Seasonal fulfillment of the genotype's calibrated requirement | Unknown requirement means unknown fulfillment, not success |
| Flower freeze | Stage-specific cold exposure using an explicit threshold/duration | Grid air temperature is not measured flower temperature |
| Harvest rain | Rain total, wet/heavy-rain days and timing in harvest | Weather exposure is not a calibrated berry-split probability |
| Disease-favorable weather | Defined wet/warm/humid exposure during susceptible stages | Not a diagnosis or automatic spray prescription |
| Dry spell / water stress proxy | Consecutive dry days, optional water-balance indicators | Rainfall alone does not represent irrigation or root-zone moisture |
| Heat | Duration/intensity during fruit development | Berry-surface heat requires additional evidence |
| Low radiation | Stage-specific shortwave and explicitly derived PAR/DLI | Conversion uncertainty and cover transmission must be shown |

Return the underlying quantity, units, valid-season count, interannual spread, and relevant threshold before presenting an ordinal risk category. Keep relative position in the UF reference panel separate from biological severity. Being inside an envelope does not mean safe; being outside it does not prove crop failure.

For historical event frequencies, show numerator and denominator and an uncertainty interval where justified. Zero events in a short record is not a zero future probability. When chill failure prevents a bloom window, report reproductive failure separately; do not silently drop the season and make conditional flower-freeze risk appear reassuring.

During model development, avoid circular phenology features: fit phenology inside training folds, then use its predictions for held-out risk windows. Actual held-out bloom dates are permissible for retrospective exposure description, but not as hidden inputs to a planting-decision benchmark.

## 8. Breeding-data foundation

### 8.1 Data contracts

Use stable identifiers and preserve original records. The essential unit is generally a **plot/plant × season × trait observation**, with its experimental context, not one averaged row per cultivar.

| Entity | Required fields and safeguards |
|---|---|
| Genotype registry | Stable ID, aliases, clone/cultivar/selection identity, release status, approved audiences, recommendable flag, adaptation evidence and provenance |
| Site | Stable ID, controlled-access coordinates, elevation if known, source accuracy, soil/substrate, associated climate cells |
| Trial | Site, design, blocks/replicates, planting date, plant age, management, irrigation/pruning/cover metadata, controls |
| Observation | Genotype, plot/plant, season/date, trait, value, units, protocol, sample size, quality flags and missingness reason |
| Phenology | Budbreak, flowering stages, harvest start/peak/end, leaf retention, observation interval, observer/protocol |
| Genomics | Genotype ID mapping, ploidy/dosage representation, marker/build metadata, QC, genotype uncertainty and permitted uses |
| Pedigree | Parent IDs, relationship confidence, unknown-parent representation and reconciliation with genotype identity |
| Management evidence | Actual structure/substrate/treatments, measured microclimate where available, scope of transferable evidence |
| Decision preferences | Trait utility definitions, constraints, weights, approval and effective version |

Keep missing, not measured, censored, plant death, establishment year and biological zero distinct. Harmonize yield per plant versus plot/area, marketable versus total yield, firmness instruments, berry sampling, Brix/TTA/acidity measures and repeated harvest aggregation. Do not merge incompatible protocols merely because column names match.

If only adjusted means are available, obtain their uncertainty and adjustment method. Avoid an unweighted second-stage analysis that treats all means as equally precise. Prefer raw design-aware analysis where feasible.

### 8.2 Required handovers and owners

- **Patricio:** approved recommendation and visibility lists; adaptation tags and evidence; decision priorities; collaborator outcomes and trial authorization.
- **Paul:** original report project, input data manifests, environmental covariates, model objects or training code, parameter definitions, expected outputs and unresolved discrepancies.
- **Diego:** harmonized genomic/pedigree inputs, genotype identity/QC rules, ploidy representation, approved historical training scope and usable trial linkage.
- **Gerardo:** phenology and clock definitions, scientifically supported management assumptions, threshold interpretation and calibration protocol.
- **Rohit:** schemas, ingestion/QC reports, reproducible pipelines, application, tests, deployment and operational documentation.

The proposed expanded historical training set requires authorization. Until obtained, use only the approved subset and report the associated loss of support. Historical retired material can inform a model without appearing in serving outputs, but access permission cannot be inferred from scientific usefulness.

## 9. Genotype prediction and selection index

### 9.1 Research questions and model ladder

The main question is: **Can genotype–environment modeling improve the choice of approved genotypes at an unseen site, beyond breeder rules and simpler genetic/main-effect models?**

Secondary questions are whether phenology-aligned exposures improve transfer, whether pedigree/genomics add value for sparsely observed lines, and whether measured management effects improve protected-system decisions.

| Model | Purpose | Promotion condition |
|---|---|---|
| M0: breeder rules + approved adaptation tags | Honest baseline and early application functionality | Reviewed rule provenance; no invented quantitative yield |
| M1: design-aware trait mixed model, with pedigree/genomic main effect when supported | Establish the value of existing phenotype/genetic information | Better grouped validation and calibrated uncertainty than simpler alternatives |
| M2: genomic reaction norm with environmental covariates | Estimate differential genotype response across environments | Demonstrated improvement on the deployment-relevant held-out environments |
| M3: boosted-tree or other compact nonlinear challenger | Test nonlinearity using engineered features | Same folds, same information, robust improvement, acceptable uncertainty |
| M4: temporal/deep model | Test learned weather representations or richer interactions | Sufficient independent environments, favorable learning curves, reproducible benefit and manageable complexity |

Do not make M4 a dependency for release. Thousands of plants measured at a few locations are not thousands of independent climates.

Reaction-norm models using genomic and environmental covariance have an established methodological basis. That establishes a plausible model family, not verified transfer from Florida blueberries to every world climate. Source: [Jarquín et al., 2014](https://link.springer.com/article/10.1007/s00122-013-2243-1).

Blueberry genomic-prediction studies also make it important to handle autotetraploid information deliberately. Agree the genotype representation with Diego rather than silently treating dosage as diploid 0/1/2. Evaluate appropriate relationship construction for the supplied representation and estimand. Sources: [Optimizing whole-genomic prediction for autotetraploid blueberry](https://www.nature.com/articles/s41437-020-00357-x), [Blueberry genomic-selection lessons](https://pmc.ncbi.nlm.nih.gov/articles/PMC8236943/).

### 9.2 Statistical specification

For each trait, begin with a design-aware model of the form:

```text
observation = fixed design/age/management terms
            + genotype main effect
            + environment effect
            + genotype × environment effect
            + block / repeated-plant effects where required
            + residual
```

An environment is a defined site-season context, not a municipal name. Management must be recorded separately enough to identify its effects. Depending on the design, some terms are fixed and some random; select them using the experiment rather than copying a universal formula.

For observation-level genomic reaction norms, a candidate interaction covariance is:

```text
K_GE = (Zg G Zgᵀ) ∘ (Ze E Zeᵀ)
```

Here `G` is the genotype relationship matrix, `E` a valid environmental kernel, `Zg`/`Ze` map observations to those entities, and `∘` is elementwise multiplication. Centering, scaling, missing-data processing and kernel hyperparameters are learned inside training folds. Test positive semidefiniteness and consistent ordering.

Start `E` with compact interpretable features: winter thermal conditions, chill, frost, heat, radiation, precipitation/wetness and water-stress proxies in fixed, documented reference phases. Then evaluate genotype-specific phenology/exposure extensions. A genotype-dependent stage definition cannot be inserted into one supposedly genotype-independent site kernel without reconsidering the model structure.

Add G×management and G×E×management only where crossed/replicated data identify them. With only open-field trials, protected-system yield predictions are unsupported extrapolations, not estimated treatment effects.

Distinguish additive breeding value from expected performance of a clonally propagated cultivar. Non-additive effects may matter to the latter; test their value when data support estimation. Do not simply add pedigree and genomic predictions as if they were independent evidence.

Use appropriate likelihoods/transforms for continuous, bounded, ordinal or count traits. Handle repeated perennial observations and heterogeneous residuals. Begin with a smaller set of reliable decision-relevant traits instead of demanding all nine report traits immediately.

### 9.3 A defensible selection index

Define the target explicitly: utility for local trial placement or expected mature-plant performance under the stated system, not an undefined “best blueberry.”

1. Apply the approved catalog/audience policy and established biological constraints.
2. Convert predicted traits to **fixed, breeder-approved utility functions** with explicit units, preferred ranges and saturation/penalty points.
3. Combine utilities using versioned weights. Account for redundant/correlated traits rather than accidentally counting the same breeding objective multiple times.
4. Propagate joint prediction uncertainty into utility and rank uncertainty.
5. Evaluate average and unfavorable-season performance separately; optionally use an approved uncertainty or downside penalty.

A possible decision rule is expected utility minus a documented uncertainty penalty. A risk-averse alternative is utility in an unfavorable part of the historical season distribution. These are alternative policy choices to validate and approve, not arbitrary new constants.

Do not normalize utilities against whichever candidates happened to be queried. Removing a retired cultivar should not change every remaining cultivar's underlying utility. Do not substitute zero for missing standard error, or 100% suitability for unknown metadata. Missing essential information reduces support or prevents a score.

Do not call low raw variation “stability” when it could describe a consistently poor genotype. Separate high performance, environmental sensitivity, model uncertainty and year-to-year variability. Propagate trait covariance where available rather than assuming independent errors.

Avoid double-counting climate penalties if the trait model already predicts their effects. Keep unmodeled hazards as separate constraints/warnings unless an explicit calibrated index term is justified.

The output should include a shortlist's robust alternatives, not imply that a tiny score difference establishes a certain winner. Where available, note bloom overlap and compatible pollinizer needs; southern highbush planting guidance supports considering compatible varieties, but the application must not invent compatibility for uncharacterized advanced lines. Source: [UF blueberry planting guidance](https://ask.ifas.ufl.edu/publication/MG359).

## 10. Validation, uncertainty and applicability

### 10.1 Validate the decision the app actually makes

Maintain separate benchmarks for:

1. Known genotype at a new site.
2. Known genotype in a new season.
3. New genotype at a represented environment.
4. New genotype at a new environment.

The primary v1 target is usually the first: choosing among approved material at a new location. Report the others separately instead of combining them into one accuracy number.

Group by experimental site and related spatial units, season, genotype/family where appropriate, and management. Keep near-duplicate environments or a farm's repeated observations together. A random split of plant rows is not a test of geographic transfer.

Use nested/grouped tuning. Fit imputers, scaling, phenotype adjustment, phenology parameters, kernels, feature selection and index tuning within the training portion. Reserve a locked final test set. Report uncertainty across independent sites/environments, not by pretending individual fruit measurements are independent deployments.

Also distinguish two uses of weather:

- **Retrospective explanation:** realized weather from the held-out season helps explain realized phenotype.
- **Planting-decision prediction:** only weather history and other information available at the decision date may be used; future seasonal conditions are uncertain.

The app primarily serves the second. Evaluate historical decision-date hindcasts and year-distribution performance accordingly. A model given the actual future season's weather is not a validated long-horizon planting adviser.

### 10.2 Metrics and release gates

| Component | Evaluation | Release gate |
|---|---|---|
| Weather | Bias, extremes, wet-day skill, coverage, masked-gap experiments | Source/profile limitations documented; no invalid zero-risk outputs |
| Phenology | Budbreak/bloom/harvest date error, interval coverage, failure-to-flower detection | Better than documented calendar baseline within the released domain |
| Traits | MAE/RMSE or appropriate likelihood, rank correlation, calibration | Consistent evidence of useful performance on grouped test cases |
| Selection | Top-k recovery and utility/regret relative to the best observed eligible option | Improves or credibly matches approved baseline; compare only genuinely evaluated candidates |
| Uncertainty | Interval coverage and width; support-state reliability | Calibration assessed by region/system and not concealed by aggregate averages |
| Applicability | Performance versus climate novelty, genetic relatedness and management support | Abstention/support boundaries calibrated on held-out cases |
| Product | Reproducibility, permissions, cache isolation, invalid inputs, jobs/failures | All safety/correctness acceptance tests pass |

Preregister primary metrics and practical effect sizes with the scientists before final model comparison. Do not promise an accuracy threshold unsupported by observations. Bloom error of two weeks, for example, may or may not be adequate depending on the relevant freeze window; derive tolerance from the decision.

Report coverage for nominated prediction intervals with sample-size uncertainty. A small test set cannot establish precise regional calibration. If M2 does not beat M1, deploy M1 and document the result. If neither supports ranking at a novel site, deploy climate diagnosis plus rules or abstention.

### 10.3 Environmental support and lookup

Assess novelty in the same scientifically relevant feature space used by the model, with additional checks for unrepresented extremes and management. A site can have an ordinary annual mean but an unprecedented bloom-freeze or harvest-rain pattern.

Learn support thresholds from held-out error/coverage curves where possible. Geographic distance and nearest analog similarity are explanatory context, not sufficient release criteria. Genetic support for an untested advanced line is an additional axis.

Do not transfer a nearby cell's rank list without testing the approximation. Interpolate trait predictions only where the method has been validated; ranks are discontinuous and should be recomputed after constraints and utilities. Outside the supported anchor domain, enqueue exact target inference or abstain. Model fitting stays offline in either case.

### 10.4 Prospective validation

Start planning trials in week one, not after the UI is finished. Select a small set of approved candidates and controls across contrasting Florida environments. Include management contrasts where feasible, randomized blocks, replication, harmonized trait protocols and local microclimate logging.

Choose the final trial size through variance estimates, power/precision or simulation, plant availability and practical constraints; do not invent a statistically sufficient fixed number of sites. Prioritize environments that test model disagreement and fill important gaps, not just the easiest collaborator sites.

Record site soil/substrate, plant age, planting material, management, phenology, marketable yield and fruit quality. Assess multiple bearing seasons. International pilot sites expand the domain only as their observations accumulate. Field evidence for a perennial crop cannot be compressed into a twelve-week software milestone.

## 11. System architecture and serving flow

### 11.1 Recommended initial stack

- **Web:** TypeScript, React/Next.js and MapLibre for the coordinate interface and four result panels.
- **API/orchestration:** Python FastAPI with validated request/result schemas.
- **Scientific core:** a versioned R package extracted from Paul's reviewed functions and the selected modeling implementation. Invoke a fixed R entry point from workers, using structured files/arguments. Do not duplicate the science in Python initially.
- **Metadata/results/jobs:** PostgreSQL with PostGIS for spatial lookup.
- **Weather/features/model artifacts:** partitioned Parquet plus manifests in local/object storage; DuckDB for offline exploration where useful.
- **Execution:** separate API and durable worker processes in containers; explicit R, Python and JavaScript dependency locks.

No GPU, Kafka, Kubernetes or separate vector database is required for the first release. Add services only in response to measured operational needs. Heavy model fitting is offline; hot cached responses do not start R or fit a model.

### 11.2 End-to-end flow

```text
Pin + management + authenticated visibility policy
    │
    ├── validate coordinate; resolve land/admin context and source grid cells
    ├── resolve versioned climate/soil/science/model/catalog artifacts
    │
    ├── complete cached result → return four panels + provenance
    │
    └── cache miss → durable job → return job ID/status
                        │
                        ├── acquire/validate missing weather and ground soil
                        ├── derive seasons, clock support and baseline risks
                        ├── apply documented management assumptions
                        ├── retrieve eligible candidate trait predictions
                        │     or run approved target inference with fixed model
                        ├── evaluate support, constraints, utility and uncertainty
                        └── atomically publish result + reproducible report
```

Use `202 Accepted` for a cold analysis that requires acquisition or computation. Provide status polling and clear stages rather than pretending every new world pin returns instantly. Initial performance objectives: cached API response around two seconds or less under the tested load; cold-path timing measured and displayed honestly. Upstream data queues can dominate cold latency.

Use a durable PostgreSQL-backed job queue with leases, retry/backoff, deduplication, concurrency limits and atomic completion. Process crashes must not lose requests. A web-process background task alone is not the durability boundary. Start with one worker and scale after measuring queue pressure.

### 11.3 Versioning and cache identity

A result manifest includes baseline and season policy, raw-source versions/checksums, variable-specific cells, QC policy, soil source/depth, management assumptions, feature/phenology versions, model version, utility-index version, genotype catalog version, audience scope and build revision.

Public climate data can be shared across users. Genotype outputs must be scoped by authorization policy. A climate-cell cache hit must not return another user's pin or another location's soil. Keep request geometry in the response envelope and include soil/site-specific inputs in the final-result identity.

Store trait summaries for all eligible candidates, not just the top five. That supports correct filtering, approved index updates, explanation and later reranking without retraining. Store richer posterior draws selectively if their decision value justifies the size.

### 11.4 Minimal API/data contract

```json
{
  "latitude": -26.312389,
  "longitude": -50.080639,
  "management": "open_ground"
}
```

Authentication and catalog policy are resolved server-side. The client cannot grant itself breeder access by adding a role field.

The result schema must include:

```text
analysis_id, status, evidence_status
request: pin, management
provenance: source cells, baseline, versions, coverage, assumptions
production_clock: supported options, method, evidence, limitations
calendar: establishment and bearing-stage intervals, status per stage
risks[]: hazard, quantity, unit, valid_seasons, severity, uncertainty
candidates[]: approved identity, rank, utility/traits where valid,
              reasons, uncertainty, evidence, limitations
diagnostics: environmental/genetic/management support, optional analogs
warnings[], report_reference
```

Unknown values are `null` with a machine-readable reason. No climate-only response should contain made-up cultivar rows to satisfy a UI layout.

### 11.5 Repository organization to implement

```text
apps/web/                       two-input, four-output interface
services/api/                   requests, authorization, results
services/worker/                durable acquisition/analysis jobs
packages/schemas/               versioned shared contracts
science/blueberryR/             reviewed weather/phenology/risk functions
science/models/                 training, validation, prediction exports
pipelines/                     source adapters, QC, feature/artifact builds
config/                        source profiles, thresholds, utility policies
tests/fixtures/                 permitted synthetic/unit and public benchmarks
tests/integration/              fresh-run and API workflow checks
docs/                          methods, decisions, data dictionary, runbooks
infra/                         containers, deployment and backup configuration
```

Keep private breeding data, credentials and large weather artifacts outside Git. Synthetic fixtures are acceptable for software tests, clearly labeled; they must never be presented as scientific evidence or real predictions.

### 11.6 Security and operations

Enforce visibility on registry, prediction, report and export paths. Test that public requests cannot reveal restricted selection names, trait values, exact private trial coordinates or cached breeder responses. Publish only approved named-reference detail.

Keep source credentials on the server. Accept coordinates and enums, not arbitrary download URLs or shell fragments. Pin source endpoints and executable entry points. Bound request size, coordinate precision, user rate and worker concurrency.

Maintain backups, restore tests, structured job logs, data-quality alerts, artifact lineage and rollback to the previous model/index. Track failures by data acquisition, scientific support and infrastructure rather than returning a generic successful-looking report.

Deploy first on the university machine or an approved persistent host with HTTPS, a durable database and protected artifact storage. Confirm institutional network/storage policies before public exposure. Publishing the public cultivar experience is a separate gate from deploying the private breeder pilot.

## 12. Offline sampling and scale

Build the initial archive around trial/reference cells and real user requests. For proactive expansion, choose representative environmental clusters across the intended blueberry domain, retaining important tails such as late freeze, warm winter, wet harvest and low light. Avoid a sample dominated by many geographically close, climatically duplicated locations.

For each anchor, preserve historical season variation and compute predictions under supported management scenarios. Validate any approximation from anchor predictions to a new target against direct fixed-model inference. An anchor's resemblance to Florida does not establish adaptation in an unobserved region.

Illustrative raw-value arithmetic for a 2011–2025 archive:

| Pack | Raw numerical values only |
|---|---|
| 10,000 cells × 5,479 days × 6 daily float32 variables | About 1.31 GB |
| 10,000 cells × 131,496 hours × 2 hourly float32 variables | About 10.52 GB |

These are not download-size or total-storage promises. Timestamps, coordinates, quality flags, file overhead, raw copies, indexes and backups increase storage; compression can reduce it. Measure the actual archive and source-request overhead on a small sample before scheduling expansion. Coordinate requests that share native cells should not duplicate those series.

Begin on ordinary CPU infrastructure. A 16–32 GB RAM pilot host is a planning starting point, not a measured requirement. Model fitting can require a separate larger machine: one dense 10,000 × 10,000 float64 matrix alone occupies about 0.8 GB, and training may allocate several matrices and temporary copies. Benchmark actual algorithms and use low-rank/iterative methods if the dataset requires them.

Keep a capacity sheet covering weather cells, retained variables, artifact versions, concurrent jobs, model-training memory and backup retention. Do not purchase a GPU or provision a distributed cluster before a model or benchmark justifies it. Obtain actual hosting costs after the deployment location and institution's available resources are known.

## 13. Delivery roadmap and acceptance gates

These estimates assume Rohit is substantially full-time, Paul is available for regular method reviews, and Patricio, Diego and Gerardo can resolve data/science decisions promptly. They are planning ranges, not promises of validated global agronomy.

| Milestone | Indicative timing | Deliverable | Gate |
|---|---|---|---|
| A. Contracts and reproducible baseline | Week 1 | Decision register, source manifests, schemas, isolated R extraction, trial-data request | Clean execution of selected functions; explicit unresolved assumptions |
| B. Climate vertical slice | Weeks 1–2 | Papanduva + reference-site weather ingestion, QC, CLI/JSON diagnosis, first source benchmark | Dated records, correct units/time, tested missingness; no fake genotype layer |
| C. Usable diagnosis application | Weeks 3–4 | Two inputs, four panels with honest unavailable states, durable jobs, soil context, qualitative management layer | End-to-end reproducibility and correctly labeled evidence |
| D. Approved rule-based pilot | Approximately weeks 3–6, dependent on catalog | Catalog policy, verified adaptation matching, report export, breeder review | No unauthorized line; no unsupported claims or filled-out fake rankings |
| E. Model-development benchmark | Approximately weeks 5–8 after usable data access | Phenotype/genotype QC, M1/M2, grouped CV, index sensitivity and support analysis | Locked evaluation and scientific review; no automatic promotion of M2 |
| F. Regional research beta | Approximately weeks 9–12+, conditional on data | Selected model artifacts, validated lookup/inference, uncertainty, protected access, operations | Beats or justifiably matches baseline in stated domain; abstains outside it |
| G. Public experience | After catalog/privacy/quality gates | Public climate diagnosis and approved cultivar subset | Authorization, report/cache isolation, plain-language limitations |
| H. Broader adaptation evidence | Subsequent bearing seasons | Prospective multi-site validation and calibrated management effects | Actual field outcomes; separately approved domain expansion |

Some tasks overlap: start trial design and metadata capture immediately, build the UI after the climate slice works, and audit historical reports in parallel. Do not wait for a deep-learning model before delivering the diagnosis app.

For a mostly solo effort, expect a longer and more variable schedule—roughly 12–20+ weeks for a substantial research beta is a more prudent planning envelope than assuming all specialist work fits twelve weeks. Missing phenotype linkage or approvals can dominate elapsed time regardless of developer speed.

### First ten working days

| Days | Work | Tangible output |
|---|---|---|
| 1–2 | Freeze source copies/checksums; record proposed requirement corrections; define input/output schemas; send structured data-handover checklist through the project team | Data inventory, decision register, schema examples, explicit blocking dependencies |
| 2–3 | Isolate Paul's climate helpers from global state and machine paths; establish locked setup and fresh-process tests | Small executable science package with provenance |
| 3–5 | Fetch Papanduva and UF reference weather; normalize timestamps/units; build QC and boundary tests | Versioned weather manifests and coverage report |
| 5–6 | Implement reviewed seasonal metrics and baseline phenology; reconcile selected Papanduva discrepancies | Climate diagnosis JSON plus comparison table |
| 6–8 | Benchmark available weather profiles against stations and audit missingness/threshold sensitivity | Source-selection evidence; unresolved-limitations list |
| 7–9 | Add management assumptions, ground-soil adapter and support states | All four scenarios executable without fabricated efficacy |
| 9–10 | Connect minimal interface, job status and four panels; review with Paul/Patricio | Demonstrable one-pin vertical slice and prioritized next sprint |

The handover checklist and stakeholder contacts above describe future team actions, not messages already sent by this review.

### Definition of done for the first working app

For Papanduva and the reference locations, each management choice produces either a reproducible result or a precise unsupported/missing-data state. A user can submit a new valid land coordinate, observe job status and receive the same four categories. Risks are computed from real dated weather; time and coverage rules are visible. Genotype candidates appear only when approved metadata support them. A climate-only result is acceptable before breeding data arrive, but it is not presented as completion of the genotype-model milestone.

### Definition of done for the model-enabled beta

The training data and permitted use are documented; the model beats or credibly matches the baseline on relevant held-out cases; calibration and applicability are reported; rankings are reproducible under a fixed utility policy; restricted material is protected; and exact target inference/lookup behavior is tested. Publish a model card describing unsupported regions, genotypes, systems and traits.

Neither definition implies commercial-success probability, global cultivar validation, or a complete long-term field-trial result.

## 14. Essential test suite

Build tests alongside the first extracted functions, not at the end.

**Time and physics:** leap day, crop year spanning December, hemisphere-specific season, local-solar versus UTC boundary, Celsius/Kelvin, radiation/precipitation accumulation conventions, exact threshold boundaries, below-freezing exclusion for the bounded chill-hours definition, and synthetic known-answer chill sequences.

**Missingness:** completely missing harvest rain remains unknown; a missing cold interval cannot create a no-freeze claim; absent bloom due chill failure is distinguished from missing observation; stateful chill gaps follow policy; stage coverage is not inferred solely from row count.

**Management and biology:** open pots retain fruit-rain exposure; a tunnel does not automatically erase freeze; pots/tunnels do not restore chill; production-calendar changes trigger recalculated stage risk; establishment and mature-bearing windows are labeled separately.

**Model and index:** genotype/marker IDs are aligned; train/test leakage checks; matrix/kernel orientation; fixed utility scales; missing SE never becomes certainty; adding/removing irrelevant candidates does not rescale other utilities; uncertain candidates are not rewarded for missing metadata; catalog filtering precedes serving.

**API and operations:** invalid/offshore coordinates; incomplete source data; upstream timeout; crash/restart mid-job; duplicate requests; idempotent retries; model rollback; concurrent public/private requests; cached results with different pin/soil context; expired catalog permissions; backup restoration.

**Regression:** reviewed reference functions and a small approved public fixture set, plus the Papanduva reconciliation table. Do not make known erroneous historical values the acceptance oracle. For scientific changes, store both the expected change and its justification.

## 15. Research experiments worth doing

Preregister a small number of consequential experiments rather than a large model leaderboard:

1. **Weather-source experiment:** Does the selected higher-resolution profile improve stage-specific cold/rain/chill estimates against independent observations, and where does it not?
2. **Phenology experiment:** Do genotype-aware stages improve out-of-site trait prediction and decision quality compared with fixed seasonal windows?
3. **G×E experiment:** Does M2 improve new-site selection regret and calibrated trait prediction beyond M1 and breeder rules?
4. **Genetic-information experiment:** For sparsely observed candidates, what is gained by pedigree, genomics, dosage-aware representations and optional non-additive effects?
5. **Management experiment:** Can measured protected/open contrasts support transportable microclimate and response parameters? Until then, which recommendations change under plausible assumptions?
6. **Index experiment:** Which shortlist decisions survive reasonable approved weight changes, uncertain traits and adverse seasons?
7. **Support experiment:** Can novelty diagnostics identify conditions where prediction error increases enough that the app should abstain?

Enviromic models have been studied using deployment-like cases such as known genotypes in new environments and new genotypes in new environments. That is a useful evaluation template, not evidence that published gains in another crop will transfer to this one. Source: [Costa-Neto et al., 2021](https://www.frontiersin.org/journals/plant-science/articles/10.3389/fpls.2021.717552/full).

Use model disagreement and uncertainty to help choose informative trial locations, subject to scientific feasibility and breeder priorities. Do not retrain on the application's own predicted recommendations as though they were observed success. New field outcomes need protocol/QC before entering the next training release.

## 16. Scope boundaries and subsequent research

Do not include in the initial release: reverse geography search, the old tonight-freeze application, live weather alerts, a full cover-control menu, automatic chemical-management prescriptions, live model training on click, a global hourly cube, or universal suitability for all blueberry species.

A perennial planting decision also extends beyond the historical baseline. The initial app must clearly say it characterizes recent historical conditions, not provide a specific forecast for an orchard's lifetime. A later research track can evaluate climate-change scenarios with downscaling/bias-correction and uncertainty appropriate to the traits and hazards. Do not quietly substitute those scenarios into the historical risk percentages.

Commercial viability also depends on water quality, labor, infrastructure, market access, licensing, plant availability and on-site agronomy. These are not quantified by climate similarity or genomic prediction. A “best current trial candidate” result is not a site investment recommendation.

## 17. Final decision summary

The recommended build is a small, rigorous climate-and-management application that grows into a model-enabled recommendation platform. Reuse Paul's useful scientific components and reports as starting evidence, repair their reproducibility and missing-data behavior, and obtain the missing fitted-model/trial inputs rather than reconstructing predictions from HTML.

The strongest improvements over the current specification are:

1. Evidence-bounded global access instead of assumed global cultivar accuracy.
2. Genotype-specific seasonal exposures instead of climate similarity as a substitute for performance.
3. Measured or explicitly provisional management effects instead of automatic risk removal.
4. Authorized broad training separated from a narrow, versioned serving catalog.
5. Fixed utilities, uncertainty propagation and deployment-matched validation instead of an arbitrary rank score.
6. Demand-driven point weather acquisition and durable jobs instead of a global data-download prerequisite.
7. A useful first app in weeks, a data-dependent model beta afterward, and field validation on the crop's actual biological timeline.

The first implementation milestone should be: **one pin, four management scenarios, real dated weather, a tested scientific packet, and an honest evidence state**. That creates the foundation on which the requested final genotype recommendation system can be built and evaluated.
