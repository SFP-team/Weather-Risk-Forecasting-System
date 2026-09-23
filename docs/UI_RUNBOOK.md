# Climate workspace UI

Updated 2026-09-23 with the supplied lab logo and revised interface copy. This is a historical research workspace, not a cultivar recommendation or weather forecast. The frontend stays in vanilla JavaScript and uses system fonts, white panels, navy/blue navigation and categorical stage colours. The current design contract is in `UI_IMPLEMENTATION_PLAN.md`.

## Map-first workflow

- The world map supports mouse-wheel/trackpad scroll zoom while the pointer is over the map, click/drag pin placement, keyboard pan/zoom, Enter or Use map center, and a world reset. Scrolling outside the map scrolls the page. Saved markers and the local name/region/county filter select a draft location. Coordinate entry remains available without the map. **Analyze is explicit**; map movement does not call the archive.
- The draft pin is separate from the committed assessment. A new selection displays a notice naming the previous result. Cancel aborts the browser request and prevents late responses replacing a newer selection; it does not claim to stop server computation.
- Five keyboard-operable tabs organize the assessment: Overview, Season & exposures, Climate history, Soil & setup, Methods & data. Overview shows system hypothesis, assumed harvest, recurring-risk cards, descriptive exposure families and one planting guide. Definitions, uncertainty and excluded reasons expand on demand.
- Stage colours mean stage identity, not severity. Selected-winter cards compare with historical means; exact values, missingness and sources remain expandable. The `stage_risks_v2` production bar starts at budbreak, matching its backend metrics. No scientific value changed.
- Coverage badges distinguish daily records, hourly analysis, calendar applicability, planting and soil. The map's dashed source rectangle comes only from the returned hourly source cell; it is not parcel resolution or a global coverage layer.
- The connected API reads complete 2010–2025 hourly series from the existing checksummed land-hourly cache for unindexed cells. Existing indexed cells retain their normalized series. Missing/corrupt installed objects fail closed; absent hourly archives retain daily-only context. No network acquisition or synthesized hourly temperature.
- HTML export expands every view and definition, retains the selected winter/stage/chart labels and embeds `style.css` plus `cycle.css`. JSON keeps the original analysis and selected management/cycle metadata. The map itself is not exported; coordinates and source-cell provenance are.
- A browser-local place card resolves containing country/region and nearest represented settlement using Natural Earth. Saved site names remain dominant. Draft and assessment names are separate; stale lookups cannot rename a newer selection. JSON adds `location_context` without changing original `site`, science, planting or analysis ID. HTML retains the committed name and source caveats. No coordinate is sent to an external naming service.

## Map dependency and privacy

