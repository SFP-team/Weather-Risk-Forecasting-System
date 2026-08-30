# Recommendation engine redesign

This is the product the breeding-program briefing asked for, mapped onto what is already in the tree. It is possible. It is not what the current analogue UI does.

The current analogue is a **farm-to-farm shortlist**: pick a known operation, rank other known operations. That is useful and we keep it.

What Patricia’s conversation asked for is a **coordinate-in, recommendation-out** tool:

1. Last 10 years of **base weather** at queryable points (not a 30-year monthly mean pretending to be winters).
2. **Formulas** that derive production system and targeted risk factors on the fly.
3. Two modes: **this is my land** vs **recommend where**.
4. Structure modifiers (tunnels, pots) that can change the system.
5. **Genotype** recommendation from a precomputed index — after the weather layer works.

Do not build the genomic model first. Do not download a global hourly cube first.

---

## Is it possible?

**Yes**, in layers. The briefing is implementable. The parts that are *not* possible yet are data and expert lock-in, not software.

| Ask | Possible now? | Blocker |
|---|---|---|
| Query any lat/lon | **Yes** | `/api/diagnose` is in this branch |
| Last 10 years dated daily T / rain / solar | **Yes** | NASA POWER daily, cached in SQLite |
| Derive chill, freeze, harvest rain, DLI on the fly | **Yes** | Existing physics + new `derive/` |
| Classify deciduous / semi-evergreen / evergreen | **Yes, provisional** | Thresholds need Gerardo + Patricia |
| Tunnels / pots change the recommendation | **Yes, provisional** | Same meeting: how much rain is too much |
| Recommend similar regions, not only the pin | **Yes** | Region pack + analogue shortlist |
| Recommend cultivars from cards | **Yes, interim** | Rule-based ranking, not genomics |
| Recommend Stage 4s + current cultivars | **Not yet** | Patricia’s list is empty on purpose |
| Genomic × weather selection index | **Later** | Pedigree, trials, Diego; precompute offline |
| Global hourly every land point | **Wrong first download** | See storage below |

---

## What the briefing actually said

Speech-to-text wrote “Wispr base word.” That is **weather base data**.

Keep a lean, queryable archive of a few raw variables. Calculate everything else at query time. Ten years is enough because the climate is moving; a 1981–2010 normal is the wrong decade for a planting decision.

Two products in one tool:

- **Specific.** “I have this land in Brazil.” Diagnose *this* coordinate: windows, risks, genotypes. Compare to the Florida → North Carolina gradient we already grow on. Within-window is not comfortable (a 51 next to a 90 is a watch). Harvest rain is the headline risk.
- **Recommendation.** “Where should I look?” Similar environments, then the *region* (Waldo is in Alachua County — return the county, not only the pin). Sometimes the best place is not the original coordinate.

Production systems are a **gradient**: deciduous, semi-evergreen, evergreen. Tunnels can run an evergreen genotype in a deciduous climate (they already do this at Waldo). Pots drain; they do not stop fruit split unless rain is also excluded.

Genotypes are a **third layer**. Sample environments offline, score an index, look up the top 5 when a query lands in that bucket. Do not run the genomic model on every click.

Update weather once a year. Retrain the genotype index when new Stage 4s or cultivars are added.

---

## What we already had (keep it)

The analogue stack is not waste. It is Layer 2’s similarity engine.

| Keep | Why |
|---|---|
| 303-site truth set | Named operations + Florida gradient + known failures |
| Variety cards (5 classes, 25 cultivars) | Interim genotype list and chill envelopes |
| Dual chill + freeze / heat / rain-crack / DLI / VPD | The formula library |
| Tunnel / cover transfer functions (Matamala) | Structure modifiers already have numbers |
| CCAFS lag + Hallegatte gates | “Recommend where” vs known ops |
| Skill sheet | Honest validation for the similarity half |
| Map UI | Same surface; new inputs |

What was **wrong for this brief**:

- Catalog-only. You could not drop a Brazil pin.
- NASA POWER **monthly climatology** expanded into one synthetic 2018. Chill hours for Waldo were a typical-year construct, not dated winters.
- Habit was a user dropdown (`deciduous` / `evergreen`). No semi-evergreen. No on-the-fly classification.
- Market week was an **input filter**. The briefing wants the tool to **recommend** the window.
- No genotype ranking. User picked the cultivar.
- UI system knobs did not recompute features (cached per site).

