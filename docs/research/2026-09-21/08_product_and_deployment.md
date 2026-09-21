<!-- Research scout report (ProductDeployment), generated 2026-09-21 for the future plan. Read-only literature/code research; claims marked [unverified] are not confirmed. -->

# Product & deployment direction — scout report

## 1. Findings with sources

### 1.1 Comparable decision tools

| Tool | Inputs | Outputs | Uncertainty shown | Deployment / auth | Learn |
|---|---|---|---|---|---|
| UF AgroClimate Chill Calculator ([USDA Hub summary](https://www.climatehubs.usda.gov/hubs/southeast/tools/agroclimate-chill-hours-calculator), [tool](https://cloud.agroclimate.org/tools/chillCalculator/)) | FAWN station, chill model (<45 °F, 32–45 °F, Utah, Dynamic), period | Accumulation curve + map with banded legend; historic average, last season, ENSO-phase overlay | Comparison lines only; no CI | Public web, no login; FL/GA only | Model selector with same-chart overlay; ENSO phases as a named scenario |
| AgroClimate Blueberry Advisory System ([tool](http://cloud.agroclimate.org/tools/bas/), [validation, Plant Disease 2021](https://apsjournals.apsnet.org/doi/10.1094/PDIS-09-20-1961-RE)) | Station pick; leaf wetness + temperature | Anthracnose risk low/moderate/high with published cut-offs (<15 %, 15–50 %, >50 %) and 24 h spray window | Three classes with explicit thresholds; field validation on 9 farms | Web + iOS/Android; account for alerts | Publish numeric class thresholds beside the label; validate against practice before release |
| Cornell NEWA ([about](https://cals.cornell.edu/integrated-pest-management/risk-assessment/newa), [degree days](https://newa.cornell.edu/about-degree-days)) | On-farm station, model, biofix date | ~40 DD/IPM tools; status boxes | Textual caveats on formula, day boundary, logging; “should not be substituted for actual observations” | Free account; station membership; 15 states | Standing caveat block per model; ‘not validated here’ language |
| WSU AgWeatherNet ([WSU](https://treefruit.wsu.edu/tools-resources/wsu-agweathernet/)) | Station | Raw data + disease/chill decision aids | Little | Guest vs registered (free) tiers | Two-tier access: public summaries, registered full data — maps onto our snapshot vs connected modes |
| Climate FieldView ([pricing](https://climate.com/en-us/pricing.html)) | Grower field data | Field maps, scripts, reports | Not scientific uncertainty | SaaS, free/$749+/Premium | Out of scope; confirms report/insight tier is what people pay for |
| FAO EcoCrop ([GAEZ](https://gaez.fao.org/pages/ecocrop), [model](https://github.com/OpenCLIM/ecocrop)) | Crop, climate grid | 0–1 suitability from optimal/absolute T and rain ranges | None; index only; tool discontinued ~2015, folded into GAEZ v4 | Public | Anti-pattern for us: single composite score hides which factor fails |
| chillR / UC Davis Global Chilling ([methods](https://treephenology.ucdavis.edu/chp/glc/materials_methods.html), [Luedeling 2011](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0020155)) | Station data, weather generator, scenarios | Safe Winter Chill = chill exceeded in 90 % of years (10th percentile), Dynamic Model only | Percentile framing; refuses to publish chill-hours maps because unreliable in warm winters | Static maps; R package | Report chill as p10 “safe” value, not mean; state why a method is withheld |
| Vineyard site tools ([Virginia Tech](https://www.cgit.vt.edu/research/archive/vineyard-site-evaluation.html), [Vermont](https://www.uvm.edu/~ebuford/VGWC/vgwc_help.html), [VineMAP](https://www.vinescapes.com/vinemap-online/)) | Map pin/parcel | Climate + topography + soil layers; site summary report | Layer-by-layer, no composite | Public GIS or paid report | Map-first input; downloadable site report is the deliverable |

[unverified] AgroClimate’s BAS and Chill Calculator may have changed UI since the cited pages; capabilities above are from documentation, not live use.

### 1.2 Current UI state (repo)
- `dist/app.js` fetches `/api/analysis` with a 90 s timeout; results are never cached client-side beyond the snapshot catalog; URL is not updated, so nothing is shareable.
- `location_api.py` has one global `BUSY` lock (503 on concurrent request), no result cache, no auth, no job model. `analysis_id` is a content hash, which is a good basis for caching.
- Badges in `index.html` are static text; evidence level is not derived from result fields.
- The `documents.modelContext.registerTool` hook exists — an unusual surface for a research tool; keep or drop deliberately.

### 1.3 Deployment facts
- GitHub Pages access control exists only on Enterprise Cloud ([GitHub](https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/changing-the-visibility-of-your-github-pages-site)); on free plans a Pages site is public.
- Cloudflare Zero Trust/Access free up to 50 users; Workers free 100k req/day, 10 ms CPU; R2 10 GB free ([Cloudflare](https://www.cloudflare.com/plans/developer-platform/)). Cloudflare Tunnel is outbound-only from the server (no inbound port).
- Tailscale Personal: free, 6 users, unlimited devices ([Tailscale](https://tailscale.com/pricing)). Fly.io has no free tier; ~$2–6/month per small VM ([pricing summary](https://www.saaspricepulse.com/blog/flyio-free-tier-2026)) — excluded by the no-paid-services constraint.

### 1.4 Uncertainty patterns
- IPCC: two separate axes, confidence (evidence × agreement) and likelihood (calibrated bands) ([guidance](https://climate-adapt.eea.europa.eu/en/knowledge/tools/uncertainty-guidance/topic2)). Matches the plan’s two status axes.
- GRADE: four certainty levels with named downgrade reasons ([NHMRC](https://www.nhmrc.gov.au/guidelinesforguidelines/develop/assessing-certainty-evidence)). Useful as ‘why is this exploratory’ reasons.
- USDA hardiness map: “average lowest, not lowest ever” caveat ([USDA](https://planthardiness.ars.usda.gov/pages/how-to-use-the-maps)); reviewers note visual uncertainty is still missing ([Applied Geography 2023](https://www.sciencedirect.com/science/article/pii/S0143622823000693)).
- BAS: class thresholds printed with the label. Global Chilling: percentile-based ‘safe’ value and an explicit refusal note for the weaker method.

## 2. Recommendations

### 2.1 Architecture (decision)
Options:
- (a) Static snapshots + SSH tunnel (current). Cost 0. Only Rohit can use it daily; two terminals per session; no cache; one request at a time. Effort 0.
- (b) Server FastAPI behind VPN/token. Cost 0. Team uses it daily if reachable: university VPN (needs IT) or Tailscale (6 seats, install on server + laptops) or Cloudflare Tunnel + Access (email OTP for @ufl.edu, no inbound port). Effort 4–6 days.
- (c) Cloud with pre-extracted per-cell store. Free tiers hold it: ~60k land cells × ~25 KB derived summaries ≈ 1.5 GB on R2 [INFERENCE]; but the production packet needs hourly per cell and Workers’ 10 ms CPU cannot run it, so cloud is static-only, and shipping raw cells off-server breaks the runbook boundary. Effort 6–8 days plus authorization; defer.

Recommend (b): `pipelines/weather/serve.py` (FastAPI, stdlib-adjacent, replaces the ad-hoc handler in `location_api.py`): bearer token from env, `POST /analyses` returning 202 + id when uncached, `GET /analyses/{id}`, SQLite cache keyed by request hash + method version, single background worker replacing `BUSY`, serves `dist/` as static. Network: Tailscale first (zero IT dependency, 6 seats covers the team), Cloudflare Tunnel later if externals are added. Keep the hosted snapshot site as the public-safe demo.

### 2.2 UX backlog (prioritised, hours for one builder with AI assistance)
| # | Item | Where | h |
|---|---|---|---|
| 1 | Verdict strip: system, window (median with p10–p90 span), top-3 gated risks with n/N and CI, evidence badge — one screen above the fold; move current tables under details | `app.js` renderProduction, `index.html` §00 | 8 |
| 2 | Risk gating per Paul (stage overlaps window AND frequency ≥ threshold) shown as “ranked / demoted (why)” with threshold visible; needs backend field | `production.py` (cross-topic), `app.js` | 6 UI |
| 3 | Evidence badges derived from result fields: availability (`ready/not_acquired/unsupported`) × interpretation (`descriptive/exploratory/validated_for_defined_use`), with reason list GRADE-style | `app.js`, API schema | 6 |
| 4 | Print stylesheet + “Report” view matching Paul’s packet: five questions (REQUIREMENTS §6), calendar figure like R §15 (l.1640–1708), risk table like §12 (l.1329–1413); browser PDF first | `style.css` @media print, new `report.js` | 12 |
| 5 | Shareable/saved scenarios: encode lat, lon, system, profile, winter, stage in URL hash; localStorage list of named scenarios | `app.js` | 6 |
| 6 | Map pin input: Leaflet or MapLibre with OSM raster tiles and attribution, no key; click sets lat/lon; show the 0.5°×0.625° cell outline for the pin | `index.html`, `app.js` | 8 |
| 7 | Two-site comparison: second column, shared cycle lanes, delta table for risks; reuse `cycle.js` with two results | `cycle.js`, `app.js` | 16 |
| 8 | Batch mode: paste/upload CSV of coordinates → table (system, window, top risks, hourly availability) → CSV download; server loops through queue | API + `batch.js` | 16 UI + 16 API |
| 9 | Chill-method toggle (hours vs Dynamic Model) once decided; show both in sensitivity | `app.js`; backend cross-topic | 6 |
| 10 | Closest UF/SE US analog panel (REQUIREMENTS §13) — depends on analog-distance work | cross-topic | 8 UI |
| 11 | Server-rendered PDF from the same result JSON (WeasyPrint) for parity with export | server | 8 |

Total ≈ 130 h ≈ 16 days.

### 2.3 Roadmap
- Phase A — team MVP (≈13 days): serve.py + token + cache + queue (5); Tailscale rollout and runbook update (1); backlog 1, 3, 4, 5, 6 (5); smoke tests and API tests in `tests/weather/test_location_api.py` (2).
- Phase B — validated internal tool (≈24 days): backlog 2, 7, 8, 9, 11 (9); parity tests against Paul’s §11 per-season output for Papanduva/Citra/Waldo (3, cross-topic); supervisor-signed label set and threshold table rendered from one config (2); restart/concurrency tests, redacted logging (3); Cloudflare Tunnel + Access if collaborators outside Tailscale seats (2); usability session with Patricio/Paul and fixes (5).
- Phase C — external release (30+ days, gated): security review, rate limits, terms and data attribution page, precomputed global cell summaries for daily-only pins (6–8), genotype layer UI once Part 3 exists (unbounded), server PDF, monitoring.

## 3. Effort per recommendation (person-days)
- Architecture (b) with Tailscale: 4–6. With Cloudflare Tunnel + Access instead: +1–2. Option (c): 6–8, not recommended now.
- UX backlog: see table; Phase A subset ≈ 5, Phase B subset ≈ 9.
- Tests/hardening for the service: 3–5.

## 4. Risks, unknowns, human decisions
- Authorization: any network exposure (Tailscale agent on the server, Cloudflare Tunnel, VPN) needs Rohit/IT approval; constraint says no deployment without it.
- Seats: Tailscale free = 6 users; team is 5 now; externals push to Cloudflare Access (50) or paid.
- Hourly coverage: on-demand hourly per cell is cheap but is an acquisition; batch mode must stay bounded and authorized per cell.
- Chill method and risk-frequency threshold are open supervisor decisions; UI should render them from config, not hard-code.
- Report parity: Paul’s hand-made HTML packets are the acceptance target; a side-by-side review with him is required before calling the PDF “done”.
- [unverified] Exact current AgroClimate/NEWA UI behaviour; sizes for a global derived-summary store are estimates.
- Cross-topic: risk gating and disease ranking (science scout); analog panel (analog scout); chill method (chill scout).
