# Climate workspace UI

Updated 2026-10-05 for the Regional evidence tab, which shows source-checked IBO report records beside the weather results. The production v3 payload, Overview decision strip, managed-cycle scan panel, 71 saved locations and literature benchmark page are unchanged. This is a historical research workspace, not a cultivar recommendation or weather forecast. The vanilla-JavaScript frontend uses the lab logo, system fonts, white/gray surfaces, black type, restrained blue pill controls and 28px shadowless cards/map. The current design contract is in `UI_IMPLEMENTATION_PLAN.md`.

## Map-first workflow

- Search places by name, region or country using the local Natural Earth reference. Results include geographic context; saved sites appear in their own group and browse list. Matching ignores accents/case and supports country aliases and multiple terms. Arrow keys, Enter and Escape operate results. Smaller villages and street addresses may be absent; coordinates remain available. Search needs no archive connection and sends no geocoder queries.
- A settlement selects its reference coordinates. A region/country frames its principal polygon extent, not every overseas territory; choose a point before analyzing. Analyze stays disabled until a valid point is selected. Browsing an area never invents region-wide weather or changes the previous report.
- The map supports wheel/pinch zoom, click/drag selection, keyboard pan/zoom, Enter or Use map center, and world reset. Scrolling outside it scrolls the page. **Analyze is explicit**; search and map movement do not call the archive.
- The draft pin is separate from the committed assessment. A new selection displays a notice naming the previous result. Cancel aborts the browser request and prevents late responses replacing a newer selection; it does not claim to stop server computation.
- Six keyboard-operable tabs organize the assessment: Overview, Season & exposures, Climate history, Soil & setup, Regional evidence, Methods & data. Overview opens with a four-part decision strip in the supervisor's reading order: production system, production window, top risks, planting guidance. Recurring-risk cards, descriptive exposure families, the planting guide and a one-line regional evidence summary follow. Definitions, uncertainty and excluded reasons expand on demand.
- Stage colours mean stage identity, not severity. Selected-winter cards compare with historical means; exact values, missingness and sources remain expandable. For profiles that require an applicable calendar, the production bar starts at budbreak, matching the backend metrics.
- Coverage badges distinguish daily records, hourly analysis, calendar applicability, planting and soil. The map's dashed source rectangle comes only from the returned hourly source cell; it is not parcel resolution or a global coverage layer.
- The connected API reads complete 2010–2025 hourly series from the existing checksummed land-hourly cache for unindexed cells. Existing indexed cells retain their normalized series. Missing/corrupt installed objects fail closed; absent hourly archives retain daily-only context. No network acquisition or synthesized hourly temperature.
- HTML export expands every view and definition, retains the selected winter/stage/chart labels and embeds `style.css`, `cycle.css` and `evidence.css`. JSON keeps the original analysis and selected management/cycle metadata, plus a separate `regional_evidence` object. Both formats keep every matched report record, whatever category filter is showing. The map itself is not exported; coordinates and source-cell provenance are.
- A browser-local place card resolves containing country/region and nearest represented settlement using Natural Earth. Saved site names remain dominant. Draft and assessment names are separate; stale lookups cannot rename a newer selection. JSON adds `location_context` without changing original `site`, science, planting or analysis ID. HTML retains the committed name and source caveats. No coordinate is sent to an external naming service.
- Search verification, 2026-09-23: city/region/country, multi-term, accent/alias, saved-name and no-match queries; Brazil keyboard selection; London search-to-hourly-analysis; Iowa area-to-point transition without extra requests; delayed query ordering and blocked-reference saved fallback. All five views fit 320/390/768/1440 px. Actual HTML/JSON export retained committed London identity while browsing another draft. Desktop/mobile inspected; JS syntax checks passed.
- Responsive verification, 2026-09-23: all five views with expanded details at 280/320/360/390/540/768/820/844/1024/1280/1440/1920/2560/3840 px, including two 1024 px heights, had no page overflow. Short landscape maps, height-bounded lists, narrow stacked controls, container-only map resize, 640 px high-DPI reflow, keyboard chart scrolling and standalone HTML at 320 px passed. Physical-device keyboard/notch and non-Chromium behavior remain unverified.

## Regional evidence