---

## Architecture (what we implement)

```
Base weather (store once)          Formulas (on the fly)           Lookup (precomputed)
─────────────────────────          ──────────────────────          ────────────────────
Tmin Tmax Tmean                    chill / freeze                  sampled-env
precip                             harvest-rain / DLI / drought    selection index
solar  RH  wind  Tdew              habit classifier                top 5 genotypes
10 years, daily, points            planting / flower / harvest     per system bucket
SQLite / parquet                   tunnel & pot modifiers
        │                                    │                              │
        └──────────── diagnose(lat, lon) ────┴──── similar environments ────┘
                              │
                    genotype shortlist (cards now;
                    Stage 4 index when Patricia fills the YAML)
```

### Layer 1 — weather + formulas (this branch)

This is the layer the briefing said to build first.

- `weather/` — NASA POWER **daily** 2015–2024, SQLite point store, fallback so the API always returns.
- `derive/` — yearly stats, windows, risk factors vs the SE US belt, habit classifier, tunnel/pot modifiers.
- `recommend/diagnose.py` — coordinate in, report out.
- `recommend/similar.py` — region pack + analogue shortlist.
- `recommend/genotypes.py` — rule-based card ranking. Advanced selections YAML is empty and labeled `awaiting_patricia`.
- `POST /api/diagnose` — the new product path. Classic `POST /api/shortlist` stays.

### Layer 2 — lean the archive

Once Layer 1 is used on real queries, drop variables we never derive from. Keep T, rain, solar (humidity if freeze/VPD stay). That is the “don’t keep junk” step.

### Layer 3 — genotype index (after the meeting)

1. Patricia: recommendable cultivars + Stage 4s, and which habits each can run (including under tunnels).
2. Gerardo: lock chill / freeze / harvest-rain / DLI thresholds and tunnel/pot mitigations.
3. Diego: pedigree / genomic matrix and trial sites.
4. Collaborator asterisk: where licensed material already performs, and in which system.
5. Sample ~200–500 global environments (not every pixel). Fit trait models offline. Collapse to **one selection index**. Store top 5–10 genotypes per (region × habit × structure) bucket.
6. At query time: classify habit + modifiers, then **look up** the bucket. No live genomic predict.

Annual job: refresh the weather store; rebuild the index if the list changed.

---

## Base weather: what to download (and what not to)

The briefing said “most points in the globe” and “base weather only.” That is not “ERA5-Land hourly for every land cell.”

**Key variables** (enough to derive the rest):

| Store | Derive on the fly |
|---|---|
| Tmin, Tmax (Tmean optional) | Chill hours / portions, freeze days, GDH, windows |
| Precipitation | Harvest-rain days, crack events, drought |
| Shortwave / solar | DLI, cloudy fruit-fill |
| RH, wind, dewpoint (cheap, keep) | VPD, wet-bulb freeze, bees, Botrytis |

Hourly is better for chill. We do **not** need to store hourly globally. Dated **daily** Tmin/Tmax plus the existing hourly curve is the Layer 1 default. Pull ERA5-Land hourly only for truth-set and shortlist points when we start selling a chill number.

### Storage if we refuse to compromise (honest)

| Product | Points | Time | Size |
|---|---|---|---|
| Catalog daily 10y | 303 | daily | ~40 MB |
| SE US 0.1° daily 10y | ~2,000 | daily | ~250 MB |
| Global land 1° daily 10y | ~15,000 | daily | ~2 GB |
| Global land 0.5° daily 10y | ~60,000 | daily | ~8 GB |
| Global land 0.25° daily 10y | ~250,000 | daily | ~30 GB |
| Same 0.25° **hourly** 10y | ~250,000 | hourly | ~0.7 TB |
| ERA5-Land global hourly 10y | full grid | hourly | **5–20 TB** |

**Recommended download, in order:**

1. NASA POWER **daily** 2015–2024 for the 303 catalog sites (start with Waldo, Alachua, the Florida belt, Vacaria, São Joaquim).
2. On-demand POWER daily for every diagnose query; persist in SQLite.
3. A global **1° land sample** (~15k points, ~2 GB) so “recommend where” is not stuck with 2 Brazil pins.
4. Denser SE US + collaborator countries (0.25°).
5. ERA5-Land hourly **only** at shortlist / trial points when we need better chill.

