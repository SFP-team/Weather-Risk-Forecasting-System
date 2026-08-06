# Data sources

Weather and climate data strategy for the Florida blueberry prototype and product.

See also: [PROJECT_PROPOSAL.md](../PROJECT_PROPOSAL.md), [architecture.md](architecture.md).

---

## 1. Variable needs (blueberry ops)

| Variable | Why it matters |
|----------|----------------|
| Tmin / Tmax (ideally multi-height) | Freeze risk, chill, heat |
| RH / dew point / wet bulb | Freeze irrigation start/stop; evaporative cooling risk |
| Wind speed | Advective vs radiation freeze; irrigation efficacy |
| Precip | Disease, harvest split, water balance |
| Solar radiation | ET / irrigation proxies |
| Soil temperature | Secondary; packing / root context |
| Leaf wetness | Disease models (rarely free; often derived) |

FAWN multi-height air temperature (e.g. 0.6 m and 2 m) is especially valuable for freeze nights versus airport ASOS alone.

---

## 2. Tier 1 — must use for prototype

### 2.1 FAWN (Florida Automated Weather Network, UF/IFAS)

**Role:** Primary Florida agricultural observation network.

| Asset | URL / access |
|-------|----------------|
| Home | https://fawn.ifas.ufl.edu/ |
| Data access | https://fawn.ifas.ufl.edu/data/ |
| FTP yearly CSV | https://fawn.ifas.ufl.edu/data/fawnpub/ |
| QAQC FTP | https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/ |
| Gap-free 2005–2020 (30 stations) | https://fawn.ifas.ufl.edu/data/fawn_data_gap_free_pub/ |
| Live feeds (CSV/JSON) | https://fawn.ifas.ufl.edu/data/feeds.php |
| Cold protection tools | https://fawn.ifas.ufl.edu/tools/coldp/ |

**Variables:** 15-minute and daily; air temp multi-height, soil temp, RH, dew point, precip, wind, solar, pressure (station-dependent).

**License note:** Public research/extension data. Confirm attribution and commercial redistribution terms with UF/IFAS before product launch.

**Reference:** Peeling, J.A., et al. (2023). Gap-free 16-year (2005–2020) sub-diurnal surface meteorological observations across Florida. *Scientific Data*.

### 2.2 Priority FAWN stations (blueberry belt)

| Station | County | Role |
|---------|--------|------|
| Alachua | Alachua | North-central production core |
| Putnam Hall | Putnam | Production belt |
| Citra | Marion | PSREU + production |
| Ocklawaha | Marion | Marion density |
| Lake Alfred | Polk | Central FL / CREC |
| Sebring | Highlands | Southern production |
| Supporting | Live Oak, Hastings, Bronson, Pierson, Okahumpka, Umatilla | N–S chill/freeze gradients |

Newer Polk stations (e.g. Babson Park, Tiger Creek) help recent years only—prefer long-record stations for training.

**Density takeaway:** Typically ~1 FAWN station per major county—excellent for regional models, **not** every frost pocket. Support grower cold-spot bias and later on-farm sensors.

### 2.3 NOAA GHCN-Daily (NCEI)

**Role:** Longer denser Tmax/Tmin/precip; climatology baselines; multi-station fill.

- Free US government open data; commercial use OK.
- CDO API: free token; rate limits apply (~5 req/s, 10k/day class—verify current limits).
- Gap: many sites lack RH, solar, soil temp.

### 2.4 NWS API (`api.weather.gov`)

**Role:** Official short-range forecasts (~7 day), hourly, alerts (freeze watches/warnings), ~2.5 km grid.

- Free for product use.
- Requires proper `User-Agent`.
- Authority for freeze **warnings**; our product is decision support layered on top.

### 2.5 NOAA Climate Prediction Center (CPC)

**Role:** Monthly and 3-month temperature and precipitation **tercile probabilities** (and shorter 6–10 / 8–14 day, week 3–4 outlooks).

- Free maps / GIS products: https://www.cpc.ncep.noaa.gov/
- Use as **features and transparent UI layers**, not as farm-level daily weather.
- Hindcast archives enable seasonal risk model training.

### 2.6 NMME / seasonal ensembles

**Role:** Multi-model monthly anomalies and ensemble spread for 30–90 day risk head.

- Free via CPC/IRI/open data channels.
- Open-Meteo seasonal (e.g. SEAS5) is a convenient API path for prototypes (commercial license for production).

---

## 3. Tier 2 — nice to have / paid

