# Critical review of Astra's science work

Reviewer: AstraScienceReview (Claude Opus 5.5 worker). Checked on 2026-10-11.
Scope: the science deliverables of Astra (`openai-codex/gpt-6-astra`, project turns 2026-09-15 to 2026-10-05): the `stage_risks_v2` risk gate, the planting window, the global phenology review and its corrections, the app user guide, and Astra's open recommendations.
Method: I read the code and docs in the repository, recomputed facts from the 71 saved snapshots in `dist/snapshots/`, and opened the cited sources online. Three research sub-checks opened most sources under my direction on 2026-10-11. I opened UF/IFAS HS1525 directly. No repository file other than this one was changed.

Conventions. "Verified" means I saw it in code, saved data or the source. Text marked [inference] is my own judgement. File references use `path:line`. Line numbers refer to the working tree on 2026-10-11.

---

## 1. Summary verdict

**Overall: careful, honest and mostly correct work, with three material weaknesses.** Astra's strongest output is the research hygiene. It separated measurements from derived values, corrected earlier project errors, and refused to tune results to expected answers. Of 20 registered phenology sources I checked, 17 fully support the claims Astra made from them, 3 partly support them (S1, S8, S14), and none is misattributed by Astra. Astra's corrections of earlier notes (Kirk and Isaacs, Carlson and Hancock, Epagri, Piracicaba, Campa and Ferreira) are all correct.

The three material weaknesses:

1. **The risk gate is correctly coded but weak as a ranking tool.** "At least one event day" definitions over long stage windows saturate. Harvest heavy rain ranks at 34 of the 41 saved sites where the winter calendar applies, and disease weather at 26. With 12 to 15 winters, the 50% gate is statistically noisy near the boundary. Failed winters leave the denominator, which contradicts Astra's own phenology review. Combined with the later v3 clock gate, nine saved sites lose their winter calendar because chill fails in 4 to 6 of 15 winters, yet chill shortfall never reaches the headline.
2. **The planting decision is defensible in principle but weakly sourced and not signed off.** No source supports Paul's "105 to 30 days before budbreak" rule, so rejecting it as a formula is reasonable. But Paul explicitly asked for a planting window "not computed independently" of flowering and harvest. Astra replaced it with an independent window built from two home-garden guides, and no supervisor sign-off is recorded. UF/IFAS's commercial guide HS1525 (July 2026) recommends planting in the early spring and fall root-growth periods. It also says new UF cultivars can crop within 12 months, which contradicts a condition `planting.py` shows to users.
3. **Several Astra documents are now stale.** The phenology review section 1, the calendar audit JSON and a v3 risk note still describe the v2 model as current, and the audit can no longer be reproduced from `dist/snapshots/`.

