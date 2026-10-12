# 2026-10-12: corrections, request safety and scheduled evidence jobs

This package records the decision-free corrections from the 2026-10-11 review. It also covers the first runs of the scheduled evidence jobs. `HANDOVER.md` gives the code changes. Nothing here changes a model threshold, a phenology constant, the planting window, the benchmark scoring or a weather correction.

## Files

| File | Content |
|---|---|
| `event_checks_v2.md`, `event_checks_v2.json` | Frost checks for Chile (30 to 31 October 2022), Waikato (6 to 7 October 2022) and the US Southeast (12 to 13 March 2022). They use 3 by 3 grid neighbourhoods, local-night minima from the hourly archive, stations and model stages. |
| `event_checks_v2.py` | The script that produced the event checks. It ran on the server from a staging copy of `code/`. |
| `scan_change_report.json` | Managed-cycle scan results for all 71 saved locations, before and after the corrected scan accounting. |

## Event checks

- **US Southeast:** the freeze is in the grid on the right night, at stations and in every land cell.
- **Waikato:** Hamilton AWS recorded -2.8 °C. The nearest-cell rule picked a coastal cell (+5.15 °C), so the app misses the frost. The inland cell came within the normal calm-night bias.
- **Chile:** published values confirm the frost: Coihueco -2.0 °C (RAN Agromet) and Linares -2.2 °C (DMC bulletin). The pin cells stay at +4.6 to +5.1 °C, even on the right night.

The old Chile and Waikato cases in `docs/research/2026-10-05/ibo_event_checks.json` are now marked `inconclusive_window_or_cell` and point to v2.

**Withheld data.** For Chile, an agent fetched hourly series from 10 RAN Agromet stations and 5 INIA-network stations. The RAN XML endpoint answered only with a browser user agent, and the INIA series came through the site's data-request form. Both routes are outside the project's access rules without approval, so those series and all values derived from them are not in this repository. The full analysis and the raw files are on the server in `reports/event_checks_v2/`. The 2026-10-11 regional research had used the same RAN route to read the Coihueco and Linares 2 values that it published.

## Regional evidence registry

`dist/evidence/ibo-regional-v1.json` is now version `ibo-regional-2026-10-12`. Fifteen records changed to match the verification table in `docs/research/2026-10-11/review/astra_ibo_evidence_review.md`, section 3. Each was checked against the server's report text.

| Record | Fields changed |
|---|---|
| `us-ga-helene-2024-09`, `pe-water-ro`, `za-north-harvest` | citations |
| `rs-water` | citations, crop context |
| `us-ca-freeze-2022`, `es-huelva-2023-cold`, `za-wc-2024-weather`, `nz-hb-2023-floods` | period, limitations |
| `cl-2022-12-heat` | period |
| `cl-2022-11-frost-hail` | crop context, limitations |
| `au-wa-pruning` | summary, limitations |
| `us-pnw-2021-2022`, `pe-lambayeque-early`, `za-limpopo-2024-frost`, `nz-2024-25-heat` | limitations |

Period convention: "late" in a month starts on the 21st and "early" ends on the 10th, with precision `season`. The project chose this convention; the sources do not state it. Page citations rose from 172 to 174.

## Benchmark registry

`pipelines/weather/benchmark_sites.json` changed in notes, sources and gap text only. No scored month changed, so the benchmark scores are the same. Two month changes are proposed but not applied, because benchmark month changes that alter scoring need Paul's approval:

- **Zimbabwe (`zw-me-marondera`):** peak harvest from July–August to August–September. EU imports from Zimbabwe under CN 08104050 (Eurostat Comext) peaked in October and then September in 2023, 2024 and 2025 (October: 568, 1,898 and 1,625 t). Shipping takes several weeks, so the harvest peak is earlier. This is an inference.
- **Linares, Chile (`cl-linares-maule`):** bloom months September–October, from one dated season (2012–13) at a Linares farm in the Maule manual (2014).

Text-only updates:

- **Tasmania:** the peak stays January–February. March is now noted as a shoulder month, and the Hort Innovation handbook 2023/24 is added as a source.
- **Mexico:** the gap note now says SIAP blueberry data run to 2025.

## Scan accounting

The corrected scan gives every start and year one outcome. Over the 71 saved locations (25,560 start-years):

| Outcome | Start-years |
|---|---|
| Complete | 23,287 |
| Stalled slow | 1,354 |
| Stalled at the horizon | 372 |
| Weather incomplete | 547 |

Effects on the scan:

- The 30 sites where the scan is the main result keep their favourable starts and months.
- At comparison sites, Grand Junction, Michigan went from one favourable start to eight, and Odemira and Pelotas each gained one.
- 121 starts at 30 sites lost a recurring freeze that had come from counting stalls as freezes.
- 116 starts at 24 sites now show recurring cycle failure.
- No start gained a recurring freeze.

The leap-day correction moved 27 median dates at 17 sites one day earlier. The benchmark summary scores did not change.

## Evidence jobs: first runs

The runbook is `docs/evidence/JOBS_RUNBOOK.md`. Data are on the server under `data/evidence/`.

| Job | Rows | Raw size | Check |
|---|---|---|---|
| `rma-col` | 3,212 blueberry rows, crop years 1995 to 2026 | 162 MB | 2022: 217 rows, USD 77.654 million indemnity, freeze (code 42) USD 49.079 million. Both match the 2026-10-11 check. |
| `rma-sobtpu` | 13,234 rows, 1999 to 2027 | 167 MB | 2022 indemnity USD 77.654 million, equal to the cause-of-loss total |
| `storm-events` | 107,221 events, 1996 to 2026, in 12 states | 308 MB | 261 narratives mention blueberries |
| `ghcnh-stations` | 88 stations (82 with temperature), 1,141 station-years, 14.65 million hourly rows | 897 MB | GHCNh has no Linares data after 2010 and no Chillán data after 2020 |
| `station-truth` | 332 station and pin pairs, 1.41 million paired days | derived | 36 of 53 benchmark pins have a station with at least one year of 80% hourly coverage |
| `odepa-catastro` | 61,873 blueberry blocks, survey years 2000 to 2025 | 123 MB | Coihueco, 2024 survey: 621 blocks, 1,120 ha, 98 farms; Legacy, Duke and Brightwell lead |
| `odepa-exports` | 13,248 rows | 316 MB | Fresh exports 2021–2025 peak in January nationally; La Araucanía, Los Ríos and Los Lagos peak in February; Coquimbo in December |
| `comext-blueberry` | 5,540 rows, January 2010 to July 2026 | 0.2 MB | EU arrivals peak in October from Zimbabwe and in November from Peru, every year 2023 to 2025 |
| `senamhi-arandano` | 70 bulletins, 322 stage sentences | 46 MB | Field stages at Cayaltí, Chao and San José |

Station truth compares NASA POWER daily Tmin in the cell containing the pin with the nearest station. Bias is grid minus station; hit rate and false-alarm ratio are for local-night minima at or below 0 °C.

| Pin | Station (distance) | Years | Bias °C | Hit rate | False-alarm ratio |
|---|---|---|---|---|---|
| Linares | Copihue Retreat (29.7 km) | 2018 | +1.76 | 0.17 | 0.14 |
| Chillán | Gral. B. O'Higgins (6.6 km) | 2016–18 | +1.30 | 0.11 | 0.33 |
| Ohaupo | Hamilton AWS (8.5 km) | 2022–25 | +2.56 | 0 of 51 | none |
| Penguin | Devonport Airport (30.4 km) | 2015–23 | +2.94 | 0 of 25 | none |
| Alma, GA | Alma airport (4.3 km) | 2010–25 | +0.40 | 0.72 | 0.19 |
| Homerville, GA | Homerville airport (2.9 km) | 2010–25 | +0.60 | 0.64 | 0.13 |
| Waldo, FL | Keystone (13.1 km) | 2012–25 | +1.20 | 0.41 | 0.06 |
| Plant City, FL | Plant City airport (5.4 km) | 2010–25 | −0.38 | 0.85 | 0.21 |
| Elizabethtown, NC | Elizabethtown airport (4.0 km) | 2010–25 | −0.09 | 0.89 | 0.17 |

In the cell that contains Hamilton AWS rather than Ohaupo's coastal cell, the bias is +0.52 °C and the hit rate 0.14. These are measurements. No model, threshold or correction changed.

## Stale documents

- `docs/weather/GLOBAL_PHENOLOGY_REVIEW.md` section 1 now notes that it describes the v2 model.
- `docs/weather/phenology_calendar_audit_2026-09-24.json` now notes that it audits the v2 snapshots and cannot be reproduced from the v3 snapshots.
- `docs/research/2026-10-05/ibo_integration_review.md` cites the Mexico 2021/22 value of 74.20 thousand t from 2023 PDF pages 48 and 18. A rendered image of page 51 shows only the 2022/23 value.
- `docs/research/2026-10-05/ibo_report_inventory.json` lists the IBO Summit 2025, the Morocco Berry Conference 2025 and the 2023 summit deck as available but unread. It also records the Scribd copies of the 2024 and 2025 reports as rejected ("All Rights Reserved").
