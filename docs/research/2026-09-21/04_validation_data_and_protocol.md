<!-- Research scout report (ValidationData), generated 2026-09-21 for the future plan. Read-only literature/code research; claims marked [unverified] are not confirmed. -->

# Ground truth and validation protocol

## 1. Findings with sources

### 1a. Observed phenology / harvest-progress datasets

| Name | Region | Years | Variables | Resolution | Access | URL |
|---|---|---|---|---|---|---|
| USDA NASS Georgia Crop Progress | Georgia (state) | weekly reports online ≥2000; blueberry row verified 2024 | "Blueberries-Harvested %" this/prev week, prev year, 5-yr avg | state, weekly | free PDF/Quick Stats | https://www.nass.usda.gov/Statistics_by_State/Georgia/Publications/Crop_Progress_and_Condition/ (verified row in GA-CropProgress-6-17-24.pdf) |
| USDA NASS Florida Crop Progress | Florida | same | No blueberry percent rows in the 2024 April/Sept issues I read; narrative only | state, weekly | free | https://www.nass.usda.gov/Statistics_by_State/Florida/Publications/Crop_Progress_&_Condition/index.php |
| USDA AMS MyMarketNews weekly shipments (WA_FV408, slug 3251) | FL, GA, other US origins + imports | historical shipping-point data retained; depth [unverified, likely ≥2010] | weekly movement (lb) by origin → harvest-progress curve (10/50/90 % cumulative) | state/district, weekly | free, API key on request, up to 100k rows/call | https://mymarketnews.ams.usda.gov/viewReport/3251 ; API https://mymarketnews.ams.usda.gov/mymarketnews-api |
| Kovaleski et al. 2015 JASHS 140:38 | Citra PSREU (FL) | 2012, 2013 bloom; buds 2011–13 | % bloom biweekly vs GDD (base 7, from 1 Jan, FAWN); 50 % bloom: Emerald 225 GDD, Jewel 302 GDD; logistic curves | plot, biweekly | open access | https://journals.ashs.org/view/journals/jashs/140/1/article-p38.xml |
| Kirk & Isaacs 2012 HortScience 47:1291 | Michigan | 15 yrs harvest + bloom of 5 NHB cultivars | GDD-bloom logistic, base temp | site, yearly | paywalled abstract free | https://journals.ashs.org/hortsci/view/journals/hortsci/47/9/article-p1291.xml |
| NeSmith / UGA rabbiteye trial | Alapaha GA | 5-yr means | 50 % bloom date by cultivar (Climax 7 Mar … Ochlockonee 27 Mar) | site, mean only | free web | https://fieldreport.caes.uga.edu/news/chilling-out-important-for-blueberry-varieties/ |
| Embrapa Clima Temperado Sistema de Produção 8 / Mirtilo | Pelotas RS | 2003 season + 3-yr study | início/plena/fim floração, início/fim maturação per cultivar | site, dates | free PDF | https://www.infoteca.cnptia.embrapa.br/bitstream/doc/745223/1/sistema08.pdf ; https://www.infoteca.cnptia.embrapa.br/infoteca/bitstream/doc/1155980/1/Sistema-de-Producao-do-Mirtilo.pdf |
| Epagri zoneamento mirtilo SC | Santa Catarina | 2020/21 cultivar evaluation | bloom onset ranking by cultivar; chill zoning maps | municipality | free PDF | https://ciram.epagri.sc.gov.br/ciram_arquivos/site/boletins_culturas/risco_climatico/SC_Mirtilo_Zoneamento.pdf |
| USA-NPN / Nature's Notebook | USA | 2009– | status/intensity (open flowers, ripe fruit) per plant; Vaccinium genus present, V. corymbosum count [unverified] | plant, visit | free, no key (self-identify), rnpn/REST | https://www.usanpn.org/data/observational ; https://github.com/usa-npn/rnpn |
| CIREN/INIA Chile phenology curves | Maule, Biobío, Araucanía | descriptive | stage curves, thermal sums (base 10 °C, 490–500 GDD bud swell→harvest) | region | free PDF | https://www.ciren.cl/wp-content/uploads/2017/12/Ar%C3%A1ndano.pdf |
| SERIDA Asturias cultivar phenology | N Spain | 2013–2016, 59 cultivars | bloom start/end, harvest start/end | site | free | https://www.serida.org/publicacionesdetalle.php?id=6724 |
| Steyn, Lötze & Hoffman 2022 Sci. Hortic. 307:111493 | Western Cape ZA | 2 seasons, 2 SHB cultivars | reproductive phenology progression | site | paywalled | https://www.sciencedirect.com/science/article/abs/pii/S0304423822006136 |
| Proarándanos weekly export (Peru), Berries ZA status reports, Morocco/Australia trade calendars | Peru, ZA, MA, AU | weekly export volumes (Peru by campaign week) | harvest-progress proxy only | country/week | press releases, no bulk file | https://arandanosperu.pe ; https://www.berriesza.co.za/berry-brief/status-report/ |
| Huelva, Mexico (Jalisco), Morocco | | | only month-level calendars found; no per-year bloom tables located | | | — |

