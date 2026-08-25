# Blueberry Analogue skill sheet

## Claim

The claim under test is **cycle can complete and stage risk is close**, not yield or packout, and not "this site will grow like Michigan."

Presence of blueberries only tests the first claim, and weakly.

## What we may say

- Belt reconstruction recall@8 of same-class neighbors in the same region: **0.46** across 25 regions (Margins 70% shape).
- Leave-one-region-out recall@8 of same-class successes *outside* the held-out region: **0.87** across 26 regions. Neighbors in the query region are hidden.
- If phenology kills known failures that Baseline-0 still likes, we may say **more transferable than climate distance**.
- If we only have presence inside the training continent, we may say **describes where blueberries are grown in this dataset**.
- We may not say this site will grow like the reference.
- We may not quote Wang & Dong 0.94. That paper is 17 staple crops with no blueberry and no suitability ground truth.

## Baselines

- Baseline-0: CCAFS Analogues-style weighted Euclidean on monthly T/P, seasonal lag.
- Baseline-1: EcoCrop trapezoid for Vaccinium, irrigated and rainfed. Irrigated EcoCrop likes Peru. That is a known lie if the clock is NHB.
- Baseline-2: NZ Landcare-style geometric mean (one chill curve, frost, drainage, slope).

- Known failures scored: 15
- Phenology kill rate on known failures: **0.87**
- EcoCrop irrigated false-positive rate on those failures: **0.87**

| Failure | Nearest T/P success | B0 T/P | EcoCrop | NZ | Pheno sim | Hard fails | Kills |
|---|---|---:|---:|---:|---:|---:|---|
| South of Ocala | us-fl-ocala | 1.00 | 1.00 | 0.92 | 0.55 | 2 | yes |
| Inland Allegan Legacy | us-mi-lawton | 0.99 | 0.00 | 0.02 | 0.54 | 2 | yes |
| Willamette Emerald | us-or-corvallis | 1.00 | 0.55 | 0.76 | 0.54 | 1 | yes |
| Willamette Biloxi | us-or-salem | 1.00 | 0.59 | 0.86 | 0.54 | 1 | yes |
| Willamette Snowchaser | us-or-salem | 1.00 | 0.59 | 0.86 | 0.54 | 1 | yes |
| Ica Ventura | pe-ica | 1.00 | 1.00 | 0.03 | 1.00 | 0 | no |
| Olmos deciduous Duke | pe-olmos | 1.00 | 0.81 | 0.03 | 0.55 | 1 | yes |
| Delhi NCR | mx-culiacan | 0.89 | 0.93 | 0.92 | 0.49 | 1 | yes |
| Lucknow | mx-culiacan | 0.88 | 0.87 | 0.87 | 0.49 | 1 | yes |
| Patna | mx-culiacan | 0.89 | 0.89 | 0.84 | 0.49 | 1 | yes |
| Kanpur | mx-culiacan | 0.89 | 0.83 | 0.03 | 0.50 | 1 | yes |
| Santiago basin | cl-linares | 0.78 | 0.86 | 0.03 | 0.47 | 2 | yes |
| Chiang Mai | mx-zapopan | 0.84 | 1.00 | 0.03 | 0.48 | 2 | yes |
| Miami-Dade | au-sunshine | 0.85 | 1.00 | 0.03 | 0.88 | 0 | no |
| Marquette | us-mi-holland | 0.90 | 0.00 | 0.02 | 0.51 | 1 | yes |

## Belt reconstruction

Shape of the Margins 70% blueberry test: fingerprint one success, recover other same-class successes in that belt. Mixed regions (US-SE is SHB and rabbiteye) are scored class-aware.

| Region | n refs | recall@8 | misses | extra non-success in top |
|---|---:|---:|---:|---:|
| AU-NSW | 2 | 0.00 | 2 | 9 |
| AU-QLD | 2 | 0.00 | 2 | 10 |
| AU-TAS | 4 | 0.50 | 2 | 2 |
| AU-VIC | 2 | 0.00 | 2 | 5 |
| AU-WA | 3 | 0.00 | 3 | 8 |
| BR-S | 2 | 0.00 | 2 | 3 |
| CA-BC | 11 | 0.91 | 1 | 12 |
| CL-CENTRAL | 2 | 0.00 | 2 | 4 |
| CL-SOUTH | 12 | 0.00 | 12 | 10 |
| ES-HUELVA | 12 | 0.83 | 2 | 5 |
| MA-NORTH | 6 | 0.83 | 1 | 7 |
| MA-SOUTH | 3 | 0.33 | 2 | 7 |
| MX-BCN | 2 | 0.50 | 1 | 8 |
| MX-JAL | 4 | 0.00 | 4 | 20 |
| MX-SIN | 3 | 0.00 | 3 | 6 |
| NZ-NORTH | 5 | 1.00 | 0 | 10 |
| NZ-SOUTH | 6 | 0.83 | 1 | 5 |
| PE-CENTRAL | 5 | 1.00 | 0 | 5 |
| PE-NORTH | 8 | 1.00 | 0 | 14 |
| PE-SOUTH | 3 | 0.67 | 1 | 4 |
| PT-ALEN | 2 | 1.00 | 0 | 0 |
| US-MI | 12 | 1.00 | 0 | 12 |
| US-NE | 4 | 0.00 | 4 | 4 |
| US-PNW | 12 | 1.00 | 0 | 12 |
| US-SE | 12 | 0.00 | 12 | 32 |

## Leave-one-region-out

