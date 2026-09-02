# Blueberry recommendation platform — full requirements

**Status:** requirements only. No UI, no weather archive, no models on this branch.  
**Date collected:** August–September 2026  
**Product owner (science):** Patricio (Patricia in speech-to-text) — UF blueberry breeding  
**Science / methods:** Paul Adunola  
**Genomics / pedigree:** Diego  
**Physiology / production systems:** Gerardo  
**Build:** Rohit  

This file is the single source of truth for what we are building. It is assembled from:

- Two working sessions with Paul (whiteboard + spoken spec)
- Three (of four mentioned) Papanduva / southern Brazil reports Paul already produced by hand
- Three stakeholder slides: *How the platform works*, *What the breeder gets*, *What is needed to build it*
- The existing UF Florida weather-risk repo (a **different** product; do not bolt this onto it)

Older analogue / diagnose UI and cached climate files live on other GitHub branches. They are **not** the starting point. We download weather and write code again against this document.

---

## 1. What we are making (one sentence)

A person drops a world coordinate and says how they will grow (open vs tunnel, ground vs pots). The tool returns a **recommendation**, not a plant-here order: which production clock fits, when to plant / flower / harvest, the top weather risks, and a short ranked list of UF genotypes that Patricio is willing to send.

**Working name:** Global Blueberry Recommendation (from Paul’s whiteboard). Brand TBD.

**Goal (from the slides):** turn breeder knowledge, climate data, and genotype data into a scalable recommendation system.

---

## 2. Who it is for

| User | Job |
|---|---|
| **Patricio / UF breeding** | Place current cultivars and Stage 4s in new countries; decide what to send a collaborator |
| **Collaborators / licensees** | “I have this land (or this town). What should I trial, when, and what will go wrong?” |
| **Later, maybe** | Independent growers — not the first audience |

This is a **breeder decision dashboard** for genotype placement and selection. It supports trial planning, reduces climate mismatch, and speeds release conversations. It does **not** replace a field visit, quarantine, soil pits, or a license.

---

## 3. What it is not

- Not a “plant 20 hectares” button. Similarity is not identity. Papanduva was a **managed pilot**, not a plantation.
- Not the Florida **tonight freeze / FAWN** farmer app already in this repo (`apps/web`, `packages/risk`). That product stays separate.
- Not “recommend other countries like this” in **version 1**. That is a later feature. v1 answers **this pin only**.
- Not a live genomic predict on every click. The heavy model is run **offline** on sampled environments; the app looks up a ranking.
- Not a 20 TB global hourly cube on day one. Store lean **base weather**; **derive** chill, freeze, harvest rain, windows, and system.
- Not a score over every historical UF genotype. Only lines Patricio will actually recommend (current cultivars + advanced selections). Old named cultivars he has replaced are out.
- Not a claim of commercial success probability.

---

## 4. Version 1 vs later

### Version 1 — build this first

**Inputs (only two):**

1. **Coordinate** (lat / lon). Snap to nearest useful climate unit (county / admin / radius), not a 10 m pixel. Example: a Gainesville pin uses **Alachua County** weather, not a single city block.
2. **Management — pick exactly one** (default = open field + ground):

   | Choice | Meaning |
   |---|---|
   | Open field + ground | Exposed climate + native / pine-bark soil. System classifier **matters**. Use soil data. |
   | Open field + pots | Exposed climate, drainage mostly solved. Fruit split can still happen. |
   | Tunnel or greenhouse + ground | Protected structure (tunnel ≈ greenhouse in the UI). Freeze and harvest rain largely controlled. |
   | Tunnel or greenhouse + pots | Most expensive, most control. Almost all highlighted weather risks shrink. Recommend from the model without filtering hard by open-field clock. |

Tunnel and greenhouse are **one bucket**. Do not ask separately for net / LDPE / woven in v1 unless we later need them.

**Outputs (exactly these four):**

1. **Top 3–5 genotypes** for that environment × management (filtered by production-system class when they are in the **ground**).
2. **Production window:** planting, flowering, harvesting (recommended; not an input market-week filter).
3. **Top risk factors** (about three): e.g. harvest rainfall, flower freeze, dry spell.
4. **Recommended production system:** evergreen / semi-evergreen / deciduous (open-field derivation, then modified by tunnels/pots).

