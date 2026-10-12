# Event checks v2: Chile, Waikato and US Southeast frosts

Date: 2026-10-12. This applies the station-based protocol in `docs/research/2026-10-11/review/astra_ibo_evidence_review.md`, section 5.5. Data and full per-cell, per-night values are in [`event_checks_v2.json`](event_checks_v2.json). This file supersedes the Chile and Waikato cases in `docs/research/2026-10-05/ibo_event_checks.json`. Those cases are kept but marked `inconclusive_window_or_cell`.

Use of the server was read-only. The archive was read through `postprocess.extract` and `hourly_archive.hourly_from_cache`. Model stages come from `production.analyse` with the primary profile `stage_thermal_v3`. All server work ran from `tmp/EventChecksRegistry/`.

## 1. Registered expectations

These were written before the v2 grid and station computations were run. They are not blind. The Coihueco, Linares 2 and Hamilton minima and the daily values of the Chile and Waikato pin cells had already been published in the 2026-10-11 review and regional reports.

| Case | Hazard | Reported stage | Expected at stations | Expected in pin cells | Expected in neighbourhood | Expected timing | Expected stage |
|---|---|---|---|---|---|---|---|
| Chile, night of 30 to 31 Oct 2022 | radiative spring frost | fruit set | yes, near Coihueco or Longaví | no | only Andean cells | 0 or 1 day | fruit in Ñuble; late flowering in Maule |
| Waikato, night of 6 to 7 Oct 2022 | radiative frost after a polar outbreak | open flowers | yes, Hamilton | no (coastal cell) | about 0 °C inland, below 0 °C to the south-east | 0 | flowering |
| US Southeast, night of 12 to 13 Mar 2022 | advective (windborne) freeze | not stated in the IBO text | yes, all four | yes | yes | 0 | not testable |

## 2. Method

- **Nights.** The night ending on day D runs from 18:00 local on D-1 to 10:00 local on D. Each case covers the event night and three nights either side. Time zones are America/Santiago (UTC-3 in summer time), Pacific/Auckland (UTC+13) and America/New_York (UTC-5 until 02:00 on 13 March 2022).
- **Grid.** For each pin, the nearest cell and its 3 by 3 neighbourhood (cells 0.5° by 0.625°). Daily Tmin is the stored UTC-day value. The hourly grid is MERRA-2 T2M from the cached hourly archive, reduced to the local-night minimum and the hours at or below 0, -1 and -2.2 °C. Cell elevation comes from one NASA POWER point request per cell. The archive holds no elevation or land fraction.
- **Stations.**
  - NOAA GHCNh 2022 hourly files: Hamilton AWS, plus Alma, Homerville, Elizabethtown and Wilmington airports. Wilmington is 31.9 km from Burgaw; no closer hourly station exists.
  - Chile: GHCNh has no 2022 data for Linares or Chillán. Series from 10 RAN Agromet stations and 5 INIA-network stations were retrieved, but they are **withheld from this repository**. The RAN XML endpoint answered only with a browser user agent, and the INIA series came through the site's data-request form. Both routes are outside the project's access rules without approval. A private copy of the full analysis is on the server in `reports/event_checks_v2/`. The Chile case below uses published station values only.
- **Normal bias** (Waikato and US cases). Station minus own-cell local-night minimum for every night of the event month in 2022. The protocol asks for 2010 to 2025; only 2022 was downloaded. "Calm" means the median wind on that night was at or below 2 m/s.

## 3. Results

### 3.1 Chile, night of 30 to 31 October 2022

