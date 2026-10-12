# Source inventory: Central, Northern and Eastern Europe plus EU-wide sources

Slug: `europe-central-north-east`. Checked on 2026-10-11. JSON list: `europe-central-north-east.sources.json` (73 sources, 14 jobs). I mark my own reasoning as [inference].

## 1. Scope and summary

**Countries covered:** Poland, Germany, the Netherlands, the United Kingdom, Serbia, Romania, Ukraine, the Baltic states, Finland, Sweden, Norway, Georgia (the country), Italy and France, plus EU-wide sources. I searched in Polish, German, Dutch, Finnish, Swedish, Norwegian, Serbian, Romanian, Ukrainian, Italian, French and English. I found nothing usable in Georgian, so Georgian sources here are English-language trade media and official homepages. I opened every URL in the JSON except one (`search-only`). For the top sources I pulled a real sample: an API response, a spreadsheet or the PDF pages.

**Five most valuable findings**

1. **The first dated, cultivar-specific northern highbush bloom and bloom-to-harvest data for this region.** The Dutch [VBB cultivar trial report 2007-2012](https://edepot.wur.nl/288774) gives the date when 5% of clusters had their first open flower, for each cultivar, site and year 2008-2012 at two farms (Melderslo, NL and Well/Weeze on the NL/DE border). Duke first flowered on 11-22 April and Bluecrop on 18-27 April. Days from first flower to first harvest were 61-68 for Duke and 64-79 for Bluecrop. At the nearby Vechta benchmark the model starts flowering on 24 May. That gap is about 4 to 6 weeks, larger than the "about two weeks late" noted in the benchmark [inference: different site, about 150 km away].
2. **The Naantali gap is now confirmed as a model gap, not an empty region.** The Luke statistics database ([table 0400_puutar](https://statdb.luke.fi/PxWeb/pxweb/en/LUKE/LUKE__maa__puutar/0400_puutar.px/)) lists 44 highbush blueberry enterprises on 32 ha in Southwest Finland in 2024, with a 68 t harvest, and 47 enterprises on 34 ha with 73 t in 2025. Finnish growers mainly grow half-high cultivars (North Blue, North Country, Aino, Alvar) and harvest from the end of July to early September ([HMLry](https://hmlry.fi/laji-info/pensasmustikka/); [Pousi 2024](https://satakunta.mtk.fi/documents/d/mtk-satakunta/pousi_11-4-2024hml-pdf)). Half-high flowers took -3 C for 8 h with little damage. At -5 C for 2 h, damage was severe ([MTT:n selvityksia 139, section 3.9](https://jukuri.luke.fi/server/api/core/bitstreams/4e7588f2-2a3e-4423-9ad8-e3c858470232/content)). FMI gives free hourly temperature and humidity at Turku ([FMI open data](https://en.ilmatieteenlaitos.fi/open-data), CC BY 4.0).
3. **Official sub-national yield anomalies for Poland and Germany.** GUS table 110 gives blueberry area, yield and harvest by voivodeship from 2020, with an index against the previous year. In 2024 the Dolnoslaskie yield fell to 47.8% of 2023 and Opolskie to 59.9% ([GUS 2024 xlsx](https://stat.gov.pl/download/gfx/portalinformacyjny/pl/defaultaktualnosci/5509/9/23/1/produkcja_upraw_rolnych_i_ogrodniczych_w_2024.xlsx)). Destatis publishes Kulturheidelbeeren by Land. Lower Saxony had 2,089 ha in 2022 ([Destatis Fachserie 2022 xlsx](https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Obst-Gemuese-Gartenbau/Publikationen/Downloads-Obst/strauchbeerenanbau-2030319227005.xlsx?__blob=publicationFile&v=3)). ARiMR publishes declared crop area by gmina ([ARiMR](https://www.gov.pl/web/arimr/powierzchnia-upraw-w-gminach)).
4. **One API gives a monthly harvest-timing proxy for every EU producer.** Eurostat Comext CN 08104050 (fresh highbush blueberry and cranberry) shows Polish exports peaking in July 2024 at 10,152 t, against 1,407 t in June and 7,083 t in August ([Comext API](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409?format=JSON&lang=EN&reporter=PL&partner=WORLD&product=08104050&flow=2&indicators=QUANTITY_IN_100KG&time=2024-07)). This matches IBO's report of an early 2024 season. Eurostat `apro_cpsh1` crop F3300 gives national area and production from one call ([Eurostat](https://ec.europa.eu/eurostat/databrowser/view/apro_cpsh1/default/table?lang=en)).
5. **The JRC MARS Bulletin is a ready citation-first RAG corpus.** It has been published monthly since 1992, and an archive since 2007 is on Agri4Cast ([JRC](https://joint-research-centre.ec.europa.eu/monitoring-agricultural-resources-mars/jrc-mars-bulletin_en)). The April 2024 issue reports Poland at more than 4 C above the long-term average, "the warmest period in the past 30 years", with rapeseed "flowering roughly 2 weeks early, increasing its vulnerability to late cold spells" ([April 2024 PDF](https://publications.jrc.ec.europa.eu/repository/bitstream/JRC136660/JRC136660_01.pdf)).

**Answers to the brief's direct questions:**

- **DWD phenology:** DWD does not observe Vaccinium. Its plant list has no Heidelbeere entry. The fruit species are apple, pear, red currant, gooseberry and cherries.
- **PEP725:** PEP725 holds a "Vaccinium" series (786 downloads in its statistics). Species and phases need a free login.
- **GUS:** GUS has had a separate blueberry table by voivodeship since 2020.
- **Destatis:** Destatis has one by Land.
- **CBS:** CBS has national area and farm counts only.
- **Defra:** Defra has a blueberry row for five recent years only.
- **Luke:** Luke has blueberry data by region from 2018 or earlier.
- **SSB:** SSB has a national series for 2010-2025.
- **SCB:** I did not open SCB. Swedish horticulture figures come from Jordbruksverket (64 ha in 2023).
- **Serbia RZS, Romania INS and Ukraine Derzhstat:** I did not confirm blueberry tables.
- **Eurostat:** Eurostat uses crop code F3300 "Blueberries".

## 2. Production context in brief

- **Size by country.** Eurostat F3300 for 2025 ([API](https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/apro_cpsh1?format=JSON&lang=EN&crops=F3300&sinceTimePeriod=2015)):

  | Country | Area (kha) | Production (kt) |
  |---|---|---|
  | Poland | 12.6 | 64.7 |
  | Germany | 3.45 | 17.27 |
  | Italy | 1.48 | 10.57 |
  | Romania | 1.44 | 4.99 |
  | Netherlands | 0.65 | 6.54 |
  | Latvia | 0.6 | not noted |
  | Lithuania | 0.58 | not noted |
  | Finland | 0.11 | 0.24 |
  | Sweden | 0.06 | 0.13 |

  France and Estonia are flagged "not significant". UK area was about 410-500 ha in the five years shown by [Defra](https://www.gov.uk/government/statistics/latest-horticulture-statistics). Serbia had 8,318 ha in the 2023 census, per [biznis.rs](https://biznis.rs/vesti/srbija/borovnica-postaje-plavi-dijamant-srpskog-vocarstva-vrednost-izvoza-dostigla-31-milion-dolara/) citing RZS (search-only). Georgia produced more than 7,500 t in 2025 and exported about 95% ([FreshPlaza](https://www.freshplaza.com/north-america/article/9814617/georgia-s-blueberry-exports-expand-as-sector-targets-eu-growth-and-new-markets/)).
- **Poland.** Area is concentrated in Mazowieckie (3,661 ha), Lodzkie (1,658 ha) and Lubelskie (1,643 ha) in 2024 ([GUS table 110](https://stat.gov.pl/obszary-tematyczne/rolnictwo-lesnictwo/uprawy-rolne-i-ogrodnicze/produkcja-upraw-rolnych-i-ogrodniczych-w-2024-r-,9,23.html)). The largest gminas in 2024 were Promna (504 ha), Janow (358 ha) and Warka (332 ha), per [Jagodnik citing ARiMR](https://jagodnik.pl/top-10-gminy-z-najwiekszym-arealem-uprawy-borowki-w-polsce/). Production is open-field northern highbush, drip-irrigated, with about 3% under structures. Exports usually peak in August (IBO records in the app).
- **Germany.** Lower Saxony dominates: 153 farms and 2,089 ha in 2022; Brandenburg had 401 ha ([Destatis](https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Obst-Gemuese-Gartenbau/Tabellen/strauchbeerenanbau.html)). LWK Niedersachsen expects the main open-field harvest from mid-July to early August, led by Duke ([Fruchthandel](https://www.fruchthandel.de/news/norddeutsche-heidelbeerernte-nimmt-fahrt-auf)).
- **Netherlands.** Area fell from 950 ha in 2019 to 570 ha in 2026 ([CBS 81302ned](https://www.cbs.nl/nl-nl/cijfers/detail/81302ned)). The VBB trial recommends Duke (early), Draper (mid), Liberty (late) and Aurora (very late, with a risk of unripe fruit in the north) ([VBB](https://edepot.wur.nl/288774)).
- **Finland, Sweden and Norway.**
  - Finland has about 110 ha, mostly half-high ([HMLry](https://hmlry.fi/laji-info/pensasmustikka/)).
  - Sweden had 64 ha and 120 t in 2023 ([Jordbruksverket](https://jordbruketisiffror.wordpress.com/2024/07/22/120-ton-odlade-blabar-skordades-2023/)).
  - Norway had 158 dekar (about 16 ha) in 2025 ([SSB 10507](https://www.ssb.no/statbank/table/10507)).
- **Romania and Serbia.** IBO already notes clay soils and April frost at altitude for Romania, and anti-hail nets and potted substrate for Serbia. Serbian ripening runs from the end of June (Earliblue) to mid-August ([Agroklub](https://www.agroklub.rs/vocarstvo/borovnica-od-berbe-do-skladistenja/88050/)).
- **Ukraine.** State statistics "cover a small part of blueberry plantations". Fresh exports went mainly to the Netherlands (about 40%) and Poland (about 30%) ([UBA](https://uaberries.com/novyny/rynok/dynamika-vyrobnytstva-ta-zovnishnoi-torhivli-iahodamy-ukrainy)).
- **Georgia.** Growing is in Samegrelo, Guria, Imereti and Adjara, in tunnels and open field, with harvest from May to July ([FreshPlaza](https://www.freshplaza.com/north-america/article/9814617/georgia-s-blueberry-exports-expand-as-sector-targets-eu-growth-and-new-markets/)). The 2021 harvest started on about 26 May ([EastFruit](https://east-fruit.com/en/news/blueberries-are-ripe-the-harvest-of-the-most-expensive-berries-begins-in-georgia/)).
- **Italy.** Duke ripens around 25 June at the Agrion station at Boves (590 m) ([Rivista di Frutticoltura](https://rivistafrutticoltura.edagricole.it/featured/mirtillo-gigante-americano-coltivazione-piemonte/)).
- **France.** About 95% of production is in open soil ([Chambres d'agriculture](https://chambres-agriculture.fr/actualites/actualite/la-production-de-myrtilles-en-france)).

## 3. What the app already has for this scope

**Benchmark sites** (`pipelines/weather/benchmark_sites.json`, results in `docs/weather/benchmark/benchmark.json`, profile `stage_thermal_v3`):

| Site | Published bloom / harvest | Model budbreak | Model flowering | Model harvest | Mean chill h |
|---|---|---|---|---|---|
| pl-lublin (51.25 N, 22.57 E) | May / Jul-Sep, peak Aug | 12 May | 25 May to 21 Jun | 20 Jul to 3 Sep | 3,604 |
| de-ni-vechta (52.73 N, 8.29 E) | May / Jun-Sep, peak Jul | 10 May | 24 May to 22 Jun | 23 Jul to 16 Sep | 3,076 |

Both sites are Deciduous in 15 of 15 winters. Harvest recall is 1.0 at Lublin and 0.75 at Vechta, because the June tunnel and Duke harvest is missed. Ranked risk is only harvest heavy rain. Spring frost at bloom is the literature risk at both sites but does not rank.

**IBO records in scope** (`dist/evidence/ibo-regional-v1.json`): nine records.

- Poland:
  - frost on green fruit in May 2024 (PL-LU, PL);
  - May 2025 frosts;
  - Bialystok cold of -41 C in 2021;
  - drip irrigation and 3% under structures;
  - an August export peak (July in 2024).
- Germany:
  - harvest from the end of June to mid-September, with 70% in the Lueneburg Heath;
  - spring 2024 frost on green fruit of early Duke.
- Romania: clay soils with high pH, and April frost on Duke and Legacy at altitude.
- Serbia: reverse-osmosis water.

There are no IBO records for NL, GB, FI, SE, NO, the Baltics, UA, GE, IT or FR.

**Recorded gaps** (registry `gaps`):

- Poland has no Instytut Ogrodnictwa month calendar for Lubelskie.
- German bloom rests on Wikipedia and a Saxony leaflet.
- Planting months are missing for both countries.

**Live pin:** Naantali (60.5 N) produces no calendar in 15 of 15 winters. A stage misses its heat requirement within the 300-day horizon (HANDOVER.md, PROGRESS_LOG.md).

**Earlier research:** The 2026-09-21 documents name no European station networks or European phenology sources. `GLOBAL_PHENOLOGY_REVIEW.md` only says to "compare Michigan/NJ and appropriate European ... trials". This inventory is new ground.

## 4. Source inventory

**Status codes:**

- O = opened;
- OL = opened-limited;
- SO = search-only.

Full fields are in the JSON.

### 4.1 Phenology observations, cultivar trials and cultivar traits

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [VBB Rassenonderzoek 2007-2012](https://edepot.wur.nl/288774) | First-flower dates, bloom days, bloom-to-harvest days, yield; 7 cultivars, 2 farms | Open PDF; "(c) VBB (2013)" | nl | 2008-2012 | O | P1 |
| [Cosmulescu 2022, Banat](https://doi.org/10.3390/agronomy12112605) | BBCH stage Julian days for Duke, Hannah's Choice, Elliott | CC BY 4.0; MDPI blocks scripts | en | 2020-2022 | OL | P1 |
| [MTT selvityksia 139, s. 3.9](https://jukuri.luke.fi/server/api/core/bitstreams/4e7588f2-2a3e-4423-9ad8-e3c858470232/content) | Aino and Alvar flower frost tolerance at -1, -3 and -5 C | Open; terms not found | fi | 2003-2005 | O | P1 |
| [Doradca Jagodowy IWT bulletins](https://doradcajagodowy.pl/blog/borowka/borowka-poczatek-kwitnienia-odmian-wczesnych-iwt-9-21-04/) | Dated BBCH stages, temperature sum above 5 C from 1 Jan, frost injury | Paid; all rights reserved | pl | 2018 seen | O | P2 |
| [Jagodnik monitoring and frost reports](https://jagodnik.pl/borowki-po-przymrozkach-2024-do-70-strat-w-niektorych-regionach/) | Dated bloom and frost narratives, gmina areas | Partly paywalled; terms not found | pl | 2016-2026 | O | P2 |
| [IO bloom assessments in trade press](https://www.sadyogrody.pl/owoce/101/borowki_2022_jakie_kwitnienie_i_zawiazanie_owocow,30613.html) | Instytut Ogrodnictwa bloom and fruit-set notes | Open; terms not found | pl | 2022 seen | O | P2 |
| [Bozek 2009, Lublin](https://doi.org/10.5586/aa.2009.011) | Bloom start, end and duration, 6 cultivars | CC BY 3.0; PDF HTTP 500 | en | 2001-2004 | OL | P2 |
| [Pavliuk et al. 2025, Czechia](https://doi.org/10.3390/app152011158) | BBCH phenology, 32 cultivars | CC BY 4.0 | en | 2020-2024 | OL | P2 |
| [Latvia, ISHS 926_26](https://ishs.org/ishs-article/926_26/) | 6 highbush and 4 half-high cultivars; season fit | ISHS paywall | en | 2007-2009 | O | P2 |
| [HMLry pensasmustikka](https://hmlry.fi/laji-info/pensasmustikka/) | Finnish cultivars and ripening order | All rights reserved | fi | current | O | P2 |
| [Pousi 2024](https://satakunta.mtk.fi/documents/d/mtk-satakunta/pousi_11-4-2024hml-pdf) | Finnish harvest window, yields, risks | Terms not found | fi | 2024 | O | P2 |
| [NLR hageblaabaer](https://www.nlr.no/kunnskap/fagartikler/frukt-og-baer/ostlandet/dyrking-av-hageblabaer) | Heat requirement in GDH per stage | Terms not found | no | 2020, upd. 2024 | O | P2 |
| [PEP725](https://pep725.eu/dataset/) | Pan-European phenology; Vaccinium present | Free login; example data CC BY 4.0 | en | 1775-2024 | OL | P2 |
| [LWK season press via Fruchthandel](https://www.fruchthandel.de/news/norddeutsche-heidelbeerernte-nimmt-fahrt-auf) | Annual harvest-start statements, Lower Saxony | Terms not found | de | annual | O | P2 |
| [Agrion via Rivista di Frutticoltura](https://rivistafrutticoltura.edagricole.it/featured/mirtillo-gigante-americano-coltivazione-piemonte/) | Duke ripens about 25 June at 590 m | Terms not found | it | 2024 | O | P3 |
| [Cacak 'Reka' study](https://www.researchgate.net/publication/351078926_Fertilization_biology_of_'Reka'_highbush_blueberry) | Bloom from the last third of April to mid-May, 5 cultivars | HTTP 403 | en | 3 yrs | SO | P3 |
| [Agroklub Serbia](https://www.agroklub.rs/vocarstvo/borovnica-od-berbe-do-skladistenja/88050/) | End of bloom to ripening 40-70 days | Terms not found | sr | 2023 | O | P3 |
| [DWD phenology](https://opendata.dwd.de/climate_environment/CDC/observations_germany/phenology/annual_reporters/fruit/historical/) | No Vaccinium; currant, gooseberry and apple proxies | CC BY 4.0 | de | 1925-2024 | O | P3 |
| [WUR teelt handbook](https://edepot.wur.nl/307323) | Cultivar descriptions | Terms not found | nl | n/a | OL | P3 |

### 4.2 Production, area and land use

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [Eurostat apro_cpsh1 F3300](https://ec.europa.eu/eurostat/databrowser/view/apro_cpsh1/default/table?lang=en) | National area, production, yield, flags | CC BY 4.0, attribution | en | 2015-2025 sampled | O | P1 |
| [GUS table 110](https://stat.gov.pl/obszary-tematyczne/rolnictwo-lesnictwo/uprawy-rolne-i-ogrodnicze/produkcja-upraw-rolnych-i-ogrodniczych-w-2024-r-,9,23.html) | Voivodeship area, yield, harvest, indices | Free with attribution | pl/en | 2020-2025 | O | P1 |
| [ARiMR area by gmina](https://www.gov.pl/web/arimr/powierzchnia-upraw-w-gminach) | Declared area by gmina | Terms not found | pl | 2021- | OL | P1 |
| [Destatis Strauchbeeren](https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Obst-Gemuese-Gartenbau/Tabellen/strauchbeerenanbau.html) | Kulturheidelbeeren by Land | Datenlizenz Deutschland 2.0 | de | annual | O | P1 |
| [Luke 0400_puutar](https://statdb.luke.fi/PxWeb/pxweb/en/LUKE/LUKE__maa__puutar/0400_puutar.px/) | Enterprises, ha, tunnel ha, yield by region | CC BY 4.0 | en/fi | 2018-2025 sampled | O | P1 |
| [GUS final crop estimate 2024](https://stat.gov.pl/files/gfx/portalinformacyjny/pl/defaultaktualnosci/5509/5/23/1/wynikowy_szacunek_glownych_ziemioplodow_rolnych_i_ogrodniczych_2024.pdf) | Dated frost damage narrative | Free with attribution | pl | annual | O | P2 |
| [CBS 81302ned](https://www.cbs.nl/nl-nl/cijfers/detail/81302ned) | NL blueberry ha and farms | CC BY 4.0 | nl | 2015-2026 | O | P2 |
| [Defra horticulture](https://www.gov.uk/government/statistics/latest-horticulture-statistics) | UK blueberry area, yield, production, value | OGL [inference] | en | 5 yrs | O | P2 |
| [RZS plant production](https://www.stat.gov.rs/sr-latn/oblasti/poljoprivreda-sumarstvo-i-ribarstvo/biljna-proizvodnja) | Serbia; blueberry table not confirmed | Terms not found | sr | ? | O | P2 |
| [SSB 10507](https://www.ssb.no/statbank/table/10507) | NO blueberry area, yield, harvest | CC BY 4.0 | no | 2010-2025 | O | P3 |
| [Jordbruksverket](https://jordbruksverket.se/om-jordbruksverket/jordbruksverkets-officiella-statistik/jordbruksverkets-statistikrapporter/statistik/2021-06-29-tradgardsproduktion-2020) | SE growers, ha, t | Terms not found | sv | 2020, 2023 | O | P3 |
| [INS TEMPO](http://statistici.insse.ro/shop/?page=tempo2&lang=ro&context=45) | Romania; blueberry category not confirmed | Terms not found | ro | ? | O | P3 |
| [Derzhstat](https://stat.gov.ua/) | Ukraine; blueberry table not confirmed | Terms not found | uk | ? | O | P3 |
| [ISTAT](http://dati.istat.it/Index.aspx?QueryId=33705) | Italy, mirtillo by region | Timeout | it | ? | OL | P3 |
| [Agreste SAA 2024](https://www.agreste.agriculture.gouv.fr/agreste-web/download/publication/publie/Chd2516/cd2025-16_SAA2024-R.Definitifs.pdf) | France; blueberry possibly combined with blackcurrant | Terms not found | fr | annual | OL | P3 |
| [Chambres d'agriculture](https://chambres-agriculture.fr/actualites/actualite/la-production-de-myrtilles-en-france) | FR basins, open soil share | Terms not found | fr | 2025 | O | P3 |
| [CSO Italy](https://www.csoservizi.com/indagine-di-cso-italy-su-fragole-e-piccoli-frutti-leggero-calo-delle-superfici-in-particolare-al-nord/) | Small-fruit area survey | Terms not found | it | 2026 | O | P3 |

### 4.3 Trade, shipments and prices

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [Eurostat Comext DS-045409](https://ec.europa.eu/eurostat/comext/newxtweb/) | Monthly CN8 08104050 trade by reporter and partner | CC BY 4.0 | en | since 1988 | O | P1 |
| [Geostat external trade](https://www.geostat.ge/en/modules/categories/35/external-trade) | Georgia exports (HS detail not tested) | Terms not found | en/ka | ? | O | P2 |
| [BLE/BMEL price report](https://www.bmel-statistik.de/preise/obst-und-gemuese) | Weekly wholesale prices by origin | Terms not found | de | weekly | O | P2 |
| [ZSRIR bulletins](https://www.gov.pl/web/rolnictwo/program-zsrir) | Weekly Polish market bulletins | Terms not found | pl | weekly | O | P3 |
| [Bronisze prices](https://wiescirolnicze.pl/ceny-rolnicze/firmy/bronisze-warszawski-rolno-spozywczy-rynek-hurtowy-sa/borowka-amerykanska/) | Daily domestic blueberry quotes | Terms not found | pl | recent | O | P3 |
| [AMI Saison Heidelbeeren](https://www.ami-informiert.de/fileadmin/shop/leseproben/50230.pdf) | Weekly season report | Paid | de | weekly | O | P3 |
| [IERiGZ](https://www.ierigz.waw.pl/) | Market analyses (blueberry content not found) | Terms not found | pl | ? | OL | P3 |

### 4.4 Damage, losses, aid and drought

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [JRC MARS Bulletin](https://joint-research-centre.ec.europa.eu/monitoring-agricultural-resources-mars/jrc-mars-bulletin_en) | Monthly dated weather anomalies by country | Public document; licence not found | en | 1992-; archive 2007- | O | P1 |
| [ARiMR frost aid](https://www.gov.pl/web/arimr/wsparcie-dla-uprawiajacych-owoce-rolnikow-ktorzy-poniesli-straty-spowodowane-przez-przymrozki-lub-grad) | Aid rules: 1 Apr-31 May frost, at least 70% loss | Terms not found | pl | 2023- | O | P2 |
| [IUNG SMSR](https://susza.iung.pulawy.pl/) | Drought risk by gmina for fruit bushes | Terms not found | pl | seasonal | O | P2 |
| [Gartenbau BB 2024](https://www.gartenbau-bb.de/aktuelles/himmlisch-heimische-heidelbeeren/) | April 2024: -3 to -7 C, 30-50% blueberry losses | Terms not found | de | 2024 | O | P2 |
| [MLUK Brandenburg aid](https://mluk.brandenburg.de/mluk/de/aktuelles/presseinformationen/detail/~25-09-2024-frosthilfen-fuer-obstbauern) | Frost aid: more than 30% loss, up to 80% paid | Terms not found | de | 2024 | O | P2 |
| [ESWD](https://eswd.eu/) | Point-dated hail and heavy rain | Registration; terms not read | en | ? | OL | P2 |
| [Copernicus EDO](https://drought.emergency.copernicus.eu/) | Drought indicators and reports | Terms not found | en | ? | O | P3 |
| [Plant protection platform PSA](https://www.agrofagi.com.pl/) | Dated phase and pest per point | Terms not found | pl | 2016- | OL | P3 |

### 4.5 Narrative and industry (RAG)

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [EastFruit](https://east-fruit.com/en/tag/georgia/) | Georgia, Ukraine, Serbia season news | Terms not found | en/ru/uk | 2021- | O | P2 |
| [UBA reports](https://uaberries.com/novyny/rynok/dynamika-vyrobnytstva-ta-zovnishnoi-torhivli-iahodamy-ukrainy) | Ukrainian berry market, monthly analytics | Terms not found | uk | 2025-2026 | O | P2 |
| [FreshPlaza Georgia](https://www.freshplaza.com/north-america/article/9814617/georgia-s-blueberry-exports-expand-as-sector-targets-eu-growth-and-new-markets/) | 2025 production and exports | Terms not found | en | 2025 | O | P3 |
| [British Berry Growers 2024](https://britishberrygrowers.org.uk/wp-content/uploads/2025/04/The-British-berry-industry-in-focus.pdf) | UK berry sector study | Terms not found | en | 2024 | OL | P3 |
| [AHDB SF 137](https://horticulture.ahdb.org.uk/sf-137-timing-of-nitrogen-applications-to-optimise-growth-and-yield-without-adversely-affecting-fruit-storability-and-frost-sensitivity) | Duke under tunnel, Aurora outdoors, frost sensitivity | Terms not found | en | 2012-2015 | O | P3 |
| [Ukraine blueberry methodology 2022](https://www.iogu.gov.ua/uploads/edition/lochina_tipograf_31_01_22.pdf) | Official growing and protection guidance | Terms not found | uk | 2022 | O | P3 |

### 4.6 Weather stations and gridded data

| Source | What it contains | Access / terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [IMGW dane publiczne](https://danepubliczne.imgw.pl/) | Hourly synoptic data, API | Free with attribution | pl | 1966-2026 | O | P1 |
| [DWD CDC hourly](https://www.dwd.de/EN/climate_environment/cdc/cdc_node_en.html) | Hourly T and RH by station | CC BY 4.0 | de/en | from 1950 at some stations | O | P1 |
| [FMI open data](https://en.ilmatieteenlaitos.fi/open-data) | Hourly T, Tmin and RH via WFS | CC BY 4.0 | en/fi | sampled 2024 | O | P1 |
| [KNMI](https://www.knmi.nl/nederland-nu/klimatologie/uurgegevens) | Hourly station data | CC BY 4.0 | nl/en | ? | O | P2 |
| [MIDAS Open (CEDA)](https://help.ceda.ac.uk/article/4982-midas-open-user-guide) | UK station data | OGL; CEDA account | en | annual release | O | P2 |
| [E-OBS](https://surfobs.climate.copernicus.eu/dataaccess/access_eobs.php) | 0.1 deg daily grid | Non-commercial research only | en | ? | O | P2 |
| [NIBIO LMT](https://lmt.nibio.no/) | Norwegian agromet stations | Terms not found | no | ? | O | P3 |
| [SMHI API](https://opendata.smhi.se/) | Swedish observations | Terms not found | sv | ? | O | P3 |
| [MET Norway Frost API](https://frost.met.no/index.html) | Norwegian observations | NLOD and CC BY 4.0 | en | ? | O | P3 |
| [api.meteo.lt](https://api.meteo.lt/) | Lithuanian observations | CC BY-SA 4.0 | lt | ? | O | P3 |
| [Estonian weather service](https://www.ilmateenistus.ee/), [ANM Romania](https://www.meteoromania.ro/), [RHMZ Serbia](https://www.hidmet.gov.rs/), [NEA Georgia](https://nea.gov.ge/), [Meteo-France open data](https://meteo.data.gouv.fr/) | National services; open download not confirmed except France | Terms not found | various | ? | O | P3 |
| [Ukrainian Hydromet Center](https://meteo.gov.ua/) | Unreachable | n/a | uk | ? | OL | P3 |

### 4.7 Top 10 sources: what the sample showed

1. **VBB trial PDF.** Figure 7 is a cultivar-by-site-by-year table of the "5% first flower open" date. Examples: Bluecrop at DM 22, 18, 26, 23 and 27 April for 2008-2012; Duke at BG 16, 17, 24, 21 and 23 April. Figure 8/9 gives bloom length in days (13-31). Figure 10 gives bloom-to-first-harvest days. Further figures give production per plant (g), 100-berry weight and Brix.
2. **Luke 0400_puutar** (API JSON). Columns: Year, Region, Species, Number of enterprises, Area total (ha), Harvesting area, Young population, Crop-yielding population, High tunnel cultivation (ha), Yield (1,000 kg). Suppressed cells show "..".
3. **GUS 2024 xlsx, table 110.** Columns: area in ha, yield in dt/ha, harvest in dt, then 2023 = 100 indices for each. There is one row per voivodeship plus Polska. A footnote to tables 122-124 says blueberry was inside "other" until 2019.
4. **Destatis.** The 2025 HTML table lists Kulturheidelbeeren with Betriebe, Anbauflaeche (ha) and Erntemenge (t). The 2022 xlsx has one sheet per Land (NI1, BB1 and so on) with farms, area, dt/ha and dt.
5. **Eurostat apro_cpsh1.** Dimensions are freq, crops, strucpro, geo and time. The strucpro codes are AR_THS_HA, MAR_THS_HA, HUMD_EU_PC, HPRD_HUMD_EU_THS_T and YLD_HUMD_EU_T_HA. Status flags are 'n' and 'e'.
6. **Comext DS-045409.** Dimensions are freq, reporter, partner, product, flow, indicators and time (monthly). The product label is "Fresh fruit of species Vaccinium macrocarpum and Vaccinium corymbosum".
7. **IMGW.** The folder `terminowe/synop/` holds per-period zips from 1966_1970 to 2026, with `s_t_format.txt` and a header CSV. `wykaz_stacji.csv` lists stations. The live synop API returns JSON fields id_stacji, stacja and data_pomiaru, among others.
8. **FMI WFS.** It returns BsWfs:Time, ParameterName and ParameterValue triples, for example TA_PT1H_AVG, TA_PT1H_MIN and RH_PT1H_AVG hourly at Turku.
9. **JRC MARS April 2024.** The issue has these sections: areas of concern, meteorological review (1 March to 13 April), forecast, fAPAR remote sensing, sowing, country analysis with dated anomalies, and yield tables.
10. **Doradca Jagodowy 2018 bulletin.** It has an observation date, cultivar, BBCH code, a "Suma aktywnych temperatur (SAT 5 C)" of 337.3 on 21 April, a 9-day forecast of the stage, frost-injury photos, and disease thresholds (grey mould above 5% of shoots, anthracnose above 10%).

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON. IBO record fields are kind, topic, period, crop_context, evidence_type, geography and citations.

| Job | Output | Exact fields | Effort | Pri |
|---|---|---|---|---|
| ECNE-01 Dutch NHB cultivar phenology | cultivar table | site, lat, lon, cultivar, class, year, first_open_flower_date, bloom_period_days, days_first_bloom_to_first_harvest, production_g_per_plant, frost_note, citation page/figure | 1.0 | P1 |
| ECNE-02 Naantali test pack | station table | Luke region-year enterprises, area_ha, high_tunnel_ha, yield_t; FMI hourly TA avg/min, RH; half-high freeze threshold; harvest window; citations | 1.5 | P1 |
| ECNE-03 Poland voivodeship and gmina layer | time series table | year, voivodeship TERYT, gmina TERYT, area_ha, yield_dt_ha, harvest_dt, yield_index, declared_area_ha, table/sheet citation | 1.5 | P1 |
| ECNE-04 National production series | time series table | ISO2, Land/region, year, area_ha, production_t, yield, farms, status flag, source | 1.0 | P1 |
| ECNE-05 Monthly trade curves | time series table | reporter, partner, CN8, flow, month, quantity, value, peak month, 10/50/90% weeks | 1.0 | P1 |
| ECNE-06 MARS bulletin claims | claim records | kind, topic=weather, period, geography, crop_context, evidence_type=agency_bulletin, anomaly type, phenology-advance statement, citations | 3.0 | P1 |
| ECNE-07 Poland 2024-2025 frost events | event records | kind=event, period (night dates), geography, cultivars and stage, loss estimate and source, station minimum, citations | 1.5 | P2 |
| ECNE-08 Germany 2024 frost package | event records | period, Land, night minimum, loss share, aid rule, Land yield change, citations | 1.0 | P2 |
| ECNE-09 Polish dated stage records | claim records | observation date, voivodeship, cultivar, BBCH, temperature-sum value and definition, citations | 2.0 | P2 |
| ECNE-10 Station bias pack | station table | station id, lat, lon, elevation, UTC time, T, Tmin, RH, precip, paired cell, monthly Tmin bias, frost hits and misses | 2.0 | P1 |
| ECNE-11 Cool-climate cultivar traits | cultivar table | cultivar, class, bloom order, ripening order, freeze threshold and exposure, heat-requirement value and unit, hardiness rank, country, citations | 1.5 | P2 |
| ECNE-12 Eastern Europe and Georgia narrative | claim records | kind, topic, period, geography, crop_context, evidence_type=industry_narrative, citations | 2.0 | P2 |
| ECNE-13 IUNG drought by gmina | event records | season, period, crop group, gmina, drought flag, water-balance class | 1.0 | P3 |
| ECNE-14 Weekly price season start and end | time series table | week, market, origin, price range, first and last domestic quote week | 1.5 | P3 |

**How the RAG jobs run (ECNE-06, -09 and -12):** they follow the IBO design rules. An LLM proposes records offline. A human checks each one against the cited page. Document, claim and event records stay separate. Raw text is not exposed.

## 6. How each source maps to model checks

### 6.1 European cool-climate phenology evidence

**Northern highbush, dated observations.** The table compares observed dates with the `stage_thermal_v3` model.

| Evidence | Place, years | Observed | Model (nearest benchmark) |
|---|---|---|---|
| [VBB trial](https://edepot.wur.nl/288774), first open flower (5% clusters) | Melderslo (DM) and Well/Weeze (BG), 2008-2012 | Duke 11-22 Apr (DM), 16-24 Apr (BG); Bluecrop 18-27 Apr (DM), 19-26 Apr (BG); Draper 19-30 Apr; Liberty 21-30 Apr; Ozarkblue 22-29 Apr; Elliott 22-29 Apr; Aurora 25 Apr-3 May | Vechta flowering start 24 May |
| VBB, bloom length | same | 13-31 days; Duke 13-22, Bluecrop 14-22 | Vechta flowering start to end: 29 days |
| VBB, first flower to first harvest | same | Duke 61-68 d; Bluecrop 64-79 d; Draper 63-79 d; Liberty 78-90 d; Ozarkblue 72-87 d; Aurora 93-106 d; Elliott 98-107 d | Vechta flowering start to harvest start: 60 d (24 May to 23 Jul) |
| [Doradca Jagodowy](https://doradcajagodowy.pl/blog/borowka/borowka-poczatek-kwitnienia-odmian-wczesnych-iwt-9-21-04/) | Lubelskie, 2018 | Patriot first flowers 20 Apr; on 21 Apr early cultivars at BBCH 60 and mid-early at BBCH 53-54, with SAT5 = 337.3; mid-early bloom expected about 14 days later | Lublin budbreak 12 May, flowering start 25 May |
| [Bozek 2009](https://doi.org/10.5586/aa.2009.011) | Niemce near Lublin, 2001-2004 | Bloom in May (3 yrs), May-June (2004); 14-21 days | Lublin flowering 25 May to 21 Jun |
| IO via [Sady Ogrody](https://www.sadyogrody.pl/owoce/101/borowki_2022_jakie_kwitnienie_i_zawiazanie_owocow,30613.html) (benchmark source) | Poland, 2022 | Bloom in the second half of May | as above |
| [Jagodnik](https://jagodnik.pl/borowki-po-przymrozkach-2024-do-70-strat-w-niektorych-regionach/) | Poland, 22-23 Apr 2024 | Duke in full bloom; Bluecrop starting bloom | as above |
| [LWK via Fruchthandel](https://www.fruchthandel.de/news/norddeutsche-heidelbeerernte-nimmt-fahrt-auf); benchmark 2024 release | Lower Saxony | Main open-field harvest mid-July to early August; Duke from week 25 in 2024 | Vechta harvest start 23 Jul |
| [Cacak study](https://www.researchgate.net/publication/351078926_Fertilization_biology_of_'Reka'_highbush_blueberry) (SO) | Serbia | Bloom from the last third of April to mid-May | no benchmark site |
| [Banat paper](https://doi.org/10.3390/agronomy12112605) (abstract) | Romania, 2020-2022 | Stage dates vary by up to 51 days (BBCH 87) and 25 days (BBCH 51, 59) across varieties and years; CV across years 6.5-21.1% | no benchmark site |
| [Agrion Boves](https://rivistafrutticoltura.edagricole.it/featured/mirtillo-gigante-americano-coltivazione-piemonte/) | Piemonte, 590 m | Duke ripens about 25 June on average | no benchmark site |
| [EastFruit](https://east-fruit.com/en/news/blueberries-are-ripe-the-harvest-of-the-most-expensive-berries-begins-in-georgia/) | Western Georgia, 2021 | Harvest start about 26 May; season 1-2 weeks late after a cold spring (search extract) | no benchmark site |

**What this says about the model** [inference]:

- **Bloom timing.**
  - The model starts flowering on 24-25 May at both European benchmark cells.
  - Dated first-flower observations are 3 to 6 weeks earlier: mid to late April in the Netherlands and western Poland, and around 20 April in an early Lublin year.
  - May-only statements from older or trade sources fit model May bloom, but they describe the whole bloom period, not its start.
  - So the "two weeks late" figure in the benchmark understates the lag at bloom start.
- **Bloom to harvest.**
  - Model flowering start to harvest start is about 56-60 days, close to the observed 61-68 days for Duke.
  - But the model reaches that interval in June-July heat.
  - If bloom moves a month earlier into cooler late April, a fixed 633 GDD (base 7 C) will take longer than 60 days.
  - So bloom and fruit-development constants must be refitted together, against the Dutch dates and nearby station weather (KNMI).
- **Cultivar class.** Late cultivars (Aurora 93-106 days, Elliott 98-107 days) need a separate class. The Dutch report warns that Aurora may not fully ripen in the north.

**Half-high and Finland (the Naantali pin):**

- **Production exists.** Southwest Finland had 44 enterprises, 32 ha and 68 t in 2024, and 47 enterprises, 34 ha and 73 t in 2025 ([Luke](https://statdb.luke.fi/PxWeb/pxweb/en/LUKE/LUKE__maa__puutar/0400_puutar.px/)). Finland-wide high-tunnel area was 5 ha of 111 ha in 2025.
- **Cultivars and timing.** The main cultivars are North Blue, North Country, Aino, Alvar, Arto and Bluecrop. Bloom is in "early summer" and ripening is late summer ([HMLry](https://hmlry.fi/laji-info/pensasmustikka/)). Aino ripens in early August over 2-3 weeks; Alvar is about one week earlier and Arto about one week later. The usual season runs from the end of July to early September, with an average yield of about 2,000-2,200 kg/ha ([Pousi 2024](https://satakunta.mtk.fi/documents/d/mtk-satakunta/pousi_11-4-2024hml-pdf)).
- **Freeze thresholds.** Aino and Alvar flowers took -1 C and -3 C for up to 8 h with little damage. At -5 C, 2 h caused heavy damage and berry numbers fell to 1-2% of control ([MTT](https://jukuri.luke.fi/server/api/core/bitstreams/4e7588f2-2a3e-4423-9ad8-e3c858470232/content)).
- **Northern heat requirements** ([NLR](https://www.nlr.no/kunnskap/fagartikler/frukt-og-baer/ostlandet/dyrking-av-hageblabaer)). Most cultivars need 7,000-8,000 growing degree hours from budbreak to bloom, and 18,500-34,000 GDH from bloom to harvest. No base temperature is given. Divided by 24 that is about 290-330 and 770-1,420 degree-days on an unknown base [inference]. Use these only as relative sizes.
- **Why Naantali fails** [inference]. The v3 chain needs 150 + 85 + 633 GDD (base 7 C) to harvest start, and 1,242 GDD after flowering start to harvest end. At 60.5 N, a stage misses its heat requirement within 300 days in 14 of 15 winters. Finnish harvest windows show real fruit ripening by August. So the SHB-derived harvest-end sum is the most likely blocker.
- **Proposed test.** A cool-climate profile should take its harvest-start and harvest-end targets from the Finnish window and the Dutch bloom-to-harvest days. Test it with FMI hourly data before any code change.

**Baltics:** a western Latvia trial (2007-2009) found all six highbush and four half-high cultivars suitable except Chandler, whose season was too late ([ISHS 926_26](https://ishs.org/ishs-article/926_26/)). A search extract of a Dobele proceedings paper ranks Polaris, Chippewa, Northblue and Patriot as the most winter-hardy and Duke as the least.

### 6.2 Source-to-model mapping

- **Budbreak and bloom timing:**
  - VBB, Doradca Jagodowy, Bozek, IO notes, Banat, Czech, PEP725 and MARS phenology-advance statements.
  - Method: compare modelled flowering start with observed first-flower dates for 2010-2012 (VBB) and 2018 (Lublin). Report error in days per cultivar class, and refit budbreak and flowering GDD using KNMI and IMGW station temperature.
- **Harvest timing:**
  - VBB bloom-to-harvest days, LWK press statements, Comext monthly exports, Geostat exports, BLE, ZSRIR and Bronisze prices, and Finnish harvest windows.
  - Method: compare modelled harvest start with the first month above 10% of the annual export volume, by year. The Polish export peak in July 2024 against August in 2025 should show as an earlier modelled season in 2024.
- **Bud and flower freeze:**
  - GUS table 110 yield indices, Destatis Land yields, the GUS final-estimate text, ARiMR aid rules, Jagodnik and Gartenbau BB 2024 reports, MLUK aid, VBB 2009 and 2011 frost notes, and MTT half-high thresholds.
  - Method: check that 2024 shows a flowering-freeze flag in Dolnoslaskie, Opolskie, Lubelskie and Brandenburg cells. Check that IMGW and DWD station minima catch the 22-23 April 2024 night that the grid may miss.
- **Fruit frost:** the GUS text and the IBO May 2024 record. Method: separate April bloom frost from May green-fruit frost.
- **Chill and dormancy:** IMGW, DWD, FMI and E-OBS. Method: the chill model is not the limiting factor here, since chill is far above any NHB requirement (3,000-3,600 h). Use stations only to correct Tmin bias.
- **Water and drought:** IUNG SMSR by gmina and EDO. Method: overlay drought periods with model fruit-development windows.
- **Harvest rain and hail:** ESWD point reports and MARS. Method: check modelled harvest heavy-rain months against reported events in Serbia, Romania and Poland.
- **Disease and pollination:** Doradca Jagodowy thresholds, NLR stigma receptivity (5-8 days) and FMI, DWD and IMGW hourly RH.
- **Location mapping:** Eurostat, GUS, ARiMR, Destatis, CBS, Defra, SSB, Luke and Jordbruksverket.
- **Management:** Luke high-tunnel area, IBO structure share, Chambres d'agriculture (95% open soil) and AHDB (Duke under Spanish tunnel).
- **Cultivar classes:** VBB, HMLry, MTT, NLR and Latvia.

## 7. Access, licensing and language risks

- **Clear open licences:**
  - CC BY 4.0: Eurostat, CBS, SSB, Luke, FMI, DWD and KNMI.
  - GUS: free use with attribution.
  - IMGW: free with attribution and a note if processed.
  - Destatis: Datenlizenz Deutschland 2.0.
  - MET Norway: NLOD plus CC BY 4.0.
  - api.meteo.lt: CC BY-SA 4.0. The ShareAlike clause may bind derived public layers.
- **Use with care:**
  - E-OBS is limited to non-commercial research and education. Keep it internal.
  - VBB (c) 2013, HMLry and Doradca Jagodowy are all rights reserved. Doradca Jagodowy is also paid. Store derived numbers with citations and ask the owners before any public table.
  - AMI and the ISHS papers are paid.
- **Terms not found:** ARiMR, IUNG, MLUK, Jagodnik, EastFruit, UBA, FreshPlaza, LWK press, MARS (the JRC record says it is a public document that may be shared), ESWD, NIBIO LMT and SMHI. Confirm terms before public display.
- **Access walls:**
  - GENESIS API needs a free account; the guest login was rejected.
  - PEP725 needs a free login.
  - MIDAS Open needs a CEDA account.
  - ESWD needs registration and returned HTTP 403 to scripts.
  - MDPI, the Agri4Cast archive and the JRC PDF host block scripts; the reader tool worked for JRC.
  - ResearchGate returned HTTP 403.
  - pbsociety.org.pl returned HTTP 500.
  - The ARiMR tool host did not answer scripts.
- **Language:** core evidence is in Polish, Dutch, German and Finnish. Extraction needs a reviewer who reads these, or an LLM translation that a human then checks. Georgian official sources were not reached in Georgian.
- **Date pitfalls:** Jagodnik slugs can carry a different date from the post (a slug ending "27-04-2024" was dated 2025-04-28). Always take dates from the body text.

## 8. Gaps

- **Poland:** no Instytut Ogrodnictwa primary document with a Lubelskie calendar or cultivar bloom table was found. inhort.pl did not respond to scripts. Gmina damage-commission protocols for 2024 are not published online. Only the aid rules are.
- **Germany:** no LWK Niedersachsen trial report (Versuchsbericht) with blueberry bloom dates was found. The LKSH 2024/25 report only names the testing. The Saxony and Lower Saxony frost-aid pages are gone (HTTP 404 and 410). Vereinigte Hagel loss data are not public [inference].
- **DWD:** no Vaccinium observations. PEP725 Vaccinium species and countries are unconfirmed without a login.
- **Finland:** no dated bloom or harvest observations for any Finnish blueberry site were found, only windows. Luke's Piikkio research station (Kaarina, near Naantali) appeared only in search results about fruit sampling, not phenology.
- **Serbia, Romania, Ukraine, Georgia, Italy and France:** no confirmed official blueberry table for Serbia (RZS), Romania (INS), Ukraine (Derzhstat) or Italy (ISTAT timed out). France combines blueberry with blackcurrant (per search summary). No open historical weather download confirmed for Romania, Serbia, Ukraine or Georgia.
- **Baltics:** Latvian and Lithuanian research full texts were not retrieved. National statistics offices were not opened; Eurostat covers LT and LV.
- **Market data:** no open weekly blueberry price series was confirmed. BLE and ZSRIR blueberry rows are unverified, and AMI is paid.
- **Full texts not read:** Banat (2020-2022) and Czech (2020-2024) phenology tables. The open licence allows use once retrieved by a person with a browser.
- **Insurance:** no public insurance loss data for blueberries in any country in scope.
- **IBO coverage:** no IBO records exist for NL, GB, FI, SE, NO, the Baltics, UA, GE, IT or FR.

## 9. Ranked top 10 actions for this scope

1. **Run ECNE-01:** extract the VBB Dutch trial dates and pair them with KNMI hourly data. Report the model bloom-start error in days for 2010-2012 per cultivar (1.5 days with KNMI).
2. **Run ECNE-02:** build the Naantali test pack. Use FMI hourly Turku data from 2010-2025 and Luke regional counts, and draft a half-high profile whose harvest targets match the end of July to early September window. Discuss it with Paul under the approved cool-climate work.
3. **Run ECNE-03:** load GUS table 110 for 2020-2025 and test whether the 2024 voivodeship yield drops line up with modelled flowering-freeze flags.
4. **Run ECNE-10 for pl-lublin and de-ni-vechta:** pull IMGW and DWD hourly station data and measure Tmin bias and missed frost nights, starting with 22-23 April 2024.
5. **Run ECNE-05:** pull Comext monthly CN 08104050 for 2010-2025 and derive the export peak month per country and year as a harvest-timing check.
6. **Run ECNE-06:** extract dated weather claims from MARS bulletins for 2010-2025 for the scope countries, with human review.
7. **Retrieve the Banat and Czech full texts** (CC BY 4.0) by hand and add their BBCH dates to the cultivar table (ECNE-11).
8. **Create free accounts** for PEP725 and GENESIS (a human decision). Check whether PEP725 Vaccinium has Finnish, Latvian or Polish records.
9. **Write evidence records** for Polish and German 2024 frost events (ECNE-07, ECNE-08) and for Georgia and Ukraine (ECNE-12), which have no IBO records.
10. **Ask Instytut Ogrodnictwa and LWK Niedersachsen** whether they will share cultivar bloom and harvest dates from their collections (Skierniewice, Langfoerden). Contacting them is a human task. No form was submitted in this research.
