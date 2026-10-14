# Climate workspace UI

Updated 2026-10-12 for the corrected managed-cycle scan accounting, request safety in the preview proxy and API, the supervised API service and scheduled evidence jobs. The Regional evidence tab (2026-10-05) shows source-checked IBO report records beside the weather results. This is a historical research workspace, not a cultivar recommendation or weather forecast. The vanilla-JavaScript frontend uses the lab logo, system fonts, white/gray surfaces, black type, restrained blue pill controls and 28px shadowless cards/map. The current design contract is in `UI_IMPLEMENTATION_PLAN.md`.

For a plain-language explanation of the current app, read the [user guide](APP_USER_GUIDE.md). It includes calendar requirements, missing-result meanings, and the reported Near Yakima example.

## Map-first workflow

- Search places by name, region or country. Towns and villages come from a GeoNames index of 5,170,300 current populated places on the archive server (`/api/places`); regions and countries, with their map outlines, come from the local Natural Earth reference. Results include county, region and country; saved sites appear in their own group and browse list. Matching ignores accents and case, reads every word as a word prefix and accepts alternate and local-script names, so `Jaiba`, `alma g` and `北京` all work. Arrow keys, Enter and Escape operate results. Street addresses and farm names are not searchable; coordinates and the map remain available. Without the archive connection the search falls back to the 7,295 larger Natural Earth towns and says so. No third-party geocoder receives queries.
- A settlement selects its reference coordinates. A region/country frames its principal polygon extent, not every overseas territory; choose a point before analyzing. Analyze stays disabled until a valid point is selected. Browsing an area never invents region-wide weather or changes the previous report.
- The map supports wheel/pinch zoom, click/drag selection, keyboard pan/zoom, Enter or Use map center, and world reset. Scrolling outside it scrolls the page. **Analyze is explicit**; map movement never calls the archive, and search asks only the place index, never for weather.
- The draft pin is separate from the committed assessment. A new selection displays a notice naming the previous result. Cancel aborts the browser request and prevents late responses replacing a newer selection; it does not claim to stop server computation.
- Eight keyboard-operable tabs organize the assessment: Overview, Season ribbon, Every winter, Season & exposures, Climate history, Soil & setup, Regional evidence, Methods & data. Overview opens with a four-part decision strip in the supervisor's reading order: production system, production window, top risks, planting window. Recurring-risk cards, descriptive exposure families, the planting window panel and a one-line regional evidence summary follow. The planting panel shows the window calculated from modelled budbreak, a "Published season · <region>" box for registered Florida, Georgia and Santa Catarina saved locations, and a "Rule, assumptions and limits" fold. Definitions, uncertainty and excluded reasons expand on demand.
- Season ribbon and Every winter (2026-10-14) come from `dist/season-views.js` and `dist/season.css`. They draw the production result that Season & exposures uses and change no number.
  - **Season ribbon:** one band for all winters, split each day by how many winters were in each stage, with grey hatching for winters without a calendar. Ticks give each transition's median date and 10th to 90th percentile range. Above the band are the planting rule, the published planting season and grower bloom and harvest months; counted risks sit below their stage, one square per winter.
  - **Published months:** `dist/benchmark-calendars.json`, written by `python3 scripts/build_benchmark_calendars.py` from `pipelines/weather/benchmark_sites.json`; rerun it after editing the registry. A site uses its own benchmark entry, otherwise the nearest benchmark site within 10 km. Each month is placed within half a year of the matching model window, so late northern and southern cross-year harvests sit beside the model.
  - **Every winter:** one row per winter, ordered by winter or budbreak, with frost, heat and heavy-rain marks that equal the risk counts, and each winter's chill hours.
  - Sites without an applicable chill-triggered calendar get an explanation and a link to the managed-cycle scan.
