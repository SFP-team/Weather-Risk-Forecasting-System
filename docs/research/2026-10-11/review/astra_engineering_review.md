# Astra engineering review (2026-10-11)

Reviewer: read-only code-review agent, 2026-10-11. The coordinator saved this report from the agent's structured output.

## Verdict
I found no critical defects and no science bug that changes results. Missing data stays missing in Python and JS: clean_rain treats a missing suspect flag as suspect, complete() and Days.get refuse gaps, and risks() never counts None as a safe year. The browser guards against stale responses with request serials and place-lookup context checks. The checksum reader verifies the same bytes it returns. The real defects are in how the service runs, how it is exposed and how much is tested: 1 high, 6 medium, 13 low. Each finding below gives severity, file:line, evidence, impact and fix.

Attribution: every commit uses the same git identity. Matching the commits in the brief shows that the BUSY lock, respond(), the Handler class and most of preview-ui.mjs come from b9cb0ff (2026-09-11) and b91cd61/f9ce9c5 (Opus era), not from Astra. Astra's lines are in hourly_archive.py (f33025f), planting.py, the stage_risks_v2 profile and the risks() gating (7f293c6), and most of the UI (df73699, 169ab13, bd7e858, 5779365). I reviewed every file in scope whoever wrote it.

## Findings by severity
- High: H1, service supervision depends on tmux and has no restart path (UI_RUNBOOK.md:82).
- Medium:
  - M1: one BUSY lock with no timeout, no way to cancel and no result cache (location_api.py:161-176).
  - M2: the Python API has no Host or Origin check (location_api.py:179-195).
  - M3: the proxy lets cross-site GETs start an analysis (preview-ui.mjs:8-11).
  - M4: sensitivity() recomputes the primary v3 profile (location_api.py:107-110).
  - M5: the evidence registry is not ready for RAG (evidence.js:118-120, app.js:815-819).
  - M6: test coverage gaps.
- Low:
  - L1: no URL scheme check in sourceLinks.
  - L2: no CSP or nosniff header.
  - L3: numeric API fields are inserted into innerHTML without escaping.
  - L4: no access log and no log rotation.
  - L5: UTC days and local solar days are mixed.
  - L6: leap-year ±1 day shifts.
  - L7: thresholds are hard-coded outside the profiles.
  - L8: hourly_for reads the file twice, and hourly_sha256 means different things on its two paths.
  - L9: the connection label is wrong while the API is busy.
  - L10: the proxy's dist root depends on the working directory.
  - L11: the bud lane window does not match the bud metric window.
  - L12: duplicated helpers and globals shared implicitly across files.
  - L13: dense code and one-letter names.
  - L14: a proxy timeout is reported as "archive unavailable".

## Verified
- `node --check` passes for app.js, places.js, map.js, cycle.js, evidence.js and preview-ui.mjs.
- Path handling: I ran the proxy's path logic offline (no server started). /../package.json, %2e%2e and ..%2f are refused. A malformed % escape throws and gives 404. //etc/passwd resolves inside dist. dist has no symlinks, and every file extension in dist has a MIME entry.
- All 71 snapshots are location-evidence-v5 / open-field-production-v3, and every index key matches its site.name.
- The 140256 check in hourly_archive.py:46 is correct: 5844 days × 24 hours.
- The registry has 91 records, all marked source_checked. Records carry no reviewer, extractor or date field. The longest summary is 500 characters. All source URLs are https.
- The existing tests cover:
  - risk gating, in test_production.py:164-247;
  - local solar days at lon 0 and -82 only;
  - leap-year chill counting in test_evidence_report.py.

## Inferred, not verified
- Whether DNS rebinding works depends on the browser's local-network protections.
- I did not measure how long the duplicated v3 run takes.
- The disk-full and tmux incident is not written down anywhere in the repo. I assume the tmux socket sits in /tmp on the root filesystem; I did not check the server.
- Tracebacks probably contain no coordinates, but I did not prove it.