That is the dashboard on the slide *What the breeder gets*.

### Later (do not build until v1 works)

- “I grow here; where else can I grow the same thing?” (Paul’s **Summary** report / RS municipality scan).
- Full cover menu (net, woven, LDPE), HCN, pollinator species.
- Fog as a first-class risk (India / IGP — research later; Paul said “not really” then “it can affect”).
- Live deep-learning vs reaction-norm bake-off in production (train both offline; deploy whichever validates).
- Global ERA5-Land hourly cube.

---

## 5. The four layers (slides + whiteboard)

```
Coordinate + management
        │
        ▼
[1] Climate     10–15 years weather → chill, freeze, rain, heat, drought, radiation
        │
        ▼
[2] Management  open vs tunnel; pots vs ground; soil only if ground
        │
        ▼
[3] Genotype    Patricio’s cultivars + Stage 4s, tagged by clock; pedigree / genomics
        │
        ▼
[4] Prediction  env match, risk, system fit, selection index (precomputed)
        │
        ▼
Ranked genotypes + window + risks + system
```

Layer 1–2 are **formulas on weather** (Paul already has R code for this).  
Layer 3–4 need **people and breeding data** before they are real. Do not invent Stage 4 lists.

---

## 6. Gold-standard reports (what “done” looks like)

Paul already produced this by hand for **Papanduva, Santa Catarina, Brazil (−26.312389, −50.080639)**, August 2026. The automated tool must be able to emit the **same kind of packet** for any coordinate.

We were given three HTML reports (a fourth was mentioned, not uploaded):

| File | Mode | What it is |
|---|---|---|
| `Blueberry_Expansion_Southern_Brazil2.html` | **Diagnose this land** | Original Papanduva full report |
| `Blueberry_Expansion_Southern_Brazil_Revised2.html` | **Diagnose this land** | Same pin, updated classifier and envelope language |
| `Southern_Brazil_Blueberry_Summary_Report.html` | **Recommend where** (later) | RS municipalities + broader genotype list |

### Five questions every diagnose report must answer

1. Is the target climate fundamentally suitable? (vs a SE US / UF reference panel — envelope, not a yes/no crop model)
2. Which production system is most consistent with the climate?
3. Which SE US / UF environments are the closest biological comparisons? (Waldo, Citra, Alachua / Bay / Dixie, etc.)
4. Which weather risks need management?
5. Which UF genotypes should be prioritized for **local validation** (not deployment)?

### Papanduva numbers (example of the payload — not global constants)

Use these to regression-test Paul’s functions when we get his R code. Do **not** hard-code them as truth for other sites.

**Climate / system**

- Hourly-style mean chill ≈ **209 h**; Chill Portions ≈ **30**; WorldClim annual proxy ≈ **368 h** (not interchangeable).
- 100-hour provisional requirement met in **22 / 24** modeled years (**91.7%**). Chill year range cited **78–368 h**.
- Winter mean ≈ **13.4 °C**; coldest month mean ≈ **12 °C**.
- Production GDD ≈ **2,355**; frost-free ≈ **314 days** (revised).
- Original classifier: **semi-evergreen**, high confidence, because 209 h sits in **150–300 h** transitional band.
- Revised classifier: **deciduous**, because WorldClim **368 h ≥ 300 h** rule — to be treated as a **low-chill deciduous hypothesis**, not proof of deep dormancy.
- Suitability: original “feasible only with major targeted risk management”; revised “**marginal / outside SE US reference envelope**” (**0%** envelope support).

**Risks (diagnose-this-land)**

- Headline: **harvest rainfall** (original **206 mm**, revised **173.6 mm**) above SE US reference **95th percentile** (~152–155 mm). Normalized harvest-rain index **100%**.
- Disease-favorable weather: ~**15.5–16.4** days across flowering + harvest.
- Drought / max dry spell in a wet climate: ~**19 days**; can coexist with high seasonal rain. Irrigation without waterlogging.
- Flower freeze / heat: **low** at Papanduva (original flower-freeze ~**4.2%** of years; revised **0**). Insufficient-chill index can look “elevated” only because references almost never fail 100 h.
- Revised also flags **low production-period radiation** (below reference 5th percentile) — sugars / drying.
- Total risk score: original **43.7**, revised **37** (moderate; ~69th percentile of references).

