# Climate evidence UI — first connected slice

Implemented 2026-09-11. This is a historical research dashboard, not a cultivar recommendation or a weather forecast. The supplied visual reference informed the monochrome palette, Geist typography, fine borders and compact controls; no reference attachment or brand assets are published.

## What works

- Coordinate inputs, three repeatable study-location presets and four growing-system choices.
- Six exposure cards, monthly and annual charts, annual data table, mapped soil profiles with uncertainty, qualitative management notes and source provenance.
- The three bundled summaries are Papanduva, Citra and Waldo, each with 2011–2025 weather and 45 soil records. They contain public derived point summaries, not bulk weather, raw rasters or supervisor source materials.
- A private read-only Python API extracts other coordinates from the existing archive. Exact pilot matches can include hourly chill and previously acquired soil; other coordinates explicitly show these as unavailable. No acquisition is triggered.
- HTML/JSON export controls use the displayed analysis and selected system. The JSON contains the analysis ID and source hashes. Reports do not fit a new model or generate new numbers.

## Two operating modes

**Private hosted snapshot UI:** `dist/` is the complete static application, configured by `.openai/hosting.json`. All three presets work without access to the university server. This deployment does **not** have a hosted connection to the archive; another coordinate displays a connection explanation instead of a substitute site. Site access is owner-private; sharing with a supervisor is a separate access decision.

**Connected local UI:** the same frontend sends requests through the local Node proxy and an authenticated SSH forward to the loopback-only Python API. It has been exercised with a new London coordinate as well as the presets. This is a single-analysis-at-a-time prototype, not an authenticated multi-user service or a durable job queue.

## Start connected mode

Use the access arrangements in `weather/SERVER_RUNBOOK.md`; no password or API secret belongs in commands committed here. On the server, check `tmux list-sessions` first and reuse an existing `blueberry-ui-api` session. Start one only if absent:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
tmux new-session -d -s blueberry-ui-api '../env/bin/python -u location_api.py >> ../logs/location_api.log 2>&1'
```

On the local machine, retain these two processes in separate terminals:

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -L 127.0.0.1:8787:127.0.0.1:8787 fpt@10.248.22.167
```

```sh
cd /Users/whiterose/Documents/Weather_Claude
node scripts/preview-ui.mjs
```

Open `http://127.0.0.1:5173/`. The connection strip indicates whether the private API is available. Stop the two local processes with Ctrl-C after use. Do not bind either service to a public interface. The local proxy accepts GET only, checks Host/Origin, and forwards only to its fixed loopback destination. That is a development boundary, not production authentication.

## Reproduce summaries and tests

Develop code under `pipelines/weather/` and copy reviewed changes explicitly into the server's `code/`, as in the server runbook. Stop/restart only this API's own session after a code change; do not disturb acquisition or unrelated server jobs.

On the server:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python location_api.py --snapshots
../env/bin/python -m unittest test_location_api test_soil_pilot test_stage_scenarios test_reconcile_methods test_evidence_report test_recovery test_pilot test_global test_observations test_regional_stations
```

The generator writes `reports/ui_snapshots.json`. Review its three-site scope and public fields before copying it to local `dist/snapshots.json`. Never copy the raw archive into `dist/`. JavaScript checks:

```sh
node --check dist/app.js
node --check scripts/preview-ui.mjs
```

## Scientific and engineering boundaries

- Complete windows are required. Flagged rainfall is not converted to zero; unavailable years/months stay null. Headline cards aggregate valid annual values and show the count. Monthly climatology requires all 15 complete monthly windows.
- Chill is hourly 0–7.2°C inclusive in a fixed reference winter. Dry spells are rain <1 mm within calendar-year boundaries; they are not measured crop drought or irrigation demand.
- Changing the growing system changes assumptions and soil interpretation, not ambient weather numbers. No calibrated tunnel transformations, severity score, soil suitability verdict or cultivar ranking exists.
- Soil estimates remain geographic WCS samples with native-grid/field validation pending. Soil acquisition remains source-blocked at 157/630 records; this UI does not retry it.
- Land support is cartographic, not parcel suitability. The source-labelled artificial “Null island” feature is excluded by `land-mask-v2`; small coasts/islands can remain unresolved.
- Missing hourly and missing/incomplete hourly windows need more granular status labels in the next schema revision. Existing stage-scenario reports are not integrated into this UI yet.
- Production work still requires authenticated archive connectivity, persisted jobs/cache, restart/concurrency tests, fuller per-section states, report download compatibility testing and a security review. No public data-host port was opened.

The staged target architecture remains in `UI_IMPLEMENTATION_PLAN.md`; this first slice deliberately uses a static frontend and standard-library Python HTTP adapter over the working science code.
