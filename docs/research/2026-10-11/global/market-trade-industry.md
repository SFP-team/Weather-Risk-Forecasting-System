# Global production, trade, market and industry-intelligence sources for blueberries

Slug: `market-trade-industry`. Checked on 2026-10-11. Companion file: [`market-trade-industry.sources.json`](market-trade-industry.sources.json) (64 sources, 10 extraction jobs).

## 1. Scope and summary

This report covers multi-country systems: FAOSTAT and Eurostat production tables, customs trade systems (UN Comtrade, WITS, BACI, Eurostat Comext, US Census, UK HMRC, China Customs, ITC Trade Map), national tariff books for the US, EU, UK, Chile, Peru, Mexico and China, USDA FAS GAIN, USDA ERS and USDA AMS Market News, the International Blueberry Organization (IBO), commercial intelligence (Agronometrics, Rabobank and others), twelve trade-press sites, four listed companies and five breeder catalogues. National statistics are listed only as pointers; the region teams own them.

I opened every URL in the JSON file. 54 sources are `opened` and 10 are `opened-limited` (bot walls, login walls, JavaScript-only pages or missing API keys). Where a fact came only from a search snippet, the text says so.

The five most useful findings:

1. **Only three of the seven tariff systems checked separate blueberries from other Vaccinium fruit.** The US HTS (0810.40.00.24 wild, .26 and .29 cultivated), the Chilean tariff (0810.4021 and 0810.4029 "Arándanos azules o blueberry") and the Mexican NICO table (0810.40.01 NICO 01 and 91 "Arándanos azules (Vaccinium corymbosum)") do. The EU and UK line 0810 40 50 combines highbush blueberry with American cranberry. Peru has a single line for all Vaccinium. China moved to a single 10-digit code in 2022, and only its 13-digit inspection suffix names blueberries. The consequence is simple: monthly trade data can time the harvest for origins that export almost nothing but blueberries (Peru, Chile, Mexico, Morocco, South Africa, Argentina, Zimbabwe, Colombia), even at HS6. For US and Canadian origins, only US import data at HTS10 level or AMS movement data can do it (section 4.3).
2. **USDA AMS has a free weekly series of blueberry shipments by origin, and sometimes by variety, from November 2017 to April 2025.** The report (WA_FV408, slug 3251) was paused on 1 May 2025. Its data continue in MyMarketNews, which needs a free API key, and in the daily movement report. The import rows are dated by US customs entry summaries, which can be filed up to ten business days after release ([daily movement report](https://www.ams.usda.gov/mnreports/fvddaily_move.pdf)). This is the best open weekly proxy for harvest start, peak and end in eight US states (California split into two regions) and six or more import origins.
3. **Eurostat Comext gives monthly EU imports by origin from 2000 without a key.** A worked example with Dutch imports from Peru (section 6.2) shows the 10 percent arrival date moving from mid- or late September in 2019 to 2022 to 6 October in 2024/25. That fits industry reports that pruning was delayed in 2024 [inference]. The same example shows the volume drop in 2023/24 that companies attribute to El Niño ([Hortifrut reasoned analysis, March 2024](https://investor.hortifrut.com/wp-content/uploads/2024/04/07.-Analisis-Razonado-HF-Mar24_English.pdf)).
4. **Most trade press cannot be used as a stored RAG corpus.** FreshPlaza and Hortidaily state `Content-Signal: ai-input=no` in robots.txt and block ClaudeBot, GPTBot and CCBot ([robots.txt](https://www.freshplaza.com/robots.txt)). Fruitnet, Portal Frutícola, Blueberries Consulting, Farm Journal (The Packer) and Great American Media Services (Fruit Growers News) forbid reproduction in their terms. FreshFruitPortal and Portal Frutícola are also deleting old articles: some now return HTTP 410 Gone. The workable design is a link-and-metadata index plus records that people write themselves, with a citation to each article.
5. **USDA FAS GAIN holds about 25 blueberry- or berry-related reports from 2005 to August 2026.** They cover Peru, Mexico, Chile, China, Canada, South Africa, Spain, Argentina, Morocco, Poland and Germany. They are US federal works, so they are not under copyright, and they include season months and dated weather impacts. They are the cleanest addition to the regional evidence library. The IBO 2021 and 2024 editions remain behind a registration form, but the 2025 IBO Summit presentations are open PDFs.

## 2. Production context in brief

- Peru is the largest exporter. In 2023 it exported 206,579 t of HS 081040, worth US$1.67 billion ([WITS](https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2023/tradeflow/Exports/partner/WLD/product/081040)). In January 2025 alone it exported 23,585 t, of which 13,946 t went to the US and 5,887 t to the Netherlands ([UN Comtrade preview API](https://comtradeapi.un.org/public/v1/preview/C/M/HS?reporterCode=604&period=202501&cmdCode=081040&flowCode=X)). Mission Produce says the Peruvian harvest "typically runs from July through January" ([Form 10-K FY2025](https://www.sec.gov/Archives/edgar/data/1802974/000180297425000048/avo-20251031.htm)). FAS uses a May-to-April marketing year ([GAIN PE2025-0010](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf)).
- Chile exported 82,491 t in 2023 ([WITS](https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2023/tradeflow/Exports/partner/WLD/product/081040)). "The bulk of blueberry production in Chile starts in November and lasts until March" ([GAIN CI2022-0030](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual+Voluntary_Santiago_Chile_CI2022-0030.pdf)).
- Mexico: FAS lists the top producing states for 2025 and reports that producers "deliberately shift their harvest season" ([GAIN MX2026-0015](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Berry+Annual+Voluntary_Guadalajara_Mexico_MX2026-0015.pdf)).
- China passed the US as the largest producer in 2021. Blueberries are grown in 26 of its 34 provinces under greenhouse, open-field and mixed systems; Guizhou, Liaoning, Shandong, Sichuan and Yunnan are the main areas ([GAIN CH2023-0046](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual+Voluntary+2023_Beijing+ATO_China+-+People%27s+Republic+of_CH2023-0046.pdf)).
- Europe: in 2025, Poland had 12.6 thousand ha of blueberries, Spain 5.14 thousand ha (70.7 thousand t) and Germany 3.45 thousand ha (17.3 thousand t) ([Eurostat apro_cpsh1, crop F3300](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1?format=JSON&lang=en&crops=F3300&geo=PL&geo=ES&geo=PT&geo=DE&sinceTimePeriod=2019)).
- Southern Africa: South Africa exported about 21,000 t from the 2024 crop. Its March-to-June production runs mainly in the north ([Fruitnet, May 2025](https://www.fruitnet.com/eurofruit/new-variety-boosts-south-africas-early-season-blueberry-business/266599.article)). An IBO Summit deck gives 22,600 t for 2024/25, shipped 60 percent by sea and 40 percent by air ([van Dyk, IBO Summit 2025](https://www.internationalblueberry.org/wp-content/uploads/2025/10/12.20-Herman-van-Dyk-Insights-into-the-South-African-Blueberry-Industry.pdf)).
- United States: ERS has state-level area, yield, production and fresh and processed prices from 1980 to 2024 ([ERS Table D-2](https://www.ers.usda.gov/data-products/fruit-and-tree-nuts-data/fruit-and-tree-nuts-yearbook-tables)). AMS reports shipments from California (central and south), Florida, Georgia, Michigan, New Jersey, North Carolina, Oregon and Washington ([daily movement](https://www.ams.usda.gov/mnreports/fvddaily_move.pdf)).
- Evergreen and managed systems in Morocco (Kenitra, Larache) and Yunnan are run by multinational growers such as Costa ([Costa Sustainability Report 2023](https://costagroup.com.au/wp-content/uploads/2025/01/J231050-Costa-Group-SR-2023-FA_online.pdf)).

## 3. What the app already has for this scope

- **Benchmark** (`pipelines/weather/benchmark_sites.json`): 53 sites in 17 countries (US 17, CL 5, BR 4, PE 3, MX 3, AR 3, ZA 3, CN 3, PT 2, MA 2, AU 2, others 1 each). Market and industry sources already cited:
  - 19 USDA FAS GAIN PDF links across 16 sites (all Chilean, Peruvian, Mexican, South African and Zimbabwean sites, plus Moguer);
  - FreshPlaza (.com 3, .es 3, .de 1), Hortidaily (.com 3, .es 1), FreshFruitPortal 2, Fruitnet 2, Blueberries Consulting 2, Agraria.pe 1 and one IBO news post (Mengzi, Yunnan).
  - The FreshPlaza and Hortidaily citations are fine as human-read references. Their text must not be fed into an AI pipeline (section 7).
- **Regional evidence** (`dist/evidence/ibo-regional-v1.json`): 91 records (39 events, 42 practice, 10 constraints) from the IBO 2023, 2025 and 2026 reports.
  - The inventory (`docs/research/2026-10-05/ibo_report_inventory.json`) lists the 2021 and 2024 editions as form-gated or excerpt-only, 2014, 2016 and 2019 as member or paid access, and 2020 as an Americas special edition that is no longer available.
- **Earlier research:**
  - `docs/research/2026-09-21/04_validation_data_and_protocol.md` proposed AMS WA_FV408 shipments as a 10/50/90 percent harvest-progress curve (archive depth then "unverified, likely ≥2010").
  - `docs/weather/GLOBAL_PHENOLOGY_REVIEW.md` (S43) recorded that the report was paused in May 2025 and warned that shipments cannot serve as flowering labels.
  - This report measures the archive (November 2017 to April 2025 in MyMarketNews, November 2018 to April 2025 on ESMIS) and adds the monthly customs systems.
- **Known gaps this scope can help with:**
  - coastal Peru flowering-to-harvest interval and 2024 pruning shift;
  - evergreen timing in Morocco, Huelva, Yunnan and Wolseley;
  - northern highbush harvest in Washington, British Columbia and Michigan;
  - the November 2022 Chile freeze;
  - the lack of year-specific harvest dates and loss data.
- **What the repository does not have:** no market or trade time series and no cultivar catalogue table from licensors.

## 4. Source inventory

Status codes: **O** = opened, **OL** = opened-limited, **SO** = search-only. Full fields are in the JSON.

### 4.1 Production and area

| Source | Contains | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [FAOSTAT QCL, item 552 Blueberries](https://www.fao.org/faostat/en/#data/QCL) | Area harvested, production, yield by country | Open bulk CSV zip (33 MB); API now needs a free account and JWT (401 without). [CC BY 4.0 plus FAO terms](https://www.fao.org/contact-us/terms/db-terms-of-use/en/) | multi | span not measured (bulk file over sample limit); blueberry rows vary by country | O | P2 |
| [FAOSTAT TM trade matrix](https://www.fao.org/faostat/en/#data/TM) | Annual bilateral trade | Open bulk (411 MB), CC BY 4.0 | en | annual | O | P3 |
| [Eurostat apro_cpsh1, F3300 Blueberries](https://ec.europa.eu/eurostat/web/agriculture/database) | Area (thousand ha), harvested production, yield by member state | Open keyless API; [Eurostat reuse notice](https://ec.europa.eu/eurostat/web/main/help/copyright-notice) | en/fr/de | 2019-2025 tested | O | P2 |
| [USDA ERS Fruit and Tree Nuts Yearbook, D-2](https://www.ers.usda.gov/data-products/fruit-and-tree-nuts-data/fruit-and-tree-nuts-yearbook-tables) | State area, yield, production, fresh and processed price | Open xlsx/csv; US federal work | en | 1980-2024 | O | P2 |

### 4.2 Trade flows (customs systems)

| Source | Contains | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [UN Comtrade](https://comtradeplus.un.org/) | Monthly and annual HS6 by reporter, partner, mode; netWgt, value | Keyless preview API worked; free account gives 100K records per call and 500 calls per day ([subscriptions](https://uncomtrade.org/docs/subscriptions/)); [re-dissemination rules](https://uncomtrade.org/docs/re-dissemination-of-data/) | en | monthly per reporter | O | P1 |
| [Eurostat Comext DS-045409](https://ec.europa.eu/eurostat/web/international-trade-in-goods/database) | Monthly CN8 by EU reporter and partner, 100 kg and EUR | Keyless JSON API; Eurostat reuse notice | en/fr/de | 2000 onward tested (label "since 1988") | O | P1 |
| [US Census International Trade API](https://www.census.gov/data/developers/data-sets/international-trade.html) | Monthly HS10 imports by country and customs district | Free API key needed ("Missing Key" without); US federal work; [API ToS](https://www.census.gov/data/developers/about/terms-of-service.html) | en | 2010 to present | OL | P1 |
| [HMRC uktradeinfo OTS API](https://www.uktradeinfo.com/) | Monthly CN8 by country and port | Keyless OData; Open Government Licence v3.0 | en | Jan 2025 tested | O | P2 |
| [WITS](https://wits.worldbank.org/trade/comtrade/en/country/ALL/year/2023/tradeflow/Exports/partner/WLD/product/081040) | Annual HS6 rankings | Open; terms not found | en/es | annual | O | P3 |
| [CEPII BACI](https://www.cepii.fr/CEPII/en/bdd_modele/bdd_modele_item.asp?id=37) | Reconciled annual HS6 flows | Licence: Etalab 2.0 | en | 1995-2024 | O | P3 |
| [OEC](https://oec.world/en/profile/hs/cranberries-blueberries-and-other-fruits-of-the-genus-vaccinium) | Product profile | JavaScript shell; terms not found | en | n/a | OL | P3 |
| [ITC Trade Map](https://www.trademap.org/) | National lines, monthly for 100+ countries (search snippets) | Free registration; fees for some users (search-only) | en/es/fr | monthly | OL | P3 |
| [USA Trade Online](https://usatrade.census.gov/) | Port-level HS10 | Login | en | n/a | OL | P3 |
| [USDA FAS GATS](https://apps.fas.usda.gov/gats/default.aspx) | HS10 queries over Census data | Browser-detection page only | en | n/a | OL | P3 |
| [China Customs statistics platform](http://stats.customs.gov.cn/) | Monthly imports by code and partner | HTTP 412 anti-bot challenge | zh | n/a | OL | P3 |

### 4.3 Tariff lines that separate blueberries from other Vaccinium fruit

| Jurisdiction | Fresh lines | Frozen and dried | Blueberries separable? | Evidence |
|---|---|---|---|---|
| US (HTS 2026) | 0810.40.00 > "Blueberries:" .24 Wild; "Cultivated (including highbush):" .26 Certified organic, .29 Other; .30 Cranberries; .40 Other | 0811.90.20 Blueberries: wild .25/.27, cultivated .30/.40; dried 0813.40.20.10 wild, .20 cultivated | Yes, and wild separate from cultivated (imports) | [USITC exportList](https://hts.usitc.gov/reststop/exportList?from=0810.40&to=0811.90.30&format=JSON&styles=false) |
| EU CN8 | 0810 40 10 V. vitis-idaea; 0810 40 30 V. myrtillus (bilberry); **0810 40 50 "V. macrocarpum and V. corymbosum"**; 0810 40 90 other Vaccinium | 0811 90 50 V. myrtillus; 0811 90 70 V. myrtilloides and V. angustifolium (wild lowbush); frozen highbush has no own line and falls in 0811 90 95 "other" (it is not excluded there) | Partly: 0810 40 50 mixes highbush with American cranberry. Lowbush and rabbiteye, strictly by species, fall in 0810 40 90 [inference from labels] | [Comext labels via API](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409?format=JSON&lang=en&freq=M&reporter=NL&partner=PE&product=08104050&flow=1&indicators=QUANTITY_IN_100KG&time=2025-01&time=2025-02&time=2025-03) |
| UK | 0810405000 "vaccinium macrocarpon and vaccinium corymbosum" (same as EU) | as EU | Same as EU | [UK Trade Tariff API heading 0810](https://www.trade-tariff.service.gov.uk/api/v2/headings/0810) |
| Chile | 0810.4011/4019 "Arándanos rojos"; **0810.4021/4029 "Arándanos azules o blueberry"** (organic, other); 0810.4031/4039 "Cranberries (Vaccinium macrocarpum)"; 0810.409x others | 0811.9011/9019 "Arándanos" (not split by species) | Yes for fresh exports | [Arancel Aduanero, Diario Oficial núm. 43.124](https://www.subrei.gob.cl/docs/default-source/default-document-library/arancel_aduanero_nacional_de_la_republica_de_chile.pdf?sfvrsn=4d26012f_0), p. 51 |
| Peru | Single line 0810.40.00.00 "Arándanos rojos, mirtilos y demás frutos del género Vaccinium" | Frozen in 0811.90.99.00 "Los demás" | No line split. Exports are in practice blueberries because Peru has no commercial cranberry [inference] | [Arancel de Aduanas 2022](https://www.sunat.gob.pe/legislacion/procedim/normasadua/gja-04/ctrlCambios/anexos/Arancel_2022.pdf) |
| Mexico | 0810.40.01 NICO **01 "Arándanos azules (Vaccinium corymbosum) orgánicos"**, **91 "Los demás arándanos azules (Vaccinium corymbosum)"**, 92 other organic, 99 other | 0811.90.99 NICO 01 "Arándanos azules" | Yes at NICO level. Whether statistics are published at NICO level was not checked | [DOF 22 Aug 2022 NICO acuerdo](https://www.diputados.gob.mx/LeyesBiblio/ref/ligie_2022/LIGIE_2022_acuerdo02_22ago22.pdf) |
| China | 08104000 / 0810400000 "鲜蔓越橘、越橘及其他越橘属植物果实". Former 0810400010 (fresh cranberry) and 0810400090 (越橘) are marked expired from 2022. Inspection (CIQ) suffix 0810400000.103 = 鲜蓝莓 (fresh blueberry) | not checked | No in published statistics; CIQ suffixes are declaration codes, not a statistics dimension [inference] | Secondary only: [i5a6](https://www.i5a6.com/hscode/detail/0810400000), [hsbianma](https://www.hsbianma.com/Code/0810400090.html). Official MOF page returned 502 and GACC 412 |
| HS6 (Comtrade, WITS, BACI, FAO TM) | 081040 all Vaccinium | 081190 mixed | No | WITS label "Cranberries, milberries...etc, fresh" |

**What this means for harvest timing.**

- Monthly HS6 or CN8 series can show harvest timing by origin when the origin exports almost no other Vaccinium fruit. That covers Peru, Chile, Mexico, Morocco, South Africa, Argentina, Colombia, Zimbabwe and Namibia [inference from their production profiles].
- For Chile and Mexico, the national lines remove the doubt if national data are used.
- For US and Canadian origins, HS6 and CN8 mix in the cranberry season (autumn) [inference]. Use US HTS10 import data, where Canadian wild and cultivated blueberries are split, or AMS movement data instead.
- Frozen trade cannot be used for timing in the EU (no highbush line) or Peru (mixed line). Frozen fruit can also be stored [inference].

### 4.4 USDA systems

**FAS GAIN.** Blueberry-relevant report series by country. The list comes from a keyword search of the [FAS data search](https://www.fas.usda.gov/data/search?keyword=blueberry) in a browser (74 results). The PDFs open directly through `apps.fas.usda.gov/newgainapi`; fas.usda.gov pages return 403 to plain HTTP clients.

| Country | Series and dates | Example URL |
|---|---|---|
| Peru | "Peruvian Blueberry Production Blooming" (Jul 2017); Blueberry Annual Voluntary (Jan 2023); Blueberry Annual (Feb 2024, Jun 2025) | [PE2025-0010](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf) (opened, 9 pages, PSD table HS 081040) |
| Mexico | Blueberry Annual Voluntary (Jan 2024, Feb 2025); Berry Annual Voluntary (Feb 2025, Mar 2026) | [MX2026-0015](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Berry+Annual+Voluntary_Guadalajara_Mexico_MX2026-0015.pdf) (opened, 13 pages) |
| Chile | Blueberry Annual Voluntary (Dec 2022); "Export Fruit Crops Put at Risk due to Unexpected Hail Storms" (Nov 2018); "Chilean Fruit Exports hit by a Port Strike and Frost in 2014" (Mar 2014); fruit export volumes 2011 (Mar 2012) | [CI2022-0030](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual+Voluntary_Santiago_Chile_CI2022-0030.pdf) (opened); [hail 2018](https://www.fas.usda.gov/data/gain/2018/11/chile-export-fruit-crops-put-risk-due-unexpected-hail-storms) |
| China | New to Market Product Report, Fresh Blueberries (Jun 2020); Blueberry Annual Voluntary 2023 (Apr 2023); frozen fruit quarantine change (Sep 2024) | [CH2023-0046](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual+Voluntary+2023_Beijing+ATO_China+-+People%27s+Republic+of_CH2023-0046.pdf) (opened, 7 pages) |
| Canada | "High Bush Blueberry Production in Canada" (Dec 2017); Blueberry Annual Voluntary (Feb 2023) | [Canada 2023](https://www.fas.usda.gov/data/gain/2023/02/canada-blueberry-annual-voluntary) |
| South Africa | "The Budding Blueberry Industry" (Oct 2017); USHBC visit (Mar 2020); "Industry Continues Strong Growth" (Jul 2020); "South African Blueberry Market Analysis" (Aug 2026) | [SA 2026](https://www.fas.usda.gov/data/gain/2026/08/south-africa-south-african-blueberry-market-analysis) |
| Spain | "Spanish soft fruit production increases" (Feb 2016); Spanish Berry Outlook (Jul 2023) | [Spain 2023](https://www.fas.usda.gov/data/gain/2023/07/spain-spanish-berry-outlook) |
| Argentina | "Blueberries" (Jan 2005, Nov 2006) | [AR 2006](https://www.fas.usda.gov/data/gain/2006/11/argentina-blueberries) |
| Morocco | "Technical Regulation on 'Red Fruit' (Berries)" (Jun 2018) | [MA 2018](https://www.fas.usda.gov/data/gain/2018/06/morocco-technical-regulation-red-fruit-berries) |
| Poland, Germany | Poland berry supplier (Nov 2013); Germany organic and blueberries (Oct 2019) | [PL 2013](https://www.fas.usda.gov/data/gain/2013/11/poland-poland-pursues-becoming-berry-supplier-russia-and-eu) |

**ERS.** [Fruit and Tree Nuts Yearbook](https://www.ers.usda.gov/data-products/fruit-and-tree-nuts-data/fruit-and-tree-nuts-yearbook-tables), Berries workbook, Table D-2 "Blueberries: Area harvested, yield, production, and season-average grower price, by State", 1980 to 2024. The same page lists Supply and Availability (G) and U.S. Trade (H) workbooks; these were not opened.

**AMS Market News and MyMarketNews.**

| Report | What it gives for blueberries | Archive | Status | Priority |
|---|---|---|---|---|
| [WA_FV408 weekly blueberry shipments (slug 3251)](https://mymarketnews.ams.usda.gov/viewReport/3251) | Weekly 10,000 lb units by class (domestic, organic, import, frozen, greenhouse, "adapted environment"), variety when reported (Berkeley, Blue Ray, Bluecap), transport mode and origin (8 US states with California split in two, Canada, Peru, Chile, Mexico, Argentina, Colombia, Morocco and more); this season and last season to date | MMN Nov 2017 to 26 Apr 2025; [ESMIS](https://esmis.nal.usda.gov/publication/weekly-shipments-movement-blueberry) Nov 2018 to Apr 2025; discontinued | O | P1 |
| [Daily Movement Report (FVDDAILY_MOV, slug 3264)](https://www.ams.usda.gov/mnreports/fvddaily_move.pdf) | Daily 40,000 lb units by district (e.g. San Joaquin Valley, Oxnard) and port of entry; season to date and last season | current; history in MMN | O | P1 |
| [National Shipping Point Trends (FVWTRDS, slug 1662)](https://mymarketnews.ams.usda.gov/viewReport/1662) | Three-week shipments in 100,000 lb units for Oregon and Washington and BC crossings; FOB prices; "LAST REPORT" season-end flags | MMN 2017 to Oct 2026; [ESMIS](https://esmis.nal.usda.gov/publication/fresh-fruit-and-vegetable-national-shipping-point-trends) Dec 2018 to Sep 2025 | O | P2 |
| [National FOB Review (slug 3130)](https://mymarketnews.ams.usda.gov/viewReport/3130) | Daily FOB prices by origin or port | 2017 onward | O | P3 |
| [Terminal market fruit, e.g. NX_FV010](https://www.ams.usda.gov/mnreports/nx_fv010.pdf) | Wholesale prices by origin | current | O | P3 |
| [USMCA seasonal perishables (slug 3466)](https://mymarketnews.ams.usda.gov/viewReport/3466) | Weekly narrative on Mexico crossings and Peru imports | current | O | P3 |
| [MyMarketNews API](https://mymarketnews.ams.usda.gov/mymarketnews-api) | Programmatic access to all of the above; all imports now on WA_FV170 | AMS says "All historical data for all shipping point markets is available" ([Specialty Crops page](https://mymarketnews.ams.usda.gov/general-resources/Specialty-Crops)) | OL (403 without key) | P1 |

The old Market News Portal host (`marketnews.usda.gov`) no longer resolves. AMS moved Specialty Crops data to MyMarketNews on 16 December 2024.

### 4.5 Industry intelligence

| Source | Contains | Access and terms | Lang | Coverage | Status | Priority |
|---|---|---|---|---|---|---|
| [IBO 2024 report](https://www.internationalblueberry.org/2024-report/) and [2021 report](https://www.internationalblueberry.org/2021-report/) | Missing editions of the global report | Registration form (not submitted); rights not confirmed | en | 2021, 2024 | O | P2 |
| [IBO Summit 2025 presentations](https://www.internationalblueberry.org/ibo-summit-sa-presentations/) | 15 PDFs incl. the [IBO Global Production Report](https://www.internationalblueberry.org/wp-content/uploads/2025/10/10.15-Colin-Fain-IBO-Global-Production-Report.pdf) (46 pages, 2024 season factor survey) and a South Africa deck | Open download; terms not found | en | 2025 | O | P2 |
| [IBO Morocco Berry Conference 2025](https://www.internationalblueberry.org/morocco-berry-conference-2025-presentations/) | 11 PDFs (French and English) | Open; one sample gave no extractable text | fr/en | Nov 2025 | O | P3 |
| [IBO news archive](https://www.internationalblueberry.org/sitemap_index.xml) | About 2,500 posts, many reposts | robots allows all; footer copyright only | en/es | 2012-2026 | O | P2 |
| [IBO Online Reports](https://www.internationalblueberry.org/online-reports/) | Member dashboards | Members only | en | 2023, 2024 | O | P3 |
| [Agronometrics](https://www.agronometrics.com/) | USDA and customs data explorer, Global Trade Data | Paid (14-day trial); [TOS](https://www.agronometrics.com/tos/) forbid resale or redistribution without consent | en/es | n/a | O | P3 |
| [Agronometrics Stories](https://stories.agronometrics.com/category/blueberries/) | Free articles and charts | Same TOS | en | ongoing | O | P2 |
| [Rabobank World Fruit Map 2025](https://www.rabobank.com/knowledge/q011486210-world-fruit-map-a-changing-basket-of-fruits-and-trade-flows) | Summary and download; berry reports only via press summaries such as [FreshFruitPortal 2022](https://www.freshfruitportal.com/news/2022/11/15/blueberry-availability-expanding-globally-rabobank/) | 403 to plain client, readable in browser; posters client-only | en | Jul 2025 | OL | P3 |
| [Frutas de Chile, Comité de Arándanos](https://frutasdechile.cl/committee/arandanos/) | Variety fact sheets (Keecrisp, Meadowlark, Blue Ribbon, Optimus, Loreto Blue, Peachy Blue), seminar decks | Open; terms not found | es | 2019-2025 | O | P3 |
| [BerriesZA Export Reports](https://www.berriesza.co.za/market-access/export-reports/) | South African shipment volumes and destinations | Members only | en | n/a | O | P3 |
| [iQonsulting](https://www.iqonsulting.com/), [Veritrade](https://www.veritradecorp.com/en/), [Tridge](https://www.tridge.com/) | Commercial trade intelligence | Paid or not visible | es/en | n/a | OL / O / O | P3 |

### 4.6 Trade press: archive depth, robots and terms

| Site | Lang | Archive depth seen | Site search | robots.txt | Terms of use | Reuse allowed? | Status |
|---|---|---|---|---|---|---|---|
| [FreshFruitPortal](https://www.freshfruitportal.com/) | en | Sitemaps list about 3,100 posts back to 2021. Some older articles return **HTTP 410 Gone** (2012-10-26 and 2022-01-26 tested); a 2021-12-01 article still opens | Disallowed (`/*?s=`) | Articles allowed; feeds, author pages and `/hemeroteca/` disallowed | No terms page found; privacy and cookie policies only | Not stated | O |
| [Portal Frutícola](https://www.portalfruticola.com/) | es | 30 post sitemaps (about 29,500 URLs); 2010 article opens; 2013 article returns 410 | Disallowed | As FreshFruitPortal | [Aviso legal](https://www.portalfruticola.com/aviso-legal/) forbids "reproducir, copiar, distribuir ... comunicar públicamente" without authorisation | No | O |
| [FreshPlaza](https://www.freshplaza.com/) (+ .es, .de) | multi | Yearly news sitemaps 2012-2026 | Allowed | **`Content-Signal: search=yes, ai-train=no, ai-input=no`**, declared a reservation under EU Directive 2019/790 Art. 4; ClaudeBot, GPTBot, CCBot, Google-Extended, Bytespider and others fully blocked | [Terms of Delivery](https://www.freshplaza.com/north-america/content/terms-of-delivery/): content "may not be copied, reproduced and/or made public" | No, and no AI input | O |
| [Hortidaily](https://www.hortidaily.com/) (+ .es) | en/es | Yearly sitemaps for 2009 and 2012-2026 | Allowed | Same Content-Signal and bot blocks as FreshPlaza | Same publisher terms | No, and no AI input | O |
| [Blueberries Consulting](https://blueberriesconsulting.com/) | es/en | Sitemaps back to 2015; hosts PDFs from 2016 | n/a | All allowed | [Aviso legal y términos de uso](https://blueberriesconsulting.com/aviso-legal-y-terminos-de-uso/): reproduction "total o parcial" and commercial use prohibited | No | O |
| [Produce Report](https://www.producereport.com/) | en | Blueberry listing about 26 pages | `/search/` disallowed | Crawl-delay 10 | Not found; "@Copyright 2015 Produce Report. All rights reserved." | Not stated | O |
| [Fruitnet](https://www.fruitnet.com/) | en/de/zh | Yearly sitemaps 1999-2026 | `/searchresults` disallowed | Articles allowed; `/api/*`, RSS disallowed | [T&C 6.3](https://www.fruitnet.com/terms-and-conditions): no copy, reproduce, republish, derivative works or download except personal or internal use | No | O |
| [The Packer](https://www.thepacker.com/) | en | Monthly sitemaps May 2016 to Oct 2026 | `/search?q=*` disallowed | Otherwise allowed | Footer: "This material may not be published, broadcast, rewritten, or redistributed." [Farm Journal ToS](https://www.farmjournal.com/terms-of-service/) body did not render | No | O |
| [EastFruit](https://east-fruit.com/en/) | ru/uk/en/uz | Posts from 2020 (sitemap lastmod) | Disallowed | Search, paging and query URLs disallowed | Not found; "Copyright © 2020-2021 EastFruit. All rights reserved." | Not stated | O |
| [Agraria.pe](https://agraria.pe/) | es | Article IDs up to about 43,000; 2019 blueberry article opened | n/a | All allowed | "Términos y Condiciones" link is empty (`#`); "Todos los derechos reservados" | Not stated | O |
| [Redagrícola](https://redagricola.com/) | es | Sitemaps back to 2015 | n/a | All allowed except shop paths | Not found | Not stated | O |
| [Fruit Growers News](https://fruitgrowersnews.com/) | en | Not measured (sitemap 403) | n/a | Crawl-delay 10; articles allowed | [Publisher terms](https://greatamericanmediaservices.com/policies/terms/): no use, copy, reproduce, link, modify, translate, publish or distribute without written consent | No | O |

### 4.7 Company disclosures

| Company | Document | Weather and timing content seen | Status | Priority |
|---|---|---|---|---|
| Hortifrut (CMF registry 1.096) | [Memorias 2008-2025](https://investor.hortifrut.com/memorias-corporativas/); [reasoned analysis Mar 2024](https://investor.hortifrut.com/wp-content/uploads/2024/04/07.-Analisis-Razonado-HF-Mar24_English.pdf) | Lower 2023 industry volumes from Peru and Chile "because of the climatic effects of the El Niño Phenomenon" | O | P2 |
| Mission Produce (Nasdaq AVO) | [10-K FY2025](https://www.sec.gov/Archives/edgar/data/1802974/000180297425000048/avo-20251031.htm) | Peru harvest "typically runs from July through January"; prior-year prices lifted by "industry supply constraints during the Peru harvest season" | O | P3 |
| Camposol (bond issuer) | [IR news](https://investors.camposol.com/news-events/news-releases), [Sustainability Report 2024](https://www.camposol.com/wp-content/uploads/2025/09/RSCAMP2024ING-1.pdf) | Pruning timing strategy, Biloxi and 'La Chola' variety statements (search snippets and trade press) | OL | P2 |
| Costa Group (ASX until 2024) | [Annual Report 2022](https://announcements.asx.com.au/asxpdf/20230421/pdf/45nw32qdp9mjc2.pdf), [Sustainability Report 2023](https://costagroup.com.au/wp-content/uploads/2025/01/J231050-Costa-Group-SR-2023-FA_online.pdf) | Morocco 2022 "delayed crop timing, due to weather" (trade-press summary of results); farms in Corindi, Tasmania, Kenitra, Larache, Yunnan | O | P3 |

### 4.8 Breeder and nursery catalogues (cultivar traits)

| Source | Fields | Status | Priority |
|---|---|---|---|
| [Fall Creek variety pages](https://www.fallcreeknursery.com/commercial-fruit-growers/varieties) (38 varieties) | Chill class (Zero to High), ripening class (Very Early to Very Late), berry size, habit. Example: [Biloxi](https://www.fallcreeknursery.com/commercial-fruit-growers/varieties/biloxi) "Zero Chill", yields "disappointing in areas with chilling above 150 hours", "grown fully evergreen" | O | P2 |
| [Planasa blueberry](https://planasa.com/product/blueberry/) (6 Blue M* varieties) | g/plant, g/fruit, Brix, Cartaya trial, monthly production calendar for "Mediterranean countries" in the [data sheet](https://planasa.com/wp-content/uploads/data-sheet/bl-1542_en.pdf) | O | P2 |
| [Costa BluGenix](https://costagroup.com.au/2026/05/29/blugenix-powers-the-future-of-blueberries/) | Programme statement: varieties for "low latitude no chill to mid-chill regions" | O | P3 |
| [Mountain Blue genetics](https://www.mountainblue.com.au/mountain-blue-genetics), [OZblu OZ Varieties](https://www.ozblu.com/oz-varieties/), [Hortifrut genetic development](https://www.hortifrut.com/innovation/genetic-development/) | No trait tables online | O | P3 |

### 4.9 Lag references

- Callao to Rotterdam container transit: 24 days ([The Freight Hero](https://www.thefreighthero.nl/en/havens/callao), forwarder page).
- South America to China: "typically take more than 45 days". The Chancay port cuts this "by at least 10 days" ([Produce Report](https://www.producereport.com/article/chancay-port-sends-first-batch-peruvian-blueberries-shanghai)).
- Peru customs revisions: Green Channel export declarations take about four weeks to stabilise. The first-week figure is typically about 37 percent below the final one, total declarations move 2 to 3 percent, and 3 to 6 percent of declared volume is never cleared ([Agronometrics, 9 Oct 2026](https://stories.agronometrics.com/when-the-model-breaks-improving-our-real-time-view-of-perus-blueberry-exports/)).

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON.

| Job | Output | Sources | Exact fields | Effort | Priority |
|---|---|---|---|---|---|
| GLOBAL-01 Tariff concordance | table with validity dates | HTS, Chile, Peru, Mexico, China, EU/UK | country, flow, code, code_level, description_verbatim, species_scope (blueberry_only / blueberry_plus_cranberry / all_vaccinium), organic_flag, fresh/frozen/dried, valid_from, valid_to, source_url, checked_on | 0.5 d | P1 |
| GLOBAL-02 AMS weekly movement | time series | WA_FV408, FVDDAILY_MOV, MMN API, FVWTRDS | week_start, week_end, commodity_class, variety, transport_mode, origin, district, volume_10000lb, season_label, source_report, release_date, revised_flag, source_url | 3 d | P1 |
| GLOBAL-03 Monthly customs curves | time series | Comext, Census, HMRC, Comtrade | month, reporter, partner_origin, code, species_scope, flow, quantity_kg, value_local, value_usd, mode, district_or_port, source, retrieved_on, revision_vintage | 2 d | P1 |
| GLOBAL-04 Season metrics and anomalies | time series | outputs of 02 and 03, lag references | origin, series_id, season_label, season_window_definition, total_volume, date_q10, date_q50, date_q90, peak_week_or_month, onset_date, end_date, lag_applied_days, lag_basis, anomaly_q10_days, anomaly_q50_days, volume_anomaly_pct, data_quality_flags, model_cell_id, model_harvest_start, model_harvest_end | 2 d | P1 |
| GLOBAL-05 GAIN claims and events | claim records | FAS GAIN | kind, topic, period, crop_context, evidence_type=government_attache_report, geography, citations (report no., page, table), summary, limitations | 2 d | P1 |
| GLOBAL-06 Company weather events | event records | Hortifrut, Mission, Camposol, Costa | kind=event, topic, period, geography, crop_context, evidence_type=company_disclosure, citations, effect_direction, limitations | 1.5 d | P2 |
| GLOBAL-07 IBO decks and gated editions | claim records | IBO 2021/2024, Summit 2025, Morocco 2025 | kind, topic, period, crop_context, evidence_type=industry_presentation, geography, citations (deck, slide), presenter | 1.5 d | P2 |
| GLOBAL-08 Trade-press link index | event records (human-written) | 12 press sites plus IBO news | url, publisher, publication_date, title, language, country_guess, hazard_keywords, season_keywords, http_status at capture, human_decision | 2 d | P2 |
| GLOBAL-09 Cultivar catalogue | cultivar table | Fall Creek, Planasa, Frutas de Chile, Costa | cultivar, licensor, type, chill_class (verbatim), chill_hours if stated, ripening_class, harvest_months_by_region, evergreen statement, test site, source_url, checked_on | 1 d | P2 |
| GLOBAL-10 Production denominators | time series | FAOSTAT, Eurostat, ERS | geography_id, year, area_ha, production_t, yield_t_ha, source, flag | 0.75 d | P3 |

**Mapping to the IBO record schema.**

- GLOBAL-05 to GLOBAL-08 produce records with the existing fields: `kind`, `topic`, `period` (start, end, precision), `crop_context`, `evidence_type`, `geography_ids`, `citations`, `limitations`.
- A new `evidence_type` value is needed for each source family: `government_attache_report`, `company_disclosure`, `industry_presentation` and `trade_press_lead`.
- Trade-press records must contain only text written by our reviewers plus a link, never quoted article text beyond a short phrase.

## 6. How each source maps to model checks

| Source | Gap or risk family | How |
|---|---|---|
| AMS WA_FV408 / MMN movement | harvest_timing in FL, GA, NC, NJ, MI, OR, WA, CA; northern highbush (Lynden, Michigan) | Compute weekly 10/50/90 percent shipment dates per state and season (2017/18 to 2024/25, then MMN). Compare their year-to-year anomalies with stage_thermal_v3 harvest start and end anomalies at the matching benchmark cells. |
| AMS BC crossings (FVWTRDS), Census HTS10 wild vs cultivated from Canada | cool-climate gap (Lynden, Lac-Saint-Jean, Cherryfield) | BC crossings give weekly timing for the Fraser Valley next to Lynden. Census 0810.40.00.24 wild imports from Canada give a lowbush season window for Quebec and the Maritimes. |
| Comext 08104050 by partner; Comtrade 081040 exports | harvest_timing for Peru, Chile, Morocco, South Africa, Zimbabwe, Argentina, Mexico | Monthly 10/50/90 percent dates after lag correction; compare with modelled harvest windows or managed-cycle scan windows. |
| Peru curves plus GAIN, Camposol and press pruning statements | Coastal Peru flowering-to-harvest gap (41-51 days modelled vs about 4 months reported); 2024 delayed pruning | Use shipment q10 dates as observed harvest starts. Use dated pruning statements as cycle starts. The implied pruning-to-harvest interval tests the managed-cycle scan. |
| GAIN Chile hail 2018 and frost 2014; IBO and press on November 2022 Linares to Chillán freeze; Chile 0810.4021/29 exports | bud_flower_freeze, fruit_frost (Chile) | Check whether season volume and q50 date show a deficit or delay after reported freezes, and whether grid Tmin shows them (it does not for 2022, per brief). |
| Hortifrut, Mission, GAIN Peru; Comext volume drop 2023/24 | heat (El Niño 2023 in coastal Peru) | Event record with season dates. Compare modelled fruit-stage heat days in 2023 with other years at Peruvian cells. |
| Eurostat F3300, ERS D-2, FAOSTAT | bud_flower_freeze (Georgia 2022, Poland), location_mapping | Year-level production dips versus modelled flowering-freeze winters. Production-weighted choice of validation cells. |
| Fall Creek and Planasa catalogues | cultivar classes, chill_dormancy | Chill-class and ripening-class priors per cultivar. Planasa monthly calendars for Huelva-type evergreen windows. |
| Trade-press link index, IBO news | all risk families; season-start statements | Leads for human-written event records with exact dates and places. |

### 6.1 Harvest timing from shipment curves

**Series that give volumes by origin over time.**

| Series | Step | Origins and regions | Years | Notes |
|---|---|---|---|---|
| AMS WA_FV408 | weekly | FL, GA, NC, NJ, MI, OR, WA, CA-central, CA-south; Canada; Peru, Chile, Mexico, Argentina, Colombia, Ecuador, Guatemala, Costa Rica, Morocco and others (imports) | Nov 2017 to Apr 2025 | 10,000 lb units; import rows dated by CBP entry summary |
| AMS MMN API (FV170, daily movement) | daily, weekly | Same, by district and port | from Dec 2024 structure; history claimed complete | free API key |
| AMS FVWTRDS | weekly (3-week window) | OR and WA, BC crossings and other districts | 2017 to now | 100,000 lb units; "LAST REPORT" flags season end |
| US Census HTS10 imports | monthly | Every origin country; customs district | 2010 to now | separates wild and cultivated blueberries |
| Eurostat Comext CN 08104050 | monthly | Every origin into each EU member state; intra-EU dispatches from ES, PT, PL, NL | 2000 to now | mixes American cranberry |
| HMRC OTS 08104050 | monthly | Every origin into the UK, by port | tested 2025 | OGL v3.0 |
| UN Comtrade HS 081040 | monthly | Exports of each reporting origin (PE, CL, MX, ZA, MA, AR, CO, ZW) | varies | mixes Vaccinium; fine for blueberry-only exporters |
| National export series (SUNAT, Chilean customs, SIAP, BerriesZA) | daily to weekly | Peru, Chile, Mexico, South Africa | region teams | pointers only here |

**Deriving season start, peak and end per origin and year.**

1. **Choose a season window per origin.** It must contain one whole season and cut at the lowest-volume month. Examples: Peru July to June; Chile September to August; Morocco and Huelva September to August; US states January to December; South Africa February to January. A human signs off each window.
2. **Clean the series.**
   - Use EU-extra imports by partner, not national reporters, for Comext. This avoids counting fruit re-exported from Dutch hubs twice.
   - Drop months flagged confidential.
   - Keep air and sea separate where the mode is given.
   - Exclude US and Canadian origins from cranberry-mixed series.
3. **Cumulative quantiles.** Compute cumulative volume and the dates at 10, 50 and 90 percent.
   - Weekly data: interpolate linearly inside the week.
   - Monthly data: spread each month uniformly over its days and interpolate. That gives a date with about plus or minus two weeks of resolution [inference].
4. **Onset, peak and end.**
   - Onset: the first week of at least two consecutive weeks above 5 percent of the season's peak weekly volume.
   - Peak: the week with the highest 3-week centred mean.
   - End: the last week above 5 percent of peak, or the AMS "LAST REPORT" flag.
5. **Lag correction to estimate harvest dates.** Subtract origin and mode lags:
   - sea transit (Callao to Rotterdam about 24 days; South America to China historically over 45 days, at least 10 days less via Chancay);
   - date-of-record rules (AMS import rows use the CBP entry summary date, filed up to ten business days after release; Comext uses the month of the import declaration);
   - packing time [inference: a few days, no source checked].
   - Store `lag_applied_days` and `lag_basis` on each row.
   - Storage time is not documented in any source I opened. Use q10 for timing, because cold storage mostly stretches the tail [inference].
6. **Anomalies.**
   - For each origin and season: `anomaly = date − median(date over all other seasons)` for q10 and q50, plus a volume anomaly in percent.
   - Use other-season medians so that a season does not shrink its own anomaly.
7. **Comparison with the model.**
   - Map each origin series to its benchmark cells (for example Peru to `pe-olmos`, `pe-chao-chavimochic`, `pe-ica`; Morocco to `ma-larache-loukkos`, `ma-agadir-souss`).
   - Take the stored stage_thermal_v3 harvest start and end per season, or the managed-cycle scan window, for each cell.
   - Report per origin: Spearman correlation of anomalies, share of seasons with the same sign, and MAE of anomalies in days, with n.
   - Weekly AMS series give about 7 seasons; Comext gives up to 25 for Chile [inference].
   - Where management dominates (Peru pruning, evergreen Morocco, Yunnan), expect little agreement. Report that result as evidence that a management layer is needed, not as a failure of the weather model.
8. **Quality flags.** `mixed_species`, `hub_reexport`, `revision_pending` (Peru declarations stabilise in about four weeks), `mode_shift` (South Africa 60/40 sea/air), `coverage_change` (AMS shipper coverage).

### 6.2 Worked example (illustration only, not calibration)

I pulled Dutch imports of CN 08104050 from Peru with one small Comext API query. Dates mark arrival in the Netherlands, not harvest. Seasons run July to June. Monthly volumes were interpolated uniformly within each month.

| Season | Volume (t) | 10% arrival | 50% arrival | 90% arrival |
|---|---:|---|---|---|
| 2019/20 | 25,660 | 2019-09-28 | 2019-11-21 | 2020-01-23 |
| 2020/21 | 38,817 | 2020-09-12 | 2020-11-07 | 2021-01-02 |
| 2021/22 | 46,501 | 2021-09-20 | 2021-11-12 | 2022-01-21 |
| 2022/23 | 68,297 | 2022-09-19 | 2022-11-09 | 2023-01-16 |
| 2023/24 | 44,472 | 2023-09-19 | 2023-11-30 | 2024-02-18 |
| 2024/25 | 68,587 | 2024-10-06 | 2024-11-28 | 2025-02-02 |

Two points stand out:

- The 2023/24 volume fell by 35 percent while the 50 percent date moved later. Companies attribute that season to El Niño ([Hortifrut](https://investor.hortifrut.com/wp-content/uploads/2024/04/07.-Analisis-Razonado-HF-Mar24_English.pdf)).
- The 2024/25 10 percent date is about two to three weeks later than in 2020 to 2022, consistent with the delayed pruning reported for 2024 [inference].

Subtracting a 24-day sea transit puts 2024/25 harvest onset for this flow in mid-September [inference]. Use the EU-extra series and the US Census series to confirm.

## 7. Access, licensing and language risks

- **AI-input prohibition.** FreshPlaza and Hortidaily robots.txt sets `ai-input=no`, which explicitly covers retrieval augmented generation. It also blocks ClaudeBot, GPTBot, CCBot and Google-Extended. Do not pass their article text through any LLM step, including the offline extraction workflow in `ibo_integration_review.md`. Human reading and linking remain fine. The existing benchmark has 11 citations to these two sites; keep them as human citations.
- **No-reproduction terms.** Fruitnet (T&C 6.3), Portal Frutícola (aviso legal), Blueberries Consulting (aviso legal), Farm Journal (The Packer) and Great American Media Services (Fruit Growers News) forbid copying or republishing. FreshFruitPortal, Agraria.pe, Redagrícola, EastFruit and Produce Report state no reuse terms, only "all rights reserved". Store metadata and links only.
- **Disappearing archives.** FreshFruitPortal and Portal Frutícola return HTTP 410 for some old articles. Record the HTTP status and a content hash when a reviewer reads an article, so citations stay checkable.
- **Commercial data.** Agronometrics TOS forbid redistribution. Rabobank berry reports and IBO Online Reports are client- or member-only. BerriesZA export reports are member-only.
- **Registration gates.** These need a human to register (free) and to record the terms accepted: IBO 2021 and 2024 forms, the Census API key, the MyMarketNews API key, a FAOSTAT API account and the Comtrade API key.
- **Open and reusable.**
  - US federal works (GAIN, ERS, AMS, Census, USITC) are not under copyright (17 U.S.C. 105).
  - FAOSTAT is CC BY 4.0, Eurostat allows reuse with source acknowledgement, and HMRC uses OGL v3.0.
  - BACI is Etalab 2.0.
  - Comtrade allows free use, but re-disseminating substantially unchanged data may need a licence.
- **Bot walls.** China Customs (412), the Rabobank site (403 to plain clients), fas.usda.gov pages (403 to plain clients), the Camposol IR site (403 or timeout), MyMarketNews HTML pages (timeouts for plain clients; they work in a browser) and an expired TLS certificate on the Costa investor site.
- **Languages.** Spanish (Portal Frutícola, Agraria.pe, Redagrícola, Blueberries Consulting, tariff books), Chinese (customs codes), Russian, Ukrainian and Uzbek (EastFruit), French (Morocco decks). Keep original-language titles in the index and translate summaries only.

## 8. Gaps: what I looked for and could not find

- An official China tariff or statistics page showing the current 10-digit code (MOF returned 502, GACC 412). The China tariff lines rest on secondary code sites.
- China's frozen-blueberry line and any open Chinese domestic shipment or wholesale-arrival series for Yunnan or Shandong.
- Whether Mexico publishes trade statistics at NICO level (0810.40.01.91). Not checked.
- Historical US HTS statistical suffixes before the current .24/.26/.29 split. A concordance is needed; not obtained.
- MyMarketNews API depth for blueberry movement before 2017. AMS claims full history, but no key was used.
- Peruvian, Chilean and Mexican weekly export series. Left to region teams; only Frutas de Chile was checked, and it shows no public weekly report.
- Storage durations for export blueberries. No source opened.
- The Chile to China express transit time (22 to 23 days) was seen only in search snippets.
- The ITC Trade Map terms and fees page (404 when fetched).
- A FreshFruitPortal terms-of-use page (none linked) and Redagrícola and EastFruit terms (none found).
- The IBO 2021 and 2024 full texts (form-gated, not submitted).
- Rabobank blueberry-specific reports (client-only).
- Cultivar trait tables from Mountain Blue, OZblu and Hortifrut (none online).
- Morocco's Office des Changes and other Moroccan trade data. Not checked; Comext covers Moroccan exports to the EU.

## 9. Ranked top 10 actions for this scope

1. **Build GLOBAL-01, the tariff concordance (0.5 d).** Every trade series depends on knowing which codes are blueberry-only.
2. **Back-fill AMS WA_FV408 from the ESMIS and MMN PDF archives, November 2017 to April 2025 (part of GLOBAL-02).** Parse classes, varieties, origins and weekly volumes.
3. **Request a free MyMarketNews API key (human action), then pull FV170 and daily movement from May 2025** so the weekly series continues.
4. **Pull Comext CN 08104050 monthly, EU-extra by partner, 2000 to now (GLOBAL-03).** No key is needed.
5. **Request a free Census API key, then pull HTS10 0810400024/26/29 monthly by country and district from 2010 (GLOBAL-03).**
6. **Run GLOBAL-04 season metrics with documented lags and compare anomalies with stage_thermal_v3** for Peru, Chile, Morocco, South Africa, Florida, Georgia, Michigan and Washington/BC. Start with Peru 2019 to 2025 to test the pruning-shift and coastal-interval gaps.
7. **Extract FAS GAIN blueberry reports into claim and event records (GLOBAL-05).** They are public domain and can go straight into the Regional evidence tab after review.
8. **Set up the trade-press link index under strict rules (GLOBAL-08).** Store metadata only, apply no AI processing to FreshPlaza and Hortidaily text, follow robots and crawl delays, and let reviewers write all records themselves.
9. **Ask a human to register for the IBO 2021 and 2024 reports and confirm their reuse terms (GLOBAL-07).** Add the 2025 Summit decks after rights checks.
10. **Build the cultivar catalogue table from Fall Creek and Planasa (GLOBAL-09)** and reconcile it with the UF and FFSP data in `docs/research/2026-09-21/05_genotype_layer.md`.
