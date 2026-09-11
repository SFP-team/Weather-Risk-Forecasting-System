# Location × growing-system analysis: implementation plan

Date: 2026-09-11. Research/design refinement, not an implemented management model or a new acquisition run. Extends Sections 6–7 of `IMPLEMENTATION_PLAN.md`. Cultivar data remain deferred to Part 3.

## Decision and current position

Build a location-based comparison of open-ground, open-pots, tunnel-ground and tunnel-pots. Start with interpretable weather exposures, soil context and explicit management assumptions. Do not train an ML model to imitate arbitrary risk scores or recommend a commercial structure from daily weather alone.

Implemented: global daily archive 2010–2025; hourly temperature/dewpoint at 14 pilots; coordinate extraction/QC; three-site climate report; provisional 50/100-hour stage scenarios. Not implemented: soil acquisition, ET0/water-balance model, tunnel microclimate response, management suitability ranking or cultivar application. Existing shortwave summaries are not a validated light-limitation model. The latest recorded 45 software tests are not validation of the proposed modules.

## Causal model

Location weather + site/root-zone information + explicit management configuration
→ canopy and root-zone exposures
→ reference-stage timing (and later calibrated cultivar phenology)
→ six hazard summaries, residual constraints and evidence quality.

Report both fixed-calendar comparisons (isolate exposure changes) and, only when justified, shifted-calendar comparisons (include phenology changes). Avoid attributing a calendar effect to physical rain interception. Unmet chill and unsupported seasons remain visible; conditional means must carry their denominator.

## Six metrics and their limits

| Domain | First defensible outputs | Additional information before biological-risk claims |
|---|---|---|
| Chill | Hourly chill counts under named definitions, seasonal distribution; optional separately tested Dynamic Model | Hourly data at new locations; cultivar requirement and dormancy strategy; no exact chill from daily averages |
| Freeze | Daily minimum, days below explicit thresholds, overlap with reference flowering; hourly duration where available | Stage-specific sensitivity, local flower/canopy temperatures, active protection; coarse grids miss cold extremes |
| Rainfall | Stage total, wet/heavy-rain days, maximum daily/multi-day rain; separate fruit and root-zone pathways | Roof geometry/coverage schedule, wind-driven rain, field runoff/drainage, leaf wetness; daily rainfall is not a flood or splitting model |
| Heat | Maximum temperature, threshold days and multi-day events, stage overlap; hourly duration where available | Berry/root temperature, ventilation, radiation and water status; no universal damage threshold |
| Drought/water supply | Dry spells; documented outdoor FAO Penman–Monteith ET0; precipitation minus ET0 labelled climatic balance | Crop coefficients, rooting volume, soil/substrate storage, effective rain, irrigation capacity/reliability and water quality; ET0 is not crop water use |
| Radiation | Daily/stage shortwave energy and low-light periods; explicitly assumed PAR/DLI conversion if needed | Cover spectral transmission, shade/aging/condensation, canopy interception and crop response; solar energy is not sunshine duration |

All metrics return units, window, source profile, valid years/expected years, historical distribution and exclusions. Thresholds are configurable and versioned; provisional values are never silently presented as universal blueberry tolerances. Short records characterize the selected historical baseline, not orchard-lifetime climate forecasts.

## Growing-system representation

Separate root-zone choice from cover choice. Retain four simple comparison labels but expand each cover into a specification: rain shelter or enclosed high tunnel; roof material/transmission; side/end openings and ventilation control; dates covered; heating/active cooling; shading; runoff collection. Pots need substrate, container volume/color, drainage/elevation and irrigation specification. Missing attributes produce conditional results, not assumed optimal management.

| Scenario | Potential benefit to investigate | Risks that remain or may increase |
|---|---|---|
| Open ground | No cover light loss; no enclosure heat accumulation | Direct fruit rain, native/amended soil constraints, cold and water supply |
| Open pots | Greater control over substrate chemistry/root zone | Fruit rain remains; root heating, small water buffer, irrigation failure, site flooding |
| Tunnel ground | Less direct fruit rain while effectively covered | Native-soil drainage remains; heat/humidity/light tradeoffs; freezing not eliminated |
| Tunnel pots | Combine rain interception with managed substrate | All cover tradeoffs plus irrigation/root-zone dependencies; neither storm-proof nor chill-restoring |

Initial matching rules are hypotheses for review: rain-dominated harvest conditions motivate evaluating an open-sided rain shelter; cool conditions may motivate seasonal covers subject to frost and shifted-phenology checks; hot conditions require testing ventilation/shade tradeoffs, not automatically adding a closed tunnel; low-light conditions require particular caution about cover losses. Wind/snow/hail structural safety requires local extremes, manufacturer engineering and applicable design requirements, not mean daily wind from this archive.

No blanket percentage risk reduction. Quantitative exposure transformations require a supporting experiment and transfer limits. Where unavailable, show qualitative direction and explicitly chosen sensitivity ranges, not fabricated confidence intervals. Literature parameters must record crop/site/system, comparator, season, measurements and uncertainty.

## Soil and water layer

