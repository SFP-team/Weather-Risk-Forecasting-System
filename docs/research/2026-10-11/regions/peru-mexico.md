# Peru and Mexico: source inventory for the blueberry weather-risk app (2026-10-11)

Slug: `peru-mexico`. Companion file: `peru-mexico.sources.json` (65 sources, 12 extraction and RAG jobs).
All URLs were fetched on 2026-10-11 unless marked otherwise. Two helper agents sampled the weather, disaster, insurance and trade sources. I sampled the theses, SIAP, GAIN, FIRA, SENAMHI bulletin and Central American items myself. Small samples were stored only in `/tmp`, never in the repository.

## 1. Scope and summary

Covered: coastal Peru (Piura, Lambayeque, La Libertad, Áncash, Lima, Ica) and Mexico (Jalisco, Michoacán, Sinaloa, Guanajuato, Baja California and smaller states). Guatemala gets a short note because it is the only Central American country where I found official blueberry documents. I searched in Spanish and English. That covered thesis repositories (UNALM DSpace API, ALICIA, RENATI, UNS, UNJFSC, Chapingo, UdeG, UAS), ministries, statistics offices, weather services, disaster and insurance open data, and the industry press.

Five most valuable findings:

1. **Coastal Peru theses give dated pruning, bloom and harvest data.** The UNALM repository has an open REST API with 121 hits for "arándano poda" ([search API](https://repositorio.lamolina.edu.pe/server/api/discover/search/objects?query=ar%C3%A1ndano%20poda&size=40)). I read 8 PDFs. They give pruning-to-harvest intervals for Olmos, Villacurí (Ica), Virú, Chao, Chepén and Jayanca, and weekly bloom curves for 9 cultivars at Virú ([Mayta 2024](https://hdl.handle.net/20.500.12996/6685)). This fills the Olmos and Ica pruning and bloom gaps recorded in `benchmark_sites.json`.
2. **The "four months" and the model's "41 to 51 days" measure different things.** First open flower to first pick is about 9 weeks in the Virú trial, while main bloom to main harvest is about 3.5 to 5 months (see section 6.1). Pruning to first harvest is 17 to 30 weeks, mostly 22 to 26.
3. **SENAMHI publishes a dekadal "Cultivo de Arándano" bulletin.** It reports the observed stage at Cayaltí (Lambayeque), Chao and San José (La Libertad), from 2024 to October 2026 ([example, 3-12 Oct 2026](https://www.senamhi.gob.pe/load/file/02981SENA-70.pdf)). It is the only official, recurring, dated blueberry stage record found in either country. It currently documents El Niño Costero 2026 disrupting chill-requiring cultivars.
4. **Monthly blueberry production by Peruvian department exists.** BCRP regional reports give monthly tonnes for La Libertad, Lambayeque and Áncash ([BCRP regional](https://www.bcrp.gob.pe/estadisticas/informacion-regional.html)). MIDAGRI "El Agro en Cifras" gives national monthly tonnes and department year-to-date tonnes ([MIDAGRI](https://www.gob.pe/institucion/midagri/informes-publicaciones/7910469-boletin-estadistico-mensual-el-agro-en-cifras-2026)). Both are observed harvest curves usable for timing checks.
5. **Mexico: SIAP blueberry data did not stop in 2022, and there are blueberry insurance claims.** The open municipal CSV runs from 2003 to 2025 and has 74 Arándano rows in 2025 ([SIAP datos abiertos](https://nube.agricultura.gob.mx/datosAbiertos/Agricola.php)). The CNSF insurance dataset has 53 Arándano claim rows (2018 to 2024) by state, year and cause (frost, hail, hurricane) under CC BY 4.0 ([CNSF](https://datos.gob.mx/dataset/informacion_estadistica_agricola_animales_sector_asegurador)). CENAPRED declarations add dated municipal frost and heat events ([CSV](http://www.atlasnacionalderiesgos.gob.mx/apps/Declaratorias/declaratoria_fns.php?consulta=csvDeclaratorias)).

### 1.1 Answers to the brief's questions

1. **Weekly or monthly series by department or state.**
   - Peru, monthly by department: BCRP regional syntheses carry monthly arándano TM for La Libertad, Lambayeque and Áncash, and summary values for Piura and Ica ([La Libertad Jan 2026](https://www.bcrp.gob.pe/docs/Sucursales/Trujillo/2026/sintesis-la-libertad-01-2026.pdf)).
   - Peru, monthly national: MIDAGRI gives national monthly tonnes (sheet c-19) and department year-to-date tonnes (c-18) ([May 2026 zip](https://cdn.www.gob.pe/uploads/document/file/10357048/7910469-cuadros-en-excel-del-boletin-el-agro-en-cifras-mayo-2026.zip?v=1790633292)).
   - Peru, weekly: Proarándanos weekly reports exist but the site returned HTTP 521. Its figures reach the public only through the press ([Agraria, 24 Sep 2024](https://agraria.pe/index.php/noticias/proarandanos-peru-exportaria-292-138-toneladas-de-arandanos--37098); [IBO, 11 Sep 2026](https://www.internationalblueberry.org/2026/09/11/proarandanos-proyecta-una-reduccion-en-el-volumen-de-exportacion/)).
   - Peru, SENASA: no open certification table was found, only press notes.
   - Peru, SUNAT: Aduanet gives annual exports by country for 0810.40.00.00. Its 2025 total (12.18 million kg) conflicts with MIDAGRI and Agrodata (387.8 million kg in 2025), so it is not usable until explained ([Aduanet](http://www.aduanet.gob.pe/cl-ad-itestadispartida/resumenPPaisS01Alias)).
   - Mexico, annual: SIAP municipal closing statistics continue through 2025 (sampled 2025; the 2023 and 2024 files are listed).
   - Mexico, monthly: the SIAP monthly "avance" covers 64 crops, and I could not confirm that blueberry is one of them.
   - Mexico, industry: Aneberries statistics are member-only. CAADES and AARFS calendars were not found, and the CESAVESIN SIVASA permit data were seen only through press quotes.
2. **Pruning, bloom and flowering-to-harvest in coastal Peru:** answered with numbers in section 6.1, from 9 thesis sources plus the SENAMHI bulletin.
3. **Bloom and pruning months for Jalisco, Michoacán and Sinaloa; a calendar for San Quintín.**
   - Michoacán: summer pruning dates 23 May to 18 July and 97 days from flower to fruit at Los Reyes ([Chapingo thesis](https://repositorio.chapingo.edu.mx/items/f27c0711-e0d4-4a93-aaac-d1e7022307d6)). Flowering falls inside October to February after end-of-season pruning ([REMEXCA e3703](https://cienciasagricolas.inifap.gob.mx/index.php/agricolas/es/article/download/3703/7541/40044?inline=1)).
   - Jalisco: harvest October to April and 90 to 120 days from flower to ripe fruit before the 2024 shift ([UdeG 2015](https://riudg.udg.mx/bitstream/20.500.12104/84743/1/LCUCBA10090.pdf)). FAS reports a February to May window now ([MX2026-0015](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Berry+Annual+Voluntary_Guadalajara_Mexico_MX2026-0015.pdf)).
   - Sinaloa: a 2019-20 trial dates planting (29 Oct 2019), harvest (19 May to 9 June 2020) and pruning (11 June 2020) ([UAS thesis](https://cca.uas.edu.mx/images/posgrado/Tesis/COHORTE%202019-2021/TESIS%20MCA_PE%C3%91UELAS%20MONTOYA.pdf)). In the warm winters of 2022 and 2023, Atlas flowered as late as January ([Blueberries Consulting 2026](https://blueberriesconsulting.com/arandano-en-sinaloa-de-la-expansion-acelerada-a-una-nueva-oportunidad/)).
   - San Quintín: no calendar was found. SADER statements say harvest had not started by the end of August 2023 or by 14 March 2024 ([Península BC](https://peninsulabc.com.mx/2023/09/cosecha-de-berries-presenta-avance-del-68-80-la-mayoria-en-san-quintin/)).
4. **Damage events, declarations and insurance.**
   - Peru, rain: INDECI COEN reports give district crop hectares affected and lost for the 2023 rains ([Informe 1438](https://portal.indeci.gob.pe/wp-content/uploads/2023/04/INFORME-DE-EMERGENCIA-N%C2%BA-1438-29ABR2023-LLUVIAS-INTENSAS-EN-EL-DEPARTAMENTO-DE-LA-LIBERTAD-45-DEE.pdf)).
   - Peru, Yaku: the Chavimochic canal broke on 10 March 2023 ([Gestión](https://gestion.pe/economia/empresas/ciclon-yaku-la-libertad-trujillo-peru-chavimochic-agroexportadoras-agroexportadoras-de-la-libertad-sin-agua-por-rotura-de-canal-madre-de-chavimochic-noticia/)).
   - Peru, 2023 heat: La Libertad blueberry output fell 50% according to ADAS ([Gestión](https://gestion.pe/peru/el-nino-tres-cultivos-agroindustriales-son-afectados-por-altas-temperaturas-en-la-libertad-adas-cultivos-agroindustriales-noticia/)). National 2023 production was 229 thousand t, down 22.5% ([MIDAGRI NT 19-2024](https://cdn.www.gob.pe/uploads/document/file/7013345/5063792-nota-tecnica-n-019-el-arandano-es-una-de-las-principales-exportaciones-peruanas.pdf?v=1727704705)).
   - Peru, SINPAD open data: the yearly files are listed but the sample returned 404.
   - Peru, SAC insurance: department and campaign only, no crop split ([SAC](https://www.datosabiertos.gob.pe/dataset/midagri-17-seguro-agr%C3%ADcola-catastr%C3%B3fico-sac-campa%C3%B1as-2009-2010-2025-2026-ministerio-de)).
   - Mexico, declarations: CENAPRED (2000 to 2024) and SSPC (2018 to 2025) declarations, with DOF texts.
   - Mexico, insurance: CNSF crop-level claims and AGROASEMEX exposure. The SAC indemnity dataset returns 404.
5. **Station networks.**
   - SENAMHI: historical daily data need a free registration. Automatic stations exist near Olmos (Tongorrape), Ica (Beta Santiago) and Chincha (Fonagro), but their tables sit behind a captcha.
   - ENFEN and ICEN: communiqués (2015 to 2026) and the monthly ICEN series (1950 to 2026) are open.
   - CONAGUA SMN: daily station files are open and deep (Ciudad Guzmán from 1897). The automatic EMAS keep only 3 days online.
   - INIFAP: 15-minute T and RH, but most stations in the Jalisco and Michoacán blueberry municipios stopped between 2008 and 2020. Downloads need a login.
   - SIMARBC (Baja California) has hourly T and RH after registration.
6. **Narrative corpora for RAG.**
   - USDA GAIN for Peru (PE2025-0010, PE2024-0002, PE2023-0002) and Mexico (MX2024-0003, MX2025-0004, MX2026-0015) are open and public domain.
   - Agraria.pe has about 89 tag pages of blueberry news from April 2016 to October 2026.
   - Redagrícola is partly behind a "Plus" subscription.
   - FIRA: the only blueberry Panorama found is Berries 2016 ([PDF](https://www.gob.mx/cms/uploads/attachment/file/200633/Panorama_Agroalimentario_Berries_2016.pdf)). No newer one was found.

## 2. Production context in brief

**Peru.**
- Area and output: harvested area was about 20,500 ha in MY 2024/25 and production 340,000 t, after a fall to 262,000 t in 2023/24 ([FAS PE2025-0010](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf)). The same report puts 80% of export production in La Libertad, Lambayeque, Áncash and Piura.
- Area by department, 2025-26: 26,786 ha, with La Libertad 42.85%, Lambayeque 26.55% and Ica 13.60%. Cultivars: Ventura 21%, Sekoya Pop 17%, Biloxi 11%, Mágica 10% ([Agraria, Proarándanos and SENASA figures](https://agraria.pe/noticias/peru-cuenta-con-23-344-hectareas-certificadas-de-arandanos-p-41924)). In 2016 Biloxi held 60% of 3,926 ha ([Agraria 2021](https://agraria.pe/noticias/ventura-supero-a-biloxi-como-la-principal-variedad-de-aranda-26228)).
- System: evergreen and pruning-scheduled, in soil or in pots, mostly open field with wind and sand nets ([FAS PE2025-0010](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf)).
- Season: production starts in August, peaks in October and falls from January to June ([MIDAGRI NT 19-2024](https://cdn.www.gob.pe/uploads/document/file/7013345/5063792-nota-tecnica-n-019-el-arandano-es-una-de-las-principales-exportaciones-peruanas.pdf?v=1727704705)). The 2025 national monthly curve rose from 1,682 t in April to 97,649 t in October (MIDAGRI c-19, sampled by helper).

**Mexico.**
- SIAP 2025, harvested area and output: Jalisco 2,076 ha and 32,371 t; Sinaloa 2,018 ha and 24,478 t; Michoacán 579 ha and 10,925 t; Guanajuato 566 ha; Baja California 338 ha. All are perennial and irrigated ([SIAP CSV 2025](https://nube.agricultura.gob.mx/datosAbiertos/Agricola.php)).
- Top municipalities: El Fuerte (1,080 ha), Zapotlán el Grande (670 ha), Tala (380 ha), Guasave (356 ha) and Ensenada/DDR San Quintín (305 ha).
- FAS estimates: 5,964 ha harvested and 73,500 t in 2025. It gives different state tonnages (Jalisco 44,000 t, Sinaloa 9,200 t) ([MX2026-0015](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Berry+Annual+Voluntary_Guadalajara_Mexico_MX2026-0015.pdf)).
- Harvest window: growers moved from an October start and late-April peak to a February to May window. They also moved to substrate (more than 8,000 plants/ha) and high tunnels.
- Sinaloa: area fell from about 3,500 ha at the peak to 1,800 ha in December 2024 ([Blueberries Consulting 2024](https://blueberriesconsulting.com/cae-drasticamente-la-superficie-de-siembra-y-la-produccion-de-arandanos-en-sinaloa/)).

**Central America.** Guatemala's MAGA maps 135,722 ha as suitable for Biloxi at 1,000 to 2,400 m ([ficha técnica](https://guatemalanosedetiene.gt/wp-content/uploads/2024/06/FICHA-TECNICA-AGROCLIMATICA-ARANDANO.pdf)). Exports were small: 112.24 t in 2022, 95.18% to Honduras ([MAGA Perfil Bayas](https://precios.maga.gob.gt/archivos/perfiles/Perfil%20Bayas.pdf)). I found no production statistics for Honduras, Costa Rica or other countries.

## 3. What the app already has for this scope

**Benchmark sites** (`pipelines/weather/benchmark_sites.json`):

| Site | Published bloom | Published harvest | Model result | Recorded gap |
|---|---|---|---|---|
| pe-chao-chavimochic | Apr-May | Aug-Jan | bloom Jun-Oct; harvest recall 0.83 | trial pruning early March; industry 15 Jan |
| pe-olmos | none | Jun-Jan | harvest recall 0.5 | no bloom, no pruning dates |
| pe-ica | none | May-Dec | precision 0.67 | no bloom, peak or pruning |
| mx-zapotlan-jalisco | none | Oct-Jun | recall 0.67 | no bloom, no pruning |
| mx-los-reyes-michoacan | Oct-Nov | Jan-Jun | recall 0.67 | one practitioner source |
| mx-el-fuerte-sinaloa | none | Feb-May | precision 0.57 | no Sinaloa bloom or peak |

The Latin America gap list also records the following:
- `mx-san-quintin-bc` was removed for lack of months.
- The note "SIAP stopped publishing blueberry data after 2022" is now superseded: municipal data run to 2025.
- The FAS 2025 state chart is illegible. FAS 2026 Table 8 is legible text.

**IBO records** (`dist/evidence/ibo-regional-v1.json`):
- PE (6): 2024 delayed pruning; El Niño 2023; 2025 cloudy winter; coastal system; reverse-osmosis water; harvest peak Sep-Nov.
- PE-LAM (1): early window. PE-ICA (1): southern growth.
- MX (4): protected share; altitude frost; 2023-24 heat; water 2026.
- MX-CENTRAL (2): tunnels; harvest shift. MX-SIN (2): system; 2023-24 heat.

New sources should not repeat these claims. They should add dates, sites and magnitudes. For example:
- the SENAMHI bulletins date the stage at named sites;
- INDECI dates the March-April 2023 rain damage by district;
- CNSF quantifies Mexican frost claims.

**Earlier research.**
- `04_validation_data_and_protocol.md` lists Proarándanos weekly exports as press-only. That remains true.
- `GLOBAL_PHENOLOGY_REVIEW.md` [S23] uses only the Chao paper for Peru and notes that no defensible phenology constants exist for Mexico. This inventory adds 9 Peruvian and 4 Mexican primary phenology sources.

## 4. Source inventory

Status codes: O = opened, OL = opened-limited, SO = search-only. Full fields are in the JSON.

### 4.0 Top 10 sources, described from an actual sample

1. **[Mayta 2024, Virú](https://hdl.handle.net/20.500.12996/6685)** (thesis PDF, 4.3 MB, read).
   - Site: Virú province, 300 m. Planted 14-15 May 2021. Pruned in the first week of December 2021. A Davis station recorded weekly Tmax, Tmin and RH.
   - Table 7, one row per cultivar: vegetative weeks, induction Tmin and month, bloom type and months. Biloxi: 19 weeks; 14.9 C in May; bloom weeks 20 to 34.
   - Bloom to first harvest: C-01 bloomed from week 30 with harvest from week 39; C-03 bloomed from week 12 with harvest from week 21.
   - Weekly harvest-share figures exist for each cultivar.
2. **[Orga 2021, Villacurí, Ica](https://hdl.handle.net/20.500.12996/4981)** (thesis PDF read).
   - Table 4 rows: pruning start and end (19 Jan to 21 Feb 2019; 7 to 22 Jan 2020); first-fruit pick (9 Jul 2019; 30 Jun 2020); peak week (45; 37); weeks harvested (23; 20); tonnes per 60 ha (560; 848).
   - The irrigation-by-stage table puts bloom in May-June.
3. **[Castro 2025, Olmos](https://hdl.handle.net/20.500.12996/7224)** (thesis PDF read).
   - Table 6 gives pruning week, harvest start week and weeks of harvest for six fields: (8, 30, 32), (15, 38, 27), (6, 29, 21), (9, 39, 27), (10, 33, 24), (7, 29, 35).
   - Text: dew in Oct-Nov, rain in Jan-Feb, Tmax 30-31 C in the harvest season.
4. **[SENAMHI Pronóstico Agrometeorológico, Cultivo de Arándano](https://www.senamhi.gob.pe/load/file/02981SENA-70.pdf)** (3-page PDF read).
   - Vol V Ed XXVII, period 3 to 12 Oct 2026.
   - Stage map as of 30 Sep 2026: fructificación and maduración at Cayaltí, Chao and San José. Chill-requiring varieties are disrupted by El Niño Costero.
   - North coast in the last dekad: Tmax 31.8 C, Tmin 22.9 C, 9.6 mm. Heat Aviso N°400 for 6 and 9 Oct.
5. **[BCRP Síntesis La Libertad](https://www.bcrp.gob.pe/docs/Sucursales/Trujillo/2026/sintesis-la-libertad-01-2026.pdf)** (sampled by helper).
   - Annex 1, row "Arándano", 2025 monthly TM: Jan 14,000; Feb 7,920; Mar 1,590; Apr 500; May 700; Jun 1,550; Jul 7,210; Aug 24,007; Sep 42,020; Oct 41,559; Nov 32,479; Dec 24,019.
   - Lambayeque and Áncash annexes have the same layout.
6. **[MIDAGRI El Agro en Cifras, May 2026 Excel](https://cdn.www.gob.pe/uploads/document/file/10357048/7910469-cuadros-en-excel-del-boletin-el-agro-en-cifras-mayo-2026.zip?v=1790633292)** (sampled by helper).
   - Sheet c-19, national arándano tonnes by month (2025 total 403,783 t).
   - Sheet c-18, Jan-May by department (La Libertad 30,146 t in 2026).
   - Sheet C.77, exports of 0810400000.
7. **[SIAP cierre agrícola 2025 CSV](https://nube.agricultura.gob.mx/datosAbiertos/Agricola.php)** (5.8 MB, read and deleted).
   - Columns: Anio, Nomestado, Nomddr, Nomcader, Nommunicipio, Nomcicloproductivo, Nommodalidad, Nomcultivo, Sembrada, Cosechada, Siniestrada, Volumenproduccion, Rendimiento, Preciomediorural, Valorproduccion.
   - 74 blueberry rows. El Fuerte: 1,080 ha, 13,137.6 t, 12.16 t/ha.
8. **[CNSF agricultural insurance](https://datos.gob.mx/dataset/informacion_estadistica_agricola_animales_sector_asegurador)** (API sample by helper).
   - Fields: anio, cultivo, ciclo_cultivo, entidad, causa_siniestro, numero_siniestros, superficie_siniestrada, monto_pagado.
   - Example rows: 2024 Jalisco Heladas, 4 claims, 16 ha; 2023 Sinaloa Huracán/vientos, 6 claims, 98 ha.
9. **[CENAPRED declaratorias CSV](http://www.atlasnacionalderiesgos.gob.mx/apps/Declaratorias/declaratoria_fns.php?consulta=csvDeclaratorias)** (5.4 MB, sampled by helper).
   - 34,453 rows. Fields: Estado, Municipio, Clave Municipio, Tipo Declaratoria, Tipo Fenómeno, Fecha Inicio, Fecha Fin.
   - Example: Tangancícuaro helada, 3 to 6 Mar 2013.
10. **[SMN daily station files](https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica)** (sampled by helper).
    - Station GeoJSON with clave, municipio, altitud, inicio, mas_reciente and situacion.
    - Daily file 14030 Ciudad Guzmán: FECHA, PRECIP, EVAP, TMAX, TMIN, from 1897-01-01 to 2026-09-28.

### 4.1 Phenology observations, trials and management (Peru)

| Source | Contains | Access and terms | Lang | Coverage | Status | Prio |
|---|---|---|---|---|---|---|
| [UNALM repository API](https://repositorio.lamolina.edu.pe/) | 121 blueberry pruning items; abstracts, PDFs | open; CC BY-NC-ND 4.0 | es | 2017-2026 | O | P1 |
| [Mayta 2024, Virú](https://hdl.handle.net/20.500.12996/6685) | weekly bloom, induction Tmin, harvest curves, 9 cultivars | open; CC BY-NC-ND 4.0 | es | 2021-22 | O | P1 |
| [Orga 2021, Villacurí](https://hdl.handle.net/20.500.12996/4981) | pruning and first-pick dates, peak week | open; CC BY-NC-ND 4.0 | es | 2018-20 | O | P1 |
| [Castro 2025, Olmos](https://hdl.handle.net/20.500.12996/7224) | pruning week vs harvest start week, 6 fields | open; CC BY-NC-ND 4.0 | es | 2024-25 | O | P1 |
| [Córdova 2026, Olmos](https://hdl.handle.net/20.500.12996/7508) | April pruning dates, weekly t/ha, Sekoya Pop | open; CC BY-NC-ND 4.0 | es | 2024-25 | O | P1 |
| [SENAMHI blueberry bulletin](https://www.senamhi.gob.pe/main.php?dp=la-libertad&p=boletines) | dekadal observed stage at 3 sites, coastal T | open; terms not found | es | 2024-2026 | O | P1 |
| [Rodríguez 2023, UNS, Jayanca](https://repositorio.uns.edu.pe/handle/20.500.14278/4306) | 10% and full bloom dates via hive entry; stage durations | open; terms not found | es | 2022 | O | P2 |
| [Yovera 2023, Jayanca](https://hdl.handle.net/20.500.12996/6046) | pruning late Jan; late cultivars bloom late Apr, pick mid-Sep | open; CC BY-NC-ND 4.0 | es | ~2022 | O | P2 |
| [Lira 2023, Chepén and Santa Rosa](https://hdl.handle.net/20.500.12996/5694) | stage timing in days after pruning (77, 85, 203) | open; CC BY-NC-ND 4.0 | es | ~2022 | O | P2 |
| [UNALM Ica monographs 2024-2025](https://hdl.handle.net/20.500.12996/7049) | budbreak 12-14 d after pruning; first bloom May; harvest Jul-Dec | open; CC BY-NC-ND 4.0 | es | ~2023-25 | O | P2 |
| [ALICIA](https://alicia.concytec.gob.pe/vufind/) | national thesis aggregator | open; terms not found | es | ongoing | O | P2 |
| [Maticorena 2017 thesis, Chao](https://hdl.handle.net/20.500.12996/3062) | 13 dated harvest passes 2015-16 | open; CC BY-NC-ND 4.0 | es | 2015-16 | O | P3 |
| [RENATI](https://renati.sunedu.gob.pe/) and [UNT](https://hdl.handle.net/20.500.14414/22595) | thesis registry; UNT Yaku/Spodoptera thesis | bot wall | es | n/a | OL | P3 |
| [UNJFSC Sayán pruning thesis](https://repositorio.unjfsc.edu.pe/handle/20.500.14067/6396) | days to budbreak by pruning level | open; CC BY-NC-ND 4.0 | es | ~2021 | O | P3 |
| [REMEXCA Piura pruning and Lasiodiplodia](https://cienciasagricolas.inifap.gob.mx/index.php/agricolas/article/view/3880) | pruning vs dieback, Piura 2022 | open; CC BY-NC 4.0 | es/en | 2022 | O | P3 |

### 4.2 Production, shipment and market series

| Source | Contains | Access and terms | Lang | Coverage | Status | Prio |
|---|---|---|---|---|---|---|
| [BCRP regional syntheses](https://www.bcrp.gob.pe/estadisticas/informacion-regional.html) | monthly TM by department | open (browser needed); terms not found | es | 2024-2026 seen | O | P1 |
| [MIDAGRI El Agro en Cifras](https://www.gob.pe/institucion/midagri/informes-publicaciones/7910469-boletin-estadistico-mensual-el-agro-en-cifras-2026) | national monthly t; department YTD; exports | open; terms not found | es | 2023-2026 | O | P1 |
| [SIAP cierre agrícola open data](https://nube.agricultura.gob.mx/datosAbiertos/Agricola.php) | municipal ha, t, damaged ha, price | open; terms not found | es | 2003-2025 | O | P1 |
| [MIDAGRI Nota Técnica 19-2024](https://cdn.www.gob.pe/uploads/document/file/7013345/5063792-nota-tecnica-n-019-el-arandano-es-una-de-las-principales-exportaciones-peruanas.pdf?v=1727704705) | 2023 production loss, seasonality | open; terms not found | es | 2016-2024 | O | P2 |
| [Proarándanos](https://proarandanos.org/) | weekly exports, projections | HTTP 521; press relays only | es | n/a | OL | P2 |
| [SIAP avance mensual](https://nube.agricultura.gob.mx/avance_agricola/) | monthly progress, 64 crops | dynamic form; blueberry unconfirmed | es | monthly | OL | P3 |
| [SUNAT Aduanet 0810.40.00.00](http://www.aduanet.gob.pe/cl-ad-itestadispartida/resumenPPaisS01Alias) | annual FOB and kg by country | open; totals inconsistent | es | 1993- | O | P3 |
| [Agrodataperu](https://agrodataperu.com/category/exportaciones/arandanos-2) | monthly FOB, kg, price (images) | open; all rights reserved | es | 2023-2026 | O | P3 |
| [Fluctuante](https://fluctuante.com/agroexportaciones/2025/04/09/exportacion-de-arandanos-avance-de-la-campana-2024-25/) | campaign-week totals; app needs login | partly login | es | 2024-2026 | O | P3 |
| [SENASA press notes](https://www.senasa.gob.pe/senasacontigo/lambayeque-exportacion-de-arandanos-alcanza-las-35-mil-toneladas-durante-campana-2021/) | regional campaign months | open | es | 2018- | O | P3 |
| [Aneberries](https://aneberries.mx/) | member statistics | member-only | es | n/a | OL | P3 |
| [FIRA Berries 2016](https://www.gob.mx/cms/uploads/attachment/file/200633/Panorama_Agroalimentario_Berries_2016.pdf) | berry area, prices | open | es | 2003-2015 | O | P3 |
| [SAGARPA Frutas del bosque 2017-2030](https://www.gob.mx/cms/uploads/attachment/file/257076/Potencial-Frutas_del_Bosque.pdf) | export seasonality, regions | open | es | 2003-2016 | O | P3 |
| [MAGA Perfil Bayas (GT)](https://precios.maga.gob.gt/archivos/perfiles/Perfil%20Bayas.pdf) | Guatemalan exports 2008-2022 | open | es | 2008-2022 | O | P3 |

### 4.3 Weather stations and climate indices

| Source | Contains | Access and terms | Lang | Coverage | Status | Prio |
|---|---|---|---|---|---|---|
| [SMN daily station files](https://smn.conagua.gob.mx/es/climatologia/informacion-climatologica/informacion-estadistica-climatologica) | daily Tmax, Tmin, rain by station | open; terms not read | es | 1897-2026 | O | P1 |
| [ICEN (IGP/ENFEN)](http://met.igp.gob.pe/datos/ICEN.txt) | monthly coastal El Niño index | open | es | 1950-2026 | O | P1 |
| [SENAMHI historical download](https://www.senamhi.gob.pe/?p=descarga-datos-hidrometeorologicos) | daily PP, Tmax, Tmin | free registration | es | decades | OL | P2 |
| [SENAMHI station map](https://www.senamhi.gob.pe/mapas/mapa-estaciones-2/) | 973 stations incl. automatic near Olmos, Ica, Chincha | captcha on tables | es | 2021- (Tongorrape) | OL | P2 |
| [INIFAP LNMySR](https://clima.inifap.gob.mx/lnmysr/) | 15-min T, RH; most blueberry-area stations stale | login for history | es | ~2005- | O | P2 |
| [SIMARBC](https://www.simarbc.gob.mx/estaciones) | hourly T, RH near San Quintín | free registration | es | 2005- | OL | P2 |
| [ENFEN communiqués](https://enfen.imarpe.gob.pe/) | alert status, outlooks | open | es | 2015-2026 | O | P2 |
| [SMN Monitor de Sequía](https://smn.conagua.gob.mx/es/climatologia/monitor-de-sequia/monitor-de-sequia-en-mexico) | municipal drought category | open | es | 2003-2026 | O | P2 |
| [SMN Reporte del Clima](https://smn.conagua.gob.mx/es/climatologia/diagnostico-climatico/reporte-del-clima-en-mexico) | monthly heat, drought, hail narrative | open | es | 2011-2026 | O | P2 |
| [SENAMHI hourly open data](https://www.datosabiertos.gob.pe/dataset/variables-meteorologicas-de-las-estaciones-autom%C3%A1ticas-de-intercambio-internacional-servicio) | hourly T, HR, PP | ODC Attribution | es | 2015-2024 | O | P3 |
| [SMN EMAS](https://smn.conagua.gob.mx/es/observando-el-tiempo/estaciones-meteorologicas-automaticas-ema-s) | station list; 3-day viewer | open | es | real time | O | P3 |
| [SECAS Sinaloa document](https://www.fps.org.mx/portal/index.php/component/phocadownload/category/12-clima?download=182%3Asistema-de-estaciones-agroclimatologicas-de-sinaloa) | 15-min network incl. leaf wetness | data on request | es | 2006- | O | P3 |
| [REMEXCA Nayarit chill hours](https://www.scielo.org.mx/scielo.php?script=sci_arttext&pid=S2007-09342019001000175) | 38 station coordinates, chill classes | CC BY-NC 4.0 | es/en | 2007-2014 | O | P3 |

### 4.4 Loss, disaster and insurance

| Source | Contains | Access and terms | Lang | Coverage | Status | Prio |
|---|---|---|---|---|---|---|
| [CNSF insurance claims](https://datos.gob.mx/dataset/informacion_estadistica_agricola_animales_sector_asegurador) | blueberry claims by state, year, cause | open; CC BY 4.0 | es | 2018-2024 | O | P1 |
| [CENAPRED declaratorias](http://www.atlasnacionalderiesgos.gob.mx/apps/Declaratorias/) | dated municipal frost, heat, drought | open | es | 2000-2024 | O | P1 |
| [INDECI COEN reports](https://portal.indeci.gob.pe/emergencias/) | district crop ha affected and lost | open | es | 2023-2026 seen | O | P2 |
| [MIDAGRI SAC](https://www.datosabiertos.gob.pe/dataset/midagri-17-seguro-agr%C3%ADcola-catastr%C3%B3fico-sac-campa%C3%B1as-2009-2010-2025-2026-ministerio-de) | indemnities by department and campaign | open; licence blank | es | 2009-2026 | O | P2 |
| [Peru press on Yaku and El Niño](https://gestion.pe/peru/el-nino-tres-cultivos-agroindustriales-son-afectados-por-altas-temperaturas-en-la-libertad-adas-cultivos-agroindustriales-noticia/) | blueberry-named losses 2023-2026 | open | es/en | 2023-2026 | O | P2 |
| [INDECI open data and compendium](https://www.datosabiertos.gob.pe/dataset/emergencias-hist%C3%B3ricas-registradas-por-el-indeci) | emergencies 2003-2018; totals 2003-2022 | files 404 | es | 2003-2022 | OL | P3 |
| [CENEPRED SIGRID](https://sigrid.cenepred.gob.pe/sigridv3/escenarios) | risk scenarios | open | es | per aviso | O | P3 |
| [SSPC Gestión de Riesgos](https://datos.gob.mx/dataset/gestion_riesgos) | declarations 2018-2025 with DOF links | open; CC BY 4.0 | es | 2018-2025 | O | P3 |
| [DOF declaratoria text](https://dof.gob.mx/nota_detalle.php?codigo=5295219&fecha=09/04/2013) | event dates and municipios | open | es | 2003-2019 | O | P3 |
| [AGROASEMEX exposure](https://www.datos.gob.mx/dataset/reaseguros_agroasemex) | insured units by state and crop | open; CC BY 4.0 | es | 2016-2026 | O | P3 |
| [Mexican press weather items](https://www.excelsior.com.mx/nacional/heladas-danan-mas-de-mil-ha-de-cultivos-en-sinaloa/1629573) | frost Jan 2024 Sinaloa; 2023 heat and rain | open | es/en | 2023-2025 | O | P3 |

### 4.5 Narrative and industry reports (RAG candidates)

| Source | Contains | Access and terms | Lang | Coverage | Status | Prio |
|---|---|---|---|---|---|---|
| [USDA GAIN Peru](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Blueberry+Annual_Lima_Peru_PE2025-0010.pdf) | PSD, cultivars, regions, weather | US public domain | en | 2023-2025 | O | P1 |
| [USDA GAIN Mexico](https://apps.fas.usda.gov/newgainapi/api/Report/DownloadReportByFileName?fileName=Berry+Annual+Voluntary_Guadalajara_Mexico_MX2026-0015.pdf) | area, state output, window shift, substrate | US public domain | en | 2024-2026 | O | P1 |
| [Agraria.pe tag arándanos](https://agraria.pe/index.php/tag/arandanos) | about 980 dated articles | open; terms not found | es | 2016-2026 | O | P1 |
| [Redagrícola blueberry section](https://redagricola.com/cultivos/frutales/arandano/) | technical articles (pruning windows, disease) | partly subscription | es | multi-year | O | P2 |
| [IBO news posts](https://www.internationalblueberry.org/2023/10/06/unraveling-the-el-nino-impact-peruvian-blueberry-production-challenges-and-future-prospects/) | El Niño 2023, 2026 projections, Mexico 2024 | open | en/es | 2023-2026 | O | P2 |
| [Chapingo thesis, Los Reyes](https://repositorio.chapingo.edu.mx/items/f27c0711-e0d4-4a93-aaac-d1e7022307d6) | pruning dates; 97 days flower to fruit | open | es | ~2010 | O | P2 |
| [UAS thesis, Sinaloa](https://cca.uas.edu.mx/images/posgrado/Tesis/COHORTE%202019-2021/TESIS%20MCA_PE%C3%91UELAS%20MONTOYA.pdf) | dated planting, harvest, pruning | open | es | 2019-20 | O | P2 |
| [Blueberries Consulting, Sinaloa](https://blueberriesconsulting.com/arandano-en-sinaloa-de-la-expansion-acelerada-a-una-nueva-oportunidad/) | warm-winter bloom failure, area collapse | open | es | 2014-2026 | O | P2 |
| [Arándanos Perú](https://arandanosperu.pe/) | industry pruning statements | open | es | 2017-2026 | O | P3 |
| [REMEXCA e3703, Los Reyes](https://cienciasagricolas.inifap.gob.mx/index.php/agricolas/es/article/download/3703/7541/40044?inline=1) | sampling Oct-Feb after pruning | CC BY-NC 4.0 | es | 2021-22 | O | P3 |
| [UdeG 2015, Jalisco](https://riudg.udg.mx/bitstream/20.500.12104/84743/1/LCUCBA10090.pdf) | harvest Oct-Apr; 90-120 days flower to fruit | open | es | ~2014 | O | P3 |
| [MAGA ficha arándano (GT)](https://guatemalanosedetiene.gt/wp-content/uploads/2024/06/FICHA-TECNICA-AGROCLIMATICA-ARANDANO.pdf) | suitability by altitude and rain | open | es | 2024 | O | P3 |

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON.

| Job | Sources | Output | Exact fields | Effort | Prio |
|---|---|---|---|---|---|
| PEMX-01 Coastal Peru thesis phenology table | 11 Peruvian thesis sources and ALICIA | cultivar table plus claim records | site_id, department, district, elevation_m, cultivar, plant_age_years, pots or soil, season, pruning start and end, budbreak week, bloom start week, 10% bloom date, full bloom date, bloom end week, harvest start, peak week, end week, days pruning to harvest, days bloom to harvest, source page, quote | 4.0 | P1 |
| PEMX-02 SENAMHI bulletin stage series | SENAMHI bulletin | event records | bulletin_id, volume, edition, period_start, period_end, observed_on, site, stage_es, stage_app, coast Tmax, Tmin, rain, aviso numbers | 1.5 | P1 |
| PEMX-03 Peru monthly production by department | BCRP, MIDAGRI | time series | department, year, month, production_t, report issue, revision flag; derived peak month and centroid | 2.0 | P1 |
| PEMX-04 ENSO covariates | ICEN, ENFEN | time series and event records | year, month, ICEN; communiqué id, date, alert status | 1.0 | P1 |
| PEMX-05 Peru damage events 2023-2026 | INDECI, press, IBO, MIDAGRI, Proarándanos, SAC | event records | kind=event, topic=weather, period start/end/precision, geography (district), crop_context (blueberry named or not), evidence_type, magnitude as quoted, citations | 2.0 | P1 |
| PEMX-06 SIAP municipal panel | SIAP | time series | year, state, DDR, CADER, municipio, cycle, water regime, planted, harvested, damaged ha, t, t/ha, price, value | 1.0 | P1 |
| PEMX-07 Mexico frost, hail, heat events | CNSF, CENAPRED, SSPC, DOF, SMN reports, press | event records | Fecha Inicio, Fecha Fin, municipio code, fenómeno, declaration type; CNSF year, state, cycle, cause, claims, ha, paid | 1.5 | P1 |
| PEMX-08 SMN station table | SMN daily, drought monitor, INIFAP | station table | clave, name, municipio, lat, lon, altitude, date, Tmax, Tmin, precip; drought category by municipio and date | 2.0 | P1 |
| PEMX-09 Narrative corpus | GAIN PE and MX, Agraria, Redagrícola, Blueberries Consulting, Arándanos Perú, SENASA | claim records | kind, topic, period, crop_context, evidence_type, geography (PE, PE-LAL, PE-LAM, PE-ICA, MX, MX-JAL, MX-MIC, MX-SIN, MX-BCN), citations with paragraph | 3.0 | P2 |
| PEMX-10 Mexico phenology records | Chapingo, REMEXCA, UdeG, UAS, GAIN | cultivar table | site, municipio, cultivar, season, pruning dates, bloom months, flower-to-fruit days, harvest start, end, peak, protection | 1.5 | P2 |
| PEMX-11 Peru area and cultivar mix | Agraria, GAIN, Proarándanos | cultivar table | season, department, area, certified area, cultivar, share | 1.0 | P2 |
| PEMX-12 Hourly station access requests | SENAMHI, SIMARBC, SMN EMAS, SECAS | station table | station id, network, lat, lon, altitude, period, variables, access route | 1.0 | P3 |

All RAG jobs follow the IBO design rules:
- document, claim and event records stay separate;
- an offline LLM proposes extractions and a human reviews every one;
- retrieval is citation-first;
- no raw full text is republished.

## 6. How each source maps to model checks

- **Coastal Peru bloom timing and flowering-to-harvest (budbreak_bloom_timing, harvest_timing).**
  - PEMX-01 and PEMX-02 give pruning dates, bloom weeks and harvest start weeks at Virú, Chao, Olmos, Jayanca, Chepén and Villacurí.
  - Check: run the managed-cycle scan with budbreak set to each recorded pruning date plus the observed budbreak lag (12 to 14 days in Ica; about 1 month at Chao). Then compare the modelled flowering start and harvest start with the recorded weeks.
- **Harvest windows and year-to-year shifts (harvest_timing, market_timing).**
  - PEMX-03 monthly department curves (BCRP, MIDAGRI) give the month of peak and the share of the crop in each month.
  - Check: the model's Aug-Dec window at Chao should hold most of the La Libertad monthly tonnage (2025: Aug to Dec = 164,084 of 197,554 t, my sum of the BCRP row).
  - Check: 2023 and 2026 should show El Niño anomalies; 2024 should show the delayed-pruning shift.
- **Heat and bloom failure (heat, chill_dormancy).**
  - ICEN (PEMX-04), the SENAMHI stage bulletins and the dated 2023 and 2026 loss statements (PEMX-05) test whether modelled fruit-stage heat and the warm-winter flags line up with Niño costero months.
  - Sinaloa 2022-2023 warm-winter flowering delays (Blueberries Consulting) test chill_shortfall for SHB cultivars that are not truly zero-chill.
- **Harvest heavy rain (harvest_rain_quality).**
  - INDECI district crop losses for March-April 2023 (Virú, Chao, Chepén), the Chavimochic canal break on 10 March 2023, and the Olmos thesis note on January-February rain and October-November dew.
  - Check: compare with modelled harvest-rain flags in those cells.
- **Frost (bud_flower_freeze, fruit_frost) in Mexico.**
  - Compare CENAPRED frost declarations (Tangancícuaro 3-6 Mar 2013; Ahome, El Fuerte, Guasave 3-4 Feb 2011 and 14-16 Jan 2013) and CNSF frost-claim years (Jalisco and Michoacán 2024, Michoacán 2021) with modelled flowering-freeze winters.
  - Use SMN station Tmin on the same nights to measure the grid warm bias (PEMX-07, PEMX-08).
- **Drought and water (water_drought).** SMN municipal drought categories for Sinaloa and Jalisco, 2024-2025.
- **Disease (disease).** Hourly T and RH are scarce. INIFAP Valle del Fuerte (live) and SIMARBC Colonet are candidates. The Ica thesis gives RH up to 84.8% in June-July with Botrytis risk.
- **Location mapping and cultivar classes (location_mapping, cultivar).**
  - SIAP municipal area (PEMX-06) places Mexican pins.
  - Peru department area and the cultivar mix (PEMX-11) weight cultivar classes: early, season and late classes as defined in the Virú thesis.

### 6.1 Flowering-to-harvest duration evidence for coastal Peru (dedicated section)

The model gives 41 to 51 days from flowering start to harvest start on the Peruvian coast. Industry reports say "about four months". The opened sources report the numbers below. Week numbers are calendar weeks; day counts are my arithmetic from the dates quoted.

| Site, cultivar, season | Pruning | Bloom | First harvest | Peak | Interval (as reported or computed) | Source |
|---|---|---|---|---|---|---|
| Virú (300 m), C-01, 2022 | 1st week Dec 2021 | start week 30 (late Jul), concentrated | last week Sep (wk 39) | wk 43-46 (58% of kg) | bloom start to first harvest about 9 weeks; to peak 13-16 weeks | [Mayta 2024](https://hdl.handle.net/20.500.12996/6685) |
| Virú, C-03, 2022 | 1st week Dec 2021 | start week 12 (Mar), 3 flushes | wk 21 | wk 43-47 (48%) | bloom start to first harvest about 9 weeks; pruning to first harvest about 24 weeks | Mayta 2024 |
| Virú, Biloxi, 2022 | 1st week Dec 2021 | weeks 20-34 (May-Aug), one long flush | June | November (33% of kg) | first harvest only a few weeks after the recorded bloom start; likely fruit from flowers before week 20 [inference] | Mayta 2024 |
| Chao, Biloxi, 2015-16 | early March 2015 | managed to start in April | 1 Aug 2015 | September | April to 1 Aug is about 4 months; industry cycle: budbreak 1 month after pruning, bloom 3 months after budbreak, set and veraison 2 months later; "periodo poda-cosecha es de 6 meses" | [Maticorena 2017](https://hdl.handle.net/20.500.12996/3062) |
| Jayanca, Ventura, 2022 | late January (company practice) | 10% bloom 13 May 2022; full bloom 24 Jun 2022 | July | Sep-Oct | 10% bloom to 1 Sep = 111 days; full bloom to 1 Sep = 69 days, to 31 Oct = 129 days; stages: petal fall to set 15-20 d, green fruit 40-45 d | [Rodríguez 2023](https://repositorio.uns.edu.pe/handle/20.500.14278/4306) |
| Jayanca, late cultivars | late January | late April | mid-September | n/a | about 143 days (late April to mid-September) | [Yovera 2023](https://hdl.handle.net/20.500.12996/6046) |
| Chepén and Irrigación Santa Rosa, pots | Dec-Mar | 77-85 days after pruning (Mar-Jun) | 203 days after pruning (Jun-Dec) | n/a | bloom to harvest 118-126 days | [Lira 2023](https://hdl.handle.net/20.500.12996/5694) |
| Villacurí (Ica), Biloxi, 2019 | 19 Jan-21 Feb | May-June | 9 Jul 2019 | week 45 | pruning start to first pick 171 days | [Orga 2021](https://hdl.handle.net/20.500.12996/4981) |
| Villacurí, Biloxi, 2020 | 7-22 Jan | May-June | 30 Jun 2020 | week 37 | pruning start to first pick 175 days | Orga 2021 |
| Olmos, Rocío and others, 2024-25 | weeks 6-15 | not stated | weeks 29-39 | Oct-Nov | pruning to harvest start 22, 23, 23, 30, 23, 22 weeks; text says 24-26 weeks | [Castro 2025](https://hdl.handle.net/20.500.12996/7224) |
| Olmos, Sekoya Pop, 2024-25 | 1-5 Apr and 8-11 Apr 2024 | not stated | weeks 34 and 31 | weeks 40-44 and 41-46 | pruning to harvest start 20 and 17 weeks | [Córdova 2026](https://hdl.handle.net/20.500.12996/7508) |
| Ica, Mágica | not stated | first bloom May; second about September | July | n/a | budbreak 12-14 days after pruning | [Serna 2025](https://hdl.handle.net/20.500.12996/7049) |

Comparison values from Mexico: 97 days from flower to fruit at Los Reyes ([Chapingo](https://repositorio.chapingo.edu.mx/items/f27c0711-e0d4-4a93-aaac-d1e7022307d6)) and 90 to 120 days in Jalisco ([UdeG](https://riudg.udg.mx/bitstream/20.500.12104/84743/1/LCUCBA10090.pdf)).

What this means for the model:
- **First open flower to first pick is about 9 weeks (about 63 days)** for the two Virú selections with clear bloom starts. That is 12 to 22 days longer than the model's 41 to 51 days, but nowhere near four months.
- **Main bloom to main harvest is about 3.5 to 5 months**, in these cases:
  - Chao: April bloom, harvest from August, September peak;
  - Jayanca: 10% bloom in mid-May, Sep-Oct peak;
  - Chepén: 118-126 days;
  - Jayanca late cultivars: about 143 days.
  The "about four months" in reports matches this quantity.
- **Pruning to first harvest is 17 to 30 weeks, most often 22 to 26 weeks.** That fits the 171-175 days at Villacurí and "6 months" at Chao.
- Bloom on the coast comes in several flushes (Virú C-02, C-03 and C-04 show three). Harvest therefore spreads over 20 to 35 weeks, and the bulk crop comes from later flushes.
- [inference] The model compresses the season because it starts harvest 633 GDD after the first flowering. Under cool coastal winters (bloom mostly May to August) fruit development takes longer than at Waldo. The model also has no multi-flush bloom.
- Calibration should fit two targets separately:
  - flowering start to harvest start, about 60-70 days;
  - main bloom to harvest peak, about 110-150 days.
  Pruning date should be the anchor, not chill.

## 7. Access, licensing and language risks

- **Licences.**
  - UNALM and UNJFSC theses are CC BY-NC-ND 4.0. Short factual extractions with citation are fine, but no derivative tables for commercial use. Confirm that the app is non-commercial.
  - CNSF, SSPC and AGROASEMEX datasets are CC BY 4.0. REMEXCA is CC BY-NC 4.0. GAIN reports are US public domain.
  - Most Peruvian and Mexican government pages state no licence. Treat them as "terms not found" and cite the publisher.
  - Agrodataperu states "Todos los derechos reservados".
- **Access walls.**
  - Proarándanos returned HTTP 521 on every path.
  - RENATI and the UNT repository show bot challenges.
  - BCRP PDFs are behind Incapsula, so a browser is needed.
  - SENAMHI station tables are behind a Cloudflare captcha, and SENAMHI historical downloads need registration.
  - INIFAP and SIMARBC histories need registration. Aneberries data are member-only.
  - The SIAP avance form is dynamic.
  - None of these walls were bypassed.
- **Data conflicts.**
  - SUNAT Aduanet annual totals disagree with MIDAGRI by a factor of about 30.
  - FAS 2026 state tonnages disagree with the SIAP 2025 CSV (Sinaloa 9,200 t vs 24,478 t). The harvested area agrees (5,964 vs 5,975 ha, my sum).
  - Press magnitudes for 2023 losses differ between outlets.
- **Language.** Nearly everything is in Spanish. Stage terms (brotación, cuajado, pinta, desbreve, maduración) need a fixed mapping to app stages. "Desbreve" means first pick of early fruit, not pruning.
- **Privacy.** Theses name companies (Beta, Agrovisión, Camposol, Agrovictoria). Store site-level facts, not company performance, in public views.

## 8. Gaps

- **Peru.**
  - No open Proarándanos weekly report and no SENASA certification table by region and week.
  - No crop-specific (arándano) damage hectares in any official source for Yaku 2023, El Niño 2023 or 2017.
  - SAC has no crop split. INDECI open files return 404.
  - No SENAMHI station within 40 km of Virú and Chao, and no confirmed hourly coastal T and RH.
  - Bloom dates for Olmos fields are not reported in the Olmos theses (only pruning and harvest weeks).
- **Mexico.**
  - No official San Quintín bloom or harvest calendar.
  - No Jalisco bloom dates after the 2024 window shift.
  - No municipio-level blueberry frost or hail loss with hectares. CNSF claims are state-year only.
  - Agricultural declarations stop in 2019, and none were found for the 2023-24 heat in the target states.
  - CAADES, AARFS and CESAVESIN SIVASA data were not accessible. Aneberries statistics are member-only.
  - Blueberry inclusion in the SIAP monthly avance is unconfirmed.
- **Central America.** No production statistics or phenology outside Guatemala's suitability sheet and export profile.
- **Narrative.** No FIRA blueberry or berry Panorama newer than 2016 was found.

## 9. Ranked top 10 actions

1. Run PEMX-01. Extract the pruning, bloom and harvest records from the 9 Peruvian theses into a cultivar-by-site table. Then refit the coastal Peru managed cycle on the two targets in section 6.1.
2. Run PEMX-02. Backfill all SENAMHI blueberry bulletins (files 1 to 70) and add each new dekad, so the 2026 El Niño season is tracked as it happens.
3. Run PEMX-03. Build monthly department production series from BCRP and MIDAGRI (2023 to 2026) and test the model's harvest windows at Chao, Olmos and Ica.
4. Run PEMX-06. Ingest the SIAP municipal CSVs 2003 to 2025. Update the benchmark note that says SIAP stopped after 2022, and re-check pins against blueberry municipalities (El Fuerte, Zapotlán, Tala, Ensenada).
5. Run PEMX-07 and PEMX-08 together. Load CNSF claims, CENAPRED frost and heat declarations, and SMN daily Tmin at about 15 stations to measure grid frost misses in Michoacán, Jalisco and Sinaloa.
6. Add ICEN as a year covariate (PEMX-04). Create event records for Yaku (March 2023), El Niño heat (2023) and El Niño 2026 (PEMX-05), linked to the IBO El Niño record.
7. Ask Proarándanos (by email, no form) for weekly export reports by campaign. Ask SENASA for certified area by region and week.
8. Run PEMX-10 for Michoacán and Sinaloa: download the Chapingo thesis PDF and extract dated pruning and bloom. Flag young-plant data in the UAS trial.
9. Decide on registrations (SENAMHI, INIFAP, SIMARBC) for hourly T and RH at Tongorrape, Beta Santiago, Fonagro, Valle del Fuerte and Colonet (PEMX-12). A person must read the terms first.
10. Run PEMX-09. Ingest GAIN Peru and Mexico (2023 to 2026) and a reviewed sample of Agraria.pe articles into claim records, starting with the 2024 delayed pruning, the Mexican window shift and the Sinaloa contraction.