| Source | Why add |
|--------|---------|
| Open-Meteo paid / self-host | Commercial license; historical + seasonal APIs |
| Visual Crossing | Cheap commercial history + forecast unified API |
| Synoptic / MesoWest commercial | Unified real-time stations including FAWN-class IDs |
| Meteomatics | Leaf wetness, high-res soil, ag parameters |
| ASOS/ISD hourly | Freeze-night wind/RH near airports (GNV, OCF, etc.) |
| OpenWeather / Weatherbit | Forecast redundancy |

### Open-Meteo free-tier caveat

Free API is generally **non-commercial**. Fine for research prototypes; **switch to paid or self-host before farmer-facing commercial launch**.

---

## 4. What NOT to rely on alone

| Alone is insufficient | Why |
|-----------------------|-----|
| CPC / NMME maps only | Coarse; probabilistic terciles—not daily farm Tmin |
| Open-Meteo free only for commercial product | License + SLA |
| GHCN Tmax/Tmin only | Missing RH, solar, canopy-height freeze physics |
| NWS 7-day only for 60–90 day product | No seasonal skill without climate layer |
| Single FAWN station as the farm | Radiation freezes vary over short distances |
| Leaf-wetness disease models without validation | FAWN does not measure leaf wetness directly |

---

## 5. Suggested daily feature / label set

### Labels (targets)

- `Tmin_2m`, `Tmin_60cm` (if FAWN), `Tmax`
- `Precip_sum`, wet-day flag
- `RH_mean` / hours RH &gt; 90%
- `Wind_mean`, `Wind_max`
- Derived: **chill hours** (and later chill portions), **frost night flags**, GDD, wet-bulb / irrigation index

### Inputs

- Lags 1–30d; rolling means/extremes; DOY harmonics for short-range
- Neighbor station deltas
- ENSO indices (ONI, Niño-3.4)
- CPC terciles / NMME anomalies + spread
- Static: lat/lon, elevation, county, distance to coast

### Model heads

1. **0–7 day** — high skill possible  
2. **8–30 day** — weekly aggregates  
3. **30–90 day** — anomaly / risk scores only  

---

## 6. End-to-end pipeline

```
HISTORICAL TRAIN
  FAWN FTP / gap-free ──► clean, daily aggregates
  GHCN-Daily ───────────► denser T/P, climatology
  Open-Meteo reanalysis ► farm-grid fill + bias-correct to FAWN
  CPC + NMME ───────────► seasonal features
  Labels: Tmin, frost, chill, precip, RH hours

LIVE INFERENCE
  FAWN feeds ──► latest obs, lag features
  NWS ─────────► 0–7d forecast features + alerts
  Optional VC/OM paid ──► multi-var forecast
  MOS/bias ML ─► calibrated Tmin & freeze P

60–90 DAY OUTLOOK
  CPC monthly + 3-mo ──► T/P tercile features
  NMME / seasonal ─────► anomaly + ensemble spread
  Map to local FAWN climatology ──► chill deficit, freeze-season severity, wet-bloom tilt
```

---

## 7. Data quality caveats

1. **Spatial sparsity** — one station ≠ farm frost pocket.  
2. **Record length** — prefer long-running stations for training.  
3. **Gaps & QC** — use QAQC and gap-free products when possible.  
4. **Real-time vs final** — GHCN revises; flag provisional data.  
5. **Height mismatch** — ASOS/NWP 2 m vs FAWN 60 cm can differ several °F on calm clear nights.  
6. **No free leaf wetness** — derive proxies or pay for ag APIs.  
7. **Climate non-stationarity** — warm winters / chill deficit trends; retrain carefully.  
8. **Product liability** — freeze decisions are high-stakes; frame as decision support.

---

## 8. “Start Monday” stack

| Layer | Choice |
|-------|--------|
| Train labels / ag variables | FAWN (Alachua, Putnam Hall, Citra, Lake Alfred, Sebring + neighbors) |
| Spatial / climate baseline | GHCN-Daily + Open-Meteo historical |
| Live short-range | NWS API + FAWN feeds |
| Optional commercial forecast API | Visual Crossing free commercial tier |
| 60–90 d features | CPC GIS + NMME anomalies |
| Later paid upgrade | Open-Meteo Pro or Meteomatics |

---

## 9. Related domain guidance (not weather APIs)

| Resource | Use |
|----------|-----|
| EDIS HS216 freeze protection | Product freeze rules and copy |
| EDIS evergreen production HS1362 | South/central system mode |
| EDIS irrigation guidance | Water balance stage demand |
| AgroClimate chill tools | Seasonal chill context patterns |
| Florida Blueberry Growers Association | Cultivars, industry practice |