**Windows (southern hemisphere example)**

- Central RS pattern: plant **May–June**, flower **August** (sometimes July–August), harvest **October–November**.
- Higher-chill southwest RS (e.g. Dom Pedrito): plant as early as **March**, flower **July–August**, harvest from **late September**.
- Chill counted **May–August** in the summary maps.

**Florida / UF analogs (examples of scores, methods differ by report)**

- Counties: Alachua, Taylor, Dixie, Bay, Calhoun (FL); Camden (GA).
- UF sites: **Waldo**, **Citra** closest; also Wild Goose, H&A, Frogmore, “Georgia” environment, Central Florida.
- Scores: adjusted similarity ~**71** (Waldo/Citra original); consensus ~**64–65** (revised); environmental kernel **Citra 0.868, Central Florida 0.761, Waldo 0.722** (summary).
- Analogues are **training / comparison environments**, not substitutes for the pin.

**Genotypes in the reports**

- Cultivar comparisons: **Albus, Falcon, Sharper, Optimus** (reaction-norm trait panels: yield, Brix, TTA, firmness, size).
- Summary also ranks advanced selections: **22-0287, 22-0321, 21-0922, 19-15, 21-0357, 21-1121**.
- Method cited: **Jarquín et al. 2014** reaction-norm genomic prediction (*Theor Appl Genet*).
- Always: **replicated trial**, not a single-cultivar commercial recommendation. Target was outside the central training climate.

**Recommend-where (summary only — later feature)**

- 15 leading **Rio Grande do Sul** municipalities as Florida-analog trial geography.
- Named: Jacuizinho, Fortaleza dos Valos, Dom Pedrito, Salto do Jacuí, Campos Borges, Lavras do Sul, plus others (Arroio do Tigre, Quinze de Novembro, Alto Alegre, Estrela Velha; risk text also Ibirubá, Selbach, Bagé, Pinhal Grande).
- Trial design: contrasting sites (central RS low freeze vs southwest high chill / higher freeze vs intermediate).
- Risks among those towns scored **relative to the top-15 mean (> 1 SD = elevated)**, not as biological law.
- Harvest rain still dominates (~167–241 mm); chill 320–556 h; flower-freeze 4–20%.

The automated v1 product is the **diagnose** packet. The summary’s municipality scan is the later “recommend where” feature.

---

## 7. Climate layer — what to store vs what to derive

### Principle (Paul, both sessions)

Keep a **lean, queryable** archive of a few raw variables. Calculate everything else at query time so the database stays small and new risks can be added without re-downloading the globe.

**How far back:** **10–15 years**, not 30-year normals. Climate is moving; a 1981–2010 mean is the wrong decade for a planting decision. Paul: 10 years is enough to be stable; 15 if we can.

**Resolution:** hourly is ideal so any window can be derived. Accept **dated daily** Tmin/Tmax/rain/solar as the first download if hourly global is too heavy; expand to hourly with a standard curve for chill. Do **not** start with a global ERA5-Land hourly cube (5–20 TB, CDS queues, Eduroam will not finish it in a weekend).

**Query model:** the file “just sits there.” We are not scanning a 20 TB cube on each click. We hit the **nearest stored point / county**, then run formulas (milliseconds).

### Base variables to download and keep

Minimum (Paul limited these so the load stays light):

| Store | Why |
|---|---|
| Temperature (hourly or daily Tmin/Tmax/Tmean) | Chill, freeze, GDD, heat, windows |
| Precipitation | Harvest rain, drought, disease wetness |
| Solar radiation / shortwave | DLI, cloudy fruit-fill, “production GDD / sunshine” |
| Relative humidity | VPD, wet-bulb freeze, disease-favorable days |
| (Useful extras if cheap) Wind, dewpoint | Advective freeze, wet-bulb |

Paul: if more variables are easy, take them and structure later — caching means load is not the issue if we stay at point/county grain.

### Features to derive (not store as raw globals)