## Top 10 fixes
1. Run the API under systemd --user with Restart=on-failure. At minimum, set TMUX_TMPDIR to /media/fpt/fpt2 and add a `df -h /` preflight step.
2. Add a result cache keyed by (METHOD, lat, lon) and the input hashes: an in-memory LRU plus JSON files on the project drive.
3. Run each analysis in a subprocess with a time budget. Report busy_since in /api/health and kill the run on timeout.
4. Make the Python Handler accept only Host 127.0.0.1:8787 or localhost:8787, and reject cross-site Sec-Fetch-Site.
5. In the proxy, require Sec-Fetch-Site same-origin or none on /api/. Add nosniff, a CSP and frame-ancestors. Resolve dist from import.meta.url.
6. Reuse the primary analyse() result inside sensitivity().
7. Share safeURL with app.js sourceLinks. Escape or format every interpolated value. Add a CSP.
8. Before any RAG work, harden the evidence registry: add per-record reviewed_by, reviewed_on and extracted_by; enforce length limits and strip control and bidi characters in validate(); retrieval returns record IDs only, and the model never writes URLs.
9. Add tests:
   - preview-ui: path traversal, Host and Origin checks, upstream errors;
   - a real ThreadingHTTPServer test for concurrency and the Host check;
   - the indexed hourly_for branch;
   - eastern and dateline longitudes;
   - leap-year calendars;
   - a JS stale-response test with a fake fetch.
10. Log one line per request (status, duration, busy rejection; no coordinates) with rotation. Generate threshold text from the profiles, and move normalize, escape and haversine into shared modules.


## Detailed findings

### 1. Remove tmux-on-root-disk as the only API supervisor; add restart path

Location: `docs/UI_RUNBOOK.md:80-83`. Reviewer confidence: 0.70.

Severity HIGH (operations). Evidence: UI_RUNBOOK.md:82 starts the API only as `tmux new-session -d -s blueberry-ui-api '../env/bin/python -u location_api.py >> ../logs/location_api.log 2>&1'`. location_api.py:193-195 runs serve_forever() with no supervisor. SERVER_RUNBOOK.md has no fallback and no disk preflight. tmux keeps its socket under /tmp, which is on the root filesystem by default [inference]. The coordinator reports an incident in which the root disk filled and tmux could not start; that incident is not recorded in the repo. Impact: if the process exits, is killed, or tmux cannot create its socket, the API stays down until someone notices by hand. Nothing restarts it, and the UI just shows 'archive not connected'. Fix: run the API as a systemd --user unit with Restart=on-failure and lingering enabled, or with setsid/nohup and a pid file on /media/fpt/fpt2. Set TMUX_TMPDIR=/media/fpt/fpt2/Weather_Claude/run when tmux is used. Add `df -h / /media/fpt/fpt2` and a stale-socket check to the start procedure.

### 2. Bound the BUSY lock: add timeout, cancellation and a result cache

Location: `pipelines/weather/location_api.py:161-176`. Reviewer confidence: 0.85.

Severity MEDIUM. Evidence: location_api.py:169 calls BUSY.acquire(blocking=False) once for the whole process and returns 503 otherwise. Nothing is cached. The analysis has no time budget. The proxy does not pass client aborts upstream, and app.js:437-440 notes that the server keeps working after a cancel. Impact: one slow or hung analysis (a disk stall, a sqlite lock) blocks every user until a manual restart, and /api/health reports 'busy' forever. After a cancel, re-analysing the same point recomputes from scratch. Two lab users cannot work at the same time. Fix: cache results keyed by (METHOD, lat, lon) and the hourly/daily identity hashes, in an in-memory LRU plus JSON on the project drive. Run analyze() in a worker process with a deadline and kill it on timeout. Record busy_since and return it from /api/health.

### 3. Validate Host and Origin in the Python API handler

Location: `pipelines/weather/location_api.py:179-187`. Reviewer confidence: 0.75.

