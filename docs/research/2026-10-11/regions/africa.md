# Africa source inventory (excluding Morocco): blueberry weather-risk app

Slug: `africa`. Checked on 2026-10-11. Companion file: `africa.sources.json` (48 sources, 8 jobs).

Verification labels follow the shared brief: `opened`, `opened-limited`, `search-only`. My own reasoning is marked [inference].

## 1. Scope and summary

I covered South Africa, Zimbabwe, Namibia, Kenya, Zambia, Tanzania and Egypt. I also added Tunisia, which exports blueberries and is not in the brief list. Morocco is out of scope. I searched in English, Afrikaans, Arabic and French. I opened each source and pulled a small sample where the source had data.

The five most valuable findings:

1. **Dated, cultivar-specific stage data for Western Cape exist in open full text.** The Steyn (2022) Stellenbosch MSc thesis ([PDF](https://scholar.sun.ac.za/server/api/core/bitstreams/47824860-fa96-4626-b2b2-da6439d6a8f4/content)) gives day-level dates for two Australian-bred cultivars at Hex River in 2020 and 2021. For cultivar 8-42, 50% flowering fell on 7 July 2020 and 9 July 2021, and peak harvest on 26 October 2020 and 25 October 2021. The thesis also gives the exact trial coordinates and the pruning date: the last week of November in 2019 and 2020. This closes the "pruning dates not found" gap for Wolseley. The ScienceDirect paper was blocked (403), but the thesis is open.
2. **The Zimbabwe peak conflict is resolved: IBO and GAIN measure different things.** GAIN's "peak season for Zimbabwe blueberries is June/July" sits in its section on South African *imports* ([GAIN SF2026-0027](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=South%20African%20Blueberry%20Market%20Analysis_Pretoria_South%20Africa%20-%20Republic%20of_SF2026-0027.pdf)). UN Comtrade shows South African imports from Zimbabwe of 129.7 t in June 2024, 46.3 t in August and 13.0 t in October. Zimbabwe's exports to the EU in 2024 were 208 t in August, 976 t in September and 1,898 t in October ([Eurostat Comext](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409)). The Horticultural Development Council says "around 60 percent of export volumes are harvested starting in August" ([HDC CEO via FreshFruitPortal](https://www.freshfruitportal.com/news/2026/06/15/zimbabwe-blueberry-boom/)). Zimbabwe's harvest peak is August to September. [inference] The benchmark peak for `zw-me-marondera` should move from Jul-Aug to Aug-Sep.
3. **Free station data sit next to three benchmark or IBO locations.**
   - The Western Cape Department of Agriculture portal ([WSP](https://gis.elsenburg.com/apps/wsp/)) has hourly and daily data. Its Veldreserwe station is about 2 km from the Steyn Hex River trial. It recorded -1.93 C on 29 August 2024, which matches IBO's "isolated unusual frost in late August to early September" 2024.
   - SASSCAL WeatherNet has a station at Mashare, Kavango East, running since February 2012 ([info sheet](https://www.sasscalweathernet.org/weatherstat_infosheet_we.php?loggerid_crit=31195)). Mashare is also the locality of Namibia's main blueberry project, where frost hit the crop in 2023.
   - Zimbabwe MSD dekadal bulletins tabulate Marondera minima ([bulletin](https://www.weatherzw.org.zw/products/dekadal-agromet-bulletin/)).
4. **Monthly trade-mirror series are the only harvest-timing evidence for the small producers.** Comext gives month-by-month EU arrivals for Zimbabwe, South Africa, Namibia, Zambia, Egypt and Kenya. Each reporter and partner pair is one API call. South Africa's EU arrivals peak in November and December. Namibia and Zambia peak in September and October. Egypt peaks in March to May.
5. **The best South African industry data are closed.** Berries ZA weekly export reports and the "top 10 planted varieties by province" report are members-only ([export reports](https://www.berriesza.co.za/market-access/export-reports/)). PPECB Intellex blocks visitors from the US ([PPECB](https://ppecb.com/)). Older public Berries ZA PDFs now return 404. A formal request is the only route.

## 2. Production context in brief

- **South Africa.** Production was 38,900 t in MY2025/26. Area peaked at 3,800 ha in MY2022/23 and fell to 2,650 ha in MY2025/26. The Western Cape grows about 60% of output, Limpopo 15%, Northern Cape 10% and Gauteng 8% ([GAIN 2026](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=South%20African%20Blueberry%20Market%20Analysis_Pretoria_South%20Africa%20-%20Republic%20of_SF2026-0027.pdf)). The Western Cape harvest peaks from September to January, with exports peaking in October and November. Limpopo and Mpumalanga harvest from May to September (same source). The Western Cape flyover census counted 465 ha of blueberries in 2013, 824 ha in 2017 and 1,762 ha in 2023 ([WCDoA mapping report](https://www.elsenburg.com/wp-content/uploads/2024/03/WCDoA-Mapping-of-Agricultural-Commodity-Final-Report-Part-1.pdf)). Commercial Western Cape blocks run as evergreen systems under 20% white net and are pruned in late November ([Steyn 2022](https://scholar.sun.ac.za/server/api/core/bitstreams/47824860-fa96-4626-b2b2-da6439d6a8f4/content)). In the floods of mid-May 2026, some growers below mountain catchments lost more than 70% of their volume. National export projections stayed near 25,000 t ([FreshFruitPortal, 31 Aug 2026](https://www.freshfruitportal.com/news/2026/08/31/sa-blueberry-weather/)).
- **Zimbabwe.** Blueberries are grown in Mashonaland East, West and Central ([HDC ZBGA page](https://hdczim.com/member-associations/zimbabwe-berry-growers-association-zbga/)). Exports were about 9,500 t in 2025, and the export season runs from April to October ([HDC CEO](https://www.freshfruitportal.com/news/2026/06/15/zimbabwe-blueberry-boom/)). The 2025 crop matured later than usual. The harvest runs from mid-March to the end of October, and shipments peak around September ([Zimbabwe Situation / The Herald](https://www.zimbabwesituation.com/news/zimbabwes-blueberry-exports-surge-as-shipments-to-china-expand/)).
- **Namibia.** The main project is Mashare in Kavango East: 60 ha, with an "extreme frost event" in 2023 and a 2024 export target of 700 t ([The Brief](https://thebrief.com.na/2024/07/mashare-blueberry-project-to-expand-production-by-30-hactares/)). A second project is planned at Divundu ([The Namibian](https://www.namibian.com.na/n15b-blueberry-project-planned-for-divundu/)).
- **Zambia, Kenya.** IBO lists Zambia at 100 ha and Kenya at 50 ha ([IBO, Nov 2025](https://www.internationalblueberry.org/2025/11/21/global-blueberry-market-2025-africas-rising-influence/)). Zambia's production is near Chisamba ([ZamBerries](https://zamberries.com/)). Kakuzi in Kenya produced 53,175 kg in 2024, up from 11,728 kg in 2023 ([Kakuzi AR 2024](https://www.kakuzi.co.ke/pages/0b7a1f81-99a7-4688-9c00-31138a9aa126/articles/0b7a1f81-99a7-4688-9c00-31138a9aa126.pdf)).
- **Tanzania.** No commercial blueberry farm was documented. Only an exporter sourcing page mentions small plots in Iringa, seen in search results only.
- **Egypt.** Production was 2,100 t in 2025. The window "starts in January and peaks in March" ([FreshPlaza, 7 Oct 2026](https://www.freshplaza.com/north-america/article/9880769/the-bet-for-egyptian-blueberries-is-to-develop-super-early-varieties/)). A 231 ha project is under way at Wadi El-Natrun ([FreshPlaza](https://www.freshplaza.com/europe/article/9800045/egypt-launches-large-scale-blueberry-production-in-wadi-el-natrun/)).
- **Tunisia.** Blueberries were 4% of summer fruit exports, with 751 t shipped to 20 destinations by early July 2026 ([La Presse](https://www.lapresse.tn/2026/07/09/fruits-les-exportations-tunisiennes-ont-rapporte-88-millions-de-dinars/)).

## 3. What the app already has for this scope

**Benchmark sites** (from `pipelines/weather/benchmark_sites.json` and the brief):

| Site | Published | Model result | Key gap |
|---|---|---|---|
| za-wc-george | deciduous SHB; bloom Jul-Aug; harvest Sep-Jan | Transitional, managed-cycle scan, 15 chill h; harvest precision 0.42 | Chill shortfall only; no station check |
| za-wc-wolseley | evergreen SHB; bloom Aug; harvest Aug-Nov | Deciduous in 100% of winters, 1,134 chill h; harvest predicted Dec-Jan (recall 0) | Town-centre coordinate; no pruning date; the 0.5 x 0.625 degree cell probably includes cold mountain terrain [inference] |
| za-lp-tzaneen | mixed; harvest May-Sep | Semi-evergreen; harvest precision 0.83 | No bloom months; elevation from a snippet only |
| zw-me-marondera | evergreen; harvest Apr-Oct; peak Jul-Aug | Semi-evergreen; harvest precision 1.0 | IBO versus GAIN peak conflict; no bloom or pruning months |

**IBO records in scope** (from `dist/evidence/ibo-regional-v1.json`): ZA has 2 records (`za-2024-late-winter`, `za-system`). ZA-LP has 1 (`za-limpopo-2024-frost`). ZA-NORTH has 2 (`za-north-2025-minor-frost`, `za-north-harvest`). ZA-WC has 2 (`za-wc-2024-weather`, `za-wc-harvest`). ZW has 4 (`zw-2022-late-rain`, `zw-2024-compressed`, `zw-2025-yield`, `zw-harvest`). NA-KAV has 1 (`na-kavango-frost`). KE has 1 (`ke-year-round`). There are no records for Zambia, Egypt, Tanzania or Tunisia. No IBO record covers the June 2023, September 2023 or May 2026 Western Cape floods.

**Known gaps** (from the `gaps` section of the registry): Steyn full text was not read. There are no Limpopo bloom months. Elevations come from snippets. Zimbabwe has no bloom, planting or pruning months. The Zimbabwe peaks conflict. The earlier research docs (`04_validation_data_and_protocol.md`, `07_weather_inputs_and_global_scaling.md`) contain no African station source. Their only African-relevant item is CHIRPS v2.

## 4. Source inventory

Priority P1 marks sources to use first. The full field lists are in the JSON.

### 4.1 Phenology, management and cultivar evidence

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [Steyn 2022 MSc thesis](https://scholar.sun.ac.za/server/api/core/bitstreams/47824860-fa96-4626-b2b2-da6439d6a8f4/content) | Dated 50% and 90% flowering and peak harvest by cultivar; pruning, hive and net details; site coordinates | Open; terms not found | en, af | 2020-2021 | opened | P1 |
| [SUNScholar: Swart 2015](https://scholar.sun.ac.za/items/0e481f6a-c00c-43de-af79-e17825f99886) | Dormex trial near George; budbreak and harvest dates | Open; terms not found | en | 2010s | opened | P2 |
| [Berries ZA varieties by province](https://www.berriesza.co.za/research-tech-hub/top-10-planted-varieties-in-sa/) | Top ten varieties by hectare per province | Members only | en | unknown | opened-limited | P2 |
| [Berries ZA ongoing research](https://www.berriesza.co.za/research-tech-hub/ongoing-research/) | Botrytis spore and weather project (due 2026), other pathogens | Open | en | 2024-2026 | opened | P2 |

### 4.2 Weather stations and gridded weather

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [WCDoA Weather Station Portal](https://gis.elsenburg.com/apps/wsp/) | 37 stations; hourly, daily and monthly temperature, humidity, rain, leaf wetness, radiation | Open; "not verified, own risk" | en | station-dependent | opened | P1 |
| [SASSCAL WeatherNet, Mashare](https://www.sasscalweathernet.org/weatherstat_infosheet_we.php?loggerid_crit=31195) | Hourly, daily and monthly temperature (min/avg/max), humidity, leaf wetness; CSV | Open; terms not found | en | 2012-present | opened | P1 |
| [Zimbabwe MSD Dekadal Agromet Bulletin](https://www.weatherzw.org.zw/products/dekadal-agromet-bulletin/) | Station Gmin, Tmin, Tmax, RH, 10-day rain; frost places | Open; terms not found | en | 2024-2026 online | opened | P1 |
| [SAWS](https://www.weathersa.co.za/) | Station data; monthly Climate Summary | Paid or free by product | en | 2006-2025 summaries | opened-limited | P2 |
| [ARC agro-climate portal](https://www.agroclimate.agric.za/WP/WP/About.php) | Hourly AWS network across South Africa | Paid (per search) | en | long | opened-limited | P2 |
| [KMD agromet and Map Room](https://meteo.go.ke/Services/climate-data-management/) | Dekadal bulletins, ENACTS maps | Open | en, sw | ENACTS | opened | P3 |
| [TAHMO](https://tahmo.org/climate-data/) | Station CSV via portal | Free research access, no sharing | en | station-dependent | opened | P3 |
| [Zambia Met Dept](https://www.zmd.gov.zm/) | Bulletins | Open | en | unknown | opened | P3 |
| [TMA](https://www.meteo.go.tz/) and [TAHA](https://www.taha.or.tz/) | No blueberry content | Open | sw, en | n/a | opened | P3 |
| [CHIRPS v3](https://www.chc.ucsb.edu/data/chirps3) | Daily rain, 0.05 degree | Public domain (CC registration), CC BY 4.0 | en | 1981-present | opened | P2 |
| [ENACTS](https://iri.columbia.edu/resources/enacts/) | National merged grids | Open | en | country-dependent | opened | P3 |
| [FEWS NET](https://fews.net/) | Food-security data | Free login | en | varies | opened | P3 |

### 4.3 Trade, shipment and production series

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [Eurostat Comext DS-045409](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409) | Monthly EU imports, CN 08104050, by partner | Reuse with source acknowledgement | en | 1988-present | opened | P1 |
| [SARS trade data wizard](https://tools.sars.gov.za/tradestatsportal/data_download.aspx) | Monthly exports and imports by tariff and country | Open; terms not found | en | 2010-2026 | opened | P1 |
| [USDA GAIN South Africa](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=South%20African%20Blueberry%20Market%20Analysis_Pretoria_South%20Africa%20-%20Republic%20of_SF2026-0027.pdf) | Area, production, trade, regional windows | Open US federal report | en | 2014/15-2025/26 | opened | P1 |
| [HMRC OTS API](https://api.uktradeinfo.com/) | Monthly UK imports by CN8 and country | OGL v3.0 | en | 2022+ checked | opened | P2 |
| [UN Comtrade preview](https://comtradeplus.un.org/) | Monthly HS 081040 by reporter and partner | Terms not found | en | varies | opened | P2 |
| [PPECB annual reports](https://annualreports.ppecb.com/2324/part-3-departmental-reports/operations-report/) | Blueberry cartons inspected per year | Reproduction needs permission | en | 2023/24+ | opened | P3 |
| [PPECB Intellex](https://ppecb.com/) | Inspection data | Geo-blocked; registration | en | unknown | opened-limited | P2 |
| [Berries ZA export reports](https://www.berriesza.co.za/market-access/export-reports/) | Shipment volumes, destinations | Members only | en | unknown | opened-limited | P2 |
| [DALRRD Abstract 2025](https://www.nda.gov.za/index.php/publication/332-statistical-abstract) | "Other berries" (blueberries not listed) | Open | en | 1995-2024 | opened | P3 |
| [Kakuzi annual reports](https://www.kakuzi.co.ke/pages/0b7a1f81-99a7-4688-9c00-31138a9aa126/articles/0b7a1f81-99a7-4688-9c00-31138a9aa126.pdf) | Kenyan blueberry kg per year | Open | en | 2019-2025 | opened | P2 |
| [ZimTrade](https://www.zimtrade.co.zw/) | No series found | Open | en | n/a | opened | P3 |
| [ZIMSTAT](https://www.zimstat.co.zw/) | Unknown | Timed out | en | unknown | opened-limited | P3 |
| [NAB horticulture statistics](https://www.nab.com.na/horticulture/horticulture-statistics/) | Grapes and vegetables to 2018/19; no blueberries | Open | en | 2010-2019 | opened | P3 |
| [Namibia Statistics Agency](https://www.nsa.org.na/) | Homepage only | Open | en | unknown | opened | P3 |
| [AFA Kenya HCD](https://afa.go.ke/resources-afa-year-book-of-statistics/) | Yearbooks | Timed out | en | unknown | opened-limited | P3 |
| [CAPMAS Egypt](https://www.capmas.gov.eg/) | JS shell | Not readable | ar | unknown | opened-limited | P3 |
| [GIFruits Tunisia](https://www.gifruits.com/) | Summer fruit export statistics menu | Open | fr | unknown | opened | P3 |

### 4.4 Land use and orchard location

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [CapeFarmMapper 3](https://gis.elsenburg.com/apps/cfm/) | Crops 2023, 2017/18, 2013/14 layers with zonal statistics | Open; accuracy disclaimer | en | 3 censuses | opened | P2 |
| [WCDoA commodity mapping 2023](https://www.elsenburg.com/wp-content/uploads/2024/03/WCDoA-Mapping-of-Agricultural-Commodity-Final-Report-Part-1.pdf) | Blueberry hectares 2013, 2017, 2023 | Open | en | 2013-2023 | opened | P2 |
| [HDC ZBGA page](https://hdczim.com/member-associations/zimbabwe-berry-growers-association-zbga/) | Growing provinces in Zimbabwe | Open | en | current | opened | P2 |
| [ZamBerries](https://zamberries.com/) | Chisamba farm | Open | en | 2017+ | opened | P3 |

### 4.5 Damage, disasters and insurance

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [WCDoA media releases](https://www.elsenburg.com/damage-to-western-cape-agriculture-infrastructure-estimated-at-r1-053-billion/) | Dated flood damage by category and district | Open | en | 2021+ | opened | P2 |
| [NDMC](https://www.ndmc.gov.za/) / [COGTA notice](https://www.cogta.gov.za/index.php/2026/05/10/the-classification-of-the-recent-severe-weather-events-as-a-national-disaster/) | Disaster classifications | Open; TLS error on COGTA | en | 2002+ | opened-limited | P3 |
| [Landbou.com](https://www.landbou.com/weer/kaapse-storms-lei-tot-sterftes-ontwrigting-en-reuse-skade-20260513-1197) | Afrikaans farm-level flood reports (Belblu near Wolseley) | Open; some paywall | af | 2017+ | opened | P2 |
| [Namibian press on Mashare](https://thebrief.com.na/2024/07/mashare-blueberry-project-to-expand-production-by-30-hactares/) | 2023 frost effect on exports | Open | en | 2023-2026 | opened | P2 |
| [Santam crop insurance](https://www.santam.co.za/products/agriculture/crop-insurance/) | Product pages only | No open loss data | en | n/a | search-only | P3 |

### 4.6 Narrative and industry reports for the RAG library

| Source | Contains | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [HDC CEO opinion (IBO, June 2026)](https://www.freshfruitportal.com/news/2026/06/15/zimbabwe-blueberry-boom/) | Season months, share from August, 2025 late season | Open | en | 2024-2026 | opened | P1 |
| [IBO website news, Africa items](https://www.internationalblueberry.org/2025/11/21/global-blueberry-market-2025-africas-rising-influence/) | Country hectares; May 2026 flood impacts | Open | en | 2025-2026 | opened | P2 |
| [FreshPlaza Egypt](https://www.freshplaza.com/north-america/article/9880769/the-bet-for-egyptian-blueberries-is-to-develop-super-early-varieties/) | Season window and volumes | Open | en | 2024-2026 | opened | P2 |
| [Economy Plus (Arabic)](https://economyplusme.com/185213/) | Egyptian export figures and FOB prices | Open | ar | 2025-2026 | opened | P3 |
| [Zimbabwe Situation / Herald](https://www.zimbabwesituation.com/news/zimbabwes-blueberry-exports-surge-as-shipments-to-china-expand/) | H1 2026 exports; September shipment peak | Open | en | 2025-2026 | opened | P3 |
| [Italian Berry IBO 2024 summary](https://italianberry.it/en/news/zimbabwe-namibia-zambia-africa-blueberries) | 2024 edition text on Zimbabwe, Namibia, Zambia | Open | en | 2024 ed. | opened | P3 |
| [Fruit SA](https://fruitsa.co.za/) | Umbrella body; no statistics | Open | en | n/a | opened | P3 |

### 4.7 Top 10 sources: what the sample showed

1. **Steyn 2022 thesis.** Table 1 lists "50% flowering 7 July / 9 July / 21 July / 6 July" for 8-42 and 9-02 in 2020 and 2021. It gives "90% of flowering 1 September / 31 August / 14 September / 2 September" and "Peak harvest 26 October / 25 October / 9 November / 27 October". Methods give Hex River at 33 37' 01" S, 19 29' 31" E, 263 m, and Wolseley at 33 29' 06" S, 19 10' 00" E, 248 m. Beehives were in place from 11 May to 7 September 2020. Pruning was "during the last week of November". The text names an iLeaf (Hortec) automatic station as the hourly temperature source.
2. **WCDoA Weather Station Portal.** `getstations.php` returned `station_id, station_name, latitude, longitude, altitude` for 37 stations. One `getdaily.php` call for Veldreserwe returned `LogDate, AvgTemp, MinTemp, MaxTemp, Radiation, Windspeed, Rainfall, Humidity, PenmanEto, LeafWetness, SHrs`. MinTemp was -1.93 on 2024-08-29 and 1.40 on 2024-08-28. The hourly table headers are `Date, Time, Type, Temp, Rainfall, Humidity, Wind Spd, Wind Dir, Radiation, ETO, Sun Hours`.
3. **SASSCAL Mashare.** The info sheet gives latitude -17.8976, longitude 20.2123, altitude 1065 m, first data 17 Feb 2012, and a relocation on 4 Mar 2018. The daily table columns are air temp avg/min/max, precip, wind, surface temp, humidity, pressure, solar irradiance and leaf wetness, with a per-month CSV download.
4. **Zimbabwe MSD bulletin, 11-20 June 2026.** The PDF table has columns Province, Station, Clouds, Gmin, Min/Max Temp, RH range, rain in 10 days, wind, evaporation and sunshine. The Marondera row reads Gmin E, Min 0, Max 24, RH 18-100, rain 000. The narrative lists frost at Chivhu (Mashonaland East), among other places.
5. **Eurostat Comext.** JSON returns monthly `QUANTITY_IN_100KG` per partner. Zimbabwe 2025: Jul 79 t, Aug 192 t, Sep 1,046 t, Oct 1,625 t, Nov 681 t. South Africa 2025: Sep 850 t, Oct 2,201 t, Nov 4,456 t, Dec 3,870 t. Egypt 2026: Mar 571 t, Apr 1,348 t, May 835 t. Namibia 2025: Sep 104 t, Oct 146 t.
6. **SARS wizard.** It offers fields `TradeType, YearMonth, Tariff, CountryOfDestinationName, CountryOfOriginName, StatisticalQuantity, CustomsValue, TransportCode, DistrictOfficeName` for 2010-2026. No query was run.
7. **GAIN SF2026-0027.** Figures 1 to 6 give area, production, exports and market shares by marketing year. Section 4.1 holds the Zimbabwe June/July sentence.
8. **UN Comtrade preview.** South Africa (reporter 710) imports from Zimbabwe (716), HS 081040: `netWgt` 129,651 kg in 2024-06, 46,284 kg in 2024-08 and 13,016 kg in 2024-10.
9. **HMRC OTS.** UK imports from Zimbabwe (CountryId 382, CommodityId 8104050) give `NetMass` by `MonthId`: 2024-08 40.2 t, 2024-09 89.6 t, 2024-10 70.5 t.
10. **HDC CEO opinion.** It states "export season typically runs from April through October, and around 60 percent of export volumes are harvested starting in August". It also says the 2025 season "matured slightly later than usual" and growers expect "a return to earlier production timing, similar to the 2024 season".

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON.

| Job | Sources | Output | Exact fields | Pri |
|---|---|---|---|---|
| AF-01 Steyn stage table | za-steyn-2022-msc-thesis, za-sunscholar-blueberry-theses | cultivar table | site_id, lat, lon, elevation_m, cultivar, season, stage (50% flowering, 90% flowering, first harvest, peak harvest, pruning, hives in/out), date, precision, protection, system, citation (pdf page, table) | P1 |
| AF-02 WCDoA stations | za-wcdoa-weather-station-portal | station table | station_id, name, lat, lon, altitude, timestamp, AvgTemp, MinTemp, MaxTemp, Humidity, Rainfall, LeafWetness, Radiation, Windspeed, PenmanEto, SHrs, qc_flag | P1 |
| AF-03 SASSCAL Kavango | na-sasscal-weathernet-mashare, na-business-press | station table, plus event records | station_id, date, hour, air_temp_min/avg/max, humidity_avg, precip_total, leaf_wetness_avg, surface_temp_avg; frost-night events linked to `na-kavango-frost-2023-2024` | P1 |
| AF-04 MSD bulletins | zw-msd-dekadal-agromet | station table | dekad_start, dekad_end, province, station, Gmin, Tmin, Tmax, RH_min, RH_max, rain_10day_mm, sunshine_h, frost_places | P1 |
| AF-05 Trade mirrors | eu-eurostat-comext-ds045409, uk-hmrc-ots-api, un-comtrade-preview-api, za-sars-trade-stats | time series table | origin, reporter, flow, product_code, period, net_mass_t, value; derived peak_month, monthly share, season start | P1 |
| AF-06 Africa evidence library | GAIN, HDC opinion, IBO news, WCDoA releases, Landbou, Namibian press, Kakuzi, FreshPlaza Egypt, Herald, Arabic press, Berries ZA research, Italian Berry | claim and event records | IBO schema: id, kind, topic, title, summary, geography_ids, period {label, start, end, precision}, crop_context, evidence_type, citations {source_id, page or URL, locator}, limitations, event_id | P2 |
| AF-07 Location layer | CFM crops, WCDoA mapping, HDC ZBGA, ZamBerries | area table | region, census_year, crop, hectares, source, centroid or polygon | P2 |
| AF-08 Access requests | Berries ZA, PPECB Intellex, SAWS, ARC | request log | target, contact, dataset, fields, cost, terms, decision | P2 |

Suggested new event records for AF-06, each to be checked by a reviewer before use:

- `za-wc-2023-06-floods`: WCDoA rapid assessment, 26 to 30 June 2023; crop losses R278 million ([release](https://www.elsenburg.com/damage-to-western-cape-agriculture-infrastructure-estimated-at-r1-053-billion/)).
- `za-wc-2026-05-floods`: from 4 May 2026; 300 to 400 mm in two to three days on some farms; some growers lost more than 70% of volume; Belblu near Wolseley flooded ([FreshFruitPortal](https://www.freshfruitportal.com/news/2026/08/31/sa-blueberry-weather/), [Landbou](https://www.landbou.com/weer/kaapse-storms-lei-tot-sterftes-ontwrigting-en-reuse-skade-20260513-1197)).
- `zw-2025-late-season`: the 2025 crop matured later than usual and overlapped with Peru and the Western Cape ([HDC CEO](https://www.freshfruitportal.com/news/2026/06/15/zimbabwe-blueberry-boom/)).
- `za-wc-2024-08-frost-station`: Veldreserwe minimum of -1.93 C on 29 Aug 2024, a measured companion to the IBO record `za-wc-2024-weather`.

## 6. How each source maps to model checks

- **Evergreen management (Wolseley, Hex River).** Use the Steyn dates as a managed cycle: prune in the last week of November, reach 50% flowering in early July, peak harvest in late October. Test whether the scan can reproduce about 110 days from 50% flowering to peak harvest (7 Jul to 26 Oct 2020). Then compare GDD over that span using WCDoA station temperatures against MERRA-2 [inference]. This replaces the current Wolseley chill_clock result, which predicts a Dec-Jan harvest.
- **Grid representativeness at Wolseley.** The model gives 1,134 chill hours, but the thesis gives a July mean minimum of 9.8 C at Wolseley. [inference] The cell likely mixes valley floor and mountains. Pull Veldreserwe and Elsenburg hours below 7.2 C for 2010 to 2025 and compare them with the cell's chill count.
- **Frost detection and Tmin bias.** Compare MERRA-2 and POWER Tmin with Veldreserwe (Hex River), George PP (George), Mashare (Kavango) and Marondera (MSD). Use the dated cold nights (29 Aug 2024 Western Cape; 2023 and 2024 Kavango winters; June 2026 Zimbabwe ground frost) to test whether the grid misses them, like the Chile and Waikato cases.
- **Harvest timing and year shifts.** Turn Comext and HMRC monthly arrivals into a peak month per origin and year. Subtract a shipping lag and compare with modelled harvest windows. For example, Zimbabwe 2024 (arrivals peak in October) can be checked against the IBO statement that the harvest peak fell in weeks 37 to 40. The HDC statement that 2025 was late and 2024 early is a direct check of modelled year-to-year shifts.
- **Zimbabwe peak.** Set the `zw-me-marondera` peak to Aug-Sep [inference]. Keep the GAIN sentence as an import-timing claim, not a harvest claim.
- **Harvest heavy rain and floods.** Use the WCDoA damage releases and NDMC classifications as dated labels. Count CHIRPS v3 heavy-rain days in the same windows for the Wolseley and Hex River cells.
- **Disease indices.** Use WCDoA and SASSCAL leaf wetness and humidity to check the hourly Botrytis and anthracnose infection hours. Follow the Berries ZA Botrytis spore project for future validation data.
- **Location mapping.** Use CFM crop layers and the census hectares to choose Western Cape cells. Use the HDC province list to widen the Zimbabwe polygon. Add Mashare and Chisamba as points.
- **Pollination.** The Steyn hive dates (11 May to 7 Sep 2020) give a managed pollination window to compare with the honey-bee flight-hour metric.

## 7. Access, licensing and language risks

- Berries ZA content is members-only. PPECB Intellex is geo-blocked and forbids redistribution. SAWS and ARC station data are mostly paid. TAHMO research data cannot be shared.
- The WCDoA portal states that its data are unverified and that only SAWS data are official. Ask before republishing raw series.
- SASSCAL, the Zimbabwe MSD, SUNScholar, SARS and UN Comtrade terms were not found. Treat them as citation-only until confirmed. Eurostat (acknowledge the source) and HMRC (OGL v3.0) allow reuse with attribution. CHIRPS v3 is public domain under CC registration and CC BY 4.0.
- Several government sites failed TLS checks (nda.gov.za, cogta.gov.za, sasscalweathernet.org). They opened only with certificate checking off. A production pipeline must handle this safely.
- Trade codes: CN 0810 40 50 and HS 0810 40 include cranberries and other Vaccinium. Arrival month is not harvest month.
- Language: Afrikaans news (Landbou) holds farm-level detail, and Netwerk24 is paywalled. In Arabic, "التوت" can mean any berry or mulberry; the Youm7 export story covers raspberries and blackberries. Only "التوت الأزرق" means blueberry. Tunisian sources are in French ("myrtille").
- Independence: the IBO website, the HDC opinion piece and Italian Berry share the IBO author network. Do not count them as independent confirmations.

## 8. Gaps

- No open weekly South African export or inspection series. Berries ZA and PPECB Intellex are closed.
- No Limpopo or Mpumalanga bloom, pruning or harvest-date observations. There is no free station network for the northern provinces. ARC and SAWS are paid. I found no Limpopo provincial calendar.
- The Steyn Scientia Horticulturae 2023 full text is still blocked. The thesis covers its content.
- Zimbabwe has no bloom, planting or pruning months, and no Zimbabwe ENACTS maproom was found. ZIMSTAT timed out. ZimTrade has no blueberry series online.
- Hail: only the IBO 2024 mention of week 43 of 2023 for Zimbabwe. No open hail or loss records exist for any country. Santam publishes no loss data.
- Kenya: AFA timed out. The lead domain `horticulture.agricultureauthority.go.ke` does not resolve. Kenyan data come only from Kakuzi.
- Namibia: the NAB statistics stop in 2018/19 and have no blueberry rows. No Namibian Meteorological Service site was reachable (meteona.com shows a default page).
- Tanzania: no commercial blueberry industry was documented.
- Egypt: I found no official weekly export statement from the Ministry of Agriculture or the plant quarantine service. CAPMAS is a JS shell. Comext is the best Egyptian timing source.
- The 2019 Berries ZA economic report PDF now returns 404.

## 9. Ranked top 10 actions

1. Run AF-01: enter the Steyn dated stages, pruning date and trial coordinates. Add Hex River and Wolseley trial sites to the benchmark.
2. Run AF-05 for Zimbabwe and update `zw-me-marondera` peak months to Aug-Sep, with the GAIN sentence recorded as an import-timing claim.
3. Run AF-02: pull WCDoA daily and hourly data for Veldreserwe, George PP and Elsenburg. Compute Tmin bias, chill hours and frost nights against the grid cells.
4. Run AF-03: pull SASSCAL Mashare and Bagani data to date the 2023 and 2024 Kavango frosts and test the grid.
5. Run AF-04: parse the MSD bulletins for Marondera, Wedza and Mutoko minima and the frost narratives.
6. Extend AF-05 to South Africa, Namibia, Zambia and Egypt. Store the monthly arrival curves as a market-timing table.
7. Add the new event records from AF-06 (June 2023 and May 2026 floods, the 2025 late Zimbabwe season, the station-confirmed August 2024 frost).
8. Re-run the Wolseley cell diagnosis: compare station chill hours with the cell's 1,134 hours and decide whether to move the site or flag the cell.
9. Ask Berries ZA (AF-08) for the weekly export reports and the variety-by-province table under a research agreement.
10. Test whether CapeFarmMapper Crops 2023 can export blueberry polygons (AF-07). If so, weight the Western Cape results by blueberry area.
