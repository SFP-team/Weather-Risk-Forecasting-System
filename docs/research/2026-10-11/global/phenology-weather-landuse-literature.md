# Global sources: phenology observations, cultivar data, land use, remote sensing, weather and literature

Slug: `phenology-weather-landuse-literature`. Checked on 2026-10-11. Machine-readable list: [phenology-weather-landuse-literature.sources.json](phenology-weather-landuse-literature.sources.json) (78 sources, 9 jobs).

This report adds to [04_validation_data_and_protocol.md](../../2026-09-21/04_validation_data_and_protocol.md), [07_weather_inputs_and_global_scaling.md](../../2026-09-21/07_weather_inputs_and_global_scaling.md) and [GLOBAL_PHENOLOGY_REVIEW.md](../../../weather/GLOBAL_PHENOLOGY_REVIEW.md). It does not repeat their sources unless there is new information. Every count below came from a live query on 2026-10-11 unless marked otherwise. My own reasoning is marked [inference].

## 1. Scope and summary

Covered: phenology networks (USA-NPN, iNaturalist, GBIF, PEP725, DWD, JMA, CPON), cultivar data (GRIN, NCGR, UPOV, CPVO, US plant patents, PBR offices, the HortScience cultivar register), land use (CDL, EuroCrops, Dutch BRP, Huelva plastic maps, global greenhouse maps, orchard census pointers), remote sensing (Sentinel-2, HLS, MODIS and VIIRS phenology, MSLSP30NA, blueberry drone and satellite studies), weather not yet in report 07, and literature access (14 indexes and national repositories with real hit counts).

Five most valuable findings:

1. **Open phenology data exist only for cool climates, but there they are good.** USA-NPN returned 4,898 highbush and 2,716 lowbush onset records (CC BY 4.0). None fall within 100 km of Citra, Waldo, Alma, Homerville or Grand Junction. They do cluster near the cool-climate pins the model fails on: 19 plants near Cherryfield (ME) and 6 near Hammonton (NJ). iNaturalist adds 97 flowering and 91 fruiting annotations within 50 km of Cherryfield, but almost nothing in the Southern Hemisphere.
2. **The cultivar table can be built from public documents.** HortScience's *Register of New Fruit and Nut Cultivars* (List 53, 2026, CC BY-NC 4.0) gives chill class, season and evergreen habit per release. US plant patents give chill hours and ripening offsets in days against named reference cultivars. UPOV TG/137 gives a 1 to 9 scale for bloom and ripening time.
3. **Hourly station truth is close to almost every benchmark site.** The NOAA GHCNh station list puts a station within 25 km of 39 of the 53 sites and within 50 km of 50. The Linares and Chillán stations are under 1 km from their pins, and Hamilton AWS is 8.5 km from Ohaupo. Those are the sites of the IBO freezes the grid missed.
4. **Location and protection layers exist.** The USDA Cropland Data Layer has a blueberry class (242), but its 2024 accuracy is low: 45.4% producer's and 39.1% user's accuracy. EuroCrops maps a blueberry code for 11 national datasets, including Spain 2023 and Portugal 2021. Junta de Andalucía maps 17,164 ha under plastic in Huelva (2021). Global-PCG-10 maps greenhouses worldwide at 10 m.
5. **New weather options.** ERA5-Land now has a point time-series service built for long series at single points. PRISM's homepage now says its 800 m grids are free, while report 07 said they were paid. MSWX offers bias-corrected global 0.1 degree temperature, but only for non-commercial use.

## 2. Production context in brief