That is the “sits there, not queried as a 20 TB cube, calculate the rest” design. A global hourly cube is possible if someone later wants it. It is the wrong week-one job.

`python -m blueberry_analogue.cli weather --live --ids us-fl-waldo,us-fl-alachua,us-fl-miami`

---

## Formulas (Layer 1, provisional)

Thresholds live in `derive/production_system.py` and `derive/risk_factors.py` so a meeting can change one file.

**Open-field habit**

- Evergreen: median winter chill < 180 h, frost days ≤ 2, winter tmin p10 ≥ 1.5 °C
- Deciduous: chill ≥ 420 h **or** winter tmin p10 < −1.2 °C **or** ≥ 6 hard-freeze days
- Semi-evergreen: the remainder (Ocala / north-central Florida mental model)

**Modifiers**

- Tunnel / greenhouse: bloom freeze and harvest rain collapse. Allowed habits expand. A deciduous open field can run evergreen under plastic (Waldo).
- Pots / substrate: drainage risk drops. Fruit split remains unless rain is also excluded.
- Covers still do **not** restore chill.

**Risks** (scored against the Florida → Carolina window, with a tighter comfort band)

1. Winter chill (too low → low-chill / evergreen genotype)
2. Bloom / winter freeze
3. **Rain during harvest** (headline)
4. Low solar / DLI during fruit fill
5. Berry-surface heat
6. Warm-season drought

Status: comfortable / borderline / concerning / extreme. Borderline means “still in the window, competing against 90s.”

**Windows** — planting, flowering, harvest from last-frost + habit. Output, not an input. Tunnels can pull bloom ~30 days.

---

## Genotype layer (honest)

Today: rank the 25 public cards by chill envelope × harvest-rain crack risk × heat × allowed habit.

Not today: Stage 4s, “cultivars Patricia would actually send,” genomic EBV × weather, collaborator performance.

`packages/analogue/blueberry_analogue/data/advanced_selections.yaml` is the hole to fill after the meeting.

---

## Meeting agenda (do not skip)

The briefing was explicit: do not invest the genotype layer until this aligns.

**Patricia**

- Cultivars he will recommend vs retired names.
- Stage 4 list and which habits each can run, including under tunnels.
- Confirm two modes (diagnose land / recommend where).
- Collaborators who already grow UF material: what works, which system.

**Gerardo**

- Chill / freeze / harvest-rain / DLI cutoffs.
- What tunnels actually change, and at what temperature.
- What pots mitigate, and how much rain is still too much.

**Diego**

- Pedigree / genomic matrix and which trial sites are usable for the index.

---

## How to run this branch

```bash
python -m blueberry_analogue.cli diagnose --lat 29.79 --lon -82.17
python -m blueberry_analogue.cli weather --live --ids us-fl-waldo,us-fl-alachua
python -m blueberry_analogue.cli serve    # http://127.0.0.1:8010
```

UI: **Diagnose this land** (click the map or type coordinates) or the classic farm-to-farm shortlist.

`POST /api/diagnose` body: `{ "lat", "lon", "structure", "media", "cover", "live" }`.

Without `--live`, diagnose expands cached POWER monthly climatology or a lat/lon fallback and **says so**. Dated winters require `live: true` or a prior `weather --live` ingest.

A live POWER daily pull for Waldo (2015–2024) gives about 334 chill hours, 3 frost days, an April–May harvest window, deciduous open-field, and a low-chill SHB list (Emerald, Jewel, Snowchaser). The old monthly cache had January tmin −6.7 °C every day — that is not a Florida winter. Dated daily is the point of Layer 1. Miami daily classifies evergreen with zero chill and recommends Ventura / evergreen Biloxi. Tunnels on Waldo unlock evergreen and semi-evergreen.

---

## What success looks like

A collaborator drops a Brazil pin. In seconds they see: nearest named cluster, open-field habit, what tunnels would unlock, harvest-rain and chill watches versus the SE US belt, a recommended window, and a short genotype list labeled as a recommendation. They can then ask “where else looks like this?” and get regions, not a plant-here button.

That is the report from four weeks ago, automated. The genomic index is the next layer, not the first.