From the whiteboard, the Brazil reports, and the spoken spec:

| Derived | Meaning |
|---|---|
| Chill hours (0–7.2 °C and/or UF 32–45 °F) | Dual currency; **do not convert linearly** |
| Chill portions (Dynamic Model) | Run in parallel with hours |
| Chill fulfillment vs a provisional requirement (reports used **100 h**) | Year-wise probability (e.g. 22/24 years) |
| Flowering-freeze probability | Freeze during the modeled bloom window |
| Freeze events / freezing hours | Absolute cold |
| Frost-free period | Length of season |
| Consecutive frost / frost streaks | “How many times we have continuous frost” |
| Harvest rainfall (mm and wet days **in the harvest window**) | **Headline risk.** Berry split. Not annual rain. |
| Disease-favorable weather | Warm + wet in flower and harvest (Botrytis / anthracnose style) |
| Maximum production dry spell | Drought *during the season*, even in a wet climate |
| Production GDD | Heat accumulation for development |
| Heat / berry-surface heat | Fruit quality; often low in southern Brazil examples |
| Production-period radiation / DLI | Low sun → sugars / drying |
| Climate variability | Interannual spread (p10/p50/p90) |
| Winter mean / coldest-month mean | System class support |

**Fog:** not in the first derive list. LinkedIn / India IGP fog can matter; Paul first said no, then yes it can. Research later. Do not block v1.

Paul will **hand over the R functions** he already used for Papanduva. Prefer those over reinventing thresholds.

### Spatial units

- User gives a point.
- We map to **nearest region we actually stored** (county in the US; municipality / admin elsewhere).
- Waldo example from the first session: Waldo is in **Alachua County** — return the **county pack**, not only the pin.
- A radius is allowed if there is no county grid; it does not have to be pixel-precise.

### Where the weather lives

- Download on the **university machine (Eduroam / campus Ethernet)**, not a personal phone plan, not the Cursor cloud VM (the cloud agent cannot see Eduroam).
- Resume-safe job; `tmux`; disable sleep; prefer **wired** for anything large.
- NASA POWER daily needs no account and is enough to start.
- Copernicus CDS (ERA5 / AgERA5) needs a key; only when we decide hourly reanalysis is worth it.
- Check campus acceptable-use if anyone proposes a multi-TB scrape.

### Honest size (do not promise TBs in two days on Wi-Fi)

| Pack | Approx. size | Fits a campus weekend? |
|---|---|---|
| Catalog / trial points, daily 10–15 y | tens–hundreds of MB | Yes |
| Global ~1° land + blueberry belts, daily | ~several GB | Yes |
| Global 0.25° daily 10 y | ~30 GB | Maybe if Wi-Fi holds |
| ERA5-Land hourly **global** 10 y | 5–20 TB | No on Eduroam |

v1 needs the **GB** pack, not the TB cube.

---

## 8. Production windows

**Output, not input.** Do not ask for market week in v1 (the earlier analogue UI did; Paul said that will not work — we *recommend* the window; tunnels can shift it).

Three stages, always:

1. **Planting**
2. **Flowering**
3. **Harvesting**

They vary by location (Florida north vs south is not one calendar; Brazil is a season flipped vs Michigan).

Paul: derive from the same weather + habit. Example logic already used: last frost, chill satisfaction, GDD after chill; evergreen flowers in the cool season. Tunnels can pull bloom ~30 days and let someone hit a high-price window (expensive, but Waldo tunnel fruit survived when the open field was wrecked).

Validate locally. Papanduva calendars were “planning estimates from modeled chilling and heat thresholds.”

---

## 9. Production systems (the clock)

Three clocks — a **gradient**, not three species:

| Clock | Meaning |
|---|---|
| **Deciduous** | Leaves drop; needs winter chill to flower cleanly. Colder end of the Florida → Carolina belt. Still a gradient (freezing vs “just cold”). |
| **Semi-evergreen** | Transitional. Partial / facultative dormancy. ~**150–300 chill hours** in Paul’s original classifier. North-central Florida / Ocala mental model. |
| **Evergreen** | Leaves stay; chill almost irrelevant; winter light and freeze-on-early-bloom matter. South / central Florida. |

