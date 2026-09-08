# Initial weather validation findings

Executed 2026-09-07 local date. This is preliminary screening, not final agronomic validation.

## Anomaly investigation

The global archive contains 89 rainfall cell-days above a conservative investigation threshold of 1,000 mm/day; 45 have land cell centres in the Natural Earth mask. This threshold selects records for investigation, not automatic deletion. The maximum is 3,525.36 mm/day at 29°N, 116.25°W on 2020-06-11 (ocean cell). NASA's separate point API returns the same value. This rules out a bulk-to-canonical conversion discrepancy for that record, but does not prove the precipitation is physically correct. Source attribution versus MERRA-2 correction artifacts still requires investigation. Do not use these flagged values uncritically in rainfall-risk calculations.

All ten humidity gaps occur at 35.5°N: nine at 77.5°E and one at 80.625°E. One is in 2010 padding and nine are in the 2011–2025 baseline. The sampled 2010-02-09 gap also appears as missing in NASA's point API. Only one gap has been API checked; all ten were located in the archive. No raw or normalized weather values were changed or filled.

Exact records and sampled API comparisons: `anomaly_locations.json`.

## Station comparisons

Station records and source documentation downloaded from NOAA GHCN-Daily, with checksums and retrieval metadata. Original measurement, quality and source flags are preserved in server Parquet extracts. Nonblank quality flags, missing values, presumed-zero measurements and lagged-temperature flags are excluded from initial metrics. Trace precipitation is retained as its encoded value with its trace flag.

Selection: nearest two stations within 250 km with inventory extent spanning 2011–2020 for minimum temperature, maximum temperature and precipitation. Compare available accepted records during 2011–2025, not just inventory endpoints. Initially requiring inventory through 2025 yielded no southern Brazil match; relaxing the endpoint to 2020 yielded Paranagua. Selection was not based on model errors.

| Station | Distance from project site | Tmin pairs / 5,479 | Mean Tmin bias, grid minus station | Tmin MAE |
|---|---:|---:|---:|---:|
| Ocala | 28.2 km from Citra | 3,694 | +1.41°C | 1.67°C |
| Gainesville Regional Airport | 33.7 km from Citra | 5,479 | +1.55°C | 1.83°C |
| Paranagua | 179.7 km from Papanduva | 178 | −2.18°C | 2.59°C |

Weather is extracted at each station's own coordinate, not the project coordinate. The reported distance is the station's distance from the project site. Daily comparisons are joined by date and do not yet reconcile observation-day boundaries with NASA UTC days. Thus biases combine spatial representativeness, measurement, timing and model differences; they are not fitted correction coefficients.

The Florida results warrant specific cold-night/frost-event checks before recommendations. Paranagua is a coastal station at 5 m elevation, far from Papanduva, with only 56 accepted Tmax days and 288 precipitation days: it is **not adequate validation for Papanduva**. Do not extrapolate its bias inland.

Detailed metrics and limitations: `station_comparison.json`. Four parser tests passed on the server: units/leap days, QC and presumed-zero exclusions, flag preservation and baseline bounds.

## Remaining work

1. Obtain FAWN Citra quality-controlled subdaily observations and inspect documented flags and time conventions; aggregate comparable UTC days without treating gap-filled estimates as observations. Public annual files and metadata are available at https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/ but have not been downloaded in this step.
2. Locate useful INMET/Epagri or other measured observations nearer Papanduva; the current GHCN selection is insufficient. Preserve station elevation and observation schedules.
3. Reconcile observation-day timing, report monthly/seasonal and cold-event errors, and use held-out years for any later bias correction. No correction was fitted here.
4. Verify more rainfall anomalies against source variables and alternate products; add explicit warning/exclusion policy to downstream risk calculations while preserving originals.

NOAA format/flag authority: https://www.ncei.noaa.gov/pub/data/ghcn/daily/readme.txt

Station-versus-grid comparisons are distinct from API parity. However, stations may contribute to reanalysis assimilation, so they are not necessarily statistically independent validation observations.
