# Blueberry Weather Forecast Model

**Florida blueberry weather risk forecasting and decision-support prototype.**

General weather apps forecast temperature and rain. This project aims to forecast **crop-relevant conditions** and **adverse-event probabilities** for Florida blueberry growers—especially freeze protection, chill accumulation, disease weather risk, and seasonal planning horizons of up to 2–3 months.

## Start here

| Document | Purpose |
|----------|---------|
| **[PROJECT_PROPOSAL.md](PROJECT_PROPOSAL.md)** | Full project proposal |
| **[docs/](docs/README.md)** | Architecture, data sources, risk definitions, roadmap |

## Product thesis (short)

**Dual-horizon decision support:**

1. **Operations (0–10 days)** — freeze protect/start-stop guidance, disease wetness, harvest weather (highest farmer willingness-to-pay).
2. **Planning (1–3 months)** — probabilistic chill deficit, freeze-night odds in a window, wet/dry tilt via local ML + NOAA CPC/NMME (not a fake daily 90-day weather calendar).

Data backbone: **FAWN** (UF/IFAS) + NOAA GHCN + NWS + Climate Prediction Center.

## Status

| Area | Status |
|------|--------|
| Research & proposal | Complete |
| Documentation | Complete (`PROJECT_PROPOSAL.md` + `docs/`) |
| Code / data pipeline | Not started (greenfield) |

## Honest scope

| We will build | We will not claim |
|---------------|-------------------|
| Near-term freeze & risk alerts | Deterministic daily weather 90 days out |
| Seasonal risk probabilities & ranges | Exact freeze dates months ahead |
| Farmer dashboard in blueberry language | Replacement for official NWS warnings |

## Next implementation steps

See [docs/roadmap.md](docs/roadmap.md). Summary:

1. Scaffold monorepo and FAWN ingest for blueberry-belt stations  
2. Chill / freeze feature baselines  
3. Short-range rules + seasonal LightGBM event models  
4. FastAPI + Next.js farmer dashboard  

## Disclaimer

This project is **decision support research/prototype**, not a substitute for National Weather Service warnings or University of Florida IFAS Extension freeze and crop advice.
