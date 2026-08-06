# Technical architecture

Prototype architecture for the Florida blueberry weather risk product. Optimized for a small team shipping a credible demo, not enterprise MLOps.

See also: [PROJECT_PROPOSAL.md](../PROJECT_PROPOSAL.md).

---

## 1. Design principles

1. **Batch-first** — Models train and forecast offline; the API serves published results only.
2. **Dual horizon** — Short-range (NWS + local calibration) is separate from seasonal risk (CPC/NMME + LightGBM).
3. **FAWN-first truth** — Prefer in-situ Florida ag stations over generic consumer APIs for observations.
4. **Honest uncertainty** — p10/p50/p90, skill vs climatology, grey-out unskilled targets.
5. **Simple ops** — Postgres + Parquet + cron before Feast/K8s/streaming.

---

## 2. Recommended stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Language / ML | Python 3.11+, pandas/polars, numpy, scikit-learn, LightGBM | Fast tabular ML; interpretable enough for risk products |
| Baselines | Climatology, ENSO-stratified stats, optional Prophet for EDA | Skill zero-point |
| Database | PostgreSQL (+ PostGIS later) | Farms, forecasts, risk events |
| Feature dumps | Parquet under `data/processed/` | Cheap training I/O |
| Orchestration | Makefile + cron (v0); Prefect later | Avoid overbuild |
| API | FastAPI, Pydantic, SQLAlchemy/asyncpg | Thin read API |
| Frontend | Next.js, TypeScript, Tailwind, Recharts, MapLibre | Mobile-first farmer UI |
| Config | `.env` + pydantic-settings | |
| Packaging | uv or poetry monorepo; Docker Compose | |
| Experiment tracking | Metrics JSON / local MLflow | Lightweight |

---

## 3. System diagram

```
[FAWN FTP/feeds] [NOAA GHCN] [Open-Meteo] [NWS API] [CPC / NMME]
        │              │            │           │          │
        └──────────────┴────────────┴───────────┴──────────┘
                              │
                     ingest → raw/ (Parquet/CSV)
                              │
                     QC → features (daily/weekly)
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
     train (monthly offline)          forecast batch (nightly/weekly)
     model registry / artifacts       blend ML + external outlooks
              │                               │
              └───────────────┬───────────────┘
                              ▼
                   Postgres: forecasts, risk_events, farms
                              │
                   FastAPI (read-only) → Next.js dashboard
                              │
                   SMS/email alerts (MVP+)
```

---

## 4. Pipeline jobs

| Job | Cadence | Purpose |
|-----|---------|---------|
| `ingest_fawn` | Daily / weekly backfill | Yearly CSV + live feeds |
| `ingest_noaa` | Weekly | GHCN-Daily neighbors + climatology |
| `ingest_open_meteo` | As needed | Gap fill / grid point features |
| `ingest_external_outlooks` | 1–6h (NWS); weekly (CPC) | Short-range + seasonal exogenous |
| `qc_observations` | Nightly | Units, gaps, outliers, source priority |
| `build_features` | Nightly | Chill, freeze hours, precip anomaly, lags |
| `train_*` | Monthly | Retrain with leave-one-winter-out metrics |
| `run_forecast_batch` | Weekly (more in bloom) | 4–12 week outlooks + event probabilities |
| `publish` | After batch | Upsert API tables |

---

## 5. Offline vs online

| Workload | Mode |
|----------|------|
| Historical backfill | Offline, heavy |
| QC + features | Offline, nightly |
| Model retrain | Offline, monthly |
| Seasonal/ML forecast batch | Offline, weekly |
| NWS freeze alert overlay | Near-real-time, 1–6h |
| API + dashboard | Online, **read-only** |

**Hard rule:** No training or heavy scrapes on the request path.

---

## 6. Integrating external forecasts with local ML

Three-layer blend:

| Horizon | Primary signal | Local role |
|---------|----------------|------------|
| Days 1–2 | NWS / Open-Meteo short-range | Bias-correct to FAWN; apply freeze rules |
| Weeks 3–6 | Local ML + residual | Blend with seasonal anomaly |
| Weeks 7–12 | CPC / NMME + climatology | Light ML residual; risk distributions only |

```
Week 1–2:   mostly NWS/Open-Meteo → risk rules + MOS
Week 3–6:   blend local ML + seasonal anomaly
Week 7–12:  seasonal + climatology + light residual model
```

Display CPC outlook **transparently** next to model risk (trust + methodology).