**v1 rules (provisional until Gerardo + Patricio lock them):**

- Original Papanduva rule: 150–300 h → semi-evergreen; below that evergreen-ish; deep chill → deciduous.
- Revised Papanduva rule: WorldClim annual ≥ **300 h** → deciduous.
- These **disagreed on the same pin**. The product must show the rule used and the uncertainty. Field check: leaf retention, budbreak uniformity.

**Open ground:** the derived clock **filters genotypes** (if land is evergreen, recommend top evergreen lines, not the best deciduous).

**Tunnels / greenhouse:** grower can run evergreen or semi-evergreen in a deciduous climate (they already do this at Waldo). Early bloom is protected. Chill is **not** restored by plastic.

**Pots:** drainage; heavy rain is less of a root problem. Berries can still split unless rain is also excluded. If pots + tunnels, Paul: you can recommend **whatever the model likes** — clock filter is soft.

Hydrogen cyanamide (HCN) rewrites chill; not a v1 user control unless Patricio wants it.

---

## 10. Management layer (user + defaults)

**Default:** open field + ground.

**User can change** to any of the four combinations in §4.

**If ground:** pull **soil** for that coordinate (pH, drainage / clay, organic matter as available — SoilGrids or better). Blueberry soil is acidic; pine bark is common in Florida. pH / Phytophthora matter on soil, not on substrate.

**If pots:** skip GIS soil. Jump to window + genotype.

**Irrigation:** assume it exists for drought recommendations; we do **not** check water rights. Call that out.

**Infrastructure cost:** tunnels + pots = most expensive, most control. The tool should say which risks go away, not hide cost.

Covers (net / woven / LDPE) change UV, PAR, rain-crack; they do not restore chill. Optional after v1.

---

## 11. Risk layer (how to talk about risk)

Risks are **targeted** and **window-specific**. Annual rainfall is the wrong number. Harvest rainfall is the right one.

**Within a window ≠ comfortable.** Paul’s metaphor: a 51 next to a 90 is still a problem. Borderline chill or borderline harvest rain is a **watch**, not a pass.

Score against a **reference belt we already grow** (Florida → North Carolina southern highbush gradient), plus year-to-year p10/p50/p90.

**Always-on list for v1**

1. Harvest rainfall / rain-crack (highest priority in every Paul report)
2. Flower / bloom freeze
3. Season dry spell / drought
4. Chill shortfall (if deciduous or semi)
5. Heat at fruit (if present)
6. Low solar / DLI in fruit fill (if present)
7. Disease-favorable wet-warm hours in bloom and harvest

**Status language:** comfortable / borderline / concerning / extreme — or Paul’s normalized % vs reference mean + SD. Prefer **one** scheme once his R code is in.

**Management text examples (from Papanduva):** drainage, open canopy, timely harvest, fruit drying, preventive disease sprays, irrigation that does not waterlog.

Tunnels collapse freeze and harvest-rain scores. Pots collapse drainage. State that explicitly.

---

## 12. Genotype layer

### What we recommend

- **Commercial cultivars Patricio still stands behind** (Albus, Falcon, Sharper, Optimus appeared in the Brazil work; the live list is **his**).
- **Advanced selections / Stage 4s** he wants in the tool (22-0287, 22-0321, … were in the summary — treat as examples until he confirms).

### What we do not recommend

- Old cultivars he has better replacements for.
- Seed of a cultivar (clones are what UF licenses; seed segregates). Out of scope for the tool, but that is why “genotype” means a **named clone / selection**.

### Required tags on every line (Patricio + program data)

- Production-system adaptation: deciduous / semi-evergreen / evergreen / more than one
- Whether tunnels change that
- Rain-crack / split tendency if known
- Heat sensitivity if known
- Typical harvest window if known
- Recommendable: yes / no

**How they know the clock today:** flowering time and leaf behavior in the breeding program, not a global G×E table. Patricio sits down and names the list. Diego attaches pedigree / genomics.

### Model constraint (Paul)

Do **not** train or serve predictions for the entire historical program. Restrict the model to the **underranged / tagged** set so the model stays small and we never recommend a line nobody will send.

### Data we will need (not public)