- Stage colours mean stage identity, not severity. Selected-winter cards compare with historical means; exact values, missingness and sources remain expandable. For profiles that require an applicable calendar, the production bar starts at budbreak, matching the backend metrics.
- Coverage badges distinguish daily records, hourly analysis, calendar applicability, planting and soil. The planting chip reads "Calculated planting window" or "No calculated planting window". The map's dashed source rectangle comes only from the returned hourly source cell; it is not parcel resolution or a global coverage layer.
- The connected API reads complete 2010–2025 hourly series from the existing checksummed land-hourly cache for unindexed cells. Existing indexed cells retain their normalized series. Missing/corrupt installed objects fail closed; absent hourly archives retain daily-only context. No network acquisition or synthesized hourly temperature.
- HTML export expands every view and definition, retains the selected winter/stage/chart labels and embeds `style.css`, `cycle.css`, `evidence.css` and `season.css`. JSON keeps the original analysis and selected management/cycle metadata, plus a separate `regional_evidence` object. Both formats keep every matched report record, whatever category filter is showing. The map itself is not exported; coordinates and source-cell provenance are.
- A browser-local place card resolves containing country/region and nearest represented settlement using Natural Earth. Saved site names remain dominant. Draft and assessment names are separate; stale lookups cannot rename a newer selection. JSON adds `location_context` without changing original `site`, science, planting or analysis ID. HTML retains the committed name and source caveats. No coordinate is sent to an external naming service.
- Search verification, 2026-09-23: city/region/country, multi-term, accent/alias, saved-name and no-match queries; Brazil keyboard selection; London search-to-hourly-analysis; Iowa area-to-point transition without extra requests; delayed query ordering and blocked-reference saved fallback. All five views fit 320/390/768/1440 px. Actual HTML/JSON export retained committed London identity while browsing another draft. Desktop/mobile inspected; JS syntax checks passed.
- Responsive verification, 2026-09-23: all five views with expanded details at 280/320/360/390/540/768/820/844/1024/1280/1440/1920/2560/3840 px, including two 1024 px heights, had no page overflow. Short landscape maps, height-bounded lists, narrow stacked controls, container-only map resize, 640 px high-DPI reflow, keyboard chart scrolling and standalone HTML at 320 px passed. Physical-device keyboard/notch and non-Chromium behavior remain unverified.
- Planting window verification, 2026-10-12: Waldo, Alma, Papanduva, Burgaw, Arcadia, River Valley, a live Clinton, NC pin and Waldo winter 2011 at 1440 and 390 px. No page errors, CSP violations or page overflow. The Season timeline's Planting lane, the published season box and the not-applicable states rendered. 34 UI tests and `node --check` passed. 251 server tests passed in a staging copy; only `blueberry-ui-api` was restarted, and the live API returned 30 Sep to 14 Dec for an Alma coordinate.
- 50 h chill requirement verification, 2026-10-12: River Valley, Waldo, Papanduva and Arcadia at 1440 and 390 px showed the new results and the badge "50 h chill requirement". No page errors, CSP violations or page overflow. 34 UI tests passed. 251 server tests passed in staging; legacy parity with `stage_risks_v2` held on 18 sites with 0 differences; only `blueberry-ui-api` was restarted. All 71 snapshots differ only inside the production and planting blocks and `analysis_id`.
- IBO 2024 report verification, 2026-10-12: the Regional evidence tab lists "report editions 2023, 2024, 2025, 2026" and the 2024 source with "Reuse with attribution (stated on printed p. 235; PDF p. 118)". Chao, Moguer, Agadir, Coffs Harbour, Mengzi, Qingdao, Marondera, Wolseley, Vechta, Ohaupo and Burgaw all showed 2024 citations, with no page errors or overflow at 1440 and 390 px. 34 UI tests passed, including the validator test.
- Season ribbon and Every winter verification, 2026-10-14: in the browser all 71 saved locations rendered; 50 drew both views and 21 explained the missing calendar. No text fell outside a chart, lane labels did not overlap, published bloom and harvest months drew one band per run of months, and there were no page errors. Waldo, Alma, Pelotas, Ovalle (3 winters without a calendar), Chao (no calendar), a live pin 5.7 km from Alma, the growing-setup note, the HTML export, keyboard tabs and 390 px passed. 42 UI tests passed. The server copy was updated with identical files, and a browser at the UF address drew the ribbon.

## Regional evidence