Published station values:
- Coihueco: -2.0 °C at 06:00 local on 31 October (RAN station 107; [RAN Agromet](https://www.agromet.cl/datos-historicos)).
- Linares: -2.2 °C. The [DMC October 2022 bulletin](https://climatologia.meteochile.gob.cl/publicaciones/boletinAgroclimatico/boletinAgroclimatico202210.pdf) (Vol. 44, p.8) lists this among the lowest values of three October cold events (8-9, 21-22 and 31 October). It does not name the day.

The station-by-station table, the wind check and the normal-bias comparison for Chile need the withheld series.

| Grid cell | Elevation | Night ending 30 Oct | Night ending 31 Oct |
|---|---|---|---|
| -36.5, -71.875 (Chillán and Coihueco pin cell) | 355 m | 2.24 | 4.56 |
| -36.0, -71.875 (Linares and Longaví pin cell) | 218 m | 3.69 | 5.07 |
| -36.5, -71.25 (Andean) | 1,428 m | -6.15 | -0.74 |
| -37.0, -71.25 (Andean) | 1,624 m | -7.06 | -2.89 |

Outcome:
- Hazard seen at stations: yes, in the published values.
- Hazard seen in the pin cells: no. The Coihueco minimum was 6.56 °C below its pin cell's local-night minimum on the event night.
- Hazard in the neighbourhood: only in the Andean cells.
- Timing: the grid is coldest one night early, on the night ending 30 October. The published Coihueco minimum is on the following night.
- Mechanism: radiative, as the trade reports describe. The station wind check is withheld.
- Stage: the model has the Ñuble pins in fruit, which agrees with the reported fruit set. The Maule pins are on the last day of flowering, an adjacent stage.

**Verdict.** The published station values confirm the frost on the night of 30 to 31 October 2022. The pin cells do not show it, so the app would not flag it even with the right date. This is expected for a daily 55 km grid on a radiative frost night. It is not a location or species error.

### 3.2 Waikato, night of 6 to 7 October 2022

Published station values ([NIWA Climate Statistics, October 2022](https://niwa.co.nz/sites/default/files/Climate%20Statistics%20-%20October%202022.pdf)), all dated 7 October:
- Hamilton AWS: -2.9 °C;
- Hamilton Ruakura: -2.0 °C;
- Te Kuiti: -2.5 °C.

The [NIWA October 2022 summary](https://niwa.co.nz/climate-and-weather/monthly/climate-summary-october-2022) describes polar fronts on 5 to 7 October. Blueberries New Zealand reported -5 °C in orchards ([Te Awamutu News](https://www.teawamutunews.nz/2022/10/how-tunnel-vision-paid-off/)).

| Series | Night ending 6 Oct | Night ending 7 Oct | Hours ≤ 0 °C on 7 Oct |
|---|---|---|---|
| Hamilton AWS (GHCNh, 8.5 km from Hamilton) | 5.9 | **-2.8** | 7 |
| Pin cell -38.0, 175.0 (coastal, 108 m) | 7.82 | 5.15 | 0 |
| Inland cell -38.0, 175.625 (225 m), the station's own cell | 6.17 | 0.06 | 0 |
| Cell -38.5, 175.625 (416 m) | 3.63 | -0.94 | 7 |

Outcome:
- Hazard seen at the station: yes.
- Hazard in the pin cell: no.
- Hazard in the neighbourhood: borderline in the inland cell; yes in the cell to the south-east.
- Timing: no offset. The night ending 7 October was the coldest of the seven in every land cell.
- Size: station minus own cell was -2.86 °C, at the edge of the October calm-night band (median -0.78, 10th percentile -3.04). Against the coastal pin cell the gap was -7.95 °C.
- Stage: the model has flowering, which agrees with the reported open flowers.

**Verdict.** The frost is confirmed at the station. The nearest-cell rule picks a coastal cell and misses it. The inland neighbour comes within the normal calm-night bias.

### 3.3 US Southeast, night of 12 to 13 March 2022

| Station | Distance to pin | Night ending 13 Mar | Own cell | Station minus cell |
|---|---|---|---|---|
| Alma airport | 4.2 km | -2.8 | -3.12 | +0.32 |
| Homerville airport | 2.9 km | -1.6 | -2.53 | +0.93 |
| Elizabethtown airport | 4.0 km | -4.5 | -5.47 | +0.97 |
| Wilmington airport (for Burgaw) | 31.9 km | -2.8 | -5.24 | +2.44 |

Outcome:
- Hazard seen at stations and in every land cell of both neighbourhoods.
- Timing: no offset.
- Mechanism: advective. Wind was 2.1 to 5.1 m/s.
- Size: the grid was slightly colder than the stations, within the normal March range.
- Stage: the model has fruit in Georgia and flowering in North Carolina. The cited IBO text gives no stage.

**Verdict.** The freeze is confirmed and represented in the grid on the right night. This is one weather episode, not four independent events.

## 4. What this means for the app

- Advective freezes are represented. Radiative frosts in orchard hollows are not, even at the right date and with a 3 by 3 neighbourhood. At Hamilton the October 2022 calm-night median of station minus own cell was -0.78 °C (10th percentile -3.04 °C); the event-night gap against the coastal pin cell was -7.95 °C.
- In Waikato, cell choice matters more than the date. In Chile, the date mattered, and with the right date the grid still misses.
- These checks do not set any threshold, bias correction or cell rule. Those decisions are still pending.

## 5. Sources and terms

- NOAA GHCNh: public US government data. The files and SHA-256 hashes are listed in the JSON.
- RAN Agromet (agromet.cl): an open MINAGRI service; no licence is stated. The Coihueco value is cited from its public historical-data page. Its series are withheld (section 2).
- INIA agrometeorology network (agrometeorologia.cl): series withheld (section 2).
- NIWA: the summary pages are CC BY-NC-ND.
- DMC: public bulletin.
- NASA POWER: open.

## 6. Limits

- Three events, so outcomes are categories, not an accuracy rate.
- The normal-bias bands use one month of 2022.
- The Chile case rests on two published values; its station series are withheld until access is approved.
- No cloud data and no cell land fraction were used.