- Yield and fruit quality (Brix, TTA, firmness, size) in UF trials
- Genomic matrix + pedigree (Diego)
- Which sites those data came from (mostly Florida today — that **limits** global transfer; Paul said this out loud)
- Collaborator results: where licensed material already worked, and in which system (asterisk for Patricio)

Until that exists, the only honest genotype layer is a **rule-based** match (chill envelope × rain-crack × heat × allowed clock). Do not fake reaction-norm numbers.

---

## 13. Prediction layer

### Two model tracks (Paul)

1. **Reaction-norm model he already has** (Jarquín-style: genomics × environment). Used for Papanduva trait panels.
2. A **second / “dependent” model** Rohit may help build. Deploy whichever validates better.

### How it is used in the app (not live globe predict)

1. Offline: sample environments (Florida first, then US, then belts, then globe) at county / radius grain.
2. Offline: predict traits for the **allowed genotype list** in each sample.
3. Offline: collapse traits to **one selection index**.
4. Store: top 5–10 genotypes **per (region × production system × management)**.
5. Online: derive system + risks + window from weather; **look up** the bucket; if ground, keep only the matching clock; if pots+tunnels, take the raw top ranks.

Training on Florida and predicting the globe is **weak**. Say so. Patricio’s next step after the tool exists: put a few genotypes in several Florida (and later foreign) environments and **validate**.

### Environmental matching (also in the diagnose report)

Even in v1, show closest UF / SE US **named** environments (Waldo, Citra, Alachua…) so a breeder can think. That is comparison, not the genotype engine.

Kernel (for prediction) and long-term phase-aligned climate (for geography) are **different** in Paul’s summary. Do not mix the scores.

---

## 14. User workflow (v1)

1. Enter location (map click or lat/lon).
2. Choose management (one of four; default open + ground).
3. Run recommendation.
4. Review: system, window, top risks, ranked genotypes, closest UF analogs, data-trust note (POWER daily vs fallback vs station).

**Copy / tone:** recommendation, pilot, book the flight, walk the land. Never “this will yield like Waldo.”

---

## 15. Phased build (from *What is needed to build it*)

| Phase | Name | What “done” means |
|---|---|---|
| **1** | Data integration | 10–15 y base weather in a queryable store; nearest-county lookup; soil extract if ground |
| **2** | Trait and environment modeling | Paul’s derive functions: risks, windows, system classifier; management modifiers |
| **3** | Pilot validation with breeder data | Patricio’s list + Diego matrix; reaction-norm / second model; Florida trials |
| **4** | Breeder-facing platform | Dashboard: the four outputs; later, recommend-where |

**Support requested (slides):** approval, data access, trial support, computing, cross-team (Patricio, Gerardo, Diego, Paul, Rohit).

**Hardest part (Paul):** getting **good** weather, not the formulas. Formulas already exist in his code.

**Annual maintenance:** refresh base weather; add new genotypes and retrain the index. Not every click.

---

## 16. Information we still need from people

Do not invent these.

### From Rohit (ops)

- [ ] Clone this repo on the **university server** and run the weather download there (Eduroam).
- [ ] Confirm audience: Patricio / collaborators only for v1?
- [ ] Paul’s R project (scripts, the 13 reference environments, exact formulas).
- [ ] The fourth report if it exists.

### From Patricio

- [ ] Recommendable cultivars vs retired names.
- [ ] Stage 4 / advanced selection list and clocks (including under tunnels).
- [ ] Confirm v1 = **this pin only** (no similar-location search yet).
- [ ] Collaborator sites and systems that already work.
- [ ] Florida validation trial plan (few genotypes × several environments).

### From Paul

- [ ] R derive functions (risks, windows, system, analog scores).
- [ ] Definition of the SE US reference panel and “consensus similarity.”
- [ ] Which chill model is official (hours vs portions vs WorldClim proxy) after the Papanduva contradiction.
- [ ] Reaction-norm training objects (or a handover with Diego).

### From Gerardo

- [ ] Final chill / freeze / harvest-rain / DLI cutoffs.
- [ ] What tunnels actually change, and at what temperature.
- [ ] What pots mitigate, and how much rain is still too much.

### From Diego