- **Library.** `dist/evidence/ibo-regional-v1.json` (version `ibo-regional-2026-10-12b`) holds 156 records checked against the complete IBO 2023, 2024, 2025 and 2026 reports: 67 events, 72 practice records and 17 constraints, across 52 geographic scopes (33 regions, 19 countries) in 23 countries. A statement that several editions repeat stays one record with several citations (301 in total: 2023 49, 2024 127, 2025 79, 2026 46), so repeat mentions never look like separate events. The 2024 report, added on 2026-10-12, brought 65 new records and 46 new citations on 43 existing records; the audit file with every accepted quote and the rejected items is `docs/research/2026-10-05/ibo_2024_extraction.json`. The 2026-10-12 review corrected 15 records against the server's report text (listed in `docs/research/2026-10-12/README.md`). The validator now strips control, zero-width and bidirectional characters and enforces text length limits. Coverage is limited to selected benchmark regions. A missing record does not mean an event did not happen, and it does not mean low risk. The PDFs stay on the server; `dist/` holds paraphrases, page citations, reuse terms and PDF hashes.
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

- Place search, map-pin selection and four growing-system choices. Search lists GeoNames towns and villages from the server, Natural Earth regions and countries, and a typed or pasted coordinate pair. Since 2026-10-14 the panel has no saved locations, coordinate fields or search help text, and every result comes from the archive API.
- Six exposure cards, monthly and annual charts, annual data table, mapped soil profiles with uncertainty, qualitative management notes and source provenance.
- Soil records exist only at the exact Citra, Waldo and Papanduva pilot points (45 each). The API matches soil by exact coordinates, so a searched place shows none.
- The private read-only API extracts daily and hourly records for supported land coordinates from existing archives. `hourly_archive.py` verifies each raw source object against a read-only SQLite checksum record. It does not create download clients, update acquisition state, fill missing chunks or persist duplicate global arrays.
- HTML/JSON export controls use the displayed analysis and selected system. The JSON contains the analysis ID and source hashes. Reports do not fit a new model or generate new numbers.
- **Production analysis (updated 2026-09-28):** `location-evidence-v5` attaches `open-field-production-v3`, primary profile `stage_thermal_v3`. Stages after budbreak follow degree-days, disease weather uses the hourly infection model, and `chill_clock` states whether the chill-triggered calendar applies, with reasons. Headlines still require at least 12 valid winters and ≥50% recurrence. "Transitional" is shown as "No two-thirds majority" with per-class counts, and the calendar is then marked tentative. Choosing a tunnel or pot setup changes notes, not outdoor numbers. Method details: [production README](weather/production/README.md).
- **Managed-cycle scan (2026-09-28):** where the chill clock does not apply, the Season view opens with the scan panel and the decision strip reports favourable flowering and harvest months as a management scenario. Elsewhere the panel follows the cycle view as "If managed as an evergreen cycle". The 24-cell strip marks favourable starts, recurring crop loss, not-rankable starts and stalled cycles. The table lists per-start dates, measures and recurring risks.
- **No-window explanations (2026-10-05):** when the scan has no favourable start, the Production window card and the scan panel name the cause instead of printing Unavailable. There are three causes. The site may be too cool to finish a cycle: a stage misses its heat requirement within the 300-day stage horizon in at least half the winters. Bud, flowering or fruit freeze may recur at every assessable start. Or too few cycles complete. Top risks then reads "Not assessed", or lists the recurring freeze families with their start counts, never "None recurring". Scan-primary windows also quote the `chill_clock` reason. Verified live on 2026-10-05: a Cascade Range pin at 46.738, −121.456 (weather cell 46.5, −121.25) and Naantali, Finland show "No complete crop cycle". Lynden, WA keeps May–Jun flowering and Jul–Sep harvest and now states "Only 11/15 winters produce a chill-triggered calendar". Arcadia gains its reason text and Waldo is unchanged. A modified copy of the payload covered the freeze branch. No page errors and no overflow at 390 px.
- **Scan accounting (2026-10-12):**
  - Payloads from `managed-cycle-scan-v4` carry per-start `outcomes` (complete, stalled slow, stalled at the horizon, weather incomplete) and a `cycle_failure` family.
  - The strip and table name blocked starts "Cycles do not complete", which takes precedence, or "Recurring freeze exposure". The table adds a "Cycles not completed" column and shows the slow, horizon and incomplete-weather counts under "Complete / stalled cycles".
  - The Production window text and Top risks say when cycles stall rather than calling a stall a freeze. Older payloads without `outcomes` keep the old "Recurring crop loss" wording.
  - Top risks adds a chill-shortfall line when the winter calendar does not apply and at least one winter falls short of the requirement.
  - The bud lane starts at budbreak, matching the bud-freeze window; forcing after chill is a thin, unmeasured bar.
  - Verified 2026-10-12 against the regenerated presets: Burgaw, Waldo, Arcadia, Mengzi (both new states), Penguin and Barben, plus live Naantali and the Cascade Range pin. The live pins read "No favourable start", with "Cycle failure" at 24 of 24 starts. There were no page errors, no CSP violations and no overflow at 1440 or 390 px; the map loaded under the CSP.
