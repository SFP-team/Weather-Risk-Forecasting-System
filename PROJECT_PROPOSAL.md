# Project Proposal: Florida Blueberry Weather Risk Forecasting System

**Working product name:** Blueberry Risk Co-Pilot (brand TBD)  
**Status:** Greenfield prototype proposal  
**Audience:** Florida commercial blueberry growers (southern highbush primary; rabbiteye secondary)  
**Date:** August 2026  

---

## 1. Executive summary

Florida blueberry farmers face major production losses from abnormal weather—warm winters with insufficient chilling, late freezes after flowering or fruit set, extreme temperatures, and high humidity that drives disease. General weather forecasts predict temperature or rainfall but do not explain **agricultural significance** for blueberry production.

This project builds a **prototype machine-learning and decision-support system** that:

1. Uses historical daily weather from multiple Florida stations (primarily FAWN + NOAA).
2. Predicts **crop-relevant conditions** and **probabilities of adverse weather events**.
3. Serves a **farmer-facing dashboard** tailored to Florida blueberry operations.
4. Covers **two horizons**: operational decisions (hours–10 days) and seasonal planning (1–3 months).

**Critical framing:** A credible product does **not** claim deterministic daily weather 90 days out (scientifically unsupported). It delivers:

- **Near-term (0–10 days):** freeze protection, disease wetness, harvest weather—where skill is real.
- **Seasonal (1–3 months):** probabilistic **risk outlooks** (chill deficit, freeze-night odds in a window, wet/dry tilt) fused with NOAA Climate Prediction Center / NMME guidance and local station models.

---

## 2. Problem statement

### 2.1 Who is hurt

Florida has roughly **5,700–7,000 commercial blueberry acres**, concentrated in:

| Region | Core counties | Notes |
|--------|---------------|--------|
| Central | Polk, Lake, Orange, Pasco, Hernando, Hillsborough | Largest acreage share; deciduous + evergreen |
| North-central | Alachua, Levy, Marion, Putnam, Sumter | Highest freeze risk during bloom |
| South-central | Highlands, Hardee, DeSoto, Manatee, Sarasota | Evergreen systems; lower chill; earlier market |

Profitability depends on the **early North American fresh window** (roughly March–early May). One late freeze can wipe the high-price crop even if bushes survive.

### 2.2 Weather hazards that matter

| Hazard | Why it matters |
|--------|----------------|
| **Late freezes** (Jan–late March) | Open flowers and young fruit highly susceptible; overhead irrigation is standard protection |
| **Insufficient chill** | Southern highbush often need ~100–400 hours (roughly 32–45°F); warm winters delay/erratic bloom and reduce yield |
| **Warm mid-winter spells** | Dehardening / early bloom → longer freeze exposure |
| **Cool + wet bloom** | Botrytis blossom blight; freeze irrigation extends leaf wetness |
| **Warm + wet fruit season** | Anthracnose / ripe rot pressure |
| **Drought during fruit fill** | Shallow-rooted pine-bark beds; size and yield loss |
| **Heat at harvest** | Soft fruit, labor risk, cooling load |
| **Tropical systems** | Windthrow, flooding, fruit drop (seasonal readiness) |

### 2.3 Gaps in existing tools

| Tool | Strength | Gap |
|------|----------|-----|
| Consumer weather apps | Maps, radar, alerts | No phenology, wet-bulb freeze logic, chill vs cultivar |
| NWS | Authoritative forecasts & warnings | Not crop-stage or farm-block specific |
| FAWN / UF-IFAS | Gold-standard Florida ag stations, cold-protection toolkit, chill tools | Fragmented tools; not a unified blueberry “night plan” product |
| National ag platforms (DTN, FieldView, etc.) | Operational weather | Commodity/Midwest gravity; weak FL blueberry freeze playbook |

**Product thesis:** Build the **decision layer on top of FAWN + NWS** that speaks blueberry phenology, Florida freeze physics, and grower jobs—not another temperature map.

---

## 3. Goals and non-goals

### 3.1 Goals

1. **Prototype ML weather-risk system** for Florida blueberry production using multi-station historical observations.
2. Forecast **daily near-term conditions** and **probabilities of adverse events** for planning windows up to ~2–3 months (as risk aggregates, not fake daily calendars).
3. Deliver a **usable farmer dashboard** with plain-language actions (protect tonight, chill on track, elevated freeze-season odds).
4. Prefer **open data** (FAWN, NOAA, NWS, CPC); document commercial API needs for launch.
5. Remain honest about **forecast skill by horizon** and always compare against climatology.

### 3.2 Non-goals (v0 / MVP)

