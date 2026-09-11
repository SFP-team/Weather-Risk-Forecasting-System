# Soil lookup for the blueberry analogue

NASA POWER already gives a climate at a lat/lon. This note is the soil half of that point query: what to fetch, what it may not say, how to show it to a breeder, and when to skip it.

**Job of this layer.** Describe the *native* mineral soil under a coordinate so a person can decide whether ground culture is cheap, expensive, or the wrong system. It does not grade a farm. It does not predict Phytophthora. It does not replace a soil test.

**ISRIC's own farm-scale limit** (do not bury this): SoilGrids is a global model. Official FAQ: results are “best suited for continental or macro region analysis”; national/regional subsetting can be reasonable; **“we do not advise to use SoilGrids at the local or farm level.”** ([SoilGrids FAQ, updated 2026-02-24](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_04.html)). That is why GIS pH is a **screen**, never a Hallegatte veto.

---

## 1. SoilGrids 2.0 — what it is

Primary product page: [isric.org/explore/soilgrids](https://isric.org/explore/soilgrids). Docs: [docs.isric.org/globaldata/soilgrids](https://docs.isric.org/globaldata/soilgrids/).

| Fact | Official value |
|---|---|
| Product | SoilGrids 2.0 global digital soil maps |
| Resolution | **250 m** (native). Mean-only aggregates at **1000 m** and **5000 m** on WebDAV (`data_aggregated/`) |
| Depths | GlobalSoilMap intervals: **0–5, 5–15, 15–30, 30–60, 60–100, 100–200 cm** |
| How depths are predicted | Mid-point of each interval; treated as constant across the interval ([Poggio et al. 2021](https://doi.org/10.5194/soil-7-217-2021)) |
| Training | ~240 000 WoSIS (+ restricted) profiles; 400+ covariates; quantile random forests |
| Native CRS | Interrupted Goode Homolosine, WGS84 (`ESRI:54052`; ISRIC also uses pseudo-EPSG `152160`) |
| WMS/WCS also serve | EPSG:4326, ESRI:54009, ESRI:54012 |
| Mask | Land without built-up, water, glacier (ESA CCI 2015). Urban / water / ice pixels are nodata |
| License | **CC BY 4.0** since 2019 ([access FAQ, updated 2026-01-27](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html)) |
| Cite properties | Poggio et al., *SOIL* 7:217–240, 2021. [doi:10.5194/soil-7-217-2021](https://doi.org/10.5194/soil-7-217-2021) |
| Cite water layers | Turek et al., *ISWCR* 11(2):225–239, 2023. [doi:10.1016/j.iswcr.2022.08.001](https://doi.org/10.1016/j.iswcr.2022.08.001) |
| Contact | soilgrids@isric.org |

Mapped values are **integers**. Divide by the conversion factor to get conventional units ([layers FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html)):

| Code | Property | Mapped units | ÷ | Conventional |
|---|---|---|---:|---|
| `phh2o` | pH in water | pH × 10 | 10 | pH |
| `soc` | Organic carbon (fine earth) | dg/kg | 10 | **g/kg** |
| `sand` / `silt` / `clay` | Texture (fine earth) | g/kg | 10 | **%** (g/100 g) |
| `cfvo` | Coarse fragments >2 mm | cm³/dm³ | 10 | **vol %** |
| `bdod` | Bulk density (fine earth, oven-dry) | cg/cm³ | 100 | **kg/dm³** |
| `cec` | CEC (pH 7) | mmol(c)/kg | 10 | cmol(c)/kg |
| `nitrogen` | Total N | cg/kg | 100 | g/kg |
| `wv0010` | θ at **10 kPa** (100 cm) | 10⁻³ cm³ cm⁻³ | 10 | vol % |
| `wv0033` | θ at **33 kPa** (330 cm) | 10⁻³ cm³ cm⁻³ | 10 | vol % |
| `wv1500` | θ at **1500 kPa** (15 000 cm) | 10⁻³ cm³ cm⁻³ | 10 | vol % |
| `ocd` / `ocs` | C density / 0–30 cm stock | — | 10 | kg/m³ / kg/m² |

`ocs` is **0–30 cm only**. Texture fractions were modelled as compositional data (sum to 100%).

WRB class layers on WebDAV (`wrb/`, EPSG:4326) are a **separate, older** product. Do not treat “MostProbable WRB” as a SoilGrids 2.0 property or as a drainage class.

### Uncertainty (use it; do not hide the mean)

For every property × depth, SoilGrids stores:

- `mean`, `Q0.5` (median)
- `Q0.05`, `Q0.95` — bounds of a **90% prediction interval** (GlobalSoilMap PI90)
- `uncertainty` on soilgrids.org = **(Q0.95 − Q0.05) / Q0.50** (PIR)

Poggio et al. 2021, global cross-validation (their Table 4; mean prediction):

| Property | RMSE (mean) | MEC (mean) | Notes |
|---|---:|---:|---|
| pH water | **0.77** | 0.68 | A 250 m pH of 5.2 is compatible with a lab 4.4 or 6.0 |
| SOC | 36.5 g/kg | 0.47 | Weak. Do not convert to “% OM” and treat as a lab test |
| BDOD | 0.19 kg/dm³ | 0.74 | Best of the chemical/physical set |
| CFVO | 12.7 vol % | 0.31 | Worst. Coarse fragments are barely predicted |
| Clay / silt / sand | 0.13 / 0.13 / 0.18 | 0.43 / 0.62 / 0.54 | Texture RMSE is reported on the modelled fraction scale (~13–18 percentage points if read as mass fraction). Clay is the weakest texture |
| CEC | 10.7 | 0.43 | |

PICP for the 90% interval is near 0.90 for pH (well calibrated). Coarse fragments over-wide (~0.95). Sand under-covers (~0.78–0.80). **MEC falls with depth.** Prefer 0–30 cm for blueberry.

Turek et al. water-retention 10-fold CV (vol. fraction): RMSE 0.064 / 0.071 / 0.065 and MEC 0.43 / 0.39 / 0.47 at 100 / 330 / 15 000 cm. Those layers mix measured SWR with a random-forest PTF fill — more uncertain than pH.

**Practical rule:** always store and display `Q0.05` and `Q0.95` for pH. If that interval straddles the UF 4.5–5.5 band, print “pH uncertain — do not rank on soil.”

---

## 2. Access in 2026 — do not build on REST

Checked 2026-09-11 from this environment, against pages last updated Dec 2025 – Feb 2026.

| Channel | Status | Use for this tool? |
|---|---|---|
| **REST** `https://rest.isric.org/soilgrids/v2.0/properties/query` | **Paused / unusable for production.** ISRIC: “temporarily pause the service… no estimated timeline” ([isric.org/explore/soilgrids](https://isric.org/explore/soilgrids), [access FAQ](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html), LinkedIn 2025-12-17). Endpoint can still return HTTP 200 JSON with **`mean: null`**. Official fair-use if it returns: **5 calls / minute**, beta, no uptime guarantee | **No.** Current `fetch_soilgrids()` in `climate/fetch.py` hits this URL. Treat as dead |
| **WCS 2.0.1** `https://maps.isric.org/mapserv?map=/map/{property}.map` | Live (GetCapabilities 200). Official “best way to obtain a subset… input to other modelling pipelines.” Per-property MapServer. Coverage ids like `phh2o_0-5cm_mean`, `phh2o_0-5cm_Q0.05`. `FORMAT=GEOTIFF_INT16`. Subset in Homolosine or request `OUTPUTCRS=EPSG:4326` | **Yes — AOI tiles / shortlist boxes** |
| **WebDAV** `https://files.isric.org/soilgrids/latest/data/{prop}/{prop}_{depth}_{stat}.vrt` | Live. GDAL `/vsicurl` range reads. ~5 GB per map; ~120 GB per property (6 depths × 4 quantiles). Aggregates: `.../data_aggregated/1000m/` and `5000m/` | **Yes — default point extract** |
| **WMS** | Visualisation only | Maps, not the engine |
| **soilgrids.org** | Browse + screenshot | Attribution; not an API |
| **GEE community** | Same rasters | Optional batch path, extra dependency |

ISRIC’s own production advice: if you need more than a one-off query, use **WebDAV or WCS**, not REST.

Anonymous WebDAV: user/password `anonymous`. GDAL URL pattern from the [Python WebDAV tutorial](https://docs.isric.org/globaldata/soilgrids/webdav_from_Python.html):

```
/vsicurl?max_retry=3&retry_delay=1&list_dir=no&url=https://files.isric.org/soilgrids/latest/data/phh2o/phh2o_0-5cm_mean.vrt
```

WCS example ([WCS docs](https://docs.isric.org/globaldata/soilgrids/wcs.html)):

```
https://maps.isric.org/mapserv?map=/map/phh2o.map
  &SERVICE=WCS&VERSION=2.0.1&REQUEST=GetCoverage
  &COVERAGEID=phh2o_0-5cm_Q0.5
  &FORMAT=GEOTIFF_INT16
  &SUBSET=X(...),SUBSET=Y(...)
  &SUBSETTINGCRS=http://www.opengis.net/def/crs/EPSG/0/152160
```

---

## 3. Which properties matter for southern highbush

Blueberry roots are shallow, hairless, and (in Florida bark systems) stay in the bed. UF: roots consistently only in the **top 14 inches / 35 cm** ([HS1525](https://ask.ifas.ufl.edu/publication/HS1525)). Fetch **0–5, 5–15, 15–30 cm**; keep 30–60 cm as a drainage/texture contrast. Do not score 100–200 cm.

| Property | Why it matters | How to use | Do not |
|---|---|---|---|
| **`phh2o`** | Fe/Zn lockup above the UF band; Al / Mn issues if very low. Official commercial target **4.5–5.5** ([HS1356](https://ask.ifas.ufl.edu/publication/HS1356), [HS1525](https://ask.ifas.ufl.edu/publication/HS1525)) | Depth-weighted 0–30 cm mean + PI90. **Screen** | Veto a site. Treat 250 m pH as a lab |
| **`sand` / `silt` / `clay`** | Texture is the only global proxy for how a *native* profile holds water. FL SHB often sits on sand that “does not retain water and nutrients” (HS1525) | USDA triangle label; flag clayey vs sandy as *investigation* | Invent a clay % kill threshold |
| **`soc`** | UF: SHB “not recommended for soils with less than **3% organic matter** unless additional organic matter is added” ([CIR1192/MG359](https://ask.ifas.ufl.edu/publication/MG359)) | Convert to a **labelled** OM estimate (below) | Call it a soil-test OM |
| **`cfvo`** | Stones change water and rooting. MEC 0.31 | Show if high; low trust | Gate on it |
| **`bdod`** | Compaction / pore space proxy. Best SoilGrids metric | Show kg/dm³; high BD + high clay → “check structure” | Invent a BD veto |
| **`wv0010` / `wv0033` / `wv1500`** | θ at 10 / 33 / 1500 kPa. USDA-style AWC ≈ θ(33 kPa) − θ(1500 kPa); sands sometimes use 10 kPa as the wet end ([Turek et al. 2023](https://doi.org/10.1016/j.iswcr.2022.08.001); Soil Survey Staff 2014) | Show AWC_33 and AWC_10 as **native-soil** mm/m. Pine-bark beds ignore this | Use as irrigation scheduling |
| **`cec`** | Buffers pH change (sulfur rate). No UF blueberry CEC target | Show only | Gate |

**SOC → “% organic matter” (convention, not UF).** SoilGrids `soc` is **g/kg C**, not % OM.

```
soc_pct_c = soc_g_kg / 10
om_pct_van_bemmelen = soc_pct_c * 1.724    # conventional factor
om_pct_pribyl = soc_pct_c * 2.0            # Pribyl 2010 alternative
```

3% OM ≈ **17.4 g/kg SOC** at 1.724, or **15 g/kg** at 2.0. Print the factor. Never say “SoilGrids OM is 1.1%.”

**Depth weight (0–30 cm),** interval mid-points 2.5 / 10 / 22.5 cm, thicknesses 5 / 10 / 15 cm:

```
x_0_30 = (5*x_0_5 + 10*x_5_15 + 15*x_15_30) / 30
```

That is a **provisional** aggregation for a shallow-rooted crop. It is not a SoilGrids product.

---

## 4. What SoilGrids cannot tell you

Print this block whenever `management` is ground or pine-bark. Do not imply the model “checked drainage.”

| Missing | Why it matters for SHB | Official hook |
|---|---|---|
| **Drainage class** | Saturated root zone → *P. cinnamomi* zoospores. UF: well-drained profile of **at least 18 inches**; plant on raised beds if water is within 18 inches of the surface for prolonged rainy-season periods ([CIR1192](https://ask.ifas.ufl.edu/publication/MG359)) | SoilGrids has no drainage class, hydrologic group, or ponding duration |
| **Water table** | Bed height “will vary by the water table level” ([PP374](https://ask.ifas.ufl.edu/publication/PP374)) | Covariates included a *global* water-table layer; the **output maps do not report depth-to-water** |
| **Phytophthora risk** | PRR is “the most common and destructive root rot” of Florida SHB. Favoured by saturation + warmth. Pathogen is widespread; disease needs host × water. Some cultivars less *likely*; **none immune**. Rabbiteye less susceptible than SHB ([PP374](https://ask.ifas.ufl.edu/publication/PP374), [HS1156/HS380](https://ask.ifas.ufl.edu/publication/HS380)) | No pathogen map. Clay + low AWC ≠ inoculum |
| **Amended pine-bark beds** | Most FL farms are **not** native-soil culture. 100% milled pine bark **or** ~**50:50** bark:soil raised beds; top up every 2–3 years. Typical FL beds **30–32 in wide × 18–22 in deep**. Older/home: **6–8 in** bark on the soil ([HS1525](https://ask.ifas.ufl.edu/publication/HS1525), [CIR1192](https://ask.ifas.ufl.edu/publication/MG359), Williamson & Lyrene BMP 2010) | 250 m pixel is the *native* profile before (or beside) the bed |
| **Irrigation water quality** | Deep FL wells “often [have] a pH in excess of **7.0**,” which “can rapidly increase soil and bark pH.” Growers inject sulfuric acid to hold **4.5–5.5**. High Ca vs Mg. Salt: blueberries “very sensitive”; HS1525: EC should **not exceed 2 dS/m** in mature plants. Coastal wells: test for intrusion ([HS1432](https://ask.ifas.ufl.edu/publication/HS1432), [HS1525](https://ask.ifas.ufl.edu/publication/HS1525), [CIR1192](https://ask.ifas.ufl.edu/publication/MG359), [HS1356](https://ask.ifas.ufl.edu/publication/HS1356)) | No water-chemistry layer |

Also not in SoilGrids: salinity/ESP, carbonates, aluminum saturation, chloride, bicarbonate, series name, hydric rating, flooding, slope class (use DEM), or whether the pixel is already a blueberry bed.

**Allowed proxies (always labelled provisional):** high clay + high `wv1500` + low sand → “native profile may drain slowly — walk the site after rain.” US-only: SSURGO drainage class (below). Never output `phytophthora_risk_pct`.

---

## 5. UF soil recommendations — and GIS pH as a screen

Use **commercial** UF numbers as the printed target. The garden guide is slightly wider; do not silently switch.

| Item | Official number | Source |
|---|---|---|
| Target pH (commercial SHB) | **4.5–5.5** | [HS1356](https://ask.ifas.ufl.edu/publication/HS1356), [HS1525](https://ask.ifas.ufl.edu/publication/HS1525), [HS1432](https://ask.ifas.ufl.edu/publication/HS1432) |
| Target pH (home garden) | 4.0–5.5 | [CIR1192/MG359](https://ask.ifas.ufl.edu/publication/MG359) |
| Organic matter | SHB: do not plant on **<3% OM** unless you add OM and mulch. Rabbiteye: often OK at 1% if mulched; better at 2–3% | CIR1192 |
| Native FL soils | Usually **low OM** and **pH above** the blueberry range; sands hold water/nutrients poorly | HS1356, HS1525 |
| Amendment | **100% milled pine bark** beds **or** bark incorporated ~**50:50** v/v. Refresh every **2–3 years**. Coir is an alternative in containers/field | HS1525 |
| Bed geometry | Wide enough for roots; tall enough to drain. Typical **30–32 × 18–22 in**. Machine harvest may differ | HS1525 |
| Pre-plant pH | Elemental **sulfur ahead of planting** (microbes, not instant). Ammonium-N acidifies in-season. Acid-inject high-pH well water | HS1525, HS1356 |
| N on new bark | Fresh bark immobilises ammonium. Apply N **≥3 months before planting** or raise N when bark is added | HS1356 |
| Drainage / PRR | 18 in drained; raised beds + ditching where the water table is high. Avoid ponding at row ends. Start with clean plants | CIR1192, PP374 |
| Water | Frequent, small events. Upper 8–10 in of bark-amended sand may hold ~**1 in** at field capacity. Test well pH/alkalinity/salinity | HS1432, CIR1192 |
| Salt | Sensitive; HS1525 cites **EC ≤ 2 dS/m** (mature) | HS1525 |
| Soil test | Before planting (pH, OM, nutrients, salinity). Same lab each year. UF/IFAS Soil Testing Lab | HS1356 |

Florida’s industry exists *because* native GIS soils fail the table and growers rebuild the root zone. A SoilGrids pH of 6.4 in Polk County is the **normal** starting point, not a reason to drop the coordinate.

### Screen, not veto (engine rule)

Today `hallegatte_gates` **fails** `soil_ph` unless `4.2 <= pH <= 5.8` (`engine.py`). That band is already **provisional** (wider than UF 4.5–5.5) and is used as a **veto**. Change it.

| Band | Meaning | Pass/fail |
|---|---|---|
| 4.5–5.5 | In the UF commercial target (mean 0–30 cm) | `screen=in_range` — **never a hard fail** |
| PI90 overlaps 4.5–5.5 | Mean may be outside; interval is not | `screen=uncertain` |
| 4.0–4.5 or 5.5–6.5 (**provisional**) | Amendable on many sands (S, bark, ammonium-N, acid water) | `screen=amendable` + cost note |
| <4.0 or >6.5 (**provisional**) | High-effort chemistry or wrong system | `screen=high_effort` + “consider pine_bark or substrate” |
| nodata / REST-null | No soil | `screen=missing` — skip the soil gate |

`passed` on a Hallegatte `soil_ph` gate should stay **true** whenever soil was fetched or skipped. The screen goes on the land card and in `warnings[]`, not in the kill list.

`ProductionSystem.soil_ph_weight` already drops to **0** on substrate and **0.35** on pine_bark. Keep that for *similarity distance* if you must use pH at all. Do not multiply a failed gate by that weight.

---

## 6. Alternative / better soil sources

SoilGrids stays the **global default**. Overlay where a national survey actually knows drainage.

### United States — use SSURGO via Soil Data Access (not a gNATSGO download)

[gNATSGO](https://www.nrcs.usda.gov/resources/data-and-reports/gridded-national-soil-survey-geographic-database-gnatsgo) is NRCS’s seamless **SSURGO + STATSGO2 + RSS** stack: 10 m (state) / 30 m (CONUS+territories) map-unit raster + the SSURGO tables. Annual refresh. US government work / treated as public domain (GEE catalog: CC0). **Do not download the national GeoPackage** for a point API.

For one lat/lon, query **[Soil Data Access](https://sdmdataaccess.nrcs.usda.gov/)** (`SDA_Get_Mukey_from_intersection_with_WktWgs84`, WKT `point(lon lat)`). From the dominant component:

- `drainagecl`, `hydgrp`, `hydricrating`
- water table / flooding (component + `comonth` where populated)
- 0–30 cm weighted `ph1to1h2o_r`, `om_r`, `awc_r`, sand/silt/clay
- series name + `comppct_r` (85% vs 40% matters)

**This is the only production-grade drainage class we should print**, and only inside the US survey mask. STATSGO2 fill in gNATSGO is coarse — if the source raster says STATSGO, label it.

### Brazil — SC / RS (Vacaria, São Joaquim, Campos de Cima da Serra)

No SSURGO equivalent. Do **not** invent a drainage class from SiBCS order.

| Source | What you get | Use |
|---|---|---|
| Embrapa/PronaSolos **pH 0–30 cm, 1 km** + uncertainty ([GeoInfo `bra_phmap030`](https://geoinfo.dados.embrapa.br/datasets/bra_phmap030:geonode:bra_phmap030/metadata_detail)) | National DSM pH, WGS84 | Overlay vs SoilGrids when country=BR. Still not a farm test |
| [IBGE Pedologia 1:250 000](https://www.ibge.gov.br/geociencias/informacoes-ambientais/pedologia/10871-pedologia.html) / BDIA | SiBCS map units | Class label (e.g. Latossolo Bruno) — context, not pH |
| [EPAGRI Sistema Solos](https://ciram.epagri.sc.gov.br/solos/) | Georeferenced **point** samples + metadata for SC | Nearest-profile note if within a few km; not wall-to-wall |
| Embrapa *Solos do Estado de Santa Catarina* (2004); RS reconhecimento (BRASIL 1973) | State reconnaissance. Vacaria unit ≈ **Latossolo Bruno Distrófico** — acid, clayey, low base saturation | Explains why GIS pH in the serra often *looks* blueberry-friendly; walk drainage anyway |
| PronaSolos / SGB geoportal | Mixed state services | Optional later |

Vacaria’s native pH is often in-range **and** the soils are clayey Latossolos. A green pH screen there is not a Phytophthora all-clear.

### Other globals (do not replace SoilGrids)

| Product | Why not default |
|---|---|
| OpenLandMap / SoilGrids 2017 | Older or parallel DSM; no better farm-scale pH |
| HWSD v2 | Taxonomy + two layers; no PI90 |
| iSDAsoil | Africa only |
| MERIT/HAND, TWI | Terrain wetness **proxies** — optional later, labelled provisional |

---

## 7. When to skip (pots / substrate)

If `media == substrate` (pots, bags, coir, soilless):

1. **Do not fetch** SoilGrids / SDA / Embrapa (save the round trip).
2. Set `soil.fetch_status = skipped_soilless`.
3. Do not show native pH, OM, clay, or AWC as if they were the root zone.
4. Show the pot card: media pH target **4.5–5.5** (same UF number, different volume); water quality still matters; nursery PRR if pots sit in runoff ([PP374](https://ask.ifas.ufl.edu/publication/PP374): impermeable / benches; discard flooded pots).
5. Keep climate (POWER, chill, heat, rain) — those still transfer.

`pine_bark`: **fetch native soil**, but every number is “soil *under/beside* the bed.” Weight already 0.35. Print the UF bark recipe, not a native-soil kill.

`open_soil`: full card + strongest “walk drainage” language.

---

## 8. Fetch and cache design

### What to fetch (ground / pine_bark)

**Always (SoilGrids 250 m, or 1000 m mean if 250 m extract is too slow on first build):**

- Properties: `phh2o`, `soc`, `sand`, `silt`, `clay`, `cfvo`, `bdod`, `wv0010`, `wv0033`, `wv1500`
- Depths: `0-5cm`, `5-15cm`, `15-30cm` (plus `30-60cm` optional)
- Stats: `mean`, `Q0.05`, `Q0.95` for **pH and SOC** at those depths; `mean` is enough for texture/BD/θ on v0

**Optional:** `cec` mean 0–30; WRB MostProbable as a caption only.

**Overlays:**

- Point in US survey: SDA dominant-component drainage + hydric + 0–30 pH/OM/AWC
- Point in BR: Embrapa 1 km pH 0–30 if the GeoTIFF is staged

**How (order):**

1. Cache hit → return.
2. GDAL `/vsicurl` WebDAV, Homolosine or warp-on-read to EPSG:4326, point sample (bilinear off; **nearest** 250 m cell — do not pretend sub-pixel pH).
3. If GDAL/WebDAV fails: WCS GetCoverage of a **2–4 cell** pad, then sample.
4. REST only as a last probe; if values are `null`, record `soilgrids_rest_null` and continue without pH.
5. Sleep / single-flight. Do not parallel-blast WebDAV. ISRIC asked for WCS/WebDAV instead of REST because REST could not take the load.

**Do not** download global 250 m mosaics into the repo. Stage **1000 m mean** COGs for `phh2o`/`soc`/`clay`/`sand` if you want an offline globe screen (~80 MB per layer for pH 0–5 mean). Keep 250 m + PI90 for the shortlist.

### Cache

Reuse `data/analogue/land/land_{site_id}.json`. Also key a **pixel cache** so two farms in the same 250 m cell share one extract:

```
data/analogue/land/pixels/sg_{lon0}_{lat0}.json
```

`lon0, lat0` = cell centre in Homolosine, or 0.0025° rounded WGS84 (~250 m at equator — good enough for the key, not for the extract).

Payload must include `fetched_at`, `source_url`, `product`, `license`, `crs`, raw integer + converted floats, and quantiles. TTL: **1 year** or until ISRIC `latest/` ETag changes. 1000 m aggregates are dated 2022 on WebDAV; 250 m VRT tiles show 2020 mtimes — treat “latest” as the live tree, not a year stamp (FAQ: “There is no year for SoilGrids”).

User-Agent: keep `BlueberryAnalogue/… (site-selection research; not a farm decision)`.

---

## 9. Warnings to print (copy)

Use these strings, or the same facts in fewer words.

1. **ISRIC farm-scale:** “SoilGrids is a 250 m global model. ISRIC does not advise using it at farm scale. This is a regional screen, not a soil test.”
2. **Native ≠ bed:** “Numbers are the native mineral soil. They do not see pine-bark beds, sulfur, or last year’s compost.”
3. **pH PI90:** “90% prediction interval for pH is {q05:.1f}–{q95:.1f} (global RMSE ≈ 0.8). Lab pH can sit anywhere in that span.”
4. **No drainage / water table / PRR:** “No drainage class, water table, or Phytophthora map. Walk the site after rain; ponding and row-end dams are the UF risk (PP374).”
5. **No irrigation water:** “Well pH, bicarbonates, and EC are unmeasured. Florida deep wells often exceed pH 7 and will lime a bark bed (HS1432).”
6. **OM conversion:** “Organic matter is estimated from SoilGrids SOC × {1.724|2.0}. UF’s 3% OM rule is a **lab** number.”
7. **US overlay:** “Drainage class is from SSURGO/SDA ({series}, {comppct}%), not SoilGrids.”
8. **BR overlay:** “Embrapa 1 km pH is still a map, not a trado. Latossolo Bruno can be acid and still wet.”
9. **Missing extract:** “SoilGrids REST is paused (2025–26); this point has no soil values.”
10. **Pots:** “Soilless system — native soil skipped.”

---

## 10. Output schema (one coordinate)

One object per lat/lon. Climate stays in the existing POWER payload. This is the `land.soil` object.

```json
{
  "lat": 29.6516,
  "lon": -82.3248,
  "management": "ground",
  "fetch_status": "ok",
  "skipped_reason": null,
  "native_soil_disclaimer": "SoilGrids 250 m native mineral soil. Not a farm soil test. Not the root zone if the system is pine bark or pots.",

  "soilgrids": {
    "product": "SoilGrids 2.0",
    "license": "CC-BY-4.0",
    "citation": "Poggio et al. 2021 SOIL 7:217-240; water: Turek et al. 2023 ISWCR 11:225-239",
    "access": "webdav_vsicurl",
    "resolution_m": 250,
    "crs": "ESRI:54052",
    "pixel_id": "igh:...",
    "depths_cm": ["0-5", "5-15", "15-30"],
    "fetched_at": "2026-09-11T16:00:00Z",
    "layers": {
      "phh2o": {
        "unit": "pH",
        "by_depth": {
          "0-5":  {"mean": 5.1, "q05": 4.3, "q95": 6.0},
          "5-15": {"mean": 5.2, "q05": 4.4, "q95": 6.1},
          "15-30":{"mean": 5.3, "q05": 4.5, "q95": 6.2}
        },
        "wmean_0_30": 5.24,
        "q05_0_30": 4.4,
        "q95_0_30": 6.1
      },
      "soc_g_kg": { "wmean_0_30": 12.0, "q05_0_30": 4.0, "q95_0_30": 28.0 },
      "sand_pct": { "wmean_0_30": 82.0 },
      "silt_pct": { "wmean_0_30": 10.0 },
      "clay_pct": { "wmean_0_30": 8.0 },
      "cfvo_vol_pct": { "wmean_0_30": 3.0 },
      "bdod_kg_dm3": { "wmean_0_30": 1.45 },
      "theta_10kpa_vol_pct": { "wmean_0_30": 18.0 },
      "theta_33kpa_vol_pct": { "wmean_0_30": 14.0 },
      "theta_1500kpa_vol_pct": { "wmean_0_30": 5.0 }
    },
    "derived": {
      "texture_class_usda": "loamy sand",
      "awc_33_minus_1500_vol_pct": 9.0,
      "awc_10_minus_1500_vol_pct": 13.0,
      "om_pct_from_soc": {
        "value": 2.07,
        "factor": 1.724,
        "factor_name": "van_bemmelen_conventional",
        "note": "Not a lab %OM. UF 3% OM rule is a soil-test number."
      }
    }
  },

  "overlay": {
    "us_ssurgo": null,
    "br_pronasolos_ph_0_30": null
  },

  "uf_targets": {
    "ph": { "low": 4.5, "high": 5.5, "source": "HS1356 HS1525" },
    "om_pct_min_unamended_shb": { "value": 3.0, "source": "CIR1192/MG359" },
    "drained_profile_in": { "value": 18, "source": "CIR1192/MG359" }
  },

  "screen": {
    "ph": {
      "band": "in_range",
      "rule": "uf_commercial_4.5_5.5",
      "veto": false,
      "detail": "SoilGrids 0-30 cm pH 5.2 (PI90 4.4-6.1). Screen only."
    },
    "om": {
      "band": "below_3pct_if_van_bemmelen",
      "rule": "cir1192_3pct_lab_om",
      "converted": true,
      "veto": false,
      "detail": "Converted OM ~2.1%. UF: do not plant SHB on <3% OM unless you add bark/peat."
    },
    "drainage": {
      "band": "unknown",
      "source": "none",
      "veto": false,
      "detail": "No drainage class. Walk after rain. Raised beds if water sits within 18 in."
    }
  },

  "breeder_card": {
    "headline": "Native soil looks sandy and near the pH band; still walk drainage.",
    "system_note": "Ground culture: GIS soil is a screen. Budget a soil test + sulfur/bark if the lab is off-band.",
    "checklist": [
      "Lab pH, OM, EC before any trial (UF/IFAS or local lab).",
      "After a heavy rain: standing water, row-end dams, water table.",
      "Test irrigation pH, alkalinity, EC. Acid-inject if the well limes the bed.",
      "If you will use pine bark: 100% bark or ~50:50; refresh 2-3 yr; N on fresh bark ≥3 months pre-plant."
    ]
  },

  "warnings": [
    "SoilGrids is a 250 m global model. ISRIC does not advise farm-scale use.",
    "No drainage class, water table, Phytophthora, bark bed, or well-water chemistry."
  ]
}
```

`fetch_status`: `ok` | `partial` | `missing` | `skipped_soilless` | `skipped_ocean_or_urban`.

### What a breeder sees — ground vs pots

**`management=ground` (`open_soil`)**

| Show | Hide / do not imply |
|---|---|
| pH mean + PI90 vs UF **4.5–5.5** | “Suitable soil” / plant 20 ha |
| Sand/silt/clay + USDA class | A clay kill score |
| Converted OM vs UF 3% (labelled) | “OM = 2.1%” without the factor |
| Native AWC (θ33−θ1500) as context | Irrigation schedule |
| Screen bands + checklist | Hallegatte fail on pH |
| US: SSURGO drainage class | “Phytophthora = high” |
| Warnings 1–6 | — |

**`management=pine_bark`**

Same native numbers, plus: “This is the soil *under* a bark bed. UF commercial SHB in Florida is usually bark, not this pixel.” Keep pH screen at reduced weight. Emphasise well-water pH (bark is a small buffer; HS1432).

**`management=pots` (`substrate`)**

| Show | Hide |
|---|---|
| “Native soil skipped (soilless).” | All SoilGrids property tiles |
| Media target pH **4.5–5.5** (UF), salt sensitivity, acid water | Native clay / AWC / OM |
| PP374 pot sanitation / flooding | Drainage class of the field |
| Climate analogue only | Land gate |

---

## 11. What the analogue code does today

| Current | Change |
|---|---|
| `fetch_soilgrids()` → REST, `0-5cm` **mean only**, `phh2o/soc/clay/bdod` | WebDAV/WCS; 0–30 cm; PI90; sand/silt/cfvo/θ |
| `land_live=False` on the default POWER build | Fetch land when media ≠ substrate |
| pH `/10`, clay `/10`; **bdod not `/100`**; SOC left in mapped units | Apply the official table |
| Gate `4.2–5.8` as pass/fail | Screen bands; `veto=false` |
| Substrate weight 0 | Also **skip the fetch** |

---

## 12. Citations (official)

**ISRIC / SoilGrids**

- [SoilGrids product](https://isric.org/explore/soilgrids) — CC BY 4.0; REST pause notice (live 2026-09-11).
- [SoilGrids docs](https://docs.isric.org/globaldata/soilgrids/) (REST notice updated 2025-12-18).
- [Access / license / Homolosine](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html) (2026-01-27).
- [Layers, units, depths](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html).
- [FAQ: farm-scale warning, citations, missing tiles](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_04.html) (2026-02-24).
- [WCS](https://docs.isric.org/globaldata/soilgrids/wcs.html), [WebDAV](https://docs.isric.org/globaldata/soilgrids/WebDav.html), [WebDAV Python](https://docs.isric.org/globaldata/soilgrids/webdav_from_Python.html).
- Poggio, L., de Sousa, L.M., Batjes, N.H., Heuvelink, G.B.M., Kempen, B., Ribeiro, E., Rossiter, D. 2021. SoilGrids 2.0: producing soil information for the globe with quantified spatial uncertainty. *SOIL* 7:217–240. https://doi.org/10.5194/soil-7-217-2021
- Turek, M.E., Poggio, L., Batjes, N.H., Armindo, R.A., de Jong van Lier, Q., de Sousa, L.M., Heuvelink, G.B.M. 2023. Global mapping of volumetric water retention at 100, 330 and 15 000 cm suction using the WoSIS database. *ISWCR* 11(2):225–239. https://doi.org/10.1016/j.iswcr.2022.08.001

**UF / IFAS**

- Phillips, D., Williamson, J.G. HS1356. *Nutrition and Fertilization Practices for Southern Highbush Blueberry in Florida.* https://ask.ifas.ufl.edu/publication/HS1356
- HS1525. *Establishing New Southern Highbush Blueberry Plantings in Florida.* https://ask.ifas.ufl.edu/publication/HS1525
- Williamson, J.G., Phillips, D.A. CIR1192/MG359. *Blueberry Gardener's Guide.* https://ask.ifas.ufl.edu/publication/MG359
- Flor, N.C., Phillips, D.A., Harmon, P.F. PP374. *Phytophthora Root Rot on Southern Highbush Blueberry in Florida.* https://ask.ifas.ufl.edu/publication/PP374
- HS1156/HS380. *Florida Blueberry Integrated Pest Management Guide.* https://ask.ifas.ufl.edu/publication/HS380
- HS1432. *Irrigation Practices for Southern Highbush Blueberry in Florida.* https://ask.ifas.ufl.edu/publication/HS1432
- Williamson, J.G., Lyrene, P.M., Olmstead, J.W. 2010. Best management practices… blueberry section (pine-bark culture 6–8 in). *HortTechnology* 20:111–117. https://doi.org/10.21273/HORTTECH.20.1.111

**US / Brazil overlays**

- USDA-NRCS. gNATSGO. https://www.nrcs.usda.gov/resources/data-and-reports/gridded-national-soil-survey-geographic-database-gnatsgo
- USDA-NRCS. Soil Data Access. https://sdmdataaccess.nrcs.usda.gov/
- Embrapa CNPS. Mapa de pH 0–30 cm do Brasil, 1 km (PronaSolos). https://geoinfo.dados.embrapa.br/datasets/bra_phmap030:geonode:bra_phmap030/metadata_detail
- IBGE. Pedologia 1:250 000. https://www.ibge.gov.br/geociencias/informacoes-ambientais/pedologia/10871-pedologia.html
- EPAGRI. Sistema Solos. https://ciram.epagri.sc.gov.br/solos/

**Provisional (not official thresholds)**

- pH amendable band 4.0–4.5 / 5.5–6.5 and high-effort <4.0 / >6.5
- 0–30 cm thickness weighting
- Van Bemmelen 1.724 (or Pribyl 2.0) SOC→OM
- AWC = θ33−θ1500 (or θ10−θ1500 on sands)
- “Clayey native soil → walk drainage” with no clay % cutoff
- Current engine 4.2–5.8 gate (retire as a veto)
