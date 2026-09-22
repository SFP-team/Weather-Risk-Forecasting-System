# Climate evidence UI — first connected slice

Implemented 2026-09-11. This is a historical research dashboard, not a cultivar recommendation or a weather forecast. The supplied visual reference informed the monochrome palette, Geist typography, fine borders and compact controls; no reference attachment or brand assets are published.

## What works

- Coordinate inputs, 18 grouped presets (Reference: Citra, Waldo, Papanduva; Georgia; Central Florida; South Florida) and four growing-system choices. Presets load `dist/snapshots/<site>.json` on demand from the small `dist/snapshots.json` index.
- Six exposure cards, monthly and annual charts, annual data table, mapped soil profiles with uncertainty, qualitative management notes and source provenance.
- Eighteen derived location summaries cover 2011–2025; Citra, Waldo and Papanduva each have 45 soil records. These are point summaries, not bulk weather, raw rasters or supervisor source materials.
- The private read-only API extracts other coordinates from the existing archive. Hourly production analysis is available within the 19 indexed source cells; the completed global hourly cache is not yet exposed for arbitrary cells. Missing hourly data does not trigger acquisition.
- HTML/JSON export controls use the displayed analysis and selected system. The JSON contains the analysis ID and source hashes. Reports do not fit a new model or generate new numbers.
- **Production analysis (updated 2026-09-22):** `location-evidence-v4` attaches `open-field-production-v2`, primary profile `stage_risks_v2`. Headlines require at least 12 valid winters and ≥50% recurrence; all other assessments retain reasons. Disease is one family with flowering/fruit/harvest evidence. A shared backend catalogue supplies pollination, warm-midwinter, fruit-frost and stage dry-spell definitions to both views. Existing chill and stage dates are preserved. Choosing a tunnel or pot setup changes notes, not outdoor numbers.
- **Growing-cycle ruler (2026-09-15):** `dist/cycle.js` renders six aligned time lanes using the existing production result, with no UI library or new weather calculations. Select a stage button or lane for exposure details; native buttons also support keyboard activation. Choose a winter to see its modelled dates and exposures instead of aggregate frequencies. Small screens scroll the scale horizontally while controls and details reflow. The system hypothesis remains visible; the original tables are under an expandable details section.
- Solid bars show analysis windows. In the typical view, outlined spans run from p10 start to p90 end across valid winters, not confidence limits or one observed season. Risks use individual-winter stages, not that envelope. Evergreen-majority or unknown primary calendars cannot support crop-stage/chill-shortfall headlines; hypothetical calculations remain labelled. Warm-midwinter context is independent.
- HTML export saves the selected cycle and stage without inert stage buttons, expands the evidence tables, and preserves the live cycle/monthly/annual select labels. JSON retains the original production data plus `cycle_view` selection metadata. Actual downloaded HTML and JSON were checked in Chromium, including exact production-data parity; other browsers remain unverified.
- **Evaluation panel and hourly by cell (2026-09-15):** `pipelines/weather/evaluation_sites.py` defines the 15 southeastern panel sites (pilot farms by their stored pins; towns by city centre) and indexes every stored hourly series by MERRA-2 source cell. `location_api.py` resolves hourly for any pin through that index, so a coordinate inside a stored cell gets the production packet even when it is not a named site; the availability strip then reads `HOURLY / cell <lat>, <lon> · shared with <site> · <km>`. All pins in one 0.5° × 0.625° cell receive identical chill and calendar; that is the data resolution, not a site measurement. Pins outside any stored cell stay daily-only. Evergreen-majority results (for example Arcadia) keep the production tables but the cycle ruler declines, as designed.
- **Establishment window (2026-09-22):** a separate source-labelled regional panel, not a bearing-cycle lane. Florida: mid-December–mid-February; Georgia: winter, displayed approximately December–February; Santa Catarina: winter while dormant, displayed approximately June–August. The latter two are season conventions, not precise source-specified dates. Unknown-region pins decline rather than infer geography from a weather cell. Sources and conditions are in the panel and [method notes](weather/production/README.md).
- **Daily-only fallback:** complete daily Tmax >21 °C counts for 15 Nov–15 Feb north / 15 May–15 Aug south, labelled **days**, never estimated hours. Chill-triggered stages stay unavailable. The API reads 2010 padding for the first northern winter.
- Old result versions are refused with a refresh explanation. Regenerate snapshots and update the API together; never label old risk rankings as v2.
- **Verification (2026-09-22):** 18 presets rendered; 135 selected winter/stage views and 855 displayed values matched the payload; empty/evergreen states, keyboard activation and management-state retention passed. Actual HTML/JSON downloads retained planting, winter 2014, fruit stage, tunnel/pots and chosen chart labels. Desktop/mobile inspected; 320/390/768/1440 px had no page overflow. Live shared-cell and daily-only coordinates both passed after restarting only `blueberry-ui-api`. Backend suite: 96 passing; 39 production/API tests passed again after fixing missing analysis-version metadata.

