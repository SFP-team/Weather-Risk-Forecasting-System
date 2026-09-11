# Soil pilot and consolidated data catalog

Started 2026-09-11. Bounded acquisition for the existing 14 weather pilot locations; no global soil rasters. Soil estimates are not field measurements or validated planting recommendations.

Verified outcome: **157/630 jobs acquired**, Citra/Papanduva/Waldo 45 each and Astin East 22. Worker stopped `blocked_source` at Astin East sand 5–15 cm Q0.05 after three timeouts (final HTTP 504). No soil tmux session remains. All 157 passed checksum/readback, 52 quantile pairs passed order/alignment checks; no source no-data records. Full server suite: 51 tests. See published `soil_audit.json` and `data_inventory.json` snapshots. Do not interpret this as complete coverage of 14 sites.

A cached rerun verified the existing 157 checksums and refused the exhausted job without resetting attempts or issuing another payload request. Recorded soil response bytes remained 99,068. This small figure is plausible for compressed tiny subsets; it excludes HTTP headers, metadata probes and package installation. The normalized dataset and raw rasters remain on the server; only aggregate audit/catalog snapshots are published.

## Scope and interpretation

- ISRIC SoilGrids 2.0, public WCS subsets, CC-BY-4.0 attribution.
- Five properties: pH in water, soil organic carbon, sand, silt and clay.
- Three distinct depths: 0–5, 5–15 and 15–30 cm. No depth averaging.
- Mean, 5th and 95th percentile prediction maps: 14 × 5 × 3 × 3 = **630 subset jobs**.
- pH map values /10 → pH; organic carbon dg/kg /10 → g/kg; texture g/kg /10 → percent. Preserve raw values as well as converted units. See [official layer definitions](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_01.html).
- Quantiles describe model prediction uncertainty, not annual variation, field measurement precision or a joint soil-property distribution. The mean need not lie within a central quantile interval in every distribution.
- The live service returns **EPSG:4326 geographic subsets**, approximately 0.0025-degree cells in this pilot, although native SoilGrids is a projected 250 m product. Recorded cell coordinates describe the returned raster. Native-grid parity/interpolation assessment remains outstanding; do not claim exact native-pixel extraction or 250 m field precision.
- No measured drainage, current moisture, irrigation-water chemistry, amended-bed or container-substrate data acquired. Soil pH is not container-leachate pH.

The [official access guide](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs_02.html) documents WCS/WebDAV alternatives to the paused REST service. WCS capabilities and DescribeCoverage were inspected live; GetCoverage TIFFs are decoded and range-checked before publication. DescribeCoverage generic range units are not authoritative soil units; property documentation controls conversions.

## Server paths

All paths below are relative to `/media/fpt/fpt2/Weather_Claude`:

| Content | Path |
|---|---|
| Immutable downloaded subsets | `data/raw/soilgrids/*.tif` |
| Normalized point/depth/statistic records | `data/normalized/soilgrids/pilot_soil.json` |
| Persistent job state, attempts and checksums | `state/soil_pilot.json` |
| Worker lock and log | `state/soil_pilot.lock`, `logs/soil_pilot.log` |
| Checksums/readback/quantile audit | `reports/soil_audit.json` |
| Consolidated weather/soil/station inventory | `reports/data_inventory.json` |

Worker is a dedicated `blueberry-soil` tmux session, with an exclusive file lock. It never touches other sessions. Each job has at most three persisted attempts; failures stop the worker for investigation. Successful cached files are checksum-checked on rerun. Mounted drive and disk floor are required. Requests are serial; per-response cap 2 MiB, aggregate payload cap 256 MiB (plus at most an in-flight response). Dependency downloads are separate from soil payload accounting.

Runtime addition: `rasterio==1.4.3` installed only inside the existing project virtual environment, not system Python. Local source and tests are in `pipelines/weather/soil_pilot.py`, `soil_audit.py`, `data_inventory.py` and `tests/weather/test_soil_pilot.py`.

## Inspect and audit

```sh
cd /media/fpt/fpt2/Weather_Claude
tail -n 5 logs/soil_pilot.log
tmux list-sessions
env/bin/python code/soil_audit.py
env/bin/python code/data_inventory.py
```

Inventory is a read-only catalog of existing raw/normalized families and reference/derived folders. It preserves original files, different weather grids and soil depths; it does not merge static soil with daily weather or duplicate bulk data. A snapshot taken while acquisition runs is not transactionally consistent across all directories. Refresh after completion. Logical file sizes are not exact network transfer or disk allocation.

Before resuming, inspect status and the worker/session. Never launch a duplicate or restart a completed acquisition. After diagnosing any terminal failure, obtain deliberate approval for resetting attempts or changing source; the worker does not silently reset them.

Tests cover pH/texture unit conversion, no-data propagation, out-of-range refusal, out-of-subset refusal and quantile request construction. Full acquisition testing also requires live source checks, successful audit and a cached rerun. These are engineering checks, not independent soil validation.