Severity MEDIUM (security). Evidence: Handler.do_GET (location_api.py:179-187) serves any Host and any Origin. UI_RUNBOOK.md forwards the laptop's 127.0.0.1:8787 to it over SSH (-L 127.0.0.1:8787:127.0.0.1:8787), so the browser can reach the API directly and bypass the proxy's Host and Origin checks. Impact: a malicious page can use DNS rebinding to read analysis JSON. A cross-site <img> or no-cors GET to http://127.0.0.1:8787/api/analysis can start analyses and hold BUSY, which denies service to the lab. Other local users on the shared server can do the same. How exploitable this is depends on the browser's local-network protections [inference]. Fix: return 403 unless the Host header is 127.0.0.1:8787 or localhost:8787. Reject requests whose Sec-Fetch-Site is cross-site or whose Origin is not one of the proxy origins.

### 4. Block cross-site GETs to /api/ in the preview proxy

Location: `scripts/preview-ui.mjs:8-11`. Reviewer confidence: 0.80.

Severity MEDIUM (security). Evidence: preview-ui.mjs:10 checks Origin only when the header is present. Browsers send no Origin on image loads, navigations or no-cors GETs. The Host check at line 8 passes because the request really targets 127.0.0.1:5173. Impact: any website the user visits can make the browser call http://127.0.0.1:5173/api/analysis?latitude=..&longitude=.. and start a server analysis, which holds the single BUSY lock (CSRF-style denial of service). It cannot read the response. Fix: for /api/ paths, require req.headers['sec-fetch-site'] to be 'same-origin' or 'none', or require a custom request header that app.js sets. Return 403 otherwise.

### 5. Reuse the primary profile result inside sensitivity()

Location: `pipelines/weather/location_api.py:107-110`. Reviewer confidence: 0.85.

Severity MEDIUM (performance under the lock). Evidence: location_api.py:108 runs analyse() for PRODUCTION_PROFILE (stage_thermal_v3). Line 110 then calls sensitivity() over list(PROFILES), which runs analyse() again for all six profiles, stage_thermal_v3 included (production.py:1191-1194). That repeats the hourly infection model, the bee-flight model and the 24-start x 15-year managed-cycle scan. Impact: the most expensive profile runs twice for every request while BUSY is held, so every user waits longer. The exact cost was not measured [inference]. Fix: pass the computed primary result into sensitivity(), or skip PRODUCTION_PROFILE there and fill its row from the existing result.

### 6. Harden evidence registry before adding a RAG or LLM layer

Location: `dist/evidence.js:115-124`. Reviewer confidence: 0.70.

Severity MEDIUM (future prompt-injection risk). Evidence: validate() in evidence.js:118-120 checks only that title, summary, crop_context and similar fields are non-empty strings. It sets no length limit and does not strip control, zero-width or bidi characters. Records have no reviewer, extractor (model) or per-record review date; the registry has one reviewed_on and every record says review_status source_checked. app.js:815-819 also registers a WebMCP tool (readOnlyHint:false) that lets an agent drive the page while the page shows third-party report text. Impact: once retrieved text is passed to an LLM, wording paraphrased or extracted from IBO PDFs (third-party content) can carry instructions or misleading claims, and nothing records who checked which record. Fix: add reviewed_by, reviewed_on and extracted_by per record. Enforce maximum lengths and a character allow-list in validate(). Keep retrieval citation-first: return record IDs, render the curated text, wrap any LLM context as quoted data, and never let model output create links (links come only from sources[].url through safeURL).

### 7. Add tests for proxy, HTTP handler, index path, longitudes and JS races

Location: `tests/weather/test_location_api.py:178-187`. Reviewer confidence: 0.85.