- [ ] Pedigree and genomic matrix for the allowed list.
- [ ] Which trial sites are usable.

---

## 17. Open contradictions (must not hide)

1. **Papanduva system:** semi-evergreen (209 h hourly) vs deciduous (368 h WorldClim ≥ 300). Same author, two reports.
2. **Harvest rain mm** and analog scores differ between original and revised (206 vs 174 mm; Waldo 71 vs 64).
3. **Flower-freeze** 4.2% vs 0%.
4. **100 h** chill gate vs **150–300 h** semi band vs **300 h** deciduous WorldClim rule.
5. First long session included “recommend similar places” as a first-class mode; the later session said **build this-pin first**, similar locations later.
6. Earlier analogue prototype asked for market week and a full cover menu; current spec is **two inputs** and a **recommended window**.
7. Hourly globe vs lean daily: both were discussed; the locked decision is **lean base data + derive**, 10–15 years, campus download.

When code starts, pick one rule, cite it, and keep the other as a sensitivity flag.

---

## 18. Claims we may and may not make

**May**

- This climate sits inside / on the edge / outside the SE US reference envelope we used.
- These are the derived window and the top weather watches.
- These genotypes are the best **current list** match for this clock and management; trial them.
- Tunnels/pots change which risks still apply.
- Data source and trust (dated daily vs monthly climatology vs fallback).

**May not**

- This site will grow like Waldo / Michigan.
- Guaranteed chill hours or yield.
- Commercial success probability.
- “AI is better than the weather service.”
- Recommend a line Patricio did not put on the list.

---

## 19. Validation Patricio asked for

After the pipeline exists: take a **few genotypes**, plant them in **several Florida environments**, collect data, compare to what the tool said. That is the first real skill test. Climate analogues and reaction-norms trained in Florida will overstate skill if we only score them on Florida.

Leave-one-region and leave-one-cultivar tests are useful later; they are not a substitute for those trials.

---

## 20. Prior work (parked — do not start from it)

Saved on GitHub so nothing is lost. This branch does **not** continue that UI.

| Branch | What is there |
|---|---|
| `main` | Florida blueberry **weather risk** prototype (tonight freeze, 7-day, season). Different product. |
| `cursor/blueberry-analogue-2206` | Global **farm-to-farm analogue** shortlist (303 sites, MapLibre, variety cards, CCAFS + gates). |
| `cursor/recommendation-engine-2206` | Diagnose API, SQLite daily store, campus POWER downloader, dual-mode UI. Useful as **reference**, not as the new trunk. |

Do not copy cached `data/analogue/climatology` or synthetic 2018 expansions forward. Dated winters will be downloaded again.

---

## 21. Glossary

| Term | Meaning here |
|---|---|
| **SHB** | Southern highbush blueberry |
| **NHB** | Northern highbush |
| **Chill hours** | Hours in a cold band (0–7.2 °C or UF 32–45 °F). Different from portions. |
| **Chill portions** | Dynamic Model units |
| **Production system / clock / habit** | Deciduous / semi-evergreen / evergreen |
| **Structure** | Open field vs tunnel/greenhouse (collapsed) |
| **Media** | Ground vs pots (pots ≈ substrate) |
| **Selection index** | One number collapsing several traits |
| **Reaction norm** | Genotype performance as a function of environment (often with genomics) |
| **Stage 4 / advanced selection** | Not a released cultivar yet; may still be recommended for trials |
| **Reference envelope** | Cloud of SE US / UF climates we treat as “known” |
| **Diagnose** | This coordinate |
| **Recommend where** | Other places (later) |
| **Eduroam** | Campus Wi-Fi — where the weather job should run |

---

## 22. First implementation slice (when coding starts again)

Order Paul and Rohit already agreed:

1. Query / store 10–15 year base weather (university server).
2. Port Paul’s derive functions: risks, window, system.
3. Wire the two inputs and four outputs (no extra chrome).
4. Only then: Patricio list + Diego data + reaction-norm / second model + lookup table.
5. Florida validation trials.
6. Optional: similar-location search.

Until step 1–2 exist, do not build another map UI on top of the old analogue.

---

*End of requirements. If a meeting changes a rule, edit this file. Do not leave a second spec in chat.*
