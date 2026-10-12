# Australia and New Zealand: blueberry source inventory (2026-10-11)

Slug: `australia-new-zealand`. Companion file: `australia-new-zealand.sources.json` (53 sources, 11 jobs). All URLs were checked on 2026-10-11. Prose marked [inference] is my reasoning, not a source statement.

## 1. Scope and summary

I covered Australia (NSW mid-north coast, Tasmania, Queensland, Western Australia, Victoria) and New Zealand (Waikato, Hawke's Bay, Northland, Southland). I looked for statistics, trade series, station weather, disaster and adverse-event records, industry and company narrative, extension documents and land-use data. I opened 43 sources, 5 were reachable only in part, and 5 were seen only in search results.

Five most valuable findings:

1. **The Waikato frost is in the station record, and the grid misses it by about 8 C.** The NIWA October 2022 summary lists Hamilton Airport at -2.9 C on 7 October 2022, the lowest October minimum since records began in 1946, plus Waikeria -2.8 C, Matamata -2.4 C and Hamilton Ruakura -2.0 C ([NIWA PDF](https://niwa.co.nz/sites/default/files/Climate_Summary_October_2022_Final.pdf)). Free NOAA ISD hourly data for Hamilton AWS (WMO 93173) show air below 0 C from 14:00 to 19:00 UTC on 6 October, with a minimum of -2.8 C at 18:00 UTC (07:00 NZDT on 7 October) ([NCEI API](https://www.ncei.noaa.gov/access/services/data/v1)). The app's POWER cell gave 5.15 C for that UTC day (`docs/research/2026-10-05/ibo_event_checks.json`). A grower measured -4.8 C on the night of 7 October ([Farmers Weekly](https://www.farmersweekly.co.nz/news/blueberry-crops-wiped-out-by-late-frost/)).
2. **The Penguin (Tasmania) chill value is far too low.** Devonport Airport, about 30 km east of Penguin, logged 555 hourly readings below 7.2 C from May to August 2023 (NOAA ISD, one API call). The model gives a mean of 58 chill hours for the Penguin cell. [inference] The sea-dominated grid cell, not the climate, drives the "chill shortfall" risk.
3. **New Zealand has a free monthly blueberry export series.** Stats NZ HS10 code 0810400001 ("Fruit, edible; blueberries, fresh") is published by month and country from 2015. In February 2026, 525,529 kg worth NZD 18.0 million went to Australia ([Stats NZ](https://www.stats.govt.nz/large-datasets/csv-files-for-download/overseas-merchandise-trade-datasets/)). This is the best open harvest-timing proxy in the region.
4. **The Hort Innovation handbook gives harvest availability by state and month, and tunnel area.** The 2023/24 blueberry chapter shows Tasmania "High" in January, February and March and "Medium" in April. It shows NSW "High" from June to January. Polyhouses and tunnels produced 42.7% of national volume, with 1,259 ha in NSW ([Berries Australia PDF](https://berries.net.au/wp-content/uploads/2025/03/BB-ahsh-hort-stats-fruit-23-24.pdf)).
5. **Dated adverse-event records exist for New Zealand, through Inland Revenue rather than MPI.** MPI pages sit behind a bot wall. An archived Inland Revenue page states: "On 10 December 2022, the Government declared this frost a medium-scale adverse event" for Waikato and Bay of Plenty ([Wayback copy](http://web.archive.org/web/20250906233615/https://www.ird.govt.nz/natural-disasters-adverse-emergency/events-list/2022-december-frost)). Blueberries NZ put the 2022 loss at 1,200 to 1,400 t of about 3,650 t national production. It also named an earlier comparable frost on 25 October 2001 ([Rural News](https://www.ruralnewsgroup.co.nz/hort-news/hort-general-news/october-frosts-bites-blueberry-industry-badly)).

## 2. Production context in brief

**Australia.** Production was 28,382 t in 2024-25 and 28,877 t in 2023-24. NSW grew 24,116 t in 2024-25 and Tasmania 1,900 t ([ABS data cube, Table 2](https://www.abs.gov.au/statistics/industry/agriculture/australian-agriculture-horticulture/2024-25)). Production centres on Coffs Harbour. Other regions are the Atherton Tablelands, Yarra Valley, Tasmania and Western Australia ([Handbook 2023/24](https://berries.net.au/wp-content/uploads/2025/03/BB-ahsh-hort-stats-fruit-23-24.pdf)). Coastal NSW grows southern highbush and rabbiteye as evergreen crops that flower and fruit through winter and spring ([NSW DPI](https://www.dpird.nsw.gov.au/agriculture/water/clean-coastal-catchments/fertiliser-stewardship-group/fsg-insights/a-study-of-seasonal-leaf-nitrogen-in-southern-highbush-blueberry-grown-as-an-evergreen-crop-in-australia)). The Oz Group cooperative supplies "over the June to January period" ([Oz Group booklet](https://ozgroupcoop.com.au/wp-content/uploads/2025/07/Oz-Group-Booklet-2025.pdf)). Tasmania grows mostly northern highbush, with a main harvest from December to May. Production sits largely on the Central North West coast ([Tasmanian Grown](https://tasmaniangrown.au/what-we-grow/fruit/blueberries/)). Western Australian growers use pruning to harvest from March to January (IBO 2025, already in the app). In Queensland, T&G runs a 36 ha tunnel and net farm ([T&G 2024 annual report](https://tandg.global/wp-content/uploads/2025/03/TG-Global-Annual-Report-2024.pdf)).

**New Zealand.** Blueberry area was 792 ha in 2024, up from 549 ha in 2011 ([Figure.NZ, Stats NZ](https://figure.nz/chart/KUrywEnAVzQynaJQ-xFo6bEu4advh2FsR)). The 2022 census places 246.1 ha in Waipā (Ohaupo), 93.2 ha in Hastings, 80.9 ha in Southland and 51.7 ha in Hauraki (Ngatea) ([Figure.NZ](https://figure.nz/chart/KXYvRQRY7ISAHDst-PYdDIfpcUFy46P2H)). The season has two halves. Before Christmas, Australian-bred cultivars grow in tunnels and substrate (about 80 ha), harvested from August. After Christmas comes outdoor fruit, much of it rabbiteye for export to Australia ([Rural News](https://www.ruralnewsgroup.co.nz/hort-news/hort-general-news/october-frosts-bites-blueberry-industry-badly)). Late rabbiteye cultivars (Maru, Rahi, Ono, Centra Blue) supply February to mid-April ([Land Use NZ](https://landusenz.org.nz/blueberries/)).

## 3. What the app already has for this scope

- **Benchmark sites** (`pipelines/weather/benchmark_sites.json`):
  - `au-nsw-coffs-harbour`: evergreen; published bloom June to August and harvest June to February.
  - `au-tas-penguin`: deciduous NHB; bloom September to October; peak January to February.
  - `nz-waikato-ohaupo`: deciduous mix; bloom September to October; harvest October to March.
- **Recorded gaps:** Coffs pruning month, Coffs bloom peak, the Tasmania peak conflict, the Costa Sulphur Creek fact (snippet only), Waikato planting months, and no Plant & Food Research document.
- **IBO records** (`dist/evidence/ibo-regional-v1.json`, 8 in scope):
  - `au-nnsw-2022-floods`
  - `au-coffs-harvest`
  - `au-alfred-2025`
  - `au-wa-pruning`
  - `nz-waikato-2022-10-frost` (month precision only)
  - `nz-hb-2023-floods`
  - `nz-2024-25-heat`
  - `nz-harvest`
- **Event check:** the POWER cell for Ohaupo shows a minimum of 5.15 C on 2022-10-06 and zero freeze days (`docs/research/2026-10-05/ibo_event_checks.json`).
- **Earlier research:** BOM Climate Data Online is already listed in `04_validation_data_and_protocol.md`. This report adds only site-specific use of it.

## 4. Source inventory

Status codes: O = opened, L = opened-limited, S = search-only.

### 4.1 Weather stations and gridded weather

| Source | Contents | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [NIWA monthly climate summaries](https://niwa.co.nz/climate-and-weather/monthly) | Record station extremes with day and rank; event narrative | Open; infographic CC BY-NC-ND 4.0 | en | 2008 to 2026, monthly | O | P1 |
| [DataHub CLIDB](https://data.niwa.co.nz/pages/clidb-on-datahub) | NZ station archive (replaces CliFlo) | Free account; non-commercial free, commercial paid | en | Station-dependent | O | P1 |
| [NOAA ISD global-hourly](https://www.ncei.noaa.gov/access/services/data/v1) | Hourly TMP and DEW at Hamilton AWS 93173, Coffs Harbour 94791, Devonport 95960, Wynyard 95957, Napier 93373 | Open | en | 1942 onward (Coffs); 2021 onward (Hamilton AWS) | O | P1 |
| [SILO](https://www.longpaddock.qld.gov.au/silo/) | Daily 0.05 deg grid and about 8,000 station points; rh_tmin, vp, radiation | Open, CC BY 4.0 | en | 1889 to yesterday | O | P1 |
| [BOM Climate Data Online](https://www.bom.gov.au/climate/data/) | Daily station Tmin, Tmax, rain | Open, CC BY 4.0 where stated | en | Station-dependent | O | P2 |
| [DPIRD Weather 2.0 API](https://cran.r-project.org/web/packages/weatherOz/vignettes/weatherOz_for_DPIRD.html) | WA minute to yearly data, frost and heat minutes | Free API key, CC BY 3.0 AU | en | Minute data 2 years back | L | P2 |
| [BOM Daily Weather Observations](https://www.bom.gov.au/climate/dwo/) | 9am and 3pm temperature and humidity | Open | en | Rolling 13 months | O | P3 |
| [HortPlus MetWatch](https://www.hortplus.com/metwatch) | 100+ orchard stations, leaf wetness, chill, frost forecast | Paid (NZD 150 per user per month) | en | Not stated | O | P3 |
| [MetService data policy](https://about.metservice.com/our-data-access-policy) | Access categories; most web data personal use only | Paid for commercial | en | n/a | O | P3 |

Samples seen:
- **NIWA PDF:** "Low records or near-records" table, with columns for location, value, day, year records began and rank.
- **ISD:** CSV with STATION, DATE (UTC), REPORT_TYPE FM-12, and TMP/DEW in tenths of a degree with quality flags.
- **SILO:** variable list with API codes (daily_rain R, max_temp X, min_temp N, rh_tmin G, vp V).

### 4.2 Production, trade and land use

| Source | Contents | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [Hort Innovation Statistics Handbook, blueberries](https://berries.net.au/wp-content/uploads/2025/03/BB-ahsh-hort-stats-fruit-23-24.pdf) | Production, trade, state share, month-by-state availability grid, tunnel ha by state | Open; terms not found | en | Annual editions | O (landing page L) | P1 |
| [Stats NZ HS10 exports](https://www.stats.govt.nz/large-datasets/csv-files-for-download/overseas-merchandise-trade-datasets/) | Monthly kg and FOB by country for HS 0810400001 | Open, CC BY 4.0 | en | 2015 to Aug 2026 | O | P1 |
| [Stats NZ census via Figure.NZ](https://figure.nz/chart/KXYvRQRY7ISAHDst-PYdDIfpcUFy46P2H) | Blueberry ha by territorial authority (2022); national ha 2011 to 2024 | Open, CC BY 4.0 | en | 2011 to 2024 | O | P1 |
| [ABS horticulture data cube](https://www.abs.gov.au/statistics/industry/agriculture/australian-agriculture-horticulture/2024-25) | Blueberry t and farm gate $m by state | Open; Creative Commons (version not read) | en | 2020-21 to 2024-25 | O | P2 |
| [UNE protected cropping map](https://www.une.edu.au/about-une/news-and-events/news/2023/07/launch-of-first-national-map-of-australias-protected-cropping-structures) | Nets, tunnels, glasshouses mapped nationally | Open dashboard; terms not found | en | 2023 onward | O (dashboard not opened) | P2 |
| [Fresh Facts](https://freshfacts.co.nz/) | NZ blueberry ha and export value by year | Open; terms not found | en | 2016 to 2025 editions | O | P3 |
| [MPI SOPI](https://www.mpi.govt.nz/resources-and-forms/economic-intelligence/situation-and-outlook-for-primary-industries/sopi-reports) | Horticulture outlook; blueberries inside "other fresh fruit" | Bot wall | en | Twice yearly | L | P3 |
| [ABARES CLUM](https://www.agriculture.gov.au/abares/aclump/land-use/catchment-scale-land-use-and-commodities-update-2023) | 50 m land use; commodity polygons | Site timed out | en | 2008 to 2023 | L | P3 |
| [NRE Tasmania market profile 2014](https://nre.tas.gov.au/Documents/Blueberry%20Profile%20updated%20March%202014.pdf) | 2012 production and retail prices by period | Open | en | 2012 | O | P3 |

Samples seen:
- **ABS Table 2:** columns "Region codes, Region, Data item, 2020-21 ... 2024-25". The Australia blueberry row reads 23,452 / 19,608 / 20,211 / 28,877 / 28,382 t.
- **Stats NZ CSV:** columns "month, hs, hs_desc, uom, country, Export_FOB, Export_Qty, Re_export_FOB, Re_export_Qty, total_export_FOB, total_export_qty, status".
- **Handbook:** a "Production system by state" table with columns for polyhouse and tunnel ha and t, and conventional t.

### 4.3 Disasters, declarations and losses

| Source | Contents | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [DisasterAssist](https://www.disasterassist.gov.au/find-a-disaster/australian-disasters) | AGRN, dates, state, hazard, name; detail pages list LGAs | Open | en | 43 pages x 20 events | O | P1 |
| [NSW disaster declarations](https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/about-us/recovery/natural-disaster-declarations) | AGRN, type, name with start date, LGAs, assistance | Open | en | FY 2018-19 to 2026-27 | O | P1 |
| [IRD adverse events list](https://www.ird.govt.nz/natural-disasters-adverse-emergency/events-list) | NZ event, classification, declaration date, regions | Open | en, mi | 2023 to 2026 live; older pages in Wayback | O | P1 |
| [QRA DRFA activations](https://www.qra.qld.gov.au/disaster-funding-activations/activations) | 150 Queensland activations with PDFs | Open | en | 2023-24 onward seen | O | P2 |
| [Beehive releases](https://www.beehive.govt.nz/release/further-support-upper-north-island-regions-hit-significant-weather) | Ministerial classification releases | Open | en | Ongoing | O | P3 |
| [MPI adverse event classification](https://www.mpi.govt.nz/funding-rural-support/adverse-events/how-we-classify-adverse-events) | Classification scale | Bot wall | en | n/a | L | P3 |
| [MPI cyclone recovery dashboard](https://www.civildefence.govt.nz/assets/emergency-uploads/Cyclone-Gabrielle/Cyclone-Recovery-Unit/MPI-Cyclone-Recovery-Dashboard-Reporting-22-May-2023-Public.pdf) | 100 growers and about 4,900 ha heavily affected (HB and Tairāwhiti) | Open | en | May 2023 | O | P3 |
| [NEDC Emergency Event Data Catalogue](https://eedc.nedc.nz/) | Data links for Gabrielle, Hale, Jan 2026 | Open | en | 2023 to 2026 | O | P3 |

Samples seen:
- **NSW FY 2021-22 table:** AGRN 980, "North East NSW severe weather from 20 October onwards", LGA Coffs Harbour. AGRN 1012, "NSW Severe Weather and Flooding from 22 February 2022 onwards", which includes Coffs Harbour.
- **DisasterAssist:** columns "Start date, End date, State / Territory, Disaster Types, Name of Disaster, AGRN".
- **IRD (archived):** "2022 December - Severe frost in Waikato and Bay of Plenty", declared medium-scale on 10 December 2022.

### 4.4 Industry, company and news narrative (RAG candidates)

| Source | Contents | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [Farmers Weekly NZ](https://www.farmersweekly.co.nz/news/blueberry-crops-wiped-out-by-late-frost/) | 7 Oct 2022 frost, -4.8 C on farm, helicopters protect to -2 C, 90% loss | Open | en | Archive | O | P1 |
| [Rural News Hort News](https://www.ruralnewsgroup.co.nz/hort-news/hort-general-news/october-frosts-bites-blueberry-industry-badly) | 1,200 to 1,400 t loss; previous frost 25 Oct 2001; tunnels unaffected | Open | en | Archive | O | P1 |
| [Oz Group booklet](https://ozgroupcoop.com.au/wp-content/uploads/2025/07/Oz-Group-Booklet-2025.pdf) | Month calendar of harvest intensity | Open | en | 2025 | O | P1 |
| [RNZ Country](https://www.rnz.co.nz/news/country/477503/blueberry-crops-in-waikato-wiped-out-in-severe-frost) | Frost loss up to NZD 25m; most Waikato growers lost 90% | Open | en | Archive | O | P2 |
| [ABC News / ABC Rural](https://www.abc.net.au/news/rural/2015-11-26/financial-assistance-blueberry-growers-nsw/6973508) | Oct 2015 Corindi hail (AUD 2.5 to 3m, 15 to 20 farms); Nov 2025 Kungala storm | Open | en | 2015 to 2026 found | O | P2 |
| [ACM regional news, May 2025 floods](https://www.begadistrictnews.com.au/story/8989569/blueberry-prices-unaffected-by-the-recent-floods-impact/) | About 25% of national crop destroyed | Soft paywall | en | June 2025 | O | P2 |
| [Australian Berry Journal](https://berries.net.au/spring-2026-australian-berry-journal-is-out-now/) | Quarterly practice, trials, profiles | Open (Issuu) | en | About 2019 to 2026 | O | P2 |
| [Berries Australia](https://berries.net.au/home/about/blueberries/) | Season windows, risks, varieties | Open; Hort Innovation copyright | en | Static | O | P2 |
| [Fruit Growers Tasmania](https://www.fruitgrowerstas.org.au/media-releases-2025/tasmanian-blueberry-season-in-full-swing/) | Dated Tasmanian season statements | Open | en | 2025 page | O | P2 |
| [Tasmanian Grown](https://tasmaniangrown.au/what-we-grow/fruit/blueberries/) | Harvest Dec to May; varieties; regions | Open | en | 2023/24 | O | P2 |
| [Costa Group annual reports](https://www.annualreports.com/HostedData/AnnualReportArchive/c/ASX_CGC_2020.pdf) | Berry weather impacts, drought response | Open | en | CY2019 to CY2022 | O | P2 |
| [T&G Global annual reports](https://tandg.global/investors/reporting/) | Queensland heat 2023/24; tunnel ha; yield assumptions | Open | en | 2023 to 2025 | O | P2 |
| [Food & Drink Business on Costa, Dec 2019](https://www.foodanddrinkbusiness.com.au/news/driscoll-s-picks-up-stake-in-costa-group) | Early pruning of blueberries at Corindi in drought | Open | en | Dec 2019 | S | P3 |
| [The Land, Oct 2021 hail](https://www.theland.com.au/story/7494774/helluva-hail-knocks-blueberry-harvest/) | Harvest-season hail at Coffs | Unknown | en | Oct 2021 | S | P3 |
| [Blueberries New Zealand](https://www.blueberriesnz.co.nz/) | Member login; little public content | Restricted | en | n/a | O | P3 |

### 4.5 Extension, phenology, cultivar and research

| Source | Contents | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [Pollination Aware case study 5](https://www.planthealthaustralia.com.au/wp-content/uploads/2024/01/10-112.pdf) | Peak flowering month by state: NSW Sep, QLD Aug, SA Sep, TAS Oct, VIC Sep | Open | en | 2008 data | O | P2 |
| [Land Use NZ: Blueberries](https://landusenz.org.nz/blueberries/) | NZ cultivars by market window; chill by type; planting timetable | Open | en | About 2017 | O | P2 |
| [NSW DPI FSG insights](https://www.dpird.nsw.gov.au/agriculture/water/clean-coastal-catchments/fertiliser-stewardship-group/fsg-insights/a-study-of-seasonal-leaf-nitrogen-in-southern-highbush-blueberry-grown-as-an-evergreen-crop-in-australia) | Evergreen SHB phenology; post-harvest growth from December | Open (Cloudflare) | en | 2020 to 2021 | O | P2 |
| [NRE Tasmania fact sheet](https://nre.tas.gov.au/Documents/WfW-Blueberry-factsheet.pdf) | Budbreak, flowering, ripening, chill, frost thresholds | Open | en | April 2012 | O | P2 |
| [NRE Tasmania RTI 2017-18](https://nre.tas.gov.au/Documents/RTI%20002%202017-18.pdf) | Costa Sulphur Creek infected premise, over 150,000 plants; 58 state sites | Open | en | 2016 to 2017 | O | P2 |
| [Hort Innovation Blueberry Fund](https://www.horticulture.com.au/Growers/Industries/Blueberry) | Levy R&D reports | JavaScript site; old links 404 | en | 2007 onward | L | P2 |
| [Coffs Landcare grower report](https://www.coffsharbourlandcare.org.au/wp-content/uploads/Blueberry-grower-report-final.pdf) | Irrigation, erosion, water practice | Open | en | 2017 | O | P3 |
| [Acta Hort 1117 (Scalzo et al. 2016)](https://www.actahort.org/books/1117/1117_8.htm) | Evergreen Sharpblue autumn, winter and spring crops; rust from 2001 | Abstract open; full text paid | en | 2016 | O | P3 |
| [NRE Tasmania blueberry rust](https://nre.tas.gov.au/biosecurity-tasmania/plant-biosecurity/pests-and-diseases/blueberry-rust) | Rust no longer List A | Open | en | 2014 onward | S | P3 |
| [Wright 1993, Acta Hort 346](https://ishs.org/ishs-article/346_7/) | Corindi SHB and RE performance | Paid | en | 1993 | S | P3 |
| [Progress in blueberry research in NZ (2011)](https://www.tandfonline.com/doi/full/10.1080/15538362.2011.619444) | Plant & Food Research breeding history | Unknown | en | 1950s to 2011 | S | P3 |

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON.

| Job | Output | Sources | Exact fields | Effort | Priority |
|---|---|---|---|---|---|
| ANZ-01 Waikato frost station table | station table | NIWA, ISD, DataHub, Farmers Weekly, Rural News | station_id, name, lat, lon, elevation_m, timestamp_utc, timestamp_local, tmin_c, dewpoint_c, hours_below_0c, hours_below_minus2c, record_rank, grid_cell_tmin_c, event_id | 1.0 d | P1 |
| ANZ-02 NZ monthly export series | time series | Stats NZ HS10, Fresh Facts | month, hs10, country, export_fob_nzd, export_qty_kg, status | 1.0 d | P1 |
| ANZ-03 AU production, seasonality, tunnel share | time series | ABS cube, Handbook, Oz Group | year, state, production_t, value_aud_m, month, availability_class, protected_ha, protected_t, conventional_t, edition | 1.5 d | P1 |
| ANZ-04 Disaster and adverse-event records | event records | NSW RA, DisasterAssist, QRA, IRD, Beehive, MPI dashboard | kind, topic, title, period.start, period.end, period.precision, geography, hazard, agrn or classification, declaration_date, evidence_type, citations | 2.0 d | P1 |
| ANZ-05 Benchmark station climate tables | station table | SILO, BOM CDO, ISD, DPIRD, DataHub | site_id, station_id, distance_km, date, tmin_c, tmax_c, hourly temp, rh, chill_hours_below_7.2c (May to Aug), frost_days, power_tmin_c, bias_c | 2.0 d | P1 |
| ANZ-06 News and industry RAG corpus | claim records | RNZ, Farmers Weekly, Rural News, ABC, ACM, The Land, FGT, ABJ, Berries Australia | kind, topic, title, summary, period, crop_context, evidence_type, geography_ids, citations, limitations | 3.0 d | P2 |
| ANZ-07 Company weather-impact claims | claim records | Costa, T&G | company, location, period, hazard, impact, management response, citations with PDF page | 1.0 d | P2 |
| ANZ-08 Tasmania timing reconciliation | claim records | NRE 2012, FGT 2025, Handbook, Tasmanian Grown, Pollination Aware, ABS | claim, months, statement date, statement type, geography, source | 0.5 d | P1 |
| ANZ-09 NZ area by district | time series | Stats NZ via Figure.NZ | territorial_authority, year, blueberry_ha, national_ha | 0.5 d | P2 |
| ANZ-10 Climate-summary extreme mining | event records | NIWA summaries, BOM statements | station, element, value, date, record_rank, year_began, region, nearest district | 2.0 d | P2 |
| ANZ-11 Cultivar and system table | cultivar table | Land Use NZ, Tasmanian Grown, Berries Australia, Acta Hort, NSW DPI | cultivar, species group, chill class, market window, region, system, source | 0.5 d | P3 |

**Review rules.** The design rules in `ibo_integration_review.md` apply. Keep document, claim and event records separate. A human reviews every extracted number. Keep a declaration date apart from the event date. Store short quotes and links only, not news full text.

## 6. How each source maps to model checks

- **Bud and flower freeze (Waikato):**
  - Compare the hourly ISD and DataHub minima at Hamilton AWS, Ruakura and Waikeria with POWER on 6 to 7 October 2022.
  - The IBO check found 0 freeze days at the cell. Hamilton AWS shows 6 hourly readings below 0 C (14:00 to 19:00 UTC).
  - Repeat for 25 October 2001, the earlier frost named by Blueberries NZ, using DataHub. ISD Hamilton AWS starts only in 2021.
  - Use the Pollination Aware bloom months and the Monavale bloom months to check that flowering overlapped both dates.
- **Chill dormancy (Penguin):**
  - Compute May to August hours below 7.2 C at Devonport, Wynyard and the SILO grid for 2010 to 2025.
  - Compare them with the modelled 58 h, and with the 800 to 1,200 h requirement in the [NRE fact sheet](https://nre.tas.gov.au/Documents/WfW-Blueberry-factsheet.pdf).
  - The 2023 sample (555 h at Devonport) already suggests the cell error, not the climate, drives the chill_shortfall risk.
- **Harvest timing:**
  - Compare modelled harvest months with the Handbook availability grid for NSW and Tasmania, the Oz Group month calendar for Coffs, and Stats NZ monthly exports for NZ rabbiteye.
  - Example: Coffs harvest recall is 0.56 because the model ends in October. The Handbook and Oz Group show high volume in December and January, so the gap is real.
- **Harvest heavy rain and storms:**
  - Match declared events for Coffs Harbour LGA (AGRN 980, October 2021; AGRN 1012, February 2022; May 2025 floods) with modelled harvest_heavy_rain hits in the same months.
  - The ABC October 2015 hail at Corindi tests fruit damage during harvest. The app has no hail family, so log it as unmodelled.
- **Heat:** T&G reports heat at the end of the 2023/24 summer on its Queensland farm. Check modelled fruit-stage heat for a Queensland cell in February to March 2024.
- **Water and drought:** Costa's late-2019 Corindi drought (raspberry removal, early blueberry pruning) and the Tumbarumba bushfire loss of 200 t serve as drought and fire validation points. The app has no fire family.
- **Management and protection:** Use the Handbook tunnel share (42.7% of national volume) and the Rural News statement that tunnel crops escaped the 2022 frost. Together they support a protected-cropping flag that suppresses frost and rain risk for tunnel production.
- **Location mapping:** Stats NZ district areas confirm the Ohaupo pin (Waipā holds 246.1 ha). The NRE RTI file confirms the Sulphur Creek farm near the Penguin pin.

## 7. Access, licensing and language risks

- **Bot walls:**
  - mpi.govt.nz (Incapsula) blocks curl, headless Chromium and the Wayback Machine. MPI SOPI and the classification page need a manual browser visit.
  - NSW DPI pages use Cloudflare. They render in a headless browser.
  - agriculture.gov.au (ABARES) timed out from this network.
- **JavaScript-only pages:** Hort Innovation (handbook landing page and project reports), DisasterAssist tables, the IRD event list, Stats NZ release pages and metservice.com. Scraping needs a browser.
- **Broken links:** Hort Innovation historic final reports return 404 (for example BB11002). The IRD removes old event pages, so cite Wayback copies.
- **Licences:**
  - Open with attribution: SILO CC BY 4.0, BOM CC BY 4.0 where stated, Stats NZ and Figure.NZ CC BY 4.0, DPIRD CC BY 3.0 AU.
  - DataHub charges for commercial use. Public display in the app needs a licence check.
  - NIWA infographics are CC BY-NC-ND.
  - MetService website data are for personal use only.
  - Handbook, Berries Australia, FGT, company and news content: no reuse licence found. Store short quotes with links only.
- **Language:** all sources are in English. IRD pages are bilingual English and te reo Māori. No other-language sources were needed. A Spanish trade-press search on Australian pruning found nothing new.
- **Statistical conflicts:**
  - Tasmania 2023/24 tonnage appears as 1,652 t (6.0%, Handbook), 1,933 t (ABS, revised), 1,900 t (9%, Tasmanian Grown) and about 2,200 t (11%, FGT for "last season").
  - Coffs share is "over 80%" (ACM), "circa 55%" (Oz Group, its own region) and 85.6% (NSW, Handbook).
  - ABS state shares are near-constant across years [inference: modelled splits].

## 8. Gaps: what I looked for and could not find

- **Coffs Harbour evergreen pruning month: not found in any primary source.**
  - Searched: NSW DPI pages, the Coffs Landcare report, Berries Australia, the ABJ index, Hort Innovation (links broken), the Acta Hort abstract, ABC Rural and Spanish trade press.
  - Indirect evidence: Oz Group shows no blueberry harvest in March to April and low volume in February and May. The Handbook shows NSW at Medium in February, Low in March and None in April to May. NSW DPI says post-harvest growth and nutrient uptake peak from December.
  - Costa early-pruned blueberries at Corindi in late 2019 because of drought (search-only).
  - [inference] Main pruning most likely falls between February and April, after the summer harvest and before winter flowering. This needs confirmation from an ABJ article, a Hort Innovation final report or the NSW DPI berry development officer.
- **Coffs bloom peak:** not found. Pollination Aware gives a September NSW peak from 2008 data, before the winter-flowering evergreen cultivars. Treat it as dated.
- **Tasmania peak conflict: explained, not a true contradiction.**
  - The government statement is a 2012 Wealth from Water fact sheet. It covers "most commercial varieties" ripening "in February to early March" in the main production regions.
  - The industry statement (FGT, 16 January 2025) covers volume and gives a peak from early January to mid February in a slightly late season.
  - The Handbook 2023/24 grid shows High in January to March.
  - Recommendation: benchmark peak January and February, with March as a shoulder. Store both claims with dates.
- **Plant & Food Research documents:** only a 2011 journal article and ISHS abstracts, seen in search results. No open P&FR phenology or frost report was found.
- **Waikato planting months:** found only as a generic NZ timetable (plants supplied May to July; field planting in autumn and winter) on [Land Use NZ](https://landusenz.org.nz/blueberries/). Nothing specific to Waikato.
- **ABARES:** no blueberry-specific statistics found. CLUM commodity content is unverified because of the timeout.
- **Crop insurance:** none. A grower states that "there is no insurance offered in NZ for such events" ([Farmers Weekly](https://www.farmersweekly.co.nz/news/blueberry-crops-wiped-out-by-late-frost/)). No Australian blueberry insurance dataset was found.
- **Australian monthly trade by HS code:** not found free. The Handbook uses GTA/TDM data, which is paid.
- **Wholesale prices:** no open Australian or NZ weekly blueberry price series found.
- **Hawke's Bay blueberry-specific Gabrielle damage:** only the IBO record. Official sources aggregate horticulture.
- **Hourly BOM history:** not free. Use ISD or SILO instead.

## 9. Ranked top 10 actions for this scope

1. **Run ANZ-01.** Add a `station_evidence` block to `nz-waikato-2022-10-frost`. It holds the NIWA record minima and the ISD hourly series, and sets the event date to the night of 6 to 7 October 2022 (day precision). Effort is 1 day.
2. **Run ANZ-05 for Penguin first.** Compute 2010 to 2025 station chill at Devonport and Wynyard, plus SILO. Mark the Penguin cell as sea-contaminated and choose an inland neighbour cell or bias-correct. Effort is 1 day.
3. **Ingest Stats NZ HS10 0810400001 monthly exports from 2015 (ANZ-02).** Use them as NZ harvest-timing truth and loss-year flags. Effort is 1 day.
4. **Extract the Handbook month-by-state availability grids and tunnel tables (ANZ-03).** Use every available edition, and add Coffs and Tasmania harvest checks. Effort is 1.5 days.
5. **Close the Tasmania peak conflict (ANZ-08).** Update the benchmark note with dated claims. Effort is 0.5 day.
6. **Build the AU/NZ declaration event table (ANZ-04).** Filter to blueberry LGAs and regions, and archive the IRD pages. Effort is 2 days.
7. **Add the new dated events to the evidence library (ANZ-06, ANZ-07).** These are: the 25 October 2001 Waikato frost, October 2015 Corindi hail, October 2021 Coffs hail, May 2025 NSW floods, the November 2025 Kungala storm, the 2019/20 Tumbarumba fire, and Queensland heat in 2023/24. Effort is 3 to 4 days.
8. **Find the Coffs pruning month.** Search ABJ article PDFs on berries.net.au and the new Hort Innovation project pages. If nothing turns up, ask Berries Australia or NSW DPI directly; that is outside this research task. Effort is 1 day.
9. **Request a DataHub account (free, non-commercial).** Pull hourly Hamilton, Ruakura and Hawke's Bay series for disease-index and frost bias checks. Effort is 1 day.
10. **Add a protected-cropping flag for NSW and NZ tunnel production.** Base it on the Handbook tunnel share, the UNE PCS map and the evidence that tunnels escaped the 2022 frost. Effort is 1 day of design.
