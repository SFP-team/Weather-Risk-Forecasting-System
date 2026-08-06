# Risk definitions and crop calendar

Crop-relevant weather risks for Florida blueberry production. Thresholds are **product guidance** for a prototype; final operational numbers need UF/IFAS agronomist review.

Primary references:

- UF/IFAS EDIS HS216 — *Protecting Blueberries from Freezes in Florida*
- FAWN Cold Protection Toolkit
- Florida Blueberry Growers Association materials

---

## 1. Production systems

| System | Where | Weather implications |
|--------|-------|----------------------|
| **Deciduous / dormant** | North-central, parts of central | Chill matters; freeze protection of flowers/fruit is signature risk |
| **Evergreen** | Central & south-central | Leaf disease year-round; chill less central; harvest can start earlier; freeze still matters |

Commercial fresh shipping is dominated by **southern highbush (SHB)**. Rabbiteye is more common northward / later U-pick.

### Approximate chill (hours &lt; ~45°F — model-dependent)

| Class | Examples | Chill (approx.) |
|-------|----------|-----------------|
| Early / evergreen-adapted | Snowchaser, Avanti, Chickadee, Kestrel, Arcadia, Optimus | ~100–200 |
| Workhorse / mid | Emerald, Jewel, Star, Windsor, Farthing | ~150–400 (Star often higher) |
| Rabbiteye | Various | ~300–600 |

Treat as **planning bands**, not hard engineering limits. Dynamic Model (chill portions) better handles warm-spell cancellation than simple chill hours.

---

## 2. Crop calendar (Florida SHB — typical north-central / central)

Timing shifts ~2–4 weeks earlier southward and under evergreen management.

| Month | Phenology & ops | Weather-sensitive decisions |
|-------|-----------------|------------------------------|
| Oct | Growth slowdown; hardening | Early freezes on soft tissue |
| Nov | Dormancy setting | Soft growth freezes; leaf disease (evergreen) |
| Dec | Chill accumulation; pruning | Chill tracking |
| Jan | Bud swell → early bloom (ultra-early/evergreen); freeze season starts | Nightly frost ops |
| Feb | Peak bloom for many SHB; bees; fruit set | Highest freeze + Botrytis risk |
| Mar | Fruit set / green fruit; harvest starts south | Freeze risk through mid–late March |
| Apr | Main harvest north-central | Heat, rain-split, rot, labor |
| May | Finish SHB; prices fall | Summer disease; drought if dry |
| Jun–Aug | Vegetative growth; flower bud initiation later | Heat, humidity, hurricanes |
| Sep | Canopy; flower bud set | Leaf disease for next year’s buds |

**Market window:** Value concentrates in **March–early May** fruit.

---

## 3. Chill

### Simple Chilling Hours Model (MVP)

- Count hours when temperature is between approximately **32°F and 45°F**.
- Below freezing: generally **no accumulation**.
- Temperatures **above ~70°F** mid-November to mid-February may **negate** some accumulated chill (Dynamic Model handles this better).

### Product metrics

| Metric | Description |
|--------|-------------|
| Season-to-date chill hours | Running total Nov–Feb (region-configurable) |
| Chill vs cultivar target | e.g. 210 / 300 hours |
| Chill shortfall probability | Seasonal head: P(end-of-window chill &lt; target) |
| Warm-spell deharden flag | Multi-day warmth advancing buds mid-winter |

### Decision lead times

| Decision | Horizon |
|----------|---------|
| Track chill / cyanamide discussion with Extension | Weeks–seasonal |
| Cultivar mix / system planning | Seasonal–annual |

---

## 4. Freeze / frost

**#1 commercial risk** for Florida SHB during bloom and early fruit.

### Stage-aware vulnerability (illustrative)

| Stage | Approximate critical guidance | Notes |
|-------|------------------------------|--------|
| Fully dormant buds | Survive much colder (plant survival rarely the issue) | Hardier mid-winter |
| Expanding buds | Progressive loss of hardiness | Stage-dependent |
| Open flowers & small fruit | Tissue kill often discussed ~**26–28°F**; economic risk higher | Young fruit highly sensitive |
| Practical protect start | Many ops near **~30°F** shelter / open-sky rules | Low dew point → start earlier (e.g. ~34°F open-sky) |

**Important:** Lethal temperatures by floral stage for southern highbush are **not as fully tabulated** as Michigan northern highbush tables. UI must present **guidance ranges**, not false precision. Confirm with field thermometers and IFAS.

### Physics that must appear in the product

| Factor | Product implication |
|--------|---------------------|
| **Dew point** | Low Td → faster drop, worse nights; start earlier |
| **Wind** | Unprotected: mixing can help; **with irrigation**: evaporative cooling & poor coverage → may exceed system |
| **Radiation freeze** | Calm clear nights; frost pockets; field colder than FAWN |
| **Advective freeze** | Wind-driven cold mass; protection harder |
| **Pine bark beds** | Can run colder at flower height on calm dry nights |

### Operational freeze events

| Event ID | Suggested definition | Action |
|----------|----------------------|--------|
| `FREEZE_PROTECT` | Forecast/obs path toward protect thresholds with stage open to damage | Prep/run irrigation |
| `FREEZE_KILL_RISK` | Stage-critical temps likely breached for meaningful duration | Loss expectation; buyer/insurance comms |
| `ADVECTIVE_FREEZE` | Freeze + wind above system design (e.g. ≥8–10 mph class) | Beyond-system / choose blocks |
| `POST_FREEZE_DISEASE` | Protect night or freeze + wetness during bloom | Botrytis follow-up weather flag |

### Start / stop rule patterns (productize carefully)