- **Literature benchmark:** Methods & data links to `benchmark.html`, the 53-site comparison of modelled and published system, bloom and harvest months. It is regional literature, not field validation of these grid cells.
- **Regional evidence (2026-10-05):** a separate tab lists source-checked IBO report records for the pin's country and region, apart from the calculated risks. See Regional evidence above.
- **Growing-cycle ruler (2026-09-15):** `dist/cycle.js` renders six aligned time lanes using the existing production result, with no UI library or new weather calculations. Select a stage button or lane for exposure details; native buttons also support keyboard activation. Choose a winter to see its modelled dates and exposures instead of aggregate frequencies. Small screens scroll the scale horizontally while controls and details reflow. The system hypothesis remains visible; the original tables are under an expandable details section.
- Solid bars show analysis windows. In the typical view, outlined spans run from p10 start to p90 end across valid winters, not confidence limits or one observed season. Risks use individual-winter stages, not that envelope. Evergreen-majority or unknown primary calendars cannot support crop-stage/chill-shortfall headlines; hypothetical calculations remain labelled. Warm-midwinter context is independent.
- HTML export saves the selected cycle and stage without inert stage buttons, expands the evidence tables, and preserves the live cycle/monthly/annual select labels. JSON retains the original production data plus `cycle_view` selection metadata. Actual downloaded HTML and JSON were checked in Chromium, including exact production-data parity; other browsers remain unverified.
- **Hourly source identity:** existing indexed cells retain their stored-series identity and sharing-site name. Other supported cells report Global hourly archive, source coordinates, displacement, UTC period, row count and a checksum identity over source objects and cell/window. All pins in one native 0.5° × 0.625° cell share weather values, not parcel observations. Evergreen-majority calendars remain inapplicable under the existing model.
- **Establishment window (2026-09-22):** a separate source-labelled regional panel, not a bearing-cycle lane. Florida: mid-December–mid-February; Georgia: winter, displayed approximately December–February; Santa Catarina: winter while dormant, displayed approximately June–August. The latter two are season conventions, not precise source-specified dates. Unknown-region pins decline rather than infer geography from a weather cell. Sources and conditions are in the panel and [method notes](weather/production/README.md).
- **Daily-only fallback:** complete daily Tmax >21 °C counts for 15 Nov–15 Feb north / 15 May–15 Aug south, labelled **days**, never estimated hours. Chill-triggered stages stay unavailable. The API reads 2010 padding for the first northern winter.
- Results older than `location-evidence-v5` / `open-field-production-v3` are refused with a refresh explanation. Update the API and the UI together.
- API errors are separated. The preview proxy marks its own tunnel-down reply with `code: 'archive_unavailable'` and the UI shows the archive as unavailable. Other 503 or 429 replies show the server's busy message. Non-JSON bodies are treated as an unavailable archive, not parsed.
- **Verification (2026-09-22):** 18 presets rendered; 135 selected winter/stage views and 855 displayed values matched the payload; empty/evergreen states, keyboard activation and management-state retention passed. Actual HTML/JSON downloads retained planting, winter 2014, fruit stage, tunnel/pots and chosen chart labels. Desktop/mobile inspected; 320/390/768/1440 px had no page overflow. Live shared-cell and daily-only coordinates both passed after restarting only `blueberry-ui-api`. Backend suite: 96 passing; 39 production/API tests passed again after fixing missing analysis-version metadata.
- **Verification (2026-09-28):** the UI agent checked Waldo, Arcadia, PF Berry and Georgia against the v3 payload, winter and stage retention across views, export names `blueberry-<site>-<analysis id>`, intercepted 503/502/HTML error bodies, cancel and a v4 refusal. `node --check` passed for `dist/app.js`, `dist/cycle.js` and `scripts/preview-ui.mjs`. After the final snapshot regeneration, Chao and Arcadia presets and a live Clinton, NC coordinate (7.8 s, `blueberry-ui-api` restarted only) rendered without page errors. All five views had no page overflow at 390 px, and the benchmark page fitted 390 px.