## Two operating modes

**Hosted snapshot UI:** `dist/` contains the updated static application and 18 saved presets. The existing owner-private Sites deployment has **not** been redeployed; its old content is not updated by local edits or a GitHub push. No public/private-network archive bridge has been deployed. The user authorized GitHub publication on 2026-09-22, not hosted redeployment.

**Connected local UI:** the same frontend sends requests through the local Node proxy and an authenticated SSH forward to the loopback-only Python API. It has been exercised with a new London coordinate as well as the presets. This is a single-analysis-at-a-time prototype, not an authenticated multi-user service or a durable job queue.

## Start connected mode

Use the access arrangements in `weather/SERVER_RUNBOOK.md`; no password or API secret belongs in commands committed here. On the server, check `tmux list-sessions` first and reuse an existing `blueberry-ui-api` session. Start one only if absent:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
tmux new-session -d -s blueberry-ui-api '../env/bin/python -u location_api.py >> ../logs/location_api.log 2>&1'
```

From the local checkout root, retain these two processes in separate terminals:

```sh
ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=30 \
  -L 127.0.0.1:8787:127.0.0.1:8787 fpt@10.248.22.167
```

```sh
node scripts/preview-ui.mjs
```

Open `http://127.0.0.1:5173/`. The connection strip indicates whether the private API is available. Stop the two local processes with Ctrl-C after use. Do not bind either service to a public interface. The local proxy accepts GET only, checks Host/Origin, and forwards only to its fixed loopback destination. That is a development boundary, not production authentication.

## Reproduce summaries and tests

Develop code under `pipelines/weather/` and copy reviewed changes explicitly into the server's `code/`, as in the server runbook. Stop/restart only this API's own session after a code change; do not disturb acquisition or unrelated server jobs.

On the server:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python evaluation_sites.py index      # rebuild config/hourly_index.json after any hourly change
../env/bin/python evaluation_sites.py fetch      # bounded: only cells without a stored series; needs explicit authorization
../env/bin/python location_api.py --snapshots
../env/bin/python -m unittest test_evaluation_sites test_location_api test_production test_soil_pilot test_stage_scenarios test_reconcile_methods test_evidence_report test_recovery test_pilot test_global test_global_hourly test_observations test_regional_stations
```

The generator writes `reports/ui_snapshots.json` for the three references plus the panel. Copy it locally and run `python3 scripts/split_snapshots.py <file>` to produce `dist/snapshots.json` and `dist/snapshots/*.json`; review the public fields before committing. Never copy the raw archive into `dist/`. JavaScript checks:

```sh
node --check dist/app.js
node --check dist/cycle.js
node --check scripts/preview-ui.mjs
```

## Scientific and engineering boundaries

- Complete windows are required. Flagged rainfall is not converted to zero; unavailable years/months stay null. Headline cards aggregate valid annual values and show the count. Monthly climatology requires all 15 complete monthly windows.
- Chill is hourly 0–7.2°C inclusive in a fixed reference winter. Dry spells are rain <1 mm within calendar-year boundaries; they are not measured crop drought or irrigation demand.
- Changing the growing system changes assumptions and soil interpretation, not ambient weather numbers. No calibrated tunnel transformations, severity score, soil suitability verdict or cultivar ranking exists.
- Soil estimates remain geographic WCS samples with native-grid/field validation pending. Soil acquisition remains source-blocked at 157/630 records; this UI does not retry it.
- Land support is cartographic, not parcel suitability. The source-labelled artificial “Null island” feature is excluded by `land-mask-v2`; small coasts/islands can remain unresolved.
- Missing hourly availability, incomplete winters and per-metric gaps are distinct in the calculations; durable per-section jobs/cache and a broader geographic adapter are still pending. Establishment guidance does not validate field suitability; the stage calendar remains assumption-based. The earlier standalone stage-scenario report is historical.
- Production work still requires authenticated archive connectivity, persisted jobs/cache, restart/concurrency tests, fuller per-section states, broader cross-browser report compatibility testing and a security review. No public data-host port was opened.

The staged target architecture remains in `UI_IMPLEMENTATION_PLAN.md`; this first slice deliberately uses a static frontend and standard-library Python HTTP adapter over the working science code.