- Deterministic **daily Tmax/Tmin calendars at 60–90 days**
- Farm-level **yield prediction** or insurance pricing
- **Pesticide prescriptions** (weather risk only; link to IFAS IPM)
- Replacing **NWS freeze warnings** as official authority
- Statewide parcel-level microclimate maps without on-farm sensors
- Full farm management system (inventory, payroll, packing CRM)

---

## 4. What we can build vs what we cannot

### 4.1 Feasibility by target and horizon

| Target | 0–7 d | 8–14 d | 15–30 d | 30–60 d | 60–90 d |
|--------|:-----:|:------:|:-------:|:-------:|:-------:|
| Daily Tmax/Tmin sequence | Good | Moderate | Poor | Poor | Poor |
| Weekly mean temperature | Good | Moderate | Poor–Mod | Poor | Poor |
| Monthly mean T / anomaly | — | — | Moderate | Moderate | Moderate–Poor |
| Monthly precip anomaly | — | — | Moderate–Poor | Poor–Mod | Poor |
| P(freeze in month/season window) | Good | Moderate | Moderate | Moderate | Moderate–Poor |
| Freeze *night timing* | Good | Moderate | Poor | Poor | Poor |
| Seasonal chill accumulation | — | — | Moderate | Mod–Good | Moderate |
| Disease-pressure *windows* | Good | Moderate | Poor | Poor | Poor |

### 4.2 Credible product claims

- Seasonal **risk outlook** for 1–3 months: temperature/precip tilts, freeze odds in a window, chill range vs cultivar.
- Station-downscaled interpretation of **NOAA CPC / NMME** for Florida blueberry regions.
- **Scenario ranges** (cool/wet, average, warm/dry)—not a single deterministic path.
- Operational **1–10 day freeze and disease** decision support.

### 4.3 Claims to avoid (false advertising / liability)

- “We predict daily weather 90 days out.”
- Exact freeze dates months ahead.
- Guaranteed chill hours for a cultivar.
- “AI freezes better than NOAA” without rigorous hindcast skill scores.
- Single 90-day daily sparkline without large uncertainty and plain-language disclaimers.

---

## 5. Product concept

### 5.1 Personas and jobs-to-be-done

| Persona | Primary job |
|---------|-------------|
| **Small family farm (5–40 ac)** | “Protect or sleep tonight? Start/stop irrigation correctly.” |
| **Mid-size commercial (40–300+ ac)** | Rank blocks when pump capacity is limited; crew night plan. |
| **PCA / consultant** | Multi-farm freeze + disease weather risk in one place. |
| **Co-op / packer** | County supply risk outlook (later phase). |

### 5.2 Dual-horizon product

```
Horizon A — Operations (0–10 days)     Highest willingness-to-pay
  Freeze protect alerts, start/stop rules, disease wetness, harvest rain/heat

Horizon B — Planning (1–3 months)      Matches original research brief
  Chill deficit risk, freeze-night frequency, wet/dry season tilt, confidence bands
```

### 5.3 MVP screens (mobile-first)

1. **Tonight** — Traffic light (Low / Watch / Protect / Beyond system); dew point, wind, coldest hour; start/stop checklist; block ranking.
2. **7-Day** — Freeze icons, disease wetness, harvest rain flags.
3. **Season** — Chill progress vs cultivar target; Month+1…+3 risk cards (not daily calendars).
4. **My Farm** — Location, FAWN station, cultivars, phenology stage, cold-spot bias, alert prefs.
5. **Alerts / verification** — History with “forecast right / late / false alarm.”

### 5.4 Alert hierarchy (MVP+)

| Level | Name | When |
|-------|------|------|
| L1 Watch | Freeze possible in 48–72h | Prep irrigation |
| L2 Action | Protect likely tonight | Assign pump person |
| L3 Critical | Near start threshold or obs colder than forecast | Start/check now |
| L4 Beyond system | Wind + cold may exceed design rate | Choose which blocks to save |
| Disease | Cool wet / post-protect wetness | Scout + spray-window weather |
| Harvest | Rain/heat/wind for crews | Labor plan |

SMS/email for freeze season is a **must-have for pilot adoption**; dashboard explains the alert.

### 5.5 Uncertainty for non-meteorologists

- Traffic lights for **action**, not raw meteorology.
- “7 in 10 nights like this, cold pockets hit 30°F” instead of bare probabilities.
- Every card: **Weather fact → Crop meaning → Suggested action**.
- Explicit humility where southern highbush critical temps by stage are less settled than northern highbush tables.

### 5.6 Differentiation