Not found publicly: UF Citra/Waldo cultivar-trial bloom and ripening logs by year, Georgia Blueberry Commission season reports with dates, Oregon NWREC harvest-date tables (Strik et al. 2017 gives cultivar harvest means only). The UF breeding program's own annual ratings (bloom %, ripening %) at Citra/Waldo/grower sites are the best field-level truth and are internal to Patricio's group.

### 1b. Station networks for grid correction

| Network | Coverage | Access |
|---|---|---|
| FAWN | ~40 FL stations, 15-min, QA/QC flags, UTC | public annual CSV zips (already wired in `regional_stations.py`); `controller.php/today|lastHour` APIs for current data only. https://fawn.ifas.ufl.edu/data/fawn_data_qaqc_pub/ |
| UGA AEMN | 87 GA stations, 15-min | web calculators/limited history; bulk by email aemn@uga.edu. https://weather.uga.edu |
| INMET | Brazil national hourly | annual zips (wired). https://portal.inmet.gov.br/dadoshistoricos |
| Epagri/CIRAM | 176 SC stations hourly | registration, instant last 24 months; older by request. https://ciram.epagri.sc.gov.br/dadosambientaispublicos/ |
| Agromet (INIA) | ~430 Chile stations, 15-min, ~12 yrs | free download + API (`agrometR`). https://www.agromet.cl ; https://github.com/ODES-Chile/agrometR |
| SIAR (MAPA) | >500 Spain stations, hourly/daily | registered users, CSV, ~13 yrs per query; API. https://eportal.mapa.gob.es/websiar/ |
| BOM | Australia daily obs | Climate Data Online (free daily), anonymous FTP `ftp.bom.gov.au /anon/gen/clim_data/IDCKWCDEA0/tables`. https://www.bom.gov.au/climate/data/ |
| GHCN-Daily | global | wired in `validate_observations.py` |

