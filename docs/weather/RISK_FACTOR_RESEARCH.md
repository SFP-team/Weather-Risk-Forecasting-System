# Weather-derived risk factors for blueberry: review of current formulas and catalogue of additions

Date: 2026-09-15. Status: research synthesis with one data check. Nothing here is implemented in `production.py` yet; every proposal names its inputs, window, threshold, source and confidence. Sources were gathered by eight parallel literature scouts (chill, forcing/phenology, freeze, heat/VPD/radiation, rain/disease, water balance, pollination/pests, system classification); numbers marked [unverified] could not be traced to a primary source or are cross-crop.

Species tags: SHB = southern highbush, RE = rabbiteye, NHB = northern highbush.

## 1. Verdict in one page

What the current formula set gets right:

- Hourly temperature for chill and daily data for rain, freeze-day and heat-day counts is the correct split. No source supports estimating chill from daily means.
- Base 7 °C for forcing degree-days is well supported (NHB 7.1–8.0 °C; UF SHB bloom model uses 7 °C).
- −2.2 °C (28 °F) is the published full-bloom kill threshold for highbush; 32 °C / 35 °C are the published green-fruit / ripening-fruit heat-damage triggers; 10 mm is a reasonable generic heavy-rain day.
- Ranking risks by frequency of winters with an event, with Wilson intervals, is honest for 15 winters.
- Refusing to invent a chill-triggered calendar for evergreen sites is right; UF/IFAS defines the evergreen system by management, not by chill.

What is wrong or unsupported, in order of consequence:

1. **Chill definition.** We count hours T < 7.2 °C with no lower bound from 1 Nov to 1 May. Every reference (UF AgroClimate, UGA, UF HS216, Epagri) counts 0–7.2 °C (32–45 °F) and stops around 1 Mar; sub-zero hours do not chill. Our rule over-counts by 15–30 % in Georgia and counts post-bloom spring hours. More important, chill hours in any form mis-rank warm-winter sites: on our own data Papanduva has 183 h but 26 Dynamic-Model chill portions, the same as Waldo (346 h, 28.5 CP). The Dynamic Model should become the primary chill metric.
2. **Chill requirement of 50 h.** No commercial cultivar needs less than ~150 h (Avanti) and most SHB need 200–400 h, RE 350–650 h. A 50 h anchor fires in November/December and makes the whole downstream calendar a function of autumn weather. Every later date, and therefore every stage risk, inherits this error.
3. **150 °C·d to budbreak** has no source. The only published SHB numbers are 225 (Emerald) and 302 (Jewel) GDD base 7 to 50 % bloom, accumulated from 1 January. Bloom should be predicted from a 1 Jan GDD accumulation with cultivar-class targets, not from chill date + 150.
4. **Harvest = flowering start + 70–110 d** fits RE (75–94 d bloom to ripe) but overshoots SHB (56–72 d in Georgia; ~65 d in Florida). One offset for both species is wrong.
5. **Disease-day rule** (15–28 °C AND RH ≥ 85 % AND rain ≥ 0.1 mm) has no duration term, uses one temperature band for pathogens with different optima (Botrytis/mummy berry 2–20 °C at bloom; anthracnose 20–27 °C at harvest), and the 0.1 mm rain condition on a 55 km grid is nearly always true. Replace with a leaf-wetness proxy and per-disease rules.
6. **Freeze risk only at full bloom.** Green fruit after petal fall is the most sensitive stage (0 to −1 °C), and swollen buds before bloom are hit by late-winter freezes at −4.4 to −7 °C. We count neither. Duration also matters; the March 2017 Georgia loss was "several hours below 28 °F".
7. **VPD as a window mean of daily means** never reaches any physiological breakpoint and hides the afternoons that matter. No blueberry VPD threshold exists. Demote or drop.
8. **Longest dry spell across the whole season** treats a January dry run (dormant, ET0 ~1 mm/day) the same as an April one (fruit fill, 4–6 mm/day). Replace with a stage water balance.
9. **Classification.** The 100/300 h cuts are loosely anchored (Sebring ≈108 h is the evergreen zone; 300 h is Lyrene's "sufficient" for NE Florida) but only for the 0–7.2 °C definition. The multi-feature test "freezing hours ≤ 1" contradicts UF/IFAS: evergreen zones do freeze and are protected. "Semi-evergreen" is not a UF/IFAS term; "Transition" is more honest.
10. **Nothing for pollination weather, post-harvest flower-bud initiation heat, spotted-wing drosophila, waterlogging, or the warm-spell-then-freeze pattern**, all of which have usable published thresholds.

## 2. Data check: chill definitions on our 18 hourly cells (2011–2025 means)

`pipelines/weather/chill_comparison.py`; full per-winter values in `chill_comparison.json`. Window Oct–Feb (north) / Apr–Aug (south) except the "current rule" column (Nov–May, T < 7.2, no lower bound).

| Site (cell) | Current rule h | 0–7.2 °C h | h below 0 °C | Chill portions (CP) | CH/CP | Hours > 21.1 °C mid-Nov–mid-Feb | p10 CH |
|---|---:|---:|---:|---:|---:|---:|---:|
| Georgia / Alma | 801 | 603 | 116 | 44.7 | 13.5 | 172 | 490 |
| Valdosta | 749 | 569 | 102 | 42.4 | 13.4 | 192 | 457 |
| Homerville | 694 | 533 | 91 | 39.9 | 13.4 | 208 | 421 |
| Folkston | 577 | 460 | 65 | 36.2 | 12.7 | 221 | 330 |
| Waldo | 420 | 346 | 38 | 28.5 | 12.1 | 297 | 221 |
| Citra | 350 | 296 | 26 | 23.4 | 12.6 | 376 | 183 |
| Wild Goose | 274 | 238 | 17 | 19.7 | 12.1 | 453 | 138 |
| H&A | 210 | 186 | 10 | 17.0 | 11.0 | 524 | 103 |
| Frogmore | 134 | 127 | 2 | 17.8 | 7.1 | 419 | 54 |
| Astin North East / Clear Springs | 173 | 155 | 7 | 14.1 | 11.0 | 587 | 79 |
| Dole | 142 | 126 | 7 | 11.8 | 10.7 | 636 | 56 |
| River Valley / Wauchula | 132 | 120 | 5 | 11.1 | 10.8 | 648 | 53 |
| Barben / Sebring / Lake Placid | 116 | 104 | 5 | 9.3 | 11.2 | 704 | 46 |
| Arcadia | 86 | 80 | 2 | 8.3 | 9.7 | 694 | 38 |
| PF Berry | 87 | 79 | 2 | 7.3 | 10.8 | 769 | 34 |
| Astin East | 40 | 40 | 0 | 8.7 | 4.5 | 577 | 10 |
| Okeechobee | 30 | 30 | 0 | 3.9 | 7.7 | 943 | 2 |
| Papanduva | 199 | 183 | 6 | 26.1 | 7.0 | 166 | 98 |

Readings:

- **Calibration.** Barben cell 104 h vs FAWN Sebring published mean 108 h (same 32–45 °F Oct–Feb definition). Waldo/Citra 346/296 h vs FAWN Gainesville 503 h: the grid undercounts by ~30–40 % at the deciduous end, consistent with the +1 °C warm night bias found in the 2020 station comparison. Any chill threshold applied to grid data must be read with that bias.
- **Papanduva.** 183 chill hours (central-Florida-like) but 26 CP (Waldo-like). Its cool hours are at 7–12 °C, which chill hours ignore and the Dynamic Model counts. The Brazilian literature reports Emerald/Jewel cropping with 0 h < 7.2 °C but 211 h < 12 °C. The chill-hour classification of Papanduva as "Semi-evergreen" is a model artefact.
- **CH/CP ratio** is 12–13.5 in Georgia/north Florida (literature SE US: 14.4 ± 1.0) and falls to 7–11 in south Florida and Brazil. A single conversion factor is not safe; compute CP directly.
- **Negation hours** (> 21.1 °C in mid-winter, the UF HS216 negation criterion) run from 170 (Alma) to 940 (Okeechobee). Chill hours cannot represent this; the Dynamic Model does.
- **The current rule inflates counts** by 60–200 h at Georgia sites through sub-zero hours and March–April hours.

## 3. Formula scorecard

| Current formula | Verdict | Replacement or amendment | Source |
|---|---|---|---|
| Chill = hours T < 7.2 °C, 1 Nov–1 May | Change | Primary: Dynamic Model chill portions from hourly T, 1 Oct–1 Mar (N) / 1 Apr–1 Sep (S). Comparator: hours 0 ≤ T ≤ 7.2 °C, same window (AgroClimate/UGA-compatible). Report Safe Winter Chill = 10th percentile across winters. Drop Utah (negative totals in SE US). | Luedeling & Brown 2011; UF HS216; AgroClimate |
| Chill requirement 50 h | Change | Cultivar-class requirement: SHB low 200 h, SHB mid 300–400 h, RE 400–600 h; in CP, derive per cell from that cell's CH/CP or use ~14–28 CP for SHB. Report fulfilment fraction per winter. | UF cultivar patents; UGA 2024 cultivar sheet; Spiers 2006 |
| Budbreak = chill date + 150 GDD base 7 | Change | GDD base 7 from 1 Jan (N) / 1 Jul (S), daily (Tmax+Tmin)/2 − 7. Bloom 10/50/90 % at cultivar-class GDD targets: SHB-early 80/225/370 (Emerald-type), SHB-mid 160/300/445 (Jewel-type), NHB 50 % ≈ 290. Keep base 7. | Kovaleski et al. 2015 JASHS 140:38; Kirk & Isaacs 2012 |
| Flowering = budbreak + 14…35 d | Change | Flowering window = [Bloom10, Bloom90] from the GDD model (≈290 GDD span, ≈5 weeks in a Florida February). | Kovaleski 2015 |
| Harvest = flowering start + 70…110 d | Change | From Bloom50: SHB first ripe +55–65 d, end +35 d later; RE first ripe +75–90 d, end +45 d later. Add +10–14 d when chill by 15 Feb < 300 h (delayed foliation). | NeSmith 2006/2012 (GA FDP tables); Williamson 2002 |
| flower_freeze_days: Tmin ≤ −2.2 °C in flowering | Keep + extend | Stage-aware thresholds: bud swell/break −7 °C; tight cluster/pink −4.4 °C; bloom −2.2 °C (RE −1.7); petal fall/green fruit 0 to −1 °C (RE −1.1). Add severity Σ max(0, θ − Tmin) and, on hourly cells, hours ≤ θ with severe = ≥ 3 h. Add bias variant Tmin − 1 °C. | UGA B1479 (MSU table); NCSU; ACES; Smith 2019 |
| fruit_heat_days Tmax ≥ 32 | Keep, narrow window | Apply only to green-fruit portion (first ~60 % of fruit window). | Yang, Bryla & Strik 2019; WSU |
| fruit_severe_heat_days Tmax ≥ 35 | Keep + add | Add ripening-only count; hourly ≥ 4 h variant; shock variant (Tmax ≥ 35 after a day < 25). | Yang 2019 |
| No bloom heat metric | Add | Days Tmax ≥ 30 °C (RE pollen tube/ovule limit) and ≥ 35 °C (no germination) in flowering window. | Yang et al. 2019 JASHS 144:339 |
| disease_days 15–28 °C & RH ≥ 85 % & rain ≥ 0.1 | Change | Leaf-wetness proxy then per-disease day rules (below). | MSU anthracnose model; UF Blueberry Advisory System; UMaine Botrytis |
| harvest_heavy_rain_days ≥ 10 mm | Keep + add | Keep as generic. Add rain-split event: 2-day rain ≥ 20 mm after 7 dry days (< 5 mm), ripe fruit only [expert-set]. | UGA 2025; Marshall 2008 |
| *_vpd_mean_kpa | Demote | No blueberry threshold. If kept, compute from Tmax and minimum RH (or hourly) and count days ≥ 3 kPa; never rank. | S. Afr. J. Bot. 2023 (qualitative only) |
| production_max_dry_days (< 1 mm run) | Change | Stage climatic water balance: rain − Kc·ET0 (Hargreaves from Tmin/Tmax/latitude), Kc 0.3 dormant → 0.95 fruit → 1.05 post-harvest; fruit_deficit_days = trailing 5-day rain < 5-day Kc·ET0. Keep dry-run as diagnostic. | Dourte, Haman & Williamson 2010; FAO-56; Bryla 2011 |
| production_gdd base 7 | Keep | | |
| production_radiation_mean_mj | Keep, descriptive | Yield plateaus at 50 % PAR; radiation is a risk only with Tmax ≥ 32. | Lobos 2013 |
| Class: < 100 Evergreen, 100–299 Semi, ≥ 300 Deciduous | Change | Use 0–7.2 °C hours Oct–Feb (or CP). Evergreen-obligate < 150 h; Transition 150–299 (both systems documented); Deciduous SHB 300–499; SHB+RE ≥ 400; NHB ≥ 800. Report reliability R = fraction of winters meeting the group requirement. | UF HS1362; Lyrene 2008; FBGA FAWN climatology |
| Multi-feature: freezing hours ≤ 1, month mean Tmin > 7.2, Tmean > 12.8 | Change | Drop freezing-hours and Tmin tests as class conditions (evergreen zones freeze and are protected). Replace with advisory flag F_hard = fraction of winters with a day ≤ −2 °C between 1 Dec and bloom end. Daily-only proxy for evergreen: coldest-month mean ≥ 16 °C [extrapolated from Lyrene's 13–16 °C ⇔ 100–400 h]. | HS216; HS1362 |
| Evergreen sites: no calendar | Keep refusal, add anchored calendar | Management anchors (N): hedge 1 Jun; flower-bud initiation 15 Aug–31 Oct; floral budbreak 1 Nov; Bloom50 1 Feb (Avanti-type) / 15 Feb (Arcadia-type); harvest 15 Feb–31 May. Shift six months for Brazil. Then apply freeze (any hour ≤ 0 °C induces dormancy/defoliation), FBI heat, water balance. | HS1362; HS1363; Growing Produce 2019 observations |

## 4. New risk factors, by stage

All inputs are variables we hold. "Hourly" means the 19 stored cells; "daily" is global.

### Winter and dormancy

| Metric | Inputs | Rule | Why | Confidence |
|---|---|---|---|---|
| Chill portions, Safe Winter Chill | hourly T | Dynamic Model cumulative CP; p10 across winters | Standard for warm winters; handles negation | High |
| Chill negation hours | hourly or daily Tmax | hours (or days Tmax) > 21.1 °C, 15 Nov–15 Feb | UF HS216 negation criterion | Medium (flag only) |
| Premature-forcing index | daily Tmean | GDD7 accumulated before chill requirement is met | Flowers forced before leaf buds are ready → poor leaf:fruit | Medium [threshold unverified] |
| Warm-spell-then-freeze | daily Tmax, Tmin | 3-day run Tmax ≥ 20 °C followed within 14 d by Tmin ≤ −4.4 (or ≤ −2.2 near bloom); report ΔT | Deacclimation: Tifblue lost 11 °C hardiness in 3 d at 20 °C; 2017 Georgia 85 °F → 29 °F | High |
| Winter kill | daily Tmin | days Tmin ≤ −15 °C | Dormant SHB hardiness; Brazil highlands only | Medium |
| Xylella cold-curing | hourly T | winter hours < 6 °C; flag < 200 h | Grape-derived, SHB bacterial leaf scorch | Low [cross-crop] |

### Bud swell to bloom

| Metric | Inputs | Rule | Why | Confidence |
|---|---|---|---|---|
| Stage-aware freeze | daily Tmin (+ hourly hours/dose) | thresholds −7 / −4.4 / −2.2 / −1 by stage; severity and hours | Most losses happen at green fruit and swollen bud, not only full bloom | High |
| Protection feasibility | Tmin, wind, dew point | protectable = Tmin ≥ −5 °C & wind ≤ 4.5 m/s; dry radiative freeze = Tmin ≤ 0 & Td ≤ −3.3 °C & wind ≤ 2 m/s (tissue ≈ air − 2 °C); wet-bulb Tw = T − (T − Td)/3 | Distinguishes protectable radiative frosts from unprotectable advective freezes; sprinkler limits | High (UGA B1479, HS216) |
| Pollination-favourable days | Tmax, rain, wind, RH, shortwave | day with Tmax ≥ 15 °C & rain < 1 mm & wind < 4.5 m/s & RH_mean < 78 % & radiation ≥ 60 % of window max; report fraction and longest unfavourable run (≥ 3 d ≈ one flower cohort lost, receptive 3–5 d) | Good-weather-only exposure doubled fruit set and berry weight (NHB); RH ≥ 78 % days = poor pollination in Florida SHB | High for thresholds, Medium for run rule |
| Bloom heat | daily Tmax, hourly T | days Tmax ≥ 30 / ≥ 35 °C; hourly ≥ 4 h at 35 | Pollen tube optimum 18 °C, none at 35 °C; ovule degeneration after 4 h at 30 °C (RE) | High (RE), unverified for SHB |
| Botrytis blossom blight day | LWD proxy, T | LWD ≥ 8 h & 15–25 °C, or ≥ 13 h & 10–28 °C | Bloom-only pathogen | High |
| Mummy berry day (RE ×1.5) | LWD proxy, T, chill | LWD ≥ 5 h & 8–20 °C or ≥ 10 h & 2–8 °C; exclude Tmax ≥ 30; gate on ≥ 400 h chill (RE) | Primary infection budbreak→bloom | Medium |
| Flower thrips pressure | Tmean | DD base 10 °C from 30 d before flowering | Proxy constants (F. occidentalis) | Low |

### Fruit development

| Metric | Inputs | Rule | Why | Confidence |
|---|---|---|---|---|
| Green-fruit heat / ripening heat | Tmax | ≥ 32 °C first 60 % of window; ≥ 35 °C last 40 % | Published cooling triggers | High |
| Berry-surface proxy | Tmax, shortwave | est_berry = Tmax + 7 if SW ≥ 20 MJ else + 3; flag ≥ 42 °C | Sun-exposed berries run 7–11 °C above air; damage at 42–48 °C in 1.5–4 h | Medium (Oregon offsets) |
| Heat-shock days | Tmax | Tmax ≥ 35 after a day < 25 | Observed damage pattern | Medium |
| Fruit heat load | Tmax | Σ max(0, Tmax − 30) | Sustained +5 °C cut fruit weight 39 % (NHB) | Medium |
| Cool-night ripening slowdown / warm-night | Tmin | nights < 10 °C; nights ≥ 21 °C | UGA C1294 | Medium |
| Stage water balance | Tmin, Tmax, rain, lat | rain − Kc·ET0_Hargreaves; deficit days; P/ETc ratio | Deficit in final expansion cuts fruit weight 10–15 % | Medium (no soil store) |
| Waterlogging | rain | 2-day ≥ 50 mm, or 3 days each ≥ 10 mm, or 5-day ≥ 100 mm; within 14 d of a freeze-protection night | ≥ 48 h saturation drives Phytophthora; SHB > RE | Low [thresholds are proxies] |
| Anthracnose risk day | LWD proxy, T | Moderate: LWD ≥ 12 h & 20–27 °C or ≥ 16 h & 15–30; High: ≥ 20 h & 20–27 or ≥ 24 h & 15–30 | MSU Enviroweather table; UF advisory | High |

### Harvest

| Metric | Inputs | Rule | Why | Confidence |
|---|---|---|---|---|
| Rain-split event | rain | 2-day ≥ 20 mm after 7 days < 5 mm; or 1-day ≥ 25 mm | Splitting is drought-then-rain on ripe fruit; cultivar-dependent (Tifblue/Climax high, Premier/Magnolia low) | Medium [mm unverified] |
| Wet-fruit harvest days | rain, LWD proxy | rain ≥ 1 mm or LWD ≥ 10 h | Alternaria / post-harvest rot | Medium |
| Anthracnose days | as above | | | High |
| SWD pressure | Tmean, RH | DD base 7.2 upper 30 °C; generations in harvest = DD/200; active days = 15–28 °C & RH ≥ 70 % | Peak April–May coincides with SHB harvest; early harvest escapes | High for DD, Medium for active-day rule |
| Wind days | wind | days wind ≥ 10 m/s in flowering and fruit windows | Bee shutdown, mechanical loss; hail not resolvable at 55 km | Medium |

### Post-harvest (next year's crop)

| Metric | Inputs | Rule | Why | Confidence |
|---|---|---|---|---|
| Flower-bud-initiation heat | Tmean, Tmax | days Tmean ≥ 28 / Tmax ≥ 29 °C, 1 Aug–31 Oct (N) / 1 Feb–30 Apr (S) | Initiation reduced at 28 vs 21 °C (SHB Misty); UGA 29.1 °C | Medium |
| Post-harvest water deficit | as water balance | harvest end + 60 d | Deficit after harvest cuts next year's flower buds | Medium |
| Root-activity soil-temp proxy | Tmean | 7-day mean ≥ 8 °C; optimum 14–18 °C | NHB only; air–soil offset unknown | Low |

### Leaf-wetness proxy (needed by the disease rules)

Hourly cells: wet hour = rain > 0 or (T − Td) ≤ 2 °C or RH ≥ 90 %; a wet period ends after 4 dry hours; LWD = run length, T_wet = mean T of the run. Daily fallback: LWD ≈ 14 h if rain ≥ 2 mm; 10 h if 0.2–2 mm; 8 h if rain < 0.2 and (Tmin − Td) ≤ 1 °C and RH_mean ≥ 80 %; else 0 [heuristic; calibrate on the hourly cells before global use]. RH ≥ 90 % was validated at Piracicaba, Brazil (0.87–0.92 fraction correct).

## 5. Recommended implementation order

1. **Chill**: add Dynamic Model CP as primary, 0–7.2 °C band as comparator, window Oct–Feb / Apr–Aug, Safe Winter Chill. Re-express class cuts. (Evidence: Section 2.)
2. **Phenology**: cultivar-class chill requirements; GDD-from-1-Jan bloom model with 10/50/90 targets; species-specific harvest offsets; delayed-foliation adjustment. Everything downstream depends on this.
3. **Freeze**: stage-aware thresholds, severity, hourly hours/dose, protection-feasibility and warm-spell-then-freeze flags. This is the main southern-Georgia constraint (UGA C1311).
4. **Pollination-favourable days** and **bloom heat**: cheap, daily-only, high-confidence thresholds, and currently a blind spot.
5. **Disease**: leaf-wetness proxy, then Botrytis/mummy berry at bloom and anthracnose at harvest; rain-split event.
6. **Water**: Hargreaves ET0 + stage Kc balance; waterlogging flag.
7. **Evergreen calendar** (management-anchored) so south Florida sites get stage risks.
8. **SWD degree-days**, FBI heat, post-harvest deficit.

Each step should add a named profile version and keep the old one for comparison, exactly as `legacy_paul_v1` is kept now.

## 6. What this review does not settle

- No SHB in-situ pollen/ovule or stage-specific freeze data exist; RE and NHB numbers are borrowed. Cultivar spread is large (1–2 °C at bloom; 22–51 % photosynthesis loss at 30 °C).
- No published chill-portion requirement for any UF/UGA cultivar; Dynamic Model constants come from peach.
- No published mm threshold for rain splitting; no hours × °C freeze dose–response; no blueberry VPD breakpoint; no blueberry hail or fog model.
- Hargreaves ET0 on grid Tmin with a +1 °C warm bias will under-estimate demand; needs a one-off comparison with Penman–Monteith from the same grid.
- Every threshold is applied to 55 × 60 km grid values that run warm at night and smooth convective rain. Field-versus-airport radiative deficits of 5–7 °C are reported in the Southeast. Thresholds should be reported with a bias-adjusted variant until a station correction is fitted.
- Supervisor decisions still needed before any of this is treated as evaluation: chill definition, cultivar classes to run, and pre-registered expected system/bloom/harvest for the 18 panel sites.

## Primary sources (selection)

- Luedeling & Brown 2011, chill model comparison and Dynamic Model constants: https://pmc.ncbi.nlm.nih.gov/articles/PMC3077742/
- Dynamic Model reference implementation: https://rdrr.io/cran/ChillModels/src/R/dynamic_model.R
- UF/IFAS HS216 chill, freeze and dew-point guidance: https://ask.ifas.ufl.edu/publication/HS216
- UF/IFAS HS1362 evergreen vs deciduous systems: https://ask.ifas.ufl.edu/publication/HS1362
- UF AgroClimate chill calculator: https://cloud.agroclimate.org/tools/chillCalculator/
- Kovaleski et al. 2015, SHB bloom GDD model: https://journals.ashs.org/view/journals/jashs/140/1/article-p38.xml
- Kirk & Isaacs 2012, base temperature and bloom GDD: https://journals.ashs.org/view/journals/hortsci/47/9/article-p1291.xml
- NeSmith 2012, SHB fruit development period Georgia: https://www.tandfonline.com/doi/full/10.1080/15538362.2011.619430
- UGA B1479 freeze protection and stage thresholds: https://fieldreport.caes.uga.edu/publications/B1479/commercial-freeze-protection-for-fruits-and-vegetables/
- NCSU freeze damage: https://content.ces.ncsu.edu/blueberry-freeze-damage-and-protection-measures
- Rowland et al. 2008 deacclimation: https://journals.ashs.org/view/journals/hortsci/43/7/article-p1970.xml
- Yang et al. 2019 RE flowering heat: https://journals.ashs.org/view/journals/jashs/144/5/article-p339.xml
- Yang, Bryla & Strik 2019 berry heat damage: https://journals.ashs.org/view/journals/hortsci/54/12/article-p2231.xml
- MSU anthracnose risk model: https://www.canr.msu.edu/news/new-blueberry-anthracnose-risk-prediction-model-launched-for-michigan-growers
- Gama et al. 2021 UF Blueberry Advisory System: https://apsjournals.apsnet.org/doi/10.1094/PDIS-09-20-1961-RE
- Tuell & Isaacs 2010 bloom weather and fruit set: https://pubmed.ncbi.nlm.nih.gov/20568598/
- Lyrene & Williamson 2003 humidity and pollination: https://journals.flvc.org/fshs/article/download/86496/83412
- Dourte, Haman & Williamson 2010 SHB crop coefficients: https://www.tandfonline.com/doi/full/10.1080/15538362.2010.510419
- Bryla 2011 blueberry ET and irrigation: https://cdn.intechopen.com/pdfs/22695/InTech-Crop_evapotranspiration_and_irrigation_scheduling_in_blueberry.pdf
- UF PP374 Phytophthora root rot: https://ask.ifas.ufl.edu/publication/PP374
- Wiman et al. 2016 SWD degree-days: https://ncbi.nlm.nih.gov/pmc/articles/PMC4943995
- Epagri Santa Catarina blueberry zoning: https://ciram.epagri.sc.gov.br/ciram_arquivos/site/boletins_culturas/risco_climatico/SC_Mirtilo_Zoneamento.pdf
- FBGA FAWN chill climatology (Sebring 108 h, Gainesville 503 h): https://www.floridablueberrygrowers.org/index.php?option=com_dailyplanetblog&view=entry&category=blueberry-blog&id=99:chill-accumulation-trends-in-florida-are-we-heading-toward-warmer-winters-
- Lyrene 2008 'Emerald' release, chill ⇔ coldest-month mean: https://www.growables.org/information/LowChillFruit/documents/BlueHortS2.pdf
- UGA C1311 south Georgia constraints: https://extension.uga.edu/publications/detail.html?number=C1311