*The only mobile-first weather risk product that converts FAWN + forecast into blueberry-stage actions for Florida freezes, wetness disease risk, and harvest logistics—in plain grower language, with SMS that wakes crews for pump decisions.*

---

## 6. Adverse weather event catalog

Events are **actionable** (threshold + phenology + confidence), not generic “bad weather.”

| Event ID | Definition (suggested) | Grower care |
|----------|------------------------|-------------|
| `FREEZE_PROTECT` | Overnight min ≤32°F (radiation) or stage rules with wind; wet-bulb trajectory critical | Start diesel, labor, valves |
| `FREEZE_KILL_RISK` | Stage-adjusted critical temp breached (open flower/fruit often ~26–28°F tissue guidance) | Loss expectation |
| `ADVECTIVE_FREEZE` | Freeze + sustained wind above system design (~8–10 mph class) | Do not assume full irrigation save |
| `POST_FREEZE_DISEASE` | Freeze protection irrigation or freeze + wet hours during bloom | Botrytis follow-up |
| `BOTRYTIS_BLOOM` | Bloom + wetness/rain + ~55–75°F extended periods | Fungicide timing (weather risk) |
| `ANTHRACNOSE_RISK` | Wetness duration × temperature risk from bloom to harvest | Spray interval compression |
| `RAIN_SPLIT_HARVEST` | Ripe fruit + heavy short rain | Accelerate harvest |
| `DROUGHT_STRESS` | Water balance deficit vs stage demand | Increase drip frequency |
| `HEAT_HARVEST` | Multi-day max ≥90–95°F during pick | Labor safety, cooling |
| `CHILL_SHORTFALL` | Season-to-date chill vs cultivar trajectory | Yield/management outlook |
| `WARM_SPELL_DEHARDEN` | Multi-day mid-winter warmth advancing buds | Earlier freeze vigilance |
| `TROPICAL_SYSTEM` | Named storm impacts | Pre-storm harvest, drainage |

**Stage-gating is mandatory:** 30°F is a non-event for dormant buds and an emergency at open bloom.

### Approximate operational freeze guidance (product rules; agronomist review required)

- Chill hours model: often hours between ~32°F and 45°F; Dynamic Model preferred later for warm-spell cancellation.
- Protect guidance often near **30°F** shelter / open-sky thermometers; very low dew point → start earlier (e.g. ~34°F open-sky practice).
- Open flowers/young fruit among most sensitive; tissue kill often discussed near mid/high 20s°F depending on conditions.
- Wind helps unprotected tissue mixing but **hurts** irrigated protection (evaporative cooling, uneven coverage).
- Stop irrigation only after ice is melting vigorously (never on cold dry mornings by air temp alone).

Primary science references: UF/IFAS EDIS HS216 (*Protecting Blueberries from Freezes in Florida*), FAWN Cold Protection Toolkit, Florida Blueberry Growers Association guidance.

---

## 7. Data strategy

### 7.1 Tier 1 — must use for prototype

| Source | Role | Access |
|--------|------|--------|
| **FAWN (UF/IFAS)** | Primary Florida ag observations: multi-height T, RH, wind, rain, soil T, solar | FTP yearly CSV, QAQC, gap-free 2005–2020 (30 stations), live JSON/CSV feeds |
| **NOAA GHCN-Daily** | Longer denser Tmax/Tmin/precip climatology | Free, commercial-friendly |
| **NWS API** | 0–7 day forecasts + freeze alerts | Free; User-Agent required |
| **CPC outlooks** | Monthly / 3-month T & P probability features | Free GIS / maps |
| **NMME / Open-Meteo seasonal** | Ensemble anomaly + spread for 30–90 day head | Free research; commercial license for product launch |

**Priority FAWN stations:** Alachua, Putnam Hall, Citra, Ocklawaha, Lake Alfred, Sebring (+ neighbors).

### 7.2 Tier 2 — nice to have / paid at scale

- Visual Crossing or Open-Meteo **paid** (commercial license; free Open-Meteo is non-commercial).
- Meteomatics (leaf wetness, high-res soil).
- Synoptic / MesoWest commercial station stream.
- ASOS/ISD hourly for freeze-night wind/RH near airports.

### 7.3 Do not rely on alone

- CPC/NMME alone as farm daily weather.
- GHCN Tmax/Tmin alone (missing RH, solar, canopy-height T).
- Single FAWN station as “the farm” on radiation freeze nights.
- Leaf-wetness disease models without proxies or paid sensors.

### 7.4 Pipeline sketch

