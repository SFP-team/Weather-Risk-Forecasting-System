# Future plan: from prototype to a usable, validated recommendation tool

Date: 2026-09-21. Basis: eight parallel research scouts (Paul's new R file, code audit, crop-modelling second opinion, validation data, genotype layer, management layer, weather inputs, product/deployment), full reports in `docs/research/2026-09-21/`, plus Paul's River Valley review (`docs/weather/SUPERVISOR_REVIEW_RIVER_VALLEY.md`). Effort figures are builder-days for one person working with AI coding assistance at about six productive hours a day; overlaps between scouts have been removed. Calendar time is longer than builder-days because every phase ends with a supervisor review.

Implementation update, 2026-09-22: the user authorized recurrence gating, disease-weather ranking, the four exposure families, one researched planting window and dashboard updates. These now run as `stage_risks_v2`; see [verified methods and sources](weather/production/README.md). Regional establishment guidance replaces the uncited budbreak planting offsets. Chill portions, new phenology constants, management/genotype models and hosted deployment were not part of this change. The user subsequently authorized GitHub publication.

## 1. Where the project stands

Built and working: completed global daily and land-hourly archives for 2010–2025; API hourly access still limited to 19 extracted cells; `stage_risks_v2` with ≥50%/12-winter gating, disease-family ranking and stage exposures; one regional establishment window; 18 updated dashboard presets and HTML/JSON exports. The full backend suite passed 96 tests; 39 production/API tests passed again after an analysis-version metadata fix.

Not built: arbitrary-cell hourly adapter, calibrated phenology, chill portions in production, management effects, genotype shortlist, scientific validation, station bias correction or team deployment. Legacy chill/GDD/stage constants remain provisional and unchanged; software verification does not resolve their agronomic limitations.

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
| 1.1 | Shared metric catalogue implemented and consumed by both JS views. Typed-result validation, environment-configurable root/port and data-driven preset grouping remain future work. | remaining scope |
| 1.2 | Implemented: individual-winter stage windows, ≥50% recurrence, ≥12 complete winters, `by_id`/`ranked`/`demoted`, reasons and UI split. | complete |
| 1.3 | Implemented: one disease-weather family with flowering, fruit-development and harvest evidence, not duplicate headline ranks. | complete |
| 1.4 | Implemented: cold-or-wet pollination proxy plus cold/dry hypothesis comparator; warm midwinter hours and separately labelled daily fallback; berry-stage frost; stage-specific dry spells. No invented loss thresholds. | complete |
| 1.5 | Implemented: `regional-establishment-v1`, independent of mature-plant budbreak. UF Florida window; UGA/Embrapa winter guidance with coarse seasonal precision. Unsupported regions decline. The R offset proposal was not adopted. | complete |
| 1.6 | Chill portions as a profile option (`chill_comparison.chill_portions` moved into production), Safe Winter Chill (p10), provisional CP class cuts, both chill quantities shown side by side | 2 |
| 1.7 | Snapshots, three-site report, runbook and current tests updated for the authorized scope; later chill-method changes will need fresh verification. | complete for this scope |

Current delivered scope: 18 presets show gated risks, disease evidence, new exposures and planting guidance. Phase 1.6 chill portions remains pending. Paul/Gerardo review of River Valley and Papanduva is still needed; modeled River Valley harvest remains 23 April–2 June, not the supervisor's early-April expectation.

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

### Phase 3 — Any coordinate on Earth (≈ 8 builder-days; revised 2026-09-21)

On 2026-09-21 the user authorized a land-only global hourly cache (`pipelines/weather/global_hourly.py`: T2M and dewpoint, 2010–2025, 3,479 land 5×5 blocks, ≈ 29 GB measured). With it, daily→hourly reconstruction and on-demand fetch are no longer needed for chill; they remain as a fallback only if a pin lands in a block the mask calls ocean.

| # | Work | Days |
|---|---|---|
| 3.1 | `hourly_for()` reads any land cell from the cached hourly store (`Source`-style slice by cell index), writes the per-cell parquet lazily, reports `hourly_source` from the cache; remove the panel-only path | 1.5 |
| 3.2 | Durable jobs and result cache (SQLite, worker thread, `POST /analyses` → 202) replacing the single lock | 3.5 |
| 3.3 | Elevation delta warning (DEM lookup vs cell mean), Tmax-only lapse toggle | 2 |
| 3.4 | Coverage check: pins in ocean-labelled blocks return an explicit `no_hourly_block` state; land-mask edge review on the panel coasts | 1 |

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
| Phases 1 + 3 + 6-core: any coordinate, usable by the team over Tailscale | ≈ 33 | 7–8 weeks |
| + Phase 4 + Phase 5: four outputs delivered (system, window, risks, cultivar shortlist), v1 | ≈ 47 | 10–11 weeks (under 3 months) |
| + Phase 2: scientifically validated for a defined use | ≈ 65 | 4–5 months, and only if UF bloom/harvest records and expert pre-registration arrive by week 6 |
| + stretch | ≈ 76 | 5–6 months |

"Complete" in the sense of REQUIREMENTS.md v1 (four outputs for any coordinate, honest evidence state) is the 47-day line. The genotype output at that point is a cited rule-based shortlist, not a trained genotype × environment model; the model needs the breeding program's trial data and is a separate 8–10 day effort with unknown start date.

Critical path: Paul's chill-method decision (needed by Phase 1.6, but both profiles can be built and the decision selects the primary), then UF data for Phase 2. Nothing else blocks.

## 5. How it gets completed

1. **Every change is a named profile beside `legacy_paul_v1`**, so old and new outputs stay comparable and Paul can see exactly what a rule change does on the 18 presets.
2. **One metric catalogue.** The implemented backend catalogue feeds both JS views. A broader typed result schema remains future work, not a claim of this delivery.
3. **Both chill metrics run until the decision**; chill hours stay visible for AgroClimate compatibility, chill portions become primary when Paul signs off.
4. **Pre-registration before validation.** Paul and Gerardo write expected class, bloom and harvest for the 18 sites before seeing model output; the sheet is checksum-locked.
5. **Bias study before correction.** Correct Tmin only where the multi-year station comparison shows a stable offset; never correct RH; never apply a lapse rate to Tmin without local evidence.
6. **Management and genotype layers consume the same site outputs**, so a change in the chill chain flows through without a second convention.
7. **Deployment stays on the university server**; the team reaches it through Tailscale or Cloudflare Access; the public site keeps serving snapshots only.
8. **Each phase ends with a supervisor review and a verified handover.** GitHub publication is authorized again as of 2026-09-22; follow the review, privacy and remote-verification rules in `AGENTS.md`. Publication does not authorize hosted deployment.

## 6. Decisions needed from people

| Decision | Who | Blocks |
|---|---|---|
| Chill metric: chill portions primary, hours as comparator | Paul | 1.6, 2.1, 5 |
| Review 50% recurrence / 12-winter reporting policy and stage applicability | Paul | implemented provisionally; calibration remains open |
| Review regional establishment guidance, stock assumptions and coarse GA/Brazil season bounds | Gerardo | local agronomic confirmation; no uncited offset fallback |
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