## Operating modes

**Server UI (since 2026-10-13):** `http://fpt-server.ad.ufl.edu:8789/` from the UF network or VPN, described under "Server UI on the UF network" below. This is the connected app for users. There is no login.

**Hosted snapshot UI:** ended on 2026-10-14, when the saved locations and their `dist/snapshots/` files were removed at the user's request; the app now needs the archive API. The owner-private Sites deployment still shows its old content and was not changed.

**Connected local UI:** the same frontend sends requests through the local Node proxy and an authenticated SSH forward to the loopback-only Python API. Use it to test changes before updating the server. Like the server UI, it is a single-analysis-at-a-time prototype, not an authenticated multi-user service or a durable job queue.

## Start connected mode

Use the access arrangements in `weather/SERVER_RUNBOOK.md`; no password or API secret belongs in commands committed here.

Since 2026-10-12 the API runs as a systemd user service, not a tmux session. Systemd restarts it after a crash, with a 10-second delay; in a test, a killed process was running again 16 seconds later. A watchdog timer checks it every 5 minutes. The watchdog restarts the service when health fails twice in a row, or when one analysis holds the busy lock for more than 15 minutes. It never starts a stopped service. On the server:

```sh
systemctl --user start blueberry-ui-api      # start
systemctl --user status blueberry-ui-api     # state, PID, last restarts
curl -s http://127.0.0.1:8787/api/health     # ready or busy
systemctl --user stop blueberry-ui-api       # stop (the watchdog leaves it stopped)
```