### 1c. Grid-error and achievable-accuracy literature
- MERRA-2 does not assimilate 2 m station temperature, so station comparisons are independent (https://nordata.physics.utoronto.ca/en/annexes-datasets-descriptions/71-temperature/modern-era-retrospective-analysis-for-research-and-applications-version-2-merra-2/).
- NASA POWER vs 40 US/Türkiye stations, 15–43 yrs: Tmin RMSE 1.23–8.37 °C, Tmax 1.50–6.89 °C (https://link.springer.com/article/10.1007/s00704-026-06532-0). Mediterranean study: local linear bias correction moved Tmin MBE from +1.03 to −0.02 °C (https://mdpi.com/2073-4395/11/6/1207/htm). Our own pilots: Citra +0.95 to +1.55 °C Tmin bias, Papanduva-area +0.9 to +1.3 °C, all observed sub-zero days missed (`REGIONAL_STATION_PILOT.md`).
- Phenology model accuracy with station data: PhenoFlex apple/pear RMSE ≈4 d; apple median validation RMSE 4.4 d, pear 3.1 d; almond combined-fit validation 6.4±3.0 d; cross-regional apple 4.6–5.4 d; split-to-split RMSE spread median 6.4 d (https://www.sciencedirect.com/science/article/pii/S016819232100174X ; https://www.sciencedirect.com/science/article/pii/S0168192325004782 ; https://link.springer.com/article/10.1007/s00484-025-03068-2). Sample-size guidance: common (pooled) models ~10 yrs per series, cultivar-specific ≥30 yrs (https://www.sciencedirect.com/science/article/pii/S1161030124002405). Gridded Daymet gave bloom RMSE ~2 d lower than sparse stations for continental phenology grids (https://www.sciencedirect.com/science/article/pii/S0168192318302193).
- Blueberry-specific: Kovaleski 2015 bloom % tracked GDD consistently across years (pseudo-R² 0.88–0.91) but under hydrogen cyanamide, which advances bud opening; Kirk & Isaacs used 15 yrs Michigan.

## 2. Recommendations (file/module level)

1. **Data request to UF breeding program** (human action): per-site-year bloom % and ripe-fruit % ratings for Citra, Waldo and grower panel sites 2011–2025, cultivar and cyanamide/tunnel flags. Store under `data/reference/phenology/` with provenance JSON like `fetch()` in `validate_observations.py`.
2. **`pipelines/weather/phenology_truth.py` (new)**: loaders for (a) NASS Georgia weekly PDFs → harvest 10/50/90 % dates per year; (b) AMS MyMarketNews WA_FV408 by origin → same for FL/GA; (c) USA-NPN `rnpn`-equivalent REST pull for Vaccinium open-flowers/ripe-fruit within 60 km of panel sites; (d) hand-entered literature table (Kovaleski, NeSmith, Embrapa, SERIDA) with citation column and `evidence_level`.
3. **Extend `regional_stations.py`** to 2011–2025 for FAWN Citra/Ocala/Alachua/Sebring and INMET A864/A862; add Agromet, SIAR, BOM parsers only when a panel site exists there. Report seasonal Tmin bias, sub-zero hit/miss/false-alarm, and Tmin ≤ −2.2 °C contingency, not only annual means.
4. **Bias correction in `production.py`**: new profile key `tmin_correction` = monthly additive offset (or quantile map for the cold tail) fitted on odd years, evaluated on even years, applied to hourly and daily T before chill and freeze counts; keep raw run alongside. Expose `evidence_level: corrected|raw` in `location_api.py` output.
5. **`pipelines/weather/validation_scores.py` (new)**: joins `season()` rows to truth by site-year; outputs MAE/median/bias in days for flowering start, 50 % bloom, harvest start; class agreement (accuracy, Cohen's κ) vs expert/pre-registered class; Brier score and reliability table for each risk's per-winter event probability against observed-station event occurrence; Wilson CIs. Write `reports/validation_scores.json` and a doc `docs/weather/VALIDATION_PROTOCOL.md`.
6. **Pre-registration**: a CSV `config/preregistration.csv` (site, expert, expected_class, expected_bloom50_doy ± range, expected_harvest_start ± range, timestamp, signature) filled by Paul and Gerardo before they see model output; lock via checksum recorded in the report. Test in `tests/weather/test_validation_scores.py` only for scoring maths (MAE, κ, Brier on fixed fixtures).

## 3. Validation protocol (step by step, effort in person-days)

| Step | What vs what | Metric | Min sample | Days |
|---|---|---|---|---|
| 0 Pre-register | Paul/Gerardo fill class + bloom50 + harvest-start expectations for 18 panel sites; freeze checksum | — | 18 sites × 2 experts | 0.5 (+ expert time) |
| 1 Station truth | FAWN/INMET 2011–2025 daily extrema, complete-day rule | Tmin bias, MAE by month; contingency for ≤0, ≤−2.2 °C | ≥10 winters per station | 2 |
| 2 Tmin correction | fit on odd years, test on even years; monthly additive vs quantile-map cold tail | held-out MAE, hit rate, chill-hour difference | same | 2 |
| 3 Chill fulfilment | model chill hours/CP at Citra vs FAWN-computed chill (same definitions) and FBGA/AgroClimate climatology | MAE hours, rank correlation across winters | 15 winters | 1 |
| 4 Class agreement | model class vs pre-registered class and vs documented practice (HS1362 zones, Epagri zoning) | accuracy, κ, confusion matrix | 18 sites | 0.5 |
| 5 Bloom | flowering start / 50 % vs Citra trial logs (if obtained), Kovaleski 2012–13, NPN records, Embrapa Pelotas | MAE days, bias, share within ±7 d | ≥8 site-years for a MAE with ~±3 d CI [INFERENCE from literature spreads] | 2 |
| 6 Harvest | harvest start/peak vs AMS shipment 10/50 % week and GA NASS 50 % week per year | MAE days, correlation of interannual anomalies | 10+ years FL and GA | 2 |
| 7 Risk frequencies | per-winter event probability vs station-observed event (freeze at bloom, heavy rain at harvest, heat at fruit) | Brier, reliability diagram, skill vs climatology | 15 winters × stations | 1.5 |
| 8 Report | `VALIDATION_PROTOCOL.md`, scores JSON, UI evidence badge | — | — | 1 |

Total ≈ 12.5 builder-days plus expert half-days; recommendation 2 loaders ≈ 3 days additional (NASS PDF parsing is the fiddly part), AMS API 1 day, NPN 0.5 day, literature table 0.5 day.

## 4. Achievable accuracy
With station-quality temperature and cultivar-specific calibration the literature floor is 2–5 days RMSE for bloom. This project has (a) ±1–1.5 °C Tmin bias and 55 km cells, (b) generic classes (SHB-early/mid, RE) rather than cultivars, (c) a fixed-offset chain (50–100 h chill → 150 GDD → +14/35 d) never fitted to data. Expect bloom-start MAE of 7–12 days after Tmin correction and cultivar-class GDD targets, worse before; harvest start ±10–14 days because fruit-development period varies 55–90 days by class and management. Class agreement should be the first pass/fail: ≥15/18 sites correct is a reasonable target; two-thirds-majority classifier is fragile near the 100/300 h cuts. Risk frequencies with 15 winters give probability resolution of ~0.07; Brier improvement over climatology is the honest claim, not calibrated probabilities. [INFERENCE] all numbers in this section.

## 5. Risks, unknowns, human decisions
- Cyanamide, tunnels and frost protection at trial sites shift observed bloom/harvest; truth must carry management flags or comparisons are biased early.
- Shipment curves lag harvest by days and mix regions; treat as ±1 week truth, use interannual anomalies rather than absolute dates.
- Florida NASS has no blueberry progress rows [verified for two 2024 issues]; Georgia does.
- USA-NPN coverage near panel sites may be zero; check before budgeting.
- Epagri historical data needs a request; Papanduva field records likely need Paul's Brazilian contacts.
- Decision needed: chill definition to validate (hours vs Dynamic Model) — validation step 3 can score both.
- Decision needed: whether to fit GDD/offset parameters to Citra data (turns model into a calibrated one; must then hold out years) or keep expert parameters and only validate.
- Cross-topic: disease and pollination-day metrics (other scouts) need RH/rain station truth from the same networks; Tmin correction changes chill and freeze counts jointly.