```
HISTORICAL TRAIN
  FAWN FTP / gap-free → clean daily aggregates
  GHCN-Daily → denser T/P + climatology
  Reanalysis fill (Open-Meteo hist) → farm-grid features
  CPC archive + NMME → seasonal features
  Labels: Tmin, frost flags, chill, precip, RH hours

LIVE INFERENCE
  FAWN feeds → lag features
  NWS gridpoint → 0–7d + alerts
  MOS/bias ML → farm-calibrated Tmin & freeze P

60–90 DAY OUTLOOK
  CPC + NMME / seasonal ensembles
  Empirical map: climate anomaly × local FAWN climatology
  Output: chill deficit risk, freeze-season severity, wet-bloom tilt + uncertainty
```

---

## 8. Machine learning approach

### 8.1 Design principle

Do **not** train a pure local daily auto-regressor and roll it out 90 days. Train for targets that match predictability: monthly anomalies, seasonal event probabilities, chill distributions. Use dynamical seasonal guidance as exogenous skill; use ML for local calibration and agricultural event layers.

### 8.2 Model heads

| Head | Horizon | Method |
|------|---------|--------|
| **A** | 0–10 days | NWS / Open-Meteo + local MOS bias-correct to FAWN; freeze P; wetness |
| **B** | 2–4 weeks | Weekly aggregates; blend residual ML + CPC week 3–4 |
| **C** | 1–3 months | NMME/CPC downscale + LightGBM quantiles for monthly T, freeze counts, chill totals |

### 8.3 MVP model stack

1. **Baselines:** DOY climatology quantiles; ENSO-stratified winters; empirical freeze/chill CDFs.
2. **Core ML:** LightGBM / XGBoost quantile and count models (station × month).
3. **Features:** lags, seasonality, ENSO/ONI, NMME anomalies + spread, station attributes, coastal distance.
4. **Calibration:** isotonic / conformal for event probabilities; reliability diagrams.
5. **Deep learning:** deferred (LSTM/TFT only after tree baselines for short-range if needed).

### 8.4 Evaluation (farmer-relevant)

| Metric | Use |
|--------|-----|
| CRPSS vs climatology | Continuous (monthly T, chill hours) |
| Brier skill score | Binary (freeze in window, chill deficit) |
| Reliability + sharpness | All probabilities |
| Hit / false-alarm at decision thresholds | Freeze protect economics |
| Leave-one-winter-out CV | Never random day shuffle (*N* ≈ winters) |

### 8.5 Success criteria for ML spike

- Positive skill vs climatology for (1) monthly temperature anomaly and (2) seasonal chill or freeze-window probability at 0–2 month lead on held-out years.
- Document near-zero skill for daily 60–90 day Tmax/Tmin so product design does not fight the data.
- Written claim sheet of what the model may and may not say.

---

## 9. System architecture

### 9.1 Stack

| Layer | Choice |
|-------|--------|
| Language / ML | Python 3.11+, pandas/polars, scikit-learn, LightGBM |
| Storage | PostgreSQL + Parquet on disk |
| API | FastAPI + Pydantic |
| Frontend | Next.js, TypeScript, Tailwind, Recharts/MapLibre |
| Batch | Cron / Makefile first; Prefect later if needed |
| Hosting (prototype) | Local Docker; Vercel + Render/Railway + Neon free tiers |

### 9.2 Offline vs online

| Workload | Cadence |
|----------|---------|
| Historical backfill | Once + incremental |
| QC + features | Nightly |
| Model retrain | Monthly |
| Seasonal forecast batch | Weekly (more often in bloom) |
| NWS short-range + freeze alerts | Every 1–6 hours |
| API / dashboard | Online read-only of published results |

**Rule:** Nothing in the request path trains models or scrapes heavy history.

### 9.3 Core domain entities

- `Station` — FAWN/GHCN metadata  
- `Observation` — hourly/daily weather  
- `FeatureDaily` — chill, freeze hours, precip anomaly, etc.  
- `FarmProfile` — location, cultivars, chill requirement, phenology, system capacity, cold-spot bias  
- `ForecastRun` / `Forecast` — versioned multi-horizon outputs with p10/p50/p90  
- `RiskEvent` — typed event probabilities + advisory text  

### 9.4 Suggested monorepo layout

```
BlueberryWeatherForecastModel/
├── PROJECT_PROPOSAL.md
├── README.md
├── docs/
│   ├── README.md
│   ├── architecture.md
│   ├── data-sources.md
│   ├── risk-definitions.md
│   └── roadmap.md
├── data/                  # gitignored raw/processed
├── packages/
│   ├── common/
│   ├── ingest/
│   ├── features/
│   ├── models/
│   └── risk/
├── services/api/
├── apps/web/
├── pipelines/
├── notebooks/
└── tests/
```

