<!-- Research scout report (WeatherInputs), generated 2026-09-21 for the future plan. Read-only literature/code research; claims marked [unverified] are not confirmed. -->

# Weather inputs and global scaling — scout report

## 1. Findings with sources

### 1.1 POWER / MERRA-2 biases in the humid subtropics

- POWER's own global validation (2,599 ISD/GSOD stations, 2001–2020 hourly, 1981–2020 daily): daily Tmin MBE +0.32 °C, RMSE 3.15; Tmax MBE −1.23 °C, RMSE 3.10; precipitation MBE +0.55 mm/d, RMSE 3.69, R² 0.39; hourly T2M MBE −0.58, RMSE 3.32. https://power.larc.nasa.gov/docs/methodology/meteorology/assessment/
- Brazil, 203 INMET stations 1997–2016 (Monteiro, Sentelhas & Pedra 2018, Int J Climatol): temperature "satisfactory" (Tmin R² 0.72, Tmax 0.57 daily); RH and wind flagged as needing improvement; recommended against RH-dependent derived variables. https://rmets.onlinelibrary.wiley.com/doi/abs/10.1002/joc.5282
- Tropical humid basin (Tan et al. 2023, J Hydrol, Kelantan, 19 gauges 1981–2020): both POWER and ERA5-Land overestimate Tmin and underestimate Tmax; both overestimate moderate rain (1–20 mm/d) and underestimate heavy (>20 mm/d) and dry days; ERA5-Land "slightly better"; bias correction recommended before any extremes analysis. https://www.sciencedirect.com/science/article/abs/pii/S002216942300882X
- Multi-decadal US/Türkiye validation (2026, Theor Appl Climatol): Tmax RMSE 1.5–6.9 °C, Tmin 1.2–8.4 °C by station; coastal sea-breeze/marine-layer sites and high-relief sites are the poor performers; RH, wind and precipitation are the geography-sensitive variables. https://link.springer.com/article/10.1007/s00704-026-06532-0
- Bias-correction evidence: station-level linear calibration + GAMM cuts RMSE ≈80 % (Tmin), 82 % (Tmax) but only 30 % (RH), RH bias being cross-variable rather than an offset (ColClim, Sensors 2026). https://doi.org/10.3390/s26134301
- Our own numbers (docs/weather/REGIONAL_STATION_PILOT.md, 2020 only): grid − station Tmin +0.95 (Citra), +0.90 (Major Vieira), +1.33 °C (Rio Negrinho); Tmax +0.61 / +0.38 / −0.86 °C; MAE 1.3–1.8 °C. The grid missed all three sub-zero days at each INMET station. Rain comparison withheld (units unresolved). This matches the literature direction: warm Tmin bias, frost under-detection.