1. Do not run when temp–wind combo exceeds system design (capacity table).
2. Calm nights: often start when open-sky thermometer in coldest spot reaches ~32°F; if Td very low, start earlier (~34°F class guidance).
3. Never shut off before ice is melting vigorously.
4. Very dry/windy mornings may require longer run / higher shaded air temp before stop.
5. Afternoon pre-wet of ground is an optional strategy on borderline nights (fuel/water/disease tradeoff).

### Decision lead times

| Decision | Horizon |
|----------|---------|
| Run irrigation **tonight** | 6–48 hours (hour-by-hour) |
| Staff / diesel / system prep | 3–7 days |
| Seasonal freeze-night budgeting | 1–3 months (counts/odds only) |

---

## 5. Disease pressure (weather risk only)

Not a pesticide recommendation engine. Output **infection-risk weather** and spray-window suitability; link to IFAS IPM.

| Disease | Drivers | Window |
|---------|---------|--------|
| **Botrytis** blossom blight / gray mold | Cool–moderate temps (~60–75°F), rain, high RH, extended wetness; freeze injury + wetness | Bloom (Feb–Mar) |
| **Anthracnose** fruit/leaf | Warm + wet; often long wetness (~8+ h near ~77°F class models) | Bloom → harvest |
| **Leaf spots** (rust, Septoria, etc.) | Warm humid summers; canopy wetness | Summer–fall (critical evergreen) |
| **Phytophthora** root rot | Saturated soils + warmth | Rainy season / over-irrigation |

| Event ID | Suggested signal |
|----------|------------------|
| `BOTRYTIS_BLOOM` | Bloom + extended wet cool hours |
| `ANTHRACNOSE_RISK` | Wetness duration × favorable temp |
| `POST_FREEZE_DISEASE` | After overhead protect nights |

**Leaf wetness:** FAWN does not measure it directly. MVP: derive from RH + precip rules; later paid APIs or sensors.

---

## 6. Drought, heat, harvest

| Event ID | Suggested definition | Action |
|----------|----------------------|--------|
| `DROUGHT_STRESS` | Multi-day water balance deficit vs stage demand (fruit fill often ~1.0–1.5 in/week class demand) | Increase irrigation frequency |
| `HEAT_HARVEST` | Multi-day max ≥90–95°F during pick | Labor, early harvest, cooling |
| `RAIN_SPLIT_HARVEST` | Ripe fruit + heavy short rain (e.g. ≥0.5–1.0 in) | Accelerate harvest |
| `EXCESS_WET_ROOT` | Multi-day saturation | Cut irrigation; Phytophthora risk |
| `TROPICAL_SYSTEM` | Named storm track impacts | Pre-storm harvest, drainage, equipment |

Pine bark beds hold little water—**frequent short** irrigations matter more than deep infrequent ones.

---

## 7. Full event catalog (MVP priority order)

| Priority | Event | MVP? |
|----------|-------|------|
| P0 | `FREEZE_PROTECT` | Yes |
| P0 | `ADVECTIVE_FREEZE` / beyond system | Yes |
| P0 | `CHILL_SHORTFALL` (seasonal) | Yes |
| P1 | `POST_FREEZE_DISEASE` / `BOTRYTIS_BLOOM` | Lite in MVP |
| P1 | `RAIN_SPLIT_HARVEST` | Yes if harvest season demo |
| P2 | `ANTHRACNOSE_RISK` | v1 |
| P2 | `DROUGHT_STRESS` | v1 |
| P2 | `HEAT_HARVEST` | v1 |
| P3 | `TROPICAL_SYSTEM` | v1+ (ingest NHC/NWS alerts) |

---

## 8. Phenology gating

Every freeze/disease risk score should be multiplied or filtered by **block phenology**:

| Stage code | Label |
|------------|-------|
| `DORMANT` | Fully dormant |
| `SWELL` | Bud swell |
| `TIGHT_CLUSTER` / `PINK` | Pre-open stages (refine with Extension) |
| `OPEN_BLOOM` | Open flowers |
| `PETAL_FALL` | Petal fall |
| `GREEN_FRUIT` | Small fruit |
| `HARVEST` | Ripe fruit present |

MVP: **manual stage entry** per block. Later: simple chill + heat accumulation proxy.

---

## 9. Decision lead-time matrix

| Decision | Ideal horizon | 2–3 month outlook useful? |
|----------|---------------|---------------------------|
| Run freeze irrigation tonight | 6–48 h | No (only seasonal counts) |
| Staff/diesel prep for freeze week | 3–7 d | No |
| Fungicide before bloom wet spell | 24–72 h | No |
| Irrigation scheduling | 1–7 d | Seasonal reservoir only |
| Harvest crew planning | 3–14 d | Rough volume only |
| Chill / cyanamide / pruning intensity | Weeks | **Yes** |
| Cultivar mix / insurance / system | Seasonal | **Yes** |
| Hurricane readiness | 3–7 d track; seasonal activity | Seasonal yes |

**Product implication:** 2–3 month forecasts are a **planning layer**. Hours-to-10-days forecasts are the **core willingness-to-pay layer**. Ship both; market both honestly.

---

## 10. Advisory copy pattern

Every risk card:

1. **Weather fact** (short, sourced)
2. **Crop meaning** (stage-aware)
3. **Suggested action** (checklist)
4. **Confidence** (high / split forecast / sensor vs model conflict)
5. **Disclaimer** when science is incomplete

Example:

> **Weather:** Calm, dew point 24°F, forecast 29°F.  
> **Crop:** Open bloom can run colder than the shelter; dry air is worse.  
> **Action:** Start when open-sky thermometer in coldest spot hits 34°F. Don’t shut off until ice is melting hard.  
> **Source:** FAWN Citra · NWS · guidance range, not a guarantee.