Severity MEDIUM (test gaps). Evidence: RespondTests (test_location_api.py:178-206) call respond() directly and never start ThreadingHTTPServer or Handler. Nothing tests scripts/preview-ui.mjs or any dist/*.js. test_hourly_archive.py:48-61 reaches hourly_for only through the no-index fallback, so the indexed branch (missing file, checksum mismatch) is untested. The local-solar-day tests (test_production.py:546-590) use only lon 0 and -82. No test covers a leap-year calendar median or a concurrent second request. Impact: regressions in path traversal handling, Host/Origin checks, the stale-response guard, the busy-retry logic, eastern-longitude day labelling and Feb 29 handling would go unnoticed. Fix: add a node:test suite for preview-ui (traversal, malformed %, Host/Origin, upstream error and timeout). Add a Python test that starts the server on an ephemeral port and fires two requests at once. Add hourly_for index tests, lon +150 and ±180 cases, and leap-winter calendar cases. Add a JS test for analyze() with a fake fetch that resolves out of order.

### 8. Validate URL scheme in sourceLinks before writing href

Location: `dist/app.js:251-253`. Reviewer confidence: 0.80.

Severity LOW (XSS hardening). Evidence: app.js:251-253 builds `<a href="${esc(s.url)}">` from API or snapshot sources and checks no scheme. cycle.js:123 and app.js:381 reuse it. evidence.js already has safeURL (https only, no credentials). Impact: a javascript: or data: URL in a tampered snapshot JSON or API payload would run when clicked. Today the sources are server constants, so the risk is low. Fix: export safeURL from one shared module, render a link only when it returns a value, and add rel=noopener.

### 9. Send CSP and nosniff headers from the preview server

Location: `scripts/preview-ui.mjs:16-16`. Reviewer confidence: 0.75.

Severity LOW. Evidence: preview-ui.mjs:16 sends only Content-Type and Cache-Control. index.html:4-10 has no CSP meta tag, even though it has no inline scripts and no on* handlers, so a CSP is practical. The app writes API data into innerHTML in many places (app.js, cycle.js). Impact: there is no second line of defence if an escaping mistake slips in. Fix: add X-Content-Type-Options: nosniff, Referrer-Policy: no-referrer and a CSP with script-src 'self', object-src 'none', base-uri 'none', frame-ancestors 'none', worker-src blob: for MapLibre, and connect-src 'self' plus the OpenFreeMap hosts. The inline style= in app.js:381 needs style-src 'unsafe-inline' or a CSS custom property instead.

### 10. Escape numeric API fields interpolated into innerHTML

Location: `dist/app.js:412-412`. Reviewer confidence: 0.70.

Severity LOW. Evidence: app.js:412 inserts r.provenance.rows, r.hourly_source.source_lat and source_lon without escaping. bars() at app.js:184 inserts labels[i] (API years). riskRows and the headline cards insert r.rank, r.years_with_event, r.valid_years and r.total_years. Impact: these fields are numbers today. If an API or snapshot field became a string, it would be parsed as HTML. Fix: pass every interpolated value through esc() or fmt(), or build these nodes with textContent the way evidence.js does.

### 11. Add a coordinate-free access log and log rotation

Location: `pipelines/weather/location_api.py:174-180`. Reviewer confidence: 0.80.

Severity LOW (operations). Evidence: location_api.py:180 replaces log_message with pass. Line 174 writes only tracebacks to stderr. UI_RUNBOOK.md:82 appends stderr to ../logs/location_api.log, and nothing rotates it. Impact: there is no record of request counts, latency, 503 busy rejections or 422/500 rates, so slow or blocked service cannot be diagnosed. The log grows without limit, which matters given the earlier disk-full incident (incident reported, not documented). Fix: write one JSON line per request with time, path, status, duration_ms and busy=true/false, with no query string. Use RotatingFileHandler or logrotate on the project drive.

### 12. Align day boundaries: UTC daily windows vs local-solar hourly metrics

Location: `pipelines/weather/production.py:344-348`. Reviewer confidence: 0.70.

Severity LOW (date and time correctness). Evidence: the daily inputs are NASA POWER UTC days (postprocess.py: 'UTC daily aggregation is not a local biological day'). Stage windows, chill_date (season().floor('D')) and warm-midwinter windows are UTC dates. infection_risk (production.py:346) and bee_flight_hours (production.py:378) label local solar days (UTC + round(lon/15) h), and Days reindexes them onto the same date labels. Impact: at |lon| near 150 to 180, flowering-window infection and bee-flight days sit 10 to 12 hours off the Tmin/Tmax days they are combined with. The cycle header still says 'UTC'. The effect is small but systematic in Australia, NZ, East Asia and the Pacific. Fix: shift the daily windows to local solar days for these metrics, or document per-metric day boundaries in METRIC_CATALOG and the UI. Add an eastern-longitude test.

### 13. Remove leap-year ±1 day bias in median dates and reference chill

Location: `pipelines/weather/production.py:755-762`. Reviewer confidence: 0.75.

Severity LOW (leap years). Evidence: calendar() (production.py:757) maps the median of per-winter offsets onto a non-leap anchor (2000-11-01 or 2001-04-01). Offsets for dates after 28 Feb in leap winters (2012, 2016, 2020, 2024) are one day larger, so medians that mix leap winters drift up to one day late. month_day() in the managed scan does the same. location_api.py:82 uses a 1 Nov to 1 Mar reference chill window, which is 2904 hours in leap winters and 2880 otherwise. Impact: displayed median dates can be one day late, and reference chill is not comparable year to year (up to 24 extra hours). Fix: compute medians on day-of-season numbers that exclude Feb 29, or anchor each offset with month/day arithmetic. Use a fixed-length reference window or exclude Feb 29.

### 14. Drive thresholds and definition text from profile constants

Location: `pipelines/weather/production.py:503-518`. Reviewer confidence: 0.85.

Severity LOW (maintainability and correctness drift). Evidence: fruit frost compares against a literal 0.0 (production.py:518) although the profiles define frost_threshold_c. The pollination proxy reads p.get('pollination_cold_tmax_c', 15.0) with hidden defaults for legacy profiles (line 504). warm_midwinter_daily hard-codes 21.0 (line 262). The risk and catalog text repeat the numbers by hand ('Tmax <15 C OR rain >=1 mm', 'hours >21 C', '<=0 C') at lines 179 and 874. Impact: changing a profile value would change one calculation but leave the other calculations and the displayed definitions wrong. Fix: read every threshold from p without defaults, and build the definition strings from p the way the flowering-freeze text already does.

### 15. Hash and parse the indexed hourly file from one read

Location: `pipelines/weather/location_api.py:64-70`. Reviewer confidence: 0.80.

Severity LOW (cache identity). Evidence: hourly_for (location_api.py:65-70) reads the whole parquet file to hash it, then pd.read_parquet(path) reads it from disk a second time. The indexed path also returns the parquet file SHA as 'sha256', while the cache path returns an identity hash over object hashes and cell indices (hourly_archive.py:52-53). The same API field therefore means different things. Impact: the parsed data could differ from the bytes that were checked (low likelihood with a single writer), and hourly_sha256 cannot be compared between the two paths. Fix: read the bytes once and parse with pd.read_parquet(io.BytesIO(data)). Label the identity scheme in the provenance (for example 'identity': 'parquet-file-sha256' or 'cached-hourly-point-v1').

### 16. Show busy API as connected in the health indicator

Location: `dist/app.js:810-814`. Reviewer confidence: 0.90.

Severity LOW. Evidence: app.js:811-813 sets 'Private archive connected' only when /api/health returns status 'ready'. When it returns 'busy' (location_api.py:164), the label stays 'Saved locations · archive not connected'. Impact: a user who opens the page while another analysis is running is told the archive is disconnected and may restart tunnels or services for no reason. Fix: treat 'busy' as connected ('Private archive connected · busy'), and recheck after an analyze attempt returns 503.

### 17. Resolve the static root from the script location, not cwd

Location: `scripts/preview-ui.mjs:5-5`. Reviewer confidence: 0.90.

Severity LOW. Evidence: preview-ui.mjs:5 sets `const root=path.resolve('dist')`, which depends on the working directory. Impact: started from any directory other than the repo root, the proxy serves 404s, or another directory's dist/. Fix: `const root=fileURLToPath(new URL('../dist/', import.meta.url)).replace(/\/$/,'')`, using fileURLToPath from node:url.

### 18. Match the bud lane window to the bud-stage metric window

Location: `dist/cycle.js:40-43`. Reviewer confidence: 0.75.

Severity LOW (UI correctness). Evidence: cycle.js:41 draws the 'buds' lane from the chill date to flowering_start - 1. The bud-freeze metrics shown in that stage's detail cover budbreak to flowering_start - 1 (production.py stage_metrics, `last = flowering[0] - 1`, get('tmin', bud, last)). detail() prints that lane span as the 'Median window'. Impact: the window shown above the bud-freeze numbers includes the forcing period before budbreak, which the metric does not cover, so users will overstate the exposure window. Fix: start the lane at offset('budbreak'), or draw the forcing period as a separate segment and label the metric window explicitly.

### 19. Deduplicate helpers and replace implicit cross-file globals

Location: `dist/app.js:9-9`. Reviewer confidence: 0.85.

Severity LOW (maintainability). Evidence:
- The text normaliser exists three times: app.js:562, places.js:21 and evidence.js:33. Region matching depends on the copies staying identical.
- HTML escaping exists twice: app.js:9 (esc) and cycle.js:15 (escape).
- The haversine formula exists three times: hourly_archive.py:49-50 inline, location_api.py haversine_km, and places.js.
- app.js:404 hard-codes 'location-evidence-v5' and 'open-field-production-v3', copying the Python METHOD constants.
- cycle.js calls app.js globals (sourceLinks, eligibilityLabel, stageClockLabel, stageTiming, systemLabel, chillCalendarApplies, scanGap, monthRuns, riskLabel, md, MONTHS). This works only because of the deferred load order.

Impact: a change to one copy silently breaks matching or escaping elsewhere, and a method bump needs coordinated edits in several files. Fix: one shared util script, or ES modules, for normalize, escape, safeURL and coordinate checks. Have the API return its method version and compare against that. Pass dependencies into CycleView.mount explicitly.

### 20. Split dense one-line functions and replace one-letter names

Location: `pipelines/weather/location_api.py:73-82`. Reviewer confidence: 0.80.

Severity LOW (maintainability). Evidence:
- app.js is 823 lines (78 KB), with 37 lines over 300 characters. bars() (L184) and renderSoil() (L192) are single-line functions. renderProduction builds about 10 KB of HTML in one template literal.
- production.py is 1,384 lines (95 KB). risks() is 135 lines with its definitions written inline.
- summarize() (location_api.py:73-82) uses p, ok, cs, ce, mp, mt, ms, a and b, and chains statements with semicolons. hourly_archive.py:49 uses sy, sx and a. app.js uses p, c, a, rk, s, m, v and r throughout.

Impact: these are hard to review and easy to break, and the parameter meaning of p, rk and so on is lost. Fix: give each statement its own line, use descriptive names (rain, chill_start, profile, risk_result), move the risk definitions into a module-level table, and split app.js into overview, production and search modules.

### 21. Distinguish proxy timeout from archive-unavailable

Location: `scripts/preview-ui.mjs:12-14`. Reviewer confidence: 0.70.

Severity LOW (error paths). Evidence: preview-ui.mjs:12-14 sets timeout:95000 and handles it with upstream.destroy(). That fires the 'error' handler, which replies 503 with code 'archive_unavailable'. If headers were already sent, it appends JSON to a partial body. Impact: an analysis that runs past 95 s, which the Python server keeps holding under BUSY, is reported as a dead tunnel. Clients other than app.js, which aborts at 90 s, get the wrong advice. Fix: on timeout, destroy with a tagged error and reply 504 with code 'archive_timeout'. When res.headersSent is true, only destroy the response.
