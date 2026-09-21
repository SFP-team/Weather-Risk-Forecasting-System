# Future plan: from prototype to a usable, validated recommendation tool

Date: 2026-09-21. Basis: eight parallel research scouts (Paul's new R file, code audit, crop-modelling second opinion, validation data, genotype layer, management layer, weather inputs, product/deployment), full reports in `docs/research/2026-09-21/`, plus Paul's River Valley review (`docs/weather/SUPERVISOR_REVIEW_RIVER_VALLEY.md`). Effort figures are builder-days for one person working with AI coding assistance at about six productive hours a day; overlaps between scouts have been removed. Calendar time is longer than builder-days because every phase ends with a supervisor review.

## 1. Where the project stands

Built and working: global daily weather 2010–2025 for every land cell; hourly temperature for 19 cells; an open-field production chain (`legacy_paul_v1`) that outputs system class, calendar and frequency-ranked risks for any pin with hourly data; a dashboard with 18 presets, a growing-cycle ruler and exports; 79 backend tests.

Not built: planting window, risk gating, disease as a ranked risk, management-system effects, genotype shortlist, any scientific validation, station bias correction, team deployment. The science layer still runs on constants that the literature and Paul's own newer R file both contradict (50 h chill anchor, chill hours with no lower bound over six months, +150 GDD budbreak with no source, one harvest offset for all species).

## 2. What the research found (one line each; details in the reports)

| Direction | Key finding | Report |
|---|---|---|
| Paul's new R file | Planting = budbreak − 105 … − 30 days; his "multiple windows" are an artefact of taking month-day medians with an April wrap; our `calendar()` already uses the correct median-offset mechanism and only lacks planting offsets. His R computes Dynamic Model chill portions (same constants as chillR) but never uses them. Ten constants differ from `legacy_paul_v1` (100 h not 50; four-month chill window; GDD from (Tmin+Tmax)/2). | 01 |
| Code audit | Science is unit-tested; API assembly, snapshot split and all JavaScript are not. Metric definitions live in five Python tables and two JS tables, so every new metric touches seven places; a registry refactor makes each later change ~30 % cheaper. Preset whitelist hides any non-southeastern site. | 02 |
| Second opinion | The chain (chill → heat → offsets) is what the field does; the parameters and data handling are the known pitfalls. Top fixes: chill portions + Safe Winter Chill, cultivar-class GDD-from-1-Jan bloom, Tmin bias correction, severity-aware gated ranking, bloom-date validation. Drop climate-analog similarity from any score. Add a CMIP6 2040s card after the chill switch. | 03 |
| Validation data | Best free truth: Georgia NASS weekly harvest %, USDA AMS weekly shipments (FL/GA), Kovaleski 2015 Citra bloom curves, Embrapa Pelotas cultivar dates, USA-NPN records. UF's own trial bloom/harvest logs are the highest-value data and are internal. Realistic accuracy with grid weather and cultivar classes: bloom MAE 7–12 days, harvest ±10–14 days; class agreement is the first pass/fail test. | 04 |
| Genotype layer | A cited attribute table for ~30 UF SHB + 10 rabbiteye cultivars (chill, bloom/harvest timing, system, split, disease) can drive a filter + score shortlist without a model. Freeze/heat tolerance per cultivar does not exist in print. Adunola et al. 2024 (24 genotypes × 4 FL environments × 5 seasons × 21 covariates) is the training set for the model path. | 05 |
| Management layer | Tunnels: Tmax +3 to +12 °C, Tmin 0 to +3 °C (Georgia tunnels gave no frost protection), PAR −25 %, rain off fruit but splitting not eliminated, harvest 2–5 weeks earlier, pollinators must be managed. Pots: waterlogging and soil pH removed; irrigation dependence and root-zone heat added. A system × risk adjustment table with sources is ready to implement. | 06 |
| Weather inputs | Keep NASA POWER as the backbone. Add daily→hourly reconstruction (Linvill/chillR method; chill portions tolerate it, chill hours less so), on-demand hourly per opened cell, a multi-year FAWN/INMET bias study before any correction, CHIRPS for rain-day counts, elevation delta as a warning. ERA5-Land only as a per-point second opinion. | 07 |
| Product/deployment | Copy three patterns from AgroClimate, NEWA and Global Chilling: provenance up front, banded classes with printed thresholds, "reliable in 90 % of years" framing. Deploy as a token-auth FastAPI on the university server reached through Tailscale (free, 6 seats) or Cloudflare Tunnel + Access (50 seats). Cloud is static-only and breaks the data boundary. | 08 |

## 3. Roadmap

### Phase 1 — Apply Paul's decisions and fix the science core (≈ 14 builder-days)

| # | Work | Days |
|---|---|---|
| 1.1 | Prerequisite refactors: metric/risk registry consumed by backend and both JS files; typed result schema (`docs/weather/analysis_schema.json`) validated in tests; `WEATHER_ROOT`/port from environment so the pipeline runs off-server; data-driven preset groups | 3.5 |
| 1.2 | Risk gating: stage-overlap rule plus configurable frequency threshold; `ranked[]` and `demoted[]` with reasons; UI split | 2 |
| 1.3 | Disease as ranked risks (flowering, harvest) | 1 |
| 1.4 | New metrics: pollination-unfavourable days, warm mid-winter hours (hourly, daily fallback), berry-stage freeze, stage-specific dry spell | 2 |
| 1.5 | Planting window: profile `paul_analogs_v2` (Paul's constants), planting offsets in `season()`/`calendar()`, single window from median budbreak, planting lane in the ruler | 2.5 |
| 1.6 | Chill portions as a profile option (`chill_comparison.chill_portions` moved into production), Safe Winter Chill (p10), provisional CP class cuts, both chill quantities shown side by side | 2 |
| 1.7 | Snapshot regeneration, runbook, changelog, tests | 1 |

Exit: 18 presets show gated risks with reasons, disease ranked, planting window, chill hours and chill portions side by side; Paul reviews River Valley and Papanduva again.

### Phase 2 — Phenology and evidence (≈ 18 builder-days; calendar gated on data)

| # | Work | Days |
|---|---|---|
| 2.1 | Cultivar-class phenology profiles: class chill requirements, GDD-from-1-Jan/1-Jul bloom with 10/50/90 targets, species-specific harvest offsets, evidence level per date | 3 |
| 2.2 | Multi-year station bias study: FAWN (4–5 stations) and INMET (4–6) 2011–2025; monthly Tmin/Tmax bias, frost hit/miss, chill-portion bias; fit monthly additive Tmin correction on odd years, test on even; `corrected` flag in results | 6 |
| 2.3 | Severity fields on freeze/heat/rain events (degree-hours, mm) and severity × frequency ordering inside the gate | 2 |
| 2.4 | Extend the hourly record to 1981 for the 19 cells (40+ winters) and recompute p10 | 1 |
| 2.5 | Phenology truth loaders: Georgia NASS weekly PDFs, AMS shipments, literature table, USA-NPN | 3 |
| 2.6 | Validation harness: pre-registration CSV (Paul/Gerardo, checksum-locked), `validation_scores.py` (MAE days, class κ, Brier), `VALIDATION_PROTOCOL.md`, evidence badge from scores | 3 |

Exit: a validation report with numbers; the first honest "validated for defined use" label or an explicit list of what failed.

### Phase 3 — Any coordinate on Earth (≈ 12 builder-days)

| # | Work | Days |
|---|---|---|
| 3.1 | Daily→hourly reconstruction with validation on the 19 cells (hourly RMSE, chill hours, chill portions, class agreement); third tier in `hourly_for()` flagged `reconstructed` | 4.5 |
| 3.2 | Durable jobs and result cache (SQLite, worker thread, `POST /analyses` → 202) replacing the single lock | 3.5 |
| 3.3 | On-demand hourly fetch for an opened cell (reusing `evaluation_sites.fetch`), bounded cache, status upgrade in the UI; requires acquisition authorization | 2 |
| 3.4 | Elevation delta warning (DEM lookup vs cell mean), Tmax-only lapse toggle | 2 |

Optional: CHIRPS rain-day source (3), ERA5-Land second opinion via Open-Meteo (2–3; needs owner decision on the service).

### Phase 4 — Management layer (≈ 8 builder-days)

Management profile dict (system × metric → remove / reduce by parameter / worsen / note, each with source and confidence), `adjust()` between exposures and ranking, `system` query parameter, baseline vs adjusted rows in the UI, management-anchored evergreen calendar profile for evergreen-class sites, tunnel chill recompute on hourly cells.

### Phase 5 — Genotype shortlist v1 (≈ 6 builder-days; model path later)

`config/cultivars.json` with a citation per cell and conflicts kept as ranges; `genotype_match.py` (evergreen branch by system membership, deciduous branch by chill requirement ≤ site p10 chill in the 0–7.2 °C band; score on bloom-window freeze exposure, split × harvest rain, disease flags, region prior); API field and UI panel with rule trace and "assumption-based" label. Model path (reaction-norm GBLUP with environmental covariates on Adunola 2024 data): 8–10 days after data access, Florida-only support.

### Phase 6 — Team deployment and product surface (≈ 11 builder-days)

FastAPI service with bearer token serving `dist/` and the cached API (overlaps 3.2; 2.5 extra), Tailscale rollout and runbook (1), verdict strip with gated risks and evidence badges (2), print/report view matching Paul's packet (2), shareable URL scenarios (1), map pin input with cell outline (1), API and restart tests (2). Later: two-site comparison (2), batch coordinates → CSV (4), server PDF (1).

### Stretch

CMIP6 2040s scenario card from NEX-GDDP-CMIP6 with delta-change to the POWER baseline (5–6); frontend module split with JS tests (2.5); sigma-dissimilarity "closest reference cell" hint replacing analog similarity (2).

## 4. How long

| Milestone | Builder-days | Calendar estimate |
|---|---|---|
| Phase 1: science core with Paul's rules | 14 | 3–4 weeks |
| Phases 1 + 3 + 6-core: any coordinate, usable by the team over Tailscale | ≈ 37 | 8–9 weeks |
| + Phase 4 + Phase 5: four outputs delivered (system, window, risks, cultivar shortlist), v1 | ≈ 51 | 11–12 weeks (about 3 months) |
| + Phase 2: scientifically validated for a defined use | ≈ 69 | 4–5 months, and only if UF bloom/harvest records and expert pre-registration arrive by week 6 |
| + stretch | ≈ 80 | 5–6 months |

"Complete" in the sense of REQUIREMENTS.md v1 (four outputs for any coordinate, honest evidence state) is the 51-day line. The genotype output at that point is a cited rule-based shortlist, not a trained genotype × environment model; the model needs the breeding program's trial data and is a separate 8–10 day effort with unknown start date.

Critical path: Paul's chill-method decision (needed by Phase 1.6, but both profiles can be built and the decision selects the primary), then UF data for Phase 2. Nothing else blocks.

## 5. How it gets completed

1. **Every change is a named profile beside `legacy_paul_v1`**, so old and new outputs stay comparable and Paul can see exactly what a rule change does on the 18 presets.
2. **Registry first.** The metric/risk registry and typed schema (1.1) are done before any new metric, because six of the later items each touch seven places today.
3. **Both chill metrics run until the decision**; chill hours stay visible for AgroClimate compatibility, chill portions become primary when Paul signs off.
4. **Pre-registration before validation.** Paul and Gerardo write expected class, bloom and harvest for the 18 sites before seeing model output; the sheet is checksum-locked.
5. **Bias study before correction.** Correct Tmin only where the multi-year station comparison shows a stable offset; never correct RH; never apply a lapse rate to Tmin without local evidence.
6. **Management and genotype layers consume the same site outputs**, so a change in the chill chain flows through without a second convention.
7. **Deployment stays on the university server**; the team reaches it through Tailscale or Cloudflare Access; the public site keeps serving snapshots only.
8. **Each phase ends with a supervisor review on the dashboard**, the handover updated, and a push.

## 6. Decisions needed from people

| Decision | Who | Blocks |
|---|---|---|
| Chill metric: chill portions primary, hours as comparator | Paul | 1.6, 2.1, 5 |
| Gating threshold (≈50 % of winters?) and overlap definition | Paul | 1.2 |
| Planting offsets (budbreak −105…−30 d) are the intended agronomy; spring planting in the SE US? | Gerardo | 1.5 |
| Cultivar classes and cultivars in scope; conflicting chill values (Primadonna, Sweetcrisp, Magnus, Krewer) | Patricio | 2.1, 5 |
| Tunnel Tmin offset (0 or +1.5 °C); splitting under cover reduce vs remove | Paul, Gerardo | 4 |
| Pre-registered expectations for 18 sites | Paul, Gerardo | 2.6 |
| Drop analog similarity from any score (Paul authored it) | Paul | stretch |
| Tailscale agent on the server / on-demand hourly acquisition | Rohit, IT | 3.3, 6 |
| Open-Meteo or CDS account for ERA5-Land comparison | owner | optional |

## 7. Data requests

- UF trial logs: per site-year bloom % and ripe % ratings at Citra, Waldo and grower sites 2011–2025, with cultivar, cyanamide, tunnel and frost-protection flags.
- Adunola et al. 2024 trial data (genotype × site × season phenotypes, coordinates, planting dates, management) and the genomic relationship matrix or SNP set (Diego).
- Program's official chill requirement per cultivar and any observations on rain splitting, bloom-freeze damage and heat.
- Any UF-cultivar trial-years in Brazil, Peru or Mexico held by licensees.
- Papanduva field records or Epagri historical station data (request needed).

## 8. Main risks

- Grid warm-night bias (+1 °C) undercounts chill at deciduous sites and frost everywhere; until Phase 2.2 every freeze and chill number carries that caveat.
- No published chill-portion requirement for any UF cultivar; class cuts in CP are derived from this project's own cells and must be labelled so.
- Validation may show the fixed-offset calendar is wrong by more than a week; the plan then fits GDD targets to Citra data and holds out years, which is a different (calibrated) model.
- Evergreen systems (south Florida, Peru) have no validated phenology model in the literature; the management-anchored calendar is a convention, and heat, not chill, is the binding risk there.
- Free third-party services (Open-Meteo, Tailscale, Cloudflare free tier) have seat and uptime limits.
