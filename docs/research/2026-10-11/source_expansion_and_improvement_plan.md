# Astra review, source expansion and whole-setup improvement plan

Date: 11 October 2026. Prepared by the coordinating agent (Claude Opus 5.5) with 17 parallel research agents. This is a research and planning package. It changes no model constant, API behaviour or dashboard behaviour. It corrects five factual errors in `docs/APP_USER_GUIDE.md` and one figure in a regional report (section 2.5).

## How to read this package

| File | What it holds |
|---|---|
| This file | Bottom line, review of Astra's work, cross-region findings, region-by-region summaries, the ingestion design summary, the improvement roadmap, decisions, rights rules and verification |
| [review/astra_science_review.md](review/astra_science_review.md) | Astra's risk gate, planting window, phenology review, 20 source checks and user-guide accuracy |
| [review/astra_ibo_evidence_review.md](review/astra_ibo_evidence_review.md) | 53 IBO registry records checked against their pages, event-check critique, schema v2 proposal |
| [review/astra_engineering_review.md](review/astra_engineering_review.md) | Code review of Astra's software: 21 findings by severity |
| [architecture/rag_ingestion_architecture.md](architecture/rag_ingestion_architecture.md) | Ingestion and retrieval design: registry, jobs, schemas, retrieval, evaluation, 44-day plan |
| `regions/*.md` and `regions/*.sources.json` | Ten regional source reports and machine-readable source lists |
| `global/*.md` and `global/*.sources.json` | Trade and market; phenology, weather, land use and literature; losses and validation |
| [source_catalog.json](source_catalog.json) | Merged index of all 824 unique sources and 174 extraction jobs |

## 1. Bottom line

1. **Astra is the OpenAI Codex model `gpt-6-astra`.** It worked in this project between 15 September and 5 October 2026. It authored 14 commits and built two more deliverables that other models committed: the growing-cycle ruler and the Regional evidence tab. Its work covered the v2 risk gate, the planting window, the hourly-archive connection, the whole map-first UI, the 43-source phenology review, the IBO report collection, the evidence registry and the user guide.
2. **Astra's work is careful and mostly correct, with four material problems.**
   - The IBO frost checks for Chile and New Zealand used the wrong window and the wrong grid cell, so they wrongly reported "freeze not represented".
   - The risk gate saturates. Harvest heavy rain ranks at 34 of the 41 sites that have a winter calendar.
   - Nine sites lose their winter calendar because chill fails, yet chill shortfall never reaches the Overview.
   - The planting window overrides Paul's requirement without a recorded sign-off and rests on home-garden guides.
   No reviewer found a result-changing code bug. The engineering risks are operational: the API runs only under tmux, has a single busy lock, has no cache, and lacks Host and Origin checks.
3. **We found 824 distinct sources in 69 countries.** 686 were opened and checked, 120 were only partly reachable and 18 were seen only in search results. 280 are blueberry-specific, and 195 more contain blueberry rows inside broader data. The sources feed 174 defined extraction or RAG jobs worth about 287 builder-days in total (168 days for the P1 jobs).
4. **The largest upgrade is ground truth, not more narrative.** The project has had no loss data and no dated field observations. It now has both:
   - county-by-month US insurance losses since 1989;
   - station networks next to most benchmark sites;
   - dated stage records in theses, plant patents, extension bulletins and national weather-service bulletins;
   - weekly or monthly harvest-timing series by region.
5. **The station evidence shows the grid misses spring frosts by 5 to 8 °C.**
   - Chile: Coihueco −2.0 °C on 31 October 2022 against about +5 °C in the grid cell.
   - New Zealand: Hamilton −2.9 °C on 7 October 2022 local time against 5.15 °C in the grid cell.
   - Tasmania: an airport station 30 km from Penguin logged 555 chill hours, against 58 modelled. Bias correction and station checks therefore come before any phenology tuning.
6. **Do these next, in order:**
   - stabilise the service (systemd or a guarded tmux, a result cache, Host checks);
   - implement the approved scan accounting;
   - re-run the Chile and Waikato checks with stations;
   - build the RMA and station truth tables;
   - pre-register the US freeze validation;
   - then use the new dated stage records to fit cultivar classes, starting with the approved cool-climate settings.
   Sections 6 and 7 give the plan and the decisions it needs.

## 2. What Astra did, and how good it was

### 2.1 Deliverables

Commits were attributed by matching commit times to the model active in the session log. Every commit uses the same Git identity.

| Date | Commit | Deliverable | Verdict from this review |
|---|---|---|---|
| 15 Sep | ced0aaf (committed by Fable) | Growing-cycle ruler (`dist/cycle.js`) | Works. One display mismatch: the bud lane starts at the chill date, while the bud-freeze metric covers only budbreak to flowering (engineering finding L11) |
| 22 Sep | 7f293c6 | `stage_risks_v2`: 50% recurrence gate in at least 12 winters, one disease family, exposure-only families, regional planting window | Correctly coded. Weak as a ranking tool, and the planting decision is not signed off (section 2.2) |
| 22 Sep | df73699, 97c8a3a | Map-first UI rebuild, wheel zoom | Works. Keeps an undocumented in-browser agent tool hook (`document.modelContext.registerTool`, `dist/app.js:815-822`) that existed before; decide whether to keep it |
| 22 Sep | f33025f | Read-only hourly archive adapter (`hourly_archive.py`) | Correct. The checksum reader verifies the same bytes it returns |
| 23-24 Sep | 169ab13, cc399b0, bd7e858, 6a5abe6, 8d7b317, 80cecea | English-first MapLibre map, local place lookup, logo, search, responsive layout, header simplification | Works. Maintainability debt: 823-line `app.js` with dense one-line functions |
| 25 Sep | 8bb4acc | Global phenology review (43 sources) and calendar audit | Strong research hygiene. 17 of 20 sources fully support its claims and 3 partly. Section 1 and the audit JSON still describe v2 as current |
| 5 Oct | 37ce6ab | IBO report collection and integration decision | Sound design. The event checks have a wrong window (Chile) and a coastal cell (Waikato) |
| 5 Oct | 5779365 (committed by Opus 5.5) | Regional evidence tab, 91-record registry, polygon-ID matching | 47 of 53 checked records supported, 5 partly, 1 page mismatch, none unsupported. The registry does not yet follow Astra's own claim and event design |
| 5 Oct | 4365013, 20eebfc | Approval record, simplified-English user guide | The guide is accurate on nearly all thresholds. Five errors were fixed today (section 2.5) |

### 2.2 Science (full review: [astra_science_review.md](review/astra_science_review.md))

- **Risk gate.** The gate is coded as documented, but four problems remain.
  - **One-day events saturate.** Every family except the pollination gap counts a winter as an event after one qualifying day. Over a roughly 41-day harvest window, humid sites hit the event almost every year. At the 41 saved sites with a winter calendar, harvest heavy rain ranks at 34 and disease weather at 26 (coordinator recomputation, 11 October).
  - **The 50% gate is noisy at 15 winters.** A family with a true 40% recurrence still passes it with probability 0.21; the binomial arithmetic was checked.
  - **Failed winters leave the denominator.** This contradicts Astra's own phenology review, line 348.
  - **One constant does two jobs.** The v3 chill clock reuses the 12-winter constant for a different purpose, so nine saved sites (five in Florida, plus Tzaneen and Ovalle) lose their winter calendar while chill shortfall stays below 50%. Chill shortfall then never appears on the Overview.
- **Planting.** Rejecting Paul's "105 to 30 days before budbreak" rule as biology is justified, because no source supports it. But Paul asked for a window "not computed independently", no sign-off is recorded, and the replacement rests on home-garden guides. UF/IFAS HS1525 (July 2026, commercial) advises planting in the early-spring and fall root-growth periods. It also says newer UF cultivars can crop within 12 months of planting; the coordinator verified both statements in the HS1525 text. Arbitrary pins never receive planting guidance (`location_api.py:121-122`).
- **Phenology review.** Astra's corrections of earlier project claims hold up. Some recommendations conflict with later v3 work: replacing the constants with new universal values, and declaring the Kovaleski formula a typo instead of confirming it with the authors. Several public dated stage tables that Astra cited were never extracted: Lyrene 2008, the UGA release tables, Campa and Ferreira, SERIDA, Antunes and the Maule Table 4.

### 2.3 Regional evidence and IBO work (full review: [astra_ibo_evidence_review.md](review/astra_ibo_evidence_review.md))

- **Registry accuracy is good.** Of 53 records checked against the server's page text, 47 are supported, 5 partly and 1 has a page mismatch; none is unsupported. An automated sweep of every number in all 91 summaries found one number missing from its cited pages. The errors come from curator-added context, such as crop type and the scope of a practice, and from loose dates.
- **The event checks were wrong in method, not just inconclusive.** The coordinator re-ran both cases on the stored archive:
  - **Chile.** The check used 1 to 30 November 2022. The Chillán grid cell, which contains Coihueco, reached +2.24 °C on 30 October UTC; the Andean cell east of it reached −6.15 °C. Stations recorded −2.0 °C at Coihueco and −2.2 °C at Linares on 31 October (RAN Agromet; DMC October 2022 bulletin, verified).
  - **New Zealand.** The selected cell (−38.0, 175.0) gave +5.15 °C on 6 October UTC. The inland neighbour cell gave +0.06 °C, and Hamilton Airport recorded −2.9 °C on 7 October local time, the lowest October minimum since 1946 (NIWA summary, verified).
  The old results should be re-labelled "window or cell choice inconclusive" and the checks repeated with stations.
- **The design is not yet implemented.** The registry has no separate claim records, no structured quantities, no edition revisions, no per-record reviewer and no allowed-use field. Every `event_id` is unique, so the UI's "same event" grouping never runs.
- **Geography is safe but coarse.** Admin-1 polygons only. Curicó receives the "Linares to Chillán" frost; Kenitra receives no northern Morocco records.
- **Inventory gaps.** No legitimate public full copy of IBO 2021 or 2024 exists; both sit behind a free IBO form that a person must fill in. Missing from Astra's inventory:
  - 15 IBO Summit 2025 presentations;
  - 11 Morocco Berry Conference 2025 presentations;
  - a 2023 summit deck.
  Scribd uploads of the 2024 and 2025 reports are marked "All Rights Reserved" and should be logged as rejected sources.

### 2.4 Engineering (full review: [astra_engineering_review.md](review/astra_engineering_review.md))

No critical defects and no result-changing bug. Missing data stays missing in both Python and JavaScript, and stale responses are guarded. Findings: 1 high, 6 medium and 13 low. Some predate Astra and are listed because they affect the whole setup.

- **High.** The API runs only as a tmux session. Nothing restarts it, and tmux failed on 5 October when the root disk was full. The session log shows `couldn't create directory /tmp/tmux-1003 (No space left on device)`.
- **Medium:**
  - one BUSY lock with no deadline, cancel or result cache;
  - no Host or Origin check in the Python API;
  - the preview proxy lets cross-site GETs start analyses;
  - `sensitivity()` recomputes the primary v3 profile on every request;
  - the evidence validator has no length limit or control-character stripping before any RAG use;
  - test gaps: proxy, HTTP handler, indexed hourly path, eastern longitudes, leap years, JavaScript races.
- **Low:** URL scheme checks, CSP headers, log rotation, UTC versus local-solar day mixing near the date line, a leap-year shift of up to one day in median dates, thresholds hard-coded outside profiles, duplicated helpers.

### 2.5 What the coordinator checked and changed today

Checks run by the coordinator, not only by agents:

| Check | Result |
|---|---|
| Server test suite (deployed `code/`) | 141 tests passed. The repository also has 141 test definitions, so the handover's earlier "140" was a miscount |
| Deployed code against the repository | `production.py`, `location_api.py`, `hourly_archive.py`, `planting.py` and `benchmark.py` are identical (SHA-256) |
| Chile and Waikato grid minima | Reproduced the review's values exactly (section 2.3) |
| USDA RMA 2022 cause-of-loss file | Downloaded to the server's project drive and deleted afterwards. 217 blueberry rows (crop code 0012) in 8 states; USD 77.65 million indemnity, of which freeze USD 49.08 million; Georgia March freeze USD 30.51 million; Bacon County USD 11.84 million in March freeze out of USD 14.63 million for all causes |
| NOAA GSOD station summaries | The Miami 2025 file ends on 27 August 2025 and no 2026 directory exists. The successor product GHCNh is online. Use GHCNh, not GSOD or ISD, for recent station data |
| UF/IFAS HS1525 | Confirms planting in the early-spring and fall root-growth periods and a marketable crop within 12 months for newer UF cultivars |
| DMC, NIWA and SENAMHI documents | Linares −2.2 °C (October 2022); Hamilton Airport −2.9 °C on 7 October 2022; SENAMHI "Cultivo de Arándano" bulletin with field stages at Cayaltí, Chao and San José |
| Chilean orchard census licence | CC BY, block-level fields: commune, species, variety, planting year, irrigation method, area |
| FreshPlaza robots.txt | `Content-Signal: search=yes, ai-train=no, ai-input=no`; AI crawlers are blocked |

Changes made:
- Corrected five statements in `docs/APP_USER_GUIDE.md`: planting for arbitrary pins, the HS1525 note, the provenance of the GDD constants, the local-time approximation and three screen labels.
- Corrected the Bacon County figure in `regions/us-southeast.md` and its JSON note.
- Removed nine Python packages that research agents installed into the repository `.venv`.
- Deleted 56 research temporary files and `/tmp/ibo` from the local machine. Some agent temporary files remain in `/tmp`, because they could not be told apart from other projects' files; macOS clears them on restart.

## 3. What new information exists: the cross-region view

### 3.1 Totals

| Measure | Value |
|---|---|
| Source entries listed by agents | 861 |
| Unique sources after merging repeated URLs | 824 |
| Countries covered | 69 |
| Verification | 686 opened, 120 partly reachable, 18 search only |
| Access | 721 open, 49 free registration, 8 on request, 24 paid, 22 restricted |
| Blueberry relevance | 280 blueberry-specific, 195 with blueberry rows, 62 berries aggregated, 287 general weather or disaster |
| Priority (unique sources) | 201 P1, 305 P2, 318 P3 |
| Extraction and RAG jobs | 174 (287 builder-days; P1 jobs 168 days) |

Largest categories: industry reports 155, loss or damage 151, weather stations 132, management practice 112, production statistics 108, shipment or export series 104, research literature 99, phenology observations 95, cultivar traits 95.

### 3.2 The ten source families that matter most

Ordered by what they do for the model. Each family lists representative sources; every region report gives the full list with fields and access.