MapLibre GL JS 5.24.0 and the adapted Positron style are vendored with licenses and source hashes in `dist/vendor/map-assets.json`. OpenFreeMap supplies vector tiles/fonts/sprites; attribution remains visible. English names take priority, then romanized names, with local names only where neither exists. Requests disclose IP and viewed area to OpenFreeMap/CDN; see its [privacy policy](https://openfreemap.org/privacy/). No paid API key, telemetry, external geocoder or bulk tile cache.

`dist/geography/places-v1.json.gz` is a 2.97 MB public-domain Natural Earth derivative, decoded once in a modern browser. Sources, hashes, 250 m simplification and cartographic limits are in `dist/geography/provenance.json`; regenerate with `scripts/build-place-index.py`, retaining raw inputs on the designated server. Country/region require polygon containment, never a nearest-city inference. Ocean/unrepresented land and exact/overlapping boundaries remain unresolved. A city label requires represented land and distance ≤100 km. WebGL/name-data failure retains coordinates and saved analyses.

2026-09-23 verification: browser lookup across Iowa, Cairo, Tokyo, Dubai, Paris, both sides of Niagara, ocean and both Fiji dateline signs; country/region remained independent of nearest city. Real Iowa analysis displayed Near Mason City while original API site/coordinates and unavailable planting were unchanged. All 18 saved names persisted. Delayed out-of-order names left Tokyo selected and the prior Iowa report unchanged. Actual HTML/JSON downloads retained the name and original science identity. Blocked map library/geography retained usable coordinates and Papanduva. Desktop/mobile inspected, 390 px without overflow; three JS syntax checks passed. No backend tests rerun for this frontend change.

## Redesign verification

2026-09-22: checked all 18 presets across five views, 270 winter/stage views and 1,350 exact values, including 209 zeros and 22 unavailable entries. Tested keyboard tab/stage controls and selected winter/stage retention after management changes. All five views had no page overflow at 320/390/768/1440 px; desktop/mobile inspected. Real API checks covered daily-only land, shared-cell land with unknown planting region and offshore refusal. Synthetic failures covered tiles, Leaflet, API disconnection and a delayed response after cancellation/new selection. The normal browser session reported no page errors.

Actual downloaded HTML exposed all five views, expanded every detail and removed interactive buttons/selects. JSON production, planting and analysis ID matched the Homerville snapshot; both reports retained winter 2014, fruit and tunnel/pots, and HTML retained temperature/heat chart labels. JavaScript syntax checks passed. Backend code/results were unchanged, so backend tests were not rerun.

Hourly integration, 2026-09-22: 102 server tests passed. The reported 43.060861, -92.548828 coordinate and London/Chile/Nairobi/Sydney read 140,256 hourly records from existing data. All 18 saved production and annual summaries were unchanged; three reference sites passed raw/indexed parity. No transfer-counter or object-count change. Browser verified the reported coordinate, another actual map-click point, source grid and calendar without page errors. Only the private API was restarted; no hosted deployment.

## What works

- Coordinate inputs, map-pin selection, 18 locally searchable saved locations and four growing-system choices. Presets load `dist/snapshots/<site>.json` on demand from the small `dist/snapshots.json` index.
- Six exposure cards, monthly and annual charts, annual data table, mapped soil profiles with uncertainty, qualitative management notes and source provenance.
- Eighteen derived location summaries cover 2011–2025; Citra, Waldo and Papanduva each have 45 soil records. These are point summaries, not bulk weather, raw rasters or supervisor source materials.
- The private read-only API extracts daily and hourly records for supported land coordinates from existing archives. `hourly_archive.py` verifies each raw source object against a read-only SQLite checksum record. It does not create download clients, update acquisition state, fill missing chunks or persist duplicate global arrays.
- HTML/JSON export controls use the displayed analysis and selected system. The JSON contains the analysis ID and source hashes. Reports do not fit a new model or generate new numbers.
- **Production analysis (updated 2026-09-22):** `location-evidence-v4` attaches `open-field-production-v2`, primary profile `stage_risks_v2`. Headlines require at least 12 valid winters and ≥50% recurrence; all other assessments retain reasons. Disease is one family with flowering/fruit/harvest evidence. A shared backend catalogue supplies pollination, warm-midwinter, fruit-frost and stage dry-spell definitions to both views. Existing chill and stage dates are preserved. Choosing a tunnel or pot setup changes notes, not outdoor numbers.
- **Growing-cycle ruler (2026-09-15):** `dist/cycle.js` renders six aligned time lanes using the existing production result, with no UI library or new weather calculations. Select a stage button or lane for exposure details; native buttons also support keyboard activation. Choose a winter to see its modelled dates and exposures instead of aggregate frequencies. Small screens scroll the scale horizontally while controls and details reflow. The system hypothesis remains visible; the original tables are under an expandable details section.
- Solid bars show analysis windows. In the typical view, outlined spans run from p10 start to p90 end across valid winters, not confidence limits or one observed season. Risks use individual-winter stages, not that envelope. Evergreen-majority or unknown primary calendars cannot support crop-stage/chill-shortfall headlines; hypothetical calculations remain labelled. Warm-midwinter context is independent.
- HTML export saves the selected cycle and stage without inert stage buttons, expands the evidence tables, and preserves the live cycle/monthly/annual select labels. JSON retains the original production data plus `cycle_view` selection metadata. Actual downloaded HTML and JSON were checked in Chromium, including exact production-data parity; other browsers remain unverified.
- **Hourly source identity:** existing indexed cells retain their stored-series identity and sharing-site name. Other supported cells report Global hourly archive, source coordinates, displacement, UTC period, row count and a checksum identity over source objects and cell/window. All pins in one native 0.5° × 0.625° cell share weather values, not parcel observations. Evergreen-majority calendars remain inapplicable under the existing model.
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
../env/bin/python -m unittest test_hourly_archive test_evaluation_sites test_location_api test_production test_soil_pilot test_stage_scenarios test_reconcile_methods test_evidence_report test_recovery test_pilot test_global test_global_hourly test_observations test_regional_stations
```

The generator writes `reports/ui_snapshots.json` for the three references plus the panel. Copy it locally and run `python3 scripts/split_snapshots.py <file>` to produce `dist/snapshots.json` and `dist/snapshots/*.json`; review the public fields before committing. Never copy the raw archive into `dist/`. JavaScript checks:

```sh
node --check dist/app.js
node --check dist/cycle.js
node --check dist/map.js
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

The current design and interaction contract is in `UI_IMPLEMENTATION_PLAN.md`. The runtime remains the static frontend and standard-library Python HTTP adapter over the existing science code; durable jobs and authenticated hosted access are future work.
