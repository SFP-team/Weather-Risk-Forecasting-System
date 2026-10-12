# Source research: United States North and West plus Canada (`us-north-west-canada`)

Checked on 2026-10-11. Companion file: `us-north-west-canada.sources.json` (67 sources, 13 extraction and RAG jobs). Items marked [inference] are my reasoning, not source statements.

## 1. Scope and summary

**Covered.** Northern highbush (NHB) states New Jersey, Michigan, Oregon, Washington and California; wild lowbush in Maine; Canada: British Columbia, Québec, Nova Scotia, New Brunswick, Prince Edward Island and Ontario. Searches were in English and French. I opened 55 of 67 sources, 5 were reachable only in part (JavaScript apps), and 7 were seen only in search results.

**Five most valuable findings**

1. **The MSU bot wall can be bypassed with an official host.** Pages on canr.msu.edu return an Incapsula wall, but the same pages load on `msu-prod.dotcms.cloud`. Through it I opened the Southwest Michigan fruit updates, the Jersey crop and pest degree-day table, the critical spring temperatures page and E3490 *Blueberry Varieties for Michigan* ([MSU GDD table](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries)). This fixes the gap the benchmark registry recorded for Michigan.
2. **Ready-made cool-climate stage thresholds exist for lowbush and NHB.** The AAFC CIPRA crop guide gives degree-days per BBCH stage for lowbush (base 0 °C, from 1 March or from the last day with 10 cm of snow) and for NHB 'Patriot' ([CIPRA guide](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf)). Nova Scotia (White 2012, Perennia), Maine (Drummond 2019), Michigan (MSU) and Washington (Rogers et al. 2026, base 7 °C, the app's own base) add independent thresholds. See section 4.1.
3. **Seven seasons of dated, site-level lowbush stage data for Maine.** The UMaine Real-Time Wild Blueberry Phenology tracker publishes weekly percentages for each stage at nine named sites, 2020 to 2026 ([2024 record](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/2024-record/)). Québec's RAP *Bleuet nain* warnings give weekly BBCH stages for each MRC sector around Lac-Saint-Jean ([RAP 13 May 2025](https://www.agrireseau.net/rap/documents/116447/bleuet-nain-avertissement-no-1-13-mai-2025)). Together they cover two of the three pins that only get scan windows.
4. **A dated NJ freeze, with bloom progress for each cultivar.** The 2026 Rutgers *Blueberry Bulletin* reprints New Jersey's State of Emergency for the freeze of 19 to 22 April 2026. The emergency notes damage above 30% in many areas and at least USD 300 million in losses across all crops ([26 May 2026 issue](https://extension.rutgers.edu/sites/default/files/2026-05/bb-v42n11.pdf)). The 28 April issue puts Duke bloom at 65-80% and Bluecrop at 60-75% complete around Hammonton ([28 April 2026 issue](https://extension.rutgers.edu/sites/default/files/2026-04/bb-v42n07.pdf)).
5. **County, month and cause loss data for the US, with open blueberry location maps for both countries.** The USDA RMA cause-of-loss files run from 1989 to 2026, with county, cause and month of loss ([RMA](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss)). The USDA Cropland Data Layer maps blueberries as class 242; Washington 2023 accuracy is 79.0% producer's and 82.7% user's ([CDL WA 2023](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_wa23.htm)). The AAFC Annual Crop Inventory maps them as class 182 under the Open Government Licence ([ACI spec](https://agriculture.canada.ca/atlas/data_donnees/annualCropInventory/supportdocument_documentdesupport/en/ISO%2019131_AAFC_Annual_Crop_Inventory_Data_Product_Specifications.pdf)).

**Answers to the brief's questions**

| Question | Answer (details in sections 4 to 8) |
|---|---|
| Q1. Sources of dated bloom and harvest observations | NJ: Rutgers Blueberry Bulletin (2026 online; older issues by email). MI: MSU regional fruit updates through the dotCMS host. WA: Rogers et al. 2026 (Duke bloom 2022-2025, Whatcom and Skagit). BC: no public dated series; IBO plus the AAFC crop profile calendar only. ME: UMaine phenology tracker 2020-2026. QC: RAP Bleuet nain and Bleuet en corymbe. NS: Perennia blog GDD stations and 2022-2024 crop-stage study. ON: ONfruit Berry Bulletin. OSU and WSU small-fruit newsletters with dated stages were not found (gap). |
| Q2. Phenology models and parameters | Lowbush: CIPRA (QC), White 2012 and Perennia (NS), Drummond 2019 (ME). NHB: CIPRA Patriot, MSU Jersey table, Rogers 2026 WA Duke, Kirk and Isaacs 2012. Chill: only ranges (OSU 800-1,500 h) and one pot trial (Duke best at 1,200 h, Portugal). Half-high: no published GDD or chill values found. |
| Q3. Loss and damage ground truth | US: RMA cause of loss (county and month), FSA designations, NOAA Storm Events. Canada: FADQ is the only public insurer table with cause and region, but blueberries are grouped under "Petits fruits"; NB and PEI publish only totals or program rules; BC publishes no claims data found. AAFC AIR gives monthly maps only (Eastern Canada since 2020). Events: NJ April 2026; Maine frost nights 2022-2026; NS, PEI and NB June 2018; BC heat dome June 2021. |
| Q4. Statistics | StatCan 32-10-0364 (1926-2025, highbush and lowbush by province), StatCan 32-10-0315 (2021 census to subdivision level), AAFC fruit overview 2024, NASS Quick Stats and the NJ series 1929-2023, UMaine Maine series. |
| Q5. Station networks | Enviroweather (MI), AgWeatherNet (WA, API needs permission), AgriMet (OR, WA), CIMIS (CA), NJ Weather Network (70 stations), Maine Mesonet, ECCC hourly API (sampled), Agrométéo Québec (redistribution not allowed), Perennia stations (NS), Farmwest (BC, search only). |

## 2. Production context in brief

- **US cultivated (highbush) blueberries, 2023.** Harvested acres: Georgia 21,400, Washington 17,700, Michigan 16,900, Oregon 13,700, New Jersey 10,800, North Carolina 9,300, California 7,100, Florida 6,100. Utilised production was highest in Washington (137.4 million lb) and Oregon (128.9 million lb). Oregon had the highest yield, 9,400 lb per acre ([NASS NJ 2023 Blueberry Statistics](https://data.nass.usda.gov/Statistics_by_State/New_Jersey/Publications/Blueberry_Statistics/NJ-2023-Blueberry.pdf)).
- **Michigan.** Most blueberries grow in the western Fruit Belt near Lake Michigan. Cumulative GDD (base 50 °F, 1 April to 1 October, 2013-2023) is 3,342 °F at Benton Harbor and 2,732 °F at Hart, so West Central harvest runs about a week later ([E3490](https://msu-prod.dotcms.cloud/blueberries/uploads/files/E3490_Blueberry_Varieties_MI_AA.pdf)). Of surveyed growers, 95.5% grow Bluecrop, 72.7% Elliott and 68.2% Duke (same source).
- **Washington.** Whatcom County led with about 7,800 planted acres in 2019. Eastern Washington plantings (about 6,500 acres) were expanding fast ([WSU 2019 industry slides](https://s3.wp.wsu.edu/uploads/sites/2093/2019/12/2019StateofBlueberryLynden.pdf)).
- **Maine (wild lowbush).** 19,100 harvested acres and 90.8 million lb in 2024. Washington County held 13,668 bearing acres in 2012 ([UMaine statistics](https://extension.umaine.edu/blueberries/resources/production-statistics/)).
- **Canada, 2025.** National production was 156,922 t. British Columbia produced 73,545 t (47%, almost all highbush) and Québec 42,951 t. Nova Scotia (15,604 t), New Brunswick (15,014 t, -38%) and PEI (8,690 t) fell after a prolonged summer drought. Lowbush made up 51% of volume ([StatCan 2 July 2026](https://www.statcan.gc.ca/o1/en/plus/9224-despite-challenging-2025-growing-season-blueberries-remain-canadas-top-selling-fruit)). Lowbush shares in 2024 were QC 46.8%, NB 25.6%, NS 17.4% and PEI 10%, and BC grew 94% of the highbush crop ([AAFC 2024 overview](https://agriculture.canada.ca/en/sector/horticulture/reports/statistical-overview-canadian-fruit-industry-2024)).
- **Seasons.**
  - **NJ.** Bloom started in mid-April 2026 under 90 °F days ([Rutgers 28 April 2026](https://extension.rutgers.edu/sites/default/files/2026-04/bb-v42n07.pdf)).
  - **SW Michigan (Jersey cultivar).** Bud break 17-18 April, bloom 14-15 May, first harvest 15 July, all as multi-year averages ([MSU table](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries)).
  - **Western Washington (Duke).** 10% bloom between 19 April and 3 May and peak bloom between 9 and 21 May, 2022-2025 ([Rogers et al. 2026](https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/2701/2026/06/horttech-article-p562.pdf)).
  - **BC.** Leaf and flower bud break runs from late March to late April, and harvest from July to September ([AAFC highbush profile](https://agriculture.canada.ca/en/science/agriculture-and-agri-food-research-centres/pest-management-centre/pesticide-risk-reduction-pest-management-centre/crop-profiles/crop-profile-highbush-blueberry-canada)).
  - **Maine lowbush, 2024.** Open flowers were 51-71% on 21-23 May, and blue fruit 12-41% on 8 July ([UMaine 2024 record](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/2024-record/)).
  - **Lowbush management.** Fields run on a two-year sprout and crop cycle, and frost during June bloom is the main abiotic limit ([AAFC lowbush profile](https://agriculture.canada.ca/fr/science/centres-recherche-lagriculture-lagroalimentaire/centre-lutte-antiparasitaire/reduction-risques-lies-aux-pesticides-au-centre-lutte-antiparasitaire/profils-culture/profil-culture-du-bleuet-nain-au-canada-2023)).

## 3. What the app already has for this scope

- **Benchmark sites** (from `pipelines/weather/benchmark_sites.json` and the region brief):
  - **`us-nj-hammonton`.** Published bloom is April-May and the model agrees. Published harvest is June-August against a model June-July (recall 0.67). Sources are Rutgers FS1299 and FS419.
  - **`us-mi-grand-junction`.** Published bloom is May but the model gives June, one month late. Published harvest is July-September against a model July-August. The sources are the 1999 crop profile, the 2002 crop timeline, E2066 from 1988, ERS Amber Waves and FreshPlaza (frosts of 2, 8-9 and 12 May 2026).
- **Pins without full calendars.** The Cascade cell near Yakima gets no calendar. Lynden (11 of 15 winters), Cherryfield (6 of 15) and Lac-Saint-Jean (3 of 15) get scan windows only.
- **IBO records in scope** (`dist/evidence/ibo-regional-v1.json`):
  - `us-ca-freeze-2022`: California, late February to early March 2022, Madera County and north, crop 24% below forecast.
  - `us-pnw-2021-2022`: heat dome, cold winter and wet spring, yield down 10-60%, Liberty and Bluecrop worse than Duke.
  - `ca-bc-harvest`: Duke hand harvest in the first week of July 2024, and about 11 July in 2022.
- **Phenology review** (`docs/weather/GLOBAL_PHENOLOGY_REVIEW.md`). It already cites Kirk and Isaacs 2012 (S10, bases 7.14-7.96 °C, field peak bloom 291 GDD), PNW 656 (S18), the BC variety table (S19) and White et al. 2012 (S20).
- **Recorded gaps.** The MSU bot wall (now bypassed, see finding 1) and the unused AMS shipping-point reports (now covered by `usda-ams-shipping-point-trends`).

## 4. Source inventory

Status codes: O = opened, OL = opened-limited, SO = search-only. Full fields, terms and caveats are in the JSON.

### 4.0 Top 10 sources, described from an actual sample

| # | Source | What the sample showed |
|---|---|---|
| 1 | [Rutgers Blueberry Bulletin](https://extension.rutgers.edu/blueberry-bulletin) | The 26 May 2026 issue has dated beating-tray tables (17 April to 23 May) from 165 scouted fields in Atlantic and Burlington counties, fruit injury tables, and trap counts by county. It reprints the 20 May 2026 freeze emergency (19-22 April). The 28 April issue gives bloom progress for Duke (65-80%) and Bluecrop (60-75%). |
| 2 | [UMaine phenology tracker](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/2024-record/) | 2024 had 15 weekly tables. Columns: visit date, site (9 towns), and stage percentages from T0 closed bud through blue fruit and over-ripe. Field notes record prune emergence and tip dieback. |
| 3 | [MSU via dotCMS host](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries) | Table columns: event, date first seen in Van Buren and in Ottawa, GDD at base 42 °F and base 50 °F. The 22 April 2025 update records bud break through southern Allegan County and lows of 23 °F. |
| 4 | [RAP Bleuet nain](https://www.agrireseau.net/rap/documents/116447/bleuet-nain-avertissement-no-1-13-mai-2025) | Columns: sector (8 MRCs), leaf bud stage (V0, V1), fruit bud BBCH (51-53), vegetation status. Includes a link to the Agrométéo lowbush model, whose start date (last 10 cm of snow) was about 15 April 2025. |
| 5 | [CIPRA guide](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf) | Tables of degree-days per BBCH stage, with base and optimum temperature, method and start rule (section 4.1). |
| 6 | [USDA RMA cause of loss](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/COL_Summary_of_Business_with_Month_All_Years.pdf) | The record layout lists 30 fields, including state and county FIPS, commodity code, stage code, cause of loss description, month of loss, policies indemnified and indemnity amount. The ZIPs run 1989-2026 (not downloaded). |
| 7 | [StatCan 32-10-0364](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210036401) | A WDS metadata call returned 13 geographies and 8 estimates (production, value, area, prices), with highbush and lowbush members, for 1926-2025. |
| 8 | [ECCC climate-hourly API](https://api.weather.gc.ca/) | One call for Abbotsford A returned 520,631 hourly records. The first was 1990-01-28 22:00 with TEMP 5.4, DEW_POINT_TEMP 4 and RELATIVE_HUMIDITY 91, plus flag fields. |
| 9 | [FADQ état des cultures](https://www.fadq.qc.ca/salle-de-presse/bulletins-dinformation/etat-des-cultures/etat-des-cultures-2023/letat-des-cultures-de-la-fadq-bilan-au-4-juillet-2023-rapport-numero-5) | The 4 July 2023 report covers severe late frosts on 17-18 May for small fruits, frosts in late May and early June in Saguenay-Lac-Saint-Jean, and damage notices for bleuetières after hail. It also has a table of damage notices and indemnities by protection. |
| 10 | [Rogers et al. 2026 (WSU)](https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/2701/2026/06/horttech-article-p562.pdf) | Full text covers Duke in Whatcom and Skagit counties, 2022-2025. GDD use base 7 °C, a single sine and hourly AgWeatherNet data from 1 January. Mean absolute error is 2.4, 3.4 and 3.7 days for 10% bloom, peak and the last 10%. |

### 4.1 Cool-climate phenology parameter sources (with the numbers each source reports)

Bases, start dates and methods differ. Do not mix them. Fahrenheit-to-Celsius conversions are mine, using degree-days × 5/9 [inference].

| Source | Crop, place | Base and method | Start | Stage thresholds reported | Data behind it |
|---|---|---|---|---|---|
| [CIPRA, lowbush model 1](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf) | Lowbush, Québec | 0 °C; optimum 28 °C; simple sine | 1 March | BBCH51 221; 53 296; 55 329; 59 410; **65 (full bloom) 554**; 67 603; 71 777; 75 982; 81 1,138; **87 (ripe) 1,516** | Fitted by the AAFC Saint-Jean-sur-Richelieu team to RAP warnings 2005-2016 |
| CIPRA, lowbush model 2 (same PDF) | Lowbush, Québec | 0 °C; optimum 28 °C; simple sine | Last day with 10 cm of snow on the ground | 51 187; 53 247; 55 285; 59 358; **65 498**; 67 548; 71 720; 75 926; 81 1,083; **87 1,443** | Same |
| CIPRA, highbush (same PDF) | NHB 'Patriot', Québec | 0 °C; optimum 30 °C; simple sine | 1 March | 51 173; 54 267; 59 462; **65 576**; 71 765; 75 929; 81 1,275; **87 1,598** | AAFC photos 2014-2016 |
| [White, Boyd and Van Acker 2012](https://doi.org/10.21273/HORTSCI.47.8.1014) | Lowbush, Nova Scotia | 0 °C | 1 April (per Perennia) | Emergence 222-265 GDD; first flowering ramets 376-409 GDD (19-30 May); model start of flowering 389 GDD; peak open flowers 552-565 GDD; tip dieback start 598-792 GDD | Field quadrats, validated on independent sets |
| [Perennia fact sheet 2022](https://www.perennia.ca/wp-content/uploads/2022/05/Understanding-Growing-Degree-Days-in-Wild-Blueberry-Production.pdf) | Lowbush, NS | 0 °C; average method | 1 April | Open flowers: start 390, 10% 412, 25% 440, 50% 480, 90% 600 DD | White model table |
| [NS Wild Blueberry Blog GDD page](https://www.novascotiawildblueberryblog.com/p/phenology-tracker.html) | Lowbush, NS | 0 °C | 1 April | Emergence starts at 213 GDD; 10-25% bloom at 353-379 GDD; harvest reference 1,700 GDD (about 90% ripe) | Perennia and WBPANS study 2022-2024 in Cumberland, Colchester and Pictou (tables are images) |
| [Drummond 2019](https://ideas.repec.org/a/gam/jagris/v9y2019i4p69-d218599.html) | Lowbush, Maine | 4.4 °C | 1 April | Bloom begins at 100 degree-days and ends at 500 (3-4 weeks); stigmas receptive 8-10 days | Maine fields (2015-2017 per a search snippet) |
| [MSU degree-day table 2019](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries) | NHB 'Jersey', SW Michigan | 50 °F (10 °C) and 42 °F | Not stated | Bud break 108 °F-GDD (about 60 °C-GDD); bloom 310 (about 172); petal fall 407 (about 226); first harvest 1,313 (about 729) | Four years of farm monitoring; authors call them guidelines, not validated models |
| [Rogers et al. 2026](https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/2701/2026/06/horttech-article-p562.pdf) | NHB 'Duke', western WA | 7 °C, no upper limit; single sine; hourly | 1 January | Thresholds appear only in Figure 1. Observed dates: 10% bloom 19 April to 3 May; peak 9-21 May; last 10% 19-30 May | 2022-2025, 12 down to 1 field; cross-validated |
| [Kirk and Isaacs 2012](https://doi.org/10.21273/HORTSCI.47.9.1291) | NHB, 5 cultivars, Michigan | 7-8 °C lower threshold (7.14-7.96 °C per repo review) | January (per repo review) | Greenhouse bloom about 100 GDD later than field; field peak bloom 291 GDD (repo review S10) | Two field seasons |
| [OSU, How blueberry plants develop](https://extension.oregonstate.edu/catalog/how-blueberry-plants-develop-grow) | NHB, PNW | Chill 32-45 °F | n/a | NHB chill requirement 800-1,500 h; SHB 200-600 h; rabbiteye 300-600 h | Extension summary |
| [Oliveira et al. 2017](https://ishs.org/ishs-article/1180_72/) | Duke, Legacy, Elizabeth (Portugal, potted) | Chill hours | n/a | Duke yield highest at 1,200 h; Elizabeth needs at least 1,000 h; Legacy did best at 501 h | One controlled trial |
| [UMN Extension](https://extension.umn.edu/fruit/growing-blueberries-home-garden) | Half-high | n/a | n/a | Hardiness and ripening class only (Northblue 1983, Northcountry 1986, Chippewa 1996, Polaris 1996). **No chill or GDD values.** | Trial gardens |

**Freeze thresholds by stage**

| Stage | NHB ([MSU critical temperatures](https://msu-prod.dotcms.cloud/blueberries/weather/critical-spring-temperatures)) | Lowbush lowest safe temperature ([UMaine FS216](https://extension.umaine.edu/blueberries/resources/irrigation/flower-primordia-development-stage/)) |
|---|---|---|
| Tight bud | n/a | -4 °F (-20 °C) |
| Bud swell / scale separation | 10-15 °F (-12 to -9 °C) | +7 °F (-14 °C) |
| Inflorescence tip visible | n/a | +10 °F (-12 °C) |
| Tight cluster / flowers visible, closed | 20-23 °F (-7 to -5 °C) | +19 °F (-7 °C) |
| Early to late pink bud / flowers distended | 23-27 °F (-5 to -2.8 °C) | +23 °F (-5 °C) |
| Full bloom / fully open | 28 °F (-2.2 °C) | +28 °F (-2.2 °C) |
| Petal fall | 32 °F (0 °C) | n/a |

The lowbush values are freezer tests with cooling at 7.2 °F per hour. Hicklenton et al. 2002 add duration: 4 h at -3.5 °C damaged 80% of open and 60% of closed lowbush flowers, and there was almost no fruit set below -3.5 °C ([ISHS](https://ishs.org/ishs-article/574_29/)). Kogan et al. 2023 give a cultivar-specific NHB hardiness model for Washington. Only the abstract is open ([DOI](https://doi.org/10.21273/HORTSCI17320-23)).

**What this means for the approved cool-climate settings** [inference]:
1. Lowbush needs its own stage model at base 0 °C with a spring start (1 March, 1 April or the snow-melt date). It should not reuse the 100-chill-hour plus 150 GDD (base 7 °C) budbreak rule.
2. For NHB, base 7 °C is supported by Kirk and Isaacs and by Rogers 2026. A start of 1 January and a bloom target near 300 GDD are consistent with the Michigan and Washington data. CIPRA's base 0 °C Patriot model is a second option for Québec.
3. The chill requirement for NHB can be set as a range (800-1,500 h) with Duke near 1,200 h. Lowbush and half-high have no published chill values, so the chill clock should not gate their calendar.

### 4.2 Dated stage observations and grower bulletins

| Source | Contains | Access, terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [Rutgers Blueberry Bulletin](https://extension.rutgers.edu/blueberry-bulletin) | Weekly NJ stages, scouting, freeze notices | Open; "please cite" | en | 2026 online; older by email | O | P1 |
| [UMaine phenology tracker](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/) | Weekly lowbush stage percentages at 9 sites | Open; terms not found | en | 2020-2026 | O | P1 |
| [MSU fruit updates (dotCMS host)](https://msu-prod.dotcms.cloud/news/southwest-michigan-fruit-update-april-22-2025) | Weekly MI stage text and weather | Open; terms not found | en | weekly, 2024-2026 seen | O | P1 |
| [RAP Bleuet nain](https://www.agrireseau.net/rap/documents/116447/bleuet-nain-avertissement-no-1-13-mai-2025) | Weekly lowbush BBCH by sector | Open; non-commercial reuse with source | fr | 2020-2026 | O | P1 |
| [RAP Bleuet en corymbe](https://www.agrireseau.net/rap/documents/117946/bleuet-en-corymbe-avertissement-no-12-2-juillet-2025) | Weekly Patriot and Duke stages by region; degree-day lag | Same | fr | 2024-2025 seen | O | P2 |
| [NS Wild Blueberry Blog GDD](https://www.novascotiawildblueberryblog.com/p/phenology-tracker.html) | Station GDD; stage GDD study | Open; terms not found | en | seasonal, study 2022-2024 | O | P1 |
| [ONfruit Berry Bulletin](https://onfruit.ca/2025/05/14/may-14-berry-bulletin/) | Ontario bloom and harvest notes | Open | en | 2025-2026 | O | P3 |
| [FADQ état des cultures](https://www.fadq.qc.ca/salle-de-presse/bulletins-dinformation/etat-des-cultures/etat-des-cultures-2023/letat-des-cultures-de-la-fadq-bilan-au-4-juillet-2023-rapport-numero-5) | Dated weather and damage by region | Open; terms not found | fr | 2021-2026 | O | P1 |

### 4.3 Phenology parameters, cultivar traits and research

| Source | Contains | Access, terms | Lang | Status | Priority |
|---|---|---|---|---|---|
| [CIPRA guide](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf) | Stage degree-days, lowbush and NHB | Open; terms not found | fr | O | P1 |
| [White et al. 2012](https://doi.org/10.21273/HORTSCI.47.8.1014) | Lowbush GDD (NS) | Open abstract | en | O | P2 |
| [Perennia fact sheet](https://www.perennia.ca/wp-content/uploads/2022/05/Understanding-Growing-Degree-Days-in-Wild-Blueberry-Production.pdf) | Bloom progression GDD | ©Perennia 2022 | en | O | P1 |
| [Drummond 2019](https://ideas.repec.org/a/gam/jagris/v9y2019i4p69-d218599.html) | Maine bloom model | Open abstract (MDPI page 403) | en | O | P1 |
| [MSU GDD table](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries) | Jersey stage dates and GDD | Open | en | O | P1 |
| [Rogers et al. 2026](https://wpcdn.web.wsu.edu/wp-labs/uploads/sites/2701/2026/06/horttech-article-p562.pdf) | Duke bloom model, WA | CC BY-NC 4.0 | en | O | P1 |
| [Kirk and Isaacs 2012](https://doi.org/10.21273/HORTSCI.47.9.1291) | NHB base temperature | Abstract | en | O | P3 |
| [Kogan et al. 2023](https://doi.org/10.21273/HORTSCI17320-23) | NHB hardiness model | Abstract | en | O | P2 |
| [MSU critical temperatures](https://msu-prod.dotcms.cloud/blueberries/weather/critical-spring-temperatures) | NHB freeze thresholds by stage | Open | en | O | P1 |
| [UMaine FS216](https://extension.umaine.edu/blueberries/resources/irrigation/flower-primordia-development-stage/) | Lowbush lowest safe temperatures | © UMaine | en | O | P1 |
| [Hicklenton et al. 2002](https://ishs.org/ishs-article/574_29/) | Lowbush flower damage by duration | Paid full text | en | O | P2 |
| [OSU plant development](https://extension.oregonstate.edu/catalog/how-blueberry-plants-develop-grow) | NHB chill range, bloom frost | Open | en | O | P2 |
| [Oliveira et al. 2017](https://ishs.org/ishs-article/1180_72/) | Duke chill response | Paid full text | en | O | P3 |
| [MSU E3490](https://msu-prod.dotcms.cloud/blueberries/uploads/files/E3490_Blueberry_Varieties_MI_AA.pdf) | MI cultivar classes, adoption, region GDD | © MSU 2024 | en | O | P1 |
| [UMN half-high varieties](https://extension.umn.edu/fruit/growing-blueberries-home-garden) | Half-high cultivar list | Open | en | O | P3 |

### 4.4 Loss, damage, insurance and disaster declarations

| Source | Contains | Access, terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [USDA RMA cause of loss](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss) | County, cause, month of loss, indemnity | Open; US public domain | en | 1989-2026 | O | P1 |
| [USDA FSA designations](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) | County disaster declarations | Open | en | 2012-2026 | O | P2 |
| [NOAA Storm Events](https://www.ncei.noaa.gov/access/storm-events-database/) | Dated frost, hail and heat events | Open | en | not verified | OL | P2 |
| [UMaine frost posts](https://extension.umaine.edu/blueberries/category/frost/) | Frost nights with station minima | Open | en | 2021-2026 | O | P1 |
| [FADQ avis de dommages](https://www.fadq.qc.ca/statistiques/assurance-recolte/assurance-recolte-avis-de-dommages-et-indemnites) | Notices, causes, indemnities ("Petits fruits") | Open | fr | 2025-2026 on page | O | P2 |
| [CBC NS frost 2018](https://www.cbc.ca/news/canada/nova-scotia/june-frost-wipes-out-nova-scotia-s-wild-blueberry-crop-1.4739817) | Up to 70% lowbush loss, NS, PEI, NB | News | en | 2018 | O | P2 |
| [Country Life in BC heat dome](https://www.countrylifeinbc.com/significant-losses-to-fruit/) | 50 berry loss notices by 29 June 2021 | News | en | 2021 | SO | P3 |
| [FreshPlaza Maine 2026 frost](https://www.freshplaza.com/north-america/article/9849174/frost-and-temperature-swings-threaten-maine-wild-blueberry-crop/) | Aurora swing from 90 °F to 21 °F | News | en | 2026 | SO | P3 |
| [AAFC AIR](https://agriculture.canada.ca/en/agricultural-production/weather/agroclimate-impact-reporter) | Monthly impact maps | Open; disclaimer | en, fr | East from 2020 | O | P3 |
| [NB insurance annual report](https://www2.gnb.ca/content/dam/gnb/Gateways/ABCs/Annual-reports2/2024-2025/AAF-NBAIC-2024-2025-annual-report-E.pdf) | Totals only | Open | en | 2022-2025 | SO | P3 |
| [PEI AgriInsurance](https://www.princeedwardisland.ca/en/information/pei-agricultural-insurance-corporation/agriinsurance) | Program rules | Open | en | 2026 | SO | P3 |
| [NCCC-212 reports](https://smallfruits.cals.ncsu.edu/nccc-212-2021/) | Research summaries; BC 2021 heat (111 °F at Clearbrook, 27-28 June) | Open | en | 2020-2021 | O | P3 |

### 4.5 Production, area and market statistics

| Source | Contains | Access, terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [StatCan 32-10-0364](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210036401) | Production, area, value by province and type | StatCan Open Licence | en, fr | 1926-2025 | O | P1 |
| [StatCan 32-10-0315](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210031501) | 2021 census blueberry area to subdivision level | StatCan Open Licence | en, fr | 2021 | O | P1 |
| [StatCan 2025 article](https://www.statcan.gc.ca/o1/en/plus/9224-despite-challenging-2025-growing-season-blueberries-remain-canadas-top-selling-fruit) | 2025 provincial changes and causes | StatCan Open Licence | en, fr | 2025 | O | P2 |
| [AAFC fruit overview 2024](https://agriculture.canada.ca/en/sector/horticulture/reports/statistical-overview-canadian-fruit-industry-2024) | Tables plus weather narrative | Open | en, fr | 2020-2024 | O | P1 |
| [AAFC highbush crop profile](https://agriculture.canada.ca/en/science/agriculture-and-agri-food-research-centres/pest-management-centre/pesticide-risk-reduction-pest-management-centre/crop-profiles/crop-profile-highbush-blueberry-canada) | BC calendar, practices | Open | en | 2021-2023 | O | P2 |
| [AAFC lowbush crop profile](https://agriculture.canada.ca/fr/science/centres-recherche-lagriculture-lagroalimentaire/centre-lutte-antiparasitaire/reduction-risques-lies-aux-pesticides-au-centre-lutte-antiparasitaire/profils-culture/profil-culture-du-bleuet-nain-au-canada-2023) | Lowbush calendar, abiotic limits | Open | fr | 2023 | O | P2 |
| [NASS Quick Stats](https://quickstats.nass.usda.gov/api) | State and county statistics | Free key | en | survey and census years | O | P1 |
| [NASS NJ blueberry statistics](https://data.nass.usda.gov/Statistics_by_State/New_Jersey/Publications/Blueberry_Statistics/NJ-2023-Blueberry.pdf) | NJ yield 1929-2023; 2023 state table | Public domain | en | 1929-2023 | O | P2 |
| [UMaine production statistics](https://extension.umaine.edu/blueberries/resources/production-statistics/) | Maine yield 2012-2024; county acres | Open | en | 1924-2025 | O | P2 |
| [NASS New England releases](https://www.nass.usda.gov/Statistics_by_State/New_England_includes/Publications/ME-Wild-Blueberry-Release.pdf) | Maine wild releases | Public domain | en | 2006 onward | SO | P3 |
| [USDA AMS shipping point trends](https://www.ams.usda.gov/mnreports/fvwtrds.pdf) | Weekly MI and NJ shipments, first and last report | Public domain | en | current week | O | P2 |
| [USDA ERS outlook FTS-384](https://ers.usda.gov/sites/default/files/_laserfiche/outlooks/113982/FTS-384.pdf) | Maine 2025 season narrative | Public domain | en | 2026 | SO | P3 |
| [WSU 2019 WA industry slides](https://s3.wp.wsu.edu/uploads/sites/2093/2019/12/2019StateofBlueberryLynden.pdf) | WA production 2006-2019; county acres | Open | en | 2006-2019 | O | P3 |
| [California Blueberry Commission reports](https://www.calblueberry.org/annual-reports.html) | Annual reports with statistics | Open | en | 2013-2024 | O | P2 |

### 4.6 Land use and remote sensing

| Source | Contains | Access, terms | Status | Priority |
|---|---|---|---|---|
| [USDA CDL class 242](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_wa23.htm) | 30 m blueberry pixels; WA 2023 accuracy 79.0% (producer's) and 82.7% (user's) | Public domain | O | P1 |
| [AAFC ACI class 182](https://agriculture.canada.ca/atlas/data_donnees/annualCropInventory/supportdocument_documentdesupport/en/ISO%2019131_AAFC_Annual_Crop_Inventory_Data_Product_Specifications.pdf) | 30 m Canada crop map, 2009-2025 | Open Government Licence - Canada | O | P1 |

### 4.7 Weather station networks

| Network | Coverage | Access, terms | Status | Priority |
|---|---|---|---|---|
| [ECCC climate-hourly API](https://api.weather.gc.ca/) | All Canadian provinces; hourly | ECCC End-use Licence | O | P1 |
| [NJ Weather Network](https://www.njweather.org/) | 70 NJ stations | Terms not found | O | P1 |
| [MSU Enviroweather](https://enviroweather.msu.edu/) | Michigan fruit belt | Registration on site; terms not seen | OL | P1 |
| [WSU AgWeatherNet](https://weather.wsu.edu/) | 300+ WA stations, 15-minute | Registration; API by permission (search snippet) | OL | P1 |
| [USBR AgriMet](https://www.usbr.gov/pn/agrimet/) | OR, WA, ID, MT | Public domain; station CSV and JSON | O | P2 |
| [CIMIS](https://cimis.water.ca.gov/) | California | Registration for API (not verified) | OL | P2 |
| [Maine Mesonet](https://mco.umaine.edu/mesonet/) | Maine; 5-minute | Terms not found | O | P2 |
| [Agrométéo Québec](https://agrometeo.solutions-mesonet.org/) | Québec; blueberry models | Personal non-commercial; no redistribution without written permission | O | P2 |
| [NEWA](https://newa.cornell.edu/) | Northeast US | Terms not found | O | P3 |
| [Perennia Farm Data Tools](https://www.farmdatatools.perennia.ca/) | NS on-farm stations | Not verified | OL | P3 |
| [Farmwest](https://farmwest.com/) | BC | Not verified | SO | P3 |
| [WSU DAS](https://decisionaid.systems/) | WA and BC models | Registration | O | P3 |

### 4.8 Industry bodies (checked leads)

| Source | Finding | Status | Priority |
|---|---|---|---|
| [BC Blueberry Council](https://www.bcblueberry.com/) | Crop data sit behind a member portal; no public reports | O | P3 |
| [Producteurs de bleuets sauvages du Québec](https://bleuetsduquebec.ca/) | Bulletin Le Bleuet (No 092, October 2025); season launch 29 July 2026 | O | P2 |
| [BC Ministry berries](https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/animals-and-crops/crop-production/berries) | Production guides; insurance perils; no claims data | O | P3 |
| [Oregon](https://www.oregonblueberry.com/) and [Washington](https://wablueberries.com/) commissions | Consumer sites; no stage or loss data | O | P3 |

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON. Effort is in person-days.

| Job | Title | Output | Method | Fields to extract | Effort | Priority |
|---|---|---|---|---|---|---|
| NWC-01 | Rutgers Bulletin stages and events | claim records | layout-aware PDF tables | kind, topic, period start and end, cultivar and % bloom progress, county, issue citation | 2.0 | P1 |
| NWC-02 | UMaine tracker to stage table | time series table | HTML scrape | site, visit_date, stage_code, percent, season, notes, nearest_station_id | 1.5 | P1 |
| NWC-03 | Québec RAP stage tables | time series table | HTML scrape | bulletin_date, network, sector, cultivar, leaf bud stage, fruit bud BBCH, DJ lag, snow date | 2.0 | P1 |
| NWC-04 | MSU fruit updates via dotCMS | claim records | HTML scrape | kind, topic, date, county, cultivar, canonical and host URL | 1.5 | P1 |
| NWC-05 | Cool-climate parameter table | cultivar table | manual review | species class, cultivar, stage, threshold, unit, base °C, optimum, method, start rule, region, years, validation metric | 1.0 | P1 |
| NWC-06 | Stage freeze thresholds | cultivar table | manual review | species class, stage, threshold °C, threshold type, duration, damage %, method | 0.5 | P1 |
| NWC-07 | RMA cause of loss for counties in scope | event records | CSV parse | year, state and county FIPS, commodity, cause, month of loss, policies indemnified, quantity, indemnity, loss ratio | 1.5 | P1 |
| NWC-08 | FADQ crop condition and notices | event records | HTML scrape | kind=event, topic=weather, period, region, bleuetière context, report citation | 1.5 | P1 |
| NWC-09 | US and Canada production series | time series table | API pull | country, state or province, year, type, area, production, yield, prices, value | 1.0 | P1 |
| NWC-10 | Cool-climate station table | station table | API pull | network, id, name, lat, lon, elevation, start, hourly flag, variables, terms, nearest pin | 1.0 | P1 |
| NWC-11 | CDL and ACI blueberry masks | time series table | API pull | year, cell, blueberry pixel count, class code, region, class accuracy | 2.0 | P2 |
| NWC-12 | Cool-climate narrative RAG corpus | claim records | manual review | IBO record fields (kind, topic, title, summary, period, crop_context, evidence_type, geography_ids, citations, limitations) | 2.0 | P2 |
| NWC-13 | AMS weekly MI and NJ shipments | time series table | layout-aware PDF tables | report date, origin, crop year, three-week shipments, first and last report flags, price range | 1.0 | P2 |

Every job keeps the IBO design rules: document, claim and event records are kept separate, and every extraction is reviewed by a person before display. NWC-12 must not repeat the three IBO records in scope.

## 6. How each source maps to model checks

- **Lowbush calendar (Cherryfield, Lac-Saint-Jean, Atlantic Canada).** Run the CIPRA model 1 and model 2 thresholds and Drummond's 100-500 DD bloom window against the UMaine tracker (2020-2026) and RAP Bleuet nain stages (2020-2026). Score the error at full bloom and at ripe fruit in days, holding out whole seasons. This tests whether a base 0 °C spring-start model gives a calendar in more winters than the current 6 of 15 and 3 of 15 [inference].
- **NHB bloom timing (Grand Junction, Lynden, Hammonton).**
  - Michigan: compare model bloom with MSU's Jersey bloom date of 14-15 May and with the dated fruit updates. The model currently says June.
  - Washington: compare with Rogers et al. 10% and peak bloom dates. Same base temperature, so a direct test.
  - New Jersey: compare with the 2026 Rutgers bloom progress figures.
- **Harvest timing.** Compare the model's harvest start with MSU's first harvest (15 July, 1,313 °F-GDD) and with the AMS first-report week for Michigan and New Jersey. Use the 1,700 GDD (base 0 °C) harvest reference for NS lowbush.
- **Bud and flower freeze.**
  - Replace the single threshold with stage tables (MSU for NHB; UMaine FS216 and Hicklenton for lowbush).
  - Validate against dated events: NJ 19-22 April 2026; Maine frost nights (22-23 May 2026, 17-18 May 2023, 24-25 May 2022); NS, PEI and NB June 2018; Québec 17-18 May 2023; Michigan 2, 8-9 and 12 May 2026.
  - Compare county freeze indemnity months in RMA (Van Buren, Ottawa, Allegan, Atlantic, Burlington, Whatcom, Washington ME) with modelled flowering-freeze winters.
- **Heat.** Check the BC heat dome of 27-28 June 2021 (111 °F at Clearbrook, NCCC-212 BC report) against the fruit-stage heat flag in Fraser Valley cells, together with the IBO PNW record. Also check RMA "heat" cause months in WA and OR.
- **Drought.** Check the 2025 Maritime drought (StatCan: NB -38%, NS -16.9%) and Maine drought years against the water_drought family. Maine yield anomalies (2020: 2,290 lb per acre) serve as targets.
- **Disease and harvest rain.** The weekly Botrytis and anthracnose notes in the Rutgers and RAP bulletins, and the FADQ hail and rain notices, can be compared with the hourly disease indices in the same weeks.
- **Weather bias.** Use ECCC hourly (Abbotsford, Lac-Saint-Jean stations), NJ Weather Network, Enviroweather, AgWeatherNet and Maine Mesonet to measure the +1 °C warm Tmin bias in cool-climate cells, and to see whether the grid misses frosts at 28 °F, the open-flower threshold.
- **Location.** Use CDL class 242 and ACI class 182 to choose validation cells that contain blueberries. Use StatCan census area for sub-provincial weighting.
- **Cultivar classes.** E3490 adoption shares (Michigan) and the CIPRA Patriot model give NHB early, mid and late classes. Half-high cannot be parameterised from public sources.

## 7. Access, licensing and language risks

- **Restrictive terms.**
  - Agrométéo Québec allows only personal, non-commercial use and requires written permission to redistribute. Use it as a reference, or ask Solutions Mesonet.
  - The RAP bulletins allow reproduction with the source cited but forbid commercial or advertising use. Confirm the app's status.
  - The WSU paper is CC BY-NC 4.0.
- **Registration.** NASS Quick Stats needs a free API key. AgWeatherNet needs registration, and its API needs permission. Enviroweather and CIMIS offer registration; their terms were not seen.
- **Fragile access.** The MSU dotCMS host is not a documented endpoint and may close. Record the canonical canr.msu.edu URL for each item. Several station sites are JavaScript-only.
- **Missing terms.** UMaine, FADQ, Perennia and the NJ Weather Network state no licence I could find. Treat their content as citation-only until confirmed.
- **Language.** All Québec sources are in French, and their stage terms need mapping to BBCH codes.
- **Unit traps.** GDD in °F versus °C, different bases (0, 4.4, 5, 7, 10 °C), and different start dates (1 January, 1 March, 1 April, snow-melt) are not interchangeable.

## 8. Gaps: what I looked for and could not find

- **Half-high chill requirement and GDD.** UMN Extension lists half-high cultivars without chill values. The only values found (800-1,000 h for Polaris, Chippewa and Northblue) are on nursery pages, which are not primary. I searched English sources for half-high chill studies with no primary result.
- **Lowbush chill requirement.** No primary forcing study was found in English or French searches. The Québec models avoid chill and start from 1 March or snow-melt.
- **NHB chill requirement by cultivar from field data.** Only extension ranges (OSU 800-1,500 h) and one Portuguese pot trial (Duke, 1,200 h) were found. Recent forcing studies (2022-2024) did not surface. A bioRxiv chill and cold-hardiness preprint returned HTTP 429, and I could not confirm its species.
- **OSU and WSU small-fruit newsletters with dated stages.** None were found. WSU's dated data are in Rogers et al. 2026, and the stage GDD values are only in a figure.
- **BC dated phenology.** The BC Blueberry Council keeps crop information in a member portal. No public season reports or bloom dates were found beyond IBO and the AAFC calendar.
- **Canadian insurance by crop and cause.** FADQ groups blueberries under "Petits fruits". NB annual reports give totals only (search snippets). PEI shows only program rules. For BC, NS and Ontario (Agricorp), no public claims statistics were found.
- **Older Rutgers Bulletins.** Only 2026 is online. Older issues are by email request.
- **Michigan Blueberry News PDFs.** Not tested on the dotCMS host.
- **RMA blueberry commodity code and Maine wild coverage.** Not checked, because the ZIPs were not downloaded.
- **Kogan et al. 2023 coefficients and Rogers et al. figure values.** Full text or a request to the authors is needed.
- **NOAA Storm Events field list.** Not confirmed; the page is a JavaScript app.

## 9. Ranked top 10 actions for this scope

1. **Build the cool-climate parameter table (NWC-05)** from CIPRA, White and Perennia, Drummond, MSU and Rogers 2026. Use it to set lowbush (base 0 °C, spring start) and NHB (base 7 °C, start 1 January) stage models. This is about 1 day.
2. **Backfill the UMaine tracker (NWC-02) and RAP Bleuet nain (NWC-03)**, then score the lowbush model on held-out seasons at the Cherryfield and Lac-Saint-Jean cells.
3. **Switch MSU citations to the dotCMS host** and extract blueberry paragraphs from SW and WC Michigan updates (NWC-04). Re-test the one-month-late bloom at Grand Junction.
4. **Add stage freeze threshold tables (NWC-06)** and rerun flowering_freeze against the dated events listed in section 6.
5. **Ingest RMA cause of loss (NWC-07)** for blueberry counties in MI, NJ, ME, OR, WA and CA, and compare freeze months with modelled freeze winters.
6. **Build the station table (NWC-10)** starting with the ECCC hourly API and the NJ Weather Network, then request AgWeatherNet API permission. Measure the Tmin bias at the pins.
7. **Extract the 2026 Rutgers Bulletins (NWC-01)** and ask NJAES for back issues.
8. **Extract FADQ crop-condition bulletins (NWC-08)** for the Lac-Saint-Jean frost and hail events.
9. **Pull StatCan 32-10-0364 and NASS series (NWC-09)** and flag low-yield years for validation.
10. **Add CDL and ACI blueberry masks (NWC-11)** to choose validation cells. Contact the WSU authors for the Figure 1 GDD values and the Kogan model coefficients.