1. **Insurance losses by place, month and cause (validates the risk families).**
   - [USDA RMA cause of loss with month of loss](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss): blueberries are crop code 0012, with data since 1989 by county, month and cause (freeze 42, frost 41, excess moisture 31, heat 12, hail 21, insufficient chilling 45, plant disease 81).
   - The companion RMA business files split insured acres into highbush and rabbiteye, and into fields with and without frost protection, which a fair test needs as denominators.
   - Elsewhere: Mexico's [CNSF insurance statistics](https://datos.gob.mx/dataset/informacion_estadistica_agricola_animales_sector_asegurador) have crop-level blueberry claims for 2018 to 2024 under CC BY 4.0. Brazil's [SISSER policy data](https://dados.agricultura.gov.br/dataset/sisser3) are geolocated by policy but showed no mirtilo rows in samples and contain personal data, so publish aggregates only. Korea added blueberry insurance in 2024.
2. **Weather stations next to production (bias correction and frost detection).**
   - [NOAA GHCNh](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly) has a station within 25 km of 39 of the 53 benchmark sites, and within 50 km of 50.
   - National networks add canopy-level and agricultural stations:
     - [FAWN](https://fawn.ifas.ufl.edu/) (Florida, 60 cm canopy temperature and leaf wetness);
     - [RAN Agromet](https://www.agromet.cl/datos-historicos) (Chile, hourly);
     - [EEAOC](https://agromet.eeaoc.gob.ar/) and [INTA SIGA](https://siga.inta.gob.ar/) (Argentina);
     - [RIA Andalucía](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/), with paired open-air and under-plastic stations in Moguer and Almonte;
     - [IMGW](https://danepubliczne.imgw.pl/), [FMI](https://en.ilmatieteenlaitos.fi/open-data) and [Western Cape agriculture](https://gis.elsenburg.com/apps/wsp/);
     - [SASSCAL](https://www.sasscalweathernet.org/) (Namibia);
     - [INMET](https://portal.inmet.gov.br/dadoshistoricos), [IDEAM](https://www.datos.gov.co/Ambiente-y-Desarrollo-Sostenible/Temperatura-Ambiente-del-Aire/sbwg-7ju4) and [INAMHI](http://www.inamhi.gob.ec/visor/) (Brazil, Colombia, Ecuador);
     - [ECCC](https://api.weather.gc.ca/) (Canada).
   - NOAA GSOD and ISD stop at the end of August 2025.
3. **Dated field observations of crop stages (calibration and validation of phenology).**
   - Peruvian university theses with pruning, bloom and harvest dates, through the [UNALM repository API](https://repositorio.lamolina.edu.pe/) and [ALICIA](https://alicia.concytec.gob.pe/vufind/).
   - US plant patents with multi-year site means ([example](https://patents.google.com/patent/USPP27026P3/en)) and the [USDA-ARS Poplarville genotype dataset](https://agdatacommons.nal.usda.gov/articles/dataset/Data_from_Phenological_variation_associates_with_the_stability_of_fruit_quality_traits_in_cultivated_tetraploid_blueberry/28339583).
   - The Dutch [VBB cultivar trials](https://edepot.wur.nl/288774), the [UMaine wild blueberry phenology tracker](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/) and Quebec's [RAP Bleuet nain](https://www.agrireseau.net/rap/documents/116447/bleuet-nain-avertissement-no-1-13-mai-2025) warnings.
   - SENAMHI's [blueberry bulletin](https://www.senamhi.gob.pe/main.php?dp=la-libertad&p=boletines), the Junta de Andalucía's [weekly crop status](https://estadisticasagrariasypesquerascom.wpcomstaging.com/), the [Rutgers Blueberry Bulletin](https://extension.rutgers.edu/blueberry-bulletin) and [Clemson field reports](https://hgic.clemson.edu/south-carolina-fruit-and-vegetable-field-report-february-23-2026/).
   - The [Steyn 2022 thesis](https://scholar.sun.ac.za/server/api/core/bitstreams/47824860-fa96-4626-b2b2-da6439d6a8f4/content) for the Western Cape and the [Qingdao paper](https://journal30.magtechjournal.com/bfnyxb/CN/abstract/abstract9395.shtml).
   - [USA-NPN](https://www.usanpn.org/data/observational) and [iNaturalist](https://api.inaturalist.org/v1/docs/), which are useful only in cool climates.
4. **Weekly or monthly harvest-timing series (harvest windows and year-to-year shifts).**
   - Chile: the [Chilean Blueberry Committee](https://frutasdechile.cl/committee/arandanos/) weekly crop report and [ODEPA exports by region of origin](https://datos.odepa.gob.cl/dataset/comercio-exterior).
   - Peru: [BCRP](https://www.bcrp.gob.pe/estadisticas/informacion-regional.html) and [MIDAGRI](https://www.gob.pe/institucion/midagri/informes-publicaciones/7910469-boletin-estadistico-mensual-el-agro-en-cifras-2026) monthly production by department.
   - Mexico: [SIAP municipal statistics](https://nube.agricultura.gob.mx/datosAbiertos/Agricola.php) to 2025.
   - United States: [NASS Georgia crop progress](https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/) and [AMS weekly shipments](https://esmis.nal.usda.gov/publication/weekly-shipments-movement-blueberry); both stopped in 2025 and continue through free-key APIs.
   - Spain, Morocco, the EU and New Zealand: [DataComex](https://datacomex.comercio.es/Metadata/Comex) by province, the [Office des Changes](https://services.oc.gov.ma/DataBase/CommerceExterieur/presentation.htm), [Eurostat Comext](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409) and [Stats NZ HS10 exports](https://www.stats.govt.nz/large-datasets/csv-files-for-download/overseas-merchandise-trade-datasets/).
   - Japan and China: the [Tokyo market arrivals](https://www.shijou.metro.tokyo.lg.jp/torihiki/geppo) and [Xinfadi prices](http://www.xinfadi.com.cn/priceDetail.html).
5. **Orchard censuses and land use (where blueberries grow; better pin placement).**
   - Chile's [CIREN-ODEPA census](https://datos.odepa.gob.cl/dataset/catastro-fruticola) records every blueberry block with variety, planting year and irrigation, under CC BY; Coihueco alone has 621 blocks.
   - [USDA CDL class 242](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_wa23.htm) has low accuracy: 45% producer's and 39% user's in 2024.
   - [EuroCrops](https://github.com/maja601/EuroCrops), [Huelva plastic maps](https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/servicios/estadistica-cartografia/actividad/detalle/175064/175485.html) and [ESYRCE](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce/), which puts 79% of Spain's blueberry area under cover.
   - National statistics: [GUS](https://stat.gov.pl/obszary-tematyczne/rolnictwo-lesnictwo/uprawy-rolne-i-ogrodnicze/produkcja-upraw-rolnych-i-ogrodniczych-w-2024-r-,9,23.html), [Destatis](https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Obst-Gemuese-Gartenbau/Tabellen/strauchbeerenanbau.html), [Luke](https://statdb.luke.fi/PxWeb/pxweb/en/LUKE/LUKE__maa__puutar/0400_puutar.px/), [MAFF](https://www.maff.go.jp/j/tokei/kouhyou/tokusan_kazyu/index.html) and [Statistics Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=3210036401).
6. **Disaster declarations (dated events with places).**
   - [USDA FSA designations](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) give freeze windows to the day.
   - Brazil's [Atlas Digital de Desastres](https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml) records hail and frost declarations by municipality and day from 1991.
   - Mexico's [CENAPRED declaratorias](http://www.atlasnacionalderiesgos.gob.mx/apps/Declaratorias/) and Australia's [DisasterAssist](https://www.disasterassist.gov.au/find-a-disaster/australian-disasters).
   - Argentina's emergency resolutions and [DesInventar](https://www.desinventar.net/DesInventar/profiletab.jsp?countrycode=col&lang=ES) (most Latin American series end between 2013 and 2015).
7. **Cultivar traits (cultivar classes).**
   - The HortScience [Register of New Fruit and Nut Cultivars](https://doi.org/10.21273/hortsci19596-26) (CC BY-NC 4.0) and US plant patents, which give chill hours and ripening offsets against named cultivars.
   - The [UPOV TG/137](https://www.upov.int/documents/d/upov/tg-documents-en-tg137.pdf) timing scale, the IFAPA trials in Huelva and the [CIPRA crop guide](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf) degree-day thresholds for lowbush and northern highbush.
8. **Narrative corpora for the reviewed evidence library (RAG).**
   - [JRC MARS bulletins](https://joint-research-centre.ec.europa.eu/monitoring-agricultural-resources-mars/jrc-mars-bulletin_en) since 2007, SENAMHI bulletins and about 25 USDA FAS GAIN blueberry reports (public domain).
   - [IBO Summit 2025 presentations](https://www.internationalblueberry.org/ibo-summit-sa-presentations/), [NABC crop calls](https://nabc.blueberry.org/wp-content/uploads/sites/6/2026/02/Crop-Call-Report-February-19-2026-1.pdf), extension libraries with stated licences (UF/IFAS EDIS is CC BY-NC-ND 4.0) and the Junta's weekly posts.
9. **Protection and management facts (management layer).**
   - ESYRCE cover share in Spain.
   - Portugal's [RCM 179/2019](https://diariodarepublica.pt/dr/detalhe/resolucao-conselho-ministros/179-2019-125633667) caps covered cropping at 40% of the Mira irrigation area, with greenhouses at most 30%.
   - Hort Innovation reports that tunnels and polyhouses gave 42.7% of Australian volume in 2023/24.
   - Peruvian pruning-to-harvest intervals of 17 to 30 weeks.
10. **Literature access for systematic mining.**
    - [OpenAlex](https://openalex.org/) (a free key has been required since February 2026).
    - National repositories: INIA Chile has 621 'arándano' records (180 on flowering), ALICIA 870 records, SciELO and J-STAGE.
    - The global phenology report specifies a literature-mining pipeline that extracts dated stages with citations.

### 3.3 What the new evidence already says about the model

These are findings, not yet model changes. Each needs the corresponding job and a pre-registered check before any constant moves.

| Finding | Evidence | Implication |
|---|---|---|
| Grid daily minima miss spring radiation frosts by 5 to 8 °C | Chile 31 Oct 2022 (Coihueco −2.0 °C; cell about +5 °C); Waikato 7 Oct 2022 (Hamilton −2.9 °C; cell +5.15 °C). A further station case is ready but not yet compared with the grid: Tucumán, July 2024 (−2.7 to −4.4 °C near Famaillá) | Station bias correction, a 3 by 3 cell neighbourhood and local-night minima before trusting freeze frequencies |
| A sea-dominated cell destroys chill at Penguin, Tasmania | Devonport airport station logged 555 hours below 7.2 °C (May to August 2023) against 58 modelled | Flag coastal cells; use an inland neighbour or station correction |
| Coastal Peru "four months" and the model's 41 to 51 days measure different intervals | Theses: first open flower to first pick about 9 weeks; main bloom to bulk harvest 3.5 to 5 months; pruning to first harvest 17 to 30 weeks | Calibrate the managed cycle on the right endpoints, not the headline gap |
| Northern highbush in the Netherlands flowers 3 to 6 weeks before the model's Vechta date | VBB trials: Duke first flower 11 to 22 April, Bluecrop 18 to 27 April; model flowering starts 24 May at Vechta | The Waldo-derived constants do not fit NHB; this supports the approved cool-climate settings |
| Cool-climate stage thresholds exist with field data | CIPRA lowbush: full bloom 554 and ripe 1,516 degree-days above 0 °C from 1 March; NS and Maine thresholds; Washington NHB base 7 °C from 1 January with 2.4 to 3.7 day error | Lowbush and NHB profiles can be built from published numbers and checked on UMaine, RAP and USA-NPN records |
| Finland grows mostly half-high cultivars, not southern highbush | Luke: 44 to 47 enterprises on 32 to 34 ha in Southwest Finland; harvest end of July to early September | Naantali needs a half-high profile; its empty calendar is a model gap |
| Zimbabwe peaks in August to September, not June to July | GAIN's June/July sentence concerns South African imports; EU arrivals from Zimbabwe peak in September and October | Change the Marondera benchmark peak to August and September |
| Tasmania peak conflict is a dating issue | Government sheet from 2012 (ripening of most varieties); industry 2025 (volume) | Benchmark peak January to February with a March shoulder |
| SIAP blueberry data continue to 2025 | Municipal CSV 2003 to 2025, 74 blueberry rows in 2025 | Correct the benchmark gap note |
| The Chile frost was at fruit set, not flowering | Ñuble frost on 31 October 2022 fell mostly on fruit set | Test fruit-frost exposure, not flowering freeze, for that case |

## 4. Region by region

Each subsection gives what the app already has, the key findings, the P1 sources (up to ten, as ranked by the research agent) and the P1 extraction jobs. The linked report has every source, sample fields, all jobs, licensing gates and the full list of gaps.

### 4.1 United States Southeast (Florida, Georgia, the Carolinas, Mississippi, Alabama)

Full report: [regions/us-southeast.md](regions/us-southeast.md). Sources: 53; jobs: 14.

**The app has** 15 benchmark sites from Homestead to Burgaw and Poplarville, plus the Florida and Georgia panel sites, and 11 IBO records for Florida, Georgia and North Carolina.

**Key findings**
- **Loss validation.** RMA files give losses by county, month and cause since 1989; Georgia lost USD 30.5 million to the March 2022 freeze. FSA designations give exact freeze windows (11 to 14 March 2022), and Storm Events records the 16 March 2017 freeze at 03:00 with a blueberry narrative.
- **Dated phenology.**
  - Plant patents give multi-year 50% flowering and ripening means by site. Example: 'Star' at Alapaha averaged 3 March and 8 May over 2009 to 2013.
  - The USDA-ARS Poplarville dataset holds 187 southern highbush genotypes for 2021 and 2022 (public domain).
  - Clemson weekly field reports and UGA county blogs give dated regional stage notes.
- **Harvest timing.** NASS Georgia weekly percent harvested runs from 2011 to May 2025. AMS weekly shipments for Florida, Georgia and North Carolina run from November 2018 to April 2025. Both continue only through free-key APIs.
- **Stations.** FAWN (canopy-height temperature and leaf wetness from 1998), the UGA network (Alma station), NC ECONet (hourly since 1996) and the Mississippi network (Poplarville). A UF/IFAS report dated 9 February 2026 gives FAWN canopy minima for the early-2026 freeze.

**Still missing:**
- site-specific evergreen phenology for central and south Florida;
- dated cultivar bloom tables from NC State or Clemson;
- a public mesonet near South Carolina or Alabama production;
- smallfruits.org documents (bot wall).

**Rights.** UF/IFAS EDIS is CC BY-NC-ND 4.0, so quote it and do not publish derivatives. ACES content is All Rights Reserved. Most other sources state no terms, so store facts and short quotes with links.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Cause of Loss Historical Data Files: Summary of Business with Month of Loss](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/) | insurance, losses | open | opened |
| [Storm Events Database (bulk CSV)](https://www.ncei.noaa.gov/access/storm-events-database/) | losses, declarations | open | opened |
| [Secretarial Disaster Designations (state and county records)](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) | declarations, losses | open | opened |
| [Quick Stats database and API](https://quickstats.nass.usda.gov/api) | statistics, land use/census, phenology | free registration | opened |
| [2022 Census of Agriculture, county data, Table 33 Berries](https://www.nass.usda.gov/Publications/AgCensus/2022/Full_Report/Volume_1,_Chapter_2_County_Level/Georgia/st13_2_033_033.pdf) | land use/census, statistics | open | opened |
| [Georgia Crop Progress and Condition (weekly), incl. Southern Region report](https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/) | phenology, statistics | open | opened |
| [Weekly Shipments (Movement) - Blueberry, WA_FV408](https://esmis.nal.usda.gov/publication/weekly-shipments-movement-blueberry) | shipments/exports, prices | open | opened |
| [Georgia Farm Gate Value Report (annual, county tables)](https://caed.uga.edu/) | statistics, land use/census | open | opened |
| [Georgia Automated Environmental Monitoring Network (georgiaweather.net)](http://www.georgiaweather.net/) | stations | open | opened |
| [Florida Automated Weather Network (FAWN) QA/QC yearly archive and report generator](https://fawn.ifas.ufl.edu/) | stations | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| USSE-01 | Blueberry insurance loss by county, month and cause | 2.0 |
| USSE-02 | County hazard windows from FSA Secretarial designations | 1.0 |
| USSE-03 | Storm Events freeze, hail and tropical events in blueberry counties | 1.5 |
| USSE-04 | Georgia weekly blueberry harvest progress | 1.5 |
| USSE-05 | Weekly blueberry shipments by origin (FL, GA, NC) | 2.0 |
| USSE-06 | Cultivar bloom and ripening table from patents and release documents | 3.0 |
| USSE-07 | Poplarville SHB genotype phenology ingest | 1.0 |
| USSE-08 | Station table for benchmark pins (FL, GA, NC, MS) | 3.0 |

### 4.2 United States North and West, and Canada

Full report: [regions/us-north-west-canada.md](regions/us-north-west-canada.md). Sources: 67; jobs: 13.

**The app has** Hammonton (NJ) and Grand Junction (MI), plus IBO records for California, the Pacific Northwest and British Columbia. Live pins fail or fall back to the scan: a Cascade Range cell near Yakima has no calendar; Lynden, Cherryfield and Lac-Saint-Jean get scan windows only.

**Key findings**
- **Published cool-climate stage thresholds:**
  - AAFC CIPRA lowbush (base 0 °C from 1 March): full bloom 554 degree-days, ripe fruit 1,516.
  - Nova Scotia: bloom at 390 to 600 GDD (base 0 °C from 1 April).
  - Maine: bloom at 100 to 500 degree-days (base 4.4 °C).
  - MSU 'Jersey': bloom 14 to 15 May at 310 GDD (base 50 °F); first harvest 15 July at 1,313 GDD.
  - Washington northern highbush: base 7 °C from 1 January, error 2.4 to 3.7 days.
- **Dated lowbush stages** for the two scan-only pins: the UMaine tracker (2020 to 2026, nine sites) and Quebec's weekly RAP Bleuet nain warnings for Lac-Saint-Jean.
- **Rutgers Blueberry Bulletin.** It dates the 19 to 22 April 2026 New Jersey freeze emergency and gives bloom percentages by cultivar.
- **Data series.** RMA losses for MI, NJ, ME, OR, WA and CA; the ECCC hourly API; Statistics Canada table 32-10-0364; FADQ crop-condition bulletins.

**Still missing:**
- a primary chill requirement for half-high or lowbush;
- public Canadian insurance losses by crop and cause.

**Rights.** Agrométéo Québec forbids redistribution. MSU pages sit behind a bot wall. The agent reached them through a CMS host, which bypasses the protection: do not build jobs on that route; ask MSU for access instead.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [The Blueberry Bulletin (weekly update to growers)](https://extension.rutgers.edu/blueberry-bulletin) | phenology, pest/disease, extension | open | opened |
| [Real-Time Wild Blueberry Phenology (weekly records 2020-2026)](https://extension.umaine.edu/blueberries/real-time-wild-blueberry-phenology/) | phenology, extension | open | opened |
| [MSU Extension regional fruit updates (Southwest and West Central Michigan) via MSU dotCMS host](https://msu-prod.dotcms.cloud/news/southwest-michigan-fruit-update-april-22-2025) | phenology, extension, pest/disease | open | opened |
| [Réseau d'avertissements phytosanitaires (RAP), Bleuet nain: avertissements et bilans](https://www.agrireseau.net/rap/documents/116447/bleuet-nain-avertissement-no-1-13-mai-2025) | phenology, pest/disease, extension | open | opened |
| [Nova Scotia Lowbush Blueberry Blog: Growing Degree Days page and station GDD updates](https://www.novascotiawildblueberryblog.com/p/phenology-tracker.html) | phenology, stations, extension | open | opened |
| [L'état des cultures de la FADQ (crop condition bulletins)](https://www.fadq.qc.ca/salle-de-presse/bulletins-dinformation/etat-des-cultures/etat-des-cultures-2023/letat-des-cultures-de-la-fadq-bilan-au-4-juillet-2023-rapport-numero-5) | losses, insurance, industry reports | open | opened |
| [CIPRA Guide des cultures (phénologie du bleuetier en corymbe et du bleuetier nain)](https://agrometeo.solutions-mesonet.org/help/guide_cultures_2022_fr.pdf) | literature, cultivar traits, phenology | open | opened |
| [Understanding Growing Degree Days in Wild Blueberry Production (fact sheet)](https://www.perennia.ca/wp-content/uploads/2022/05/Understanding-Growing-Degree-Days-in-Wild-Blueberry-Production.pdf) | extension, literature | open | opened |
| [Drummond 2019. Reproductive Biology of Wild Blueberry (Vaccinium angustifolium Aiton). Agriculture 9(4):69](https://ideas.repec.org/a/gam/jagris/v9y2019i4p69-d218599.html) | literature | open | opened |
| [Using degree days to predict pest and crop development in blueberries (Isaacs, Albert, Mason 2019)](https://msu-prod.dotcms.cloud/news/using-degree-days-to-predict-pest-and-crop-development-in-blueberries) | phenology, extension, pest/disease | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| NWC-01 | Rutgers Blueberry Bulletin weekly stage and event extraction | 2.0 |
| NWC-02 | UMaine wild blueberry phenology tracker to stage table | 1.5 |
| NWC-03 | Québec RAP blueberry stage tables (bleuet nain and corymbe) | 2.0 |
| NWC-04 | MSU fruit updates via dotCMS host | 1.5 |
| NWC-05 | Cool-climate phenology parameter table | 1.0 |
| NWC-06 | Stage freeze threshold table | 0.5 |
| NWC-07 | RMA cause of loss for blueberry counties in scope | 1.5 |
| NWC-08 | FADQ crop condition and damage notices | 1.5 |

### 4.3 Peru and Mexico

Full report: [regions/peru-mexico.md](regions/peru-mexico.md). Sources: 65; jobs: 12.

**The app has** Chao, Olmos and Ica in Peru; Zapotlán, Los Reyes and El Fuerte in Mexico; and IBO records for both countries and four regions.

**Key findings**
- **Peruvian theses** give pruning, bloom and harvest dates for Olmos, Villacurí, Virú, Chao, Chepén and Jayanca. The UNALM repository has an open API (121 hits for "arándano poda").
  - Pruning to first harvest takes 17 to 30 weeks.
  - Main bloom to bulk harvest takes 3.5 to 5 months, which explains the "four months" gap.
- **SENAMHI** publishes a dekadal blueberry bulletin (2024 to now) with observed stages at Cayaltí, Chao and San José. It currently tracks El Niño Costero 2026.
- **Monthly production by department:** BCRP (La Libertad, Lambayeque, Áncash) and MIDAGRI.
- **Mexico:** SIAP municipal data run to 2025, not 2022 as the benchmark notes say. CNSF holds blueberry insurance claims for 2018 to 2024 (frost, hail, hurricane) under CC BY 4.0, and CENAPRED dates frost and heat declarations by municipality.

**Still missing:**
- Proarándanos weekly reports (the site returned HTTP 521; ask by email);
- an explanation for SUNAT export totals about 30 times below MIDAGRI's;
- hourly stations near production without registration;
- a San Quintín calendar.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Repositorio Institucional UNALM (DSpace 7 REST API), blueberry theses](https://repositorio.lamolina.edu.pe/) | literature, phenology, management | open | opened |
| [Comportamiento fenológico, características organolépticas y productividad del arándano en La Libertad (Mayta Aparicio, 2024)](https://hdl.handle.net/20.500.12996/6685) | phenology, cultivar trial, stations | open | opened |
| [Manejo agronómico del cultivo de arándano en contenedores en Villacurí, Ica (Orga Porras, 2021)](https://hdl.handle.net/20.500.12996/4981) | phenology, management, statistics | open | opened |
| [Manejo de la cosecha en cultivo de arándano para exportación en la irrigación del Proyecto Olmos (Castro Castro, 2025)](https://hdl.handle.net/20.500.12996/7224) | phenology, management | open | opened |
| [Manejo y evaluación comparativa de dos sistemas de poda en arándano cv. Sekoya Pop en Olmos (Córdova Sandoval, 2026)](https://hdl.handle.net/20.500.12996/7508) | phenology, management, cultivar trial | open | opened |
| [Pronóstico Agrometeorológico: Cultivo de Arándano (dekadal bulletin)](https://www.senamhi.gob.pe/main.php?dp=la-libertad&p=boletines) | phenology, extension, stations | open | opened |
| [Índice Costero El Niño (ICEN), official monthly series](http://met.igp.gob.pe/datos/ICEN.txt) | gridded weather, regulation | open | opened |
| [Boletín Estadístico Mensual 'El Agro en Cifras' (PDF and Excel tables)](https://www.gob.pe/institucion/midagri/informes-publicaciones/7910469-boletin-estadistico-mensual-el-agro-en-cifras-2026) | statistics, shipments/exports | open | opened |
| [BCRP Síntesis de Actividad Económica (regional monthly reports)](https://www.bcrp.gob.pe/estadisticas/informacion-regional.html) | statistics | open | opened |
| [USDA FAS GAIN Blueberry Annual, Peru (PE2025-0010, PE2024-0002, PE2023-0002)](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf) | industry reports, statistics | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| PEMX-01 | Coastal Peru thesis phenology table | 4.0 |
| PEMX-02 | SENAMHI blueberry agromet bulletin stage series | 1.5 |
| PEMX-03 | Peru monthly blueberry production by department | 2.0 |
| PEMX-04 | Peru ENSO and coastal anomaly covariates | 1.0 |
| PEMX-05 | Peru weather damage event records 2023-2026 | 2.0 |
| PEMX-06 | Mexico SIAP blueberry municipal panel 2003-2025 | 1.0 |
| PEMX-07 | Mexico frost, hail and heat events at blueberry municipios | 1.5 |
| PEMX-08 | Mexico SMN daily station table for blueberry sites | 2.0 |

### 4.4 Chile, Argentina and Uruguay

Full report: [regions/chile-argentina-uruguay.md](regions/chile-argentina-uruguay.md). Sources: 64; jobs: 16.

**The app has** five Chilean and three Argentine benchmark sites, plus IBO records for Chile, the Linares-to-Chillán area and Argentina.

**Key findings**
- **The 2022 frost.** It struck on the morning of 31 October 2022 (Coihueco −2.0 °C, Longaví −2.2 °C, San Ignacio −1.7 °C; DMC confirms Linares −2.2 °C). It fell mostly at fruit set. The old check missed it by starting on 1 November.
- **Orchard census.** The CIREN-ODEPA census (CC BY, 1999 to 2025) lists every blueberry block with variety, planting year and irrigation. A map service adds farm polygons.
- **Harvest timing.** ODEPA monthly exports by region of origin run from 1998. The Committee's weekly crop report gives regional shares and tonnes by variety.
- **Argentina's second missed-frost case.** EEAOC returned 49 Tucumán stations for 10 to 16 July 2024: Monte Grande 2 (Famaillá) reached −4.4 °C with 41.9 h below 0 °C, and Concordia −3.5 °C. Resolution SGA 77/2019 names blueberries in a rain emergency.
- **Chilean bloom months** are partly answered for Maule: O'Neal flowers mid-August to early September and Brigitta in October.

**Still missing:**
- a 2022 Ñuble frost decree;
- open insurance claims;
- Uruguayan area or export series;
- documented station endpoints. RAN, EEAOC and INTA use undocumented ones, so ask the operators before bulk pulls.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Red Agroclimática Nacional (RAN) Agromet: historical station data](https://www.agromet.cl/datos-historicos) | stations | open | opened |
| [DMC Boletín Agroclimático Mensual](https://climatologia.meteochile.gob.cl/application/publicacionesb/boletinAgroclimatico) | stations, extension, losses | open | opened |
| [INIA Boletín Nacional de Análisis de Riesgos Agroclimáticos (monthly, one bulletin per region)](http://riesgoclimatico.inia.cl/public/publicaciones) | extension, phenology, losses | open | opened |
| [Catastro frutícola CIREN-ODEPA (open data, block level)](https://datos.odepa.gob.cl/dataset/catastro-fruticola) | land use/census, cultivar traits | open | opened |
| [IDE Minagri / CIREN Catastro Frutícola map service (fruit producer polygons)](https://esri.ciren.cl/server/rest/services/IDEMINAGRI/CATASTRO_FRUTICOLA/MapServer) | land use/census | open | opened |
| [ODEPA Comercio Exterior open data (monthly exports by product, region of origin and destination)](https://datos.odepa.gob.cl/dataset/comercio-exterior) | shipments/exports | open | opened |
| [Chilean Blueberry Committee Crop & Exports Report (weekly, powered by iQonsulting)](https://comitedearandanos.cl/) | shipments/exports, industry reports, cultivar traits | open | opened |
| [Frutas de Chile news archive (includes Blueberry Committee releases, DMC frost warnings, season estimates)](https://frutasdechile.cl/news/minimos-efectos-de-las-heladas-lluvia-y-granizo-de-noviembre-sobre-la-produccion-de-arandanos-de-chile/) | news, industry reports, losses | open | opened |
| [EEAOC Seccion Agrometeorologia station network (web app and JSON services, including frost summary datos-heladas.php)](https://agromet.eeaoc.gob.ar/) | stations, losses | open | opened |
| [INTA SIGA (Sistema de Informacion y Gestion Agrometeorologica) station catalogue and daily series](https://siga.inta.gob.ar/) | stations | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| CAU-01 | Chile 2022 spring frost station table (Maule, Ñuble, Biobío) | 1.5 |
| CAU-02 | Chile station bias-correction set near benchmark sites | 3.0 |
| CAU-03 | Chile blueberry block census table | 1.5 |
| CAU-05 | Chile monthly blueberry exports by region of origin | 1.0 |
| CAU-06 | Chilean Blueberry Committee weekly crop report table | 2.0 |
| CAU-07 | Chile weather event records (frost, rain, hail, heat) | 2.5 |
| CAU-11 | Tucumán and Concordia July 2024 frost station table | 1.5 |
| CAU-14 | Argentina and Uruguay weather event records | 1.0 |

### 4.5 Brazil, Colombia and Ecuador

Full report: [regions/brazil-colombia-ecuador.md](regions/brazil-colombia-ecuador.md). Sources: 93; jobs: 23.

**The app has** Vacaria, Pelotas, Lages, Piracicaba and Guasca, the Papanduva reference site, and IBO records for the Colombian highlands and Ecuador.

**Key findings**
- **Brazilian disaster records.** The Atlas Digital de Desastres CSV (1991 to 2025) gives hail (code 13213) and frost (code 13322) declarations by municipality and day, with an agricultural-loss column. The live S2iD system blocks requests from outside Brazil.
- **Brazilian insurance.** SISSER/PSR insurance is per policy and geolocated (CC BY). Samples held no mirtilo rows, and the files contain personal data, so use aggregates of temperate-fruit claims only.
- **Santa Catarina harvest shares.** Epagri/Cepa 2014/15 gives monthly shares for Campos de Lages (December 37%, January 18%, February 41%, March 4%). The region containing Papanduva had no blueberry then.
- **Two new cases.** A Paraná dataset (Cerro Azul, 659 m, CC BY 4.0) is a candidate low-chill site, with bloom July to September and harvest November to January. A Vacaria frost on 12 to 14 September 2015 caused about 30% loss with flowers open.
- **Colombia and Ecuador.** Colombia has EVA municipal rows (about 907 ha in 2025), monthly exports peaking in December and January, IDEAM hourly stations and UNGRD frost and hail events. Ecuador has an INAMHI hourly API.

**Still missing:**
- Papanduva bloom or harvest dates (ask Epagri and growers);
- IBGE or Epagri mirtilo tables;
- a public list of Colombian farms registered for export.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Atlas Digital de Desastres no Brasil (Base de Dados Completa 1991-2025)](https://atlasdigital.mdr.gov.br/paginas/downloads.xhtml) | declarations, losses | open | opened |
| [SISSER: Programa de Subvenção ao Prêmio do Seguro Rural (PSR) policy-level open data](https://dados.agricultura.gov.br/dataset/sisser3) | insurance, losses | open | opened |
| [Fruticultura em números: safra 2014/15 (Epagri Documentos 271) and BD Fruticultura Catarinense 2014-15](https://docweb.epagri.sc.gov.br/website_cepa/Fruticultura/Doc_271_Fruticultura_em_Numeros_2014_15.pdf) | statistics, shipments/exports, land use/census | open | opened |
| [Informativo Conjuntural (weekly crop situation bulletin)](https://www.emater.tche.br/site/info-agro/informativo_conjuntural.php) | extension, phenology, losses | open | opened |
| [INMET automatic stations: dados históricos (annual zips) and station catalogue API](https://portal.inmet.gov.br/dadoshistoricos) | stations | open | opened |
| [Epagri/Ciram Download de Dados Ambientais (hourly, last 24 months) and data requests](https://ciram.epagri.sc.gov.br/dadosambientaispublicos/) | stations | free registration | opened |
| [Epagri/Ciram meteorological notes on frost and cold days (with station minimum tables)](https://ciram.epagri.sc.gov.br/index.php/2025/06/25/mais-de-100-estacoes-com-minimas-negativas-e-dia-mais-frio-do-ano-no-litoral/) | stations, losses, news | open | opened |
| [Monitoramento do frio (Informe Técnico): chill hours ≤7.2 °C and chill units at SC stations](https://ciram.epagri.sc.gov.br/index.php/monitoramento-do-frio/) | stations, management, extension | open | opened |
| [Medeiros et al. 2018, Phenology, production and quality of blueberry produced in humid subtropical climate (Rev. Bras. Frutic. 40(3) e-520)](https://www.scielo.br/j/rbf/a/B4wvqmqZsXB9pVfWByCt9zj/?lang=en) | phenology, cultivar trial, literature | open | opened |
| [Geada traz prejuízos aos produtores (STR Vacaria, 29 Sep 2015)](https://www.strvacaria.com.br/geada-tras-prejuizos-aos-produtores/) | losses, news | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| BCE-01 | Brazil municipal hail, frost and drought declarations (Atlas Digital) | 2.0 |
| BCE-02 | Temperate-fruit insurance losses as a freeze and hail proxy (PSR/SISSER) | 2.0 |
| BCE-03 | Southern Brazil highland station table and Tmin bias (INMET + Epagri/Ciram) | 3.0 |
| BCE-04 | Published chill-hour table for SC and PR stations | 1.0 |
| BCE-05 | Brazilian dated phenology and harvest calibration table | 2.0 |
| BCE-11 | Colombia: EVA arándano municipal area and production table | 0.5 |
| BCE-12 | Colombia: Monthly blueberry export series by origin department | 0.5 |
| BCE-13 | Colombia: IDEAM highland station table and hourly temperature pull | 1.5 |

### 4.6 Spain, Portugal and Morocco

Full report: [regions/iberia-morocco.md](regions/iberia-morocco.md). Sources: 81; jobs: 12.

**The app has** Moguer, Odemira, Sever do Vouga, Larache and Agadir, plus IBO records for all three countries and four regions.

**Key findings**
- **Paired stations in Huelva.** RIA has open-air and under-plastic stations side by side in Moguer and Almonte, with daily data from 2001. These can measure the tunnel effect the model lacks. Hourly SiAR data need a free registration tied to a Spanish ID number.
- **Dated stages.** The Junta's weekly crop status gives dated blueberry stages by district since 2017. Its campaign synthesis gives monthly sales shares: 55.4% in April and May 2025/26, with the peak in the second half of May.
- **Cultivar harvest dates.**
  - IFAPA Moguer 2020/21: 'Cupla' 15 February to 6 May.
  - INIAV Duke at Odemira: 50% picked by 5 June under tunnel and by 17 July in open air.
  - An Évora thesis gives bloom dates.
- **Protection share.** ESYRCE puts 79% of Spain's blueberry area under cover. Huelva plastic area is mapped by municipality, 2004 to 2026. Portugal's RCM 179/2019 caps covered cropping in the Mira irrigation area.
- **Monthly exports:** DataComex by province (from 1995), the INE Portugal API, and Morocco's Office des Changes (from 1998, CAPTCHA per query).

**Still missing:**
- Morocco Foodex export data (login required);
- Agroseguro loss figures (bot wall; press quotes only);
- MAMDA and Moroccan weather-service data (not open);
- a Moroccan tunnel share.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Síntesis de campaña: Frutos Rojos (provincia de Huelva), Observatorio de Precios y Mercados](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?action=DownloadS&element=5534749&field=DOCUMENTO&table=12030) | industry reports, statistics, shipments/exports | open | opened |
| [Cartografía de cultivos bajo plástico en la provincia de Huelva (annual remote-sensing mapping)](https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/servicios/estadistica-cartografia/actividad/detalle/175064/175485.html) | land use/census, remote sensing, management | open | opened |
| [Red de Información Agroclimática de Andalucía (RIA), including 'bajo plástico' stations](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/) | stations | open | opened |
| [SiAR, Sistema de Información Agroclimática para el Regadío (web portal and API SiAR)](https://servicio.mapa.gob.es/siarweb/masInformacion) | stations | free registration | opened |
| [Evaluación de Variedades de Arándanos (IFAPA trials at El Cebollar, Moguer; campaigns 2020/21 and 2021/22)](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/servifapa/registro-servifapa/751da974-6d88-48c8-b8b7-2f88ae5d1e3f) | cultivar trial, phenology, management | open | opened |
| [Estado de los cultivos y la ganadería (weekly crop status) and Boletín Semanal de Información Agraria y Pesquera](https://estadisticasagrariasypesquerascom.wpcomstaging.com/) | phenology, losses, extension | open | opened |
| [ESYRCE, Encuesta sobre Superficies y Rendimientos de Cultivos (results incl. arándano by secano, regadío, invernadero)](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce/) | land use/census, statistics, management | open | opened |
| [DataComex: Estadísticas del comercio exterior español (monthly, by TARIC and province)](https://datacomex.comercio.es/Metadata/Comex) | shipments/exports | open | opened |
| [INE base de dados: Superficie e Producao das principais culturas agricolas por Regiao agraria e Especie (indicadores 0000019, 0000021; NUTS versions 0000018, 0013080, 0013082)](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0000019&lingua=PT) | statistics, land use/census | open | opened |
| [INE Exportacoes (kg) de bens por Local de destino e Tipo de bens (NC8); Mensal (indicator 0008149)](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0008149&lingua=PT) | shipments/exports | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| IBM-01 | Huelva paired open-air and under-plastic station table | 2.0 |
| IBM-02 | Huelva campaign evidence library (official weekly and annual narratives) | 3.0 |
| IBM-03 | Spanish cultivar harvest and phenology table | 1.5 |
| IBM-04 | Spain monthly blueberry export and production panel | 1.0 |
| IBM-20 | INE Portugal blueberry area, production and monthly exports | 1.0 |
| IBM-21 | Portuguese dated blueberry phenology and harvest percentiles | 1.0 |
| IBM-30 | Morocco monthly blueberry export and arrival series (OC + Eurostat + HMRC) | 1.5 |
| IBM-31 | Morocco dated berry weather events and season-timing claims (press RAG) | 1.5 |

### 4.7 Central, Northern and Eastern Europe

Full report: [regions/europe-central-north-east.md](regions/europe-central-north-east.md). Sources: 73; jobs: 14.

**The app has** Lublin and Vechta, IBO records for Poland, Germany, Romania and Serbia, and a failing pin at Naantali, Finland.

**Key findings**
- **Dutch VBB cultivar trials (2008 to 2012)** give first-flower dates: Duke 11 to 22 April, Bluecrop 18 to 27 April. That is 3 to 6 weeks before the model's flowering start at Vechta. First flower to first harvest took 61 to 68 days for Duke and 64 to 79 for Bluecrop.
- **Finland grows mostly half-high.** Luke counts 44 to 47 enterprises on 32 to 34 ha in Southwest Finland, harvesting from the end of July to early September. MTT tests found little flower damage at −3 °C for 8 h but severe damage at −5 °C for 2 h.
- **Official sub-national yields:** GUS table 110 by voivodeship from 2020, Destatis by Land, and ARiMR declared area by gmina.
- **Monthly exports by country** from Eurostat Comext CN 08104050, which mixes highbush blueberry with American cranberry.
- **JRC MARS bulletins** since 2007 form a ready citation-first corpus. Poland's official frost aid covers 15 to 30 April 2024, while the IBO record says May.

**Still missing:**
- Vaccinium observations: DWD does not observe it, and PEP725 needs a login;
- official blueberry tables for Serbia, Romania, Ukraine and Italy;
- dated bloom observations in Finland.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Rassenonderzoek Blauwe bes 2007-2012 (blueberry cultivar trial report)](https://edepot.wur.nl/288774) | phenology, cultivar trial, cultivar traits | open | opened |
| [Horticultural Statistics, table 0400_puutar 'Food production in the open by region' (species: Highbush blueberry)](https://statdb.luke.fi/PxWeb/pxweb/en/LUKE/LUKE__maa__puutar/0400_puutar.px/) | statistics, land use/census, management | open | opened |
| [FMI open data (WFS download service, weather observations)](https://en.ilmatieteenlaitos.fi/open-data) | stations | open | opened |
| [MTT:n selvityksia 139, section 3.9 'Kotimaisen pensasmustikan kukkien hallankestavyys' (frost tolerance of flowers of Finnish half-high blueberry)](https://jukuri.luke.fi/server/api/core/bitstreams/4e7588f2-2a3e-4423-9ad8-e3c858470232/content) | cultivar traits, literature, losses | open | opened |
| [Crop production in EU standard humidity (apro_cpsh1), crop F3300 Blueberries](https://ec.europa.eu/eurostat/databrowser/view/apro_cpsh1/default/table?lang=en) | statistics | open | opened |
| [EU trade since 1988 by HS2-4-6 and CN8 (DS-045409), product 08104050 fresh Vaccinium corymbosum and V. macrocarpon](https://ec.europa.eu/eurostat/comext/newxtweb/) | shipments/exports | open | opened |
| [Produkcja upraw rolnych i ogrodniczych (annual), table 110 'Powierzchnia uprawy, plony i zbiory borowki wysokiej w sadach' and tables 122-124](https://stat.gov.pl/obszary-tematyczne/rolnictwo-lesnictwo/uprawy-rolne-i-ogrodnicze/produkcja-upraw-rolnych-i-ogrodniczych-w-2024-r-,9,23.html) | statistics | open | opened |
| [Powierzchnia upraw w gminach / Rejestr upraw (declared crop area by municipality)](https://www.gov.pl/web/arimr/powierzchnia-upraw-w-gminach) | land use/census | open | opened-limited |
| [Strauchbeerenanbau (shrub berry survey), Kulturheidelbeeren rows; Fachserie 3 Reihe 3.1.9 and GENESIS 41232](https://www.destatis.de/DE/Themen/Branchen-Unternehmen/Landwirtschaft-Forstwirtschaft-Fischerei/Obst-Gemuese-Gartenbau/Tabellen/strauchbeerenanbau.html) | statistics, management | open | opened |
| [The Influence of Variety and Climatic Year on the Phenology of Blueberry Grown in the Banat Area, Romania. Agronomy 12(11): 2605](https://doi.org/10.3390/agronomy12112605) | phenology, literature, cultivar traits | open | opened-limited |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| ECNE-01 | Dutch NHB cultivar phenology table from the VBB 2007-2012 trial | 1.0 |
| ECNE-02 | Naantali cool-climate test pack (Luke + FMI + Finnish half-high traits) | 1.5 |
| ECNE-03 | Poland voivodeship and gmina blueberry layer | 1.5 |
| ECNE-04 | National blueberry production series for the scope | 1.0 |
| ECNE-05 | Monthly blueberry trade curves as harvest-timing proxy | 1.0 |
| ECNE-06 | JRC MARS bulletin weather-anomaly claims for the scope | 3.0 |
| ECNE-10 | Station bias pack for European NHB benchmark cells | 2.0 |

### 4.8 Africa (South Africa, Zimbabwe, Namibia, Kenya, Zambia, Egypt, Tunisia)

Full report: [regions/africa.md](regions/africa.md). Sources: 48; jobs: 8.

**The app has** George, Wolseley, Tzaneen and Marondera, plus IBO records for South Africa (three regions), Zimbabwe, Namibia (Kavango) and Kenya.

**Key findings**
- **Steyn's 2022 Stellenbosch thesis (open)** gives day-level stages at Hex River for 2020 and 2021. Cultivar 8-42 reached 50% flowering on 7 July 2020 and peaked on 26 October 2020. Pruning fell in the last week of November, which closes the Wolseley pruning gap.
- **Zimbabwe's peak is August to September.** GAIN's "June/July" describes South Africa's imports; EU arrivals peak in September and October.
- **Free stations sit beside three key places.** The Western Cape portal's Veldreserwe station, about 2 km from the trial, recorded −1.93 °C on 29 August 2024. SASSCAL Mashare in Namibia has run since 2012. Zimbabwe's MSD dekadal bulletins tabulate Marondera minima.
- **Harvest timing for small producers** comes only from monthly EU and UK arrivals (Comext, HMRC).

**Still missing:**
- open data from the South African industry (Berries ZA reports are members-only; PPECB blocks US visitors);
- any open loss or insurance data;
- bloom data for Limpopo or Zimbabwe;
- a free station network for northern South Africa.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Steyn (2022) MSc thesis: Investigating plant growth dynamics of selected southern highbush blueberry cultivars under South African growing conditions](https://scholar.sun.ac.za/server/api/core/bitstreams/47824860-fa96-4626-b2b2-da6439d6a8f4/content) | phenology, management, literature | open | opened |
| [Western Cape Department of Agriculture Weather Station Data Portal](https://gis.elsenburg.com/apps/wsp/) | stations | open | opened |
| [SARS Trade Statistics data download wizard](https://tools.sars.gov.za/tradestatsportal/data_download.aspx) | shipments/exports | open | opened |
| [USDA FAS GAIN South Africa blueberry reports (SF2026-0027, 12 Aug 2026; June 2020 report)](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=South%20African%20Blueberry%20Market%20Analysis_Pretoria_South%20Africa%20-%20Republic%20of_SF2026-0027.pdf) | industry reports, statistics, shipments/exports | open | opened |
| [Meteorological Services Department Dekadal Agromet Bulletin](https://www.weatherzw.org.zw/products/dekadal-agromet-bulletin/) | stations, extension, losses | open | opened |
| [Linda Nielsen (HDC CEO), 'Zimbabwe's blueberry boom keeps building momentum' (IBO website, 5 June 2026; republished by FreshFruitPortal)](https://www.freshfruitportal.com/news/2026/06/15/zimbabwe-blueberry-boom/) | industry reports | open | opened |
| [Eurostat Comext DS-045409 (EU trade since 1988 by CN8), monthly imports of CN 0810 40 50 by partner](https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409) | shipments/exports | open | opened |
| [SASSCAL WeatherNet (station Mashare, Kavango East, and Bagani near Divundu)](https://www.sasscalweathernet.org/) | stations | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| AF-01 | Steyn 2022 dated stage table for Hex River and Wolseley | 1.0 |
| AF-02 | Western Cape WCDoA station pull for benchmark and trial sites | 2.0 |
| AF-03 | SASSCAL Mashare and Bagani station pull for Kavango frosts | 1.0 |
| AF-04 | Zimbabwe MSD dekadal bulletins to station table and frost events | 1.5 |
| AF-05 | Monthly trade-mirror arrival curves for African origins | 1.5 |

### 4.9 China, Japan, South Korea and India

Full report: [regions/china-east-asia-india.md](regions/china-east-asia-india.md). Sources: 76; jobs: 22.

**The app has** Mengzi, Qingdao and Dandong, plus IBO records for China (six regions) and India.

**Key findings**
- **Qingdao bloom dates.** A 2025 paper by the Huangdao weather bureau gives open-field first bloom on 21 to 25 April and full bloom from 26 April to 12 May; cold-shed first bloom is 21 to 25 March. Orchard minima ran 2.7 to 2.9 °C below the national station.
- **Li Yadong's 2024 report** gives the top-eight provinces, the protected share and ripening windows; Yunnan evergreen cultivars flower in August and September and ripen in November. Mengzi harvests from November to June.
- **Dated damage from weather bureaus.** Liaoning and Guizhou publish blueberry-specific services and damage dates: Dandong hail on 21 June 2021, Guizhou rainstorms on 22 to 24 June 2020.
- **Japan and Korea** have official blueberry rows:
  - MAFF prefecture area and production, 2003 to 2023;
  - Tokyo market monthly arrivals since 2002;
  - Korean census tables split into open field and protected cultivation;
  - Korean blueberry insurance since 2024.

**Rights and access.** CMA station data need real-name registration. NMC bulletins forbid reuse without written permission; keep them link-only.

**Still missing:**
- Dandong bloom dates;
- Mengzi pruning dates;
- Indian data beyond monthly imports.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [2024年中国蓝莓产业发展报告 (China Blueberry Industry Development Report 2024), Li Yadong et al.](http://sqtv.net/news/bencandy.php?fid=103&id=253081) | industry reports, statistics, management | open | opened |
| [NOAA NCEI Integrated Surface Database (Global Hourly) and GSOD, Chinese stations near blueberry areas](https://www.ncei.noaa.gov/access/search/data-search/global-summary-of-the-day) | stations | open | opened |
| [青岛市蓝莓低温伤害统计及预警指标构建 (Blueberry low temperature damage statistics and early warning index construction in Qingdao), Rao, Chen and Hu, 北方农业学报 53(1):115-124, 2025](https://journal30.magtechjournal.com/bfnyxb/CN/abstract/abstract9395.shtml) | phenology, losses, literature | open | opened |
| [Liaoning Meteorological Bureau news on blueberry meteorological services (Dandong 草莓蓝莓气象服务中心)](http://ln.cma.gov.cn/xwzx/qxxw/202107/t20210713_3523136.html) | losses, extension, news | open | opened |
| [北京新发地农产品批发市场 price data, 蓝莓 (Beijing Xinfadi wholesale market daily blueberry price)](http://www.xinfadi.com.cn/priceDetail.html) | prices | open | opened |
| [特産果樹生産動態等調査 (Survey of special fruit tree production trends), 特産果樹生産出荷実績調査 table 2-2 種類別栽培状況（都道府県） 2) かんきつ類以外の果樹【落葉果樹】](https://www.maff.go.jp/j/tokei/kouhyou/tokusan_kazyu/index.html) | statistics, land use/census | open | opened |
| [過去の気象データ検索 (Past weather data search), hourly pages hourly_s1 (staffed/special stations) and hourly_a1 (AMeDAS)](https://www.data.jma.go.jp/stats/etrn/select/prefecture.php?prec_no=44) | stations | open | opened |
| [過去の気象データ・ダウンロード (Past weather data download tool)](https://www.data.jma.go.jp/risk/obsdl/index.php) | stations | open | opened-limited |
| [東京都中央卸売市場 市場統計情報（月報・年報） 市場統計情報明細データ (青果 y-files)](https://www.shijou.metro.tokyo.lg.jp/torihiki/geppo) | shipments/exports, prices | open | opened |
| [普通貿易統計 品別国別表（輸入）, statistical code 0810.40-000 クランベリー、ビルベリーその他のヴァキニウム属の果実 (fresh)](https://www.e-stat.go.jp/stat-search/files?page=1&toukei=00350300&tstat=000001013141&cycle=1&tclass1=000001013180&tclass2=000001013182&layout=datalist&tclass3val=0) | shipments/exports, prices | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| CEAI-01 | China stage calendars and dated phenology (Mengzi, Qingdao, Dandong) | 1.5 |
| CEAI-02 | China dated weather-damage event records | 1.5 |
| CEAI-04 | China station table and orchard offset | 1.0 |
| CEAI-05 | Beijing Xinfadi daily blueberry price series | 0.5 |
| CEAI-09 | Japan prefecture blueberry area and production table (was JP-01) | 1 |
| CEAI-10 | Tokyo wholesale market monthly blueberry arrivals by origin (was JP-02) | 1.5 |
| CEAI-11 | Monthly fresh Vaccinium imports by origin (was JP-03) | 0.5 |
| CEAI-12 | JMA station table and hourly series for production districts (was JP-04) | 2 |

### 4.10 Australia and New Zealand

Full report: [regions/australia-new-zealand.md](regions/australia-new-zealand.md). Sources: 53; jobs: 11.

**The app has** Coffs Harbour, Penguin and Waikato, plus IBO records for New South Wales, Queensland, Western Australia, New Zealand, Waikato and Hawke's Bay.

**Key findings**
- **The Waikato frost is in the station record.** Hamilton Airport fell to −2.9 °C on 7 October 2022, the lowest October value since 1946. NOAA hourly data show air below 0 °C from 14:00 to 19:00 UTC on 6 October, and a grower measured −4.8 °C. MPI classified it a medium-scale adverse event on 10 December 2022. Blueberries NZ put the loss at 1,200 to 1,400 t of about 3,650 t.
- **Penguin's 58 modelled chill hours are a cell artefact.** Devonport Airport logged 555 hours below 7.2 °C from May to August 2023.
- **Stats NZ** publishes free monthly blueberry exports by country from 2015.
- **Australian statistics.** The Hort Innovation handbook gives harvest availability by state and month, and tunnels or polyhouses gave 42.7% of 2023/24 volume. ABS state series run from 2020-21 to 2024-25.
- **Dated declarations and company reports.** DisasterAssist lists Coffs Harbour events (October 2021 storms, February 2022 floods). Company reports date crop losses: Costa lost 200 t to the Tumbarumba fire in 2019/20.
- **The Tasmania peak conflict is a dating issue:** use January to February with a March shoulder.

**Still missing:**
- a primary source for the Coffs Harbour pruning month;
- access to MPI pages (bot wall; Inland Revenue mirrors the classifications).

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [NIWA / Earth Sciences New Zealand monthly climate summaries (incl. October 2022)](https://niwa.co.nz/climate-and-weather/monthly) | stations, losses, literature | open | opened |
| [DataHub access to the National Climate Database (CLIDB), replacing CliFlo](https://data.niwa.co.nz/pages/clidb-on-datahub) | stations | free registration | opened |
| [NOAA Integrated Surface Database (global-hourly) for AU/NZ stations near blueberry sites](https://www.ncei.noaa.gov/access/services/data/v1) | stations | open | opened |
| [SILO Australian climate data (point and gridded)](https://www.longpaddock.qld.gov.au/silo/) | gridded weather, stations | open | opened |
| [Australian Horticulture Statistics Handbook, Berries - Blueberries chapter](https://www.horticulture.com.au/about-hort-innovation/what-we-do/data-and-insights/australian-horticulture-statistics-handbook) | statistics, shipments/exports, land use/census | open | opened |
| [Stats NZ Agricultural Production Statistics: blueberry area by territorial authority (via Figure.NZ) and national series](https://www.stats.govt.nz/information-releases/agricultural-production-statistics-year-to-june-2022-final/) | land use/census, statistics | open | opened |
| [Stats NZ overseas merchandise trade datasets, HS10 exports by country (HS 0810400001 blueberries, fresh)](https://www.stats.govt.nz/large-datasets/csv-files-for-download/overseas-merchandise-trade-datasets/) | shipments/exports | open | opened |
| [Oz Group Co-op booklet 2025 (seasonal berry calendar)](https://ozgroupcoop.com.au/about/) | industry reports, phenology | open | opened |
| [Disaster Assist: Australian disasters list (DRFA activations by AGRN)](https://www.disasterassist.gov.au/find-a-disaster/australian-disasters) | declarations | open | opened |
| [NSW Reconstruction Authority natural disaster declarations by financial year](https://www.nsw.gov.au/departments-and-agencies/nsw-reconstruction-authority/about-us/recovery/natural-disaster-declarations) | declarations | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| ANZ-01 | Waikato October 2022 frost station table | 1.0 |
| ANZ-02 | NZ monthly fresh blueberry export series | 1.0 |
| ANZ-03 | Australian production, seasonality and tunnel-share table | 1.5 |
| ANZ-04 | AU and NZ disaster and adverse-event records for blueberry districts | 2.0 |
| ANZ-05 | Station climate tables for AU/NZ benchmark sites | 2.0 |
| ANZ-08 | Tasmania season-timing reconciliation | 0.5 |

### 4.11 Global trade, market and industry intelligence

Full report: [global/market-trade-industry.md](global/market-trade-industry.md). Sources: 64; jobs: 10.

**Key findings**
- **Tariff lines.** Only the US, Chile and Mexico separate blueberries in their tariff lines. The EU and UK line CN 0810 40 50 mixes highbush blueberry with American cranberry. Peru has one Vaccinium line.
- **Which trade data can time the harvest.** Monthly trade can time harvest for origins that export almost only blueberries: Peru, Chile, Mexico, Morocco and South Africa. For US and Canadian origins, use US HTS10 imports or AMS movement data.
- **AMS WA_FV408** gives weekly shipments by origin, archived November 2017 to April 2025, then continues through the MyMarketNews API with a free key.
- **Eurostat Comext** monthly data by origin go back to 2000 with no key. A worked example shows the 2024/25 Peruvian season start shifting to early October.
- **About 25 public-domain USDA FAS GAIN blueberry reports** cover 11 countries.

**Rights.** Trade press works only as a link index:
- FreshPlaza and Hortidaily declare `ai-input=no` (verified for FreshPlaza);
- five other publishers forbid reproduction;
- some old articles return HTTP 410.

The report's section "Harvest timing from shipment curves" gives the quantile method, the lags and the comparison with model windows.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [UN Comtrade (Comtrade+), HS 081040 monthly and annual trade by reporter and partner](https://comtradeplus.un.org/) | shipments/exports | free registration | opened |
| [Eurostat Comext DS-045409 'EU trade since 1988 by HS2-4-6 and CN8', CN 0810 40 50 and related lines](https://ec.europa.eu/eurostat/web/international-trade-in-goods/database) | shipments/exports | open | opened |
| [US Census Bureau International Trade API (imports by HS10, country and district, monthly)](https://www.census.gov/data/developers/data-sets/international-trade.html) | shipments/exports | free registration | opened-limited |
| [US Harmonized Tariff Schedule REST service, headings 0810.40, 0811.90.20, 0813.40.20](https://hts.usitc.gov/) | regulation | open | opened |
| [Arancel Aduanero Nacional de la República de Chile (Diario Oficial núm. 43.124, CVE 2033045)](https://www.subrei.gob.cl/estudios-y-documentos/documentos/detalle-otras-fichas-y-reportes/arancel-aduanero-nacional-de-la-rep%C3%BAblica-de-chile) | regulation | open | opened |
| [Arancel de Aduanas 2022 (Perú), subpartida 0810.40.00.00](https://www.sunat.gob.pe/legislacion/procedim/normasadua/gja-04/ctrlCambios/anexos/Arancel_2022.pdf) | regulation | open | opened |
| [Acuerdo de NICO (Números de Identificación Comercial), DOF 22 agosto 2022, fracción 0810.40.01](https://www.diputados.gob.mx/LeyesBiblio/ref/ligie_2022/LIGIE_2022_acuerdo02_22ago22.pdf) | regulation | open | opened |
| [USDA FAS GAIN attaché reports on blueberries and berries](https://www.fas.usda.gov/data/search?keyword=blueberry) | industry reports, statistics, management | open | opened |
| [AMS Fruit and Vegetable Weekly U.S. Commodity Shipment Reports - Blueberries (WA_FV408, MMN slug 3251, discontinued)](https://mymarketnews.ams.usda.gov/viewReport/3251) | shipments/exports | open | opened |
| [AMS Daily Movement Report - All Fruits and Vegetables (FVDDAILY_MOV, MMN slug 3264)](https://www.ams.usda.gov/mnreports/fvddaily_move.pdf) | shipments/exports | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| GLOBAL-01 | Tariff-line concordance table | 0.5 |
| GLOBAL-02 | AMS weekly blueberry movement backfill and continuation | 3.0 |
| GLOBAL-03 | Monthly origin curves from EU, US and UK customs | 2.0 |
| GLOBAL-04 | Season metrics and anomaly table from shipment curves | 2.0 |
| GLOBAL-05 | FAS GAIN blueberry report claims and events | 2.0 |

### 4.12 Global phenology, cultivar, land-use, weather and literature sources

Full report: [global/phenology-weather-landuse-literature.md](global/phenology-weather-landuse-literature.md). Sources: 78; jobs: 9.

**Key findings**
- **Open phenology data cover cool climates only.**
  - USA-NPN (CC BY 4.0) holds 4,898 highbush and 2,716 lowbush onset records; none lie within 100 km of the Florida, Georgia or Michigan benchmark sites, but they cluster near Cherryfield and Hammonton.
  - iNaturalist adds 97 flowering and 91 fruiting annotations near Cherryfield.
- **A cultivar trait table** can be built from the HortScience register, US plant patents and the UPOV TG/137 scale.
- **Stations.** GHCNh puts a station within 25 km of 39 of the 53 benchmark sites; Linares and Chillán stations are under 1 km away.
- **Land use.** CDL blueberry accuracy is low (45% producer's, 39% user's, 2024). EuroCrops maps blueberry for 11 datasets, including Spain 2023 and Portugal 2021.
- **Weather.** ERA5-Land now has a point time-series service. PRISM's 800 m grids appear to be free now; recheck the terms.
- **Literature counts.** OpenAlex returned 140 to 153 hits (a free key has been needed since February 2026); INIA Chile 621 'arándano' records; ALICIA 870; J-STAGE 168. The report specifies the literature-mining pipeline.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [USA-NPN National Phenology Database (Nature's Notebook) and data API](https://www.usanpn.org/data/observational) | phenology | open | opened |
| [UPOV Test Guidelines TG/137/5 Rev. Blueberry](https://www.upov.int/documents/d/upov/tg-documents-en-tg137.pdf) | cultivar traits, regulation | open | opened |
| [US plant patents for blueberry (Google Patents full text and USPTO image PDFs)](https://patents.google.com/patent/USPP24876P3/en) | cultivar traits | open | opened |
| [Register of New Fruit and Nut Cultivars (Brooks and Olmo), HortScience, blueberry section](https://doi.org/10.21273/hortsci19596-26) | cultivar traits | open | opened |
| [USDA NASS Cropland Data Layer, class 242 Blueberries (CroplandCROS)](https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php) | land use/census, remote sensing | open | opened |
| [EuroCrops harmonised parcel crop labels (HCAT3)](https://github.com/maja601/EuroCrops) | land use/census | open | opened |
| [Cartografía de cultivos bajo plástico en la provincia de Huelva (annual reports)](https://www.juntadeandalucia.es/sites/default/files/2021-11/Informe_plastico_huelva_v210305_1.pdf) | land use/census, remote sensing, management | open | opened |
| [ERA5-Land hourly time-series (ARCO point extraction)](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries) | gridded weather | free registration | opened |
| [Global Historical Climatology Network hourly (GHCNh)](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly) | stations | open | opened |
| [Dirección Meteorológica de Chile, Servicios Climáticos](https://climatologia.meteochile.gob.cl/) | stations, losses | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| GL-01 | Citizen phenology observations near pins (USA-NPN and iNaturalist) | 2.5 |
| GL-02 | Cultivar trait table from registers, patents and test guidelines | 6.0 |
| GL-03 | Literature mining of dated stage observations | 8.0 |
| GL-04 | Hourly station truth table near benchmark sites | 4.0 |

### 4.13 Global losses, extreme events and the validation design

Full report: [global/losses-extremes-validation.md](global/losses-extremes-validation.md). Sources: 46; jobs: 10.

**Key findings**
- **RMA** is the only blueberry-specific loss series found anywhere: crop code 0012, county by month, 1989 to 2026. The coordinator verified the 2022 figures on the server.
- **Cause codes and strata.** The RMA cause codes cover most model families, including insufficient chilling (45) and plant disease (81). The business files split insured acres into highbush and rabbiteye, and into fields with and without frost protection; in Georgia, 6,545 of 9,700 insured highbush acres are frost-protected.
- **Other US event sources.** FSA designations date freezes to the day. Storm Events has no Georgia or North Carolina frost rows for March 2022, so it cannot serve as a freeze list.
- **Outside the US there is no open blueberry-specific loss series.** Substitutes:
  - DesInventar (most Latin American series end by 2015);
  - Brazil's SISSER (personal data);
  - official declarations;
  - Chile's 2013 ODEPA frost study (4,761 t of blueberries lost).
- **The validation design** covers all eight risk families, with matching rules, metrics, confounders and a pre-registration file. 2022 is held out of the headline score because it has already been examined.

**P1 sources**

| Source | Data type | Access | Checked |
|---|---|---|---|
| [Cause of Loss, Summary of Business with Month of Loss (colsom files)](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss) | losses, insurance | open | opened |
| [Summary of Business, State/County/Crop with Coverage Level and Type/Practice/Unit Structure files (sobcov, sobtpu)](https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business) | insurance, land use/census, management | open | opened |
| [FCIC Appendix III / M13 Handbook Exhibit 21: Cause of loss codes by crop (RY 2010)](https://pubfs-rma.fpac.usda.gov/pub/Publications/M13_Handbook/2010/approved/REC21EXH.PDF) | insurance, regulation | open | opened |
| [USDA FSA Disaster Designation Information (Secretarial and Presidential designation files)](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) | declarations | open | opened |
| [ARiMR support for fruit growers hit by spring frost or hail (2024 programme)](https://www.gov.pl/web/arimr/wsparcie-dla-poszkodowanych-przez-przymrozki-lub-grad-rolnikow-ktorzy-uprawiaja-owoce--trwa-nabor) | declarations, regulation | open | opened |

**P1 jobs**

| Job | What it builds | Days |
|---|---|---:|
| GLOBAL-01 | RMA blueberry cause-of-loss backfill, 1989-2026 | 2.0 |
| GLOBAL-02 | RMA insured exposure by county, type and frost-protection practice | 1.0 |
| GLOBAL-03 | FSA Secretarial designations with peril flags and day dates | 1.0 |

## 5. How the ingestion and RAG system should work

Full design: [architecture/rag_ingestion_architecture.md](architecture/rag_ingestion_architecture.md). It keeps Astra's principles:
- documents, claims and events stay separate;
- editions and revisions are preserved;
- rights are recorded per source;
- the LLM proposes extractions offline and a person approves them;
- answers cite their sources first;
- weather calculations never read evidence.

| Part | Design |
|---|---|
| Source registry | One JSON registry generalising `ibo_report_inventory.json`: identity, URLs, family, languages, cadence, rights and allowed use, acquisition status, checksums |
| Storage | Raw files, extracted text and manifests under the server's project drive. Raw files are immutable, and derived files are keyed by input hash and tool version. Nothing raw goes to Git |
| Jobs | One YAML job plus a small Python adapter per source. systemd user timers (cron fallback) instead of tmux. Conditional fetches, retries that honour Retry-After, JSON logs with rotation, and guards on the root disk and temporary directories (the 5 October disk-full incident) |
| Extraction | Poppler text layer and pdfplumber tables, OCR only for image pages, HTML with hidden-text warnings, APIs and spreadsheets. Original-language quotes are the citation basis. Deterministic unit and number parsing (for example, "92.900" in Spanish means 92,900). The LLM proposes; it never converts units or decides conflicts |
| Schemas v2 | Document, claim, event, phenology observation, loss record, time-series point, station observation and cultivar trait, with admin-1 and admin-2 geography (geoBoundaries with the licence recorded per boundary; GADM excluded). The 91 IBO records import unchanged, and a golden test re-exports `ibo-regional-v1.json` exactly |
| Retrieval | SQLite FTS5 with hard filters on geography, crop, season and evidence type. Chinese text is indexed as character pairs, because the trigram tokenizer cannot match 蓝莓. Embeddings come only if a held-out test gains at least 0.05 recall@10 without losing citation precision. Abstain when evidence is missing |
| App | A separate loopback evidence API on port 8788 that never touches the weather lock. A breeder brief view joins model outputs to evidence by deterministic rules, not by an LLM. The weather app keeps working when evidence fails |
| Evaluation | 80 breeder questions with gold records or "must abstain", extraction precision and recall on labelled samples, and prompt-injection fixtures |

Phased plan: phases 0 to 6 take about 44 builder-days. Phase 7 (embeddings and cited answers) takes 7 more days, and only if the gates are met. Suggested first families: RMA, stations at the Chilean and New Zealand discrepancy sites, the Chilean weekly crop report, then the Michigan updates (once access is agreed), literature and news.

## 6. Whole-setup improvement plan

Effort is in builder-days for one builder with AI assistance; the estimates are inferences. Each phase lists what it unblocks. Phases A and B can run together; C needs B's station table; D's infrastructure supports B and C, but its document side can start later.

### Phase A: stabilise and correct (about 10 days)

| # | Work | Days | Why |
|---|---|---:|---|
| A1 | Run the API under a systemd user service with `Restart=on-failure`. If systemd is unavailable, set `TMUX_TMPDIR` and `TMPDIR` on the project drive and add a `df -h /` preflight. Rotate logs, and log one JSON line per request with no coordinates | 1.5 | The 5 October outage: tmux could not start on a full root disk |
| A2 | Add a result cache keyed by method, coordinates and input hashes. Run each analysis in a subprocess with a deadline, report `busy_since`, and reuse the primary result inside `sensitivity()` | 2 | One slow request currently blocks everyone, and v3 runs twice per request |
| A3 | Add Host and Origin checks in the Python handler and a Sec-Fetch-Site check in the proxy. Add CSP and nosniff headers and a shared `safeURL`. Decide whether to keep the `modelContext` agent tool | 1 | Cross-site requests can start analyses; hardening before team use |
| A4 | Implement the approved scan accounting:<br>- separate four outcomes: completed, thermal requirement not reached, weather incomplete, freeze exposure;<br>- report a separate "cycle failed" frequency;<br>- show chill shortfall on the Overview when unmet chill is why the winter calendar is missing (nine sites).<br>Add regression tests, regenerate snapshots and check legacy parity | 3 | Approved by Paul; removes a blind spot and the stall-as-freeze labelling |
| A5 | Corrections:<br>- re-run the Chile and Waikato checks: window 25 October to 15 November 2022, 3 by 3 cells, local-night minima, GHCNh, RAN and NIWA stations; re-label the old results;<br>- fix the stale v3 risk note (`production.py:939`) and add a v3 header to the phenology review and audit JSON;<br>- check the Mexico 74.20 citation visually | 2 | Astra's event checks reached the wrong conclusion |
| A6 | Planting decision with Paul. Three options: his budbreak offsets, the current home-garden windows, or commercial windows (HS1525, Embrapa). Ask what "planting" means in his R workflow | 0.5 | The current window overrides his requirement without sign-off |

### Phase B: ground truth and validation (about 15 days)

| # | Work | Days | Depends on |
|---|---|---:|---|
| B1 | Minimal evidence infrastructure: registry schema, manifests, job runner with guards and timers (architecture phases 0 and 2, trimmed) | 5 | A1 |
| B2 | RMA cause-of-loss and business tables, 1989 to 2026, with a cause-to-family crosswalk and the protected and unprotected strata | 3 | B1 |
| B3 | Station truth table: GHCNh for the 39 sites with a station within 25 km, plus FAWN, RAN, RIA paired stations, Hamilton, Devonport, Western Cape and INMET. Report Tmin bias and frost hit and miss rates by month | 4 | B1 |
| B4 | Pre-registered US freeze validation. Paul signs and hashes the file first; tune on odd seasons, score once on even seasons, keep 2022 out of the headline; report POD, FAR, Peirce, AUC and Spearman | 2.5 | B2, B3 |
| B5 | FSA designations and Storm Events as dated event records for the six Southeast states | 1 | B1 |

### Phase C: phenology calibration (about 22 days, gated on B3 and on Paul's crop choices)

| # | Work | Days | Data |
|---|---|---:|---|
| C1 | Cultivar trait table: chill, bloom and ripening classes from the HortScience register, plant patents, UPOV TG/137, the Poplarville dataset and the IFAPA trials | 6 | Global and US Southeast reports |
| C2 | Approved cool-climate profiles:<br>- lowbush (CIPRA base 0 °C);<br>- northern highbush (base 7 °C from 1 January; MSU Jersey; VBB);<br>- half-high (Finland).<br>Validate on held-out years from UMaine, RAP, VBB, USA-NPN and Rutgers | 5 | US North and West, Europe |
| C3 | Recalibrate the coastal Peru managed cycle on thesis endpoints (pruning to first harvest, main bloom to bulk harvest) and SENAMHI stages | 3 | Peru and Mexico |
| C4 | Station-based correction of the minimum-temperature cold tail and flags for sea-dominated cells (Penguin) | 3 | B3 |
| C5 | Tunnel offsets from the paired RIA stations, feeding the management layer | 2 | Iberia |
| C6 | Risk-gate refinements: per-stage-day rates or multi-day events for harvest rain and disease, an interval-aware display at the 50% boundary, a freeze severity column, and overlapping stage windows | 3 | Science review |

### Phase D: evidence platform and breeder brief (about 30 days)

Architecture phases 1 and 3 to 6:
- schemas v2 with the golden IBO test;
- structured families: NASS, AMS, ODEPA, BCRP and MIDAGRI, SIAP, DataComex, Comext, Stats NZ, CIREN census;
- documents and review: the Chilean weekly crop report, SENAMHI bulletins, the Junta weekly posts, JRC MARS, extension libraries with clear licences;
- FTS5 retrieval and the evidence API;
- the breeder brief view;
- evaluation on 80 breeder questions.

### Phase E: team access and engineering hygiene (about 10 days)

- Authenticated team access (FastAPI behind Tailscale or Cloudflare Access, per the 21 September product report); needs Rohit's and IT's approval.
- Tests for the proxy, the HTTP handler, eastern and dateline longitudes, leap years and JavaScript stale-response races.
- Generate threshold text from the profiles, and share helpers across files.
- Align local-solar and UTC days; fix the leap-year median shift.

### First 30 days, concretely

1. A1 to A3 (service, cache, security).
2. A4 (approved scan accounting).
3. A5 (event checks and stale texts).
4. A6 (planting meeting with Paul).
5. B1 to B3 (infrastructure, RMA, stations).
6. B4 (pre-registered freeze validation).
7. In parallel, send the data requests in section 7.

## 7. Decisions and requests that need a person

| Who | Decision or request | Why |
|---|---|---|
| Paul | What "planting" means in his workflow; which planting option to show | Current window lacks sign-off (A6) |
| Paul | Target crops and cultivars for cool-climate work: northern highbush, lowbush, half-high | Needed before C2 settings ship |
| Paul | Sign the pre-registration file for the US freeze validation | Prevents tuning to the answer (B4) |
| Paul | Accept benchmark note changes: Zimbabwe peak August to September, Tasmania January to February, SIAP to 2025 | These change benchmark scoring |
| Rohit | Free registrations: NASS Quick Stats, MyMarketNews, OpenAlex, NIWA DataHub, PEP725, Copernicus CDS (ERA5-Land licence), Epagri/Ciram | Needed for continuity of the US series and for stations |
| Rohit | Fill in the free IBO form for the 2021 and 2024 reports | No legitimate public copy exists |
| Rohit or IT | Enable systemd user lingering on the server, or approve cron | Phase A1 and the job scheduler |
| Rohit and UF | Rights policy for sources with no stated terms (architecture decision D7) | Decides what may appear in public `dist/` files |
| Rohit and UF | Which LLM may propose extractions (interactive sessions, a local model, or a UF-approved service) | Architecture decision D3 |
| Lab email | Data requests, without web forms: Proarándanos (weekly exports), SENASA Peru, Berries ZA (weekly exports and varieties by province), MSU (access to fruit updates), IFAPA (RIA bulk data), Epagri (Planalto Norte records), Instytut Ogrodnictwa and LWK Niedersachsen (cultivar dates), Berries Australia (Coffs Harbour pruning month), RAN, EEAOC and INTA (bulk station pulls) | These sources hold data the web cannot give |

## 8. Rights, access and compliance rules for every new job

- **Do not bypass access controls.** Bot walls protect MSU (the agent found a CMS host that skips the wall: do not use it), smallfruits.org, Agroseguro and MPI. Ask for access, or read manually.
- **Respect content signals.** FreshPlaza and Hortidaily declare `ai-input=no` and block AI crawlers. Use them as a human-written link index only. Five other publishers forbid reproduction.
- **Follow stated licences.**
  - UF/IFAS EDIS is CC BY-NC-ND 4.0: quote it, do not publish paraphrased derivatives.
  - The HortScience register is CC BY-NC 4.0.
  - USA-NPN, the CIREN-ODEPA census, CNSF and the Cerro Azul data are CC BY.
  - US federal data are public domain where the page says so; record "terms not found" otherwise.
  - Agrométéo Québec forbids redistribution, ACES is All Rights Reserved, and China's NMC forbids reuse without written permission.
- **Personal data.** Brazil's SISSER files and Chilean producer polygons identify people or farms. Store them privately and publish aggregates only.
- **Registrations.** SiAR requires a Spanish ID number, so we cannot register. CMA requires real-name registration. Several APIs need free keys; keep keys outside the project tree.
- **Downloads stay on the server.** Research agents saved some temporary files in local `/tmp`. Cleanup is recorded in section 2.5. Future jobs write only to the project drive with disk guards.
- **The IBO rules still apply.** Keep publication year, crop season and event date separate. Repeated mentions are not independent confirmation. A missing record is not evidence of no damage.

## 9. Verification and limits of this research

- **Agent verification.** 686 of 824 unique sources were opened and matched their description; 120 were partly reachable; 18 were seen only in search results. Each research agent sampled its top 10 sources, and the reports describe real fields.
- **Coordinator checks.** The coordinator re-ran or re-read the high-impact claims listed in section 2.5. All matched except one figure: the US Southeast report gave Bacon County's all-causes total as its March freeze loss, now corrected. The checks also confirmed that the 1 November 2022 date in the benchmark registry is an industry reporting date; stations put the Chilean frost on 31 October.
  The coordinator did not re-check every number in the regional reports. Treat region-report numbers as agent-verified unless section 2.5 lists them.
- **No bulk ingestion was run.** Only small samples and one RMA year (deleted afterwards) were read. Source availability changes: NASS state reports and the AMS weekly report stopped in 2025, and NOAA GSOD stopped in August 2025.
- **Effort figures are inferences** by the research agents and the coordinator.
- **This package changes no model behaviour.** Section 3.3 findings need the Phase B and C jobs and pre-registered checks before any constant changes.
