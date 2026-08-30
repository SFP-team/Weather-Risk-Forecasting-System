# Weather Risk Forecasting System

**Florida blueberry weather risk forecasting and decision-support product.**

Repository: [SFP-team/Weather-Risk-Forecasting-System](https://github.com/SFP-team/Weather-Risk-Forecasting-System)

General weather apps forecast temperature and rain. This system forecasts **crop-relevant conditions** and **adverse-event probabilities** for Florida blueberry growers—freeze protection, chill accumulation, disease weather risk, and seasonal planning (1–3 months as risk outlooks, not fake daily calendars).

## Product thesis

**Dual-horizon decision support:**

1. **Operations (0–10 days)** — Tonight freeze protect / start-stop guidance, 7-day freeze–wetness–harvest risk  
2. **Planning (1–3 months)** — Chill progress + probabilistic freeze-window / chill cards (LightGBM + climatology)

## Quick start

### 1. Python backend

```bash
cd Weather-Risk-Forecasting-System   # or this folder
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Build data, features, models, demo farms
python pipelines/run_all.py

# API (http://127.0.0.1:8000/docs)
cd services/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Web dashboard

```bash
cd apps/web
npm install
npm run dev
```

Open **http://localhost:3000**

### 4. Blueberry Analogue (site selection)

A separate product. Diagnose a coordinate (production system, harvest-rain and chill risk, windows, genotypes) or shortlist similar operations. It is not bolted onto the Florida farm demo. See [docs/analogue/REDESIGN.md](docs/analogue/REDESIGN.md).

```bash
source .venv/bin/activate
python -m blueberry_analogue.cli build          # offline climate fallback
python -m blueberry_analogue.cli build --live   # NASA POWER point climatology
python -m blueberry_analogue.cli serve          # http://127.0.0.1:8010
```

See [docs/analogue/README.md](docs/analogue/README.md). Shortlist only. Book the flight. Do not plant 20 ha.

### 3. Tests

```bash
source .venv/bin/activate
pytest -q
```

## Demo farms

| Farm | County | Station | Focus |
|------|--------|---------|--------|
| North Florida Emerald Block | Alachua | ALACHUA | Freeze + chill (deciduous) |
| Central Florida Star & Avanti | Polk | LAKE_ALFRED | Evergreen / fruit |
| Highlands Early Evergreen | Highlands | SEBRING | Early harvest |

## API highlights

| Endpoint | Purpose |
|----------|---------|
| `GET /health` | Status |
| `GET /farms` | Demo farms |
| `GET /farms/{id}/tonight` | Freeze decision card |
| `GET /farms/{id}/seven-day` | Operational week |
| `GET /farms/{id}/season` | Chill + 1–3 month risk cards |
| `GET /farms/{id}/chill` | Chill progress |
| `PATCH /farms/{id}` | Update phenology / bias |
| `GET /meta/metrics` | Model skill vs climatology |
| `GET /docs` | OpenAPI |

## Repository layout

```
packages/common      schemas, stations, DB, farms
packages/ingest      synthetic FL history, Open-Meteo, NWS
packages/features    chill hours, freeze flags
packages/risk        tonight freeze engine, seasonal cards
packages/models      LightGBM seasonal train/predict
services/api         FastAPI
apps/web             Next.js farmer dashboard
pipelines/run_all.py end-to-end batch
docs/                product & architecture docs
PROJECT_PROPOSAL.md  full proposal
```

## Data notes

- **Training corpus:** multi-year synthetic Florida blueberry-belt climatology (realistic freeze/chill/precip patterns) for offline reliability.
- **Live overlay:** Open-Meteo archive/forecast + NWS point forecast when network allows.
- **Stations:** Alachua, Putnam Hall, Citra, Ocklawaha, Lake Alfred, Sebring (FAWN-oriented).

## Honest scope

| We build | We do not claim |
|----------|-----------------|
| Near-term freeze decision support | Deterministic daily weather 90 days out |
| Seasonal risk probabilities | Exact freeze dates months ahead |
| Farmer dashboard in blueberry language | Replacement for NWS warnings |

## Documentation

- [PROJECT_PROPOSAL.md](PROJECT_PROPOSAL.md)
- [docs/](docs/README.md)

## Disclaimer

Decision support prototype only. Not a substitute for National Weather Service warnings or University of Florida IFAS Extension freeze and crop advice.
