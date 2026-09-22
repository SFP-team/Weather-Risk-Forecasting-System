# Weather acquisition: server runbook

Started 2026-09-07. This is operational state and instructions, not a claim that the whole project is finished.

## Location and access

- Host: `fpt@10.248.22.167` (requires the appropriate university/private network).
- Project: `/media/fpt/fpt2/Weather_Claude`.
- Mount: `/media/fpt/fpt2`, verified as `/dev/nvme1n1p1` when this run began.
- Runtime: `/media/fpt/fpt2/Weather_Claude/env/bin/python`.
- Source snapshot: `/media/fpt/fpt2/Weather_Claude/code`.
- Credentials are not stored in this repository or this runbook.

Develop source under local `pipelines/weather` and tests under `tests/weather`; explicitly copy changed files into the server's `code` directory. Do not overwrite code used by a running worker without considering its loaded version. No Git commits or pushes have been made.

## Verified milestones

1. Preflight: project drive mounted, Python environment isolated, NASA public datastore reachable. Copernicus configuration absent at first check.
2. Source metadata: NASA POWER v10 daily meteorology at 0.5° latitude × 0.625° longitude; daily shortwave at 1° × 1°. UTC products. Source grids remain separate.
3. Smoke test: Citra and Papanduva, leap year 2020, daily fields and hourly temperature/dewpoint, checked against the matching NASA point API.
4. Pilot: all 14 source sites, 2010–2025, 42 Parquet files. Each site has 5,844 daily meteorology rows, 5,844 daily solar rows and 140,256 hourly rows. The audit found zero missing weather values.
5. Resume check: a repeated smoke run left downloaded bytes unchanged at 122,284,174; cached source objects were reused.
6. Geographic tests: 40 software/source probes, including climate/hemisphere/dateline/polar/ocean edge cases. These are not field trials or evidence of crop adaptation. Point-API parity was additionally checked at Chile, Germany, the Indian highland probe and New Zealand.
7. Global plan: 7,257 variable/spatial tiles. Normalized float32 values: 35,539,748,352 bytes. Conservative storage bound including raw chunks/overhead/pilot allowance: 137,747,659,844 bytes. Resource gates passed.
8. The global worker completed at 2026-09-07 23:23:55 UTC: all 7,257 tiles validated. Do not restart it.
9. Postprocessing verified the tile inventory and counts and passed coordinate extraction at all 14 pilot locations, an ocean negative control and three invalid-coordinate cases. Citra, Waldo and Papanduva demonstrations are in remote `reports/demos/`.

The aggregate audit recorded 18,824,365,917 weather response bytes and approximately 37.54 GB project disk use. Ten relative-humidity values are missing across the global native grid; all other selected fields have zero missing values. The rainfall maximum is 3,525.36 mm/day: this requires source/extreme-value investigation before rainfall-risk use. Passing the current numeric QC does not establish physical plausibility or station accuracy.

Twelve initial unit tests passed (nine pilot tests and three global tests). Real-data API/bulk parity, Parquet round trips, pilot checksums/date coverage and cache reuse were also checked. This is engineering/source consistency validation, not independent station or agronomic validation.

2026-09-08 02:45 UTC recovery audit: 24 tests passed (12 original, seven station-related and five downloader recovery tests). A synthetic child process was abruptly exited immediately before atomic publication; its final file was absent and its partial file present. A restarted client recovered successfully, then reused the completed file with no additional request or transfer-counter increment. No production worker or real weather payload was interrupted. Corrupt-cache refusal, missing-mount refusal and persisted five-attempt exhaustion also passed.

The audit found and fixed a retry defect: a terminal HTTP failure could previously be retried after reopening the client. `pilot.py` now refuses persisted `failed_terminal` jobs pending investigation, and a regression test verifies no request occurs on reopen. No real job states were reset. Server snapshot: 15,003 downloaded weather objects; 18,824,365,917 tracked bytes unchanged; no global worker process or tmux session; project drive approximately 2.9 TB free.

## Read current status

2026-09-08 supervisor demo: `env/bin/python code/evidence_report.py` from project root generates `reports/climate_evidence/climate_evidence.html` and JSON from stored data only. Three-site indicators now include monthly summaries, seasonal alignment, annual rain/cold/heat/dry-spell tables and reference-winter chill hours. 35 tests passed. Local copies are in `docs/weather/climate_evidence/`. No cultivar model, validated phenology or completed core sign-off is implied.