Unit files are in `ops/api/` (installed to `~/.config/systemd/user/`). The preflight and watchdog scripts are in `ops/bin/` (deployed to the project's `ops/bin/`).

- **Output.** The service writes to `logs/location_api.log`; the watchdog rotates it at 20 MiB and keeps 5 copies. Watchdog decisions go to `logs/ops/api_watchdog.jsonl`.
- **Disk.** Temporary files go to `tmp/api` on the project drive, so a full root disk no longer blocks the API.
- **Retired.** Do not start the old `blueberry-ui-api` tmux session as well.

### Server UI on the UF network (2026-10-13)

At the user's request the app runs on the lab server: `http://fpt-server.ad.ufl.edu:8789/`, or `http://10.248.22.167:8789/`, from the UF network or VPN. The systemd user service `blueberry-ui-web` runs `scripts/preview-ui.mjs` from the project's `ui/` folder. It serves `ui/dist/` and forwards `/api/` to the API on loopback port 8787, which the network cannot reach. Port 8788 belongs to another lab app.

- **Settings.** `ops/api/blueberry-ui-web.service` sets `PREVIEW_PORT=8789`, `PREVIEW_BIND=0.0.0.0` and `PREVIEW_HOSTS=fpt-server.ad.ufl.edu,10.248.22.167`. Host and Origin must name 127.0.0.1, localhost or one of those names, with port 8789. Other names, including the server's second address 10.248.68.79, get 403.
- **Node.** The system Node is version 12, too old for the proxy. Node 24.21.0, the newest LTS release on 2026-10-13, is in `tools/node`, a link to `tools/node-v24.21.0-linux-x64`, checked against the release's `SHASUMS256.txt`.
- **Boot.** `blueberry-ui-web` and `blueberry-ui-api` are both enabled, and user lingering starts them without a login.
- **Log.** `logs/ui_web.log` has start lines only; requests are not logged.
- **Access.** There is no login: anyone who reaches the address can search places and run analyses, one at a time. Plain HTTP is not encrypted, and browsers withhold WebCrypto on such pages, so `Shared.sha256Hex` computes the geography digest in script.

Install or change the unit, from the project root on the server:

```sh
cp ops/api/blueberry-ui-web.service ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now blueberry-ui-web
systemctl --user status blueberry-ui-web
```

Update the files from the local checkout root after the checks in "Reproduce summaries and tests". The service reads each file on every request, so a `dist/` change needs no restart; restart `blueberry-ui-web` after changing `scripts/preview-ui.mjs`. A file removed from `dist/` must also be deleted from `ui/dist/`.

```sh
{ git ls-files -z dist; printf 'scripts/preview-ui.mjs\0'; } \
  | rsync -a --from0 --files-from=- ./ fpt@10.248.22.167:/media/fpt/fpt2/Weather_Claude/ui/
```

Checked on 2026-10-13 from a Mac on the VPN: the page by name and address, health, a Jaíba place search, and an `app.js` identical to the local file. A foreign Host or Origin and a cross-site API call got 403, a POST 405 and path traversal 404, and port 8787 was unreachable. The Mac then lost the VPN, so a browser test mapped the server's name to a local copy of the same files. It loaded the page as a plain-HTTP origin without WebCrypto, and place names and regional evidence resolved. On 2026-10-14, with the VPN back, a browser at the address found Jaíba through the server's place search and completed its live analysis, with no page errors or CSP violations.

### Branch test copy (port 8790)

A branch can run beside the live app before it is merged. `ops/api/blueberry-test-api.service` runs the API from `test/code/` on loopback port 8791 with its own cache and access log (`LOCATION_API_PORT`, `LOCATION_API_CACHE`, `LOCATION_API_ACCESS_LOG`). `ops/api/blueberry-test-web.service` serves `test/ui/` at http://fpt-server.ad.ufl.edu:8790/ and forwards `/api/` to 8791 (`PREVIEW_UPSTREAM_PORT`). Neither starts at boot. Port 8788 belongs to another lab app; do not use it.

```sh
R=/media/fpt/fpt2/Weather_Claude
ssh fpt@10.248.22.167 "mkdir -p $R/test/code $R/test/ui $R/test/cache $R/test/logs $R/test/tmp"
rsync -a --exclude __pycache__ pipelines/weather/ fpt@10.248.22.167:$R/test/code/
{ git ls-files -z dist; printf 'scripts/preview-ui.mjs\0'; } | rsync -a --from0 --files-from=- ./ fpt@10.248.22.167:$R/test/ui/
rsync -a ops/api/blueberry-test-api.service ops/api/blueberry-test-web.service fpt@10.248.22.167:.config/systemd/user/
ssh fpt@10.248.22.167 'systemctl --user daemon-reload && systemctl --user start blueberry-test-api blueberry-test-web'
```

To keep a branch's batch run from overwriting the live `reports/ui_snapshots.json`, pass an output path: `python location_api.py --snapshots <path>`. After the merge or when the branch is dropped, stop both units with `systemctl --user stop blueberry-test-web blueberry-test-api`.

`dist/enso.json` holds NOAA's Oceanic Niño Index from 2010 for the Year-round planner. Rebuild it with `python3 scripts/build_enso.py`. A warm or cool run at the end of the series stays unlabelled until it lasts five seasons; the 2026 run, at +2.16 for July to September, is unlabelled for that reason.

### Local copy for development

From the local checkout root, run these two processes in separate terminals:

```sh
while true; do
  ssh -N -o ExitOnForwardFailure=yes -o ServerAliveInterval=15 -o ServerAliveCountMax=4 -o ConnectTimeout=10 \
    -L 127.0.0.1:8787:127.0.0.1:8787 fpt@10.248.22.167
  rc=$?
  echo "$(date '+%F %T') tunnel exited with code $rc; reconnecting in 5 s"; sleep 5
done
```

SSH exits with code 255 ("server not responding") after about a minute without keepalive replies, as when the network or VPN drops; on 2026-10-13 a plain tunnel died this way after 44 minutes. The loop reconnects 5 seconds after any exit; in a test, killing the SSH process gave the page a 503 "archive unavailable" and the API was back 6 seconds later. The loop saves the exit code before calling `date`; the version committed on 2026-10-13 logged code 0 every time, because `$(date …)` resets `$?`. To stop the loop, press Ctrl-C until the prompt returns, or close its terminal.

```sh
node scripts/preview-ui.mjs
```

Open `http://127.0.0.1:5173/`. The connection strip shows whether the private API is available, and adds "busy" while it runs an analysis. Stop the two local processes with Ctrl-C after use. The preview binds 127.0.0.1 unless `PREVIEW_BIND` is set, and only the server deployment sets it. `PREVIEW_PORT` selects another port.

Request safety (2026-10-12). This is a development boundary, not production authentication.

- **Preview proxy** (`scripts/preview-ui.mjs`):
  - accepts GET only, and checks Host, Origin and, on `/api/`, `Sec-Fetch-Site`. Host must be 127.0.0.1, localhost or a name in `PREVIEW_HOSTS`, with the listening port; an Origin, when sent, must be `http://` with one of those;
  - forwards only to its fixed loopback destination, with `Host: 127.0.0.1:8787`, and no Origin, cookies or other client headers;
  - after 95 seconds it answers 504 `archive_timeout`, and the page explains that the server may still be finishing. A connection failure gives 503 `archive_unavailable`;
  - every response carries `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` and a Content Security Policy. The policy allows scripts and styles from the page only, the MapLibre blob worker, and OpenFreeMap tiles, fonts and sprites;
  - inline styles are allowed only for `benchmark.html`.
- **API** (`location_api.py`):
  - answers 403 `forbidden_host` unless the Host is `127.0.0.1:8787` or `localhost:8787`;
  - answers 403 `forbidden_origin` for a cross-site `Sec-Fetch-Site` or an Origin other than the preview or the API itself.
- **Place search.** `/api/places?q=…&limit=…` (limit 1 to 25, default 15) reads `data/reference/geonames/places.sqlite` read-only and never waits for a running analysis. A missing or repeated `q`, a name over 100 characters or a bad limit gives 400 with the reason; a missing index gives 503 `place_index_unavailable`. The access log records the path only, never the typed text. Answers carry GeoNames attribution (CC BY 4.0) and the data date.
- **Health.** `/api/health` reports `status` (`ready` or `busy`), `method`, `busy_since`, `busy_seconds` and cache counters.
- **Result cache.**
  - Successful analyses are cached: 64 in memory, and up to 2,000 JSON files in `cache/location_api/`.
  - The cache key covers the API method, the primary profile, a hash of the code files that shape a result, and the coordinates. A code deployment therefore never serves an old result.
  - Data are not in the key. After any archive, land-mask, soil or `config/` change, delete `cache/location_api/*.json` and restart the service.
  - `--snapshots` never uses the cache.
- **Access log.** Every request adds one line without coordinates to `logs/location_api_access.jsonl`: path, status, duration, cache hit or miss, and busy refusal. The log rotates at 10 MiB and keeps 5 copies.

Place index (2026-10-13). `pipelines/weather/place_index.py` builds one SQLite file from a GeoNames dump: all populated places except abandoned, destroyed and historical ones (5,170,300 of 5,231,990), with a full-text index of names, alternate names, county, region and country. Rows are numbered by prominence, population raised to a floor for administrative seats without one, so each query reads at most 400 candidates; real queries take 0.1 to 7 ms. Results rank by match quality minus prominence: an exact name wins unless a prefix match is about 100 times larger, so `new york` gives New York City first while `alma` gives Alma, Quebec before Almaty. Entries that the list could not tell apart are merged. The dump of 2026-10-13 (data to 2026-10-12) and its `SHA256SUMS` are in `data/reference/geonames/20261013/`; the 1.03 GB index took 200 s to build. To refresh:

```sh
D=data/reference/geonames/$(date -u +%Y%m%d); mkdir -p $D
for f in allCountries.zip admin1CodesASCII.txt admin2Codes.txt countryInfo.txt readme.txt; do curl -sSf -o $D/$f https://download.geonames.org/export/dump/$f; done
(cd $D && sha256sum * > SHA256SUMS)
TMPDIR=tmp env/bin/python code/place_index.py build $D data/reference/geonames/places.sqlite   # replaces the file atomically
```

No restart is needed: each request opens the file afresh.

The API has been enabled at boot since 2026-10-13, because the UF-network UI depends on it. User lingering, already on for the account, starts it without a login; `systemctl --user disable blueberry-ui-api` reverses this.

## Reproduce summaries and tests

Develop code under `pipelines/weather/` and copy reviewed changes explicitly into the server's `code/`, as in the server runbook. After a code change, restart only this API (`systemctl --user restart blueberry-ui-api`); do not disturb acquisition or unrelated server jobs.

On the server:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
../env/bin/python evaluation_sites.py index      # rebuild config/hourly_index.json after any hourly change
../env/bin/python evaluation_sites.py fetch      # bounded: only cells without a stored series; needs explicit authorization
../env/bin/python location_api.py --snapshots
../env/bin/python benchmark.py                   # reports/benchmark/benchmark.{html,json}; copy the HTML to dist/benchmark.html
../env/bin/python -m unittest discover -p "test_*.py"
```

The generator writes `reports/ui_snapshots.json` on the server for the three references, the panel and the 53 benchmark sites in `benchmark_sites.json`. The app no longer ships these results; use the file to compare model versions before and after a change. Never copy the raw archive into `dist/`. JavaScript checks:

```sh
node --check dist/shared.js
node --check dist/app.js
node --check dist/cycle.js
node --check dist/map.js
node --check dist/places.js
node --check dist/season-views.js
node --check dist/evidence.js
node --check scripts/preview-ui.mjs
node --test tests/ui/        # proxy safety, shared helpers, season views and the evidence validator against the shipped library
python3 -m unittest tests/ops/test_api_watchdog.py
```

`dist/shared.js` holds the helpers that `app.js`, `cycle.js`, `places.js` and `evidence.js` share: HTML escaping, the https-only link check `safeURL`, the text cleaner used by the evidence validator, the managed-cycle state rules, and `sha256Hex`, which uses WebCrypto where the browser offers it and a script SHA-256 on plain-HTTP pages. Every value placed into the page as HTML goes through `escapeHTML` or a number formatter. Every external link goes through `safeURL`, so a link is either https without credentials or plain text.

## Scientific and engineering boundaries

- Complete windows are required. Flagged rainfall is not converted to zero; unavailable years/months stay null. Headline cards aggregate valid annual values and show the count. Monthly climatology requires all 15 complete monthly windows.
- Chill is hourly 0–7.2°C inclusive in a fixed reference winter. Dry spells are rain <1 mm within calendar-year boundaries; they are not measured crop drought or irrigation demand.
- Changing the growing system changes assumptions and soil interpretation, not ambient weather numbers. No calibrated tunnel transformations, severity score, soil suitability verdict or cultivar ranking exists.
- Soil estimates remain geographic WCS samples with native-grid/field validation pending. Soil acquisition remains source-blocked at 157/630 records; this UI does not retry it.
- Land support is cartographic, not parcel suitability. The source-labelled artificial “Null island” feature is excluded by `land-mask-v2`; small coasts/islands can remain unresolved.
- Missing hourly availability, incomplete winters and per-metric gaps are distinct in the calculations; a broader geographic adapter is still pending. Establishment guidance does not validate field suitability; the stage calendar remains assumption-based. The earlier standalone stage-scenario report is historical.
- Since 2026-10-12 the API runs under systemd with crash restart and a watchdog, and it caches successful results on disk. Production work still requires authenticated archive connectivity, a queue for more than one analysis at a time, fuller per-section states, broader cross-browser report compatibility testing and a security review. The server has only private UF addresses. Since 2026-10-13 the UI listens on its port 8789 for the UF network and VPN, without a login; the API stays on loopback.

The current design and interaction contract is in `UI_IMPLEMENTATION_PLAN.md`. The runtime remains the static frontend and standard-library Python HTTP adapter over the existing science code; durable jobs and authenticated hosted access are future work.
