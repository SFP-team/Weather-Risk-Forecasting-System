# Citra and near-Papanduva observation pilot

Completed a bounded 2020 pilot using public station archives. This improves on the earlier same-date NOAA screening but does not establish multi-year or field-level accuracy. Original NASA data are unchanged; no bias correction was fitted.

## Results

Bias below means NASA grid minus observed temperature. Each grid series is extracted at the weather station's coordinate, not at the project field coordinate.

| Station | Usable temperature days | Tmin bias | Tmin MAE | Tmax bias | Tmax MAE |
|---|---:|---:|---:|---:|---:|
| FAWN Citra 250 | 224 | +0.95°C | 1.41°C | +0.61°C | 1.29°C |
| INMET Major Vieira A864 | 365 | +0.90°C | 1.70°C | +0.38°C | 1.55°C |
| INMET Rio Negrinho A862 | 365 | +1.33°C | 1.65°C | −0.86°C | 1.83°C |

Major Vieira is 29.6 km from the target Papanduva coordinate, at 799.58 m elevation. Rio Negrinho is 50.4 km away at 856.89 m. These are substantially more relevant regional observations than coastal Paranagua, but not measurements of the target field.

On accepted UTC days, each Brazilian station records three below-zero temperature days. The matching grid misses all three at each station. Major Vieira's grid additionally has one below-zero day not observed there; Rio Negrinho's has none. These are threshold comparisons of a small sample, not verified crop frost damage or an independently validated event detection rate. Citra has no below-zero days in the strictly accepted subset, so this subset cannot assess its frost sensitivity.

## Methods and limitations

- FAWN: 34,987 original 15-minute Citra records retained, including original quality flags. Source flags serialize as strings such as `0.0` and `17.0`; integral decimal suffixes are normalized only for filtering. A day requires all 96 temperature samples with flag zero. This leaves 224 days; nothing is filled. The strict filter may preferentially exclude extreme days. Daily extrema of sampled temperatures may miss between-sample extrema.
- FAWN timestamps are documented UTC. Citra station coordinates are 29.4101, −82.1732, distinct from the supplied research-field coordinate. The selected NASA cell centre is about 30.6 km from the station.
- INMET: use the two closest stations in the downloaded 2020 national archive. The hourly maximum/minimum fields refer to the preceding hour. Shift interval-ending midnight into the prior UTC day, require 24 valid hourly extrema, and exclude the incomplete final day because the next year's midnight record is absent. No gap filling.
- INMET CSVs lack per-measurement QC flags. Preserve the source and apply only missing-sentinel, broad temperature-range and temperature-order screening. This is not provider-certified QC.
- Rainfall: FAWN comparison withheld because metadata calls its field inches/hour and the interval accumulation semantics require confirmation. INMET preliminary rainfall outputs remain labelled provisional for interval timing and limited QC; Major Vieira has only 89 complete rainfall days versus 365 at Rio Negrinho. Do not use these as approved rainfall correction coefficients.
- Monthly metrics, raw flags, station metadata and exact source-grid locations are retained in machine-readable reports. Seven station-related tests passed on the server, covering parsing, flags, complete-day exclusion, leap dates and midnight interval assignment.

## Artifacts

Local report details: `fawn_citra_2020.json`, `inmet_near_papanduva_2020.json`.

Server root: `/media/fpt/fpt2/Weather_Claude`.

- `data/reference/validation/fawn_2020.zip` and `inmet_2020.zip`: downloaded original annual archives, with adjacent checksums/retrieval provenance.
- `data/normalized/stations/FAWN_250_2020.parquet`: original selected Citra fields and flags.
- `data/normalized/stations/INMET_A864_2020.parquet` and `INMET_A862_2020.parquet`: original selected station tables.
- Corresponding `_daily.parquet` files: derived complete-day comparisons.
- `reports/inmet_candidates.json`: distance-ranked station inventory for reproducible selection.

Reproduce on the server from `code/` using `../env/bin/python regional_stations.py acquire`, then actions `fawn` and `inmet`. Acquisition reuses checksummed downloads. This pilot intentionally downloads only 2020; it is not the full historical station archive.

## Next research decisions

Extend across multiple years and quantify coverage by season before fitting corrections. Investigate flagged cold observations rather than simply loosening QC to obtain more frost events. Verify rainfall accumulation semantics against another official export. Retain held-out years for any correction model; evaluate minimum-temperature tails and cold-event timing, not just average error.

Epagri's public service requires registration and provides immediate downloads for the last 24 months. Older periods require a request. No account was created and no message was sent. Direct Papanduva records would improve validation, but INMET enables regional progress without those credentials.

## Primary sources

- [FAWN Citra station metadata](https://fawn.ifas.ufl.edu/station.php?id=250)
- [FAWN QA/QC field and time documentation](https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/metadata.txt)
- [FAWN measured-data archives with flags](https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/)
- [INMET historical annual archives](https://portal.inmet.gov.br/dadoshistoricos)
- [INMET glossary, including preceding-hour extrema](https://portal.inmet.gov.br/glossario/massa-de-ar)
- [Epagri data access and historical-request conditions](https://ciram.epagri.sc.gov.br/dadosambientaispublicos/)