- The app's 53 literature benchmark sites span 17 countries and three systems (evergreen, semi-evergreen, deciduous) ([benchmark_sites.json](../../../../pipelines/weather/benchmark_sites.json)). Southern Hemisphere and tropical supply (Peru, Chile, Mexico, Morocco, South Africa, Australia) relies heavily on evergreen or managed cycles. Temperate supply (US, Canada, Poland, Germany, China north) is mostly deciduous NHB or lowbush.
- Management moves calendars. Examples include Peru's delayed pruning in 2024 (IBO 2025 p.71) and evergreen production in Huelva, Morocco, Yunnan and Wolseley ([ibo_integration_review.md](../../2026-10-05/ibo_integration_review.md)).
- Protected cultivation is large in some production regions. Huelva had 15,276 ha of plastic surface in 2021, up 112% since 2004 ([Junta de Andalucía 2021](https://www.juntadeandalucia.es/sites/default/files/2021-11/Informe_plastico_huelva_v210305_1.pdf)). Globally, Tong et al. mapped 1.3 million ha of greenhouses in 2019, with Spain at 5.6%, Mexico 3.3% and Morocco 2.3% of the total ([Nature Food 2024](https://www.nature.com/articles/s43016-024-00985-0)).
- New cultivars drive the calendar. For example, List 52 records Berry Blue's 'BB14-232PT-2' as "no-chill, early ripening southern highbush selected in Peru" and Costa's 'C14-771' as evergreen with "chilling requirement 150-300 h" ([NMSU copy of List 52](https://jujube.nmsu.edu/documents/2024-fruit-cultivar-registration-52-hortsci-article-p1220.pdf)).

## 3. What the app already has for this scope

- **Phenology**: `GLOBAL_PHENOLOGY_REVIEW.md` lists 43 sources (S1 to S43). It verified the USA-NPN protocol (S38) but did not count records. It also uses one patent (S37), the UGA release dossier (S9), Kovaleski (S7), Campa and Ferreira (S8) and the BBCH scale (S2).
- **Weather**: report 07 covers POWER biases, ERA5-Land (CDS and Open-Meteo), AgERA5, CHIRPS, IMERG, TerraClimate, Daymet, PRISM, gridMET, hourly reconstruction and lapse rates. Report 04 covers FAWN, UGA AEMN, INMET, Epagri/CIRAM, Agromet, SIAR, BOM and GHCN-Daily (already used in `validate_observations.py`).
- **Evidence layer**: 91 IBO records (39 events, 42 practices, 10 constraints) in `dist/evidence/ibo-regional-v1.json`, with fields `kind`, `topic`, `period`, `crop_context`, `evidence_type`, `geography_ids` and `citations`.
- **Benchmark gaps this scope can address** (from the `gaps` section of `benchmark_sites.json`):
  - no site-specific evergreen phenology in Florida;
  - no evergreen versus deciduous acreage split in central Florida;
  - Chilean bloom months not found (INIA PDFs returned 403);
  - Peru pruning dates only from one trial;
  - no China bloom months;
  - no tunnel-share data for north Florida;
  - Huelva calendar only from breeders.
- **Known model gaps**: cool climates; coastal Peru (41 to 51 days modelled versus about four months reported); Pelotas rabbiteye too early; Tafí del Valle; Penguin with 58 chill hours; the Chile (November 2022) and Waikato (October 2022) freezes missing from grid cells; and no cultivar classes.

## 4. Source inventory

Status codes: `opened` means I fetched the page and saw matching content. `opened-limited` means a bot wall, login, JavaScript-only page or error. Full fields for every source are in the JSON.

### 4.1 Phenology observation networks

| Source | What it contains (seen) | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [USA-NPN observational data](https://www.usanpn.org/data/observational) | One `getSummarizedData` call returned 7,885 onset rows. Highbush: 4,898 rows (225 plants, 132 sites). Lowbush: 2,716 (79 plants). V. virgatum: 36 (5 plants). V. darrowii: 235 (8 plants, all GA). Highbush rows include 421 open-flower and 396 ripe-fruit onsets. Fields: `site_id, latitude, longitude, elevation_in_meters, state, individual_id, phenophase_description, first_yes_doy, numdays_since_prior_no, last_yes_*` | Open, CC BY 4.0 ([Data Use Policy](https://www.usanpn.org/about/terms)) | en | 2009-2026 | opened | P1 |
| [iNaturalist API v1](https://api.inaturalist.org/v1/docs/) | All quality grades. Term 12 "Flowers and Fruits" and term 36 "Leaves". V. corymbosum: 25,852 obs, 1,063 Flowers, 1,261 Fruits, 293 Flower Buds, 52 Breaking Leaf Buds, 3,338 captive. V. angustifolium: 34,063 / 1,697 / 1,750 / 287 / 35. V. virgatum: 873 / 31 / 34 / 8 / 2. V. darrowii: 2,271 / 64 / 100 / 29 / 20 | Open API; licence per observation (sample record: cc0) | en | many years | opened (website 403) | P2 |
| [GBIF occurrence API](https://techdocs.gbif.org/en/openapi/v1/occurrence) | V. corymbosum 37,723 records (24,725 specimens; US 30,694; NL 2,592). V. angustifolium 22,030. V. darrowii 2,386. V. ashei is a synonym of corymbosum in the backbone, and V. virgatum did not match. The iNaturalist subset (6,450 corymbosum) is CC BY-NC 4.0, and `reproductiveCondition` was empty in the sample | Per-dataset licence | en | specimens to present | opened (website 403) | P3 |
| [PEP725](https://pep725.eu/) | Over 13 million records, about 265 species ([New Phytologist 2026](https://pmc.ncbi.nlm.nih.gov/articles/PMC13001019/)). Vaccinium appears only in a search snippet | Free registration. The [pep725 R vignette](https://rdrr.io/cran/pep725/f/inst/doc/getting-started.Rmd) says there is no redistribution | en, de | from 1868 | opened-limited | P3 |
| [DWD phenology open data](https://opendata.dwd.de/climate_environment/CDC/observations_germany/phenology/) | Fruit: apple, pear, plum, cherries, red currant, gooseberry. 34 wild species. **No Vaccinium** | Open; terms PDF not read | de | 1925-2024 | opened | P3 |
| [JMA phenology](https://www.data.jma.go.jp/sakura/data/index.html) | Plum and cherry flowering, maple and ginkgo colouring. **No blueberry** | Open | ja | long-term | opened | P3 |
| [CPON 24-species grid (ESSD)](https://essd.copernicus.org/articles/16/277/2024/) | 24,552 observations of 24 woody plants, 122 sites, 1951-2020. Data at [ScienceDB](https://doi.org/10.57760/sciencedb.07995). Homepage cpon.ac.cn timed out | Article CC BY 4.0 | en, zh | 1951-2020 | opened | P3 |
| [UMaine Signs of the Seasons, lowbush](https://extension.umaine.edu/signs-of-the-seasons/indicator-species/lowbush-blueberry-fact-sheet/) | Lowbush indicator-species protocol. It cites the USA-NPN protocol, so its data likely feed NPN [inference] | Open | en | n/a | opened | P3 |

**Records near production areas.** NPN plants within 100 km: Tallahassee 8, Hammonton 6, Elizabethtown 2, Burgaw 1, and 0 at the other 13 US benchmark sites. Near the Cherryfield pin there are 19 plants (17 open-flower onsets); near Lynden, 34 plants (0 open-flower onsets); near Lac-Saint-Jean, none. Pin coordinates are approximate.

iNaturalist observations within 50 km (all four taxa; total / Flowers / Fruits):

| Site | Total | Flowers | Fruits |
|---|---|---|---|
| Hammonton | 1,157 | 80 | 73 |
| Cherryfield pin | 1,382 | 97 | 91 |
| Citra | 178 | 4 | 5 |
| Grand Junction | 185 | 1 | 10 |
| Lynden pin | 172 | 3 | 8 |
| Alma | 3 | 0 | 0 |

Chillán, Moguer, Lublin and Coffs Harbour each had 0 or 1 observation.

### 4.2 Cultivar data

| Source | What it contains (seen) | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [HortScience Register of New Fruit and Nut Cultivars, List 53](https://doi.org/10.21273/hortsci19596-26) and [List 52](https://doi.org/10.21273/hortsci18040-24) | Blueberry section per cultivar: trade name, type, chill requirement or class, ripening season, evergreen habit, breeder, selection place and year, USPP or PBR number and date (sampled in the [List 52 copy](https://jujube.nmsu.edu/documents/2024-fruit-cultivar-registration-52-hortsci-article-p1220.pdf)) | CC BY-NC 4.0 (Crossref). ASHS pages are JavaScript-walled | en | Lists 43 (2006) to 53 (2026) | opened | P1 |
| [US plant patents (Google Patents text)](https://patents.google.com/patent/USPP24876P3/en) | USPP24876 states "approximately 200-300 hours (<7 C)" of chill, maturity "earlier by 5-7 days" than Star and "earlier by 10 days" than Emerald, and a test site near Interlachen, Fla. The [USPTO image PDF](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/PP24876) has no text layer | Public documents | en | 1990s-present [inference] | opened | P1 |
| [UPOV TG/137/5 Rev. Blueberry](https://www.upov.int/documents/d/upov/tg-documents-en-tg137.pdf) | Characteristics 34 to 37 score the time of flowering and ripening from 1 to 9. Flowering examples: Patriot 1, Weymouth 3, Berkeley 5, Darrow 7, Jersey 9. Ripening examples: Bluetta 1 to Elizabeth 9. Chill groups: H is above 750 h and L is below 600 h, counting hours below 7 C | Open PDF | en, fr, de, es | 2019, rev. 2022 | opened | P1 |
| [UPOV PLUTO](https://www.upov.int/en/find-and-explore/databases/pluto-search) | Protected varieties by country (PBR, plant patents, national lists) | Free registration (WIPO account), no download. Premium costs CHF 750 per year ([terms](https://www.upov.int/en/file-and-manage/pluto-contribute/terms-of-use)) | en | varies | opened | P2 |
| [GRIN-Global](https://npgsweb.ars-grin.gov/gringlobal/search) | Vaccinium accessions; descriptors not readable | HTTP 502 on 2026-10-11 | en | unknown | opened-limited | P2 |
| [NCGR Corvallis](https://www.ars.usda.gov/pacific-west-area/corvallis-or/national-clonal-germplasm-repository/) | Holds the berry collections; links to GRIN | Open | en | n/a | opened | P3 |
| [CPVO Variety Finder](https://vf.plantvarieties.eu/) and [technical protocols](https://cpvo.europa.eu/en/applications-and-examinations/technical-examinations/technical-protocols/cpvo-technical-protocols) | EU protection records | JavaScript-only | en | varies | opened-limited | P3 |
| [Canada PBR Office](https://inspection.canada.ca/en/plant-health/plant-varieties/plant-breeders-rights) | Plant Varieties Journal and variety descriptions | Open | en, fr | varies | opened | P2 |
| [IP Australia PBR](https://www.ipaustralia.gov.au/plant-breeders-rights) | Information page; the database host did not resolve | Open | en | varies | opened-limited | P2 |
| [PatentsView, now on the USPTO ODP](https://data.uspto.gov/support/transition-guide/patentsview) | Bulk patent metadata | Service in transition, JavaScript only | en | n/a | opened-limited | P3 |

### 4.3 Land use and orchard location

| Source | What it contains (seen) | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [USDA NASS Cropland Data Layer](https://www.nass.usda.gov/Research_and_Science/Cropland/SARS1a.php) / [CroplandCROS](https://croplandcros.scinet.usda.gov/) | Class 242 Blueberries at 30 m. [2024 metadata](https://www.nass.usda.gov/Research_and_Science/Cropland/metadata/metadata_CDL24_FGDC-STD-001-1998.htm): 368 correct pixels, producer's accuracy 45.4%, user's accuracy 39.1% | "public domain and free to redistribute" | en | annual | opened | P1 |
| [EuroCrops](https://github.com/maja601/EuroCrops) | HCAT3 `blueberry` 3303020400. National codes mapped for Flanders (9722), DK (519), EE, ES 2023 (216 ARÁNDANO), FI (5313), IE, LV (924), NL (1869), PT 2021 (202 MIRTILO), SI (652) and SK. No blueberry mapping found for DE, PL or AT | CC BY-SA 4.0 | multi | 2018-2023 single years | opened | P1 |
| [Junta de Andalucía, plastic cartography Huelva 2021](https://www.juntadeandalucia.es/sites/default/files/2021-11/Informe_plastico_huelva_v210305_1.pdf) | Sentinel-2 images from 11 Jan and 15 Feb 2021, on SigPac parcels. 17,164 ha mapped, 15,276 ha of plastic surface, table by municipality, series since 2004 | Terms not found | es | 2004-2021 seen | opened | P1 |
| [Global-PCG-10 (ESSD 2025)](https://essd.copernicus.org/articles/17/5065/2025/) | 10 m global greenhouse map for 2020. Overall accuracy 98.04% ± 0.12%; total area 14,259.85 km2 | Article CC BY 4.0; data licence not read | en | 2020 | opened | P2 |
| [Tong et al. 2024](https://www.nature.com/articles/s43016-024-00985-0) | 1.3 million ha of greenhouses in 119 countries, 2019 | Terms not found | en | 2019 | opened | P3 |
| [PDOK BRP Gewaspercelen](https://www.pdok.nl/introductie/-/article/basisregistratie-gewaspercelen-brp-) | Annual Dutch crop parcels (WFS, OGC API, Atom) | Terms not found | nl | annual | opened | P3 |
| [ODEPA catastros frutícolas](https://www.odepa.gob.cl/estadisticas-del-sector/catastros-fruticolas) | Chilean orchard census (pointer) | Open | es | regional rounds | opened | P2 |
| [USDA Quick Stats](https://quickstats.nass.usda.gov/) | Census county acres (already used by the benchmark) | Open | en | 2002-2022 | opened | P3 |

### 4.4 Remote sensing

| Source | What it contains (seen) | Access and terms | Lang | Coverage | Status | Pri |
|---|---|---|---|---|---|---|
| [MSLSP30NA v011](https://www.earthdata.nasa.gov/data/catalog/lpcloud-mslsp30na-011) | 30 m North American dates for greenup, maturity, senescence and dormancy | Earthdata login | en | 2016-2019 | opened | P2 |
| [HLS S30](https://www.earthdata.nasa.gov/data/catalog/lpcloud-hlss30-2.0) and [L30](https://www.earthdata.nasa.gov/data/catalog/lpcloud-hlsl30-2.0) v2.0 | 30 m global; combined revisit about 1.6 days | Earthdata login | en | 2015-11-28 to present | opened | P2 |
| [Copernicus Data Space](https://dataspace.copernicus.eu/) | Sentinel-2 L2A | Free registration | en | 2015-present | opened | P2 |
| [MODIS MCD12Q2 v061](https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd12q2-061) and [VIIRS VNP22Q2](https://lpdaac.usgs.gov/products/vnp22q2v002/) | 500 m yearly greenup and dormancy dates | Earthdata login | en | 2001-present | opened | P3 |
| [Wild blueberry UAV phenology, Acta Hortic. 1357](https://ishs.org/ishs-article/1357_6/) | Drone indices against stages; R2 0.13 to 0.71 at bud break | Abstract free | en | single study | opened | P3 |
| [Wild blueberry multispectral, Remote Sens. 17:334](https://doi.org/10.3390/rs17020334) | Drone estimates of F4/F5 and F6/F7 stages (search abstract) | 403 | en | single study | opened-limited | P3 |
| [Nuevo Chao Sentinel-2 NDWI](https://www.mdpi.com/2673-4591/83/1/27) | Peru blueberry stage classification with 93% accuracy (search abstract) | 403 | en | single study | opened-limited | P3 |

### 4.5 Weather: new sources not in report 07

| Source | What it adds (seen) | Access and terms | Hourly? | Status | Pri |
|---|---|---|---|---|---|
| [ERA5-Land hourly time-series](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries) | ARCO subset "specifically designed for retrieving long time-series for individual points". 0.1 degree, 1950 to present, 2 m temperature and dewpoint | CDS account and licence acceptance | yes | opened | P1 |
| [NOAA GHCNh](https://www.ncei.noaa.gov/products/global-historical-climatology-network-hourly) | Replaces ISD. PSV or parquet files by station or year. [Station list](https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/doc/ghcnh-station-list.csv) has 38,870 stations: within 25 km of 39 of 53 sites, within 50 km of 50 | NOAA open data | yes | opened | P1 |
| [DMC Chile Servicios Climáticos](https://climatologia.meteochile.gob.cl/) | Hourly station data; annual "Recopilación de eventos extremos del año"; agroclimatic bulletins | Terms not found | yes | opened | P1 |
| [HadISD](https://www.metoffice.gov.uk/hadobs/hadisd/) | ISD stations with quality control "designed to remove bad data while keeping the extremes" | Non-Commercial Government Licence | sub-daily | opened | P2 |
| [IEM ASOS download](https://mesonet.agron.iastate.edu/request/download.phtml) | US METAR CSV export: `tmpf, dwpf, relh, p01i` | Terms not found | yes | opened | P2 |
| [Meteostat](https://dev.meteostat.net/) | Bulk CSV, Python library, JSON API | CC BY 4.0 ([legal](https://meteostat.net/en/legal)) | yes | opened | P2 |
| [MSWX](https://www.gloh2o.org/mswx/) | Bias-corrected global data, 0.1 degree, 3-hourly, from 1979 | CC BY-NC 4.0, request form | 3-hourly | opened | P2 |
| [MSWEP V3](https://www.gloh2o.org/) | Hourly 0.1 degree precipitation from 1979, with a 2-hour delay | Non-commercial, request form | yes | opened | P2 |
| [E-OBS v33.0e](https://surfobs.climate.copernicus.eu/dataaccess/access_eobs.php) | Daily European grid, 1950-2025 | "strictly for use in non-commercial research and education" | no | opened | P2 |
| [CR2MET v2.5](https://www.cr2.cl/datos-productos-grillados/) | Chile daily precipitation and temperature, 1960-2021 | Registration form; cite Boisier 2023 | no | opened | P2 |
| [CR2 Explorador Climático](https://explorador.cr2.cl/) | Chilean station explorer with export | Terms not found | daily | opened | P2 |
| [BR-DWGD](https://sites.google.com/site/alexandrecandidoxavierufes/brazilian-daily-weather-gridded-data) | Brazil daily 0.1 degree data, 1961-2025: Tmax, Tmin, rain, RH, wind, ETo | Terms not found | no | opened | P2 |
| [SILO](https://www.longpaddock.qld.gov.au/silo/) | Australian grids and infilled station series | CC BY 4.0 | no | opened | P2 |
| [FMI open data](https://en.ilmatieteenlaitos.fi/open-data) | Finnish stations (Naantali pin) | CC BY 4.0 | yes | opened | P2 |
| [ECCC historical climate](https://climate.weather.gc.ca/) | Canadian hourly and daily stations | [ECCC licence](https://climate.weather.gc.ca/prods_servs/attachment1_e.html) | yes | opened | P2 |
| [NIWA CliDB on DataHub](https://data.niwa.co.nz/pages/clidb-on-datahub) | Replaces CliFlo. New account; free for non-commercial use | Free registration | yes | opened | P2 |
| [WSU AgWeatherNet](https://weather.wsu.edu/) | Washington agricultural stations | JavaScript only | yes [inference] | opened-limited | P2 |
| [CERRA](https://cds.climate.copernicus.eu/datasets/reanalysis-cerra-single-levels) | European regional reanalysis, 1984 to present | CDS account | sub-daily | opened | P3 |
| [NOAA HRRR on AWS](https://registry.opendata.aws/noaa-hrrr-pds/) | 3 km hourly US model | "open to the public and can be used as desired" | yes | opened | P3 |
| [ISD and GSOD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database) | Legacy; GSOD days are GMT-based | NOAA open data | yes | opened | P3 |
| [OGIMET](https://www.ogimet.com/) | SYNOP archive from July 2004 | Terms not found | synoptic | opened | P3 |
| [AEMET OpenData](https://opendata.aemet.es/) | Spanish stations | JavaScript only; API key [inference] | yes | opened-limited | P3 |

### 4.6 Weather: already documented in report 07 or report 04 (only new details here)

| Source | New detail | Status |
|---|---|---|
| [PRISM](https://prism.oregonstate.edu/) | The homepage now says "Both 4km and 800m spatial resolutions available" and "We offer these datasets to the public free of charge". Report 07 said 800 m was paid; recheck the terms before use | opened |
| [Daymet](https://daymet.ornl.gov/), [gridMET](https://www.climatologylab.org/gridmet.html) | No change. gridMET RH min and max could serve as a disease-index reference in the Southeast | opened |
| ERA5-Land full grid, Open-Meteo, AgERA5, CHIRPS, IMERG, TerraClimate | Not re-listed. See report 07 | n/a |
| GHCN-Daily, FAWN, INMET, Agromet, SIAR, BOM, Epagri | Not re-listed. See report 04 | n/a |

### 4.7 Research literature access (real hit counts, 2026-10-11)

| Source | Query and hits | Access and terms | Status | Pri |
|---|---|---|---|---|
| [OpenAlex](https://openalex.org/) | `title_and_abstract.search: blueberry phenology` = 140 (77 OA). The boolean (blueberry OR Vaccinium) AND (bloom OR flowering) AND (date OR phenology) = 153. `search=arandano fenologia` = 11. Dissertations matching blueberry, arandano or mirtilo = 985. The top-cited hits were off-topic | CC0 data; free key with USD 1 per day of usage ([pricing](https://help.openalex.org/access/pricing/)) | opened | P1 |
| [CORE API](https://core.ac.uk/services/api) | `title:"blueberry" AND (phenology OR flowering OR bloom)` = 93 | Free without registration, rate-limited | opened | P1 |
| [SciELO](https://search.scielo.org/) | (mirtilo OR arándano OR blueberry) AND (fenologia OR fenología OR phenology) = 3. Adding flowering or harvest terms = 37. All blueberry = 108 | Per-article CC licences; scripts get 403 | opened | P1 |
| [INIA Chile Biblioteca](https://biblioteca.inia.cl/) | DSpace API: arándano = 621, + fenología = 64, + floración = 180, + heladas = 130 | Terms not read | opened | P1 |
| [ALICIA (Peru)](https://alicia.concytec.gob.pe/vufind/) | arándano = 870, + floración = 3, + cosecha = 53, + poda = 6, + fenología = 1 | Per thesis | opened | P1 |
| [Embrapa Alice](https://www.alice.cnptia.embrapa.br/) and [Infoteca-e](https://www.infoteca.cnptia.embrapa.br/) | Search returns 403; [OAI-PMH](https://www.alice.cnptia.embrapa.br/oai/request?verb=Identify) works | Terms not found | opened | P1/P2 |
| [Unpaywall](https://unpaywall.org/products/api) | doi 10.1371/journal.pone.0206361 → is_oa true, licence cc-by | Email parameter | opened | P1 |
| [Semantic Scholar](https://www.semanticscholar.org/product/api) | Bulk `blueberry + (phenology \| bloom \| flowering)` = 730 | Key on request | opened | P2 |
| [J-STAGE WebAPI](https://www.jstage.jst.go.jp/static/pages/JstageServices/TAB3/-char/en) | ブルーベリー 開花 = 168; blueberry flowering = 94 | J-STAGE terms | opened | P2 |
| [BASE](https://www.base-search.net/) | blueberry phenology = 326; the trilingual boolean = 367 | Bot check | opened | P2 |
| [Crossref](https://www.crossref.org/documentation/retrieve-metadata/rest-api/) | Relevance hits only (23,949); useful for DOIs and licences | Open | opened | P2 |
| [AGRIS](https://agris.fao.org/) | Search blocked by Cloudflare | Terms not found | opened-limited | P2 |
| [CNKI Overseas](https://oversea.cnki.net/index/) | Login wall. OpenAlex `search=蓝莓 物候期` gave 140 loose hits | Paid | opened-limited | P2 |
| [Acta Horticulturae](https://www.actahort.org/) | Bot check; ISHS abstract pages open | Paid full text | opened-limited | P2 |
| [Europe PMC API](https://europepmc.org/developers) | (blueberry OR Vaccinium corymbosum) AND (phenology OR bloom OR flowering) = 1,747 | Website 403; API works | opened-limited | P3 |
| [PMC and PubMed E-utilities](https://pmc.ncbi.nlm.nih.gov/tools/developers/) | PMC loose = 4,161; PubMed "blueberry AND phenology" = 35 | Only listed services allowed for automated retrieval | opened | P3 |
| [Redalyc](https://www.redalyc.org/) | "arándano fenología" = 4,393 (OR-style matching) | Diamond OA | opened | P3 |
| [RENATI](https://renati.sunedu.gob.pe/) | Search URLs return 404 | Bot check | opened-limited | P3 |
| [LA Referencia](https://www.lareferencia.info/vufind/) | 0 results for every query, including "arándano" | n/a | opened-limited | P3 |

## 5. Proposed extraction and RAG jobs

These match `rag_jobs` in the JSON. The record fields reuse the IBO design (`kind, topic, period, crop_context, evidence_type, geography, citations`) where outputs are claim or event records.

| Job | Output | Sources | Exact fields | Effort (days) | Pri |
|---|---|---|---|---|---|
| GL-01 Citizen phenology near pins | time series table | USA-NPN, iNaturalist, UMaine, GBIF | `obs_source, obs_id, lat, lon, elevation_m, taxon, cultivated_flag, stage, stage_definition_ref, event_date, doy, onset_precision_days, year, licence, nearest_benchmark_site_id, distance_km` | 2.5 | P1 |
| GL-02 Cultivar trait table | cultivar table | Register Lists, US patents, UPOV TG/137, PLUTO, CFIA, IP Australia, GRIN | see 5.3 | 6.0 | P1 |
| GL-03 Literature mining | event records + stage table | OpenAlex, Crossref, S2, CORE, Unpaywall, SciELO, J-STAGE, INIA, ALICIA, Alice, Europe PMC, BASE, AGRIS, CNKI, Acta Hort. | see 5.2 | 8.0 | P1 |
| GL-04 Hourly station truth | station table | GHCNh, HadISD, IEM, Meteostat, FMI, ECCC, NIWA, CR2, DMC, OGIMET, ISD, AgWeatherNet | `station_id, network, lat, lon, elevation_m, distance_to_site_km, elevation_difference_m, timestamp_utc, local_night_date, temperature_c, dewpoint_c, rh_pct, precip_mm, qc_flag, completeness_pct_by_month` | 4.0 | P1 |
| GL-05 Second-opinion grids | time series table | ERA5-Land time series, MSWX, MSWEP, E-OBS, CR2MET, BR-DWGD, SILO, PRISM, CERRA | `product, site_id, grid_lat, grid_lon, grid_elevation_m, date/hour, tmin_c, tmax_c, t2m_c, dewpoint_c, precip_mm, chill_hours_lt_7_2, frost_hours_le_0` | 4.0 | P2 |
| GL-06 Blueberry location mask | time series table | CDL, EuroCrops, BRP, Quick Stats, ODEPA | `grid_cell_id, year, blueberry_area_ha, n_parcels_or_pixels, source, class_accuracy_note` | 3.0 | P2 |
| GL-07 Protected cultivation share | claim records | Global-PCG-10, Junta Huelva, Tong 2024 | `kind=practice, topic=protection, geography, period, quantity_ha, crop_context="all crops under plastic", evidence_type, citations` | 2.0 | P2 |
| GL-08 Satellite phenology pilot | time series table | MSLSP30NA, HLS, CDL, EuroCrops, MCD12Q2, Sentinel-2 | `field_id, year, greenup_onset_doy, maturity_doy, senescence_doy, evi2_amplitude, product, matched_obs_bloom_date` | 4.0 | P3 |
| GL-09 Met-service extreme events | event records | DMC, INIA, Embrapa Infoteca, ALICIA | `kind=event, topic=weather, period, geography, hazard, measured_value_unit, crop_context, evidence_type=met_service_bulletin, citations(page)` | 3.0 | P2 |

### 5.1 Notes on GL-01 and GL-04

- GL-01: keep NPN rows only when `numdays_since_prior_no` is 14 or less. Report onset as an interval (prior no date, first yes date), not a point. Join to the nearest pin within 100 km. Do not pool wild V. corymbosum with commercial NHB without a flag.
- GL-04: aggregate to local nights. Compute monthly Tmin bias, sub-zero hit, miss and false alarm counts, and chill hours below 7.2 C. Then compare these with the MERRA-2 cell, following steps 1 and 2 of report 04's protocol. Start with Linares, Chillán and Hamilton AWS for the two IBO freezes.

### 5.2 Literature mining job

Goal: find papers and theses with dated stage observations (site, cultivar, year, stage definition, date, management), extract them into a table with citations, and review and deduplicate them. This is reproducible with free tools.

**Step 1. Candidate harvest (scripted, logged).** Save every query string, endpoint, date and raw response ID in a run manifest.

| Index | Query template | 2026-10-11 hits |
|---|---|---|
| OpenAlex `/works` | `filter=title_and_abstract.search:(blueberry OR Vaccinium) AND (bloom OR flowering) AND (date OR phenology)` | 153 |
| OpenAlex dissertations | `filter=type:dissertation,title_and_abstract.search:blueberry OR arandano OR mirtilo` | 985 |
| Semantic Scholar bulk | `blueberry + (phenology \| bloom \| flowering)` | 730 |
| CORE v3 | `title:"blueberry" AND (phenology OR flowering OR bloom)` | 93 |
| SciELO (browser) | `(mirtilo OR arándano OR blueberry) AND (floração OR floración OR flowering OR colheita OR cosecha OR harvest)` | 37 |
| INIA DSpace API | `arándano floración`; `arándano fenología`; `arándano heladas` | 180; 64; 130 |
| ALICIA VuFind | `arándano cosecha`; `arándano poda`; `arándano floración` | 53; 6; 3 |
| J-STAGE API | `ブルーベリー 開花` | 168 |
| Embrapa Alice and Infoteca | OAI-PMH `ListRecords`, keep records whose title or subject contains mirtilo | not counted (search 403) |
| Manual | CNKI (蓝莓 物候期, 蓝莓 花期 采收期), AGRIS, Acta Horticulturae, Redalyc | manual |

Add language variants: Spanish (arándano, floración, brotación, cosecha, poda, cianamida), Portuguese (mirtilo, floração, brotação, colheita, poda), Chinese (蓝莓, 物候期, 花期, 成熟期), Japanese (ブルーベリー, 開花, 収穫), Polish (borówka wysoka, kwitnienie), German (Kulturheidelbeere, Blüte, Ernte).

**Step 2. Normalise and deduplicate the metadata.** Use DOI as the key, then OpenAlex ID, then a normalised title (lowercase, no accents, no punctuation) plus year plus the first author's surname. Link versions: a thesis and the journal paper from the same thesis share author and site. Keep both but mark `derived_from`. Repository mirrors (CORE, BASE, LA Referencia) collapse to one work.

**Step 3. Screen.** The first pass is title and abstract with an LLM classifier (offline, as in the IBO design rules). Label: `has_dated_stage`, `has_cultivar`, `has_site`, `has_year`. The LLM proposes; two people decide on a random 20% sample and on all positive cases. My test shows why screening matters: OpenAlex's top-cited hits for "blueberry phenology" were Drosophila and bee ecology papers.

**Step 4. Rights gate.** Look up each DOI in Unpaywall (`is_oa`, licence, `best_oa_location`). Store full text only when it is OA with a licence that allows storage. Otherwise store metadata, page locator and a short excerpt under 200 characters.

**Step 5. Extraction.** Use layout-aware PDF parsing, keeping tables and figure captions. The LLM fills the stage observation table below. Every value carries `page`, `table_or_figure` and `quote`. Values read from figures get `approximate=true`.

| Field | Example and rule |
|---|---|
| `obs_id` | hash(work_id, site, cultivar, season, stage, threshold) |
| `work_id`, `doi`, `citation_locator` | DOI, page, table or figure |
| `site_name_as_written`, `lat`, `lon`, `elevation_m`, `geocode_method` | coordinates as stated, else geocoded with `geocode_method=town_centroid` |
| `country`, `admin1` | ISO codes |
| `species_type`, `cultivar` | SHB, NHB, RE, lowbush, half-high; cultivar as written plus normalised ID from the cultivar table |
| `plant_age_years`, `system` | evergreen, deciduous, managed cycle; tunnel, open field, substrate |
| `management` | pruning date, defoliation, hydrogen cyanamide date and rate, frost protection, irrigation |
| `season_label`, `crop_year` | keep the original label; derive the crop year using the IBO rule (season starting year) |
| `stage_name_as_written`, `stage_code` | for example "plena floración" → `bloom_50`; BBCH code if given (Wichura 2024 scale) |
| `stage_threshold` | first, 5%, 10%, 50%, 90%, end, as defined by the author |
| `date` or `doy`, `date_precision` | day, week or month |
| `n_plants`, `sampling_interval_days` | as stated |
| `weather_source` | on-site station, nearest station, none |
| `evidence_type` | peer_reviewed_trial, thesis, extension_bulletin, conference_abstract |
| `review_status`, `reviewer`, `conflicts` | as in the IBO records |

**Step 6. Review and deduplicate observations.** One person checks each record against the quoted source. A second person checks 20% plus all outliers (dates more than 30 days from the regional median). Duplicate observations are those with the same site, cultivar, season, stage and threshold from linked works. Keep one record and add citations, as IBO does with repeated editions. Conflicting values stay as separate records flagged `conflict`.

**Step 7. Use.** Feed the table into report 04's `phenology_truth.py` loader idea. Hold out whole sites, not random rows, for validation.

Throughput estimate [inference]: 1,000 to 1,500 unique candidates. After screening, 100 to 200 works with usable dated stages. About 8 builder days plus reviewer time.

### 5.3 Cultivar trait table design

One row per cultivar, with an evidence table under it, because a value can come from several sources.

`cultivar` (one row per cultivar)

| Column | Type | Notes |
|---|---|---|
| `cultivar_id` | text | stable slug |
| `denomination`, `trade_names[]`, `synonyms[]` | text | denomination from PBR, PLUTO or patent |
| `species_type` | enum | SHB, NHB, RE, half-high, lowbush, other |
| `ploidy` | int | if stated |
| `breeder_program`, `country_of_selection`, `selection_site`, `release_year` | text, int | Register and patent |
| `protection_ids[]` | text | USPP, PBR (AU, CA), CPVO |
| `chill_class` | enum | none, very_low (<150 h), low (150-400 h), medium (400-800 h), high (>800 h). Thresholds are a proposal [inference] |
| `chill_req_low_h`, `chill_req_high_h` | int | as stated |
| `chill_definition` | text | threshold and model (for example "<7 C hours", "0-7.2 C", "Utah"), as written |
| `evergreen_capable` | bool | Register and patent wording ("retains leaves during winter") |
| `upov_bloom_note` | 1-9 | TG/137 characteristic 34 |
| `upov_ripening_note` | 1-9 | TG/137 characteristic 36 |
| `relative_ripening_days`, `reference_cultivar` | int, text | for example -10 days versus Emerald |
| `fdp_days` | int | flowering to ripening, if stated |
| `adoption_regions[]` | text | regions with stated planting (IBO, Register "selected in Peru") |

`cultivar_evidence` (one row per value per source)

| Column | Notes |
|---|---|
| `cultivar_id`, `field_name`, `value`, `unit` | |
| `source_id`, `locator`, `quote` | quote of 200 characters or fewer |
| `test_location`, `test_years` | for example Interlachen, FL |
| `evidence_type` | breeder_claim, independent_trial, test_guideline_example |
| `review_status` | |

Model use: cultivar classes map to `chill_class` × `species_type` × `evergreen_capable`. Each class gets its own chill and GDD targets, fitted from GL-01 and GL-03 observations that name a cultivar.

## 6. How each source maps to model checks

| Gap or risk family | Sources | How |
|---|---|---|
| Cool climates (Cherryfield, Lac-Saint-Jean, Naantali, Yakima, Lynden) | USA-NPN, iNaturalist, FMI, ECCC, AgWeatherNet | Compare modelled budbreak and bloom start with NPN onset intervals near Cherryfield (19 plants) and the iNat flowering day-of-year distribution. Use FMI and ECCC hours to check whether the 100 chill-hour trigger misfires because of grid warmth. |
| Chill shortfall and Penguin's 58 chill hours | SILO, GHCNh (Burnie Round Hill 12.4 km), ERA5-Land time series | Recompute chill hours from station and 0.1 degree data. If both exceed the MERRA-2 value, the sea-dominated cell is the cause. |
| Missing IBO freezes (Chile Nov 2022, Waikato Oct 2022) | GHCNh (Linares 0.7 km, Chillán 0.8 km, Hamilton AWS 8.5 km), DMC, CR2 Explorador, NIWA CliDB, ERA5-Land | Check station minima on the reported nights against grid Tmin. Score a hit if station Tmin ≤ 0 C while the grid is above 0 C. |
| bud_flower_freeze and fruit_frost in the Southeast | IEM ASOS, GHCNh, PRISM 800 m, HRRR | Count frost nights at Alma, Homerville and Waldo stations against the grid; quantify missed-frost rates before any bias fix. |
| Harvest rain and disease | MSWEP hourly, gridMET RH | Count wet hours in modelled harvest windows and check RH-based disease days against a gauge-corrected product. |
| Coastal Peru flowering to harvest | ALICIA theses, Nuevo Chao S2 study, Register (Peru-selected cultivars), GL-03 | Extract pruning, flowering and first-harvest dates from theses. Compare the observed duration with the model's 41 to 51 days. |
| Pelotas rabbiteye harvest too early; Brazil frost | Embrapa Alice and Infoteca (OAI), SciELO, BR-DWGD | Literature stage dates per cultivar against modelled harvest start; BR-DWGD Tmin against MERRA-2 for frost and chill. |
| NHB bloom late in Europe | E-OBS, PEP725, DWD, EuroCrops parcels | Compare forcing sums from E-OBS with POWER at Lublin and Vechta. Use DWD red currant and gooseberry bloom as a local spring-anomaly proxy (weak) [inference]. |
| Management (tunnels, evergreen) | Junta Huelva, Global-PCG-10, Tong 2024 | Add a `protection_share` warning to pins in municipalities or cells with high plastic share. |
| No cultivar classes | Register, patents, UPOV TG/137, PLUTO, PBR | GL-02 table → class parameters. |
| Location mapping | CDL 242, EuroCrops, Quick Stats | Report "blueberry mapped within the cell" and weight validation toward producing cells. |
| Satellite stage proxy | MSLSP30NA, HLS | Correlate 30 m greenup with NPN onsets on CDL blueberry pixels. Adopt only if the error is under the model's present bloom error [inference]. |

## 7. Access, licensing and language risks

- **Non-commercial licences**: MSWX (CC BY-NC 4.0), MSWEP (non-commercial form), E-OBS ("non-commercial research and education"), HadISD (Non-Commercial Government Licence), NIWA (fees for commercial use), iNaturalist GBIF export (CC BY-NC 4.0), and Register Lists 52 and 53 (CC BY-NC 4.0). The app is university research today. Any commercial use would need a licence review.
- **Share-alike**: EuroCrops is CC BY-SA 4.0. Any derived blueberry mask must carry the same licence.
- **No redistribution**: PEP725 (per the R package vignette) and PLUTO (no download; reproduction needs UPOV permission). Store derived facts with citations, not raw records.
- **Registration**: CDS (ERA5-Land, CERRA), NASA Earthdata (HLS, MODIS, MSLSP), OpenAlex key (free, USD 1 per day budget), PLUTO (WIPO account), NIWA DataHub, PEP725, CR2MET form. Per the shared brief, a human must create these accounts.
- **Bot walls and outages**: GBIF and iNaturalist websites, SciELO, AGRIS, BASE, RENATI, Acta Horticulturae, MDPI and Taylor & Francis returned bot checks. GRIN returned 502. Use the documented APIs (GBIF, iNaturalist, CORE, OpenAlex, DSpace REST, VuFind, OAI-PMH), not scraping.
- **Paid**: CNKI and Acta Horticulturae full text. Use UF library access manually.
- **Languages**: Spanish (INIA, ALICIA, DMC, CR2, Junta), Portuguese (Embrapa, BR-DWGD), Chinese (CNKI), Japanese (J-STAGE, JMA) and Dutch (BRP). Translation affects stage terms. Map "plena floración", "floração plena" and "盛花期" to `bloom_50` only when the author defines the threshold.
- **Breeder claims**: patent and Register chill values are not independent trials and use different thresholds. Keep `evidence_type=breeder_claim`.

## 8. Gaps: what I looked for and could not find

- No open, dated phenology network covers commercial blueberry in Florida, Georgia, Peru, Chile, Mexico, Morocco, Spain, Australia or China. NPN has 2 highbush plants in Florida. iNaturalist has 0 or 1 Vaccinium observation near Chillán, Moguer, Lublin and Coffs Harbour.
- DWD and JMA have no Vaccinium series. PEP725 Vaccinium content could not be verified without a login. CPON's homepage was unreachable.
- GRIN-Global descriptors for Vaccinium (bloom date, ripening date, chill) could not be read because the site was down (502).
- No total count of US blueberry plant patents: the Google Patents count endpoint failed and PatentsView is migrating.
- No published satellite or tunnel map specific to blueberry for Huelva, Peru, Chile or China. The Huelva and global maps cover all crops under plastic. The only Peru blueberry satellite study is a short conference paper (403).
- No satellite method shown to detect blueberry bloom. Published stage detection uses drones on wild lowbush fields.
- EuroCrops has no blueberry mapping for Germany, Poland or Austria. Spain 2023 regional coverage was not checked.
- LA Referencia returned zero results for every query. RENATI search URLs returned 404. Embrapa search returned 403, though OAI-PMH works.
- Station periods of record in the GHCNh list were not checked, so "station within 25 km" does not yet mean "hourly data for 2010-2025".

## 9. Ranked top 10 actions

1. **GL-04 first slice**: pull GHCNh hourly data for Linares, Chillán and Hamilton AWS for October and November 2022 to test the two missing IBO freezes (0.5 day).
2. **GL-01**: ingest USA-NPN summarized data and iNaturalist annotations for the four taxa. Build onset intervals near Cherryfield, Hammonton and New England to calibrate cool-climate settings (2.5 days).
3. **GL-02**: build the cultivar table from Register Lists 43 to 53 and the UPOV TG/137 scale, then add chill hours and ripening offsets from US plant patents for cultivars planted in Peru, Mexico and Morocco (6 days).
4. **GL-04 full**: build a station truth table for the 39 sites with a GHCNh station within 25 km. Report Tmin bias and frost hit and miss rates by month (4 days).
5. **GL-03 pilot**: run the literature pipeline on INIA (180 floración hits), ALICIA (53 cosecha, 6 poda) and SciELO (37) to get Chile and Peru stage dates and pruning-to-harvest durations (3 days of the 8).
6. **ERA5-Land time series**: have an owner accept the CDS licence. Pull hourly 2 m temperature and dewpoint for the 53 benchmark cells and compare chill and frost hours with MERRA-2 (1.5 days).
7. **GL-07**: add a protection-share warning from the Junta Huelva municipal table and Global-PCG-10 (2 days).
8. **GL-06**: build a blueberry mask from CDL class 242 (multi-year persistence) and EuroCrops Spain and Portugal parcels. Show "mapped blueberry nearby" in the pin result (3 days).
9. **Recheck PRISM terms**: if 800 m daily data are free, add them as the US Tmin reference for Florida and Georgia frost checks (0.5 day).
10. **GL-09**: extract dated frost and heat events from DMC's annual extreme-events bulletins and INIA frost bulletins into event records linked to IBO events (3 days).
