# Coordinate-based climate and soil dashboard

Date: 2026-09-11. **Design specification only: no UI, API or deployment created in this task.** This is the interim Parts 1–2 product; cultivar ranking and production-system classification remain deferred. It narrows the original four-output final-product architecture to the evidence we can actually serve now.

Implementation follow-up on the same date: the first static UI and loopback-only Python API are now implemented. See `UI_RUNBOOK.md` for the actual capability boundary and startup instructions. The queue, framework choices and production endpoints below remain target architecture, not completed functionality.

## Product decision

Build a web-first location assessment. The page itself is the readable report, with interactive evidence and an export of the same result. Primary inputs remain latitude/longitude (or map pin) and one of four management choices. Default: open ground. Preset Citra, Waldo and Papanduva buttons provide repeatable demonstrations. No market-date input, cultivar selector or chat assistant in this release.

"Live" means on-demand computation and progressive display from the historical archive, not live sensors, current weather or a forecast. Prominently show **Historical baseline 2011–2025**, 2010 boundary padding, analysis timestamp and data/method versions. Do not imply a fresh calculation contains 2026 weather.

## One-page information hierarchy

1. **Location bar:** labelled latitude/longitude inputs, map-pin alternative, four-choice growing-system selector, Analyze button. Coordinates work even if the basemap provider fails. Keep map attribution visible; avoid mandatory geocoding or a paid API key for the coordinate-first slice.
2. **Context/status strip:** requested pin; weather source-cell displacement/resolution; baseline; daily/hourly/soil availability; overall job stage. Show the entered pin separately from weather/soil cells. Never silently substitute nearest pilot soil or hourly data.
3. **Six exposure cards:** chill, freeze, rainfall, heat, dry-weather/water demand and radiation. Each card shows one precisely labelled headline quantity, unit, window, valid/expected seasons and an evidence label. Expand for annual values, thresholds, methods and gaps. Do not apply a common 0–100 scale across unlike hazards.
4. **Evidence area:** monthly climate and year-to-year variation; selected-factor details; optional reference-stage overlays. Default to outdoor calendar-based exposure. Existing 50/100-hour calendars are a separately labelled exploratory mode with exact dates and unmet-chill years visible. Never display actual flowering predictions from these assumptions.
5. **Soil context:** property/depth table with mean and Q0.05/Q0.95; source, returned grid and caveats. Pots switch to a substrate/irrigation requirements panel while native soil remains available as site context. Partial properties/depths remain partial, not one misleading "soil ready" badge.
6. **Growing-system comparison:** four systems, what may improve, what can worsen and what must be supplied/measured. Ambient measurements do not change just because a dropdown changes. Quantitative adjusted metrics appear only for versioned, supported transformations; initial tunnel effects are qualitative.
7. **Summary and export:** short deterministic summary, main constraints and next field checks; save a self-contained HTML report and analysis JSON. Print styling allows browser PDF initially. Later server-generated PDF must use the same immutable result snapshot. No model-generated numbers or extra LLM API required.

Desktop: compact location/map region followed by a 3 × 2 card grid and full-width evidence panels. Mobile: stacked inputs/cards with keyboard-operable detail controls, readable units, accessible chart descriptions and table alternatives. Warnings use text/icons as well as color. Avoid six simultaneous dense charts or gauges with invented severity cutoffs.

## Capability-aware card contents

| Card | First metric | Support boundary |
|---|---|---|
| Chill | Seasonal hours under a named threshold/window, distribution across winters | Hourly input only at existing supported pilots initially. Other pins show "hourly data needed", not daily-derived exact chill. Dynamic Model not implemented. |
| Freeze | Days with Tmin below explicit threshold and worst daily minimum | Grid exposure, not crop damage; stage-window metrics labelled exploratory; cold events can be missed. |
| Rainfall | Annual/seasonal total, wet/heavy-rain days; optional reference harvest rain | Suspect/missing dates make affected metrics unavailable; rain does not establish drainage or splitting probability. |
| Heat | Days with Tmax above named threshold, annual maximum; later hot-spell duration | Label threshold as screening; no berry-temperature or yield-loss claim. |
| Dry weather | Longest consecutive <1 mm/day spell in the stated window | Do not label this actual plant drought. ET0 and water balance remain unavailable until implemented and tested. |
| Radiation | Mean/stage shortwave MJ/m²/day and monthly variation | No unvalidated optimal-light score; DLI is a separate assumption-based derivation, not the source measurement. |

Do not prioritize unlike metrics through arbitrary weights. Until approved severity rules exist, show a stable order, factual summary and explicit data-quality warnings. Historical event counts/frequencies include numerator/denominator; a zero does not mean zero future risk. Change season controls only inside advanced evidence views, with defaults displayed and versioned.

## User flow and partial results

1. Validate finite coordinate ranges; normalize longitude consistently; run land/coast support checks. Invalid or unsupported points return a clear explanation, not a successful-looking result.
2. Resolve a versioned cached analysis or submit a durable job. Return an analysis ID immediately; do not block one HTTP request waiting for upstream services.
3. Read local daily arrays and publish usable outdoor metrics first. Independently resolve hourly pilot support and cached soil. Pending/failed enhancements never erase the daily-weather result.
4. Progress labels reflect real stages: validating location → reading weather → calculating indicators → checking soil/hourly support → preparing report. Show determinate percentages only for counted work, no fake countdown.
5. Keep partial results usable. Downloads requiring new sites run only through a bounded, budgeted server queue enabled for the deployment; do not trigger hundreds of requests from map dragging. Analyze is explicit; debounce map interaction and deduplicate jobs.
6. Show `blocked_source`, `not_acquired`, `unsupported_location` or `insufficient_data` where applicable. Browser refresh retrieves the same job; user retry cannot reset terminal acquisition attempts. Current soil source failure remains recorded, not hidden.
7. Bind every response to its analysis ID/request hash. A late response for pin A cannot overwrite pin B. Freeze one immutable snapshot for export; a later enhancement creates a new revision, not a silently changed report.

