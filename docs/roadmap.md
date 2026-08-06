# Build roadmap

Phased plan for the Florida blueberry weather risk prototype and pilot product.

See also: [PROJECT_PROPOSAL.md](../PROJECT_PROPOSAL.md), [architecture.md](architecture.md).

---

## Phase 0 — Proposal (complete)

- [x] Multi-agent research (ag science, data, ML, product, architecture)
- [x] [PROJECT_PROPOSAL.md](../PROJECT_PROPOSAL.md)
- [x] Supporting docs in `docs/`

---

## Phase 1 — Data foundation (weeks 1–2)

**Goal:** Reproducible multi-station Florida weather corpus with blueberry labels.

| Task | Done when |
|------|-----------|
| Scaffold monorepo (`packages/`, `services/`, `apps/`, `data/`) | Repo builds empty packages |
| FAWN historical ingest for priority stations | Daily tables on disk/Postgres |
| GHCN-Daily neighbors for same counties | Merged station catalog |
| QC: units, gaps, source flags | QC report notebook |
| Features: chill hours, freeze flags (32/28/24°F), precip, RH hours | `FeatureDaily` table |
| Climatology baselines (DOY quantiles, freeze rates) | Baseline metrics JSON |
| FarmProfile schema + 3 demo farms (Alachua, Polk, Highlands) | Seed data |

**Exit gate:** Can plot multi-year chill and freeze-night counts for Alachua vs Lake Alfred.

---

## Phase 2 — Models (weeks 3–5)

**Goal:** Dual-horizon skill vs climatology documented.

### Short-range (Head A)

| Task | Done when |
|------|-----------|
| Ingest NWS gridpoint forecasts for demo locations | Stored forecast features |
| MOS / bias model: NWS or Open-Meteo → FAWN Tmin | Holdout MAE / freeze Brier |
| Rules engine: Tonight protect / watch / beyond system | Unit tests on historical freeze nights |

### Seasonal (Head C)

| Task | Done when |
|------|-----------|
| Align CPC / NMME hindcasts with winters | Feature matrix by station-month |
| LightGBM quantiles: monthly T, freeze counts, chill totals | Leave-one-winter-out CV |
| Calibrated event probs: P(freeze window), P(chill shortfall) | Reliability diagrams |
| Claim sheet: what we may/may not say | Checked into `docs/` or `artifacts/` |

**Exit gate:** Positive skill on ≥1 seasonal target (monthly T anomaly **or** chill/freeze window). Document near-zero skill for daily 60–90d Tmax/Tmin.

---

## Phase 3 — API + dashboard (weeks 5–7)

**Goal:** Farmer-readable demo without SMS yet.

| Task | Done when |
|------|-----------|
| FastAPI: stations, farms, forecasts, risk_events | OpenAPI docs |
| Batch `run_forecast` writes versioned `ForecastRun` | Idempotent weekly job |
| Next.js **Tonight** screen | Traffic light + checklist |
| **Season** screen | Month+1…+3 risk cards + chill bar |
| **7-Day** strip | Icons for freeze / wet / rain |
| Methodology + disclaimer footer | FAWN/NWS/CPC attribution |
| Deploy free tiers (optional) | Public demo URL |

**Exit gate:** Demo script: “Farm A chill status; weeks 3–5 freeze risk; tonight NWS frost path → protect checklist.”

---

## Phase 4 — Pilot polish (weeks 7–10)

**Goal:** Usable for a small grower cohort in freeze season.

| Task | Done when |
|------|-----------|
| Manual phenology stage per block | UI + API |
| Cold-spot bias setting | Affects thresholds |
| SMS/email L1–L4 freeze hierarchy | Delivery logs |
| Bilingual Night Plan (EN/ES) | Shareable link |
| After-action log (protected? damage?) | Stored events |
| Verification dashboard (hits/false alarms) | Season summary |
| Disease wetness lite (post-protect flag) | Morning email |

**Exit gate:** 15–40 pilot-ready accounts; alert usefulness survey template ready.

---

## Phase v1 (season 2 / months 6–14)

- Fuller Botrytis / anthracnose wetness×temp indices
- Harvest logistics (rain/heat crew planning)
- Consultant multi-farm view
- Optional on-farm sensor integration
- Dynamic chill model (portions)
- Paid commercial weather API path finalized
- Soft partnership content review with IFAS/FBGA

---

## Phase v2 (months 14–24)

- DEM-based frost pocket ranking within farm
- Pump capacity optimizer (“which 60% of acres to save”)
- Evergreen vs deciduous product modes refined
- Co-op / packer regional risk board
- Expansion exploration: Georgia blueberry, Florida strawberry adjacency

---

## 6-week ML experiment plan (detail)

| Week | Focus |
|------|--------|
| 1 | Truth, targets, baselines; leave-one-year-out climatology + ENSO |
| 2 | NMME/CPC ingest; simple downscaling; score vs climatology |
| 3 | LightGBM hybrid; reliability diagrams |
| 4 | Event products + farmer metrics; draft claim language |
| 5 | Ablations, rare freezes, spatial holdout stations |
| 6 | Lock MVP stack; optional wire 0–10d NWP module; evaluation report |

---

## Pilot scope (when product ready)

| Dimension | Recommendation |
|-----------|----------------|
| Geography | Alachua–Marion–Putnam first |
| Users | 20 mixed small + mid-size + 2–3 consultants |
| Season | Before January freeze season |
| Partners | FAWN/UF-IFAS content review; FBGA intro |
| Kill criterion | If growers say “FAWN SMS is enough,” iterate until Night Plan + stage + capacity language is the retention reason |

---

## Success metrics by phase

| Phase | Metric |
|-------|--------|
| 1 | Data completeness %; chill/freeze series plottable |
| 2 | CRPSS/BSS &gt; 0 on priority seasonal target |
| 3 | Demo walkthrough &lt; 5 minutes without engineer narration |
| 4 | Pilot usefulness ≥4/5 on freeze nights; median L2 lead ≥12h |
| v1 | Paid conversion or co-op LOI |

---

## Immediate next actions (implementation)

1. Initialize git repo, `README.md`, `.gitignore`, `pyproject.toml`.
2. Implement `packages/ingest` FAWN FTP downloader for priority stations.
3. Compute chill hours + freeze flags; write baseline notebook.
4. Scaffold FastAPI + minimal Next.js shell reading mock risk JSON (parallelize).
5. Replace mocks with real batch outputs after Phase 2 gate.

---

## Explicit non-goals until later

- 90-day daily weather calendar as a primary feature
- Yield prediction / insurance pricing
- Pesticide rate recommendations
- Full FMS (inventory, payroll)
- Hardware sales as core business