2026-09-08 05:16 UTC: 29 tests passed. Downloader now rejects HTML error bodies even when HTTP status is 200, records a terminal failure and does not publish the payload. Retry-After supports both numeric delays and HTTP dates, with past/invalid dates falling back to exponential backoff. Both behaviors have regression tests. Existing weather files and transfer totals remain unchanged. Remaining response testing: corrupted compressed source chunks; remaining deliverables: expanded indicator demonstrations and final audit. Core completion has not been declared.

2026-09-08 03:18 UTC update: 27 tests passed, including new numeric `Retry-After` handling, disk floor/quota and exclusive-lock tests. All 14 extraction controls passed again. Coordinate outputs now include `precip_suspect_extreme` and versioned screening metadata. A real land-cell control at −14.5°, 12.5° correctly reports one suspect precipitation day and `rainfall_risk_admissible: false`, preserving the original 2,500.73 mm value. This is an investigation threshold, not a universal plausibility guarantee. Derived risk consumers must honor this flag; historical exports made before this change need regeneration to gain it.

Run these **on the server**:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python pilot.py --scope status
../env/bin/python -m json.tool ../state/global.json
tail -n 10 ../logs/global.log
tmux list-sessions
df -h /media/fpt/fpt2/Weather_Claude
```

The global state includes completed/total tiles, PID and update time. A completed `tmux` session disappears; always inspect the persisted state and log before calling that a failure. `pilot.py --scope status` reports downloaded raw objects, not completed global output tiles.

### Land hourly cache worker (started 2026-09-21, user-authorized)

`code/global_hourly.py` fills `data/raw/zarr/met_hourly` (T2M, T2MDEW, 2010–2025) for every 5×5 block containing land: 3,479 of 8,468 blocks, 6,958 jobs, ≈ 29 GB measured-compression estimate, through the same checksummed `Downloads.get` path. No normalized copy is written. Plan: `state/global_hourly_plan.json`; state: `state/global_hourly.json`; log: `logs/global_hourly.log`; tile rows share the `tiles` table with the `met_hourly/` prefix. Session `blueberry-weather-hourly`.

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python global_hourly.py status
tail -n 5 ../logs/global_hourly.log
tmux list-sessions | grep hourly
```

Restart only if `state/global_hourly.json` shows `blocked` and the cause is understood; it resumes from the `tiles` table and skips validated jobs. Launch command:

```sh
tmux new-session -d -s blueberry-weather-hourly \
  'cd /media/fpt/fpt2/Weather_Claude/code && ../env/bin/python -u global_hourly.py run >> /media/fpt/fpt2/Weather_Claude/logs/global_hourly.log 2>&1'
```

The worker holds `state/worker.lock` while running. **Completed 2026-09-22 01:12 UTC**: 6,958 / 6,958 blocks validated in 4 h 39 min, 20,885 objects, 40.5 GB. Do not restart it; `status` should read `complete`.

The private API now reads this cache through `hourly_archive.py` for unindexed land cells. Deploy it alongside `location_api.py`; restart only `blueberry-ui-api`. The reader opens `jobs.sqlite` with `mode=ro`, verifies cached object hashes, and never instantiates the downloader. Six new synthetic archive regressions and real global-point checks passed on 2026-09-22; no acquisition counters changed. Existing indexed series remain the optimized path. API readiness does not imply scientific validation or soil/planting coverage.

## Important files

| Path relative to the remote project | Meaning |
|---|---|
| `state/smoke.json` | Smoke-test stage status |
| `state/pilot.json` | Full pilot stage status |
| `state/probes.json` | Geographic source/QC results |
| `state/global_download_plan.json` | Finite global manifest and estimates |
| `state/global.json` | Live global stage status |
| `state/jobs.sqlite` | Raw-object attempts/checksums/bytes and global tile status |
| `state/worker.lock` | Advisory lock preventing overlapping project workers |
| `reports/pilot_audit.json` | Detailed pilot quality and coverage audit |
| `reports/PILOT_AUDIT.md` | Readable pilot audit |
| `reports/parity/` | API-versus-bulk consistency tests |
| `reports/source_*.json` | Source metadata, units, grids and array chunk layout |
| `reports/environment.lock.txt` | Installed runtime dependency versions |
| `data/raw/zarr/` | Checksummed, reusable native source chunks |
| `data/raw/api/` | Original point-API comparison responses |
| `data/normalized/pilot/pilot/` | The full 14-site daily/hourly Parquet archive |
| `data/normalized/pilot/probes/` | Geographic source/QC probe extracts |
| `data/normalized/global/` | Completed global daily arrays; scientific validation remains pending |
| `reports/global_coverage.json` | Aggregate counts, extrema, transfer and disk audit |
| `reports/extraction_tests.json` | Coordinate and negative-control test results |
| `data/reference/ne_10m_land.geojson` | Checksummed Natural Earth 1:10 million cartographic land mask, not 10-metre resolution |