Two separate status axes: computational availability (`ready`, `pending`, `not_acquired`, `blocked_source`, `invalid_data`, `unsupported`) and scientific interpretation (`descriptive`, `exploratory`, later `validated_for_defined_use`). Acquisition success or 51 software tests must never produce a "scientifically validated" badge.

## Engineering architecture

- **Frontend:** TypeScript/React, following the original Next.js direction; MapLibre optional for pin selection. Coordinate entry is the first required interaction. Basemap tiles/attribution/usage conditions must be selected before integration; MapLibre itself is not a hosted tile entitlement. [MapLibre documentation](https://maplibre.org/maplibre-gl-js/docs/)
- **API:** Python FastAPI, validated inputs and structured results. Keep scientific calculations on the server, not duplicated in JavaScript.
- **Science:** wrap/refactor the existing tested Python extraction, indicators, stage scenarios and soil records into library functions with injected data roots/configuration. This deliberately supersedes the original R-first implementation detail for this interim slice: the working code is Python and Paul's full R pipeline remains unreconciled. Do not rewrite proven calculations merely to match the old plan.
- **Data:** read the existing server Zarr/Parquet/soil JSON; cache small analysis artifacts, not copies of global arrays. Soil native-grid parity remains a caveat. Check soil sampling identity separately from shared weather cells.
- **Jobs:** separate durable worker, bounded concurrency, leases, persisted attempts and idempotency. PostgreSQL-backed queue for the multi-user release; a private single-worker prototype may use a separate SQLite job store if concurrency/restart tests pass. Do not reuse or mutate the acquisition database schema for web jobs.
- **Progress:** status polling with backoff is enough initially; no WebSocket infrastructure needed. FastAPI's in-process background tasks are not the durability boundary for this work; its documentation distinguishes heavier processing needs. [FastAPI background-task guidance](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- **Narrative:** deterministic templates from validated result fields. The UI and export read one result artifact; they must not calculate separate numbers or silently use different windows.

Proposed interfaces: `POST /analyses`, `GET /analyses/{id}`, `GET /analyses/{id}/report`, `GET /capabilities`. A cold request returns 202 and a job ID; an existing ready result can return immediately. Responses include per-section progress and reasons. Result schema: request pin/system, baseline, source grids, metrics with units/windows/valid counts, soil depth/statistics, scenario assumptions, warnings, provenance, artifact version and report reference.

Cache raw weather by source grid/profile; cache full results by requested geometry, soil sampling identity, management, baseline/window/threshold config, QC/science/source versions and access scope. Never let two pins sharing weather receive each other's soil or private request identity. Preserve permissions for exports and job lookups; unguessable IDs are not authorization.

## Delivery stages and tests

**A. First connected slice:** coordinate form → existing server extraction → six card slots → seasonal charts → on-page summary and HTML export. Use three pilot fixtures and one non-pilot land coordinate. Unsupported chill/soil are explicit. Freeze/rain/heat/dry-spell/radiation cards must use actual implemented metrics; slots alone are not completion.

**B. General coordinate support:** persistent jobs/cache, partial results, soil adapter isolation, validated on-demand hourly path under acquisition limits, error states and restart recovery. Reuse approved source jobs; do not restart completed global downloads or reset the failed soil job from the browser.

**C. Management comparison:** first qualitative mechanism-based comparisons; numerical scenarios only after implementing their documented assumptions/tests. Supervisor review of labels, stage definitions and system profiles. No cultivar shortlist or evergreen/deciduous verdict yet.

**D. Private supervisor pilot:** authenticated access, report parity, mobile/keyboard checks, performance measurement, logs with redacted coordinates and a restart/security review. Cached-response target around two seconds is an objective to benchmark, not an existing measured capability. Measure cold weather-only latency separately from source acquisition.

Required tests: invalid/offshore coordinate; new pin with daily-only support; missing/flagged rain; partially populated soil; stale/racing response; duplicate submit; API/worker restart; blocked provider; exact parity with existing pilot calculations; same analysis ID/version in page/export; no ambient risk reduction on management toggle; no arbitrary soil transfer between nearby pins; protected lookup/export; responsive and keyboard paths.

## Deployment boundary

The data host is on a private 10.x network. A public static site cannot simply read its disk or call it from every visitor's browser. Initial development can use a loopback-bound API and an authorized SSH connection/private-network setup. Public access requires an approved authenticated gateway or deployment/data-serving arrangement. No public ports, new cloud services, paid accounts or live deployments are authorized by this planning task. Follow the available site-building/hosting workflow at implementation time and reconcile its backend reachability before publishing anything.

No supervisor dataset or new API key is necessary to implement the coordinate-first private slice. Supervisor confirmation of scientific thresholds/structure assumptions remains necessary before validated recommendations. Prioritize the connected slice over further global downloads or decorative mock dashboards.