Use bounded on-demand SoilGrids subsets for pilot locations: pH, sand/silt/clay, organic carbon, bulk density and coarse fragments at relevant standard depths, with quantiles, units and source version. Preserve depth intervals rather than silently averaging. Cache the exact sampled pixel separately from the user's coordinate. Current official documentation reports REST paused; verify supported WCS/WebDAV access during implementation and return unavailable on failure. No global soil download is needed.

Treat mapped soil as predicted regional context, not measured drainage or an unconditional planting veto. Request local pH/EC, soil profile/seasonal water table, drainage/amendment history and irrigation-water alkalinity/EC where available. Terrain can flag possible context but is not a hydrological flood diagnosis. In pots, suppress native-soil chemical suitability scoring, not ground flooding/access considerations; evaluate substrate and irrigation instead. Unknown water quality or supply is an explicit constraint.

## Implementation sequence and acceptance gates

1. **Unify the existing metric engine.** Reuse tested coverage/QC and stage code; add daily rain-event, heat-event and radiation summaries. Named configs for thresholds/windows. Test units, missing/flagged values, cross-year windows and denominators. Complete pending weather reliability gates in parallel.
2. **Add bounded soil and atmospheric-demand adapters.** Start at the three demonstrated sites, then the remaining pilots/diverse probes. Verify SoilGrids scaling/depth/quantiles against official metadata. ET0 must audit wind height, humidity convention, elevation/pressure and net-radiation calculation; retain estimated inputs. Verify against published known-answer calculations. Do not apply outdoor ET0 unchanged inside a tunnel.
3. **Implement a management evidence registry and four-scenario evaluator.** Encode exposure pathways, prerequisites and unknowns. Test that open pots retain fruit rain; unheated tunnels do not erase frost; cover cannot create chill; missing irrigation does not imply no drought. Compare scenarios as tradeoffs, not a single arbitrary score.
4. **Generate one location × four systems report.** Begin Papanduva, Citra and Waldo, using existing weather. Show six exposure rows, baseline, intervention mechanism, residual issue, evidence class, valid seasons and required field checks. Explicitly separate not-applicable, unavailable and observed-zero outputs. No site-specific system winner without evidence.
5. **Validate and then increase model complexity.** Collect paired outside/inside air temperature/RH, radiation and rainfall interception; soil/substrate temperature/moisture; irrigation volumes; actual cover operation and stage dates. Use enough seasons/events for the intended claim, hold out sites/years, and compare a simple model against added complexity. Only then estimate management response and later connect cultivar-specific phenology and performance.

Proposed components: `pipelines/weather/risk_metrics.py`, `pipelines/soil/`, `config/management/`, `science/management/` and a reproducible comparison-report generator. These paths are planned, not created implementations.

## Supervisor decisions needed now

- Approve the first comparison sites, priority hazards and reference seasonal windows.
- Specify which actual structures and root-zone systems are realistic locally, including cover/ventilation schedule and whether heating is present.
- Confirm provisional chill/phenology settings with Paul; request measured paired system data or trials if available.
- Identify available field soil, drainage and irrigation-water evidence. Full cultivar/genomic data are not required to start this phase.

Continue engineering with clearly labelled unknowns while awaiting these inputs. They constrain validated recommendations, not all progress.

## Research basis and transfer limits

- [Ogden et al., blueberry leaf/bud temperature experiment](https://pure.korea.ac.kr/en/publications/leaf-and-bud-temperatures-of-southern-highbush-blueberries-vaccin/): daytime warming did not imply nighttime frost protection in the studied tunnels. Do not infer a universal warming offset.
- [Matamala et al., 2023, cover materials at two Chilean blueberry locations](https://www.mdpi.com/2223-7747/12/20/3556): material-specific radiation and crop responses support explicit cover attributes; do not transfer reported yield changes as global coefficients.
- [Smrke et al., 2021, planting system and protected environment](https://www.mdpi.com/2311-7524/7/12/591): contextual evidence for root-zone temperature differences; not a general pot-temperature correction.
- [UF/IFAS commercial container guidance](https://ask.ifas.ufl.edu/publication/HS1476): substrate aeration/water retention, irrigation, drainage and pH/EC monitoring remain essential in pots. Its container-leachate guidance is not a universal threshold for mapped field-soil pH.
- [UF/IFAS site/soil guidance](https://ask.ifas.ufl.edu/publication/MG359): regional guidance supports local soil/drainage assessment rather than unconditional decisions from a map pixel.
- [ISRIC layer definitions](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html) and [access documentation](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html): predicted 250 m properties, depths and uncertainty; documented alternatives to paused REST access. Static soil predictions are not annual moisture observations.
- [FAO reference evapotranspiration](https://www.fao.org/4/X0490E/x0490e05.htm): reference atmospheric demand is distinct from actual crop water use and soil-water stress.
- [OSU blueberry development](https://extension.oregonstate.edu/catalog/how-blueberry-plants-develop-grow): chill, development and cold sensitivity require biological context.
- [MSU lighting guide](https://www.canr.msu.edu/floriculture/uploads/files/Indoor%20lighting%20guide-mid.pdf): DLI measurement definition, not evidence for a blueberry-specific optimum.

Three parallel research reviews informed this plan (weather metrics, protected systems, soil/root zone). No new runtime tests, downloads, soil adapter or management implementation were performed in this planning task.