---

## 7. Domain model

### Station

- `id`, `source` (`fawn` | `ghcn` | `synthetic`)
- `name`, `lat`, `lon`, `elev_m`, `county`, `active`
- `start_date`, `end_date`, `timezone`

### Observation

- `station_id`, `ts`
- `temp_c`, `temp_min_c`, `temp_max_c`
- `rh_pct`, `precip_mm`, `wind_ms`, `solar` (if any)
- `qc_flag`, `source`

### FeatureDaily / FeatureWeekly

- `station_id` or `location_id`, `date`
- `chill_hours`, `gdd_base`, `freeze_hours_le_32`
- `precip_mm`, `precip_anom`, `mean_temp`, …
- `feature_version`

### FarmProfile / LocationProfile

- `id`, `name`
- `lat`, `lon` or `nearest_station_id`
- `cultivar_group`, `chill_requirement_hours`
- `critical_freeze_temp_f` by phenology stage (guidance ranges)
- `irrigation_freeze_protection`, `system_rate_in_per_hr`
- `cold_spot_bias_f` (e.g. −2°F vs FAWN)
- `production_system` (`deciduous` | `evergreen`)
- phenology stage per block

### ForecastRun

- `id`, `created_at`, `model_version`, `horizon_days`
- `init_time`, `config_hash`

### Forecast

- `run_id`, `location_id`
- `valid_start`, `valid_end` (week or month bins preferred beyond day 14)
- `variable` (`tmin_mean` | `precip_total` | `chill_accum` | …)
- `value`, `unit`, `p10`, `p50`, `p90`
- `method` (`ml` | `climatology` | `external` | `blend`)
- `confidence` (`low` | `med` | `high`)

### RiskEvent

- `run_id`, `location_id`
- `event_type` (see [risk-definitions.md](risk-definitions.md))
- `window_start`, `window_end`
- `probability`, `severity` (1–5)
- `drivers` (JSON)
- `advisory_text` (templated in v0)

---

## 8. Repository structure

```
BlueberryWeatherForecastModel/
├── PROJECT_PROPOSAL.md
├── README.md
├── docker-compose.yml
├── pyproject.toml
├── .env.example
├── data/
│   ├── raw/           # gitignored
│   ├── interim/
│   └── processed/
├── packages/
│   ├── common/        # schemas, db models, config
│   ├── ingest/        # FAWN, NOAA, NWS, CPC clients
│   ├── features/      # chill, freeze, precip features
│   ├── models/        # train, evaluate, predict
│   └── risk/          # event defs + calibration
├── services/
│   └── api/           # FastAPI
├── apps/
│   └── web/           # Next.js dashboard
├── pipelines/
│   ├── nightly.sh
│   └── Makefile
├── notebooks/         # EDA only
├── tests/
└── docs/
```

Shared `common` package holds Pydantic schemas so API and batch never drift.

---

## 9. Hosting (low-cost prototype)

| Component | Local | Cheap cloud |
|-----------|--------|-------------|
| Postgres | Docker | Neon / Supabase free |
| Batch | Laptop cron / GH Actions | Render worker or scheduled GH Action |
| API | uvicorn | Render / Railway / Fly.io |
| Frontend | next dev | Vercel free |
| Models / parquet | `./data` | R2 or local artifact store |

**Demo topology:** Vercel (web) + Render (API) + Neon (DB) + weekly GitHub Action for forecast batch.

---

## 10. Security, liability, and disclaimers

- v0 can be open read-only demo; later magic-link or simple auth.
- UI must state: **decision support only**; not a substitute for NWS warnings or UF/IFAS freeze advice.
- Attribute FAWN, NWS, CPC; confirm UF/IFAS data terms before commercial redistribution.
- Do not emit free-form LLM agronomy advice in v0; use templated advisories.

---

## 11. Explicit v0 cuts

- No real-time on-farm IoT required
- No deep foundation weather models
- No multi-tenant enterprise auth
- No automated SMS until pilot phase (dashboard first is OK for tech demo)
- ~10 demo locations, not every FL parcel
- One risk family first (**freeze**), then chill, then precip/disease

---

## 12. Success metrics (engineering)

- Full pipeline in one documented command path.
- Reproducible `ForecastRun` with model version + data as-of.
- Dashboard load of risk calendar &lt; 3 seconds for a selected farm.
- Holdout skill report checked into `docs/` or `artifacts/` after first train.