Interpretation for this product: the warm-Tmin bias directly inflates the "no frost" story and deflates chill hours (fewer hours < 7.2 °C), so Tmin bias matters more than Tmax bias for the classifier. RH-based disease days (Paul's decision 2) sit on the worst-behaved POWER variable.

### 1.2 Alternative free datasets

| Dataset | Grid / step | Variables relevant to us | Coverage / latency | Licence, access | Size for our scope [computed] |
|---|---|---|---|---|---|
| NASA POWER (MERRA-2 + GEOS-IT) | 0.5°×0.625°, daily + hourly | T, Tmin, Tmax, Tdew, RH, P, wind, solar | 1981– (hourly 2001–), ~2 days | Public domain-style, no key; point API | Daily global 2010–25 already held (18.8 GB raw); hourly T+Tdew global land ≈ 60 k cells × 140 k h ≈ 34 GB float32 (constraint forbids) |
| ERA5-Land | 0.1° (~9 km), hourly | T, Tdew, P, wind, solar (no RH; derive) | 1950–, 5 days | CC-BY 4.0; ECMWF account + licence acceptance on CDS; queued retrievals | Global land hourly ≈ 1.8 M cells × 140 k h × 2 B ≈ 500 GB per variable — infeasible; per-point cheap |
| ERA5-Land via Open-Meteo API | same | same + derived RH | same | CC-BY 4.0; no key; free non-commercial, 10 k calls/day, no uptime guarantee; self-hostable | Per point only |
| AgERA5 | 0.1°, daily (Tmin/Tmax/Tmean, RH at 06/09/12/15/18, P, solar, wind) | agro-ready, elevation-corrected | 1979–, ~7 days | Copernicus licence (free, any purpose); CDS key | Global land daily 16 yr ≈ 21 GB/variable int16; ~150 GB for 7 vars |
| CHIRPS v2/v3 | 0.05°, daily precipitation | rain only | 50°S–50°N (v3: 60°), prelim 2 d, final ~3 wk | Public domain (CC0) | Global daily 16 yr ≈ 25 GB |
| IMERG Final v07 | 0.1°, 30-min / daily | rain only | 60°S–60°N (full globe daily), 3.5 months | CC-BY 4.0; Earthdata login | Daily ≈ 60 GB |
| TerraClimate | 1/24° (~4 km), monthly | Tmax, Tmin, P, VPD | 1958– | CC0 | Small; monthly only — no daily thresholds |
| Daymet / PRISM / gridMET | 1 km / 800 m–4 km / 4 km, daily | full met | North America / CONUS only | Daymet public; PRISM 4 km free, 800 m paid; gridMET public | US-only; not for global scope |

Sources: ECMWF ERA5-Land docs https://confluence.ecmwf.int/display/CKB/ERA5-Land:+data+documentation ; Open-Meteo pricing/terms https://open-meteo.com/en/pricing ; AgERA5 PUGS (warns tropical rainfall must be evaluated) https://confluence.ecmwf.int/x/3FmaE ; CHIRPS https://www.chc.ucsb.edu/data ; IMERG https://gdex.ucar.edu/datasets/d731000/ ; TerraClimate https://www.climatologylab.org/terraclimate.html ; POWER sources https://power.larc.nasa.gov/docs/methodology/data/sources/ .

Does anything beat POWER for our needs? Temperature: ERA5-Land/AgERA5 are marginally better in most head-to-heads and 5–6× finer, but not categorically (a 2025 Türkiye study had POWER ahead, RMSE 2.56 vs 3.33 °C; https://link.springer.com/article/10.1007/s00704-025-05605-w). Rainfall: POWER (PRECTOTCORR is gauge-corrected MERRA-2) and ERA5 both smear heavy-rain days; CHIRPS/IMERG are the datasets built for rain-day counting and would improve the harvest-rain risk, at the cost of a second grid. RH: no free product is good; ERA5 dewpoint is the better derivation than POWER RH2M [inference from ColClim + Monteiro, unverified for our sites].

### 1.3 Daily→hourly reconstruction

- chillR `stack_hourly_temps`/`make_hourly_temps` implement Linvill (1990): sine by day, log decay by night, sunrise/sunset from latitude (Spencer 1971; Almorox 2005). This is exactly what Luedeling & Brown 2011 used to compute Safe Winter Chill for 5,078 stations globally (Chill Portions, chill hours, Utah). https://cran.r-project.org/web/packages/chillR/vignettes/hourly_temperatures.html ; https://link.springer.com/article/10.1007/s00484-010-0352-y
- Published error (chillR vignette, Winters CA, one season): hourly RMSEP 1.9 °C (idealised curve from local Tmin/Tmax), 2.5 °C (curve from proxy station), 3.9 °C (linear fill); cumulative Chill Portions 13.8 vs observed 12.2 (local curve), 20.1 (proxy), 23.1 (linear). Take-away: the idealised curve from the same cell's extremes is acceptable; anything using a different location or linear interpolation overstates chill by 60–90 %.
- Cesaraccio et al. 2001 (Interpol.T) fits four curve pieces with monthly calibration; better hourly RMSE where calibrated, but needs hourly training data — we have 19 cells to fit and test.
- Key subtlety for our chill rule: chill hours (T < 7.2) are far more sensitive to the nightly curve shape than Chill Portions, because the threshold sits inside the night-time range in Florida winters. The Dynamic Model's two-step buffer damps that. This is one more argument for Paul's open decision 7 to favour CP [inference].

### 1.4 Elevation within a 55 km cell

- Standard practice for gridded downscaling: T_pin = T_cell + Γ·(z_cell − z_pin) with Γ ≈ 6.5 K/km (MicroMet, Liston & Elder 2006). Observed surface lapse rates are 3.9–5.2 K/km with strong seasonal and diurnal cycles; Tmin lapse rates are systematically lower than Tmax and invert at night in valleys (Minder 2010; Rolland 2003; Dutra 2020 ELR for ERA5). https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2009JD013493 ; https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2019ea000984
- Chill mapping practice: recent 1 km chill-portion maps (NE Spain, 2025) compute CP from daily gridded Tmin/Tmax after lapse-corrected interpolation. https://pmc.ncbi.nlm.nih.gov/articles/PMC13134984/ AgERA5 already ships elevation-corrected temperature. AgroClimate's chill tool does no interpolation at all: it reports the nearest FAWN station. https://journals.flvc.org/edis/article/download/118311/116247/172902
- For Papanduva (≈800 m) inside a MERRA-2 cell whose mean elevation may differ by 100–300 m, a 6.5 K/km correction is 0.7–2 °C — same order as the measured bias, but of unknown sign for Tmin. Blind application could create frost days that don't exist.

## 2. Concrete recommendations

R1. Daily→hourly fallback (`pipelines/weather/hourly_reconstruct.py`, new). Port Linvill/Spencer daylength to numpy; input daily Tmin/Tmax from the existing tiles, output the same hourly `Series` contract `production.season()` consumes (line 194). Wire into `location_api.hourly_for()` (41–56) as third tier with `hourly_source.note = 'reconstructed'`. Validation harness in `chill_comparison.py`: for each of the 19 cells, reconstruct from POWER daily Tmin/Tmax and compare against stored POWER hourly: hourly RMSE, chill hours (<7.2 and 0–7.2), Chill Portions, per-winter classifier agreement. Report per-cell error in the API `limitations`. Optional stage 2: Cesaraccio monthly calibration on 14 cells, test on 5.

R2. On-demand POWER hourly for opened pins. `evaluation_sites.fetch()` already does checksummed per-cell acquisition; expose it behind a bounded job (`location_api` returns 'reconstructed' immediately, upgrades to 'stored hourly' when the fetch lands, keyed by `cell_key`). Cap cache (e.g. 500 cells ≈ 500 × 140 k × 2 vars ≈ 0.6 GB parquet).

R3. Bias diagnostics before bias correction. Extend `regional_stations.py` to 2015–2025 for FAWN Citra + 3–4 more FAWN sites and 4–6 INMET stations (Santa Catarina/Paraná highlands). Compute monthly Tmin/Tmax bias, frost-day hit/miss rates, and Chill-Portion bias. Publish as `docs/weather/STATION_BIAS.md`; surface in the UI as "grid vs nearest station" evidence. Fit a correction only if bias is stable across years (held-out years); simplest defensible model is monthly additive Tmin/Tmax offsets per region, applied before reconstruction. Do not correct RH.

R4. Rain-day second source. Add CHIRPS daily (public domain) as the harvest heavy-rain (≥10 mm) counter for 50°S–50°N, keeping POWER for everything else. Storage ≈ 25 GB global or per-tile on demand; if the storage budget is tight, fetch per pin from the CHC HTTP tiles.

R5. Elevation awareness. Add pin elevation (SRTM/Copernicus DEM tile lookup, or the existing SoilGrids-style point query) and MERRA-2 cell mean elevation; show Δz and a warning above ±150 m. Apply Γ = 6.0 K/km to Tmax/Tmean only as an optional toggle; leave Tmin uncorrected with an explicit note. Revisit after R3 shows whether the highland INMET stations behave.

R6. ERA5-Land as second opinion, not backbone. `pipelines/weather/era5_point.py` calling Open-Meteo historical API per pin (hourly T, Tdew, P; CC-BY, no key, 10 k calls/day) into the same hourly contract; show chill/frost side-by-side. Fallback path via CDS API requires an ECMWF account and licence acceptance — a human decision.

Architecture: POWER daily global (existing) → pin → [stored hourly | on-demand POWER hourly | reconstructed hourly] → `production.analyse` → risks; station bias diagnostics attached as evidence; CHIRPS for rain-day counts; Open-Meteo ERA5-Land as comparison layer; elevation delta as warning.

## 3. Effort (one builder with AI assistance)

| Rec | Person-days |
|---|---|
| R1 reconstruction + 19-cell validation + API wiring + tests | 4–5 |
| R1 stage 2 Cesaraccio calibration | +2 |
| R2 on-demand hourly job + cache + UI status | 3 |
| R3 multi-year FAWN/INMET bias study (acquire, QC, report) | 5–6; +2 if a correction model is fitted |
| R4 CHIRPS integration for rain days | 3 |
| R5 elevation lookup + warning + optional Tmax lapse toggle | 2 |
| R6 Open-Meteo ERA5-Land comparison layer | 2–3 |

Total core (R1, R2, R3, R5): ~15 days; full set: ~22–25 days.

## 4. Risks, unknowns, human decisions

- Chill metric decision (Paul's item 7) interacts with R1: reconstruction error is tolerable for Chill Portions, marginal for chill hours < 7.2. Recommend deciding CP (or reporting both) before shipping the fallback.
- Warm-Tmin bias plus frost under-detection means the current risk ranking probably understates flower-freeze frequency in Brazil highlands; any bias correction changes the classifier for border sites — needs Paul's sign-off on evidence level.
- Open-Meteo is a third-party free service with no uptime guarantee and a non-commercial clause; CDS needs an ECMWF account — both require an owner decision (Patricio/Rohit).
- CHIRPS stops at 50°N/S (v3 60°); poleward pins would fall back to POWER rain. IMERG needs Earthdata credentials.
- Lapse-rate Tmin adjustment can manufacture false frost; keep it off until R3 validates on highland stations.
- Unverified: exact Monteiro 2018 Tmin/Tmax bias magnitudes (abstract-level only) [unverified]; storage sizes are back-of-envelope [computed, unverified]; chillR vignette error numbers are one Californian season, not humid-subtropical winters.
- Cross-topic: disease-day metric depends on RH, the least correctable variable — the risk-factor scout should consider dewpoint-depression or rain-based proxies.