---

## 10. Roadmap

| Phase | Timeline | Deliverable |
|-------|----------|-------------|
| **0 — Proposal** | Done | This document + docs/ |
| **1 — Data + baselines** | Weeks 1–2 | FAWN/GHCN ingest, chill/freeze labels, climatology scores |
| **2 — Dual models** | Weeks 3–5 | Short-range MOS + seasonal LightGBM events; skill report |
| **3 — API + dashboard** | Weeks 5–7 | Tonight + Season screens; demo farms |
| **4 — Pilot polish** | Weeks 7–10 | SMS freeze hierarchy, bilingual Night Plan, verification |
| **v1** | Season 2 | Disease spray windows, consultant multi-farm, optional sensors |
| **v2** | Later | DEM frost pockets, capacity optimizer, co-op regional board |

### Pilot scope

- **Geography:** Alachua–Marion–Putnam first; then Polk/Highlands evergreen.
- **Users:** ~15–40 farms + 2–3 consultants (when product ready).
- **Season:** Deploy before January freeze season when possible.
- **Partners:** Soft alignment with FAWN/UF-IFAS content review and FBGA.

---

## 11. Monetization (brief)

| Model | Fit |
|-------|-----|
| Freemium county outlook | Acquisition |
| Subscription per farm + $/acre | Primary |
| Co-op / packer licensing | B2B2C |
| Consultant multi-farm seat | Channel |

Niche acreage is small; willingness-to-pay is high for freeze nights. Price risk reduction, not “weather app.”

---

## 12. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Chaos / low seasonal skill | Dual-horizon UX; skill vs climatology; grey-out unskilled targets |
| Liability on freeze advice | Decision-support disclaimers; NWS as official warnings; Extension-aligned language |
| Incomplete SHB critical temp tables | Ranges + “confirm with thermometer/IFAS,” not hard kill °F |
| FAWN distance from frost pockets | Grower cold-spot bias; later on-farm sensors |
| Open-Meteo non-commercial free tier | Prototype free; paid license before launch |
| Competing with free FAWN | Win on Night Plan, stage, SMS, verification workflow |
| Small addressable market | High per-farm value; expand to GA blueberry / FL strawberry adjacency later |
| Alert fatigue | Strict hierarchy; escalate only when conditions worsen |

---

## 13. Success metrics

### Prototype demo

- Farmer can open dashboard, select a FL blueberry location, see **2–3 month risk cards** and **tonight decision** in seconds.
- Short-range freeze advisory consistent with NWS when cold air is imminent.
- Full pipeline: ingest → features → forecast → API → UI documented and reproducible.

### ML

- Beat climatology on weekly/monthly min-temp and at least one event probability (freeze window or chill).
- Document skill decay by horizon.
- Versioned `ForecastRun` with model + data as-of date.

### Pilot (later)

- Median lead time to protect guidance; false-alarm rate; grower usefulness rating; SMS Night Plan open rate; retention next freeze season.

---

## 14. Immediate next build steps

1. Scaffold monorepo structure and `README.md`.
2. Ingest FAWN historical data for blueberry-belt stations; compute daily chill and freeze labels.
3. Implement climatology baselines and a rules-based **Tonight** freeze engine (value before fancy ML).
4. Train seasonal LightGBM event models with CPC/NMME features; write skill report.
5. Ship FastAPI + Next.js dashboard for 3 demo farms (Alachua, Polk, Highlands).
6. Add SMS/email freeze hierarchy for pilot.

---

## 15. References (selected)

- FAWN data access: https://fawn.ifas.ufl.edu/data/
- FAWN Cold Protection Toolkit: https://fawn.ifas.ufl.edu/tools/coldp/
- UF/IFAS EDIS HS216 — Protecting Blueberries from Freezes in Florida: https://edis.ifas.ufl.edu/publication/HS216
- NOAA Climate Prediction Center outlooks: https://www.cpc.ncep.noaa.gov/
- NWS API: https://www.weather.gov/documentation/services-web-api
- Peeling et al. (2023) — Gap-free FAWN 2005–2020 dataset (Sci Data)

---

## 16. Bottom line

Florida blueberry profitability is an **early-market freeze gamble** executed with **diesel, water, dew point, and chill**. Existing tools supply data; few own the full grower narrative from chill → pump night → wetness disease → harvest crews → seasonal planning.

**Build:** dual-horizon FAWN-first decision support with honest ML seasonal risk.  
**Do not build:** a 90-day daily weather fantasy.

Supporting detail lives in [`docs/`](docs/README.md).