Neighbors in the query region are hidden. Hit if a same-class commercial success from another region is in the top 8. This is known-cultivar / new-region.

| Region | n refs | recall@8 | misses | extra non-success in top | no outside family |
|---|---:|---:|---:|---:|---:|
| AU-NSW | 2 | 1.00 | 0 | 9 | 0 |
| AU-QLD | 3 | 1.00 | 0 | 13 | 0 |
| AU-TAS | 4 | 1.00 | 0 | 4 | 0 |
| AU-VIC | 2 | 1.00 | 0 | 5 | 0 |
| AU-WA | 3 | 1.00 | 0 | 8 | 0 |
| BR-S | 2 | 1.00 | 0 | 3 | 0 |
| CA-BC | 11 | 1.00 | 0 | 1 | 0 |
| CL-CENTRAL | 2 | 0.00 | 2 | 3 | 0 |
| CL-SOUTH | 12 | 0.25 | 9 | 10 | 0 |
| ES-HUELVA | 12 | 1.00 | 0 | 3 | 0 |
| MA-NORTH | 7 | 1.00 | 0 | 6 | 0 |
| MA-SOUTH | 4 | 0.75 | 1 | 7 | 0 |
| MX-BCN | 3 | 0.33 | 2 | 11 | 0 |
| MX-COL | 1 | 1.00 | 0 | 6 | 0 |
| MX-JAL | 5 | 1.00 | 0 | 23 | 0 |
| MX-SIN | 3 | 1.00 | 0 | 6 | 0 |
| NZ-NORTH | 5 | 1.00 | 0 | 10 | 0 |
| NZ-SOUTH | 6 | 1.00 | 0 | 12 | 0 |
| PE-CENTRAL | 5 | 1.00 | 0 | 9 | 0 |
| PE-NORTH | 8 | 1.00 | 0 | 10 | 0 |
| PE-SOUTH | 3 | 1.00 | 0 | 3 | 0 |
| PT-ALEN | 2 | 1.00 | 0 | 0 | 0 |
| US-MI | 12 | 1.00 | 0 | 12 | 0 |
| US-NE | 4 | 1.00 | 0 | 4 | 0 |
| US-PNW | 12 | 1.00 | 0 | 13 | 0 |
| US-SE | 9 | 0.22 | 7 | 25 | 3 |

## Leave-one-cultivar-out

Duke is not Ochlockonee. Report the share of top-8 analogues that stay in class.

| Cultivar | Class | Same-class share@8 | Other-class share@8 |
|---|---|---:|---:|
| emerald | low_chill_shb | 0.65 | 0.35 |
| jewel | low_chill_shb | 0.73 | 0.27 |
| star | high_chill_shb | 0.00 | 1.00 |
| snowchaser_evergreen | evergreen_zero_chill | 0.00 | 1.00 |
| avanti | evergreen_zero_chill | 0.00 | 1.00 |
| kestrel | evergreen_zero_chill | 0.00 | 1.00 |
| brightwell | rabbiteye | 0.00 | 1.00 |
| tifblue | rabbiteye | 0.00 | 1.00 |
| climax | rabbiteye | 0.00 | 1.00 |
| ochlockonee | rabbiteye | 0.00 | 1.00 |
| rebel | high_chill_shb | 0.00 | 1.00 |
| suziblue | high_chill_shb | 0.00 | 1.00 |
| legacy | high_chill_shb | 0.17 | 0.83 |
| biloxi | low_chill_shb | 0.38 | 0.62 |
| duke | nhb | 0.92 | 0.08 |
| bluecrop | nhb | 0.94 | 0.06 |
| draper | nhb | 0.96 | 0.04 |
| elliott | nhb | 0.96 | 0.04 |
| aurora | nhb | 1.00 | 0.00 |
| top_shelf | high_chill_shb | 0.00 | 1.00 |
| biloxi_evergreen | evergreen_zero_chill | 0.02 | 0.98 |

## Malosetti G×E cells

A climate analogue only claims known-cultivar / new-region and both-new. Those are the hardest cells and they have no genetics in them.

| Cell | n pairs | Mean similarity |
|---|---:|---:|
| known_cultivar_known_region | 8 | 0.64 |
| new_cultivar_known_region | 43 | 0.55 |
| known_cultivar_new_region | 26 | 0.53 |
| both_new | 43 | 0.40 |

## Blocked vs random pairs

- Random pair skill: **0.58**
- 5.0° blocked pair skill: **0.55**
- Large spatial blocks also hold out climate (Roberts Box 4). Believe blocked.

## No-analogue mask

Williams & Jackson 2007. Novel climates are not ranked. The cutoff is published and subjective (CCAFS authors already say so).

## Human panel (qualitative)

If the model loves a site growers already abandoned, that is a bug. Seed panel:

- Willamette Emerald / Biloxi / Snowchaser (OSU: do not plant).
- Star south of Ocala.
- Inland Michigan Legacy fruit buds.
- IGP Delhi / Lucknow / Patna winter fog.
- Olmos deciduous Duke.
- Ica Ventura 2023/24 heat.
- Santiago basin Legacy vs Osorno.
- Miami Star.

## Hindcast questions we still owe

- Would we have flagged Peru 2005, Morocco 2010, Mexico 2015 before the industry did?
- Report misses in public when those reconstructions are run on dated climate.

## Data trust

This sheet is only as good as the climate at the points. NASA POWER monthly climatology is the current operational source. CHELSA 1 km and hourly ERA5-Land on the shortlist still need to be staged. If a 10-year station disagrees on chill or harvest rain, the pixel is untrusted.

