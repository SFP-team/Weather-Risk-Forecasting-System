# Losses, extreme events and a validation design for the risk families

Slug: `losses-extremes-validation`. Checked on 2026-10-11. The source list is in [losses-extremes-validation.sources.json](losses-extremes-validation.sources.json) (46 sources, 10 extraction jobs). Downloaded samples went to `/tmp` and were deleted after reading. Nothing was stored in the repository.

## 1. Scope and summary

**What I covered.** US loss, insurance and declaration data (USDA RMA, FSA, NOAA, NASS). International event databases (EM-DAT, DesInventar, GDACS, Copernicus EMS, ReliefWeb, JRC MARS, the drought observatories, ESWD). National declaration and insurance sources for Brazil, Chile, Argentina, Mexico, Peru, Spain, Poland, Canada, South Africa, Australia, New Zealand and China. I also wrote a validation design for each of the eight model risk families, with a worked US example.

**Five most valuable findings.**

1. **RMA cause-of-loss files give blueberry losses by county, month and cause from 1989 to 2026.** Blueberries are commodity code `0012`. I opened the 2022 file. It holds 217 blueberry rows in 8 states and USD 77.65 million of indemnity. Freeze (cause 42) accounts for USD 49.08 million of that. Bacon County, Georgia, alone received USD 11.84 million for March freeze ([RMA Cause of Loss](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss), file `colsom_2022.zip`).
2. **RMA has cause codes for most of the model's families.** For blueberries the M13 exhibit lists Insufficient Chilling Hours (45), Plant Disease (81) and the adverse-weather group: Heat 12, Hail 21, Excess Moisture 31, Frost 41, Freeze 42, Cold Winter 43, Cold Wet Weather 44 ([FCIC Appendix III Exhibit 21, RY 2010](https://pubfs-rma.fpac.usda.gov/pub/Publications/M13_Handbook/2010/approved/REC21EXH.PDF)). Chill shortfall, heat and harvest rain can therefore be tested as well as freeze.
3. **RMA Summary of Business files split insured blueberry acres by type and by frost-protection practice.** In Georgia in 2022, rabbiteye "Irr. Without Frost Protection" covered 6,983 insured acres. Highbush "Irr. With Frost Protection" covered 6,545 acres ([SOB State/County/Crop](https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business), `sobtpu_2022.zip`). These splits give the denominators and the strata that a fair validation needs.
4. **FSA Secretarial designations add freeze dates to the day.** For Bacon County, Georgia, the 2022 file lists freezes on 29 to 30 January and 12, 13 and 13 to 14 March 2022. The file also has a column flag for "Insufficient Chill Hours" ([FSA Disaster Designation Information](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information), `METADATA_CY2022_SEC_YTD.xlsx`). NOAA Storm Events has **zero** Frost/Freeze rows for Georgia or North Carolina in March 2022 ([Storm Events bulk CSV](https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/)). Do not treat Storm Events as a list of freezes.
5. **Two known discrepancies have explanations that can be checked.** The 2022 Ñuble frost hit on 31 October and 1 November, mostly in orchards at fruit set ([PortalFruticola, 9 Nov 2022](https://www.portalfruticola.com/noticias/2022/11/09/chilecomo-se-han-afectado-los-arandanos-de-nuble-por-las-heladas/)). The window already checked started on 1 November and tested flowering freeze. Poland's 2024 frost-aid programme covers frosts from 15 to 30 April 2024 ([ARiMR, 4 Oct 2024](https://www.gov.pl/web/arimr/wsparcie-dla-poszkodowanych-przez-przymrozki-lub-grad-rolnikow-ktorzy-uprawiaja-owoce--trwa-nabor)). The IBO record dates the damaging frost to May 2024.

Outside the US, no open blueberry-specific loss series exists. The best substitutes are DesInventar (municipal frost and hail records, but most Latin American series end between 2013 and 2015), Brazil's SISSER insurance microdata (farm coordinates and cause, blueberry presence unconfirmed), official declarations, and a few quantified case studies such as [ODEPA's 2013 frost study](https://www.odepa.gob.cl/wp-content/uploads/2013/12/estudioDanioHeladas.pdf).

## 2. Production context in brief

- **US.** NASS reports 104,700 acres of cultivated blueberry harvested in 2025. Georgia had 23,200 acres, Washington 17,100, Michigan 16,600 and Oregon 13,900. Florida had 6,600 acres. Its yield fell from 4,610 lb/acre in 2024 to 3,650 in 2025 ([NASS Noncitrus Fruits and Nuts, May 2026](https://esmis.nal.usda.gov/sites/default/release-files/795891/ncit0526.txt)).
- **Insured footprint 2022.** RMA blueberry policies existed in CA, FL, GA, MI, NC, NJ, OR and WA. Insured APH acres were about 17,750 in GA, 11,200 in MI, 8,530 in NC, 6,200 in NJ, 5,220 in WA, 3,870 in CA, 2,980 in FL and 2,540 in OR (`sobtpu_2022.zip`). Washington and Oregon insure a much smaller share of their acreage than Georgia does [inference from NASS 2023 acreage].
- **Southeast systems.** Southeast Georgia grows southern highbush (about 61% of surveyed acreage) and rabbiteye (about 39%). Growers use frost protection for southern highbush. The source is the UGA C1311 grower survey quoted in `pipelines/weather/benchmark_sites.json` (site `us-ga-alma`).
- **Global.** Regional systems, seasons and weather narratives are covered by the region agents and by the IBO library (`dist/evidence/ibo-regional-v1.json`). This report covers only loss and event sources.

## 3. What the app already has for this scope

- **IBO evidence layer.** There are 91 records: 39 events, 42 practices and 10 constraints. Thirty-eight are weather events. Eighteen of them have a start date: 16 to the month and 1 to the day (the 12 to 13 March 2022 Southeast US freeze, record `us-se-freeze-2022-03`). The design rules in `docs/research/2026-10-05/ibo_integration_review.md` say to keep document, claim and event records separate. They also say not to turn report prose into loss probabilities.
- **Event checks already run.** `docs/research/2026-10-05/ibo_event_checks.json` compares grid minimum temperatures with IBO events, using daily windows in UTC. Results: Alma -3.12 C and Homerville -2.53 C on 13 March 2022; Elizabethtown -5.47 C and Burgaw -5.24 C on the same day. The grid did not reproduce the Chile cells (+7.59 C at Linares, +7.66 C at Chillán for November 2022) or Waikato (+5.15 C for October 2022).
- **Benchmark sites in RMA counties.** These had blueberry rows in the 2022 file: Alma (Bacon), Homerville (Clinch), Elizabethtown (Bladen), Burgaw (Pender), Waldo (Alachua), Citra (Marion), Hammonton (Atlantic), Grand Junction (Van Buren), Plant City (Hillsborough) and Groveland (Lake). I did not see rows for Highlands (Sebring) or DeSoto (Arcadia) in 2022.
- **Modelled windows (stage_thermal_v3 medians, `docs/weather/benchmark/benchmark.json`).**

| Site | Modelled flowering | Ranked risks |
|---|---|---|
| Alma, GA | 3 Feb to 19 Mar | harvest heavy rain, disease weather, flowering freeze |
| Homerville, GA | 2 Feb to 14 Mar | harvest heavy rain, disease weather |
| Elizabethtown, NC | 15 Feb to 10 Apr | harvest heavy rain, flowering freeze, disease weather |
| Waldo, FL | 7 Feb to 9 Mar | harvest heavy rain, disease weather |
| Hammonton, NJ | 30 Apr to 29 May | harvest heavy rain, disease weather |
| Grand Junction, MI | 1 Jun to 26 Jun | harvest heavy rain, disease weather |

- **Known gap.** The shared brief lists "no loss data for validation". The prior validation plan (`docs/research/2026-09-21/04_validation_data_and_protocol.md`) scores risks only against station-observed weather events, not against losses. This report adds loss labels.

## 4. Source inventory

Status codes: **O** = opened, **OL** = opened-limited, **S** = search-only. Full fields are in the JSON.

### 4.1 Insurance and loss data

| Source | Contents | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [RMA Cause of Loss with month](https://www.rma.usda.gov/tools-reports/summary-of-business/cause-loss) | County x crop x plan x cause x month of loss: policies, acres, liability, indemnity | Open, US federal, no licence text | en | 1989-2026 | O (2022 file parsed) | P1 |
| [RMA SOB state/county/crop and type/practice](https://www.rma.usda.gov/tools-reports/summary-of-business/state-county-crop-summary-business) | Insured acres, liability, indemnity by type (Rabbiteye, Highbush) and practice (with or without frost protection) | Open, US federal | en | 1989-2027 (tpu from 1999) | O (2022 file parsed) | P1 |
| [M13 Exhibit 21 cause codes](https://pubfs-rma.fpac.usda.gov/pub/Publications/M13_Handbook/2010/approved/REC21EXH.PDF) | Allowed causes for Blueberries 0012, full code list | Open | en | RY 2010 | O | P1 |
| [RMA Stage Code Listing](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/Stage_Code_Listing.pdf) | Claim stage codes (H, UH, FL) | Open | en | 1989-2026 | O | P2 |
| [AgRisk Viewer](https://agrisk.jornada.nmsu.edu/) | Map and download of RMA data | Open, terms not found | en | RMA years | O | P3 |
| [SHELDUS](https://cemhs.asu.edu/sheldus) | County hazard losses incl. insured crop losses since 1989 | Register/log in; terms not read | en | 1960-2024 | OL | P3 |
| [Brazil SISSER / PSR](https://dados.agricultura.gov.br/dataset/sisser3) | Subsidised policies with crop, municipality, decimal lat/lon, indemnity, `EVENTO_PREPONDERANTE` | Open, Creative Commons Attribution; contains personal data | pt | 2006-2025 | O (dictionary read, partial 2025 sample) | P2 |
| [PROAGRO bulletins, BCB](https://www.bcb.gov.br/content/publicacoes/boletimderop/Boletim%20Derop%20Dezembro-2022.pdf) | National share of loss reports by event | Open; MDCR is ODbL | pt | 2020s | OL | P3 |
| [Peru SAC](https://www.gob.pe/institucion/midagri/campa%C3%B1as/19256-seguro-agricola-catastrofico-sac) | Smallholder catastrophe cover; dataset MIDAGRI-17 2009-10 to 2025-26 | Open, terms not found | es | 2009-2026 | O | P3 |
| [Agroseguro](https://agroseguro.es/) | Line 328 strawberry and other red berries; claims reports | Bot-blocked (403) | es | annual | OL | P2 |
| [ENESA](https://www.mapa.gob.es/es/enesa/) | Spanish insurance policy body | Open | es | annual | O | P3 |
| [Agroseguros Chile](https://www.agroseguros.gob.cl/) | Subsidised contracts by region, comuna, month | Open | es | not read | O | P3 |
| [BC Berry Production Insurance](https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/programs/agriculture-insurance-and-income-protection-programs/redirect-production-insurance/berries) | Blueberry yield and plant loss perils | Open | en | current | O | P3 |
| [FADQ assurance récolte statistics](https://www.fadq.qc.ca/statistiques/assurance-recolte/assurance-recolte-avis-de-dommages-et-indemnites) | In-season damage notices, causes, indemnities, regions per product; lowbush insurable | Open | fr | 2025-2026 bilans seen | O | P2 |

### 4.2 Disaster declarations

| Source | Contents | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [FSA Secretarial designations](https://www.fsa.usda.gov/resources/disaster-assistance-program/disaster-designation-information) | County, peril flags (incl. Frost/Freeze, Insufficient Chill Hours), begin and end dates | Open, US federal | en | 2012-2026 | O (2022 xlsx parsed) | P1 |
| [Chile emergency resolutions (Ley Chile)](https://www.bcn.cl/leychile/navegar?idNorma=1171039) | Peril, regions, comunas, start dates | Open | es | multi-year | O | P2 |
| [Argentina emergencia agropecuaria](https://www.argentina.gob.ar/agricultura/emergencia-agropecuaria) | Resolutions by province, from 2021 online ([list](https://www.magyp.gob.ar/sitio/areas/d_eda/resoluciones/)) | Open | es | 2021-2026 | O | P3 |
| [Mexico declaratorias (SSPC)](https://www.datos.gob.mx/dataset/gestion_riesgos) | Emergency 2018-2025 and disaster 2019-2025 CSVs | CC BY 4.0 | es | 2018-2025 | O | P3 |
| [Brazil S2iD](https://s2id.mdr.gov.br/) | Municipal recognitions with COBRADE codes | Open | pt | not read | OL (no response) | P2 |
| [Atlas Digital de Desastres no Brasil](https://atlasdigital.mdr.gov.br/) | Municipal disaster records, downloads | Open | pt | not read | O | P2 |
| [Peru INDECI / SINPAD](https://www.gob.pe/indeci) | Emergency registry | Open | es | not read | OL | P3 |
| [Poland ARiMR frost aid 2024](https://www.gov.pl/web/arimr/wsparcie-dla-poszkodowanych-przez-przymrozki-lub-grad-rolnikow-ktorzy-uprawiaja-owoce--trwa-nabor) | Eligible frost window 15 to 30 April 2024, hail 1 to 31 May 2024, borówki listed | Open | pl | 2024 | O | P1 |
| [South Africa NDMC classification example](https://www.gov.za/speeches/national-disaster-classification-7-nov-2023-0000) | National disaster classification for September 2023 floods | Open | en | per event | O | P3 |
| [Australia DisasterAssist](https://www.disasterassist.gov.au/find-a-disaster/australian-disasters) | AGRN list by state, type, date | Open; list is JavaScript | en | not read | OL | P3 |
| [NZ MPI adverse events](https://www.mpi.govt.nz/funding-rural-support/adverse-events/how-we-classify-adverse-events) | Localised, medium-scale, large-scale classification | JavaScript shell | en | not read | OL | P3 |
| [Canadian Disaster Database](https://www.publicsafety.gc.ca/cnt/rsrcs/cndn-dsstr-dtbs/index-en.aspx) | Major disasters, Open Government spreadsheet | Open | en, fr | not read | O | P3 |

### 4.3 Event databases and monitoring bulletins

| Source | Contents | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [NOAA Storm Events](https://www.ncei.noaa.gov/access/storm-events-database/) | Dated events by county or zone; Frost/Freeze, Hail; crop damage field | Open, US federal | en | 1950-present | O (2022 file parsed) | P2 |
| [SPC severe weather database](https://www.spc.noaa.gov/wcm/) | Point hail and wind reports 1955-2025 | Open | en | 1955-2025 | O | P3 |
| [EM-DAT](https://www.emdat.be/) | Global disasters with GADM units, dates, damage | Free registration, [non-commercial terms](https://doc.emdat.be/docs/legal/terms-of-use/) | en | 1900-present | O (docs) | P3 |
| [DesInventar](https://www.desinventar.net/DesInventar/) | Municipal records incl. FROST, HAILSTORM, HEATWAVE, "Damages in crops Ha." | Open; data terms not found | en, es | country-specific, mostly to 2013-2015 | O | P2 |
| [GDACS](https://www.gdacs.org/) | Cyclone, flood, drought alerts | Open | en | recent | O | P3 |
| [Copernicus EMS mapping](https://mapping.emergency.copernicus.eu/activations/) | Flood and fire activations | Open; JavaScript list | en | 2012-present | OL | P3 |
| [ReliefWeb](https://reliefweb.int/) and [API](https://apidoc.reliefweb.int/) | Disaster pages and reports; API needs pre-approved appname since 1 Nov 2025 | Open | en, es, fr | 1996-present | O | P3 |
| [JRC MARS Bulletin](https://joint-research-centre.ec.europa.eu/monitoring-agricultural-resources-mars/jrc-mars-bulletin_en) | Monthly European crop-weather narrative; archive since 2007 | Open; terms not found | en | 2007-present | O (archive OL) | P2 |
| [EDO/GDO and EDID](https://drought.emergency.copernicus.eu/) | Drought indicators and impact database | "free, full and open access" under Regulation (EU) 2021/696 | en | varies | O | P3 |
| [ESWD](https://www.essl.org/cms/european-severe-weather-database/) | European hail, wind, rain reports | User's Agreement; no commercial use | en | not read | OL | P3 |
| [Poland SMSR drought monitoring](https://susza.iung.pulawy.pl/) | Gmina drought flags by crop group | Open | pl | not read | O | P3 |
| [AAFC Agroclimate Impact Reporter](https://agriculture.canada.ca/en/agricultural-production/weather/agroclimate-impact-reporter) | Volunteer impact maps | Open | en, fr | not read | O | P3 |
| [CMA China Climate Bulletin](https://www.cma.gov.cn/zfxxgk/gknr/qxbg/) | Annual bulletins (2024, 2025 listed) | Open | zh | annual | O | P3 |
| [NIWA weather hazards](https://niwa.co.nz/hazards/weather-hazards) | Former HWE address now redirects here | Open | en | n/a | OL | P3 |

### 4.4 Yields and case studies

| Source | Contents | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [NASS Noncitrus Fruits and Nuts](https://esmis.nal.usda.gov/publication/noncitrus-fruits-and-nuts) | State blueberry acres, yield, production, price | Open | en | 3 years per release, archive older | O (table read) | P2 |
| [NASS Quick Stats API](https://quickstats.nass.usda.gov/api) | Same series via API | Free key required | en | varies | O | P3 |
| [ODEPA 2013 frost study](https://www.odepa.gob.cl/wp-content/uploads/2013/12/estudioDanioHeladas.pdf) | Arándano damage 10%; 4,761 t lost nationally, 3,716 t in Maule | Open | es | Sept 2013 | O | P2 |
| [PortalFruticola Ñuble frost 2022](https://www.portalfruticola.com/noticias/2022/11/09/chilecomo-se-han-afectado-los-arandanos-de-nuble-por-las-heladas/) | Frost 31 Oct and 1 Nov 2022; fruit set; 0 to over 80% damage | Open | es | 2022 | O | P2 |
| [Western Cape agriculture damage](https://www.westerncape.gov.za/agriculture/article/damage-western-cape-agriculture-infrastructure-estimated-r1053-billion) | R1.053 billion agricultural infrastructure damage | Open | en | 2023 | O | P3 |
| [FSA ELAP](https://www.fsa.usda.gov/resources/disaster-recovery/emergency-assistance-livestock-honeybees-farm-raised-fish) | Honeybee loss programme page only | Open | en | n/a | O | P3 |

### 4.5 Real samples of the top sources

**RMA `colsom_2022.txt`.** I downloaded `colsom_2022.zip` (5.5 MB, last modified 5 Oct 2026). It contains one pipe-delimited file with 30 fields. The [record layout](https://pubfs-rma.fpac.usda.gov/pub/Web_Data_Files/Summary_of_Business/cause_of_loss/COL_Summary_of_Business_with_Month_All_Years.pdf) names them: commodity year, state code and abbreviation, county code and name, commodity code and name, plan code and abbreviation, coverage category, stage code, cause code and description, month of loss and name, year of loss, policies earning premium, policies indemnified, net planted quantity, net endorsed acres, liability, total premium, producer-paid premium, subsidy, state/private subsidy, additional subsidy, EFA discount, net determined quantity, indemnity, loss ratio. A real row:

`2022|06|CA|019|Fresno|0012|Blueberries|90|APH|A|H|21|Hail|03|MAR|2022|3|3|31.96|...|610053.4|...|31.96|181923.4|6.41`

The 217 blueberry rows had these features:

- States: GA 67 rows, NC 37, MI 34, CA 28, FL 28, NJ 14, OR 6, WA 3.
- Plans: APH 184, SCO-YP 22, HIP-WI 11.
- Stage codes: H 124, UH 60, FL 33.

Indemnity by cause:

| Cause | Rows | Indemnity USD |
|---|---|---|
| 42 Freeze | 91 | 49,078,858 |
| 21 Hail | 15 | 8,775,631 |
| 55 Area plans (SCO and others) | 28 | 6,377,937 |
| 12 Heat | 25 | 5,716,623 |
| 61 Wind/Excess Wind | 9 | 4,829,053 |
| 92 Hurricane | 5 | 733,046 |
| 31 Excess Moisture/Precipitation/Rain | 13 | 492,232 |
| 41 Frost | 6 | 362,842 |
| 44 Cold Wet Weather | 5 | 205,122 |
| 43 Cold Winter | 3 | 133,372 |

Freeze indemnity by state and month: GA March 30.51 M, NC March 5.03 M, GA January 4.64 M, CA February 4.02 M, FL January 1.53 M, WA February 1.53 M.

Pitfalls seen in the real rows:

- One Alachua, Florida, freeze row is dated December 2021 but filed under crop year 2022.
- SCO-YP rows carry years of loss of 2023 and 2025 inside the 2022 crop year. These are area-yield triggers, not weather.
- One Sampson, North Carolina, row has month `00` and cause XX.
- No Plant Disease (81) or Insufficient Chilling Hours (45) rows appeared in 2022.

**RMA `SOBSCCTPU22.TXT`.** The file has 795 blueberry rows. Indemnity totals by state match the cause-of-loss file to the dollar. Type names are 001 Rabbiteye, 002 Highbush, 006 Early To Late Highbush (Group B) and 007 Very Late Highbush & Rabbiteye (Group A). Practice names include 032 Irr. With Frost Protection, 042 Irr. Without Frost Protection and 003 Non-Irrigated. Most North Carolina highbush acreage is insured as frost-protected (6,817 of 7,351 APH acres).

**Benchmark counties in 2022 (APH plan only; loss cost = indemnity / liability).**

| County | Insured acres | Liability USD | Indemnity USD | Loss cost | Largest cause-months |
|---|---|---|---|---|---|
| Bacon, GA (Alma) | 5,471 | 21,193,494 | 13,626,164 | 0.64 | Freeze Mar 11.84 M; Freeze Jan 1.77 M |
| Clinch, GA (Homerville) | 4,370 | 17,359,090 | 3,570,197 | 0.21 | Freeze Mar 2.88 M; Freeze Jan 0.67 M |
| Bladen, NC (Elizabethtown) | 5,170 | 23,528,075 | 8,217,871 | 0.35 | Freeze Mar 3.72 M; Wind Mar 2.88 M; Heat Jun 0.53 M |
| Pender, NC (Burgaw) | 1,722 | 7,792,458 | 517,917 | 0.07 | Freeze Mar 0.31 M; Wind Mar 0.17 M |
| Alachua, FL (Waldo) | 841 | 3,633,411 | 481,029 | 0.13 | Freeze Jan 0.33 M; Hail Apr 0.15 M |
| Marion, FL (Citra) | 96 | 924,372 | 436,134 | 0.47 | Freeze Jan 0.44 M |
| Atlantic, NJ (Hammonton) | 5,594 | 13,926,963 | 465,897 | 0.03 | Freeze Mar 0.33 M; Freeze Apr 0.09 M |
| Van Buren, MI (Grand Junction) | 4,953 | 9,097,498 | 720,191 | 0.08 | Heat May 0.39 M; Hail Jun 0.16 M; Frost Apr 0.07 M |

**FSA `METADATA_CY2022_SEC_YTD.xlsx`.** The file has 4,954 rows and 34 columns. Its columns are FIPS, County, State, Designation Code, Designation Number, 24 peril flags, Approval date, Begin Date, End Date, Description of disaster and CALENDAR DISASTER YEAR. The peril flags include "Frost, FREEZE", "Insufficient Chill Hours", "Heat, Excessive heat" and "Excessive rain, moisture, humidity". 345 rows carry the freeze flag. None carries Insufficient Chill Hours. On the page, the link labelled "2021" opens the CY2020 file.

**NOAA Storm Events details 2022.** The file has 69,887 rows and 51 columns: dates with `CZ_TIMEZONE`, `EVENT_TYPE`, `CZ_TYPE`, `CZ_FIPS`, `DAMAGE_CROPS`, `MAGNITUDE`, the begin and end coordinates, and the narratives. It has 423 Frost/Freeze rows, all forecast-zone records. None is in Georgia or North Carolina in March, and none has nonzero crop damage. Hail has 7,180 rows. The only blueberry mentions are road names.

**Brazil SISSER.** The [dictionary](https://dados.agricultura.gov.br/dataset/baefdc68-9bad-4204-83e8-f2888b79ab48/resource/2c5c55d0-1473-4749-b08f-cfaf887a9fa3/download/dicionariodedados-sisser.pdf) lists the insured's name and CPF/CNPJ, municipality, `CD_GEOCMU`, latitude and longitude, crop, area, insured yield, indemnity and `EVENTO_PREPONDERANTE`. I read a 13.9 MB partial sample of the 2025 CSV: 46,137 rows. Every `EVENTO_PREPONDERANTE` value in the sample was "-". No mirtilo row appeared.

**DesInventar Chile profile.** The profile shows FROST with 168 records and HAILSTORM with 14. Effect columns include "Damages in crops Ha.", "Losses $USD" and "Losses $Local". The database period is 1970 to 2014.

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON.

| Job | Sources | Output | Exact fields | Effort | Pri |
|---|---|---|---|---|---|
| GLOBAL-01 RMA blueberry cause-of-loss backfill | RMA COL, M13 codes, stage codes | time series table `rma_col_blueberry` | commodity_year, state_fips, county_fips, county_name, plan_code, coverage_category, stage_code, cause_code, cause_desc, month_of_loss, year_of_loss, policies_indemnified, net_planted_acres, liability_usd, total_premium_usd, net_determined_acres, indemnity_usd, source_file, file_last_modified; derived winter_season and risk_family | 2.0 d | P1 |
| GLOBAL-02 RMA exposure strata | RMA SOB tpu | time series table `rma_sob_blueberry` | commodity_year, state_fips, county_fips, plan_code, type_code, type_name, practice_code, practice_name, unit_structure, insured_acres, liability_usd, total_premium_usd, indemnity_usd; derived frost_protected_share, rabbiteye_share, loss_cost | 1.0 d | P1 |
| GLOBAL-03 FSA designations | FSA Secretarial files | event records | kind=event, topic=weather, period.start/end from Begin/End Date, precision=day, county FIPS, peril flags, designation number, approval date | 1.0 d | P1 |
| GLOBAL-04 Storm Events and SPC hail | NOAA, SPC | event records | BEGIN_DATE_TIME + CZ_TIMEZONE, county or zone, EVENT_TYPE, MAGNITUDE, DAMAGE_CROPS, EVENT_ID, narrative excerpt | 1.0 d | P2 |
| GLOBAL-05 NASS state yields | NASS Noncitrus, Quick Stats | time series table | state, year, species, area_harvested_acres, yield_lb_per_acre, production, utilized, price, value, release | 0.5 d | P2 |
| GLOBAL-06 DesInventar frost, hail, heat | DesInventar | event records | event type, date, admin1, admin2, crops ha, losses USD, source | 1.5 d | P2 |
| GLOBAL-07 Official declarations (CL, AR, MX, BR) | Ley Chile, MAGyP, SSPC, Atlas Digital, S2iD | event records | resolution number and date, peril, comunas or municipios, start and end, evidence_type=official_declaration | 2.0 d | P2 |
| GLOBAL-08 Brazil PSR claims | SISSER | event records | crop, CD_GEOCMU, lat/lon rounded to 0.1 degree, policy start and end, indemnity, cause; personal fields dropped | 1.5 d | P2 |
| GLOBAL-09 European narratives | MARS, ARiMR, ESWD, Agroseguro | claim records | period as written, region, crop_context, evidence_type, bulletin issue and page | 2.0 d | P2 |
| GLOBAL-10 Quantified blueberry frost cases | ODEPA 2013, PortalFruticola 2022, FADQ | event records | dates, region/comuna, stage wording, quantity in original unit, citation page | 0.8 d | P2 |

Every event record keeps the IBO record fields (`kind`, `topic`, `period`, `crop_context`, `evidence_type`, `geography_ids`, `citations`, `limitations`). Add `loss_basis`, which takes one of four values: insured_indemnity, declaration, estimate or narrative. Add `families_testable` as a list. A declaration never becomes a blueberry loss value.

## 6. How each source maps to model checks

### 6.1 Common rules for every family

**Unit of analysis.**

- US: county by season. Other countries: comuna or municipio by season, or region by season where only regional data exist.
- A Northern Hemisphere season runs from 1 October to 30 September. RMA commodity year Y maps to the winter of Y-1 to Y. A December loss filed under commodity year Y belongs to season Y. This happened in the 2022 Alachua row.
- A Southern Hemisphere season runs from 1 July to 30 June.

**Place matching.** The grid cell is 0.5 by 0.625 degrees, about 55 by 60 km at 31 N. A Georgia county spans one to four cells.

- Primary: use the cell that holds the county's blueberry centroid. Where a benchmark site lies in the county, use the site's cell.
- Sensitivity 1: count an event if any cell that touches the county has one.
- Sensitivity 2: use cell weights by cropland area.
- Neighbouring counties often share a cell, so their seasons are not independent. Resample by season or by cell, never by county-season.

**Date matching.**

- Build nightly minimum temperature in local standard time from MERRA-2 hourly data. A night runs from 18:00 on day D-1 to 10:00 on day D. POWER daily values are UTC days, and the checks already run used UTC windows. A freeze on the local night of 12 to 13 March can straddle two UTC days.
- RMA gives only the month of loss. A modelled event matches if a qualifying night falls in that month. If the night falls in the last five days of the previous month, it also matches, to allow for reporting lag.
- FSA begin and end dates, where present, confirm the night.
- A modelled event in the wrong stage window is a stage-timing miss. It is not a weather miss. Report the two separately.

**Labels.**

- Positive county-season for a family: indemnity from the mapped causes in the family's stage months, divided by APH liability, is at least the pre-registered threshold, and at least two policies are indemnified.
- Negative: liability is above zero and no mapped indemnity is paid.
- Missing: no liability, or fewer than three policies earning premium.
- Exclude area plans (cause 55), the XX cause, and rows with month 00.

**Metrics.**

- Hit rate (probability of detection) and false alarm ratio.
- Peirce skill score: hit rate minus false alarm rate.
- ROC AUC of a continuous model severity, such as the lowest Tmin in the stage window.
- Brier skill score of the model's per-county event frequency against county climatology.
- Recurrence correlation: Spearman rank correlation across counties between modelled event frequency and observed loss frequency.
- Report 95% intervals from a season-block bootstrap.

**Base rates.** Compute observed loss frequency per county and family before looking at model output. The app ranks a risk at 50% of winters or more (`risk_min_frequency`, `pipelines/weather/production.py`). A family with an observed loss base rate under about 10% will produce many false alarms by construction. Score such families with AUC and the Brier score, not with the ranking gate.

**Confounders to record for every score.**

1. Insurance participation and liability changes, from SOB acres by year.
2. Frost-protection share (SOB practice 032 versus 042).
3. Species share (rabbiteye versus highbush types).
4. Price elections. Use acres lost (net determined quantity divided by net planted quantity) as a price-free check.
5. Cause coding. A windborne freeze can be coded Wind (Bladen, March 2022, USD 2.88 million).
6. Tunnels and macrotunnels. These are rare in insured US blueberry but dominant in Huelva, Morocco and Colombia.
7. New plantings and abandonment.
8. Grid warm bias of about +1 C in Tmin. Run raw and corrected variants.

**Pre-registration (do this before any tuning).**

1. Write `config/validation_preregistration_losses.yaml`. It holds the county list, seasons, cause-to-family crosswalk, thresholds, primary grid variant, expected direction and minimum skill for each family, and the families declared exploratory.
2. Record the model commit and the profile hash.
3. Split the seasons. Odd commodity years are for any threshold or bias-correction choice. Even years are for scoring. Alternatively, tune on 2011-2017 and test on 2018-2025.
4. Compute the SHA-256 of the file and print it in the validation report.
5. Report every family, including failures. Add no counties or seasons after unblinding.

### 6.2 Family-by-family design

| Family | Loss sources that can test it | Matching rule | Metric | Base rate and confounders | Pre-registered expectation |
|---|---|---|---|---|---|
| Bud-stage freeze (`bud_freeze_days`) | RMA 42, 41, 43 in months between modelled budbreak and flowering start; FSA freeze dates; ODEPA 2013 Chile; ARiMR 2024 window | Night with Tmin at or below -6.7 C (early) or -3.9 C (late) inside the bud window | POD, FAR, Peirce; AUC of the lowest bud-window Tmin | Florida January 2022 freezes (Alachua, Marion) fall before the modelled flowering starts at Waldo (7 Feb median) and test this family. Code 43 Cold Winter can be dormant-season injury: report it separately. | Exploratory in the US Southeast; primary in Florida. |
| Flowering freeze (`flower_freeze_days`) | RMA 42 and 41 in flowering months; FSA dates; IBO 2022 Southeast record | Night with Tmin at or below -2.2 C inside the modelled flowering window | As above, plus Spearman across counties | Frost protection on 6,545 of 9,700 GA highbush APH acres and 6,817 of 7,351 NC highbush acres lowers losses for a given temperature. Stratify. | Primary family. See 6.3. |
| Fruit frost (`fruit_frost_days`) | RMA 42 and 41 after flowering end; Chile 2022 fruit-set frost; IBO Poland 2024 and 2025 green-fruit frost; DesInventar FROST | Night with Tmin at or below 0 C between flowering end and harvest start | POD, FAR | Few US cases expected. Outside the US, use event-level checks only. | Exploratory. |
| Fruit-stage heat (`fruit_severe_heat`) | RMA 12 Heat and 62 Hot Wind; FSA heat flag; IBO Chile Dec 2022, Peru El Niño 2023 | Day with Tmax at or above 35 C (severe) or 32 C in the fruit window; month match | AUC of hottest fruit-window Tmax; POD | 2022 had heat losses in Van Buren MI (May) and Bladen NC (June). Michigan May falls before the modelled MI flowering (June), so a hit there needs fixed phenology first. | Exploratory until cool-climate phenology is fixed. |
| Harvest heavy rain (`harvest_heavy_rain`) | RMA 31 Excess Moisture, 92 Hurricane; FSA excess-rain flag; Agroseguro Huelva; IBO NC 2024 and 2025 | Day with rain of 10 mm or more in the harvest window, month match | AUC of harvest heavy-rain days; Brier | The app ranks this risk at nearly every site. RMA excess-moisture losses were small in 2022 (USD 0.49 million). Expect low precision: the model measures exposure, not loss. | Primary for a calibration test of the threshold, not for detection. |
| Disease weather (`disease_weather`) | RMA 81 Plant Disease (none seen in 2022); IBO anthracnose narratives | Infection-index day in flowering to harvest, month match | Descriptive counts only | Disease losses are rarely insured as a separate cause. Fungicide use breaks any weather-to-loss link. | Declared descriptive; no skill target. |
| Pollination gap (`flowering_longest_no_flight_run`) | No direct loss source found. Proxies: RMA 44 Cold Wet Weather in flowering months; FSA "Cold, wet weather" flag; IBO PNW 2022 pollination problem | Run of 4 or more no-flight days in flowering, month match | Descriptive; odds ratio if 20 or more positives | Bee hiving density and bumble bees confound. Code 44 also covers other cold-wet damage. | Declared exploratory. |
| Chill shortfall (`chill_shortfall`) | RMA 45 Insufficient Chilling Hours; FSA "Insufficient Chill Hours" flag; IBO Florida warm winters | Season with chill hours below the profile requirement; season match | POD, FAR; Spearman across counties | 2022 had no ICH rows in RMA and no ICH flags in FSA. Count ICH rows in all years before choosing a target. Cyanamide use and low-chill cultivars reduce losses. | Primary only if the backfill finds 10 or more positive county-seasons. |

Outside the US the same rules apply at event level:

- DesInventar FROST records by comuna test flowering and fruit freeze recurrence in Chile and Argentina for 1990 to 2014.
- Chile and Argentina declarations, the ARiMR window, MARS bulletins and the case studies are single dated events. Score them as a case list: did the cell show a qualifying night inside the correct stage window? Do not compute a false alarm rate from them, because absence of a declaration is not absence of a loss.

### 6.3 Worked example: RMA blueberry freeze indemnities versus modelled flowering-freeze winters (US)

**Question.** Across insured blueberry counties, do seasons with a modelled flowering-freeze night line up with seasons and months of RMA freeze indemnity? Does the model's per-county flowering-freeze frequency rank counties the same way as observed freeze-loss frequency?

**Step 1. Universe (pre-registered).** Counties with blueberry APH liability of at least USD 1 million in at least 8 of the 15 commodity years 2011 to 2025, in FL, GA, NC, NJ and MI. In 2022 this includes Bacon, Clinch, Bladen, Pender, Alachua, Atlantic and Van Buren, each holding a benchmark site. List the full set from GLOBAL-02 before scoring.

**Step 2. Observed label.**

- Take APH-plan rows with cause 41 or 42.
- Freeze loss cost = indemnity divided by APH liability for the county-season.
- Positive if the loss cost is at least 0.05 and at least two policies are indemnified. Sensitivity thresholds: 0.02 and 0.10.
- Keep the month vector.
- Run a sensitivity that adds cause 61 in February to April, to catch windborne freezes.

**Step 3. Model output.** For each county cell and season, run `stage_thermal_v3` and keep four outputs:

- flowering start and end;
- `flower_freeze_days` (Tmin at or below -2.2 C);
- `bud_freeze_days`;
- the lowest Tmin in the flowering window, from local-time nightly minima.

Keep the raw grid as the primary run and the Tmin-corrected run as a pre-registered secondary.

**Step 4. Match.**

- Season level: a hit is a modelled flowering-freeze night plus an observed positive.
- Month level: share of observed loss months that contain a modelled freeze night in the bud or flowering window.
- Where FSA has a freeze designation for the county, check that the modelled night falls between Begin Date and End Date.

**Step 5. Metrics.** Compute pooled and per-state results:

- the contingency table, POD, FAR, POFD and Peirce;
- AUC of the lowest flowering-window Tmin as a predictor of a positive;
- Spearman across counties of modelled flowering-freeze frequency against observed freeze-loss frequency;
- Brier skill against each county's climatology.

Use a season-block bootstrap with 2,000 resamples.

**Step 6. Pre-registered expectations (to be signed before running).**

1. For 2022, the model flags a flowering-freeze night at Alma, Homerville, Elizabethtown and Burgaw. The earlier check found grid Tmin of -3.12, -2.53, -5.47 and -5.24 C on 13 March 2022 (`ibo_event_checks.json`). Each county's RMA March freeze loss is positive at the 0.05 threshold except Pender, at 0.04 for freeze alone [computed from the 2022 sample: 309,276 / 7,792,458]. The 2022 losses were already inspected for this report, so this item is a sanity check, not a blind test. Keep 2022 out of the headline score, or flag it.
2. Pooled GA and NC: POD at least 0.6, FAR at most 0.5, Peirce above 0.2.
3. The Spearman correlation across counties is at least 0.4.
4. Expected failures, stated in advance:
   - New Jersey and Michigan. The modelled flowering starts 30 April (Hammonton) and 1 June (Grand Junction). The 2022 losses were in March and April. Misses there are attributed to phenology timing, not to the freeze threshold.
   - Florida January freezes. Alachua and Marion losses in January 2022 come before the modelled flowering at Waldo. They should be scored under bud freeze, not flowering freeze.
5. Frost-protected share will lower the loss rate at a given modelled freeze severity. Test this with a logistic model: loss on lowest Tmin, frost-protected share, and their interaction. The expected interaction sign is positive.

**Step 7. Confounder handling.**

- Repeat the scoring with acres lost (net determined quantity divided by net planted quantity) in place of dollars.
- Drop seasons in which county liability changed by more than 50% from the previous season.
- Report results separately for counties with rabbiteye share above and below 50%.

**Step 8. Sample size and power [inference].** About 10 to 15 counties over 15 seasons gives 150 to 225 county-seasons. Neighbouring counties share cells and freeze nights, so the effective sample may be closer to 40 to 75 independent cell-seasons. A Peirce score difference of 0.2 will have wide intervals. Treat the pooled score as a check, not as a calibration target.

**Step 9. What would change the model.** No threshold change is allowed on even seasons. If odd-season results show that -2.2 C misses most losses, test the stage-specific critical temperatures (NC State values already used for bud freeze) on odd seasons. Then score them once on even seasons.

## 7. Access, licensing and language risks

- **US federal data** (RMA, FSA, NOAA, NASS): no licence text was found. The data are US federal works. Cite the file name and the file date, because RMA revises past years (the 2022 file was modified on 5 Oct 2026).
- **EM-DAT**: free registration, no commercial use without a separate licence ([terms](https://doc.emdat.be/docs/legal/terms-of-use/)). **ESWD**: signed User's Agreement, no commercial use. **ReliefWeb API**: pre-approved appname required from 1 November 2025. **NASS Quick Stats**: free key.
- **Brazil SISSER** is CC BY, but it holds names and CPF/CNPJ numbers. Drop those columns before anything is stored. Never show farm coordinates; round them to 0.1 degree.
- **Blocked or unreachable**: Agroseguro (403), S2iD (no response), JRC publications repository ("Request Rejected"), MPI New Zealand (JavaScript shell), SHELDUS (login). Use landing pages and cite search-only facts as such.
- **DesInventar** software is under an "Apache-2-like" licence. Data reuse terms were not found. Confirm before public display.
- **Languages**: Spanish (Chile, Argentina, Mexico, Peru, Spain), Portuguese (Brazil), Polish, French (Quebec), Chinese (CMA). Declarations use local legal names for perils: helada, geada, przymrozki, gel. Keep the original words in the records.

## 8. Gaps

- **No open blueberry-specific loss data outside the US.** Chile's Agroseguros publishes contracts, not claims. Agroseguro pools blueberries with other berries and was blocked. Peru's SAC covers smallholder crops, not export blueberries. No Morocco, Zimbabwe, Namibia or China loss tables were found. DesInventar's Morocco series ends in 2014.
- **No pollination-failure loss data anywhere.** FSA ELAP covers honeybee colony losses, not pollination.
- **Disease losses are almost uninsured.** No blueberry cause-81 rows appeared in RMA 2022.
- **Storm Events frost recall is poor.** It has no March 2022 Southeast freeze rows, so absence there is not evidence of no frost.
- **Day-level dates.** RMA has months only. FSA dates exist only where a county was designated.
- **Not checked in this pass.** Multi-year RMA counts of cause 45 Insufficient Chilling Hours, because only one yearly file was opened under the sample rule. BC and FADQ claim history by year (the FADQ bilans showed no blueberry row in 2025 to 2026). The NIWA Historic Weather Events catalogue (its address now redirects). The South African NDMC list of classifications (no structured list found).
- **Search-only facts.** The PROAGRO frost and hail shares (4.4% and 4.1%) and the ARiMR loss bands for borówki were seen in search snippets only.

## 9. Ranked top 10 actions

1. **Build GLOBAL-01 and GLOBAL-02.** Backfill RMA blueberry cause-of-loss and SOB type and practice files for 1989 to 2026 into two tables, with the cause-to-family crosswalk (3 days).
2. **Write and hash the pre-registration file** for the US freeze example (section 6.3) before running any model comparison (0.5 day plus expert time from Paul).
3. **Add local-time nightly Tmin from MERRA-2 hourly data** for stage windows. Rerun the 13 March 2022 checks in local time (1 day).
4. **Build GLOBAL-03.** Ingest FSA designations to add day dates and the Insufficient Chill Hours flag (1 day).
5. **Run the worked example** on odd seasons, then score once on even seasons. Publish POD, FAR, Peirce, AUC and Spearman with season-block intervals (2 days).
6. **Count RMA cause 45 rows across all years** to decide whether chill shortfall can be a primary validation family (0.5 day, part of action 1).
7. **Re-examine the Chile November 2022 and Poland April 2024 IBO cases** with the corrected dates (31 October to 1 November 2022 at fruit set; 15 to 30 April 2024). Use station data from the region agents (0.5 day).
8. **Run GLOBAL-06.** Extract DesInventar FROST and HAILSTORM records for Chile, Argentina, Peru and Uruguay for a pre-2015 recurrence check (1.5 days).
9. **Run GLOBAL-08 on SISSER.** Confirm whether mirtilo appears. If it does not, decide whether frost claims on other fruit are acceptable for frost-detection checks in southern Brazil (1.5 days).
10. **Run GLOBAL-09.** Extract frost, heat and rain sentences from JRC MARS bulletins for 2015 to 2026 for northern highbush areas, as reviewed claim records (2 days).
