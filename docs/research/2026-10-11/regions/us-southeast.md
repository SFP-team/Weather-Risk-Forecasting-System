# US Southeast (FL, GA, SC, NC, MS, AL): source inventory for the blueberry weather-risk app

Slug: `us-southeast`. Checked on 2026-10-11. Companion file: `us-southeast.sources.json` (53 sources, 14 jobs).

## 1. Scope and summary

**Scope.** Florida, Georgia, South Carolina, North Carolina, Mississippi and Alabama. I covered federal datasets used at state or county level (RMA, NOAA Storm Events, FSA, NASS, AMS domestic movement), state weather networks, cultivar and phenology data, and extension, industry and news text for a citation-first library. I opened every URL I list and sampled one small file each from RMA, FSA, NOAA, AMS, FAWN and NASS. All sources are in English. I found no Spanish-language source of value for this region [inference: the regional industry publishes in English].

**Five most valuable findings**

1. **County-by-month blueberry insurance losses exist back to 1989.** The RMA "Summary of Business with Month of Loss" files ([directory](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/), [layout](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/COL_Summary_of_Business_with_Month_All_Years.pdf)) carry county, cause of loss, month of loss and indemnity. In the 2022 file, Georgia blueberry Freeze losses in March total USD 30.5 million. Bacon County's March freeze indemnity was USD 11.84 million, out of USD 14.63 million for all 2022 causes (coordinator check, 2026-10-11). This is the first loss series that can score the model's flowering-freeze winters county by county.
2. **Plant patents hold multi-year, site-specific bloom and ripening dates.** The 'TH-906' patent ([Google Patents](https://patents.google.com/patent/USPP27026P3/en)) gives 2009-2013 means at Alapaha, GA: 50 % flowering 'Star' 3 March, 'Camellia' 11 March, 'TH-906' 8 March; 50 % ripening 8, 15 and 12 May. A USDA-ARS public-domain dataset adds 187 SHB genotypes at Poplarville with 50 % flowering and ripening for 2021-2022 ([Ag Data Commons record](https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_Phenological_variation_associates_with_the_stability_of_fruit_quality_traits_in_cultivated_tetraploid_blueberry/28339583), [paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12239625/)).
3. **Two weekly harvest-timing series exist, but both stopped in 2025.** NASS Georgia "Blueberries - Harvested" percent runs from 2011 ([2011 report](https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/2011/current_ga25.pdf)) to the last state PDF on 27 May 2025. AMS weekly shipments by origin (FL, GA, NC) run from November 2018 to April 2025 ([ESMIS](https://esmis.nal.usda.gov/publication/weekly-shipments-movement-blueberry)); AMS paused the report from 1 May 2025 and moved the data to MyMarketNews ([notice](https://www.ams.usda.gov/mnreports/wa_fv408.pdf)). The backfill is easy; continuity needs a free API key.
4. **The early-2026 freeze is documented at station level.** A UF/IFAS report dated 9 February 2026 ([PDF](https://fbga.memberclicks.net/assets/docs/Freeze%20event%20and%20Florida%20Blueberries%20-%20Feb%209%202026.pdf)) lists FAWN canopy-height minima, dew points, winds and hours below 32 F per county for 31 January to 3 February 2026, and says the freeze hit flowering and early fruit set. RMA ([MGR-26-001](https://www.rma.usda.gov/policy-procedure/bulletins-memos/managers-bulletin/mgr-26-001-claims-advisory-2026-freeze-damage)), FDACS via [WGCU](https://www.wgcu.org/agriculture/2026-03-04/usda-issues-disaster-declaration-for-florida-in-wake-of-crop-damage-by-2026-freeze) and NABC crop calls ([12 Feb](https://nabc.blueberry.org/wp-content/uploads/sites/6/2026/02/Crop-Call-Report-February-12-2026.pdf), [19 Feb](https://nabc.blueberry.org/wp-content/uploads/sites/6/2026/02/Crop-Call-Report-February-19-2026-1.pdf)) add dated loss estimates.
5. **Hourly station truth covers most benchmark pins.** FAWN has QA-flagged 15-minute data from 1998 with 60 cm canopy temperature and leaf wetness at Arcadia, Sebring, Homestead, Citra, Alachua, Live Oak, Monticello, Dover, Balm and Okahumpka ([metadata](https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/metadata.txt)). Georgia AEMN has an Alma station ([ALMA](http://georgiaweather.net/mindex.php?site=ALMA)), NC ECONet has hourly data since 1996 ([CLOUDS](https://api.climate.ncsu.edu/networks.php)), and MSU's network lists a Poplarville station with hourly output ([report form](https://deltaweather.extension.msstate.edu/weather-station-result/)). South Carolina and Alabama have no comparable public network near production.

**Answers to the brief's six questions**

1. *Dated, cultivar-specific bloom and harvest observations.* Best sources: US plant patents (multi-year 50 % flowering and ripening means by site), the USDA-ARS Poplarville genotype dataset (2021-2022), FSHS Proceedings trial papers (1888-2023), Clemson weekly field reports (regional stage notes), UGA county blogs (e.g. [Appling, 1 May 2026](https://site.extension.uga.edu/applingcrop/2026/05/2026-blueberry-harvest-update/)), and Bill Cline's NC cultivar notes ([Legacy](http://ncblueberryjournal.blogspot.com/2011/08/blueberry-cultivar-legacy.html)). UGA cultivar development reports sit on smallfruits.org behind a bot wall. No NC State or Clemson table of dated observations by year was found.
2. *Site-specific evergreen SHB phenology for central and south Florida.* Not found. The closest are cultivar release notes: 'Avanti' with "significant production in late January and early February in trials in South-Central Florida" and 'Arcadia' fruit "from February through May" ([Growing Produce, 2015](https://www.growingproduce.com/fruits/berries/florida-blueberry-growers-exploring-evergreen-varieties/)), and 'Albus' notes for central Florida ([FBGA blog](https://floridablueberrygrowers.org/index.php?category=blueberry-blog&id=200%3Auf-blueberry-breeding-program-update&option=com_dailyplanetblog&view=entry)). The gap stands.
3. *Dated freeze and rain losses.* RMA cause-of-loss (county, month, cause), FSA designations (county hazard windows with begin and end dates), Storm Events (zone, hour, narrative), RMA claims advisories, and extension and industry statements. Event coverage:
   - **2017 Georgia freeze**: RMA [MGR-17-004](https://www.rma.usda.gov/policy-procedure/bulletins-memos/managers-bulletin/2017/mgr-17-004-claims-advisory-2017-freeze) (15-16 March 2017, reports of 80 % damage in southern Georgia); Storm Events 2017 file (Frost/Freeze 16 March 2017 03:00, narrative "as much as 80 percent of the blueberry crop was lost", about USD 204 million); UGA [2018 news](https://fieldreport.caes.uga.edu/news/spring-freeze-dooms-georgia-blueberries-for-second-consecutive-year/) (2018 loss up to 60 %, after the 2017 loss); GDA [Market Bulletin, 23 May 2018](http://www.forms.agr.georgia.gov/MBADS/pdf/2018/052318-Market-Bulletin.pdf).
   - **March 2022 freeze**: FSA CY2022 designations ([xlsx](https://www.fsa.usda.gov/sites/default/files/documents/METADATA_CY2022_SEC_YTD.xlsx)) with Georgia windows 11-14 March 2022 and S5224 "Freezing Temperatures and High Winds" 12-14 March in GA, NC and SC; RMA 2022 file (Georgia March Freeze USD 30.5 million; NC March Freeze USD 5.0 million); UGA climate blog ([27 May 2022](https://site.extension.uga.edu/climate/archive/post/georgia-blueberry-crop-struggling-following-march-freeze-event/)). IBO record `us-se-freeze-2022-03` already holds the IBO view.
   - **Early-2026 Florida frosts**: the UF/IFAS report, RMA MGR-26-001 (freeze from 31 January into early February), FDACS figures (6,400 acres, 90 % production loss, USD 78.5 million, via [FreshPlaza](https://www.freshplaza.com/north-america/article/9815619/updated-report-details-winter-storm-damage-to-florida-produce/)), NABC calls (Georgia 30 %+ loss on 12 February, "less severe than initially feared" on 19 February) and ERS [FTS-384](https://ers.usda.gov/sites/default/files/_laserfiche/outlooks/113982/FTS-384.pdf). The 2026 Storm Events file has freeze rows in all six states but no crop damage values. Mississippi had a separate mid-March 2026 freeze ([MSU](https://extension.msstate.edu/news/crop-report/2026/states-blueberry-crop-hurt-march-freeze)) and 30+ inches of rain mid-May to mid-June 2026 ([MSU](https://extension.msstate.edu/news/feature-story/2026/watermelons-blueberries-devastated-summer-rain)).
   - Grower associations: FBGA posted the 2026 freeze documents; no Georgia Blueberry Commission website was found.
4. *Weekly harvest-timing series.* NASS Georgia crop progress (2011 to May 2025); AMS WA_FV408 weekly shipments by origin (Nov 2018 to Apr 2025, then MyMarketNews API); AMS shipping-point FOB reports with Central and North Florida and South Georgia sections ([WA_FV101 sample](https://www.ams.usda.gov/mnreports/wa_fv101.txt)); NABC crop calls in season. NASS Florida and North Carolina crop progress reports have no blueberry percent row (NC sample [25 May 2025](https://data.nass.usda.gov/Statistics_by_State/North_Carolina/Publications/Crop_Progress_&_Condition/2025/CW052525.pdf)).
5. *Station networks.* FAWN (open yearly zips 1998-2025, 15-minute, QA flags); UGA AEMN (web history per station, bulk by email request); NC ECONet (hourly since 1996, free account, monthly data-point quota); MSU Delta Agricultural Weather Center (hourly and daily, incl. Poplarville); South Alabama Mesonet (1-minute, 26 stations, CSV form); SC has only the request-based State Climatology Office and a Tempest-based Clemson network with no archive download seen. Details in section 4D.
6. *Extension corpora and reuse terms.* UF/IFAS EDIS: CC BY-NC-ND 4.0, images excluded ([copyright](https://ask.ifas.ufl.edu/copyright)). MSU: unaltered nonprofit copying with credit ([P1758 PDF](https://extension.msstate.edu/sites/default/files/publications/P1758_web.pdf)). UGA Farm Gate report: educational use with full credit. UGA extension pages, NC State Extension, Clemson HGIC: no reuse licence found. ACES: "All Rights Reserved". Southern Region Small Fruit Consortium: blocked (HTTP 403 bot wall).

## 2. Production context in brief

- **Florida.** About 5,700 planted acres (NASS 2022); 21.5 million lb in 2022 and about 15.7 million lb in 2023 after Hurricane Ian ([HS742](https://ask.ifas.ufl.edu/publication/AC031)). Three shipping regions: central (Polk, Lake, Orange, Pasco, Hernando, Hillsborough) about 50 % of acreage; north-central (Alachua, Levy, Marion, Putnam, Sumter) about 25 %; south-central (Highlands, Hardee, DeSoto, Manatee, Sarasota) about 25 %. South-central requires the evergreen system ([HS742](https://ask.ifas.ufl.edu/publication/AC031); [HS1362](https://ask.ifas.ufl.edu/publication/HS1362)). Florida targets the March-May window; prices fall from May when Georgia and North Carolina start ([HS742](https://ask.ifas.ufl.edu/publication/AC031)).
- **Georgia.** 45 million lb from over 20,000 acres in 2021; spring freezes are common in March and April ([C1311](https://fieldreport.caes.uga.edu/publications/C1311/blueberry-production-in-south-georgia-variety-preference-and-major-constraints/)). In the grower survey reported in C1311 (26 growers, 3,238 acres), 'Farthing' held 28 % and 'Brightwell' 22 %; SHB 61 % and rabbiteye 39 % (same source). 2022 county acres: Bacon 7,620, Appling 4,400, Ware 2,125, Clinch 1,690 ([Farm Gate 2022, p. 52](https://caed.uga.edu/content/dam/caes-subsite/caed/publications/annual-reports-farm-gate-value-reports/2022%20Farm%20Gate%20Value%20Report.pdf)). Utilized production 99.1 million lb in 2023 ([NASS Southern Region](https://www.nass.usda.gov/Statistics_by_State/Regional_Office/Southern/includes/Publications/Crop_Releases/Fruit_Production/NoncitrusFruitNut2024.pdf)).
- **North Carolina.** 9,300 acres harvested and 54 million lb in 2023; Bladen County 5,736 acres; production in Bladen, Pender, Sampson and nearby counties ([NC State statistics](https://blueberries.ces.ncsu.edu/blueberries-nc-blueberry-statistics/)). 'Legacy' blooms about 1 April and is first picked about 30 May to 3 June in southeastern NC ([Cline](http://ncblueberryjournal.blogspot.com/2011/08/blueberry-cultivar-legacy.html)).
- **South Carolina.** County acreage largely suppressed in the 2022 Census ([Table 33](https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/South_Carolina/st45_2_033_033.pdf)). In 2026, Midlands buds were breaking with early cultivars flowering on 23 February, and blueberries were in full bloom on 23 March ([Clemson, 23 Feb](https://hgic.clemson.edu/south-carolina-fruit-and-vegetable-field-report-february-23-2026/); [23 Mar](https://hgic.clemson.edu/south-carolina-field-update-march-23-2026-cold-damage-being-assessed-as-strawberry-harvest-begins/)).
- **Mississippi.** Acreage and production are down; SHB and rabbiteye in the southern half; a grower in Perry County farms 160 acres ([MSU 2026](https://extension.msstate.edu/news/crop-report/2026/states-blueberry-crop-hurt-march-freeze)). USDA-ARS Poplarville runs the regional SHB panel ([PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC12239625/)).
- **Alabama.** About 834 acres in 2017 and about 1,000 acres in 2022, concentrated in south Alabama; rabbiteye recommended for frost resilience ([Auburn, 2024](https://wire.auburn.edu/content/agriculture/2024/07/20240725-JaySpiers-blueberries.php)).
- NASS annual cultivated blueberry production is published for eight states, of which only Florida, Georgia and North Carolina are in this scope ([ERS FTS-384](https://ers.usda.gov/sites/default/files/_laserfiche/outlooks/113982/FTS-384.pdf)).

## 3. What the app already has for this scope

**Benchmark sites (15)** from `local://brief/regions/us-southeast.md` and `pipelines/weather/benchmark_sites.json`: Homestead, Arcadia, Sebring, Plant City, Groveland, Citra, Waldo, Live Oak, Tallahassee (FL); Alma, Homerville (GA); Loris (SC); Elizabethtown, Burgaw (NC); Poplarville (MS). No Alabama site.

Patterns in the model-versus-literature results:
- Evergreen pins (Homestead, Arcadia, Sebring) fall back to the managed-cycle scan. Harvest precision is 0.25 to 0.5 and published December-February bloom is not reproduced.
- Deciduous pins with long harvests are cut short: model harvest ends in May (or June in the Carolinas), while literature runs to July (Live Oak, Alma, Homerville, Poplarville) or August (Elizabethtown, Burgaw). Harvest recall is 0.33 to 0.5 there. Rabbiteye and late SHB timing is the likely cause [inference].
- Flowering freeze ranks as a recurring risk only at Tallahassee, Alma, Elizabethtown, Burgaw and Poplarville, although every source here documents freeze losses in central Florida and south Georgia.

**IBO records in scope** (`dist/evidence/ibo-regional-v1.json`): `us-se-freeze-2022-03` (GA 13 March, NC 12 March 2022), `us-nc-frost-varieties`, `us-nc-soils-water`, `us-nc-harvest`, `us-nc-2025-harvest-rain`, `us-ga-helene-2024-09`, `us-ga-2025-01-cold-snow`, `us-ga-cultivar-shift`, `us-fl-2026-frost` (dates not given by IBO), `us-fl-chill-winters`, `us-fl-harvest`. New sources should add exact dates and county detail to `us-fl-2026-frost` and `us-se-freeze-2022-03`, and add events IBO lacks: 2017 and 2018 Georgia freezes, the 2020 NC freeze ([NC State, 30 June 2020](https://cals.ncsu.edu/news/berrying-on/)), the 2023 Mississippi freeze, and 2026 Mississippi freeze and rain.

**Known gaps from the benchmark file** (abridged): no site-specific evergreen phenology; no evergreen versus deciduous split for central Florida; Waldo and Citra rest on older Gainesville cultivar tables; no SC bloom-date publication; NC and SC bloom months inferred; no UGA commercial planting calendar; Krewer and NeSmith cultivar guide unread (403); NeSmith Alapaha tables are images; AMS shipping-point reports unused; no north Florida tunnel share.

## 4. Source inventory

Status: **O** = opened, **OL** = opened-limited, **S** = search-only. All sources are in English. Full fields are in the JSON.

### 4A. Insurance, disaster designations and loss events

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [RMA Cause of Loss with Month of Loss](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/) | County, commodity, cause, month of loss, acres, indemnity | Open zips; terms not found | 1989-2026 | O | P1 |
| [RMA Summary of Business](https://www.rma.usda.gov/tools-reports/summary-of-business) | Insured acres, liability, premium by county and crop | Open; terms not found | 1989-present | O | P2 |
| [RMA claims advisories (MGR-26-001)](https://www.rma.usda.gov/policy-procedure/bulletins-memos/managers-bulletin/mgr-26-001-claims-advisory-2026-freeze-damage), [MGR-17-004](https://www.rma.usda.gov/policy-procedure/bulletins-memos/managers-bulletin/2017/mgr-17-004-claims-advisory-2017-freeze) | Dated freeze events, damage statements | Open; terms not found | 2017, 2026 | O | P2 |
| [AgRisk Viewer](https://agrisk.jornada.nmsu.edu/) | Viewer over RMA files | Open; terms not found | Mirrors RMA | O | P3 |
| [NOAA Storm Events](https://www.ncei.noaa.gov/access/storm-events-database/), [bulk CSV](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/) | Event type, zone, hour, crop damage, narratives | Open; terms not found | 1950-2026 | O | P1 |
| [FSA Secretarial designations](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) | County hazard flags, begin and end dates | Open xlsx; terms not found | 2012-2026 | O | P1 |
| [fsa-disasters archive](https://github.com/sustainable-fsa/fsa-disasters) | Tidy copy of FSA files | Open; licence not checked | 2012-present | O | P3 |
| FDACS 2026 assessment via [WGCU](https://www.wgcu.org/agriculture/2026-03-04/usda-issues-disaster-declaration-for-florida-in-wake-of-crop-damage-by-2026-freeze) and [FreshPlaza](https://www.freshplaza.com/north-america/article/9815619/updated-report-details-winter-storm-damage-to-florida-produce/) | Crop loss USD, acres, percent | Open news; primary PDF not found ([fdacs.gov](https://www.fdacs.gov/)) | Dec 2025-Feb 2026 | O | P2 |
| [UF/IFAS freeze report, 9 Feb 2026](https://fbga.memberclicks.net/assets/docs/Freeze%20event%20and%20Florida%20Blueberries%20-%20Feb%209%202026.pdf) | Station minima, wind, hours below 32 F, stage, damage | Open PDF; terms not found | 31 Jan-3 Feb 2026 | O | P1 |
| [NHC data archive](https://www.nhc.noaa.gov/data/) | Hurricane reports and tracks | Open; terms not found | to 2025 | O | P3 |
| [ERS Fruit and Tree Nuts Outlook FTS-384](https://ers.usda.gov/sites/default/files/_laserfiche/outlooks/113982/FTS-384.pdf) | 2026 freeze narrative | Open; terms not found | March 2026 | O | P3 |

### 4B. Production, acreage and land use

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [NASS Quick Stats API](https://quickstats.nass.usda.gov/api) | Acres, production, price, progress | Free key; terms not found | Varies | O | P1 |
| [2022 Census Table 33 (GA)](https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/Georgia/st13_2_033_033.pdf) | County blueberry farms and acres, 2017 and 2022 | Open; terms not found | 2017, 2022 | O | P1 |
| [Noncitrus Fruits and Nuts 2024 Summary](https://www.nass.usda.gov/Publications/Todays_Reports/reports/ncit0525.pdf), [Southern Region release](https://www.nass.usda.gov/Statistics_by_State/Regional_Office/Southern/includes/Publications/Crop_Releases/Fruit_Production/NoncitrusFruitNut2024.pdf) | State area, yield, production, price, harvested-not-sold | Open; terms not found | Annual | O | P2 |
| [Georgia Farm Gate Value Report 2022](https://caed.uga.edu/content/dam/caes-subsite/caed/publications/annual-reports-farm-gate-value-reports/2022%20Farm%20Gate%20Value%20Report.pdf) | County blueberry acres and value | Educational use with full credit | Annual; value series from 2012 | O | P1 |
| [Cropland Data Layer GA 2023 accuracy](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_ga23.htm), [EE catalog](https://developers.google.com/earth-engine/datasets/catalog/USDA_NASS_CDL) | 30 m class 242 Blueberries | Public domain (stated in catalog) | 1997-2025 | O | P2 |
| [NC State blueberry statistics](https://blueberries.ces.ncsu.edu/blueberries-nc-blueberry-statistics/) | State and Bladen acreage | Open; terms not found | 2023 data | O | P2 |

### 4C. Harvest-timing and market series

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [NASS Georgia Crop Progress](https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/) | Weekly Blueberries - Harvested percent, condition | Open PDFs; terms not found | 2011-May 2025 | O | P1 |
| [NASS Florida Crop Progress](https://www.nass.usda.gov/Statistics_by_State/Florida/Publications/Crop_Progress_&_Condition/index.php) | Narrative only | Open; terms not found | to 2025 | O | P3 |
| [AMS WA_FV408 weekly shipments](https://esmis.nal.usda.gov/publication/weekly-shipments-movement-blueberry) | Weekly lb by origin state | Open; terms not found | Nov 2018-Apr 2025 | O | P1 |
| [AMS shipping-point FOB recap WA_FV101](https://www.ams.usda.gov/mnreports/wa_fv101.txt) | Daily FL and GA blueberry supply, demand, price | Open; terms not found | Daily in season | O | P2 |
| [MyMarketNews API](https://mymarketnews.ams.usda.gov/mymarketnews-api) | Post-2025 data sets | Free key; site timed out | 2025 onward | OL | P2 |
| [NABC Crop Call reports](https://nabc.blueberry.org/wp-content/uploads/sites/6/2026/02/Crop-Call-Report-February-19-2026-1.pdf) | Weekly state forecasts, losses, GDD shifts | Open PDFs; terms not found | 2026 checked | O | P1 |

### 4D. Weather stations and decision tools

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [FAWN QA/QC archive](https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/) | 15-min T at 60 cm, 2 m, 10 m; RH; leaf wetness; rain; wind; QA flags | Open zips; terms not found | 1998-2025 | O | P1 |
| [UGA AEMN](http://www.georgiaweather.net/) | 15-min and hourly station data, chill hours, frost dates, blueberry pages | Web history open; bulk by email; terms not found | Long-running | O | P1 |
| [NC ECONet / Cardinal](https://econet.climate.ncsu.edu/) | Hourly T, RH, wind, rain, soil | Free account, 300,000 points per month (public tier) | Hourly since 1996 | O | P1 |
| [MSU Delta Ag Weather Center](http://deltaweather.extension.msstate.edu/) | Hourly and daily, incl. Poplarville | Open form; terms not found | Varies by station | O | P1 |
| [South Alabama Mesonet](http://chiliweb.southalabama.edu/) | 1-min T, RH, rain, wind, soil | Open CSV form; terms not found | 2004- | O | P3 |
| [IEM NWS warnings](https://mesonet.agron.iastate.edu/request/gis/watchwarn.phtml), [IEM ASOS](https://mesonet.agron.iastate.edu/request/download.phtml) | Freeze warnings by county; airport hourly obs | Open; terms not found | Long archive | O | P2 |
| [Clemson Extension Weather Network](https://blogs.clemson.edu/sccrops/clemson-weather-station-network/) | Tempest stations near SC farms | No archive seen | 2020- | O | P3 |
| [SC State Climatology Office](https://www.dnr.sc.gov/climate/sco/) | Weekly reports, data on request | On request | 1986- | O | P3 |
| [AgroClimate BAS](http://www.agroclimate.org/BAS), [PP366](https://ask.ifas.ufl.edu/publication/PP366) | Anthracnose and Botrytis risk by FAWN/AEMN station | Live app only | Current | O | P2 |
| [NC chill models](https://products.climate.ncsu.edu/ag/chill-models/) | Mainland blueberry chill model by station | Open | Current season | O | P3 |

### 4E. Phenology, cultivar trials and traits

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [US plant patents (TH-906)](https://patents.google.com/patent/USPP27026P3/en), [Alapaha](https://patents.google.com/patent/USPP16266P3/en), [Heintooga](https://patents.google.com/patent/US20170188494P1) | Multi-year 50 % flowering and ripening by site, chill estimates | Open text; terms not found | 1990s-2020s | O | P1 |
| [USDA-ARS Poplarville phenotypes](https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_Phenological_variation_associates_with_the_stability_of_fruit_quality_traits_in_cultivated_tetraploid_blueberry/28339583) | 187 SHB genotypes: 50 % flowering, ripening, FDP | U.S. Public Domain; file download bot-walled | 2021-2022 phenology | OL | P1 |
| [FSHS Proceedings](https://journals.flvc.org/fshs) | Florida trial papers | Open; terms not found | 1888-2023 | O | P2 |
| [Georgia cultivar release pages](http://georgiacultivars.com/cultivars/alapaha) | Relative bloom and ripening, chill | Open; terms not found | UGA releases | O | P3 |
| [NC Blueberry Journal](http://ncblueberryjournal.blogspot.com/2011/08/blueberry-cultivar-legacy.html) | NC cultivar bloom and first-harvest dates | Open; terms not found | 2011 | O | P3 |
| [Southern Region Small Fruit Consortium](https://smallfruits.org/) | UGA cultivar reports, IPM guide | HTTP 403 bot wall | Unknown | OL | P2 |

### 4F. Extension, industry and news corpora (RAG)

| Source | Contains | Access and terms | Coverage | Status | Priority |
|---|---|---|---|---|---|
| [UF/IFAS EDIS / Ask IFAS](https://ask.ifas.ufl.edu/publication/HS1362) | Systems, regions, freeze, cultivars, calendars | CC BY-NC-ND 4.0 | Current and archived | O | P1 |
| [FBGA site and newsletters](https://www.floridablueberrygrowers.org/) | Monthly management items, 2026 freeze documents | Open; "© 2019 FBGA" | 2019-2026 | O | P2 |
| [Doug's Blog, UF/IFAS](https://www.blueberrybreeding.com/blog) | Monthly disease and pest timing, evergreen notes | Open; terms not found | to Jul 2026 | O | P2 |
| [UGA Blueberry Blog](https://site.caes.uga.edu/blueberry/) | Specialist posts, Helene recovery | Open; terms not found | 2014-2026 | O | P2 |
| [Climate and Agriculture in the Southeast](https://site.extension.uga.edu/climate/) | Daily weather-to-crop posts | Open; terms not found | 2014-2026 | O | P2 |
| [CAES Field Report](https://fieldreport.caes.uga.edu/news/spring-freeze-dooms-georgia-blueberries-for-second-consecutive-year/) | News and circulars (C1311, B1413) | Open; terms not found | about 2011-2026 | O | P2 |
| [UGA county blogs (Appling)](https://site.extension.uga.edu/applingcrop/2026/05/2026-blueberry-harvest-update/) | County harvest and freeze notes | Open; terms not found | 2015-2026 | O | P2 |
| [Clemson SC Field Report](https://hgic.clemson.edu/south-carolina-fruit-and-vegetable-field-report-february-23-2026/) | Weekly regional stage and damage notes | "© 2026 Clemson University" | 2022-2026 seen | O | P1 |
| [NC State Extension blueberry portal](https://blueberries.ces.ncsu.edu/) | Statistics, freeze thresholds, practices | Open; terms not found | 1998-2025 | O | P2 |
| [NC State CALS news (2020)](https://cals.ncsu.edu/news/berrying-on/) | 2020 freeze and rain season story | Open; terms not found | 2020 | O | P3 |
| [NC Blueberry Council](https://ncblueberrycouncil.org/) | Member resources | Mostly member-only | Unknown | O | P3 |
| [MSU Extension blueberry](https://extension.msstate.edu/publications/establishment-and-maintenance-blueberries) | P1758; 2023 and 2026 loss stories | Unaltered nonprofit copying with credit | 1996-2026 | O | P2 |
| [ACES blueberry pages](https://www.aces.edu/blog/topics/crop-production/pruning-blueberries/), [Auburn news](https://wire.auburn.edu/content/agriculture/2024/07/20240725-JaySpiers-blueberries.php) | Practice and acreage statements | All Rights Reserved | Current | O | P3 |
| [GDA Market Bulletin 2018](http://www.forms.agr.georgia.gov/MBADS/pdf/2018/052318-Market-Bulletin.pdf) | Grower loss story | © 2018 GDA | 2018 issue | O | P3 |
| [Specialty Crop Grower](https://specialtycropgrower.com/lesson-learned-generational-weather-event-challenged-freeze-protection-measures-in-blueberries/) | Trade news on freezes | Terms not found | about 2021-2026 | O | P3 |

### Top 10 sources: what the sample showed

1. **RMA Cause of Loss (colsom_2022.zip, 5.8 MB).** Pipe-delimited, 30 fields per row: commodity year, state and county codes and names, commodity code (Blueberries = 0012), insurance plan, stage code, cause code and description, month of loss, year of loss, policies earning premium, policies indemnified, net planted quantity, net endorsed acres, liability, premiums and subsidies, determined quantity, indemnity amount, loss ratio. 217 blueberry rows nationally in 2022; in scope only FL, GA and NC appear. Largest in-scope totals: GA Freeze in March USD 30.51 million; NC Freeze in March USD 5.03 million; GA Freeze in January USD 4.64 million; NC Wind/Excess Wind in March USD 3.72 million; FL Freeze in January USD 1.53 million.
2. **FSA designations CY2022 xlsx.** 4,954 rows, 34 columns: FIPS, County, State, Designation Code, Designation Number, one column per hazard (incl. "Frost, FREEZE", "Insufficient Chill Hours", "Excessive rain, moisture, humidity", "Hurricanes, Typhoons, Tropical Storms"), Approval date, Begin Date, End Date, Description, Calendar Disaster Year. Georgia freeze windows in 2022 included S5262 (13-14 March), S5263 (13 March), S5264 (11-13 March), S5265 (12 March, 39 counties) and S5395-S5397 (22-28 December).
3. **Storm Events details d2017 and d2026.** 51 columns including BEGIN_DATE_TIME, EVENT_TYPE, CZ_NAME, CZ_FIPS, DAMAGE_CROPS, BEGIN_LAT/LON, EPISODE_NARRATIVE, EVENT_NARRATIVE. 2017: Georgia Frost/Freeze 16 March 2017 03:00 in many zones, each with DAMAGE_CROPS 7.85M, and a narrative tying the loss to blueberries. 2026: freeze and cold rows in all six states, no crop damage values.
4. **NASS Georgia Crop Progress.** Row "Blueberries - Harvested" with this week, previous week, previous year and 5-year average. 2011 issue shows 83, 73, N/A, N/A. 2025 Southern Region issue (19 May) carries "Georgia Blueberries - Harvested" and a blueberry condition row.
5. **AMS WA_FV408 (19 Oct 2021 TXT).** "SHIPMENTS BY ORIGINS (AMOUNTS ARE SHOWN IN UNITS OF 10,000 LBS)", mode TRUCK, origins incl. FLORIDA, GEORGIA, NORTH CAROLINA, three weekly columns plus season-to-date this and last season (FL 1954, GA 4167, NC 1669 for 2021).
6. **FAWN metadata.txt.** Columns ID, UTC, temp_soil_10cm_C, temp_air_60cm_C, temp_air_2m_C, temp_air_10m_C, rh_2m_pct, bp_2m_mb, leaf_wetness_60cm_ohms, rain_2m_inches, rfd_2m_wm2, wind speeds and directions, each with a quality flag (0 passed, 1 suspect, 2 warning, 3 erroneous, 4 missing, 5 repeated, 7 step check). 53 station IDs.
7. **UF/IFAS freeze report, 9 Feb 2026.** Table 1 columns: Region, County, Station, Min 60 cm Air Temp (F), Min Dew Point, Min Wet Bulb, Max Wind Speed, Max Wind Gust. Rows such as Lake/Okahumpka 21.05 F with 41.5 mph gusts; text gives Alachua 16.43 F and 41.5 h below 32 F, longest high-wind spell 30.75 h at Babson Park.
8. **TH-906 plant patent.** Table 1: 5-year means 2009-2013, Alapaha, GA, for 'Star', 'Camellia', 'TH-906': ratings plus date of 50 % flowering (3, 11, 8 March), date of 50 % ripening (8, 15, 12 May), fruit development period about 65-66 days.
9. **Poplarville dataset (Figshare API record).** Title, licence "U.S. Public Domain", one file "Phenotypic data -Agdata.xlsx" (88,318 bytes). Paper methods: 4 plants per genotype; 50 % flowering and 50 % ripening counted as days from 1 January for 2021 and 2022; FDP as their difference. The xlsx itself could not be fetched by script.
10. **Georgia Farm Gate 2022, p. 52.** "Blueberries Farm Gate Value 2022" with Rank, County, Acres, Farm gate Value for every county, e.g. Bacon rank 1, 7,620 acres, USD 127,819,500.

## 5. Proposed extraction and RAG jobs

Fields below are the exact targets. IBO-style records use `kind, topic, title, summary, geography_ids, period{start,end,precision}, crop_context, evidence_type, citations[]`.

| Job | Sources | Output | Method | Fields | Cadence | Effort | Priority |
|---|---|---|---|---|---|---|---|
| USSE-01 Insurance loss by county, month, cause | RMA COL, RMA SOB | time series table | CSV parse | year, state_fips, county_fips, commodity_code 0012, cause_code, cause_desc, month_of_loss, year_of_loss, policies_indemnified, net_endorsed_acres, liability_usd, indemnity_usd, loss_ratio; derived indemnity per insured acre, cause_family | backfill 1989-2026, then annual | 2.0 | P1 |
| USSE-02 County hazard windows | FSA designations | event records | CSV parse | kind=event, topic=weather, period from Begin/End Date (day), county FIPS, hazard flags to risk family, designation number | backfill 2012-2026, weekly in winter-spring | 1.0 | P1 |
| USSE-03 Storm Events in blueberry counties | Storm Events, IEM | event records | CSV parse | period (hour), CZ_FIPS, event_type, damage_crops_usd, blueberry narrative flag, EVENT_ID | backfill 1996-2026, monthly | 1.5 | P1 |
| USSE-04 Georgia harvest progress | NASS GA CP, Quick Stats | time series table | API pull (PDF fallback) | week_ending, pct_harvested, prev week, prev year, 5-yr avg, condition; derived 10/50/90 % dates | backfill 2011-2025 | 1.5 | P1 |
| USSE-05 Weekly shipments by origin | WA_FV408, MMN API, FOB | time series table | layout-aware PDF tables | week window, origin, mode, shipments_10k_lb, season-to-date; derived first week and 10/50/90 % weeks; first and last FOB quote | backfill Nov 2018-Apr 2025, then weekly via API | 2.0 | P1 |
| USSE-06 Cultivar bloom and ripening table | patents, cultivar pages, EDIS, Cline, SRSFC, FSHS | cultivar table | manual review | cultivar, species, site, years, date_50pct_flowering, date_50pct_ripening, fdp_days, chill_estimate, comparison cultivars, citation | backfill ~40 cultivars | 3.0 | P1 |
| USSE-07 Poplarville genotype phenology | ARS dataset | cultivar table | manual review | genotype, year, flowering_50pct_doy, ripening_50pct_doy, fdp_days | one-off | 1.0 | P1 |
| USSE-08 Station table for pins | FAWN, AEMN, ECONet, DAWC, IEM, USA Mesonet | station table | API pull | station metadata, distance to pin; hourly utc, t60cm, t2m, rh, dewpoint, leaf wetness, wind, rain, qc_flag | backfill 2010-2025, annual | 3.0 | P1 |
| USSE-09 Freeze event dossiers 2017-2026 | RMA bulletins, UF report, NABC, UGA, MSU, Clemson, NCSU, FDACS, FSA, RMA COL | event records | manual review | IBO event fields plus measurements (min temp, hours below 32 F, wind, loss percent, loss USD) | one-off, then per event | 3.0 | P1 |
| USSE-10 Extension advisory corpus | EDIS, FBGA, UF blog, UGA, NCSU, MSU, ACES, FSHS | claim records | HTML scrape | kind=practice/constraint/threshold, topic, crop_context (evergreen SHB, deciduous SHB, rabbiteye), region, revision date, citations | one-off, quarterly check | 4.0 | P2 |
| USSE-11 Dated stage notes | Clemson, UGA county blogs, UGA blog, FBGA, NASS FL | event records | HTML scrape | observation_date, region or county, species, cultivar, stage vocabulary, percent, source sentence | backfill 2021-2026, weekly Feb-Jul | 3.0 | P2 |
| USSE-12 Location and acreage layer | Census, Farm Gate, CDL, NCSU stats, Quick Stats | time series table | API pull | county_fips, year, source, tame_acres, bearing_acres, farms, farm_gate_value_usd, cdl pixels, cdl accuracy | backfill, annual | 2.0 | P2 |
| USSE-13 NABC crop calls | NABC | claim records | layout-aware PDF tables | report_date, state, reporter, forecast lb (fresh, processed), loss text, GDD vs prior year, shipment shift weeks | backfill 2026, weekly in season | 1.0 | P2 |
| USSE-14 FSHS blueberry papers | FSHS | claim records | layout-aware PDF tables | paper, year, site, cultivar, bloom and harvest period, freeze notes, page | one-off | 2.0 | P3 |

Review and licensing gates per job are in the JSON. Common rules: an LLM proposes extractions offline; a human checks each quote, date and geography; FSA and Storm Events rows are never shown as blueberry losses unless another source names blueberries; news and NABC text is stored as short quotes with links.

## 6. How each source maps to model checks

- **Flowering freeze and bud freeze (all deciduous pins).** Compare RMA Freeze and Frost indemnity by county-month (USSE-01) with modelled flowering-freeze winters at Alma, Homerville, Elizabethtown, Burgaw, Poplarville and Citra. Use FSA begin and end dates (USSE-02) and Storm Events hours (USSE-03) to check whether the model's freeze nights fall inside documented windows. Score hits for 2017 (15-16 March), 2022 (11-14 March) and 2026 (31 Jan-3 Feb). The model currently ranks flowering freeze only at five of 15 pins, so expect misses in central Florida and south Georgia.
- **Grid minimum-temperature bias and missed frosts.** Use FAWN 60 cm and 2 m temperatures at the matching Florida pins, ALMA for Alma, ECONet towers in Bladen and Pender, and Poplarville (USSE-08). The UF 2026 report gives canopy minima of 16.4 to 25 F; check whether MERRA-2 cells reach freezing on those nights.
- **Wind and frost protection (management layer).** The UF 2026 report, NABC 12 February and IBO `us-nc-frost-varieties` all say wind defeats overhead irrigation. Add a "windy freeze" flag (Tmin below 28 F with wind above a threshold) and test it on the 2026 and 2022 events.
- **Harvest timing.** Derive Georgia 10/50/90 % harvest dates from USSE-04 and FL, GA, NC shipment curves from USSE-05; compare with modelled harvest start and peak at Plant City, Groveland, Alma, Homerville, Elizabethtown and Burgaw. The literature runs to July or August at several pins while the model stops in May or June; shipment tails will show whether that is a rabbiteye or cultivar effect.
- **Cultivar classes and bloom timing.** Patent tables and the Poplarville dataset (USSE-06, USSE-07) give 50 % flowering and fruit-development periods by cultivar and site. Fit separate GDD targets for early SHB, mid SHB and rabbiteye, and test against Alapaha and Poplarville means. Current constants come from one Waldo site.
- **Chill shortfall.** FSA "Insufficient Chill Hours" flags, AEMN chill tables, the NC Mainland model and FAWN hourly data allow a check of modelled chill hours. The UF/IFAS Waldo trial note (168 chill hours before January in 2019 and 2020, in the benchmark file) is one anchor.
- **Disease weather.** FAWN leaf wetness at 60 cm and the AgroClimate BAS risk classes give a reference for our hourly anthracnose and Botrytis indices at Florida and south Georgia stations.
- **Harvest heavy rain.** RMA "Excess Moisture/Precipitation/Rain" and "Cold Wet Weather" by month, MSU's 2026 rain story, NCSU's 2020 rain story and IBO `us-nc-2025-harvest-rain` give dated rain-loss seasons.
- **Location and system.** Census, Farm Gate and CDL (USSE-12) show where acreage is, so pins and station choices sit on real fields. HS742 region shares support a region-level evergreen versus deciduous prior for Florida.

## 7. Access, licensing and language risks

- **Discontinued federal series.** NASS state crop progress PDFs ended in May 2025 ([Red River Farm Network](https://www.rrfn.com/2025/05/26/nass-to-end-state-specific-reports/)). AMS paused WA_FV408 from 1 May 2025. Continuity depends on Quick Stats and MyMarketNews, both needing free keys. MyMarketNews timed out from this machine.
- **Bot walls.** smallfruits.org (403), Ag Data Commons file download (202, empty), journals.ashs.org (JavaScript only), WJTV (403), weather.uga.edu (timeout). Manual browser download is needed.
- **Licences.** Only EDIS (CC BY-NC-ND 4.0), CDL (public domain, stated), the ARS dataset (U.S. Public Domain), MSU (unaltered nonprofit copying) and the Farm Gate report (educational use with credit) state terms. No licence was found for RMA, FSA, NOAA, NASS or AMS pages; they are federal works, but treat them as "terms not found" until a page states otherwise. UGA, NC State, Clemson, FBGA, NABC and news sites: show facts and short quotes with links only. ACES is "All Rights Reserved".
- **NoDerivatives.** EDIS text should be quoted, not paraphrased into new published text without attribution; summaries in claim records should cite and link.
- **Data access quotas.** NC Cardinal public tier: 300,000 data points per month. AEMN bulk history needs an email request.
- **Language.** All English. No translation risk.
- **Privacy.** Patents and the Poplarville dataset include named and numbered selections; keep only publicly released cultivars and published genotype IDs; no private breeding data.

## 8. Gaps: what I looked for and could not find

- **Evergreen SHB phenology for central and south Florida**: no site-specific, dated table. Searched UF/IFAS EDIS, HortScience/HortTechnology, FSHS and FBGA. Only release-note descriptions exist.
- **FDACS primary 2026 damage report**: not found on fdacs.gov by search; figures come from WGCU and FreshPlaza.
- **Georgia Blueberry Commission website**: not found by search.
- **South Carolina**: no public hourly mesonet; no Clemson bloom-date table; Census acreage suppressed. Clemson weekly reports are the only dated stage notes.
- **NC State or Clemson dated bloom observations by year**: not found beyond Cline's typical dates and patent tables.
- **Post-May 2025 NASS Georgia blueberry progress**: not confirmed in Quick Stats (needs a keyed call).
- **AMS Raleigh shipping-point blueberry report for NC**: seen only in third-party summaries; MyMarketNews unreachable.
- **Storm Events crop damage for 2026**: empty for SE freeze rows.
- **SC, MS, AL annual production**: NASS does not publish these states.
- **Tunnel share in north Florida and a UGA commercial planting calendar**: not found in this pass (not searched in depth).
- **Krewer and NeSmith cultivar guide and UGA Alapaha reports**: still blocked on smallfruits.org.

## 9. Ranked top 10 actions

1. Ingest RMA cause-of-loss blueberry rows for FL, GA, NC, 1989-2026 (USSE-01) and score modelled flowering-freeze winters by county and month.
2. Build the station table for the 15 benchmark pins from FAWN, AEMN (ALMA), ECONet and MSU Poplarville (USSE-08); report Tmin bias and frost hit and miss rates, including FAWN 60 cm temperature.
3. Create the 2017, 2022 and 2026 freeze dossiers (USSE-09) and attach exact dates and station minima to IBO records `us-se-freeze-2022-03` and `us-fl-2026-frost`.
4. Transcribe patent bloom and ripening tables for about 40 Southeast cultivars (USSE-06) and draft SHB early, SHB mid and rabbiteye classes.
5. Download the Poplarville xlsx by hand and ingest 2021-2022 genotype phenology (USSE-07).
6. Backfill Georgia weekly harvest percent 2011-2025 (USSE-04) and AMS weekly shipments Nov 2018-Apr 2025 (USSE-05); request free Quick Stats and MyMarketNews keys for continuity.
7. Ingest FSA designations 2012-2026 (USSE-02) and Storm Events 1996-2026 (USSE-03) for the six states.
8. Start the SC and Georgia stage-note extraction from Clemson weekly reports and UGA county blogs (USSE-11) to replace inferred bloom months at Loris and Alma.
9. Build the acreage and location layer from Census, Farm Gate and CDL (USSE-12) to weight results and place pins on fields.
10. Load EDIS and MSU text into the citation-first library under their stated licences (USSE-10); hold UGA, NCSU, Clemson and NABC text at quote-and-link level until terms are confirmed.