- **Library.** `dist/evidence/ibo-regional-v1.json` (version `ibo-regional-2026-10-05`) holds 91 records checked against the complete IBO 2023, 2025 and 2026 reports: 39 events, 42 practice records and 10 constraints, across 51 geographic scopes (33 regions, 18 countries) in 23 countries. A statement that several editions repeat stays one record with several citations (172 in total), so repeat mentions never look like separate events. Coverage is limited to selected benchmark regions. A missing record does not mean an event did not happen, and it does not mean low risk. The PDFs stay on the server; `dist/` holds paraphrases, page citations, reuse terms and PDF hashes.
- **View.** `dist/evidence.js` renders the tab and `dist/evidence.css` styles it. Filters cover harvest, management, weather and resources. Each card states the report scope, period, crop context, evidence type and limitations, and links to the cited pages. Records dated after the weather baseline (2025-12-31 for the presets) carry an "Outside" or "Partly outside weather baseline" tag. Report statements are context. They are not observations at the pin, loss probabilities or model inputs.
- **Matching.** Country records match the pin's containing country. Regional records also need the containing region polygon. `PlaceNames.lookup()` now returns that polygon's `region_id` and the SHA-256 of the uncompressed `places-v1.json.gz` bundle. The registry's `geography_reference` lists polygon IDs for the 33 regional scopes and the hash of the bundle they belong to. If the hashes differ, the panel shows no records rather than falling back to names. Names alone failed in testing, because the reference labels both Washington state and Washington, DC "Washington". After replacing the geography bundle, review the crosswalk and update its hash.
- **States.** Evidence follows the committed assessment, not the draft pin, and a slow library or place lookup cannot attach one place's reports to another place's result. Loading, missing library, mismatched geography, unresolved boundary and no curated records each show their own message. None of them changes the weather results.
- **Exports.** JSON adds `regional_evidence`: library version, matched records and sources, geographic identity and `weather_analysis_id`. HTML shows every matched record with details open and no scripts, even when the live view was filtered.
- **Verification, 2026-10-05.** In the browser, all 71 presets kept their weather payloads unchanged after evidence loaded; 61 matched report records and 10, including Papanduva and the Tasmania site, had no curated match. Six live coordinates (Gainesville, Lima, Huelva, Nairobi, Tbilisi and daily-only Bermuda) also kept their API payloads unchanged. Before the polygon-ID fix, Washington, DC received the Pacific Northwest heat-dome record; afterwards DC had no match and Seattle kept it. Fault checks covered a missing library, a malformed library, missing geography, a geography hash mismatch, delayed library and geography loads and draft-only pin changes. Weather stayed usable each time and no stale evidence appeared. All six tabs fit 390 px, keyboard tab navigation worked, and desktop and phone layouts were inspected. A Chao / Virú export made while the view was filtered kept all six records in JSON, with weather unchanged, and in standalone HTML (six cards, details open, no filters or scripts, no overflow at 390 px). `node --check` passed for `app.js`, `places.js` and `evidence.js`. No backend code changed, so the Python suite was not rerun.

## Map dependency and privacy

