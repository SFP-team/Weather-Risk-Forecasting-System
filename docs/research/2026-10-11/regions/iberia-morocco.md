# Source research: Spain, Portugal and Morocco (`iberia-morocco`)

Checked on 2026-10-11. Companion JSON: `docs/research/2026-10-11/regions/iberia-morocco.sources.json` (81 sources, 12 jobs). My own reasoning is marked [inference]. Portugal and Morocco sources were opened by two helper agents working to the same verification rules; I spot-checked the Odemira rule against a second source.

## 1. Scope and summary

I covered Spain (Huelva and the north), Portugal (Odemira and the Mira irrigation scheme, Centro and Norte) and Morocco (Loukkos and Gharb, Souss-Massa). I looked for statistics, trade series, weather stations, loss and insurance data, management rules, dated phenology, cultivar data and narrative reports. I searched in Spanish, Portuguese, French and English. The JSON lists 81 sources: 73 opened, 8 opened-limited. Priorities: 27 P1, 26 P2, 28 P3.

### 1.1 Five most valuable findings

1. **Huelva has paired open-air and under-plastic weather stations.** The IFAPA RIA network lists stations flagged "Bajo plástico": El Cebollar 21/102 next to open-air 21/101 in Moguer, Almonte 21/103 next to 21/10, Palos de la Frontera 21/107, and Lepe 21/106 (now inactive) next to 21/2 ([station list](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/estaciones)). El Cebollar has daily data from 17-09-2001 ([station 21/101](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/estacion/21/101)). The same network feeds SiAR, whose API serves hourly temperature and humidity after a free registration ([SiAR API manual](https://servicio.mapa.gob.es/siarweb/documentos/manuales/ManualTecnico_WEB_API_SIAR.pdf)). This lets us measure tunnel warming and humidity directly, and correct the warm Tmin bias in the Moguer cell.
2. **There are official, dated, sub-provincial blueberry stage notes for Huelva.** The Junta's weekly "Estado de los cultivos" posts say, for example, that blueberry bloom ended and fruit set began in Andévalo and Condado Campiña in the week of 25-31 May 2026, with heat damage to flowers ([post](https://estadisticasagrariasypesquerascom.wpcomstaging.com/2026/06/03/estado-de-los-cultivos-y-la-ganaderia-85/)). After storm Garoé in late January 2025, they reported the Snow and Ventura harvest about 20 days late ([A en verde copy](https://www.aenverde.es/comienzan-las-plantaciones-de-sandia-en-los-invernaderos/)). The Observatorio's annual synthesis adds the share of volume sold each month (55.4% in April-May 2025/26) and a peak in the second half of May 2026 ([Síntesis 2025/26](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?action=DownloadS&element=5534749&field=DOCUMENTO&table=12030)).
3. **Cultivar-level harvest dates exist for Moguer and Odemira.** IFAPA's 2020/21 trial at El Cebollar gives harvest start and end per cultivar, with covered and uncovered plots. Examples: Cupla 15 Feb to 6 May; Star 12 Mar to 30 Jun; Legacy, uncovered, 15 May to 30 Jun ([IFAPA 2020/21 PDF](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/servifapa/index.php/registro-servifapa/91f47311-fc8b-4ff0-a41a-397a6542aad5/download)). In Portugal, the INIAV CompetitiveSouthBerries manual gives Duke harvest percentiles at Fataca (Odemira): in tunnel, 5% on 10 Apr and 50% on 5 Jun; in open air, 5% on 25 Jun and 50% on 17 Jul ([manual](https://www.iniav.pt/images/publicacoes/livros-manuais/Manual_GO_CompetitiveSouthBerries.pdf)). An Évora thesis gives 2011 bloom dates per cultivar ([thesis](https://dspace.uevora.pt/rdpc/handle/10174/15277)).
4. **Tunnel share now has official numbers.**
   - Spain-wide: ESYRCE 2025 puts 5,017 of 6,380 ha of blueberry under "invernadero" (about 79%) ([ESYRCE 2025](https://www.mapa.gob.es/es/dam/jcr%3A4ab54d2c-65ad-4ec7-a248-33e16e3f4d0b/ComentariosEspana2025.pdf)).
   - Huelva: protected area has been mapped every year since 2004, by municipality. The 2026 estimate is 15,520 ha, all berry crops together, with 3,687 ha in Moguer ([cartography 2026](https://www.juntadeandalucia.es/sites/default/files/2026-04/260406%20Informe_cultivos_protegidos_huelva_v260330.pdf)).
   - Odemira: RCM 179/2019 caps greenhouses, high tunnels, tunnels and estufins at 40% of the total area of the Mira irrigation scheme (AHM), with greenhouses at most 30%. The earlier park rules allowed 30% greenhouses plus up to 80% with estufins and tunnels ([DRE](https://diariodarepublica.pt/dr/detalhe/resolucao-conselho-ministros/179-2019-125633667); confirmed by the [government release](https://portugal.gov.pt/gc22/comunicacao/comunicados/resolucao-do-conselho-de-ministros-reduz-area-de-estufas-no-parque-natural-do-sudoeste-alentejano-e-costa)).
5. **Monthly trade series exist in all three countries, with uneven access.**
   - Spain: DataComex has monthly exports by province and TARIC from 1995 ([metadata](https://datacomex.comercio.es/Metadata/Comex)).
   - Portugal: the INE API returns monthly exports for HS6 081040 ([indicator 0008149](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0008149&lingua=PT)).
   - Morocco: the open Office des Changes database has a national code for fresh blueberries (0810400010) from 1998. Every query needs a reCAPTCHA ([portal](https://services.oc.gov.ma/DataBase/CommerceExterieur/presentation.htm)). Morocco Foodex (formerly EACCE) keeps its export data behind a login.

### 1.2 Answers to the brief's questions

1. **Huelva calendars, evergreen management, macrotunnel share, weekly data.**
   - **Calendar.** Harvest runs January to July, mainly March to June ([Datos básicos 2023/24](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?ec=default&action=DownloadS&table=11113&element=4891826&field=DOCUMENTO)). The insurance order defines an "extra temprano" blueberry cycle (harvest 1 Jan-30 Apr) for the Huelva, Cádiz and Sevilla comarcas ([Orden APA/461/2026](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-10316)).
   - **Pruning.** RAIF gives the dates: the second half of May for the earliest varieties, June to early July for mid and late ones ([RAIF 26/06/2024](https://www.juntadeandalucia.es/agriculturapescaaguaydesarrollorural/raif/manejo-previo-a-la-poda-del-scirtothrips-aurantii-en-el-cultivo-del-arandano-2/)).
   - **Weekly stage notes.** The Estado de los cultivos posts give them. In September 2026, Snow, Emerald and Star were in "reposo vegetativo" ([Hortidaily.es copy](https://www.hortidaily.es/article/9876566/almeria-cadiz-granada-y-huelva-estado-fenologico-de-los-invernaderos-en-la-tercera-semana-de-septiembre/)). [inference] An autumn rest period suggests that commercial Huelva plantings are not managed as true evergreens. Evergreen and zero-chill claims come only from breeders: Cupla is described as harvesting December to May ([eComercio Agrario](https://ecomercioagrario.com/trece-variedades-de-arandanos-a-examen/)). No IFAPA or Junta month-by-month planting calendar was found.
   - **Macrotunnel share.** See finding 4. The legal definition matters too: Huelva blueberry counts as "bajo invernadero" only if it is covered for the whole cycle (Orden APA/461/2026, art. 1). IFAPA trials used 600-gauge thermal plastic on early and mid cultivars, and hail net only on late ones.
   - **Weekly campaign data.** These are the Observatorio weekly follow-up reports and price tool.
   - **Aforos.** I found no published Junta aforo (pre-season crop estimate) for blueberry. The síntesis gives campaign estimates instead.
2. **Spanish statistics and trade.**
   - ESYRCE has an "ARANDANO" row split into secano, regadío and invernadero.
   - MAPA's provincial workbook has Arándano (code NC4300) rows for every province. Huelva 2025 (provisional): 4,700 ha, 66,600 t, 58,484 t sold for export ([workbook](https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/2.agricultura/3.-superficies-y-producciones-anuales/reglamento-n--543-2009/re1_frutales_no_citricos_formato_tabla_global-0.xlsx)).
   - The monthly "Avances" do not carry arándano: the August 2024 issue lists fresa and frambuesa only ([Avances agosto 2024](https://www.mapa.gob.es/dam/mapa/contenido/estadisticas/temas/estadisticas-agrarias/2.agricultura/2.-avances-de-superficies-y-producciones-de-cultivos/2024/cuaderno_agosto2024.pdf)).
   - Trade: DataComex has monthly data by province. FEPEX relays the same customs data; its database looks member-only [inference].
   - Northern Spain: SERIDA's 59-cultivar phenology (2013-2016) exists but its servers were down or returned 403 today. MAPA's campaign report charts area in Galicia, Asturias and Cantabria ([MAPA 2024/25](https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/producciones-agricolas/frutas-y-hortalizas/frutas-y-hortalizas/informacion-subsectorial/frutos-rojos/informe-campana-2024-25-frutos-rojos--oct24-ago25-.pdf)).
3. **Weather stations.**
   - **RIA.** The web pages are open and give daily data from 1999-2001 onward. The REST endpoints returned HTTP 403 from this machine, so access needs testing from the lab network or a request to IFAPA. Moguer has three stations: Moguer 21/4 (inactive), Moguer El Fresno 21/12, and El Cebollar 21/101 and 21/102. Lepe has 21/2, and Almonte 21/10 and 21/103.
   - **SiAR.** Hourly data need a free account, and the token call uses the user's DNI.
   - **AEMET OpenData.** Needs a free API key requested by e-mail ([info](https://opendata.aemet.es/centrodedescargas/info)).
   - **MeteoGalicia.** Open under CC BY-SA 4.0 ([dataset](https://abertos.xunta.gal/catalogo/medio-abiente/-/dataset/0114/estacions-meteoroloxicas)).
   - **IPMA.** The API lists Odemira S. Teotonio (1210577) but keeps only 24 hours of hourly data ([api.ipma.pt](https://api.ipma.pt/)).
   - **Morocco DGM.** The archive sits behind authentication. Open history comes from NCEI GSOD and OGIMET for Larache 60105, Kenitra 60120 and Agadir 60252.
4. **Loss data.**
   - **Agroseguro.** The site returned 403 and a Cloudflare check, so figures come through press quotes. For example, the January-February 2026 storms produced more than 5,000 claims on berry macrotunnels, about 2,500 ha affected, and 3.6 M EUR paid in Huelva by 26 Feb 2026 ([Andalucía Información](https://www.andaluciainformacion.es/articulo/andalucia/agricultores-andaluces-golpeados-borrascas-reciben-primeros-pagos-seguro-agrario/202602261314163220134.html)).
   - **ENESA.** The annual memoria gives line-level national totals. For "Fresón y frutos rojos" in 2024: 1,091 policies, 9,418.72 ha and 960,476.11 EUR in indemnities ([memoria 2024](https://www.mapa.gob.es/dam/mapa/contenido/enesa/090_publicaciones/memorias-de-actividades-de-enesa/documentos/memoria_enesa_2024_definitiva_enlinea.pdf)).
   - **Portugal SIPAC.** IFAP announces crop-insurance statistics for 1996-2017 by crop and concelho, but the tables were not reached. Storm Kristin support is documented by CCDR Alentejo ([page](https://www.drapalentejo.gov.pt/tempestade-kristin-apoios-exploracoes-agricolas-afetadas)).
   - **Morocco MAMDA.** Confirmed not open: only aggregate figures are published ([MAMDA](https://www.mamda-mcma.ma/vous-conseiller/actualites/dispositif-specifique-face-la-secheresse-2022)).
5. **Portugal.**
   - **INE.** The API gives mirtilo area and production by agrarian region. 2025: 2,708 ha and 23,701 t ([indicator 0000019](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0000019&lingua=PT)).
   - **GPP.** Only a 2016 fact sheet.
   - **Manuals.** The INIAV FLF 216 manual opens with a browser user-agent. The AJAP manual is text-based, not image-only: tunnels close in January and reopen March-April ([AJAP](https://culturasemergentes.ajap.pt/wp-content/uploads/2019/01/Manual_Culturas_Emergentes_Mirtilo_Digital-min.pdf)).
   - **Advisories.** DRAP warning bulletins are now indexed by SNAA. None of them covers berries in the Alentejo or Algarve ([SNAA](https://snaa.dgav.pt/circulares-aviso)).
   - **Producer bodies.** Lusomorango and Portugal Fresh have websites but publish no data series.
   - **Odemira rules.**
     - The 40%/30% cap above (RCM 179/2019).
     - A drought freeze on new protected crops ([Despacho 2935/2024](https://diariodarepublica.pt/dr/detalhe/despacho/2935-2024-856212566)), partly relaxed in 2025 ([Despacho 4555/2025](https://files.diariodarepublica.pt/2s/2025/04/073000000/0018900190.pdf)).
     - Restrictions reported lifted in June 2026 (Rádio M24, via the Portugal notes).
6. **Morocco.**
   - **Morocco Foodex.** EACCE was renamed Morocco Foodex, and its statistics are partner-only or need a login ([Foodex](https://www.moroccofoodex.org.ma/); [AGROSTAT](http://www.agrostat.ma/)).
   - **Office des Changes.** The database is open (see finding 5).
   - **Interproberries.** Its own domain does not resolve. The COMADER page gives undated red-fruit areas: Loukkos 5,510 ha, Souss-Massa 4,960 ha, Gharb 1,780 ha ([COMADER](https://comader.ma/interproberries/)).
   - **Ministry.** The live site timed out; it was read through 2022 Wayback copies.
   - **ONSSA.** Certification framework only.
   - **USDA.** There is no GAIN berry annual. The 2022 IATR says harvest runs September to June, with most shipments January to May ([IATR](https://www.fas.usda.gov/data/spotlight-morocco-fruit-exports)).
   - **Calendars.**
     - Loukkos: planting October to mid-March, greenhouses uncovered November to January, harvest November to May ([BTTA 203](https://www.agrimaroc.net/bulletins/btta_203.pdf)).
     - Souss: harvest December to May, peak mid-February, pruning June to 31 July (Agriculture du Maghreb 2017, read via a [LinkedIn repost](https://www.linkedin.com/pulse/la-myrtille-du-souss-siham-zahidi)).
   - **Tunnel share for Morocco.** Not found.

## 2. Production context in brief

- **Spain.**
  - Andalucía had 4,850 ha and an estimated 68,500 t of blueberry in 2025/26, and production is "casi al 100%" in Huelva ([Síntesis 2025/26](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?action=DownloadS&element=5534749&field=DOCUMENTO&table=12030)). Freshuelva gives 59,500 t (-6%) for the same campaign ([FEPEX](https://www.fepex.es/noticias/detalle/balance-campana-frutos-rojos-menos-produccion-exportacion)).
  - The crop is low-chill SHB under macrotunnel, on soil or substrate. Harvest runs January to July, mainly March to June, and starts earlier each year as extra-early cultivars spread ([Datos básicos](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?ec=default&action=DownloadS&table=11113&element=4891826&field=DOCUMENTO)).
  - Protected cropping concentrates in Condado Litoral (55%) and Costa (28%) ([cartography 2026](https://www.juntadeandalucia.es/sites/default/files/2026-04/260406%20Informe_cultivos_protegidos_huelva_v260330.pdf)).
  - Pruning follows harvest, from the second half of May into early July (RAIF).
  - Northern Spain (Galicia, Asturias, Cantabria) grows open-field highbush for summer harvest. These regions held 10.7% of national area in 2024 ([MAPA 2024/25 report](https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/producciones-agricolas/frutas-y-hortalizas/frutas-y-hortalizas/informacion-subsectorial/frutos-rojos/informe-campana-2024-25-frutos-rojos--oct24-ago25-.pdf)).
- **Portugal.**
  - INE gives 2,708 ha and 23,701 t in 2025. Area is largest in Entre Douro e Minho (1,055 ha), but output is highest in the Alentejo (7,739 t from 326 ha) and Beira Litoral (7,652 t) ([INE 0000019/0000021](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0000019&lingua=PT)). [inference] The Alentejo's high yield per hectare fits intensive tunnel and substrate farms around Odemira.
  - In the south-west, SHB tunnels close in January and reopen in March-April. Harvest runs April to June, with flushes in late August-September and November-December (AJAP manual).
  - The north grows mostly open-air NHB, such as Duke and Legacy (IBO record pt-system).
- **Morocco.**
  - Red fruit areas by perimeter, from an undated COMADER figure: Loukkos 5,510 ha, Souss-Massa 4,960 ha, Gharb 1,780 ha. Loukkos had 2,175 ha of blueberry in 2022-23 ([FNH](https://fnh.ma/articles/fruits-rouges-maroc-economie)).
  - Season blueberry exports in 2025/26 were 102,141 t (Foodex figure via [Blueberries Consulting](https://blueberriesconsulting.com/en/marruecos-fortalece-su-posicion-en-el-mercado-mundial-del-arandano-con-mayores-volumenes-de-produccion-y-exportacio/)).
  - Loukkos harvests November to May under greenhouses that are uncovered November to January (BTTA 203). Souss starts about one week earlier and peaks in mid-February, in canary-type greenhouses (Agriculture du Maghreb 2017).
  - Late seasons pushed the northern peak to March-April in 2024, 2025 and 2026 (AgriMaroc and FreshPlaza items in the JSON).

## 3. What the app already has for this scope

- **Benchmark sites** (`pipelines/weather/benchmark_sites.json`; results in `docs/weather/benchmark/benchmark.json`).
  - `es-hu-moguer` is a mismatch. The model says Deciduous (723 chill h), with bloom in March-April and harvest in May-June. The literature says bloom January-February and harvest January-July, so harvest recall is 0.29.
  - `pt-odemira-sao-teotonio`: the model says Semi-evergreen, harvest May-July; the literature says April-June.
  - `pt-sever-do-vouga`: Deciduous, with a harvest window narrower than May-August.
  - `ma-larache-loukkos` and `ma-agadir-souss`: Evergreen, using the managed-cycle scan. Larache is shifted about two months late (model January-July vs published November-May).
- **IBO records** in `dist/evidence/ibo-regional-v1.json` (13 in scope):
  - es-huelva-tunnels, es-huelva-harvest, es-huelva-water, es-huelva-2023-cold, es-huelva-2025-rain, es-2026-rain-cold, es-north-highchill;
  - ma-agadir-system, ma-agadir-water, ma-north-system, ma-2023-cold, ma-2025-26-rain-cold;
  - pt-system.
  - They cover the tunnel share (about 97% in Huelva per IBO 2023), season shape and the main weather years. They do not give dated stages, cultivar data, station data or municipal extents.
- **Recorded gaps**, from `benchmark_sites.json`:
  - no IFAPA/Junta month-by-month calendar or planting months for Huelva;
  - evergreen management supported only by breeder calendars;
  - the INIAV manual (403) and the Évora thesis not read;
  - no bloom months for Odemira or Sever do Vouga;
  - no official Moroccan bloom or peak calendar;
  - no Souss-specific system evidence.
- **Sources already in the repository** that I did not count as new: SERIDA phenology and SiAR (`docs/research/2026-09-21/04_validation_data_and_protocol.md`), and the Barrau et al. 2006 Huelva trial (`docs/weather/GLOBAL_PHENOLOGY_REVIEW.md`, S21). This report closes or narrows most of the listed gaps. Section 8 lists the ones it does not close.

## 4. Source inventory

Tables are generated from the JSON. "Status" is the verification status. Terms are quoted when the site states them.

### 4.1 Weather stations and climate

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Red de Información Agroclimática de Andalucía (RIA), including 'bajo plástico' stations](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/riaweb/web/) (`es-ifapa-ria-andalucia`) | ES | province id; station code; station name; active flag | open; terms not found (page states an open-data policy; data published via a REST service) | es | network operating since 1999; El Cebollar (21/101) first day 17-09-2001 to present | opened | P1 |
| [SiAR, Sistema de Información Agroclimática para el Regadío (web portal and API SiAR)](https://servicio.mapa.gob.es/siarweb/masInformacion) (`es-mapa-siar-api`) | ES | Fecha; Estacion; HorMin; TempMedia | open-with-free-registration; terms not found | es | network created 1998; more than 500 stations | opened | P1 |
| [NOAA NCEI Global Summary of the Day (GSOD) for Larache 60105099999, Kenitra 60120099999, Agadir Al Massira...](https://www.ncei.noaa.gov/access/services/data/v1) (`ma-ncei-gsod-moroccan-stations`) | MA | STATION; DATE; TEMP; MAX | open; terms not found | en | daily; 2025 rows returned; Jan 2026 query returned empty (lag or gap) | opened | P1 |
| [IPMA open data API (api.ipma.pt): station observations, concelho daily temperature/precipitation/ET0](https://api.ipma.pt/) (`pt-ipma-open-data-api`) | PT | idEstacao, localEstacao, lon/lat; hourly temperatura, humidade, precAcumulada, intensidadeVento, idDireccVento, radiacao, pressao; concelho daily mean/min/max/percentiles of maxt2m, meant2m, mint2m (zname, zid) | open; IPMA 'Condicoes de Utilizacao': free personal or public use without profit, source must always be cited; IPMA asks users to email webmaster@i... | pt | Rolling: station observations last 24 hours; concelho daily files last 20 days | opened | P1 |
| [AEMET OpenData API (observación convencional, valores climatológicos)](https://opendata.aemet.es/centrodedescargas/info) (`es-aemet-opendata`) | ES | idema; fint (hour); ta, tamin, tamax; hr | open-with-free-registration; AEMET legal notice (aviso legal): free reuse with attribution to AEMET as summarised by the climaemet package | es,en | daily climatological values for the historical station record; conventional hourly observations for the las... | opened | P2 |
| [Direction Generale de la Meteorologie (Maroc Meteo): Donnees et informations climatologiques; Observation n...](https://www.marocmeteo.ma/fr/donn%C3%A9es-et-informations-climatologiques) (`ma-dgm-marocmeteo-climatology`) | MA | products listed: hourly, 3-hourly, 06/12/18h, daily, dekadal and monthly climatological data, normals, absolute records; network: 48 staffed synoptic stations (30 airport, 4 coastal, 5 centennial), 156 automatic stations, 309 c... | restricted; terms not found | fr,ar | unknown (products sold or supplied on request) | opened | P2 |
| [OGIMET SYNOP summaries: Larache (60105), Kenitra (60120), Agadir (60250), Agadir Al Massira (60252)](https://www.ogimet.com/home.phtml.en) (`ma-ogimet-synop-larache-kenitra-agadir`) | MA | Date; Temperature Max/Min/Avg (C); Td Avg (C); Hr. Avg (%) | open; DISCLAIMER: 'The information in these pages must be taken as merely informative ... No any critical mission should use this data.' | en,es | daily summaries and raw SYNOP; [inference] archive back to about 2000 | opened | P2 |
| [MeteoGalicia: Estacións meteorolóxicas (open data JSON services)](https://abertos.xunta.gal/catalogo/medio-abiente/-/dataset/0114/estacions-meteoroloxicas) (`es-meteogalicia-estacions`) | ES | station id; station list with coordinates; daily and monthly parameters (temperature, humidity, rain, wind); last hourly data | open; Creative Commons BY SA 4.0 | gl,es | dataset registered 05-06-2013; daily, monthly, last hourly and last 10-minute services | opened | P3 |
| [WIS2 'Hourly synoptic observations from fixed-land stations (SYNOP) (ma-marocmeteo)'](https://wis2-gdc.weather.gc.ca/collections/wis2-discovery-metadata/items/urn:wmo:md:ma-marocmeteo:h6vqw6) (`ma-wis2-dgm-synop`) | MA | temperature; visibility; precipitation; pressure | open; wmo:dataPolicy 'core' | en | real time since metadata creation 2025-03-15 (no archive) | opened | P3 |
| [COTR SAGRA (Sistema Agrometeorologico para a Gestao da Rega no Alentejo) and SAGRA-Net](https://www.cotr.pt/) (`pt-cotr-sagra`) | PT | daily station data and Penman-Monteith ET0 (SAGRA-Net); hourly data only under contract (per a COTR paper seen in search) | open-with-free-registration; terms not found | pt | not verified | opened-limited | P3 |
| [IPMA Series longas (daily and monthly long series, 16 stations plus mainland aggregate)](https://www.ipma.pt/pt/oclima/series.longas/) (`pt-ipma-series-longas`) | PT | daily and monthly Tmin, Tmean, Tmax, precipitation, pressure; original and homogenised series | open; Use requires citing the source (IPMA and IDL data policy) | pt | From 1855 for some stations; mainland series from 1931 | opened | P3 |
| [SNIRH Sistema Nacional de Informacao de Recursos Hidricos (APA) meteorological and hydrometric stations](https://snirh.apambiente.pt/) (`pt-snirh-apa`) | PT | not seen | open; terms not found | pt | not verified | opened-limited | P3 |

### 4.2 Phenology, cultivar trials and traits

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Evaluación de Variedades de Arándanos (IFAPA trials at El Cebollar, Moguer; campaigns 2020/21 and 2021/22)](https://www.juntadeandalucia.es/agriculturaypesca/ifapa/servifapa/registro-servifapa/751da974-6d88-48c8-b8b7-2f88ae5d1e3f) (`es-ifapa-servifapa-evaluacion-variedades-arandano`) | ES | cultivar; breeder; planting date; system (soilless substrate under 7.2 m macrotunnel; organic soil under 6.6 m macrotunnel) | open; Creative Commons Reconocimiento-No comercial-Sin obra derivada 3.0 España (CC BY-NC-ND 3.0 ES) | es | campaigns 2020/21 (published Dec 2021) and 2021/22 (published 11/12/2022); later blueberry campaigns not found | opened | P1 |
| [Estado de los cultivos y la ganadería (weekly crop status) and Boletín Semanal de Información Agraria y Pes...](https://estadisticasagrariasypesquerascom.wpcomstaging.com/) (`es-junta-estado-cultivos-semanal`) | ES | report week (date range); province; comarca; crop (arándanos) | open; terms not found | es | weekly blog posts since November 2017; PDF bulletins for 2016-2017 and a historical archive before that | opened | P1 |
| [Tecnologias de producao de pequenos frutos para producao fora de epoca (Manual do GO CompetitiveSouthBerrie...](https://www.iniav.pt/divulgacao/publicacoes-bd/manual-do-grupo-operacional-competitivesouthberries-tecnologias-de-producao-de-pequenos-frutos-para-producao-fora-de-epoca) (`pt-iniav-competitivesouthberries-manual`) | PT | Quadro 5.4 'Duke' dates of 5%, 50%, 95% fruit harvested: open air 25 Jun / 17 Jul / 29 Jul; tunnel 10 Apr / 5 Jun / 19 Jun; cold-stored plants out 15 May: 17 Jul / 29 Jul / 14 Aug; Quadro 5.1 yield g/plant and fruit weight, Sta... | open; terms not found | pt | Trials 1994-2017 at Fataca, Odemira; book 2022 (ISBN 978-972-579-061-8) | opened | P1 |
| [Araujo Duarte (2016) Estudo fenologico e qualitativo de Vaccinium corymbosum (cultivares Duke, Draper, Chan...](http://repositorio.ipvc.pt/bitstream/20.500.11960/1963/1/Araujo_Duarte_1820.pdf) (`pt-ipvc-thesis-araujo-2016`) | PT | days after 1 January for BBCH-type phenophases per cultivar (Figura 3.1); budbreak: Ozarkblue and Draper day 80, Duke and Chandler about a week later; full bloom (stage 65) day 121 for Ozarkblue, Draper, Chandler, Duke; Legacy... | open; terms not found | pt | Weekly observations 29 Feb-17 Jul 2016 (continues 2014 and 2015 work) | opened | P1 |
| [Jesus, R.N.A. (2012) Avaliacao do comportamento agronomico de cultivares de mirtilo (Vaccinium corymbosum L...](https://dspace.uevora.pt/rdpc/handle/10174/15277) (`pt-uevora-thesis-jesus-2012`) | PT | Tabela 7 bloom start (5% open) and end (90% open): Misty and Star 11 Jan-10 Mar; Southmoon 11 Jan-25 Mar; O'Neal, Ozarkblue, Nui 26 Feb-28 Apr; Tabela 8 fruit development start/end: Misty 11 Mar-12 May; Star 11 Mar-10 May; Sout... | open; terms not found | pt | Trial planted 2009; observations 2011 season | opened | P1 |
| [SERIDA Asturias: blueberry collection phenology (59 cultivars, 2013-2016) and 'El cultivo del arándano en e...](https://www.serida.org/publicacionesdetalle.php?id=6724) (`es-serida-arandano`) | ES | cultivar; year; flower opening date; end of flowering date | open; terms not found | es | collection planted 2010; weekly phenology scoring 2013-2016 | opened-limited | P2 |
| [Jornada Técnica del Cultivo del Arándano en la Provincia de Huelva (COITAND) and breeder variety summaries](https://www.coitand.es/2024/10/15/vii-jornada-tecnica-del-cultivo-del-arandano-en-la-provincia-de-huelva/) (`es-coitand-jornada-tecnica-arandano-huelva`) | ES | cultivar; breeder; chill requirement (e.g. <100 h); harvest window months | open; terms not found | es | IV Jornadas (2017/18) to VII Jornada (6 Nov 2024) | opened | P3 |

### 4.3 Trade, shipments and prices

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [DataComex: Estadísticas del comercio exterior español (monthly, by TARIC and province)](https://datacomex.comercio.es/Metadata/Comex) (`es-datacomex`) | ES | flujo (export/import); periodo year and month; país; TARIC (CN 0810 40 and 8-digit 08104050 Vaccinium corymbosum) | open; terms not found | es | monthly 1995-2026 (definitive to 2023, provisional after) | opened | P1 |
| [AGROSTAT, Navigateur Statistique (official agri-food export statistics portal)](http://www.agrostat.ma/) (`ma-eacce-agrostat-navigateur`) | MA | unknown until access granted; [inference] product, campaign, week or month, destination, tonnes from export inspection records | on-request; terms not found | fr | unknown (behind login) | opened-limited | P1 |
| [Eurostat Comext DS-045409 'EU trade since 1988 by HS2-4-6 and CN8' (EU imports from Morocco, CN 08104050)](https://ec.europa.eu/eurostat/comext/newxtweb/) (`ma-eurostat-comext-eu-imports-from-ma`) | MA,* | freq; reporter (EU or each member state); partner (MA); product (08104050 'Fresh fruit of species Vaccinium macrocarpum and Vaccinium corymbosum') | open; Eurostat copyright notice: reuse of statistical data authorised provided the source is acknowledged (Commission Decision 2011/833/EU) | en | monthly; dataset since 1988, start year of CN8 08104050 not checked; latest value seen May 2025 in test call | opened | P1 |
| [Office des Changes, Base de donnees du commerce exterieur du Maroc](https://services.oc.gov.ma/DataBase/CommerceExterieur/presentation.htm) (`ma-office-des-changes-bdce`) | MA | Annee; Mois; Code/Libelle du produit SH (10-digit; 0810400010 'AIRELLES ET MYRTILLES FRAICHES', 0810400090 'AUTRES FRUITS FRAIS DU GENRE VACCINIUM'); Sens du flux (Exportations FAB) | open; terms not found | fr | monthly, 1998 to June 2026 (2026 provisional) | opened | P1 |
| [HMRC uktradeinfo Overseas Trade Statistics API (UK imports from Morocco, CN 08104050)](https://www.uktradeinfo.com/api-documentation/) (`ma-uk-hmrc-ots-imports-from-ma`) | MA,GB | MonthId; FlowTypeId (3 = non-EU imports); SuppressionIndex; CommodityId (8104050) | open; Open Government Licence v3.0 ('All content is available under the Open Government Licence v3.0, except where otherwise stated') | en | monthly; test call returned rows from 2024-01 | opened | P1 |
| [INE Exportacoes (kg) de bens por Local de destino e Tipo de bens (NC8); Mensal (indicator 0008149)](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0008149&lingua=PT) (`pt-ine-trade-nc8-exports`) | PT | month (Dim1 S3A<yyyymm>); destination country or aggregate (geocod: MUNDO, INTRA, ES, FR ...); goods code dim_3 (HS6 081040 'Airelas, mirtilos e outras frutas do genero Vaccinium, frescas'; CN8 08104050 also listed); export mas... | open; terms not found | pt | Monthly; last period 'Agosto de 2026' (updated 2026-10-09); start year not verified in this session | opened | P1 |
| [Informe de seguimiento, Frutos Rojos (weekly campaign follow-up), Observatorio de Precios y Mercados](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?ec=default&action=DownloadS&table=12030&element=4861974&field=DOCUMENTO) (`es-junta-opm-seguimiento-frutos-rojos`) | ES | ISO week; weekly origin price EUR/kg arándano and week-on-week change; cumulative marketed volume vs same week last campaign (%); narrative on early varieties and supply start | open; 'Se permite la reproducción total o parcial de la información incluida en esta publicación, citando su procedencia.' | es | seen for campaigns 2023/24 (week 1) and 2024/25 (weeks 50/2024 to 2/2025); older weekly issues exist in the... | opened | P2 |
| [Morocco Foodex (formerly EACCE, Etablissement Autonome de Controle et de Coordination des Exportations) web...](https://www.moroccofoodex.org.ma/) (`ma-morocco-foodex-eacce`) | MA | none publicly; Market Notes, Flash Exports and Watch Notes sit behind a partner login | restricted; terms not found | fr,ar,en | site live 2026; partner reports undated (not accessible) | opened | P2 |
| [FEPEX: export statistics service and frutos rojos news](https://www.fepex.es/servicios/mercado) (`es-fepex-estadisticas`) | ES | exports t and EUR by crop and period (from Aduanas, processed by FEPEX); Freshuelva campaign production (arándano 59,500 t in 2025/26, -6%); destination ranking | restricted; terms not found | es | news items 2024-2026 seen | opened | P3 |
| [Arándano: precios en origen (Huelva) price query tool, Observatorio de Precios y Mercados](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?action=Static&producto=11000&subsector=19&url=generadorInformesOR.jsp) (`es-junta-opm-precios-arandano-origen`) | ES | product (ARÁNDANO); price position (origen, mayorista destino, consumo); type/subtype; period | open; terms not found | es | archive depth not confirmed (the query form lets the user choose a period) | opened | P3 |
| [Boletín semanal de precios de frutas y hortalizas (MAPA)](https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/producciones-agricolas/frutas-y-hortalizas/frutas-y-hortalizas/boletin-semanal-de-precios/ano-2026/19-2026-bolet-n-semanal-de-precios-de-fyh--4-10-mayo-.pdf) (`es-mapa-boletin-semanal-precios-fyh`) | ES | ISO week; product (arándano); Huelva regional market price change %; difference vs average % | open; terms not found | es | weekly issues; 2026 week 19 opened | opened | P3 |
| [Agronometrics: Morocco Data Club (weekly exports by destination, members only) and Global Trade Data charts](https://www.freshplaza.com/north-america/article/9812013/morocco-data-club-launched-at-fruit-logistica-2026/) (`ma-agronometrics-morocco-data`) | MA | weekly export volumes by destination (contributor-submitted, anonymised); monthly export volume and weighted price by partner country | paid; '(c) 2023 Agronometrics. All rights reserved.' | en | MDC from 2026 season; GTD monthly exports by partner | opened | P3 |

### 4.4 Production, area, land use and tunnel extent

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Cartografía de cultivos bajo plástico en la provincia de Huelva (annual remote-sensing mapping)](https://www.juntadeandalucia.es/organismos/agriculturapescaaguaydesarrollorural/servicios/estadistica-cartografia/actividad/detalle/175064/175485.html) (`es-junta-cartografia-cultivos-plastico-huelva`) | ES | municipality; comarca; mapped protected area ha; estimated protected area ha (excluding paths) | open; terms not found | es | 2004-2026 (annual estimates; SigPac-based mapping since 2012; Landsat 2004-2015, Sentinel-2 since 2016) | opened | P1 |
| [ESYRCE, Encuesta sobre Superficies y Rendimientos de Cultivos (results incl. arándano by secano, regadío, i...](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/esyrce/) (`es-mapa-esyrce`) | ES | crop (ARANDANO); secano ha; regadío ha; invernadero ha | open; 'los contenidos de esta publicación podrán ser reutilizados, citando la fuente y la fecha, en su caso, de la última actualización.' | es | ESYRCE annual since 2004 (pivot table 2004-2024 mentioned); 2025 provisional results opened | opened | P1 |
| [INE base de dados: Superficie e Producao das principais culturas agricolas por Regiao agraria e Especie (in...](https://www.ine.pt/bddXplorer/htdocs/minfo.jsp?var_cd=0000019&lingua=PT) (`pt-ine-crop-area-production-api`) | PT | year (Dim1 code S7A<year>); geocod / geodsg (regiao agraria or NUTS); dim_3=11104 'Mirtilos'; area ha (0000019) | open; terms not found | pt,en | Indicator series 1986-2025 (metadata); mirtilo national total seen for 2012 (211 ha), 2015 (1 325 ha), 2017... | opened | P1 |
| [Datos básicos ARÁNDANO (annual fact sheet), Observatorio de Precios y Mercados](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?ec=default&action=DownloadS&table=11113&element=4891826&field=DOCUMENTO) (`es-junta-opm-datos-basicos-arandano`) | ES | area ha 2019/20-2023/24 (3,050 to 4,520); production t; yield t/ha; area not yet in production (310 ha in 2023/24) | open; 'Se permite la reproducción total o parcial de los datos o gráficos de esta publicación, citando su procedencia.' | es | editions 2022/23 and 2023/24 seen; each gives a 5-campaign series (2019/20-2023/24) | opened | P2 |
| [Superficies y producciones anuales de cultivos: Frutales no cítricos, tabla global (provincial arándano rows)](https://www.mapa.gob.es/es/estadistica/temas/estadisticas-agrarias/agricultura/superficies-producciones-anuales-cultivos) (`es-mapa-superficies-producciones-provincial`) | ES | PRO_ID; PRO_DESCRIPCION (province); crop code NC4300 Arándano; variable code (STRU area irrigated, SPTU area in production, PRTR production harvested, RRRU yield, VFEE sold for export, VFCF fresh domestic, VFTR processing, PLNA... | open; terms not found | es | provisional 2025 and 2024 workbooks on the page; Anuario de Estadística series in earlier years | opened | P2 |
| [Finances News Hebdo, 'Fruits rouges: la filiere genere un chiffre d'affaires annuel de 4,5 milliards de DH'...](https://fnh.ma/articles/fruits-rouges-maroc-economie) (`ma-fnh-loukkos-red-fruit-area-2022-23`) | MA | Loukkos red fruit area 2022-23: 7,042 ha (strawberry 2,822; raspberry 2,822; blueberry 2,175; other 15); national production last campaign: 36,000 t blueberries; exported share: 96% of blueberries; off-season production Nov to May | open; terms not found | fr | campaign 2022-2023 | opened | P2 |
| [Ministere de l'Agriculture: 'Filiere Petits fruits rouges' regional pages (Tanger-Tetouan-Al Hoceima; Rabat...](https://www.agriculture.gov.ma/fr/filieres-regions/petits-fruits-rouges) (`ma-minagri-filiere-petits-fruits-rouges`) | MA | region; red-fruit area ha 2008 vs 2019 (TTA 809 -> 1914; RSK 2280 -> 4102, from indicator images); share of national production (TTA ~26%; RSK 66% in 2019); share exported by crop (TTA: blueberries 95%) | open; terms not found | fr,ar | 2008 and 2019 indicators; campaign 2021-2022 export news | opened-limited | P2 |
| [INE Estatisticas Agricolas (annual publication)](https://www.ine.pt/xurl/pub/66302566) (`pt-ine-estatisticas-agricolas`) | PT | Quadro 1.1 Producao das principais culturas: Frutos pequenos de baga > Mirtilo, Superficie (ha) and Producao (t) for two years; narrative of the agricultural year weather (e.g. 2023/24 sixth warmest since 1931/32, warmest winte... | open; terms not found | pt | Editions seen: 2010, 2017, 2020, 2023, 2024 (published July 2025); mirtilo row in Quadro 1.1 at least from... | opened | P2 |
| [ORMVA du Souss-Massa website (Production vegetale; Agriculture en chiffres)](https://www.ormvasm.ma/index.php/fr/2013-11-30-16-45-33/production-vegetale.html) (`ma-ormva-souss-massa`) | MA | primeurs under cover 8,031 ha vs open field 8,527 ha (2012/13); crop area/production/exports table (no berries) | open; 'Copyright 2014 (c) Tous droits reserves' | fr,ar | campaign 2012/2013 | opened | P3 |

### 4.5 Losses, insurance and disasters

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Agroseguro: informe de siniestralidad, eventos más significativos por cultivos, and press releases](https://agroseguro.es/sala-de-prensa/informe-de-siniestralidad/eventos-mas-significativos-por-cultivos/) (`es-agroseguro-siniestralidad`) | ES | event date; hazard (lluvia persistente, viento, inundación, pedrisco, helada); crop group (fresón y frutos rojos); area declared ha | open; terms not found | es | annual siniestralidad reports (2023 report URL seen); event pages per year | opened-limited | P2 |
| [Orden APA/461/2026 (BOE-A-2026-10316): seguro de explotaciones de fresón y otros frutos rojos (Línea 328 co...](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2026-10316) (`es-boe-orden-apa-461-2026-seguro-frutos-rojos`) | ES | blueberry harvest cycle (extra temprano 1 Jan-30 Apr; temprano 15 Mar-30 Jun; media estación 15 Jun-31 Aug; tardío 1 Aug-1 Nov); protection system (invernadero vs aire libre); eligible comarcas per cycle; end of guarantee dates | open; terms not found | es | published 12 May 2026 (yearly orders exist for earlier plans) | opened | P2 |
| [CCDR Alentejo: Tempestade Kristin - Apoios as exploracoes agricolas afetadas (legislation list and quarterl...](https://www.drapalentejo.gov.pt/tempestade-kristin-apoios-exploracoes-agricolas-afetadas) (`pt-ccdra-kristin-apoios`) | PT | legal acts: RCM 15-B/2026 (calamity, 30 Jan), 15-C/2026, 17-A/2026, 24-A/2026, Despacho 1335-A/2026 (Kristin recognised as catastrophe; PEPAC C.4.1.3), DL 40-A/2026, DL 79-A/2026, Portarias 86-A/2026/1, 181/2026/1, 296-B/2026/1... | open; terms not found | pt | Storm 28 Jan-Feb 2026; measures Jan-Oct 2026 | opened | P2 |
| [IFAP Seguro de Colheitas e Vitícola: estatisticas 1996-2017 (by year, crop and concelho)](https://www.ifap.pt/portal/web/guest/home/-/asset_publisher/OppM0H3bXzAg/content/id/11290127) (`pt-ifap-sipac-seguro-colheitas`) | PT | year; crop; concelho; capital seguro | open; terms not found | pt | 1996-2017 | opened-limited | P2 |
| [Memoria de ENESA: principales indicadores del seguro agrario](https://datos.gob.es/en/catalogo/ea0022323-https-www-mapa-gob-es-es-enesa-publicaciones-memoria_enesa) (`es-enesa-memoria`) | ES | insurance line (FRESÓN Y FRUTOS ROJOS); policies; insured area ha; insured production kg | open; datos.gob.es aviso legal (terms of use) | es | annual memorias (2024 edition opened) | opened | P3 |
| [Fonds de Solidarite contre les Evenements Catastrophiques (FSEC)](https://fsec.ma/) (`ma-fsec-catastrophic-events-fund`) | MA | declared catastrophic events (decree in Bulletin officiel); scope: bodily injury and loss of principal residence of uninsured households | restricted; terms not found | fr,ar | operational since about 2020 | opened-limited | P3 |
| [MAMDA assurance multirisque climatique (cereals and fruit-tree climate insurance)](https://www.mamda-mcma.ma/vous-conseiller/actualites/dispositif-specifique-face-la-secheresse-2022) (`ma-mamda-multirisque-climatique`) | MA | perils covered for arboriculture: grele, gel, vents violents, chergui, exces d'eau, hautes temperatures; 3.8 billion DH indemnified in total; 1 million ha insured 2021-22 | restricted; terms not found | fr | press items 2016-2022 | opened | P3 |

### 4.6 Management rules, advisories and manuals

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Agriculture du Maghreb (agri-mag.com), Fruits Rouges section and archive](https://www.agri-mag.com/category/arboriculture/fruits-rouges/) (`ma-agri-mag-fruits-rouges`) | MA | Souss: harvest December to May (available Dec-Jun), peak mid-February, pruning June to 31 July, greenhouses uncovered Nov-Jan, ~300 ha hors-sol and 50 ha soil (Mar 2017), canary greenhouses, misting against chergui, cultivars V... | open; 'Copyright Agri-mag 2026' | fr,ar | 2017-2026 (articles seen Mar 2017 via LinkedIn repost, Mar 2026, Jun 2026) | opened | P1 |
| [Bulletin de Transfert de Technologie en Agriculture n 203 (July 2016), 'Conduite technique de la Myrtille'...](https://www.agrimaroc.net/bulletins/btta_203.pdf) (`ma-btta-203-myrtille-inra-tanger`) | MA | planting period Oct to mid-March; greenhouses uncovered (plastic removed, shade kept) November to January; chill requirement by group (NHB ~1000 h; SHB 150-500 h; rabbiteye 400-600 h); cultivars named (Misty, Star) | open; terms not found | fr | trials 2014-2016 at INRA Larache experimental station | opened | P1 |
| [Despacho n.o 2935/2024 (19 Mar 2024) and Despacho n.o 4555/2025 (14 Apr 2025): water security measures in t...](https://diariodarepublica.pt/dr/detalhe/despacho/2935-2024-856212566) (`pt-dre-despachos-mira-water`) | PT | 2024: temporary ban on new permanent crops and on new protected crops (estufas, tuneis elevados, tuneis, estufins) except Varzea da ribeira de Corte Brique block; no water for new precarious protected crops; Santa Clara reservo... | open; terms not found | pt | 2023 (Despacho 5084/2023, revoked) to 2025; 2026 campaign restrictions lifted per ABM (news) | opened | P1 |
| [Resolucao do Conselho de Ministros n.o 179/2019 (regime especial e transitorio do Aproveitamento Hidroagric...](https://diariodarepublica.pt/dr/detalhe/resolucao-conselho-ministros/179-2019-125633667) (`pt-dre-rcm-179-2019-mira`) | PT | n.o 9 a): greenhouses, high tunnels, tunnels and estufins limited to max 40% of AHM area; greenhouses max 30%; redelimitation criteria (exclude PNSACV partial protection I/II, complementary protection I, 100 m cliff strip; tota... | open; terms not found | pt | In force from Oct 2019; Grupo de Projeto do Mira mandate 10 years | opened | P1 |
| [Manual de Boas Praticas de Fruticultura, 8.o Fasciculo: Mirtilo (Pedro Bras de Oliveira, INIAV; FLF Revista...](https://www.iniav.pt/images/publicacoes/livros-manuais/FLF_216_Manual_de_fruticultura_Mirtilo.pdf) (`pt-iniav-manual-mirtilo-flf216`) | PT | Figura 5 production calendar by region (south: tunnel/plastic SHB; north: open-air NHB, RE); open-air harvest from late April/early May to end of September; heated-plastic tunnels advance harvest about two months; Portugal can... | open; terms not found | pt | Published about 2020-2021 (cites Oliveira 2020) | opened | P1 |
| [SNAA Servico Nacional de Avisos Agricolas: consulta de circulares por cultura e inimigo](https://snaa.dgav.pt/circulares-aviso) (`pt-snaa-circulares-index`) | PT | Ea (station); NomeCircular; Data (issue date); Ano | open; terms not found | pt | 2 130 circulars indexed, 2006-2026 (most 2009-2026) | opened | P1 |
| [Datos obtenidos del seguimiento de plagas y enfermedades en las estaciones de control biológico [2006-2026]...](https://www.juntadeandalucia.es/datosabiertos/portal/dataset/raif) (`es-junta-raif-datos-abiertos`) | ES | PROVINCIA; MUNICIPIO; PARCELA (plot file RAIF_[Cultivo]_Parcelas); sampling records RAIF_[Cultivo]_Muestreos by province | open; terms not found | es | 2006-2026 (Fresa file 2007-2026) | opened | P2 |
| [RAIF, Red de Alerta e Información Fitosanitaria: frutos rojos pages and Huelva bulletins](https://www.juntadeandalucia.es/agriculturapescaaguaydesarrollorural/raif/manejo-previo-a-la-poda-del-scirtothrips-aurantii-en-el-cultivo-del-arandano-2/) (`es-junta-raif-frutos-rojos`) | ES | article date; crop; pest or disease; management timing (pruning window) | open; terms not found | es | RAIF since 1996; frutos rojos articles seen for 2024-2025 | opened | P2 |
| [Manual Boas Praticas para Culturas Emergentes: A Cultura do Mirtilo (AJAP, 2017)](https://culturasemergentes.ajap.pt/wp-content/uploads/2019/01/Manual_Culturas_Emergentes_Mirtilo_Digital-min.pdf) (`pt-ajap-manual-mirtilo`) | PT | open-air NHB in the north, production May to August; SW Alentejo tunnel studies: cover closed in January after chill, reopened March-April; harvest April-June, second flush late August-September, third Nov-Dec; two export windo... | open; terms not found | pt | 2017 edition (upload 2019) | opened | P2 |
| [Estacao de Avisos de Entre Douro e Minho: Circulares (CCDR Norte)](https://agrodigital.ccdr-n.pt/sia/Avisos-Agr%C3%ADcolas/Circulares) (`pt-ccdrn-eaedm-circulares`) | PT | issue date and place; weather narrative of past days (e.g. June 2026 showers 1.5-16 mm on the 25th; 6 mm on 14 June); 'MIRTILOS EM CULTURA DE AR LIVRE' section with crop stage (end of harvest) and D. suzukii advice; mass trappi... | open; terms not found | pt | Circulars at least 2018-2026 (SNAA index) | opened | P2 |
| [Guia Tecnico de Protecao Integrada dos Pequenos Frutos - Parte I: Amora, Framboesa, Morango e Mirtilo (INIA...](https://iniav.pt/divulgacao/publicacoes-bd/guia-tecnico-de-protecao-integrada-dos-pequenos-frutos-parte-i-amora-framboesa-morango-e-mirtilo) (`pt-iniav-guia-pi-pequenos-frutos`) | PT | pest and disease sheets per crop with 'Registar o estado fenologico' monitoring steps; infection conditions, e.g. Botrytis favoured by RH >95% and 15-20 C (seen in text) | open; terms not found | pt | Edition January 2025 | opened | P2 |
| [Plan Especial de Ordenación de las zonas de regadío al norte de la Corona Forestal de Doñana (Decreto 178/2...](https://www.juntadeandalucia.es/boja/2014/254/18) (`es-junta-plan-especial-regadios-donana`) | ES | irrigable parcel zones; groundwater extraction limits; municipalities; plan category of each zone | open; terms not found | es | approved Dec 2014; commission changed by Decreto 140/2025 | opened | P3 |
| [ONSSA, Controle a l'importation et a l'exportation / Certification a l'exportation](https://www.onssa.gov.ma/controle-a-limportation-et-a-lexportation/) (`ma-onssa-export-certification`) | MA | control directorates (Casablanca, Tanger, Agadir) and border posts; legal basis Loi 28-07; export certificate requirement | open; terms not found | fr,ar,en | page modified 2023-02-27 | opened | P3 |
| [USDA FAS GAIN 'Morocco: Technical Regulation on 'Red Fruit' (Berries)' (MO2018-3519, 21 June 2018)](https://www.fas.usda.gov/data/gain/2018/06/morocco-technical-regulation-red-fruit-berries) (`ma-usda-gain-red-fruit-regulation-2018`) | MA | MinAg Order No. 2109-17 on production of strawberry, raspberry, blueberry, blackberry, gooseberry, blackcurrant; imported plant material must be in the official Moroccan variety catalogue from 5 Oct 2018 | open; terms not found [inference: US federal work] | en | 2018 | opened | P3 |
| [Produzir Mirtilos (COTHN, projeto Cluster dos Pequenos Frutos, ficha tecnica)](https://www.cothn.pt/files/1305_MTPMirtil_532afd5d3c6c1.pdf) (`pt-cothn-produzir-mirtilos`) | PT | site selection items (frequency and intensity of frosts, chill hours, rain probability at harvest); weekly harvest every 3 to 7 days; spacing 0.8-1.5 m x 2.5-3.0 m; soil pH 4.5-5.5 | open; terms not found | pt | PDF created March 2014 | opened | P3 |
| [Mirtilos: guia de boas praticas para producao, promocao e comercializacao (Mirtilusa / AGIM / ADRIMAG, 2008)](https://www.mirtilusa.com/documentos/manual_mirtilo.pdf) (`pt-mirtilusa-manual`) | PT | Sever do Vouga about 60 t from about 80 producers; 95% exported (2007); fruit placed on EU market in May/June; chill at least 700 h at about 7 C; risk of late cold after flower opening; >30 C scorching | open; terms not found | pt | Project Sept 2007-Aug 2008; PDF created June 2008 | opened | P3 |

### 4.7 Industry reports, research and news (RAG corpus)

| Source | Country | What it contains | Access and terms | Language | Coverage | Status | Priority |
|---|---|---|---|---|---|---|---|
| [Síntesis de campaña: Frutos Rojos (provincia de Huelva), Observatorio de Precios y Mercados](https://ws142.juntadeandalucia.es/agriculturaypesca/observatorio/servlet/FrontController?action=DownloadS&element=5534749&field=DOCUMENTO&table=12030) (`es-junta-opm-sintesis-frutos-rojos`) | ES | campaign; area ha (fresa, frambuesa, arándano) Andalucía 4 campaigns; production t by crop 4 campaigns; share of volume marketed per month (arándano: 55.4% in April-May 2025/26) | open; 'Se permite la reproducción total o parcial de la información incluida en esta publicación, citando su procedencia.' | es | campaigns 2018/19 to 2025/26 seen (2018/19 cited by a UCA paper; 2019/20 record dated 18-11-2020; 2023/24 a... | opened | P1 |
| [AgriMaroc.ma blueberry and red fruit news archive (Actu' Export, Culture de la myrtille)](https://www.agrimaroc.ma/production/baies/culture-de-la-myrtille/) (`ma-agrimaroc-berry-news`) | MA | article date; region; event type (cold delay, flood, wind); stage at event (floraison / debut de nouaison) | open; terms not found | fr | articles seen 2025-02 to 2026-03; archive [inference] back to about 2016 | opened | P1 |
| [FreshPlaza (EN/FR) Morocco soft fruit season reports (Amine Bennani, Moroccan Association of Soft Fruit Pro...](https://www.freshplaza.com/north-america/article/9850943/morocco-s-soft-fruit-exports-down-5/) (`ma-freshplaza-morocco-soft-fruit-reports`) | MA | season fresh blueberry exports (89,236 t 2025-26 vs 83,929 t 2024-25); regional change (Loukkos -16%, Souss-Massa +33%, Meknes 127 t vs 614 t, Oriental 112 t vs 16 t); frozen blueberry exports (5,841 t vs 7,019 t); weather even... | open; terms not found | en,fr | 2023-2026 seen (season reports each year) | opened | P1 |
| [Freshuelva (Asociación Onubense de Productores y Exportadores de Fresas) news and campaign statements](https://freshuelva.es/) (`es-freshuelva`) | ES | campaign area ha by berry (planting survey of member firms); campaign production t; season delay narrative; technical day summaries | open; terms not found | es | news since at least 2017/18 (article on 2017/18 campaign seen) | opened | P2 |
| [Análisis / Informe de campaña de frutos rojos (MAPA subsector reports)](https://www.mapa.gob.es/dam/mapa/contenido/agricultura/temas/producciones-agricolas/frutas-y-hortalizas/frutas-y-hortalizas/informacion-subsectorial/frutos-rojos/informe-campana-2024-25-frutos-rojos--oct24-ago25-.pdf) (`es-mapa-informe-campana-frutos-rojos`) | ES | area and production by crop vs 5-year mean; monthly export volume t (Eurostat, Oct-Aug); destinations; unit values | open; terms not found | es | campaigns 2021/22, 2023/24 and 2024/25 seen | opened | P2 |
| [Agence Ecofin, 'Maroc : 33 millions $ pour attenuer l'impact des inondations sur l'agriculture' (2 Mar 2026)](https://www.agenceecofin.com/actualites-agro/0203-136272-maroc-33-millions-pour-attenuer-l-impact-des-inondations-sur-l-agriculture) (`ma-ecofin-gharb-loukkos-floods-2026`) | MA | ~105,000 ha farmland affected (85,000 Gharb; 20,000 Loukkos); disaster declaration mid-February 2026; 300 MDH support announced 27 Feb 2026 at Kenitra | open; terms not found | fr | Feb 2026 | opened | P2 |
| [INTERPROBERRIES MAROC (Federation interprofessionnelle des fruits rouges) page on the COMADER site](https://comader.ma/interproberries/) (`ma-interproberries-comader`) | MA | Exportations 204 132 t; Production annuelle 229 500 t; Marche local 25 368 t; Superficie de culture 12 250 ha | open; '(c) Copyright 2026. Comader All rights reserved' | fr | single undated snapshot (image uploaded 2024-09) | opened | P2 |
| [USDA FAS International Agricultural Trade Report 'Spotlight: Morocco Fruit Exports' (10 Nov 2022)](https://www.fas.usda.gov/data/spotlight-morocco-fruit-exports) (`ma-usda-fas-iatr-morocco-fruit-2022`) | MA | blueberries harvested September through June; bulk of fresh blueberry shipments January through May; production spread to Dakhla-Oued Ed-Dahab; EU market share 23% (27,000 t) in 2021 | open; terms not found [inference: US federal work] | en | 2016-2021 | opened | P2 |
| [Meteored/tempo.pt (9 Feb 2026): Depressao Kristin arrasa cultura dos pequenos frutos em Odemira](https://www.tempo.pt/noticias/actualidade/depressao-kristin-arrasa-cultura-dos-pequenos-frutos-em-odemira-perdeu-se-entre-50-a-70-da-capacidade-produtiva.html) (`pt-news-kristin-odemira`) | PT | Lusomorango: about 40 member growers, provisional direct losses >10 M EUR, 50-70% of productive capacity lost (tunnels, irrigation, equipment); Lusomorango 17% of national small-fruit production; sector exports 348 M EUR in 202... | open; terms not found | pt | Feb 2026 | opened | P2 |
| [AEMET Resúmenes climatológicos (monthly, seasonal and annual climate summaries)](https://www.aemet.es/en/serviciosclimaticos/vigilancia_clima/resumenes) (`es-aemet-resumenes-climatologicos`) | ES | month; temperature anomaly; precipitation % of normal by region; named storms and wind gust records by station | open; AEMET legal notice | es | monthly summaries; January to June 2026 listed on the page; archive by year | opened | P3 |
| [Spanish agri-press on Huelva berries (A en verde, Andalucía Información, Huelva Red, Revista Mercados, Fres...](https://www.andaluciainformacion.es/articulo/andalucia/agricultores-andaluces-golpeados-borrascas-reciben-primeros-pagos-seguro-agrario/202602261314163220134.html) (`es-press-huelva-berries`) | ES | article date; event; affected crops and ha; claims count | open; terms not found | es | 2017-2026 articles seen | opened | P3 |
| [USDA FAS GAIN: Spanish Berry Outlook (SP2023-0024, 3 July 2023)](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Spanish+Berry+Outlook++_Madrid_Spain_SP2023-0024.pdf) (`es-usda-gain-spanish-berry-outlook-2023`) | ES | planted area by berry (blueberry 4,138 to 4,278 ha); MAPA production estimate 2022/23 (70,381 t); drought narrative; trade | open; US federal government work (public domain) | en | 2023 report | opened | P3 |
| [Blueberries Consulting, Morocco articles (season totals quoting Morocco Foodex, IBO; Larache 2026 delays)](https://blueberriesconsulting.com/en/marruecos-fortalece-su-posicion-en-el-mercado-mundial-del-arandano-con-mayores-volumenes-de-produccion-y-exportacio/) (`ma-blueberries-consulting-morocco`) | MA | 2025/26 exports 102,141 t (fresh 92,510; processed 9,631), +7%, per Morocco Foodex; fresh exports 89,236 t, +6%; Feb-Mar 2026 shipments down, Apr-May above normal; Larache 2026: wind, cold and storms delayed; peak expected earl... | open; terms not found | es,en,fr,pt | 2024-2026 seen | opened | P3 |
| [HortitecNews, 'Tempetes au Maroc : la production de myrtilles chute de plus de 20 % dans le Souss-Massa' (1...](https://www.hortitecnews.com/tempetes-maroc-myrtille-souss-massa-baisse-production-2026/) (`ma-hortitecnews-souss-storm-2026`) | MA | event dates 26-27 Feb 2026; expected 2026 production loss 15-25%, >50% on some farms (IBO estimate relayed); week 9 harvested volume vs previous year; smaller fruit size from low light and cold | open; terms not found | fr | 2026 | opened | P3 |
| [INRA Maroc, Centre Regional de la Recherche Agronomique de Tanger (fiches techniques, programme petits frui...](https://tanger.inra.org.ma/) (`ma-inra-crra-tanger`) | MA | no myrtille fiche found; fiches listed: fraisier, avoine, noyer; research programme line 'Contribution au developpement de la filiere des petits Fruits rouges' | open; terms not found | fr,ar | site 2024-2026 | opened | P3 |
| [Capital do Mirtilo - Sever do Vouga: Mirtilo de Sever do Vouga](https://www.capitaldomirtilo.pt/mirtilo-de-sever-do-vouga/) (`pt-capitaldomirtilo-sever`) | PT | harvest May to August; hundreds of smallholder producers on south-facing terraces; introduced 1990 (Fundacao Lockorn); Mirtilusa founded 1994; Feira Nacional do Mirtilo since 2008; most farms GlobalG.A.P. | open; terms not found | pt | Page published 2020-07-12, modified 2026-06-09 | opened | P3 |
| [Governo de Portugal comunicado: Pequenos frutos atingem 398 milhoes de euros em exportacoes (10 June 2026)](https://portugal.gov.pt/pt/gc25/comunicacao/comunicados/pequenos-frutos-atingem-398-milhoes-de-euros-em-exportacoes-e-reforcam-peso-na-agricultura-portuguesa) (`pt-gov-pequenos-frutos-2026`) | PT | small-fruit exports 2025 (398 M EUR, +17% y/y); mirtilo area 2 670 ha; framboesa 1 564 ha; main destinations ES, NL, FR | open; terms not found | pt | 2025 figures, 2020-2024 trend | opened | P3 |
| [GPP Ficha de Internacionalizacao: Pequenos Frutos Vermelhos - Mirtilo e Framboesa, Amora e Groselha](https://www.gpp.pt/images/gam/1/fi/PequenosFrutosVermelhosFI.pdf) (`pt-gpp-ficha-pequenos-frutos`) | PT | SWOT headings: Cenario de antecipacao, Breve caracterizacao, Analise interna pontos fortes/fracos, Oportunidades, Fatores criticos de sucesso | open; terms not found | pt | Created 18 Nov 2016 (PDF metadata) | opened | P3 |


### 4.8 Top 10 sources: what an actual sample showed

1. **RIA station 21/101 (El Cebollar) and station list.**
   - The daily table has columns Fecha, Día Juliano, Temp. Máxima, Hora Temp Máxima, Temp. Mínima, Hora Temp Mínima, Temp. Media, Humedad Relativa Máxima/Media/Mínima, Velocidad Viento Media/Máxima, Dirección Viento Media, Radiación (MJ/m2 d), Precipitación (mm) and ETo (mm/día).
   - Sample row: 08-10-2026, Tmax 29.1 at 15:44, Tmin 13.6 at 6:48.
   - The station list has columns Id, Provincia, Nombre, Activa, Altitud, **Bajo plástico**, Huso, Latitud, Longitud, Visible, XUTM and YUTM.
2. **Estado de los cultivos, week of 25-31 May 2026.** Free text by province and comarca. The blueberry line names the stage ("finaliza ... la floración y se entra en la de cuajado") and the damage ("El calor y el sol han dañado parte de las flores").
3. **IFAPA blueberry variety evaluation 2020/21.**
   - Table 4 columns: Variedad, inicio recolección, fin recolección, días, g/planta/día. Ten cultivars, e.g. "Cupla 15 febrero 6 mayo 80 31".
   - Table 3 gives monthly yield February to July.
   - Methods give the planting date (December 2019), the tunnel width (7.20 m) and the cover type.
4. **Junta Síntesis de campaña 2025/26.**
   - Tables for area (ha) and production (t) by crop for 2022/23 to 2025/26.
   - Text giving the April-May share of blueberry volume (55.4%).
   - Export table for January-June: Volumen (t) and Valor (miles EUR) for three campaigns.
   - Protected-area paragraph naming the top municipalities.
5. **Huelva plastic cartography 2026.** Table 6 has rows MUNICIPIO and year columns 2004 to 2026, plus 26-25 ha, 26-25%, 26-04 ha and 26-04%. Example: MOGUER 2,357 ... 3,687.
6. **MAPA provincial workbook, 2025 provisional.**
   - Sheet BD_HORTALIZAS-NO has columns PRO_ID, PRO_DESCRIPCION, CSP_DCW_AB1234 (NC4300), CSP_CLV_TXT_FORMULARIO (Arándano), CSP_DCW_TXYZ (variable code) and CSP_DCW_VALOR.
   - Huelva rows: STRU 4700, PRTR 66600, RRRU 14866, VFEE 58484, PLNA 180.
   - The ESYRCE 2025 row reads "ARANDANO 95 1.268 5.017 6.380".
7. **INE Portugal API** (helper agent sample).
   - JSON keys: IndicadorCod, Dados{period:[rows]}. Row keys: geocod, geodsg, dim_3, dim_3_t, valor.
   - Example: `{"geocod":"6","geodsg":"Alentejo","dim_3":"11104","dim_3_t":"Mirtilos","valor":"326"}`.
   - Exports (0008149) for May 2025, HS6 081040: world 689,597 kg.
8. **INIAV CompetitiveSouthBerries Quadro 5.4 and Évora thesis Tabela 7.**
   - Quadro 5.4 columns: Tratamento, 5%, 50%, 95% harvest dates for Duke. Ar livre 25/jun, 17/jul, 29/jul; Túnel 10/abr, 05/jun, 19/jun.
   - Tabela 7 columns: Cultivar, Início, Final and Duração of bloom. Example: "Misty 11 Jan. 10 Março 8".
9. **Office des Changes BDCE** (Morocco).
   - Query axes include chapter and product code and label, flow direction, partner country, Mois and Année. Indicators are Poids en Kg, Valeur en MAD and Unité complémentaire.
   - The product lookup returned `0810400010 - AIRELLES ET MYRTILLES FRAICHES`.
10. **FreshPlaza Morocco season-close report, mid-2026.**
    - Fresh and frozen export tonnes by product, this season vs last.
    - Regional changes: Loukkos -16%, Souss-Massa +33%.
    - Narrative causes: floods early in the year, labour shortage, price fall from late April.

## 5. Proposed extraction and RAG jobs

All jobs follow the IBO design rules: document, claim and event records stay separate; every record carries citations; LLM extraction is proposed offline and reviewed by a person. The JSON `rag_jobs` holds the full objects.

**IBM-01: Huelva paired open-air and under-plastic station table** (P1, about 2.0 days)

- Sources: `es-ifapa-ria-andalucia`, `es-mapa-siar-api`, `es-aemet-opendata`.
- Output: station table. Method: API pull. Cadence: one-off backfill 2001-2026 (daily RIA) and SIAR hourly for the same stations, then weekly.
- Fields: station_key (province-code, e.g. 21-101); network (RIA | SIAR | AEMET); name; lat; lon; altitude_m; under_plastic (bool); pair_id (21-101/21-102 El Cebollar; 21-10/21-103 Almonte; 21-2/21-106 Lepe; 21-107 Palos); active; first_date; last_date; date; hour (SIAR HorMin); t_mean_c; t_min_c; t_min_time; t_max_c; t_max_time; rh_mean; rh_min; rh_max; precip_mm; wind_mean_ms; radiation; eto_mm.
- Human review: Confirm RIA REST access from the lab network (403 here); confirm SIAR registration works for a non-Spanish user; check under-plastic station crop and cover periods with IFAPA; flag gaps and sensor changes.
- Licensing gate: RIA and SIAR terms not found; ask IFAPA/MAPA before publishing derived station values. AEMET requires attribution.
- App value: Measured tunnel warming and humidity offsets for the Huelva cell, station Tmin to correct the +1 C MERRA-2 bias, and observed frost and chill counts at Moguer, Almonte and Lepe.

**IBM-02: Huelva campaign evidence library (official weekly and annual narratives)** (P1, about 3.0 days)

- Sources: `es-junta-opm-sintesis-frutos-rojos`, `es-junta-opm-seguimiento-frutos-rojos`, `es-junta-estado-cultivos-semanal`, `es-junta-raif-frutos-rojos`, `es-freshuelva`, `es-mapa-informe-campana-frutos-rojos`, `es-press-huelva-berries`.
- Output: claim records. Method: layout-aware PDF tables. Cadence: one-off backfill 2017/18-2025/26, then weekly in season (Dec-Jul) and annual after the Síntesis appears (September).
- Fields: kind (claim | event | practice); topic (timing | weather | management | market); period (start, end, precision: week | month | season); crop_context (blueberry; cultivar names when given; covered vs uncovered); evidence_type (official_statistics | official_narrative | industry_statement | press); geography (ES-H; comarca names Condado Litoral, Costa, Andévalo, Condado Campiña); citations (document, page, quote, URL, retrieved_on); stage (floración, cuajado, recolección, reposo vegetativo); delay_days; monthly_volume_share.
- Human review: Separate blueberry statements from strawberry and raspberry; reconcile conflicting production totals (Junta 68,500 t vs Freshuelva 59,500 t for 2025/26); de-duplicate against IBO records es-huelva-harvest, es-huelva-2023-cold, es-huelva-2025-rain and es-2026-rain-cold; keep weekly stage notes as observations only when a comarca and week are stated.
- Licensing gate: Junta Observatorio PDFs allow reproduction with attribution; blog and RAIF terms not found (cite and quote briefly); press: short quotes and links only.
- App value: A dated, citation-first Huelva record of season start, peak month, bloom and fruit-set weeks, storm and heat damage, and pruning windows to test the es-hu-moguer calendar and risk families.

**IBM-03: Spanish cultivar harvest and phenology table** (P1, about 1.5 days)

- Sources: `es-ifapa-servifapa-evaluacion-variedades-arandano`, `es-serida-arandano`, `es-coitand-jornada-tecnica-arandano-huelva`.
- Output: cultivar table. Method: manual review. Cadence: one-off.
- Fields: cultivar; breeder; species_group (SHB | NHB | RE); site; season; system (substrate | soil; macrotunnel thermal plastic | hail net | open); planting_date; bloom_start; bloom_end; harvest_start; harvest_end; harvest_duration_days; monthly_yield_g_plant; chill_requirement_h (breeder claim); evidence_grade (trial | collection | breeder_claim); citation.
- Human review: Keep breeder claims apart from trial observations; note IFAPA plants were young and in substrate; for SERIDA filter non-commercial taxa and use 25%-ripe definition for harvest start.
- Licensing gate: IFAPA reports are CC BY-NC-ND 3.0 ES: store facts and cite, do not republish tables; SERIDA and press terms not found.
- App value: First cultivar classes for Iberia: low-chill SHB under cover (Feb-May), mid SHB (Mar-Jun) and uncovered late cultivars (mid-May to July) in Moguer, plus NHB bloom and harvest dates for Asturias.

**IBM-04: Spain monthly blueberry export and production panel** (P1, about 1.0 days)

- Sources: `es-datacomex`, `es-junta-opm-datos-basicos-arandano`, `es-mapa-superficies-producciones-provincial`, `es-mapa-esyrce`.
- Output: time series table. Method: CSV parse. Cadence: one-off backfill 1995-2026, then monthly (exports) and annual (area, production).
- Fields: country=ES; province (Huelva, Sevilla, Asturias, A Coruña, Lugo, Pontevedra); year; month; cn_code (08104050 and HS6 081040); flow=export; partner; kg; eur; area_ha; area_in_production_ha; production_t; yield_kg_ha; protected_area_ha (ESYRCE invernadero); source; provisional_flag.
- Human review: Check CN8 code history for Vaccinium; customs province vs growing province; mark provisional years (2024 onward).
- Licensing gate: DataComex terms not found; MAPA ESYRCE allows reuse with citation; confirm before public display.
- App value: Year-specific monthly harvest curves for Huelva to compare with modelled harvest windows and to detect delayed seasons (2023, 2025, 2026); national tunnel share prior.

**IBM-05: Huelva protected-cropping extent and insurance cycle definitions** (P2, about 1.0 days)

- Sources: `es-junta-cartografia-cultivos-plastico-huelva`, `es-boe-orden-apa-461-2026-seguro-frutos-rojos`, `es-junta-plan-especial-regadios-donana`.
- Output: time series table. Method: layout-aware PDF tables. Cadence: one-off backfill 2004-2026, then annual (April release).
- Fields: municipality; comarca; year; mapped_protected_ha; estimated_protected_ha; insurance_cycle (extra temprano | temprano | media estación | tardío); cycle_harvest_window; protection_definition; frost_area_class; citation.
- Human review: Protected area is all berries and some fruit trees; do not label it blueberry area. Keep insurance windows as legal priors, not observations.
- Licensing gate: Cartography terms not found; BOE text is public legislation.
- App value: Municipality tunnel density for location weighting in Huelva and official cycle windows for the managed-cycle scan.

**IBM-06: Spain berry weather-loss events** (P2, about 1.0 days)

- Sources: `es-agroseguro-siniestralidad`, `es-enesa-memoria`, `es-aemet-resumenes-climatologicos`, `es-press-huelva-berries`.
- Output: event records. Method: manual review. Cadence: one-off backfill 2018-2026, then after each insurer release.
- Fields: kind=event; topic=weather; hazard (lluvia persistente | viento | inundación | helada | pedrisco | calor); period (start, end, precision); geography (ES-H; comarca); crop_context (fresón y frutos rojos; blueberry share unknown); claims_count; area_ha; indemnity_eur; named_storm; evidence_type (insurer_statement | official_statistics | press); citations.
- Human review: Agroseguro pages are behind a bot wall: a person must open and copy figures. Berry totals mix crops. Link each event to the AEMET monthly summary for the same dates.
- Licensing gate: Agroseguro terms not found; quote figures with attribution only.
- App value: Sized, dated storm and rain events (22 Oct 2023; Jan-Feb 2026) to validate harvest_heavy_rain and add a wind/structure risk for tunnels in the Huelva cell.

**IBM-20: INE Portugal blueberry area, production and monthly exports** (P1, about 1.0 days)

- Sources: `pt-ine-crop-area-production-api`, `pt-ine-trade-nc8-exports`, `pt-ine-estatisticas-agricolas`.
- Output: time series table. Method: API pull. Cadence: one-off backfill (one call per year or month), then annual for area and production, monthly for exports.
- Fields: country=PT; region (regiao agraria geocod/geodsg; NUTS II where available); year; crop=mirtilo (dim_3 11104); area_ha; production_t; month; destination (geocod); export_kg (dim_3 081040); source_indicator; data_last_updated.
- Human review: Confirm first year with regional values; confirm why CN8 08104050 is zero and keep HS6 081040; tag the HS6 cranberry/bilberry mix caveat
- Licensing gate: INE reuse terms were not found on the pages opened; confirm the INE dissemination policy before public display
- App value: Regional weight for Portuguese evidence and a monthly export curve to check modelled harvest timing and storm years

**IBM-21: Portuguese dated blueberry phenology and harvest percentiles** (P1, about 1.0 days)

- Sources: `pt-iniav-competitivesouthberries-manual`, `pt-uevora-thesis-jesus-2012`, `pt-ipvc-thesis-araujo-2016`, `pt-ajap-manual-mirtilo`, `pt-iniav-manual-mirtilo-flf216`.
- Output: event records. Method: manual review. Cadence: one-off.
- Fields: kind=phenology_observation; topic (bloom_start, bloom_end, harvest_5pct, harvest_50pct, harvest_95pct, budbreak, full_bloom); period (date or day-of-year, season year); crop_context (cultivar, species group SHB/NHB/RE, open air or tunnel, substrate or soil); geography (site name, lat/lon if printed); evidence_type=trial; citations (table number and page).
- Human review: Confirm the season year for the Fataca Duke table (planted spring 2012 [inference: 2013 harvest]); separate manual calendars (schematic) from observed dates
- Licensing gate: Theses and INIAV manuals: no licence stated; cite and store only extracted facts
- App value: First observed, cultivar-specific Portuguese stage dates to calibrate bloom and harvest offsets for the Odemira and Sever do Vouga benchmark sites

**IBM-22: Odemira policy, drought and storm event records plus northern disease warnings** (P2, about 1.0 days)

- Sources: `pt-dre-rcm-179-2019-mira`, `pt-dre-despachos-mira-water`, `pt-ccdra-kristin-apoios`, `pt-news-kristin-odemira`, `pt-snaa-circulares-index`, `pt-ccdrn-eaedm-circulares`.
- Output: claim records. Method: HTML scrape. Cadence: one-off backfill, then weekly poll of the SNAA index for new mirtilo circulars.
- Fields: kind (regulation, drought_restriction, disaster_declaration, storm_loss, disease_warning); topic; period (act date, effect dates, circular date); crop_context (protected crops, small fruits, mirtilo); geography (AHM / Odemira, Aljezur; EA region); evidence_type (law, official notice, industry estimate, advisory); citations (DRE id, paragraph; circular number).
- Human review: Quote the exact paragraph for each legal limit; label industry loss estimates as such; check each SNAA circular's blueberry section before tagging stage or disease
- Licensing gate: Diario da Republica text is public legislation; news excerpts quoted briefly with links; SNAA PDFs: no licence found
- App value: Management-layer cap (<=40% covered) and dated drought and storm events for the Odemira cell, plus dated Botrytis and SWD warnings for northern blueberries

**IBM-30: Morocco monthly blueberry export and arrival series (OC + Eurostat + HMRC)** (P1, about 1.5 days)

- Sources: `ma-office-des-changes-bdce`, `ma-eurostat-comext-eu-imports-from-ma`, `ma-uk-hmrc-ots-imports-from-ma`.
- Output: time series table. Method: API pull (Eurostat, HMRC); manual CSV export per year from Office des Changes (reCAPTCHA). Cadence: one-off backfill (OC 1998-2026; Comext and OTS full depth), then monthly.
- Fields: country=MA; series_source; flow (export FAB / EU import / UK non-EU import); product_code (0810400010 | 08104050); year; month; partner; net_mass_kg; value_local_currency; currency; campaign (Sept-Aug); retrieved_on.
- Human review: Check the OC code changes over time (pre-2012 codes for blueberries), sum UK rows across ports, flag suppressed cells, and treat arrival month versus export month as a 0-1 month lag.
- Licensing gate: Eurostat (attribution) and HMRC (OGL v3) are cleared; Office des Changes terms not found, so confirm reuse before public display.
- App value: Year-by-year monthly season curves for Morocco to test managed_cycle harvest windows and detect late seasons (2023, 2024, 2025, 2026).

**IBM-31: Morocco dated berry weather events and season-timing claims (press RAG)** (P1, about 1.5 days)

- Sources: `ma-agrimaroc-berry-news`, `ma-freshplaza-morocco-soft-fruit-reports`, `ma-ecofin-gharb-loukkos-floods-2026`, `ma-hortitecnews-souss-storm-2026`, `ma-blueberries-consulting-morocco`, `ma-usda-fas-iatr-morocco-fruit-2022`.
- Output: event records. Method: HTML scrape of the listed articles, then LLM-proposed claim and event records offline, then manual review. Cadence: one-off backfill 2023-2026, then each season (Feb-Jun).
- Fields: kind (event | claim); topic (weather | timing | market); period (start, end, precision); geography (MA-NORTH: Larache, Moulay Bousselham, Kenitra, Sidi Slimane, Gharb; MA-SMD: Chtouka Ait Baha, Agadir); crop_context (stage at event, e.g. floraison/nouaison); evidence_type (industry_narrative | official_statement); hazard (cold, flood, wind, chergui); impact (percent volume, ha affected, peak shift); citations (url, date, quote).
- Human review: De-duplicate against the existing IBO records ma-2023-cold and ma-2025-26-rain-cold; fix unit errors (HortitecNews week-9 'kilos'); separate blueberry claims from strawberry or raspberry claims.
- Licensing gate: Press copyright: show short quotes and links only; no full-text display.
- App value: Validation events for harvest_heavy_rain, wind/structure and cold-delay risks in both Moroccan cells, plus observed peak months per season.

**IBM-32: Morocco management calendar (Loukkos and Souss) from extension sources** (P2, about 0.75 days)

- Sources: `ma-btta-203-myrtille-inra-tanger`, `ma-agri-mag-fruits-rouges`, `ma-fnh-loukkos-red-fruit-area-2022-23`, `ma-interproberries-comader`.
- Output: claim records. Method: layout-aware PDF tables (BTTA 203) plus HTML scrape, then manual review. Cadence: one-off, then annual review.
- Fields: kind=practice; topic=management; geography (MA-NORTH Loukkos/Larache; MA-SMD Souss); period (planting Oct-mid Mar; cover off Nov-Jan; harvest Nov-May north / Dec-May Souss; peak mid-Feb Souss; pruning Jun-31 Jul Souss); crop_context (SHB, substrate vs soil, canary greenhouse, misting); evidence_type (extension | trade_press); citations.
- Human review: Date each claim (2016, 2017 and 2026 sources differ); mark the Souss 2017 figures as early-stage; keep bloom months empty unless a dated source appears.
- Licensing gate: BTTA terms not found; Agri-mag copyright. Use paraphrased claims with links.
- App value: Fills the benchmark gap 'no Souss-specific production-system evidence' and supplies cover-off and pruning windows for the managed-cycle scan.


## 6. How each source maps to model checks

- **Moguer calendar mismatch** (model bloom March-April and harvest May-June vs published bloom January-February and harvest January-July).
  - Compare IFAPA cultivar harvest-start dates (February for low-chill cultivars under thermal plastic, mid-May for uncovered late cultivars) with the modelled start. Fit a "tunnel offset" in days.
  - Check the offset against DataComex monthly Huelva exports by year and the Síntesis monthly shares.
  - Use the Estado de los cultivos bloom and fruit-set weeks to test the model's bloom timing in Huelva comarcas.
- **Chill clock and evergreen hypothesis in Huelva.**
  - Use RIA open-air vs under-plastic daily Tmin, plus hourly SiAR, to count chill hours inside and outside tunnels. [inference] If tunnels cut effective chill sharply, the model's "Deciduous, 723 h" label for the Moguer cell is not the crop's experience.
  - Use the RAIF pruning window (second half of May to early July) and the September "reposo vegetativo" note to set the managed-cycle start and a rest period. Do not assume a true evergreen system.
- **Fruit frost, bud and flower freeze.**
  - Count nights at or below 0 C and 2 C at RIA open-air vs plastic stations, January-March.
  - Check against the IBO 2023 cold event (late January-March 2023) and the frost guarantee zoning in Orden APA/461/2026.
  - For Morocco, GSOD Tmin at Larache, Kenitra and Agadir tests the 2023 cold spell reported by FreshPlaza.fr (picking cut to once a week, volumes down by more than 60%).
- **Harvest heavy rain and wind on structures.**
  - Match Agroseguro and press event dates (22 Oct 2023; January-February 2026 storms; storm Garoé, late January 2025) with modelled harvest_heavy_rain recurrence in the Moguer cell.
  - [inference] Add a wind and structure family for tunnels. Agroseguro claims are mostly structural.
  - For Odemira, use storm Kristin (30 Jan 2026 calamity declaration) and the Lusomorango loss estimate. For Loukkos, use the February 2026 floods: at least 10% of red-fruit greenhouse area damaged, with plants in bloom or early fruit set (AgriMaroc).
- **Disease weather (anthracnose, Botrytis).**
  - Hourly RH from SiAR inside and outside tunnels can test whether tunnels raise or lower infection hours.
  - The INIAV IPM guide states the Botrytis conditions (RH above 95%, 15-20 C). SNAA circulars for Dão and Entre Douro e Minho give dated Botrytis warnings for northern Portugal.
- **Heat at bloom and fruit.** Use the Estado de los cultivos heat damage to flowers (late May 2026) and RIA Tmax at Andévalo-area stations. Use Souss chergui events (August 2024 losses, misting in canary greenhouses).
- **Northern highbush late bloom in Europe.** Compare SERIDA bloom dates (Asturias 2013-2016), IPVC Vila Verde NHB full-bloom days and AJAP/Mirtilusa windows with the model's NHB bloom. Use MeteoGalicia and IPMA stations for local temperature.
- **Larache and Souss managed cycles.**
  - Office des Changes, Eurostat and HMRC monthly series give the shape of each season. BTTA 203 and Agriculture du Maghreb give the cover-off and pruning windows that seed the scan.
  - [inference] The model's January-July window at Larache starts about two months late. The export curve from November is the test.
- **Location mapping.** Use the Huelva municipal plastic area, the MAPA provincial rows, INE regional area, the Odemira 40% cap and the Morocco perimeter areas to weight pins and choose representative cells.
- **Water and drought.** Use the Despacho 2935/2024 freeze (Santa Clara reservoir at dead volume), the Doñana plan extraction limits, and IBO es-huelva-water and ma-agadir-water.

## 7. Access, licensing and language risks

- **Bot walls and blocks.**
  - Blocked from this machine: agroseguro.es (Cloudflare), the RIA REST API (403), serida.org (403), SNIRH (403), the IFAPA SERVIFAPA search (403), agriculture.gov.ma (timeout), ada.gov.ma (403), Medias24 and L'Economiste (403).
  - Plan for manual copying or formal requests. Do not plan on scripted pulls from these sites.
- **Registration.**
  - SiAR needs an account. Its token call uses a DNI, so a non-Spanish user may need an NIE or a formal request [inference].
  - AEMET needs a free e-mailed key.
  - Morocco Foodex AGROSTAT needs an e-mail request to statistiques@eacce.org.ma.
  - IPMA history beyond 24 hours must be requested and may be charged.
  - COTR SAGRA sits behind a members area.
- **Licences.**
  - Clear: Junta Observatorio PDFs ("Se permite la reproducción ... citando su procedencia"), ESYRCE ("podrán ser reutilizados, citando la fuente"), MeteoGalicia (CC BY-SA 4.0), USDA reports (public domain), HMRC (OGL v3), Eurostat (attribution).
  - IFAPA trial reports are CC BY-NC-ND 3.0 ES. Store extracted facts with citations; do not republish tables.
  - Terms not found: RIA, SiAR, DataComex, the Junta blog, RAIF, Agroseguro, INE Portugal, Office des Changes, Moroccan press. Confirm these before public display.
- **Captcha.** Office des Changes needs a reCAPTCHA tick per query, so it cannot be automated without breaking its terms [inference].
- **Language.**
  - Spanish sources are plain administrative Spanish. Portuguese manuals use agronomic terms such as "estufins" and "túneis elevados", which need a glossary. Moroccan sources are French, with Arabic institution names.
  - Comarca names (Condado Litoral, Andévalo) and Portuguese agrarian regions (Entre Douro e Minho) need mapping to the app's region polygons.
- **Dead or hijacked domains.** The old Junta blog domain (informacionagropesquera.com) now serves unrelated spam, so do not ingest links to it. www.interproberries.ma does not resolve.

## 8. Gaps: what I looked for and could not find

- **Spain.**
  - An IFAPA or Junta month-by-month planting calendar for Huelva.
  - Junta aforos (pre-season estimates) for blueberry.
  - IFAPA variety trials after 2021/22.
  - A split of Huelva protected area by crop or between macrotunnel and greenhouse.
  - Agroseguro tables by crop and province (no open data; blocked site).
  - A blueberry-specific file in the RAIF open dataset (only a Fresa file; its content was not inspected).
  - RIA hourly data through RIA itself (only via SiAR).
  - Any blueberry bloom-date series for Huelva from fixed plots.
- **Portugal.**
  - Mirtilo by municipality from RA2019.
  - Regional INE values for 2012-2017 (suppressed as "x").
  - A current GPP export series.
  - The INIAV 16 Feb 2026 Odemira estimate document (seen only through a Público snippet, about 150 ha of blueberry).
  - Berry advisories for the Alentejo or Algarve.
  - Dated phenology for Sever do Vouga.
  - IFAP insurance tables, and SIPAC data after 2017.
  - Hourly IPMA history.
  - The measured tunnel share inside the Mira scheme (only a 2019 press figure of about 10%, seen as a snippet).
  - Storm Kristin losses by crop.
- **Morocco.**
  - Any open weekly or monthly Foodex series.
  - A red-fruit contrat-programme document.
  - An official bloom calendar.
  - Blueberry tunnel share vs open field.
  - Official Souss blueberry area.
  - An open DGM archive.
  - MAMDA crop or region losses.
  - A GAIN berry annual (none exists).
- **All three countries.** Observed, dated bloom data by cultivar and year at commercial farms. Only trial and thesis data were found (IFAPA 2020/21-2021/22, Évora 2011, Fataca, SERIDA 2013-2016).

## 9. Ranked top 10 actions for this scope

1. Pull RIA daily data for the paired open-air and under-plastic stations (21/101-21/102, 21/10-21/103, 21/107, 21/2-21/106) for 2001-2026, and SiAR hourly data for the same stations. Measure tunnel Tmin, Tmax and RH offsets and the Moguer-cell bias (IBM-01). If RIA REST stays blocked, ask IFAPA through its contact form.
2. Build the Huelva campaign evidence library from Estado de los cultivos (2017-2026), the Observatorio Síntesis and weekly reports, and RAIF. Start with dated blueberry stage and damage notes (IBM-02).
3. Load the IFAPA 2020/21 and 2021/22 cultivar harvest tables, the CompetitiveSouthBerries Duke percentiles and the Évora bloom table into a first Iberian cultivar table with covered and open plots (IBM-03, IBM-21).
4. Download DataComex monthly fresh blueberry exports for Huelva province (1995-2026), and INE Portugal monthly exports. Derive yearly harvest curves and compare them with modelled windows (IBM-04, IBM-20).
5. Re-run the es-hu-moguer benchmark with a tunnel offset fitted from actions 1, 3 and 4. Report harvest recall before and after.
6. Export Office des Changes monthly 0810400010 series by hand (1998-2026) and pull the Eurostat and HMRC mirrors. Test the Larache and Souss managed-cycle windows (IBM-30).
7. Ingest the Huelva municipal plastic series (2004-2026), the ESYRCE invernadero share and the Odemira 40%/30% cap as management-layer priors and location weights (IBM-05, IBM-22).
8. Record the sized 2023-2026 storm and flood events for Huelva, Odemira and Loukkos as event records, with Agroseguro figures copied by hand (IBM-06, IBM-22, IBM-31).
9. Download the RAIF Fresa zip once to check for blueberry plots and stage codes. If they are present, it becomes a plot-level weekly series for 2007-2026.
10. Send three data requests: SiAR API registration (or a request for a non-DNI account), Morocco Foodex AGROSTAT access (statistiques@eacce.org.ma), and IPMA hourly history for Odemira S. Teotónio.