The user guide (Astra's last deliverable) is accurate on nearly every threshold, gate, unit and behaviour I tested. I found 1 material inaccuracy (planting guidance for arbitrary pins), 2 label mismatches against its own "exact spelling" promise, 1 time-convention imprecision and 1 incomplete statement.

---

## 2. Area 1: `stage_risks_v2` design and its inheritance by `stage_thermal_v3`

### 2.1 What the code does (verified)

- Profile `stage_risks_v2` copies `legacy_paul_v1` and adds `risk_min_frequency: 0.5`, `risk_min_valid_years: 12`, `require_applicable_calendar: True` and the pollination and warm-midwinter constants (`pipelines/weather/production.py:59-67`). `stage_thermal_v3` inherits all of these (`production.py:98-99`).
- For each family, `risks()` collects per-winter values from complete windows only (`production.py:893-894`, `event_values()` at `:796-804`). An event is a value of at least 1 day, or at least `pollination_gap_days` (4) for the v3 pollination family (`:807-809`). Chill shortfall counts winters with chill below the requirement (`:896`).
- Decision order is: `not_applicable` (unsupported calendar), then `definition_pending` (exposure-only), then `insufficient_data` (n below 12), then `below_frequency` (k/n below 0.5), else `ranked` (`:899-918`). Ranking sorts by frequency with competition ranks for ties (`:927-934`). Wilson 95% intervals are attached (`:922`, `:727-734`).
- Exposure-only families are warm midwinter, flowering dry spell and fruit dry spell, plus the cold-or-wet pollination proxy when no bee model is active (`:889-890`).
- Disease weather is one family. In v2 it is the sum of three complete stage counts, which equals the union of stage events (`:799-801`). In v3 it is `crop_high_infection_days` from flowering start to harvest end: anthracnose index at least 0.50 on any day, or Botrytis at least 0.70 during flowering (`:538-542`, `:802-803`).
- Per-winter stage windows, not median calendars, drive exposures (`season()` at `:688-697`).
- Tests cover the 12-winter and 50% boundary, ties, missing windows and descriptive families (`tests/weather/test_production.py:154`, `:176`, `:205`, `:221`).
- `sensitivity()` now reads `by_id`, so the crash Astra predicted for a demoted flowering freeze is fixed (`production.py:1206`).

**Implementation verdict: correct.** The code does what the design says, and missing data never becomes zero.

### 2.2 Evidence from the 71 saved snapshots (verified, recomputed 2026-10-11)

| Measure | Value |
|---|---|
| Saved sites where the chill-triggered calendar applies | 41 of 71 |
| Ranked at those 41 sites: harvest heavy rain | 34 |
| Ranked: disease weather | 26 |
| Ranked: flowering freeze | 6 |
| Ranked: bud freeze | 1 (Burgaw, 8/15) |
| Ranked: fruit severe heat | 1 |
| Harvest window length, all complete site-years at those sites (n = 597) | median 41 days, p10 35, p90 53 |
| Waldo | harvest heavy rain 14/15 and disease 13/15 ranked; flowering freeze 3/15 demoted |
| Burgaw, NC | disease 15/15, harvest rain 14/15, flowering freeze 10/15, bud freeze 8/15 ranked |

Sites where the calendar is not applicable only because fewer than 12 of 15 winters produce a calendar, while chill shortfall stays below the 50% gate:

| Site | Calendars | Chill shortfall | Decision |
|---|---|---|---|
| Barben, Dole, Lake Placid, Sebring, us-fl-sebring | 9/15 | 6/15 | below_frequency |
| River Valley, Wauchula, Tzaneen (ZA) | 10/15 | 5/15 | below_frequency |
| Ovalle (CL) | 11/15 | 4/15 | below_frequency |

At these nine sites, the only reason for the missing winter calendar is unmet chill (`status_counts` show only `complete` and `chill_not_met`). Yet the Overview "Top risks" card shows managed-cycle scan risks only when the scan is primary (`dist/app.js:316`, `:340-352`). Chill shortfall is therefore never on the headline card, even when it is ranked (for example PF Berry 11/15, Penguin 14/15, George 15/15).

### 2.3 Is the gating sound?

**Recurrence gate of 50% in at least 12 winters.**
- Verified: the gate applies to the point estimate. Binomial arithmetic for a family with a true recurrence p:

| n winters | Needed k | P(ranked) if p = 0.3 | p = 0.4 | p = 0.5 | p = 0.6 | p = 0.7 |
|---|---|---|---|---|---|---|
| 12 | 6 | 0.12 | 0.33 | 0.61 | 0.84 | 0.96 |
| 15 | 8 | 0.05 | 0.21 | 0.50 | 0.79 | 0.95 |

  Wilson intervals at the boundary are wide: 8/15 gives 0.30 to 0.75, and 6/12 gives 0.25 to 0.75.
- [inference] The gate is a reasonable display policy, and the code and README say so (`production.py:161`). It is not a decision threshold. A family with a true 40% recurrence enters the headline about one time in five at n = 15, and a true 60% family drops out about one time in five. The UI should show the interval next to the gate decision, which the detail tables already do, and should avoid wording that treats "below 50%" as "not a risk". The demoted list does this well.
- [inference] Paul's example was "about half of winters". A frequency gate alone cannot express freeze severity. UF/IFAS HS216 reports that early-flowering SHB at Gainesville averaged losses above 60% without overhead irrigation (verified quote via sub-check, https://ask.ifas.ufl.edu/publication/HS216), yet Waldo's flowering freeze at 3/15 is demoted. A severity or degree-hour measure next to frequency, as the earlier risk research proposed (`docs/research/2026-09-21/03_science_second_opinion.md:42`), is still missing.

**"At least one day" events over long windows.**
- Verified: every family except the v3 pollination gap uses a one-day event (`production.py:807-809`). Harvest windows are about 41 days and the v3 disease window runs from flowering start to harvest end.
- [inference] With one-day events, frequency rises with window length. In humid climates the harvest rain and disease families saturate near 100%, which is why they dominate the headline (34 and 26 of 41 sites). Astra saw this in its own plan ("heavy rain would remain") but kept the one-day event. A per-stage-day rate, a multi-day threshold, or ranking against a site's own climatology would separate sites better. The managed-cycle scan (later work) already uses share-of-stage-days for these families (`production.py:955-964`), which is the better design and is inconsistent with the winter ranking.

**Denominator excludes failed winters.**
- Verified: crop families count only winters with complete stage windows (`production.py:893-894`). Winters with `chill_not_met`, `gdd_not_met_within_horizon` or `stage_gdd_not_met` carry no metrics (`:660-687`) and leave the denominator.
- Verified: Astra's own phenology review says the opposite: "For a season where chilling is insufficient or the stage does not occur, retain that outcome in the denominator" (`docs/weather/GLOBAL_PHENOLOGY_REVIEW.md:348`).
- [inference] Excluding failed winters is the right rule for "frequency of freeze given a crop", and the code reports `valid_years` and `total_years` for every family (`production.py:920-921`). But the headline frequency is then conditional on a completed calendar. At marginal sites the user cannot see that the crop cycle itself failed in some winters. The approved scan-accounting fix (section 6) should also cover this path.

**Interaction with the v3 clock gate (later work, inherited constant).**
- Verified: v3's `chill_clock()` reuses `risk_min_valid_years` (12) as the minimum number of calendar winters (`production.py:1122`). It also exempts chill shortfall from `not_applicable` only at non-tropical, non-evergreen sites (`:899-900`, `:1124-1125`).
- [inference] One constant now means two different things: "enough winters to estimate a frequency" and "the calendar works in 80% of winters". The result is the nine-site gap in section 2.2. Either show chill shortfall on the Overview whenever it is the reason the calendar is not applicable, or align the two gates.

**Single disease family.**
- [inference] Sound. Treating flowering, fruit and harvest disease weather as one family with one annual event (the union) stops one weather type from filling all three headline slots. Requiring all three windows to be complete (v2) is strict but honest.
- Verified stale text: the v3 risk note still says "Disease weather is one family with three complete stage windows" (`production.py:939`, also in `dist/snapshots/waldo.json`). Under v3 the family uses one flowering-to-harvest high-risk count.

**Exposure-only families.**
- [inference] Sound. Warm midwinter hours, dry spells and the cold-or-wet pollination proxy have no published loss threshold. Keeping them as `definition_pending` exposures avoids invented severity. The README states this clearly (`docs/weather/production/README.md:123`).

**Verdict for Area 1.** The design is a clear improvement on "rank everything" and the implementation is correct. The weak points are saturation of one-day events, the noisy point-estimate gate, the conditional denominator, and (through later v3 reuse) a chill-failure blind spot on the Overview.

---

## 3. Area 2: planting window

### 3.1 What the code and docs do (verified)

- `planting.py` returns one fixed regional window for registry regions only: Florida mid-December to mid-February, Georgia December to February, Santa Catarina June to August (`pipelines/weather/planting.py:8-49`). Unknown regions return `unavailable` (`:64-68`).
- `location_api.analyze()` passes a region only when the pin exactly matches a saved site (tolerance 1e-7 degrees). Any other pin becomes `{'name': 'Selected location'}` without a region (`pipelines/weather/location_api.py:121-122`, `:136`). Arbitrary pins therefore never get planting guidance.
- 30 of the 71 saved sites show a window: all saved Florida, Georgia and Santa Catarina sites, including evergreen-majority Arcadia, Okeechobee and Astin East and tropical-edge Homestead.
- Paul's R rule exists as described: `planting_end_before_budbreak_days <- 30`, `planting_window_length_days <- 75`, under the comment "Preliminary phenology offsets after estimated budbreak", with no source (`southern_brazil_blueberry_climate_analogs.R:86-92`, `:1219-1220`). The scout report `docs/research/2026-09-21/01_paul_r_planting_window_and_chill.md` describes the rule and its month-day median defect correctly (lines 14-16).
- Paul's recorded requirement: "Planting window from his R code ... required as a **single** window chosen to align with flowering and harvest, not computed independently" (`docs/weather/SUPERVISOR_REVIEW_RIVER_VALLEY.md:23`). His overlap rule also defines the production window as "planting → flowering → harvest" (`:9`).
- Astra's own record says the implementation choices are "provisional implementation decisions, not a record of subsequent supervisor sign-off" (`SUPERVISOR_REVIEW_RIVER_VALLEY.md:53`). The README still says Paul's rule "is still not adopted" (`docs/weather/production/README.md:108`).

### 3.2 Source checks for the planting claims

| Claim in `planting.py` or README | What the source says | Verdict | Link and status |
|---|---|---|---|
| Florida: UF/IFAS CIR1192 recommends mid-December to mid-February, bare-root or container plants | "The best time to plant blueberries in Florida is from mid-December to mid-February. Bare-root or container-grown plants can be used." Page title "CIR1192/MG359: Blueberry Gardener's Guide", Williamson and Phillips, revised December 2025 | supported | https://ask.ifas.ufl.edu/publication/MG359 (opened) |
| Florida condition: remove first-season flowers before fruit set | "During the first growing season, remove all flowers before fruit set occurs." (home-garden guide) | supported for the home-garden guide; contradicted for commercial UF cultivars by HS1525 (next rows) | MG359 (opened) |
| Georgia: UGA C946 recommends winter transplanting, no dates | Only planting-time sentence: "Obtain your plants in time for winter transplanting." No months; fall planting not mentioned. Krewer and NeSmith, first published 1999, reviewed 2017 | supported | https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/ (opened) |
| Georgia: remove first-season flowers; remove most second-season flower buds on highbush | "The first year, remove any flowers or fruit..."; "in the second season remove all or nearly all flower buds" | supported | C946 (opened) |
| Georgia guide is home-garden guidance for several types | Covers rabbiteye, SHB, NHB; says SHB "can be less desirable choices for the home gardener" | supported | C946 (opened) |
| Santa Catarina: Embrapa-authored "Grande potencial" recommends winter transplanting while dormant | "As mudas devem ser transplantadas no inverno, quando estiverem em dormência." (Plants should be transplanted in winter, while dormant.) Credits "Embrapa Uva e Vinho" and "Embrapa Clima Temperado", no named authors; posted 10 Nov 2015 | supported for the statement; "Embrapa-authored" is partly supported (unit credits only) | https://revistacultivar.com.br/artigos/grande-potencial (opened) |
| Prefers two-year-old stock | "Usar preferencialmente mudas de dois anos de viveiro..." | supported | same (opened) |
| "Irrigation must be available to prevent establishment losses" | "A irrigação é importante para evitar perdas após o plantio" (irrigation is important to avoid losses after planting) | partly supported: "must" overstates "important" | same (opened) |

New sources the review did not use:

| Source | What it says | Relevance |
|---|---|---|
| UF/IFAS HS1525 "Establishing New Southern Highbush Blueberry Plantings in Florida", Phillips, Williamson, Nunez, Harmon, Dittmar, Cabezas, July 2026, CC BY-NC-ND 4.0 | "Blueberry plants have two periods of fast root growth: one in the early spring and one in the fall. It is advisable to plant during these periods to increase transplant success." Also: irrigation matters "especially if they are planted during summer or early fall", and "newer southern highbush cultivars from the UF/IFAS blueberry breeding program can produce a marketable crop within 12 months of planting." | The commercial UF guide for this lab's own crop type. It does not give the winter window and contradicts the "remove first-season flowers" condition for new UF cultivars. https://journals.flvc.org/edis/article/download/140453/148081 (opened) |
| Embrapa Documentos 96, Santos and Raseira 2002, "O Cultivo do Mirtilo" | "As mudas podem ser plantadas, durante toda a fase de dormência. Em geral, o plantio é realizado com mudas de dois ou três anos." | Primary Embrapa text agreeing with the dormancy rule, with named authors. https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/744138/1/documento96.pdf (opened by sub-check) |
| UGA C1278 and C1267 (Rubio Ames and Espinoza 2023, commercial) | No planting window found | No commercial Georgia window located. https://fieldreport.caes.uga.edu/publications/C1278/blueberry-production/ (opened by sub-check) |

### 3.3 Judgement on rejecting "105 to 30 days before budbreak"

Verified facts:
- No reviewed source links planting dates to modelled budbreak. The R constants carry no citation.
- Astra's own arithmetic showed the rule gives autumn intervals: River Valley 16 October to 30 December, Homerville 11 September to 25 November, Papanduva 9 April to 23 June (brief, science plan section 4).
- HS1525 recommends early spring or fall planting for commercial Florida SHB.
- The README benchmark scores Paul's rule at 38% recall and 33% precision of published planting months (`README.md:108`). The benchmark's Florida and Georgia planting months are themselves taken from the same home-garden guides, as its notes say: "Planting months come from UF home-garden guidance (CIR1192)" for `us-fl-homestead`, and "Planting months follow UGA dormant-season (home/backyard) guidance" for `us-ga-alma` (`pipelines/weather/benchmark_sites.json`).

Assessment [inference]:
- Rejecting the formula as a biological rule is justified. Nursery establishment depends on stock, root growth and irrigation, not on a bearing bush's budbreak.
- The replacement is weaker than its framing. It rests on home-garden guides, while a commercial UF guide published two months before Astra's work points to fall and early-spring planting. For Florida, Paul's rule (autumn) and HS1525 (fall) may agree better than the displayed winter window does.
- The 38% benchmark result does not "fail to rescue" the rule in a fair test. The Florida and Georgia labels share a source with the replacement, so the comparison is circular there.
- Governance: the decision overrides an explicit supervisor requirement ("not computed independently") without recorded sign-off. Astra disclosed this honestly, but the open question has not been closed. [inference] Paul may mean "planting" as the start of a production cycle in his analog workflow (`production_phase_months <- 1:8 # compare first 8 months after planting`, R line 66), not nursery establishment. That needs his answer, not more modelling.
- The "approximately December to February" and "June to August" display months for Georgia and Santa Catarina are invented conventions. They are labelled as such in code and README, which is honest, but users see them as month bars.

**Verdict for Area 2: partly sound.** The formula rejection is right on evidence. The replacement should use commercial sources, drop or qualify the first-season flower condition for Florida, and go back to Paul as a decision.

---

## 4. Area 3: global phenology review, calendar audit and Astra's corrections

### 4.1 Source-check table (20 registered sources plus 6 related sources)

Status key: opened = fetched and matched; opened-limited = abstract only, paywall or bot wall. All checked on 2026-10-11.

| # | Source | Claim checked (where Astra used it) | What the source says | Verdict | Link and status |
|---|---|---|---|---|---|
| 1 | S7 Kovaleski et al. 2015, JASHS 140:38 | Emerald and Jewel at Citra; bloom 2012 and 2013; mature plants; freeze protection; hydrogen cyanamide late December; base 7 C from 1 January; coefficients -3.3740/0.0150 and -4.6172/0.0153; pseudo-R2 0.88/0.91; F50 225/302 GDD; printed formula [(Tmax - Tmin)/2] - Tbase; initiation early August vs late September | All confirmed: "8-year-old 'Emerald' and 'Jewel'"; "Hydrogen cyanamide (1.5%) was applied in late December of each year"; "starting on 1 Jan."; "Peak bloom (50% bloom) for 'Emerald' occurred at 225 GDDs ... 302 GDDs for 'Jewel'"; formula printed with a minus sign; weather from FAWN. Derived F10 to F90 spans 293.0 and 287.2 GDD check out | supported | https://journals.ashs.org/view/journals/jashs/140/1/article-p38.xml (opened) |
| 2 | S10 Kirk and Isaacs 2012, HortScience 47:1291 | Five NHB cultivars in SW Michigan; field bloom at three sites in 2009 and 2010, not 15 years; bases 7.14 to 7.96 C; 291 GDD field vs 420 greenhouse; bases for bloom only | "sampled during the 2009 and 2010 field seasons"; "ranged from 7.14 °C for 'Duke' to 7.96 °C for 'Liberty'"; "291 accumulated GDDs under field conditions compared with 420"; "relevant only to bloom prediction" | supported; the earlier "15 yrs harvest + bloom" note (`04_validation_data_and_protocol.md:17`) was misattributed, and Astra's correction (`:5`) is right | https://journals.ashs.org/view/journals/hortsci/47/9/article-p1291.xml (opened) |
| 3 | S40 Carlson and Hancock 1991, JASHS 116:774 | 15-year, 13-cultivar Michigan first-picking study; 22 to 69% lower SD of prediction error | "Fifteen years of Michigan harvest data ... first-picking dates of 13 cultivars"; "reduced the standard deviation of the prediction error from 22% to 69%" | supported | https://journals.ashs.org/view/journals/jashs/116/5/article-p774.xml (opened-limited, abstract) |
| 4 | S9 NeSmith 2014 UGA dossier TH-917/921/948 | Star, Camellia, TH-948 at Alapaha and Griffin: 50% flowering, 50% ripening, FDP (66, 73, 65, 67, 55, 54 days); five-year means | All six rows match Tables 1 and 2 exactly; titles "5 Year avg." The five years are not named; FDP is a mean of yearly values with SD, not the gap between mean dates | supported | http://georgiacultivars.com/images/uploads/documents/NeSmith_Blueberry_TH921_TH917_TH948.pdf (opened over HTTP) |
| 5 | S13 NeSmith 2014 Georgia Dawn, HortScience 49:674 | Tables estimate 50% ripening; 10% ripe 7 to 10 days earlier | "The data are estimates of 50% ripening time, and typically berries will begin ripening (10% ripe fruit) 7 to 10 d earlier than this." | supported | https://journals.ashs.org/view/journals/hortsci/49/5/article-p674.xml (opened) |
| 6 | S11 NeSmith 2006, Acta Hort. 715 | Rabbiteye FDP 75.3 to 93.9 days, seven cultivars, two Georgia sites; heat units improve prediction; flowering varies up to 24 days | All three statements quoted in the abstract | supported | https://www.actahort.org/books/715/715_19.htm (opened-limited, abstract) |
| 7 | S12 NeSmith 2012, Int. J. Fruit Sci. | SHB FDP 56.2 to 82.8 days; Emerald 82.8 | Abstract lists Southern Splendour 56.2 to Emerald 82.8. It also says heat units "did not greatly reduce the coefficient of variation" for SHB | supported | https://api.openalex.org/works/doi:10.1080/15538362.2011.619430 (opened, abstract); publisher page blocked |
| 8 | S8 Campa and Ferreira 2018, PLOS ONE | 70 accessions 2012 to 2017; flowering 19 to 66 d; harvest 14 to 51 d; harvest start late May to September; F10, 25% harvest start, more than 90% harvested end; weekly, two plants; "includes cranberry and non-commercial-type accessions" | All numbers and definitions confirmed. Includes V. macrocarpon and V. uliginosum, but the paper calls all 70 "commercial blueberry cvs" | partly supported ("non-commercial-type" is Astra's wording, not the paper's) | https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0206361 (opened) |
| 9 | SERIDA bulletin 2016 (earlier note, replaced by Astra's correction) | "59 cultivars, 2013 to 2016" | Real, separate article by the same authors: "59 variedades ... Datos de los años 2013, 2014, 2015 y 2016" | the old note was accurate for this bulletin; it is a second source, not an error | https://www.serida.org/publicacionesdetalle.php?id=6724 (opened-limited, 403; read via Wayback) |
| 10 | S29 Medina et al. 2018, Piracicaba | 2014/15, open-sided cover, pots, thirty 3-year-old plants per cultivar; 5 h below 7.2 C and 211 h below 12 C; Emerald and Jewel calendars; station 7 km away | All confirmed in Table 1 and text. The paper's own Conclusion 1 says "without the occurrence of temperatures below 7.2 ºC", which contradicts its table | supported; Astra's correction from zero to five hours is right and Astra noted the loose wording | https://revistas.ufg.br/pat/article/download/52093/25717 (opened) |
| 11 | S31 Pandolfo et al. 2017, Epagri zoning | 2017 zoning, not a 2020/21 cultivar trial; chill and frost zoning; average phenology | "Agropecuária Catarinense ... v.30, n.1 ... 2017"; "optou-se por trabalhar com uma fenologia média"; chill hours "<= 7,2°C" (no lower bound); groups I to V from 200 to more than 800 h; no cultivar trial | supported; earlier note (`04:20`) was wrong and Astra's correction is right | https://ciram.epagri.sc.gov.br/ciram_arquivos/site/boletins_culturas/risco_climatico/SC_Mirtilo_Zoneamento.pdf (opened) |
| 12 | S28 Antunes et al. 2008, Pelotas | Eight rabbiteye cultivars, 2003/04 to 2005/06, 164 m; flowering from August; picking December to January; spans 21 to 48 d; bloom start more than 5% open | All confirmed | supported | https://apct.sede.embrapa.br/pab/article/download/382/5609 (opened) |
| 13 | S4 Schuchovski and Biasi 2021 | Pinhais 920 m, 2016 only; forcing 25 ± 2 C; 50% of green-tip buds open; Climax and Powderblue 44 h; Bluegem and Delite 134 h; negative Utah for Climax | All confirmed (Climax Utah -11.0) | supported | https://www.scielo.br/j/babt/a/RzPzN5fYSfPvcVjWGJM6Pqb/?lang=en (opened) |
| 14 | S3 Olmstead et al. 2015 | 23 selections plus Emerald, Primadonna; Citra and Windsor; 0 to 7 C chill at 50/100/150/200 h; Spiers stage 5; 70% criterion; none at 50 h, three at 100 h in older plants; hydrogen cyanamide at Windsor only | All confirmed, including the call for separate vegetative-bud evaluation | supported | https://journal.americanpomological.org/index.php/jofaps/article/download/2867/2871 (opened) |
| 15 | S14 Williamson et al. 2002, HortScience 37:539 | "10 to 14-day harvest advance after hydrogen cyanamide in a low-chill Misty experiment without changing bloom date" (`GLOBAL_PHENOLOGY_REVIEW.md:172`) | Abstract: hydrogen cyanamide "advanced flowering slightly" and "shortened the fruit development period". The 10 to 14 day figure appears only in a secondary citation | partly supported: "without changing bloom date" contradicts the abstract | https://journals.ashs.org/view/journals/hortsci/37/3/article-p539.xml (opened-limited, abstract) |
| 16 | S6 UF/IFAS HS216 | Revised September 2026; temperatures above 70 F from mid-November to mid-February may negate chill; Dynamic Model and chill hours; later flowering trades freeze risk against early-market ripening | Metadata date 9/1/2026; "probably negate some accumulated chilling"; both models described; partial chill bounded 45 to 55 F; trade-off text present | supported | https://ask.ifas.ufl.edu/publication/HS216 (opened) |
| 17 | S16 UF/IFAS HS1362 | Evergreen defined by leaf retention and management; early market about March to May; some cultivars from early March | All quoted on the page; revised April 2026 | supported | https://ask.ifas.ufl.edu/publication/HS1362 (opened) |
| 18 | S1 UGA C1293, Rubio Ames 2024 | Review text: describes flower-bud initiation and floral vs vegetative buds. Astra's 2026-09-25 report: "Delayed leafing can affect fruit development ... UGA's blueberry phenology guidance explains this distinction" | Initiation and bud types are described. No statement that delayed spring leafing affects fruit development; the leaf statement concerns fall defoliation reducing flower buds | partly supported: the review text is supported, the report sentence is not | https://fieldreport.caes.uga.edu/publications/C1293/recognizing-flower-and-vegetative-buds-in-blueberries-blueberry-phenology/ (opened) |
| 19 | S33 Maule technical manual 2014 | Base-7 sums from 1 July; O'Neal flowering mid-August to early September, Brigitta October; maturity late November to January; chill-to-bloom totals are not requirements | All confirmed. Table 4 gives cumulative sums from 1 July. The v3 code values 593 and 665 (`production.py:71-73`) are differences of means (650.8 - 58.1 and 929.8 - 265.1), not printed numbers | supported for Astra; partly supported for later v3 citation | https://portalberries.com/wp-content/uploads/2025/04/Manual-Especificaciones-Tecnica-Economica.pdf (opened) |
| 20 | S35 Steyn, Lötze and Hoffman 2023 | 2020 season at Hex River and Wolseley; 8-42 flowering April to mid-October, harvest August to mid-November; 9-02 peak early August at one site, late September at the other | All in the abstract (Wolseley early August, Hex River late September) | supported | https://agris.fao.org/search/fr/records/65e01dd963b8185d9cb16f1c (opened-limited, abstract) |
| 21 | S32 Lobo Zavalía et al. 2018, Tafí del Valle | 2,279 m; 15 cultivars; 2012 to 2016; bud swelling from September, flowering from October; harvest December to March | All confirmed | supported | https://www.scielo.org.ar/scielo.php?script=sci_arttext&pid=S1851-30182018000200002 (opened) |
| 22 | Lyrene 2008 "Emerald", HortScience 43:1606 (used in RISK_FACTOR_RESEARCH and v3) | 100 to 400 h adaptation range for Emerald; 300 h "sufficient" in NE Florida; 100 to 400 h linked to coldest-month mean 13 to 16 C | "well adapted ... (100 to 400 h below 7 C)"; "300 h below 7 C seems sufficient"; the 13 to 16 C link is stated for the tetraploid low-chill class | supported | https://www.growables.org/information/LowChillFruit/documents/BlueHortS2.pdf (opened) |
| 23 | UF/IFAS MG359 (CIR1192) | Planting claims, see section 3.2 | | supported | https://ask.ifas.ufl.edu/publication/MG359 (opened) |
| 24 | UGA C946 | Planting claims, see section 3.2 | | supported | https://fieldreport.caes.uga.edu/publications/C946/home-garden-blueberries/ (opened) |
| 25 | Revista Cultivar "Grande potencial" | Planting claims, see section 3.2 | | partly supported | https://revistacultivar.com.br/artigos/grande-potencial (opened) |
| 26 | UF/IFAS HS1525 (not used by Astra) | Commercial planting timing | Early spring and fall root-growth periods; first-year crop possible with new UF cultivars | contradicts the home-garden basis | https://journals.flvc.org/edis/article/download/140453/148081 (opened) |

Tally for the 20 registered sources (S1, S3, S4, S6, S7, S8, S9, S10, S11, S12, S13, S14, S16, S28, S29, S31, S32, S33, S35, S40), judged on Astra's own claims: 17 supported, 3 partly supported (S1, S8, S14), 0 unsupported, 0 misattributed. Astra used S33 correctly; only the later v3 code comment cites derived S33 values as if printed.

### 4.2 Findings on the review documents

Verified:
- Astra's corrections in `docs/research/2026-09-21/04_validation_data_and_protocol.md:5`, `docs/research/2026-09-21/03_science_second_opinion.md:5` and `docs/weather/RISK_FACTOR_RESEARCH.md:5` are all supported by the sources above.
- `GLOBAL_PHENOLOGY_REVIEW.md` section 1 (lines 23-40) and `phenology_calendar_audit_2026-09-24.json` describe `stage_risks_v2` with fixed offsets as "the current program". Neither file mentions v3. All 71 files in `dist/snapshots/` now carry `stage_thermal_v3`, so the audit's 235 identical offset tuples cannot be reproduced from the current snapshots.
- Astra warned that the Kovaleski formula typo must "not be silently copied or silently declared resolved" (`GLOBAL_PHENOLOGY_REVIEW.md:114`). Later v3 code states "The paper's printed daily formula (Tmax - Tmin)/2 is a typo for the mean" (`production.py:77-78`) without recording author confirmation.
- The Pelotas engineering comment in v3 (later work) says flowering-to-first-harvest of "116 d cool-spring rabbiteye, Pelotas" is beyond published maxima (`production.py:988-990`). The Antunes Table 1 dates give 120 to 126 days in 2005/06 (bloom 10 August, harvest from 8 to 14 December). The 150-day cap is above both, so there is no effect on results.

Assessment [inference]:
- The review is the best piece of Astra's science work. It is cautious about transfer, separates fitted quantiles from observations, and its parameter-decision table (`GLOBAL_PHENOLOGY_REVIEW.md:322-342`) stopped several unsupported rules (150 h floor, CH/CP conversion, 300 h plus 10 to 14 days) from entering the model.
- Its main gap is that it found the right calibration data but did not extract any. Lyrene 2008 Tables 1 and 2 (Emerald 50% flowering at Windsor 2001 to 2007 and 50% ripe 2002 to 2007), the TH dossier tables, Campa and Ferreira's S1 table and the SERIDA bulletin are dated, cultivar-specific stage records that could seed a validation table now.
- The review is long. For the coordinator, the parameter table in section 10 and the source register are the parts worth reusing.

**Verdict for Area 3: well supported, with small wording errors and stale status text.**

---

## 5. Area 4: `docs/APP_USER_GUIDE.md` accuracy

### 5.1 Guide-accuracy table

| Guide line | Statement | Code or data evidence | Verdict |
|---|---|---|---|
| 186 | Label "No two-thirds majority" | `dist/app.js:209` maps `Transitional` to that label | accurate |
| 191, 193 | Deciduous at 300 h or more; Evergreen needs under 100 h plus warm-winter and low-freezing rules | `production.py:715-724`, profile `:47-52` | accurate |
| 195 | Two-thirds of valid years, 10 of 15 | `production.py:790`, `class_majority: 2/3` (`:53`) | accurate |
| 222-226 | Planting covers selected registered locations; "An arbitrary pin can lack planting guidance even inside one of those regions" | Every non-saved pin gets `{'name': 'Selected location'}` with no region (`location_api.py:121-122`), so `planting_window()` always returns `unavailable` (`planting.py:54`, `:64`) | **inaccurate (understated): an arbitrary pin never receives planting guidance** |
| 243 | Timeline separates winter chill, bud development, flowering, fruit, harvest, whole cycle | `dist/cycle.js:8-13` | accurate |
| 270 | Production chill: below 7.2 C including sub-zero; November to April north, April to September south | `production.py:240-244`, `:274-275` | accurate |
| 271 | Reference chill: 0 to 7.2 C; November to February north, May to August south | `pipelines/weather/evidence_report.py:21-23`; `location_api.py` `summarize()` windows | accurate |
| 293-295 | 91 records, 51 geographic scopes, 23 countries | `dist/evidence/ibo-regional-v1.json`: 91 records, 51 geographies, 23 country codes | accurate |
| 307 | Records outside the baseline are labelled | `dist/evidence.js:315-321`, `:390-391` | accurate |
| 319-321 | 17 C gives 10 GDD; daily mean capped at 30 C after budbreak | `production.py:427-448`, `:459`; budbreak search uses no cap (`:668`) | accurate |
| 331-341 | 100 h chill, 150 GDD to budbreak, 85/375 GDD to flowering, 633/1242 GDD to harvest | `production.py:100-107`, `:668` | accurate |
| 345 | "The harvest-end requirement ... was derived from an older Waldo calendar" | True, but 85 and 633 GDD were derived the same way (`production.py:68-73`) | accurate but incomplete |
| 347 | Budbreak search 450 days from winter start; later stages 300 days | `production.py:36`, `:668`, `:103`, `:459-464` | accurate |
| 351 | A failed later endpoint removes both flowering and harvest windows | `stage_dates()` returns None on any failure (`production.py:465-466`) | accurate |
| 359-361 | Calendar applies at abs(latitude) 23.44 or more, known non-Evergreen class, 12 of 15 calendars | `chill_clock()` `production.py:1115-1125` | accurate |
| 367 | "Tentative" marks extra classification uncertainty | `dist/app.js:284`, `:329` | accurate |
| 375 | 1st and 15th of each month, 24 starts | `production.py:948` | accurate |
| 383 | Starts excluded when bud freeze, flowering freeze or fruit frost recurs at 50% | `production.py:1062-1073` | accurate |
| 399-402 | Over 66 days of flowering or over 150 days to first harvest counts as stalled; horizon failures are not stalled; stalls are added to freeze families | `production.py:991-992`, `:1027-1031`, `:1055-1057` | accurate |
| 434 | Ranked risk needs a defined event, applicable calculation, 12 valid winters, 50% frequency | `production.py:899-918` | accurate |
| 495 | One qualifying day makes an event winter | `production.py:807-809` | accurate |
| 503-510 | Event definitions (100 h; -6.7 C then -3.9 C after half the heat to flowering; -2.2 C; 0 C; 35 C; 10 mm; high infection index; 4 days without a flight hour) | `production.py:840-888`, `:543-553` | accurate |
| 512 | Flight hours at 12.8 C or more, 09:00 to 17:00 "local solar time" | Code uses UTC plus `round(lon / 15)` whole hours (`production.py:378`); true solar time can differ by up to 30 minutes from this, plus the equation of time | **imprecise: whole-hour longitude offset, not solar time** |
| 522-523 | Warm hours above 21 C; daily fallback counts days with Tmax above 21 C | `production.py:647`, `:254-262` | accurate |
| 532 | Denominator is the number of valid winters | `production.py:894`, `:898` | accurate |
| 586-594 | "No complete crop cycle" can appear when some cycles complete; 450 vs 300 day searches | `dist/app.js:229-244` | accurate |
| 607 | Message "Chill requirement not reached" | Screen text is "Chill requirement not met" (`dist/cycle.js:24`) | **label mismatch** (guide line 7 promises exact screen spelling) |
| 609 | Message "Incomplete stage dates" | Screen text is "Incomplete temperature history after budbreak" (`dist/cycle.js:26`) | **label mismatch** |
| 608, 610-613 | "Heat requirement not reached", "No favourable start", "Not assessed", "Not ranked", "None ranked", "None recurring" | `dist/cycle.js:25`; `dist/app.js:244`, `:347`, `:352`, `:358-359` | accurate |
| 631-635 | 503 busy, 400 invalid, 422 unsupported, 500 failed, older method rejected | `location_api.py:161-176`; `dist/app.js:404-405` | accurate |
| 648 | Burgaw flowering-freeze exposure in 10 of 15 winters; regional reports describe spring freezes and a move away from early bloomers | `dist/snapshots/us-nc-burgaw.json` 10/15 ranked; IBO records for US-NC include the March 2022 freeze and growers removing 'Star' | accurate |
| 662-664 | Waldo harvest 4 April to 12 May; heavy rain 14 of 15 | `dist/snapshots/waldo.json` median 04-04 to 05-12; 14/15 | accurate |
| 737 | 140 tests passed on 2 October 2026 | `HANDOVER.md:67` records this; not re-run here | consistent with record |
| 752 | All 71 saved assessments have an applicable calendar or a selected scan window | Recomputed: 0 of 71 lack one | accurate |
| 540-570 | Near Yakima details (cell 46.5, -121.25 about 31 km away; 4,095 chill hours; 14 winters failed a stage) | No saved snapshot for this pin. Distance checks out (about 30.8 km); 4,095 h is below the 4,344-hour maximum of the November to April window | not reproducible from the repository; plausible |

### 5.2 Inaccuracies to fix

1. `docs/APP_USER_GUIDE.md:226`: change "can lack planting guidance" to say that only saved locations in Florida, Georgia and Santa Catarina receive guidance, and every other coordinate returns "Planting guide unavailable". Evidence: `location_api.py:121-122`, `:136`; `planting.py:54`, `:64`.
2. `docs/APP_USER_GUIDE.md:607` and `:609`: use the screen labels "Chill requirement not met" and "Incomplete temperature history after budbreak" (`dist/cycle.js:24`, `:26`), or drop the exact-spelling promise at line 7.
3. `docs/APP_USER_GUIDE.md:512`: say "local time approximated as UTC plus longitude/15 hours, rounded to whole hours" (`production.py:378`). The same wording appears in `production.py:93`, `:148`, `:201` and `README.md:72`.
4. `docs/APP_USER_GUIDE.md:345`: add that the 85 and 633 GDD requirements also come from the Waldo translation (`production.py:68-73`).
5. Omission: section 5.4 does not tell the reader that the planting windows come from home-garden extension guides. The API caveat does (`planting.py:21`, `:33`), and the commercial UF guide gives different timing (section 3.2).

**Verdict for Area 4: accurate overall.** One material understatement, two label mismatches, one imprecise time convention, one incomplete statement.

---

## 6. Area 5: Astra's open recommendations

Classification: **valid** (still valid, not done), **done**, **superseded by v3**, **conflict** (conflicts with later work), **blocked** (needs data or a human decision).

| # | Recommendation (Astra report, date) | Status | Evidence |
|---|---|---|---|
| 1 | Correct scan accounting: separate completed, thermal requirement not reached, weather incomplete and freeze exposure; stop counting stalls as freezes (sign-off answer, 10-05) | valid, approved, not implemented | `production.py:1027-1031`, `:1055-1057`; `README.md:57`; guide `:395-408` |
| 2 | Keep failed or absent stages in denominators and report the no-stage frequency (phenology review, 09-25) | conflict with the v2 risk code Astra built | `GLOBAL_PHENOLOGY_REVIEW.md:348` vs `production.py:893-894` |
| 3 | Cool-climate settings from an explicit crop scenario, not inferred from coordinates (10-05) | valid, approved; partly blocked on Paul's target crops | `HANDOVER.md`; guide `:689-700` |
| 4 | Ask the breeding team for cultivars, sites and dated stage records (10-05, 09-25) | blocked on human input | guide `:716-729` |
| 5 | Build a cultivar, stage and management parameter registry with the listed fields (09-25) | valid, not started | `GLOBAL_PHENOLOGY_REVIEW.md:346`; v3 constants live only in code comments (`production.py:68-97`) |
| 6 | Do not replace 50 h, 150 GDD, +14/+35 d and +70/+110 d with new universal values (09-25) | conflict: v3 replaced them with Waldo-translated GDD sums and 100 h | `production.py:98-107`, `:142` |
| 7 | Confirm the Kovaleski formula with the authors before importing (09-25) | conflict: v3 declared it a typo | `production.py:77-78` |
| 8 | Separate stage endpoints (floral and vegetative budbreak, F10/F50/F90, R10/R50/R90, harvested mass) (09-25) | valid; blocked on observation data | `GLOBAL_PHENOLOGY_REVIEW.md:56` |
| 9 | Allow overlapping stage windows (09-25) | valid, not implemented | `production.py:689` (fruit starts the day after flowering ends) |
| 10 | Validate on held-out years and sites, errors in days (09-25) | valid; blocked on data | `GLOBAL_PHENOLOGY_REVIEW.md:290-298` |
| 11 | Compare chill hours with Dynamic Model chill portions; no ratio conversion (09-25) | partly done (portions reported, not used) | `production.py:144`, `:657` |
| 12 | Reconcile River Valley's expected early-April harvest (09-22) | partly superseded by v3 (hypothetical 3 April to 6 May); still blocked on observed dates | `HANDOVER.md:50` |
| 13 | Clarify Paul's "cold and dry" pollination rule (09-22) | superseded by v3 bee-flight gap; comparison metric kept | `production.py:148`, `:180` |
| 14 | Replace the daily disease proxy with pathogen models later (09-22) | superseded by v3 hourly BAS/SAS indices | `production.py:145`, `:330-367` |
| 15 | Rank and gate risks per winter (≥50%, ≥12 winters) with exclusion reasons (09-22) | done | section 2 |
| 16 | Versioned profiles; keep `legacy_paul_v1` reproducible (09-22) | done | `production.py:28-58` |
| 17 | Fix `sensitivity()` and `ranked[0]` crashes (09-22) | done | `production.py:1206` |
| 18 | Connect arbitrary land cells to the hourly archive (09-22) | done | `location_api.py:56-70` |
| 19 | One planting window (plan: 105 to 30 days; implemented: regional establishment) (09-22) | conflict with the supervisor requirement (`SUPERVISOR_REVIEW_RIVER_VALLEY.md:23`) and with UF/IFAS HS1525; needs Paul's decision | section 3 |
| 20 | Before and after review with Paul on the same data (09-22, step 7) | blocked; no sign-off recorded | `SUPERVISOR_REVIEW_RIVER_VALLEY.md:53` |
| 21 | Regional evidence panel, then a reviewed event registry, then RAG (10-05) | panel done (91 records); event registry partial (`event_id`); RAG not started | `dist/evidence/ibo-regional-v1.json` |
| 22 | Check the Chile November 2022 and Waikato October 2022 freeze misses with farm locations and stations (10-05) | valid; blocked on station data | `docs/research/2026-10-05/ibo_event_checks.json` |
| 23 | Obtain complete IBO 2021 and 2024 (10-05) | blocked on access | `ibo_report_inventory.json` |
| 24 | Show the weather-feasible window apart from reported commercial practice (Peru pruning) (10-05) | partly done (scan plus evidence tab) | `dist/app.js:330-334` |
| 25 | A 2026/27 forecast needs current-season weather and crop observations (09-25) | valid; out of current scope | guide `:467-477` |

### Prioritised list

P1, do next:
1. **Scan and season accounting (items 1 and 2).** Implement the approved categories. Count stage failures in the denominator for crop families, or report them as a separate "cycle failed" frequency. Show chill shortfall on the Overview whenever it is the reason the winter calendar does not apply (the nine sites in section 2.2).
2. **Planting decision with Paul (items 19 and 20).** Put three options to him: his budbreak offsets, the current home-garden windows, or commercial windows from UF/IFAS HS1525 and Embrapa Documentos 96. Ask what "planting" means in his R workflow. Until then, label the Florida window as home-garden guidance and remove the first-season flower condition for commercial UF cultivars.
3. **Stage-record request plus public seed data (items 4, 8, 10).** Send the breeding-team request now. In parallel, transcribe the public dated stage tables Astra found but did not extract: Lyrene 2008 Tables 1 and 2, the UGA TH and Georgia Dawn tables, Campa and Ferreira S1, the SERIDA bulletin, Antunes Table 1, Medina and the Maule Table 4.
4. **Cool-climate scenario (item 3).** Start with an explicit northern-highbush scenario from Kirk and Isaacs (bloom) and Carlson and Hancock (first pick), keeping their own bases and anchors.

P2:
5. Parameter registry (item 5), with v3's constants entered first and their provenance (Waldo translation, Kovaleski span, typo assumption, items 6 and 7).
6. Risk-gate refinements from section 2.3: per-stage-day rates or multi-day events for harvest rain and disease, an interval-aware display at the 50% boundary, and a severity column for freezes.
7. Reviewed IBO event registry and the Chile and Waikato station checks (items 21 and 22).
8. Fix the guide items in section 5.2 and the stale texts: the v3 risk note (`production.py:939`), and a v3 header in `GLOBAL_PHENOLOGY_REVIEW.md` and the audit JSON.

P3:
9. Overlapping stage windows (item 9), Dynamic Model requirement comparison (item 11), IBO 2021 and 2024 (item 23).
10. Small source fixes: Williamson 2002 bloom wording (`GLOBAL_PHENOLOGY_REVIEW.md:172`), the C1293 leafing sentence, "non-commercial" in the Campa row (`:194`), the Pelotas 116-day comment (`production.py:988-990`), and the Maule values written as derived differences (`production.py:71-73`).

---

## 7. Verified facts and inferences, kept apart

Verified in this review (code, saved data or opened source):
- Gate constants, decision order, event thresholds, disease union and exposure-only families as cited in section 2.1.
- Snapshot counts in section 2.2 (41 applicable sites; 34, 26, 6, 1, 1 ranked; nine chill-gap sites; harvest window median 41 days).
- The binomial and Wilson numbers in section 2.3 (computed).
- Planting behaviour for arbitrary pins; 30 of 71 saved sites with a window; the R constants; Paul's written requirement.
- Every source verdict in sections 3.2 and 4.1, with the access status given.
- Guide statements in section 5.1 against the cited lines.

[inference] Judgements, not verified facts:
- That the 50% gate should be shown with its interval and that a severity measure is needed.
- That one-day events saturate because of window length rather than climate alone.
- That Paul's rule may agree with HS1525's fall planting in Florida, and that Paul may mean "production-cycle start" rather than nursery establishment.
- That the circular benchmark labels make the 38% result uninformative for Florida and Georgia.
- The priorities in section 6.