The API's solar output is MJ/m²/day, while the inspected bulk solar data is mean W/m². Conversion is explicitly ×0.0864 for a full daily interval and was checked against the API. Do not use the same factor for hourly quantities.

## Resume safely

Check state, PID/process command and the named `tmux` session first. Never launch a duplicate. Repair code defects locally, run the tests and deploy the changed files. Preserve already validated source files and output tiles.

If the global worker is not running and the failure has been diagnosed/resolved:

```sh
tmux new-session -d -s blueberry-weather-global \
  'cd /media/fpt/fpt2/Weather_Claude/code && ../env/bin/python -u global_daily.py run >> /media/fpt/fpt2/Weather_Claude/logs/global.log 2>&1'
```

The worker resumes from SQLite and verifies completed tile checksums. It has bounded request retries. Do not erase attempts or repeatedly restart a persistent authorization, rate-limit or source problem to evade the retry policy. A corrupt cache or changed source requires deliberate investigation and a versioned correction, not blanket deletion.

Global limits: 200 GiB project storage, 500 GiB transfer, at least 20% of the drive free. The code remains single-request/single-worker and uses small tiles. Download-time per-object payloads are bounded. Keep unrelated server jobs untouched.

## Work remaining after the global worker finishes

The current global worker performs per-variable QC, output read-back checksums, a final cross-variable temperature-order check and comparison with the original pilot extracts. Its `complete` status means this acquisition stage passed—not that all handoff criteria or the application are finished.

Remaining core handoff work includes:

- Completed: coordinate-extraction CLI with land/offshore handling and source-grid displacement. The cartographic mask can miss small islands/coastlines and is not a land-suitability assessment.
- Completed: aggregate coverage/gap report; still investigate the ten humidity gaps and extreme rainfall values at their exact coordinates/times.
- Completed: calendar-year climate demonstrations with attribution and no cultivar recommendations. Biological chill/phenology analyses remain separate.
- Independent station comparison where appropriate public data are accessible; preserve measured versus gap-filled observation flags. Current API/bulk comparisons are not independent validation.
- Completed: interrupted-publication, persisted retry/checksum/mount, numeric Retry-After, disk quota/floor and exclusive-lock tests using synthetic fixtures. Remaining tests include HTML-with-200/corrupt source decoding and HTTP-date Retry-After handling.
- Remaining mandatory demonstration details: tested bounded chill hours with explicit time/season convention, dry spells, monthly summaries and diverse-probe human-readable output. Annual Citra/Waldo/Papanduva summaries alone do not satisfy all demonstration requirements.
- Remaining final handoff: explicitly flag suspect rainfall in downstream extraction/indicators, audit artifact versions/resources and prepare final completion report. The ten humidity gaps and 89 rainfall cell-days above the investigation threshold are located in `anomaly_locations.json`; sampled API confirmation is documented in `VALIDATION_FINDINGS.md`.

Copernicus comparison remains conditional on the user's account/token and accepted dataset terms. Soil pilot is optional. Do not claim these are complete.

## Extract a coordinate

Run on the server; default output is a read-only metadata/QC summary for 2011–2025:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python postprocess.py extract --latitude 29.41 --longitude -82.17
```

Add `--export` to save the eight daily fields as Parquet plus provenance under `data/derived/extractions/`. Add `--include-padding` for 2010–2025. Unsupported ocean/unresolved-island requests are rejected without inland snapping. Weather availability is not a blueberry recommendation. `postprocess.py report` regenerates coverage counts; `postprocess.py demos` repeats the coordinate checks.

## Follow-up monitor

Regional validation update: a 2020 FAWN Citra / INMET Major Vieira and Rio Negrinho pilot is complete. See local `REGIONAL_STATION_PILOT.md` and server `reports/fawn_citra_2020.json` / `reports/inmet_near_papanduva_2020.json`. Station archives and flag-preserving extracts are retained. This is not full scientific sign-off: multi-year validation, rainfall semantics and correction evaluation remain pending. Do not equate pilot completion with global/core completion.

A thread follow-up was created with ID `complete-weather-data-acquisition`, scheduled every 30 minutes. It is instructed to inspect persisted state, advance/repair safe in-scope work, avoid duplicate workers, stay quiet for healthy non-actionable progress, and pause on completion or a genuine external blocker. It must not confuse a finished global worker with the full core handoff.

The server download continues independently of the laptop. Local follow-up checks require the desktop app/computer to be available and the server network to be reachable. No promise is made that checks can run while those dependencies are unavailable.