MapLibre GL JS 5.24.0 and the adapted Positron style are vendored with licenses and source hashes in `dist/vendor/map-assets.json`. OpenFreeMap supplies vector tiles/fonts/sprites; attribution remains visible. English names take priority, then romanized names, with local names only where neither exists. Requests disclose IP and viewed area to OpenFreeMap/CDN; see its [privacy policy](https://openfreemap.org/privacy/). No paid API key, telemetry, external geocoder or bulk tile cache.

`dist/geography/places-v1.json.gz` is a 2.97 MB public-domain Natural Earth derivative, decoded once in a modern browser. Sources, hashes, 250 m simplification and cartographic limits are in `dist/geography/provenance.json`; regenerate with `scripts/build-place-index.py`, retaining raw inputs on the designated server. Country/region require polygon containment, never a nearest-city inference. Ocean/unrepresented land and exact/overlapping boundaries remain unresolved. A city label requires represented land and distance ≤100 km. WebGL/name-data failure retains coordinates and saved analyses.

2026-09-23 verification: browser lookup across Iowa, Cairo, Tokyo, Dubai, Paris, both sides of Niagara, ocean and both Fiji dateline signs; country/region remained independent of nearest city. Real Iowa analysis displayed Near Mason City while original API site/coordinates and unavailable planting were unchanged. All 18 saved names persisted. Delayed out-of-order names left Tokyo selected and the prior Iowa report unchanged. Actual HTML/JSON downloads retained the name and original science identity. Blocked map library/geography retained usable coordinates and Papanduva. Desktop/mobile inspected, 390 px without overflow; three JS syntax checks passed. No backend tests rerun for this frontend change.

## Redesign verification

2026-09-22: checked all 18 presets across five views, 270 winter/stage views and 1,350 exact values, including 209 zeros and 22 unavailable entries. Tested keyboard tab/stage controls and selected winter/stage retention after management changes. All five views had no page overflow at 320/390/768/1440 px; desktop/mobile inspected. Real API checks covered daily-only land, shared-cell land with unknown planting region and offshore refusal. Synthetic failures covered tiles, Leaflet, API disconnection and a delayed response after cancellation/new selection. The normal browser session reported no page errors.

Actual downloaded HTML exposed all five views, expanded every detail and removed interactive buttons/selects. JSON production, planting and analysis ID matched the Homerville snapshot; both reports retained winter 2014, fruit and tunnel/pots, and HTML retained temperature/heat chart labels. JavaScript syntax checks passed. Backend code/results were unchanged, so backend tests were not rerun.

Hourly integration, 2026-09-22: 102 server tests passed. The reported 43.060861, -92.548828 coordinate and London/Chile/Nairobi/Sydney read 140,256 hourly records from existing data. All 18 saved production and annual summaries were unchanged; three reference sites passed raw/indexed parity. No transfer-counter or object-count change. Browser verified the reported coordinate, another actual map-click point, source grid and calendar without page errors. Only the private API was restarted; no hosted deployment.

## What works

- Coordinate inputs, map-pin selection, 71 locally searchable saved locations and four growing-system choices. Saved groups are Reference, Georgia, Central Florida and South Florida, then the four benchmark groups: US transect; Peru, Chile and Mexico; other Latin America; rest of world. Presets load `dist/snapshots/<site>.json` on demand from the small `dist/snapshots.json` index; benchmark files are named by benchmark id.
- Six exposure cards, monthly and annual charts, annual data table, mapped soil profiles with uncertainty, qualitative management notes and source provenance.
- Seventy-one derived location summaries cover 2011–2025; Citra, Waldo and Papanduva each have 45 soil records. These are point summaries, not bulk weather, raw rasters or supervisor source materials.
- The private read-only API extracts daily and hourly records for supported land coordinates from existing archives. `hourly_archive.py` verifies each raw source object against a read-only SQLite checksum record. It does not create download clients, update acquisition state, fill missing chunks or persist duplicate global arrays.
- HTML/JSON export controls use the displayed analysis and selected system. The JSON contains the analysis ID and source hashes. Reports do not fit a new model or generate new numbers.
- **Production analysis (updated 2026-09-28):** `location-evidence-v5` attaches `open-field-production-v3`, primary profile `stage_thermal_v3`. Stages after budbreak follow degree-days, disease weather uses the hourly infection model, and `chill_clock` states whether the chill-triggered calendar applies, with reasons. Headlines still require at least 12 valid winters and ≥50% recurrence. "Transitional" is shown as "No two-thirds majority" with per-class counts, and the calendar is then marked tentative. Choosing a tunnel or pot setup changes notes, not outdoor numbers. Method details: [production README](weather/production/README.md).
- **Managed-cycle scan (2026-09-28):** where the chill clock does not apply, the Season view opens with the scan panel and the decision strip reports favourable flowering and harvest months as a management scenario. Elsewhere the panel follows the cycle view as "If managed as an evergreen cycle". The 24-cell strip marks favourable starts, recurring crop loss, not-rankable starts and stalled cycles. The table lists per-start dates, measures and recurring risks.
- **No-window explanations (2026-10-05):** when the scan has no favourable start, the Production window card and the scan panel name the cause instead of printing Unavailable. There are three causes. The site may be too cool to finish a cycle: a stage misses its heat requirement within the 300-day stage horizon in at least half the winters. Bud, flowering or fruit freeze may recur at every assessable start. Or too few cycles complete. Top risks then reads "Not assessed", or lists the recurring freeze families with their start counts, never "None recurring". Scan-primary windows also quote the `chill_clock` reason. Verified live on 2026-10-05: a Cascade Range pin at 46.738, −121.456 (weather cell 46.5, −121.25) and Naantali, Finland show "No complete crop cycle". Lynden, WA keeps May–Jun flowering and Jul–Sep harvest and now states "Only 11/15 winters produce a chill-triggered calendar". Arcadia gains its reason text and Waldo is unchanged. A modified copy of the payload covered the freeze branch. No page errors and no overflow at 390 px.
- **Literature benchmark:** Methods & data links to `benchmark.html`, the 53-site comparison of modelled and published system, bloom and harvest months. It is regional literature, not field validation of these grid cells.
- **Regional evidence (2026-10-05):** a separate tab lists source-checked IBO report records for the pin's country and region, apart from the calculated risks. See Regional evidence above.
- **Growing-cycle ruler (2026-09-15):** `dist/cycle.js` renders six aligned time lanes using the existing production result, with no UI library or new weather calculations. Select a stage button or lane for exposure details; native buttons also support keyboard activation. Choose a winter to see its modelled dates and exposures instead of aggregate frequencies. Small screens scroll the scale horizontally while controls and details reflow. The system hypothesis remains visible; the original tables are under an expandable details section.
- Solid bars show analysis windows. In the typical view, outlined spans run from p10 start to p90 end across valid winters, not confidence limits or one observed season. Risks use individual-winter stages, not that envelope. Evergreen-majority or unknown primary calendars cannot support crop-stage/chill-shortfall headlines; hypothetical calculations remain labelled. Warm-midwinter context is independent.
- HTML export saves the selected cycle and stage without inert stage buttons, expands the evidence tables, and preserves the live cycle/monthly/annual select labels. JSON retains the original production data plus `cycle_view` selection metadata. Actual downloaded HTML and JSON were checked in Chromium, including exact production-data parity; other browsers remain unverified.
- **Hourly source identity:** existing indexed cells retain their stored-series identity and sharing-site name. Other supported cells report Global hourly archive, source coordinates, displacement, UTC period, row count and a checksum identity over source objects and cell/window. All pins in one native 0.5° × 0.625° cell share weather values, not parcel observations. Evergreen-majority calendars remain inapplicable under the existing model.
- **Establishment window (2026-09-22):** a separate source-labelled regional panel, not a bearing-cycle lane. Florida: mid-December–mid-February; Georgia: winter, displayed approximately December–February; Santa Catarina: winter while dormant, displayed approximately June–August. The latter two are season conventions, not precise source-specified dates. Unknown-region pins decline rather than infer geography from a weather cell. Sources and conditions are in the panel and [method notes](weather/production/README.md).
- **Daily-only fallback:** complete daily Tmax >21 °C counts for 15 Nov–15 Feb north / 15 May–15 Aug south, labelled **days**, never estimated hours. Chill-triggered stages stay unavailable. The API reads 2010 padding for the first northern winter.
- Results older than `location-evidence-v5` / `open-field-production-v3` are refused with a refresh explanation. Regenerate snapshots and update the API together.
- API errors are separated. The preview proxy marks its own tunnel-down reply with `code: 'archive_unavailable'` and the UI shows the archive as unavailable. Other 503 or 429 replies show the server's busy message. Non-JSON bodies are treated as an unavailable archive, not parsed.
- **Verification (2026-09-22):** 18 presets rendered; 135 selected winter/stage views and 855 displayed values matched the payload; empty/evergreen states, keyboard activation and management-state retention passed. Actual HTML/JSON downloads retained planting, winter 2014, fruit stage, tunnel/pots and chosen chart labels. Desktop/mobile inspected; 320/390/768/1440 px had no page overflow. Live shared-cell and daily-only coordinates both passed after restarting only `blueberry-ui-api`. Backend suite: 96 passing; 39 production/API tests passed again after fixing missing analysis-version metadata.
- **Verification (2026-09-28):** the UI agent checked Waldo, Arcadia, PF Berry and Georgia against the v3 payload, winter and stage retention across views, export names `blueberry-<site>-<analysis id>`, intercepted 503/502/HTML error bodies, cancel and a v4 refusal. `node --check` passed for `dist/app.js`, `dist/cycle.js` and `scripts/preview-ui.mjs`. After the final snapshot regeneration, Chao and Arcadia presets and a live Clinton, NC coordinate (7.8 s, `blueberry-ui-api` restarted only) rendered without page errors. All five views had no page overflow at 390 px, and the benchmark page fitted 390 px.

## Two operating modes

**Hosted snapshot UI:** `dist/` contains the updated static application and 71 saved presets. The existing owner-private Sites deployment has **not** been redeployed; its old content is not updated by local edits or a GitHub push. No public/private-network archive bridge has been deployed. The user authorized GitHub publication on 2026-09-22, not hosted redeployment.

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
../env/bin/python benchmark.py                   # reports/benchmark/benchmark.{html,json}; copy the HTML to dist/benchmark.html
../env/bin/python -m unittest discover -p "test_*.py"
```

The generator writes `reports/ui_snapshots.json` for the three references, the panel and the 53 benchmark sites in `benchmark_sites.json`. Copy it locally and run `python3 scripts/split_snapshots.py <file>` to produce `dist/snapshots.json` and `dist/snapshots/*.json`; review the public fields before committing. Never copy the raw archive into `dist/`. JavaScript checks:

```sh
node --check dist/app.js
node --check dist/cycle.js
node --check dist/map.js
node --check dist/places.js
node --check dist/evidence.js
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
