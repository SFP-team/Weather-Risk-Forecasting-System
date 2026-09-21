# Supervisor review: River Valley walkthrough (recorded 2026-09-21)

Paul reviewed the dashboard on the River Valley preset after the 2026-09-15 growing-cycle and risk-research work. This note records decisions only. The spoken review is a private input and is not reproduced.

## Governing rule

A weather exposure is a **risk factor** only if both hold:

1. Its stage window overlaps the site's predicted production window (planting → flowering → harvest).
2. It happens often enough across the analysed winters (he used about half of winters as the example threshold; make it a profile constant).

Everything else is not shown as a risk. It may stay in an expandable "checked, not a risk here" list for audit.

Applied to River Valley: chill is met (not a risk); flowering freeze occurs in fewer than half the winters (not a risk); heat and heavy rain fall after harvest ends in early April (not risks); the whole-cycle dry-spell number is uninformative; **disease** (humidity plus rain during flowering and fruit) is the real risk and is not ranked today.

## Add

- **Disease as a ranked risk** (humidity and rain during flowering/fruit; the existing `disease_days` metrics exist but are unranked).
- **Pollination-unfavourable days** in flowering: cold (Tmax below ~15 °C) **and** dry (no rain). Cold with rain is acceptable; cold without rain means overcast. Report count and fraction of winters; set the "how many is bad" threshold from the distribution across sites.
- **Warm mid-winter hours**: hours above 21 °C mid-November to mid-February (hourly cells; daily Tmax fallback). Rare but include.
- **Berry-stage freeze**: freeze on set fruit, next to the existing flower freeze.
- **Stage-specific dry spell** (flowering, fruit) instead of whole-cycle.
- **Planting window** from his R code (`southern_brazil_blueberry_climate_analogs.R`), required as a **single** window chosen to align with flowering and harvest, not computed independently; his current code yields multiple windows for some sites.

## Do not prioritise

Frost at every bud stage, frost-protection feasibility, wet-picking rot (fans), post-harvest heat and drought (crop already sold; then pruning), spotted-wing drosophila, sun-scald, waterlogging. These are either management-layer items or "you would not plant there" screens, not field risk factors.

## Keep

Rain splitting ripe fruit at harvest (most important harvest risk). Heat during fruit development only when inside the window; minor when irrigated.

## Sequencing

Field risks first. The management layer (tunnel, pots) is applied afterwards and removes some risks. Genotype selection follows the production-system label: where freezes during flowering are frequent, early-flowering genotypes are excluded rather than flagged.

## Still open

- Chill method: chill hours versus Dynamic Model chill portions (the 2026-09-15 data check argues for chill portions; Papanduva changes class).
- His risk factors came from his own experience rather than a specific paper; the research catalogue is supporting evidence, not his source.
- Pre-registered expected system, bloom and harvest for the 18 panel sites.
