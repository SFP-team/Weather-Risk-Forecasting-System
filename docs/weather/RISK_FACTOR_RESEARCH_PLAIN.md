# Weather risks for blueberries — plain-language summary

*This is the easy-to-read version. The full technical version, with every research paper linked, is in `RISK_FACTOR_RESEARCH.md`.*

Date: 15 September 2026.

## What this is

The tool looks at the weather at a place and works out things like: when the plant will flower, when the fruit will be ready, and what weather could ruin the crop. This note answers two simple questions:

1. Are the weather rules we already use correct?
2. What else should we be watching?

We did two things to find out: we read the science, and we tested our own weather data. **Nothing here has been built yet.** It's a to-do list with reasons.

A few words used below:

- **Blueberry types:** *southern highbush*, *rabbiteye*, and *northern highbush*. They behave differently, so a rule that fits one may not fit another.
- **Chill:** the amount of cold a plant needs over winter before it will wake up and flower properly. Too little chill and the plant flowers poorly or not at all.
- **Bloom:** flowering.
- **Weather box:** the free global weather data comes in boxes about 55 km wide. Every farm inside the same box gets the same weather record. So our answers are area-level, not field-level.

## The short version

**What we already get right:**

- We use hour-by-hour temperature for the cold calculations, and daily totals for rain and heat. That is the correct way to split it.
- Our damage temperatures are close to the research: frost kills open flowers at about −2 °C, fruit starts cooking above 32–35 °C, and a 10 mm day counts as heavy rain.
- We count how many of the last 15 winters had a given problem, and we show how confident we can be. That is honest.
- For warm places with almost no winter cold, we do **not** invent a flowering calendar out of thin air. That is the right call.

**What we got wrong, worst first:**

1. **How we count winter cold is off.** We count every hour below 7.2 °C, right down through freezing, from November all the way to May. Everyone else counts only the hours between 0 and 7.2 °C, and only from October to February. Freezing-cold hours don't actually add chill, and spring hours come too late to matter. Our method over-counts Georgia's cold by a lot. Even worse, counting "cold hours" ranks warm places wrongly (see the test below). We should switch to a better cold measure called **chill portions**.
2. **Our "chill needed" number is far too low.** We assume a plant is satisfied with 50 hours of cold. In reality no commercial variety needs less than about 150 hours, and most need 200–650. Because our number is so low, the plant's "clock" starts too early, and every date after that — flowering, harvest — comes out wrong.
3. **Our flowering date has no source.** We add a fixed amount of warmth after the cold is met to predict flowering, but that fixed amount was never based on anything. The published blueberry numbers are different, and they count warmth from 1 January, not from the cold date.
4. **We use one harvest gap for all varieties.** Rabbiteye takes longer from flower to ripe fruit than southern highbush. Using one number for both is wrong.
5. **Our disease rule is too crude.** It flags a day as risky if it's mildly warm, humid, and had any rain at all. But "any rain" on a 55 km box is almost every day, and different diseases like different temperatures and need the leaves to stay wet for a certain number of hours. It needs to be redone per disease.
6. **We only check frost during full bloom.** The most fragile stage is actually the young green fruit just after the flowers drop — it dies at around 0 °C. Swelling buds before bloom also get hurt by hard late-winter freezes. We miss both. How long the cold lasts matters too, not just how cold it got.
7. **A few other measures don't work** (a dryness-of-air average that never reaches a meaningful level, and a "longest dry spell" that treats a dry winter month — when the plant needs little water — the same as a dry spring month during fruit fill).

## The cold test we ran

We compared three ways of scoring winter cold at our 18 measured locations. The important columns:

- **Our count** — the way we do it now (hours below 7.2 °C, Nov–May).
- **Standard count** — the way everyone else does it (hours between 0 and 7.2 °C, Oct–Feb).
- **Chill-portion score** — the better method, which correctly credits cool-but-not-freezing hours.

| Place | Our count (hrs) | Standard count (hrs) | Chill-portion score |
|---|---:|---:|---:|
| Georgia / Alma | 801 | 603 | 44.7 |
| Valdosta | 749 | 569 | 42.4 |
| Homerville | 694 | 533 | 39.9 |
| Folkston | 577 | 460 | 36.2 |
| Waldo | 420 | 346 | 28.5 |
| Citra | 350 | 296 | 23.4 |
| Wild Goose | 274 | 238 | 19.7 |
| H & A | 210 | 186 | 17.0 |
| Frogmore | 134 | 127 | 17.8 |
| Clear Springs / Astin NE | 173 | 155 | 14.1 |
| Dole | 142 | 126 | 11.8 |
| River Valley / Wauchula | 132 | 120 | 11.1 |
| Barben / Sebring | 116 | 104 | 9.3 |
| Arcadia | 86 | 80 | 8.3 |
| PF Berry | 87 | 79 | 7.3 |
| Astin East | 40 | 40 | 8.7 |
| Okeechobee | 30 | 30 | 3.9 |
| Papanduva (Brazil) | 199 | 183 | 26.1 |

What this shows, in plain terms:

- **Our method over-counts.** At the Georgia sites our count is 100–200 hours higher than the standard count, because we include freezing hours and spring hours that don't count.
- **The data is trustworthy where it's warm, and runs a little warm where it's cold.** Our standard count at the Barben box (104 hours) matches the nearby weather station's published average (108). But at Waldo/Citra we get about 300–350 hours where the station reports around 500 — the free data runs about 1 °C too warm at night, so it slightly under-counts cold in cooler places. Keep that in mind for any cold-based decision.
- **This is the clincher.** Look at Papanduva in Brazil: by the "cold hours" way it looks like central Florida (183 hours, similar to Citra). But by the better chill-portion score it looks like Waldo (26 vs 28.5) — a much colder place for a plant. The reason: Papanduva's cool weather sits at 7–12 °C, which "cold hours" throw away but chill portions correctly count. So calling Papanduva a low-chill site is a mistake caused by the old method. **This is why we should switch methods, and it changes the answer for a real location.**

## What else we should watch, by season

Everything below can be worked out from weather data we already have.

### Winter

- **A proper cold score** (chill portions) and a "reliable-cold" figure — the amount of cold you can count on in a poor winter, not just an average year.
- **Too-warm winter days** that cancel out chill (hours above about 21 °C in mid-winter).
- **Warm spell then hard freeze.** A few warm days wake the plant up, then a freeze kills the softened buds. This caused big Georgia losses in 2017. Worth flagging directly.

### Bud swelling to flowering

- **Frost at every stage, not just full bloom**, with the right temperature for each stage and how long the cold lasted.
- **Can the frost even be protected against?** Sprinklers only help in a still, radiation-type frost; they don't help in a windy, dry cold blast. Worth telling the grower which kind it was.
- **Good pollination days.** Bees need it warm enough (above ~15 °C), calm, and not raining. Several bad days in a row during bloom loses a batch of flowers. We measure none of this today, and it matters a lot.
- **Heat during bloom.** Above about 30 °C blueberry pollen struggles; at 35 °C it basically stops.

### Fruit growing

- **Heat on green fruit vs ripe fruit** (different limits for each).
- **Sun-scald risk** — a berry in full sun runs much hotter than the air.
- **Water shortage during fruit fill**, measured properly as rain minus what the plant actually uses (which changes through the season), not just "days without rain".
- **Waterlogging** after very heavy rain, which rots roots.
- **Fruit-rot risk**, based on how long leaves and fruit stay wet and at what temperature.

### Harvest

- **Rain that splits ripe fruit** (a dry spell followed by a downpour is the worst).
- **Wet picking days** that cause rot.
- **Spotted-wing fly pressure** — a fruit fly that peaks right at southern-highbush harvest time.

### After harvest (affects next year)

- **Late-summer heat**, which quietly reduces next year's flower buds.
- **Water shortage** in the weeks after picking.

## What to do first

1. Fix the cold measure: add chill portions and the standard 0–7.2 °C count, over the right months.
2. Fix flowering and harvest timing: use realistic "chill needed" numbers per variety, base flowering on warmth from 1 January, and use different harvest gaps for the different blueberry types.
3. Add stage-by-stage frost, including whether it was protectable and the warm-then-freeze pattern. This is the main problem for south Georgia.
4. Add good-pollination-days and bloom-heat — cheap to compute and currently a blind spot.
5. Redo the disease rules around how long things stay wet.
6. Add the proper water-use calculation.
7. Build a management-based calendar for warm, evergreen sites so they get useful risk numbers too.
8. Add the fruit fly and the after-harvest heat measures.

Each of these should be added as a **new version alongside the old one**, so we can compare results and never lose what we had.

## What we still don't know

- Most exact numbers come from studies on other blueberry types or other crops, then borrowed. The best matches for our southern varieties often don't have their own published study.
- No one has published the exact cold requirement, in the better units, for any of the varieties we care about.
- There is no published rain amount that reliably splits blueberry fruit, no exact freeze dose-response, and no blueberry-specific air-dryness limit.
- The free weather data runs about 1 °C warm at night and smooths out local downpours, so every number should be read as an area estimate, and we should eventually correct it against real stations.

Before any of this is treated as a real evaluation, the science lead still needs to decide the cold definition (this test now argues for chill portions), which varieties to run, and what flowering/harvest dates we should expect at a couple of known sites so we can check our numbers against reality.

## Where the numbers come from (a few key sources)

- University of Florida chill, freeze and frost guidance: https://ask.ifas.ufl.edu/publication/HS216
- University of Florida evergreen vs deciduous growing systems: https://ask.ifas.ufl.edu/publication/HS1362
- The better cold model (chill portions) explained: https://pmc.ncbi.nlm.nih.gov/articles/PMC3077742/
- Southern-highbush flowering-timing study: https://journals.ashs.org/view/journals/jashs/140/1/article-p38.xml
- Georgia freeze-protection guide (stage-by-stage cold limits): https://fieldreport.caes.uga.edu/publications/B1479/commercial-freeze-protection-for-fruits-and-vegetables/
- Heat and pollination study: https://journals.ashs.org/view/journals/jashs/144/5/article-p339.xml
- Fruit-rot risk model: https://www.canr.msu.edu/news/new-blueberry-anthracnose-risk-prediction-model-launched-for-michigan-growers
- Bloom-weather and fruit-set study: https://pubmed.ncbi.nlm.nih.gov/20568598/
- Blueberry water-use figures: https://www.tandfonline.com/doi/full/10.1080/15538362.2010.510419
