# Analogue data sources (small-first)

Monthly climatology is the globe screen. Hourly temperature is the fingerprint for the shortlist only. Do not download global ERA5-Land on day one.

## What the code actually fetches

| Source | Role | How |
|---|---|---|
| NASA POWER climatology | Working v0 monthly Tmin/Tmax/RH/precip/SW/wind | Point REST, cached under `data/analogue/climatology` |
| NASA POWER daily | Optional multi-year spine | Same API, not called in the default build |
| CHELSA v2.1 | Commercial-ok 1 km monthly screen (CC0) | Local GeoTIFF extract only. Place files under `data/analogue/chelsa`. |
| CHIRPS v3 | Rain fingerprint | Local files under `data/analogue/chirps` |
| ERA5-Land hourly | Chill portions, frost nights, heat, VPD | CDS request payload for shortlisted cells. Not auto-downloaded. |
| AgERA5 daily | ET0, VPD-at-Tmax, wet-hour fraction | CDS request payload. Not a chill substitute. |
| SoilGrids REST | pH, SOC, clay at the point | Weight = 0 under substrate |
| OpenTopoData Copernicus 30 m | Elevation | Point REST |
| GHCN / FAWN / INIA / SIAR | Station spine | Documented; disagreement makes the pixel untrusted |

## What we will not ship

- WorldClim without written permission (`info@worldclim.org`)
- PRISM without a commercial conversation
- ERA5/AgERA5 precip as rain truth
- NASA POWER as a fake 1 km grid
- Open-Meteo free tier for a commercial launch
- Köppen or USDA zone as the model

## Licenses (MVP)

- CHELSA: CC0
- CHIRPS: public domain / CC-BY
- ERA5-Land / AgERA5: Copernicus CC-BY
- NASA POWER: CC-BY
- SoilGrids: CC-BY

## Trust rule

If CHELSA or ERA5-Land and the nearest 10-year station disagree on chill or harvest rain by more than the set band, the pixel is **untrusted**, not 85% similar.

## Structure transfer (not climate data)

How tunnels, covers, and pots change weather exposure is in [structure-weather.md](structure-weather.md). Those effects are residual-risk bands, not 0/1 multipliers.
