# Project progress log

## 2026-10-14: Formula sheet

- **Request.** The user asked for a brief HTML sheet of all the formulas the model uses, such as the budbreak calculation, and of all the folders.
- **Written.** `docs/weather/production/formula_sheet.html`: chill, the thermal clock, classification, calendar applicability, stage exposures, the infection and bee-flight models, risk ranking, the managed-cycle scan, the planting window and Climate history measures, each with file and line on `main`, then maps of the repository and server folders. Year-round planner rules are marked as test-branch only.
- **Checks.** Values come from a read-only extraction of the code, with the core rules re-read directly; one wording error about wet periods was corrected before commit. The page rendered in a browser without overflow. It is linked from the production README and the user guide.

## 2026-10-14: Location panel cut to search only

- **Request.** The user called the panel's search note noise and asked to remove it, the saved locations and the latitude and longitude fields, so that people choose places by search, and to push the change to the servers.
- **Changed.** The panel holds the search box and Analyze location beside the map. Saved locations are gone from the list, search, map pins and page load, together with the 71 files in `dist/snapshots/`, their index and the split script; every result comes from the archive API. A coordinate pair can still be typed or pasted into the search box. The GeoNames CC BY 4.0 credit moved to the page footer. Analyze stays disabled until a place is chosen.
- **Side effects.** Soil records and published planting seasons match only the exact coordinates of registered sites, so searched places show neither.
- **Verification.** 42 UI tests passed. Local browser checks covered the empty start, a Gainesville search and live analysis, a region view, a no-match search, a typed coordinate pair, a map selection, 390 px and no page errors. Deployed to http://fpt-server.ad.ufl.edu:8789/ with matching file hashes; a browser there showed the new panel and completed the Gainesville analysis.

## 2026-10-14: Season ribbon and Every winter tabs

- **Request.** The user chose concepts 1 and 2 of the season-chart sketches and asked for them as new tabs, keeping Season & exposures.
- **Built.** `dist/season-views.js` and `dist/season.css` add two tabs after Overview. The Season ribbon shows one band for all winters, split each day by stage, with grey hatching for winters without a calendar, transition dates with their middle-80% range, the planting rule beside the published planting season, grower-reported bloom and harvest months, and counted risks under their stage. Every winter shows one row per winter with frost, heat and heavy-rain marks and that winter's chill hours. Neither changes a number; both explain sites where the chill-triggered calendar does not apply.
- **Published months.** `scripts/build_benchmark_calendars.py` writes `dist/benchmark-calendars.json` from the benchmark registry. A site uses its own benchmark entry, otherwise the nearest benchmark site within 10 km, so the Waldo, Alma, Citra, Homerville, Arcadia and Sebring reference presets match their twins at 0 to 4 km. Months are placed within half a year of the matching model window; a fixed window had put a Michigan July-to-September harvest's September in the previous autumn.
- **Verification.** 42 UI tests passed, 6 of them new. In the browser all 71 saved sites rendered (50 drawn, 21 explained), with no text outside a chart, no overlapping lane labels, one published band per run of months, and no page errors. The per-winter marks equal the risk counts at all 50 sites with a calendar. Spot checks covered a southern site, partial and missing calendars, a live pin, the growing-setup note, the HTML export, keyboard tabs and 390 px. Deployed to the server with identical files, and a browser at the UF address completed a live Jaíba analysis, which had been unchecked since the VPN dropped.

## 2026-10-14: Season chart concepts

- **Request.** Scientists found the "Crop stages & analysis windows" chart hard to read, and the user asked for a thorough brainstorm on a more intuitive design.
- **Why it confuses.** Seven rows hold four kinds of thing drawn alike (a fixed chill-counting window, five stages, a grower action and a summary row). Five marks have no legend on the chart, the bars join median or percentile dates rather than real winters, the chill bar runs to 30 April although 50 hours are met in late November or December, and risks sit in separate cards.
- **Drawn.** `docs/research/2026-10-14/season_chart_concepts.html`, self-contained and drawn from the saved results of Waldo, Alma and Pelotas: a season ribbon, one row per winter, chill and heat clocks, a season wheel, and the current chart with quick fixes, plus further ideas with their data needs. It recommends the ribbon as the default view, with the other views behind switches.
- **Seen in the drawings.** At Waldo the model's bloom (median 22 Jan to 24 Feb) starts 10 days and ends 5 weeks before the February to March bloom growers report. At Pelotas the model's harvest (18 Oct to 10 Dec) runs 6 to 7 weeks ahead of the December to January harvest. At Alma all 8 winters with the earliest budbreak carry a frost mark on buds, flowers or young fruit, against 4 of the 7 latest.
- **Checks.** All five drawings for all three sites and both row orders rendered in a browser with no page errors and no text outside the drawings; at phone width the page fits and drawings scroll sideways. Nothing in the app changed.

## 2026-10-14: The app on the UF network

- **Request.** The user asked to run the app on the lab server at an address, like their other app on port 8788.
- **Deployed on 13 October.** http://fpt-server.ad.ufl.edu:8789/ serves the app to the UF network and VPN, without a login. The systemd user service `blueberry-ui-web` runs the existing proxy with Node 24.21.0 LTS from `tools/node`, checked against the release checksums, because the system Node 12 is too old. The API stays on loopback. Both services start at boot; until now the API had been started by hand.
- **Code.** The proxy accepts configured server names and still refuses other hosts and origins. Browsers withhold WebCrypto on plain-HTTP pages, which would have stopped place names and regional evidence loading; a script SHA-256 now takes its place there. The connection check runs on any HTTP address.
- **Verification.** 36 UI tests passed, 2 of them new. Curl from the VPN covered the page by name and address, health, a Jaíba search, an `app.js` identical to the local file, and the 403, 405 and 404 refusals; port 8787 was unreachable from the network. The VPN then dropped. A browser on the server's name, mapped to a local copy of the same files, showed a plain-HTTP origin without WebCrypto, a geography digest matching the evidence library, Waldo's 3 regional records and no page errors. A live browser analysis through the server address is still to be checked.
- **Tunnel loop.** The runbook loop logged exit code 0 every time, because `$(date …)` reset `$?`; it now saves the code first. The local preview and tunnel stopped at about 01:09 on 14 October and were restarted.

## 2026-10-13: Supervisor direction on growing setups and soil; breeder guide fix

- **Direction (relayed by the user, not implemented).** The base stays open field + ground, and users pick tunnel + ground, tunnel + pots or open field + pots. A setup changes risk factors, the production system and possibly the planting window. In-ground setups get soil warnings for pH, organic matter and salinity, with amendment advice. Thresholds are to be set with a UF extension specialist.
- **Checked against existing evidence.** The 2026-09-21 management review supports rain protection and higher daytime heat under tunnels. It also reports harvest 2 to 5 weeks earlier and no frost protection from unheated Georgia tunnels. Pots add root-zone heat and irrigation dependence.
- **Soil sources for a commercial product.** SoilGrids and ISRIC's global salinity map are CC BY 4.0. SoilGrids' 1 km pH layer is about 79 MB per depth and holds means only. HWSD v2 is CC BY-NC-SA, so it cannot be used commercially. FAO's GSASmap states no licence and lacks Eurasia and the Near East/North Africa.
- **Breeder guide fix.** The two planting settings added on 2026-10-12 reused P47 and P48, which already belonged to bud-stage freeze and bee-flight hour. The page saves comments by number, so in a browser test a bud-stage comment came back as the planting comment after reload. They are now P50 and P51, and the same test keeps both comments. The guide has 67 comment boxes, P1 to P51, with no duplicates.

## 2026-10-13: Worldwide town and village search

- **Problem.** Searching "Jaiba" found nothing. The search covered only Natural Earth's 7,295 larger towns, and Jaíba, Minas Gerais, about 35,000 people, is not one of them. The nearest listed towns are Janaúba, 64 km away, and Januária, 76 km.
- **Why the full list.** On our 32 benchmark towns, GeoNames' 15,000-person tier found 14 and its 500-person tier 29. Only the full list of 5.2 million populated places found all 32.
- **Built.** `place_index.py` builds a 1.03 GB SQLite full-text index of 5,170,300 current populated places from the 2026-10-13 GeoNames dump, CC BY 4.0. The API serves it at `/api/places` in 0.1 to 7 ms per query, without logging what is typed. The page takes towns from the server and regions and countries from Natural Earth, and falls back to the local list with a clear message. A searched name now labels the place card and the assessment.
- **Ranking.** An exact name wins unless a prefix match is about 100 times larger, so "new york" gives New York City and "jai" gives Jaipur. Later words can name the region, so "alma g" gives Alma, Georgia. Entries the list could not tell apart are merged.
- **Verification.** 262 server tests passed, 11 of them new. Deployed with matching hashes, and only the API was restarted. Browser checks covered Jaíba from search to live analysis, other small towns, the fallback, rapid typing and phone width.
- **Open.** Street addresses and farm names would need a self-hosted OpenStreetMap geocoder or a paid service. That decision belongs to the commercial launch.
- **Tunnel.** The local SSH tunnel to the API died with exit code 255 after 44 minutes, when the server stopped answering keepalives during a network drop; the server and API stayed up. The tunnel now runs in a reconnect loop, documented in `docs/UI_RUNBOOK.md`. In a test, killing its SSH process left the API back 6 seconds later.

## 2026-10-12: Chill requirement 50 hours and the IBO 2024 report

- **Chill requirement.** At the user's request `stage_thermal_v3` now needs 50 chill hours, not 100, the same as the legacy profiles. Nothing else in the model changed, and the 100-hour profiles stay as sensitivity comparisons.
  - The winter calendar now applies at 50 of the 71 saved locations, up from 41. Nine moved from the scan, among them River Valley, Dole, Barben, Wauchula and Sebring. No production-system majority changed.
  - Waldo flowers from 22 January and harvests 29 March to 10 May, within two days of the legacy calendar the thermal sums came from. Papanduva gets a calendar in all 15 winters, and River Valley in 14, with harvest 24 March to 29 April.
  - Burgaw now breaks bud on 29 December, so flowering freeze ranks there in 11 of 15 winters. Pollination gaps rank at Burgaw, Elizabethtown and Loris.
  - Planting windows: 50 locations now get one. The rule's overlap with published planting months falls to 22%.
  - Verification: 251 server tests passed after updating one test that pinned the 100-hour chill date. Legacy parity held at 18 sites with 0 differences. The change is deployed with matching hashes, and snapshots, packet and benchmark were regenerated. Browser checks covered River Valley, Waldo, Papanduva and Arcadia.
- **IBO 2024 report.** The user supplied the complete 2024 edition. It is stored on the server with text and an updated manifest, not in Git. Its licence on printed p.235 allows reuse with attribution.
  - Five region agents proposed 2024 citations and records with verbatim quotes. A script checked every quote against its printed page, and each summary was reviewed by hand. 9 proposals were rejected.
  - The registry now holds 156 records, up from 91, with 301 citations, 127 of them from 2024. New events include Huelva's warm 2022/23 winter cutting chill, South Africa's cold 2023 winter, Peru's El Nino detail and British Columbia's bloom heat. The audit file is `docs/research/2026-10-05/ibo_2024_extraction.json`.
  - Verification: the library validator and 34 UI tests passed. The Regional evidence tab shows editions 2023 to 2026 at 11 checked presets.
- **Docs.** The formula guide's Waldo example was recomputed for 50 hours. The explainer, production README, user guide, runbooks, plans and IBO review were updated, and the UI was left running throughout.

## 2026-10-12: Planting window calculated from modelled budbreak

- **Decision.** The user approved Paul's R planting rule as the app's planting window. Planting ends 30 days before modelled budbreak and lasts 75 days. The R labels the offsets preliminary and cites no source, so the app says so.
- **Model.** Only `stage_thermal_v3` has the rule. Each winter gets its own window, and the typical window counts back once from the median budbreak, with the p10 and p90 budbreak as its spread. This avoids the R bug that took medians of month-days and could draw reversed or phantom windows. Legacy profiles are unchanged.
- **API.** The planting block (`budbreak-planting-v1`) is available, not applicable ("Set by management" or "No calculated window") or unavailable. The UF/IFAS, UGA and Embrapa regional seasons stay as a "Published season" line for registered regions only. Dropped pins get a calculated window but never a published season.
- **UI.** The Overview card and panel show the calculated window. The Season timeline has a new Planting lane before budbreak, and the calendar tables have planting rows and a per-winter column.
- **Results.** 41 of the 71 saved locations get a window: Papanduva 19 Apr to 3 Jul, Waldo 11 Oct to 25 Dec, Alma 30 Sep to 14 Dec. The other 30 have none: 18 set by management and 12 with too few calendar winters. In the literature benchmark the rule covers 38% of published planting months at 15 sites, and its months usually start earlier. No weather, calendar or risk number changed in any snapshot.
- **Verification.** 251 server tests passed in staging, 8 of them new. Legacy parity held at 18 sites with 0 differences. The changed files are deployed with matching hashes, and only `blueberry-ui-api` was restarted. Snapshots, the production packet and the benchmark were regenerated. Browser checks at 1440 and 390 px covered six presets, a live pin and a single winter, with no errors, CSP violations or overflow.
- **Docs.** The user guide, runbooks, production README, formula guide and explainer now describe the calculated window, with three explainer screenshots recaptured.

## 2026-10-12: Plain-language platform explainer for presentations

- Added `docs/presentation/platform_explained.html` with 12 screenshots of the running app. In very simple words it explains:
  - the weather source and grid;
  - what "Mean 199 chill hours · 28.6 chill portions" means;
  - the production-system rule and the 2018 calendar chain;
  - medians and p10/p90, and an annotated copy of the Season & exposures window;
  - the calendar-or-scan tests and the managed-cycle scan;
  - top risks, planting guidance and regional evidence;
  - the other tabs, limits, an FAQ and a glossary.
- The worked example uses Papanduva. The 2018 chain, recomputed from the server archive, matches the model's dates.
- Checked in a browser at 1440 and 390 px with no errors or overflow. Documentation only.

## 2026-10-12: Corrections, request safety, supervised API and scheduled evidence jobs

- **Scan accounting (Paul-approved).**
  - Every scanned cycle is now complete, stalled slow, stalled at the horizon, or weather incomplete.
  - Freezes count complete cycles only, and stalls form a separate `cycle_failure` family. The UI shows "Cycles do not complete" or "Recurring freeze exposure".
  - The 30 scan-primary presets keep their windows. Grand Junction, MI gains seven favourable starts, and Odemira and Pelotas gain one each.
- **Other corrections.**
  - Leap-day median fix (v3 only).
  - Thresholds quoted from profile values, and the v3 disease note fixed.
  - Florida planting text now cites UF/IFAS HS1525.
  - Overview chill-shortfall line; the bud lane starts at budbreak.
  - Escaped HTML everywhere and a shared https-only link check.
  - A hardened evidence validator.
- **Request safety and service.**
  - Host, Origin and Sec-Fetch-Site checks on the proxy and the API, plus a 504 timeout code and CSP, nosniff and no-referrer headers.
  - A result cache and an access log without coordinates.
  - The API runs as a systemd user service with crash restart and a 5-minute watchdog.
- **Evidence jobs.** Nine jobs are on systemd timers: RMA cause of loss, RMA summary of business, NOAA Storm Events, GHCNh stations, station truth, ODEPA census, ODEPA exports, Eurostat Comext and SENAMHI. The first backfills total 2.06 GiB, and the RMA 2022 check matches.
- **Research.**
  - Event checks v2: the US freeze is represented, the Waikato frost is missed through the coastal cell, and the Chile frost is absent from the pin cells.
  - 15 IBO records corrected.
  - Benchmark notes updated. Two scoring month changes are proposed for Paul's approval.
  - Stale v2 documents flagged and the Mexico citation fixed.
- **Disclosed breach.** An agent used a browser user agent for RAN Agromet and the INIA data-request form for Chilean station series. Those series are withheld from the repository pending the user's decision.
- **Verification.**
  - 243 server tests passed. Legacy parity held at 18 of 18 sites with 0 differences.
  - 34 UI tests and 7 watchdog tests passed.
  - Browser checks of 6 presets and 2 live pins at 1440 and 390 px found no errors.
  - Benchmark scores are unchanged.

## 2026-10-11: Review of Astra's work and source expansion for every region

- **Astra's work reviewed.** "Astra" is the model `openai-codex/gpt-6-astra`. It worked here from 15 September to 5 October 2026: 14 commits, plus the cycle ruler and the Regional evidence tab, which other models committed. Three review agents covered science, IBO evidence and code.
  - Science: careful and mostly correct; 17 of 20 checked sources fully support its claims. The risk gate saturates, chill shortfall is hidden at nine sites, and the planting window lacks Paul's sign-off.
  - IBO evidence: 47 of 53 registry records supported, 5 partly, 1 page mismatch. The Chile and Waikato frost checks used the wrong window and cell.
  - Engineering: 1 high, 6 medium and 13 low findings; no result-changing bug.
- **Sources researched.** Fourteen agents covered ten regions, three global themes and an ingestion design: 824 unique sources in 69 countries (686 opened) and 174 extraction jobs. Package and roadmap: `docs/research/2026-10-11/`.
- **Coordinator checks.**
  - The server suite passed 141 tests, and the deployed code matches the repository.
  - Re-checked the Chile and Waikato grid minima on the server: the stations were 6 to 8 °C colder than the cells.
  - Verified the RMA 2022 blueberry losses (217 rows, USD 77.65 million, freeze USD 49.08 million) and corrected the Bacon County figure.
  - Confirmed NOAA GSOD stopped in August 2025, and confirmed the HS1525, DMC, NIWA, SENAMHI, ODEPA licence and FreshPlaza robots claims.
- **Fixes.** Corrected five user-guide statements and added a correction note to the IBO review. Removed the agent-installed `.venv` packages and agent temporary files. No model, API or UI behaviour changed.

## 2026-10-05: Complete user guide and current-state explanation

- Added `APP_USER_GUIDE.md` in simplified technical English, with a formal ASD-STE100 compliance disclaimer. Covers completed improvements, current project stage, all six tabs, calendar requirements, risk interpretation, missing values, service errors, the reported screenshot, and approved future work.
- Clarified different production/reference chill definitions and the all-endpoints calendar dependency. Recorded existing summary-wording and scan-accounting limitations rather than describing them as fixed.
- Checked current source constants, all 71 saved assessments, selected risk counts, the 91-record evidence library, and all 28 guide links. No model changes, service startup, new live-pin run, or backend test run.

## 2026-10-05: Approval for cool-climate phenology and scan accounting

- The user reports Paul's sign-off for both open items. Recorded the next steps in the handover: separate thermal non-completion from missing weather and actual freeze exposure, then review sourced cultivar-specific settings rather than applying one northern-highbush profile to every cold location.
- Target cultivars, production systems and site-year observations would support calibration and validation. Approval is not evidence for particular coefficients. No code, model settings or runtime changed; no tests run for this documentation-only update.

## 2026-10-05: Explaining locations with no production window

- A pin labelled "Near Yakima" (46.738, −121.456) had no flowering or harvest window. Its weather cell, centred 46.5, −121.25 in the Cascade Range, is too cool for the v3 stage constants. Budbreak arrives 26 May to 7 Jul, a later stage misses its heat requirement within the 300-day horizon in 14 of 15 winters, and no scan start completed a cycle. Naantali, Finland behaves the same. Yakima city, Prosser, Corvallis and South Haven, MI keep calendars. Lynden, Cherryfield and Lac-Saint-Jean fall back to scan windows, and all 71 presets have windows.
- The Production window card and the scan panel now state the cause. Top risks reads "Not assessed" or lists recurring freeze families instead of "None recurring", and scan windows quote the chill-clock reason. Frontend only; browser-verified with no page errors and no overflow at 390 px.
- Open: northern-highbush and cool-climate stage constants, and whether scan cycles that miss the 300-day horizon should count as stalled.

## 2026-10-05: Regional evidence tab from the IBO reports

- Added a sixth dashboard tab, Regional evidence, backed by `dist/evidence/ibo-regional-v1.json`: 91 records checked against the complete IBO 2023, 2025 and 2026 reports (39 events, 42 practice, 10 constraints; 51 scopes in 23 countries; 172 page citations). Cards state scope, period, crop context and limitations and link to the cited pages; filters cover harvest, management, weather and resources. HTML and JSON exports keep every matched record and the weather analysis ID. Weather calculations, constants, snapshots and backend code are unchanged.
- Records match the pin's containing country and region polygon. Region IDs are tied to the SHA-256 of the existing Natural Earth bundle, which fixed a reproduced error: matched by name, Washington, DC had received the Pacific Northwest heat-dome record. A hash mismatch, missing library or geography, or a stale lookup shows no evidence and leaves the weather untouched.
- Browser checks: 71 presets with unchanged weather payloads (61 matched, 10 no curated match), six live coordinates including daily-only Bermuda, fault and stale-lookup states, keyboard tabs, 390 px layout and real exported HTML/JSON. `node --check` passed for `app.js`, `places.js` and `evidence.js`; the Python suite was not rerun because no backend code changed.

## 2026-10-05: IBO report collection and integration decision

- Retrieved complete 2010 USHBC precursor, 2022, 2023 and 2025 PDFs on the designated server; reused the supplied 2026 report and prior review. Five complete reports total 802 physical PDF pages. Also retained a separate 38-slide 2016-data preview, a limited 2012 public transcript and seven 2024 secondary excerpts. Full 2021 and 2024 remain access-blocked; the inventory distinguishes older confirmed editions, previews, broken/truncated copies and unread sources. No registration forms, paid access or weather downloads.
- Read the acquired substantive text and inspected relevant charts. Recorded differing year conventions, historical revisions and shared source lineage. Peru's delayed pruning in 2024 shows why temperature alone cannot predict managed harvest timing. Recommended a reviewed regional evidence layer and dated event registry, then citation-first retrieval; no model or RAG implementation. Review, source manifest and comparison JSON are in `docs/research/2026-10-05/`.
- Ran read-only archive extraction for seven new event comparisons. Four GA/NC cells show freezing on 13 March 2022; the sampled Linares, Chillan and Waikato cells do not reproduce the reported regional freezes. These are unresolved geography/weather/species checks, not crop-loss validation. No application tests, recalibration, API/UI startup or deployment.

## 2026-10-02 — End-to-end test and "no data" fixes

- Three test agents covered about 80 global coordinates, API input edge cases and browser flows at 1440 and 390 px. Causes of "no data": the UI was served without its `/api` proxy (start it with `node scripts/preview-ui.mjs`, not a plain static server); 1,509 small-island land polygons have no hourly cache and returned HTTP 500; coastal and city-centre pins up to about 2 km outside the Natural Earth coastline were refused as ocean; coordinate fields dropped decimal commas, N/S/E/W letters and pasted pairs, which silently changed or blocked the location.
- Fixed: hourly gaps now return the daily climate with production marked unavailable; pins within 5 km of mapped land are accepted with `land_snap_km` in provenance (source cell still from the original pin); strict parameter parsing with specific 400 messages, 422 for sea points, 500 JSON with server-side tracebacks, health reports busy. UI accepts decimal commas, hemisphere letters, DMS/DDM and pasted pairs, word-prefix search with Enter picking the top result, automatic retry after a self-cancelled request, clearer error text. Server suite 140 tests passed; live checks: Bermuda, Malé, Tahiti daily-only; Hong Kong, Copenhagen, Miami accepted; open sea 422.
- Not fixed (needs decisions): download of about 409 extra hourly blocks for islands, northern-highbush stage constants, planting guidance for arbitrary pins, polar ice classified as Deciduous.

## 2026-09-30 — Bud-stage freeze and pollination gap from innov8.ag review

- Reviewed innov8.ag Market Insights from its public page and page code. Adopted two ideas that fit the product and have published thresholds: frost checked at the bud stage (NC State critical temperatures) and honey bee flight hours (12.8 °C, 09:00–17:00) with a pollination gap of 4 or more flowering days in a row without flight (UF/IFAS IN1237 receptivity). Rejected fixed-from-1-January GDD stages, frost kill percentages, sine-interpolated hours and the market features. Notes in `docs/research/2026-09-30/innov8_market_insights_review.md`.
- Both are ranked families and managed-cycle scan measures in `stage_thermal_v3` only. Across 71 presets only Burgaw, NC gains a ranked risk (bud-stage freeze, 8 of 15 winters). Scan recall of published harvest months rose from 0.79 to 0.81; chill-clock benchmark scores did not change. 130 server tests passed and legacy v2 reproduced 18 of 18 snapshots exactly. Dashboard, breeder guide (P47–P49, Q14) and production README updated. The bee model uses temperature only, so it is an upper bound and not validated against pollination records.

## 2026-09-30 — Formula guide for breeder review

- Added `docs/weather/production/model_formulas_for_breeder_review.html` so a breeder can review and comment on every formula without reading code. It covers chill hours and portions, budbreak, degree-day stages, production-system rules, when the winter calendar applies, the managed-cycle scan, risk events and ranking with Wilson intervals, the hourly disease models, unranked exposures and planting. It also has a 46-row settings template and 13 questions, each with a comment box, a notes download and a print layout.
- The Waldo 2016–17 worked example, the chill-portion table and the infection-index tables were recomputed with the production code; the trace reproduced the model's chill, budbreak, flowering and harvest dates. Verified in a browser, on a phone-width layout and in Chrome print output. No model behaviour changed.

## 2026-09-30 — Corrected two v3 statements

- Rechecked v3 claims against the committed snapshots while preparing a before/after explanation. The thermal constants do not keep Waldo's old calendar: with 100 chill hours its flowering start moves from 20 January to 7 February, while harvest moves only from 31 March–10 May to 4 April–12 May. Fixed the API change list, the production README and the regenerated packet and snapshots.
- River Valley's 3 April–6 May v3 harvest is a hypothetical chill-clock calendar. Only 10 of 15 winters reach 100 hours, so the managed-cycle scan is its primary window. Corrected the handover and plan, and recorded that 10 of the 18 pilot sites, all in central and south Florida, now use the scan.

## 2026-09-28 — Production v3, literature benchmark and decision-first dashboard

- Reviewed the v2 model against its own outputs and the literature. Fixed day offsets gave every site a 40-day harvest and put central Chile's harvest in Sep–Nov against published Nov–Jan. The 50 h chill requirement sat below published Emerald values, and the daily disease rule had no source. v2 gave no production window at 14 of 46 southern-highbush benchmark sites, including all of Peru and Mexico.
- Implemented `stage_thermal_v3` as primary (`open-field-production-v3`, `location-evidence-v5`). It adds degree-day stages after budbreak, a 100 h chill requirement, chill portions reported beside chill hours, the hourly BAS anthracnose / SAS Botrytis infection model and a `chill_clock` applicability test. Where the chill clock does not apply, a managed-cycle scan of 24 start dates gives the production window. A review pass fixed the scan: stalled cycles now count as failed crop-loss cycles, and favourable starts come from the Pareto front plus near ties, which can no longer come out empty.
- Built a 53-site literature benchmark, drafted from published sources and independently re-verified before any model comparison. Across the 46 southern-highbush sites, v3 leaves none without a window (v2 14). The chill-clock harvest midpoint falls in published months at 25/27 sites (v2 19/32) and bloom at 13/19 (v2 6/20). Scan sites cover 79% of published harvest months. Misses are documented: management-driven evergreen sites, high elevation, rabbiteye, tunnels, northern-highbush bloom timing, a sea-dominated coastal cell and Peru fruit-development time.
- Dashboard: decision strip (system, window, top risks, planting), managed-cycle scan panel, 71 presets including the benchmark sites, benchmark page, separated busy/disconnected API states, stable export names and fixed preview MIME types.
- Verification: 127 server tests on deployed `code/`; exact legacy parity for 18 sites with `stage_risks_v2` as primary; live API at Clinton, NC and Chao, Peru; browser checks with no page errors and no 390 px overflow. Only `blueberry-ui-api` restarted. Constants remain provisional; this is not field validation.

## 2026-09-24 — Global blueberry phenology research

- Completed a 43-source synthesis covering bud initiation/differentiation, floral and vegetative budbreak, flowering, ripening and commercial harvest across global production regimes. Regional examples retain cultivar, site, system, stage definitions and source-access limitations. Usual dates, forecasts and favorable management scenarios are treated separately.
- Read-only audit: 18 saved sites, 270 site-years, 235 computed calendars; all retain +14/+35 flowering and +70/+110 harvest offsets. Reconstructed Emerald/Jewel flowering quantiles from published logistic coefficients and recorded the treatment/anchor/formula caveats.
- Corrected earlier recommendations and source descriptions: Kirk & Isaacs is not the 15-year harvest series; Epagri is modeled zoning, not cultivar-date validation; Piracicaba reports five rather than zero hours below 7.2°C; general CH/CP conversion and several harvest/chill-delay/accuracy claims lack support.
- Delivered `docs/weather/GLOBAL_PHENOLOGY_REVIEW.md` and calculation audit JSON; updated earlier research and roadmap pointers. Citation and arithmetic checks performed. No live model, snapshots, weather data or UI changes; no tests rerun or scientific validation claimed. Further parameter changes require a separate implementation decision and relevant observations.

## 2026-09-24 — Removed platform heading

- Removed Blueberry Decision Support from the visible page and browser-tab title. The lab logo remains; search and map follow the header without the hero's blank space. Direct-map layout visually inspected. No backend changes.

## 2026-09-23 — Simplified platform title

- Replaced the introductory block with Blueberry Decision Support and retained the lab logo. Removed redundant header text; moved connection status to Methods & data. Assessment baseline and scientific caveats remain.
- Desktop browser inspection and 320 px reflow passed. No backend changes or tests rerun.

## 2026-09-23 — Responsive layouts across screen sizes

- Replaced fixed heading/map sizing with fluid width/height rules, reduced landscape spacing, added safe-area padding and mobile keyboard viewport hints. Narrow coordinate/action/stage controls stack; map follows container size through ResizeObserver.
- Bounded search/saved lists by viewport height. Kept select text at 16 px and gave charts labelled, keyboard-scrollable regions rather than shrinking labels below readable size.
- Verified five expanded assessment views at 15 viewport sizes, 280 px through 3840 px, without page overflow. Landscape map is 260 px in a 390 px viewport, previously 500 px. Container-only resizing, narrow search-to-point flow, 640 px high-DPI reflow, arrow-key chart scrolling and downloaded HTML at 320 px passed. Screenshots inspected; no page errors; map.js syntax passed. Chromium emulation only, not physical-device or cross-engine certification.

## 2026-09-23 — Geographic search and gallery design

- Expanded search beyond saved sites to local reference settlements, regions and countries. Saved names remain searchable in their own group. Added accent/case matching, multi-term context, country aliases, bounded results and keyboard selection with stale-query protection.
- Region/country selection frames the principal polygon, clears point coordinates and disables Analyze until the user selects a specific point. Previous committed assessments remain named. Search and browsing never request weather automatically.
- Applied the supplied white/gray gallery palette, centered responsive 80px desktop heading, quiet typography, 28px shadowless map/cards and pill controls. Retained the lab logo, science caveats, stage categories and report styling.
- Verified city/region/country/alias/accent/empty/saved queries, keyboard controls, real London hourly analysis, Iowa area-to-map-point flow without extra API requests, delayed query races and unavailable-reference saved fallback. All five views fit 320/390/768/1440 px. Actual HTML/JSON exports retained London while draft selection changed. JS syntax checks passed; backend tests not rerun for this frontend-only change.

## 2026-09-23 — Lab branding and UI copy

- Added the supplied logo as a transparent native-resolution PNG in the header; original AVIF remains untouched and outside publication. Replaced generic branding and promotional headings with concrete climate-analysis labels.
- Refined navy/blue colours, typography, panel corners and responsive header. Preserved scientific caveats, data definitions and controls.
- Chromium desktop/mobile inspection passed, logo loaded, all five assessment views fit 390 px without horizontal overflow and no page errors. `node --check` passed for app.js and cycle.js. No backend tests rerun.

## 2026-09-23 — English-first vector map and local place context

- Confirmed `97c8a3a` was on origin/main before implementation as requested. Replaced Leaflet assets with MapLibre 5.24.0 and an adapted OpenFreeMap Positron style. English/romanized labels, quieter markers, native wheel/pinch/keyboard, source-cell overlay and coordinate fallbacks retained.
- Added browser-local Natural Earth lookup: 258 country/territory areas, 4,596 admin areas and 7,295 sampled settlements in a 2.97 MB compressed bundle. Polygon containment assigns country/region; nearest represented settlement and great-circle distance are separate. Raw source cache stays on server. Public-domain provenance, source hashes and reproducible generator included.
- Place cards, assessment/cycle headings and actual HTML/JSON reports now retain resolved display context without changing API site, coordinates, science, planting or analysis ID. Async guards keep old name responses from overwriting newer pins/reports. Saved farm names remain primary.
- Verified ten global/border/ocean/dateline points, real Iowa analysis, all 18 saved names, delayed out-of-order naming, actual downloads, blocked map-library/reference-data fallbacks and desktop/mobile layout. Syntax checks passed. Boundaries/settlement coverage remain approximate; no geocoder queries, backend changes or hosted deployment.

## 2026-09-22 — Map wheel zoom

- Enabled scroll-wheel zoom in the map element and updated its interaction help. Existing zoom buttons, keyboard controls and pin-selection behavior remain unchanged.
- Chromium verification: wheel zoom 2→3→2, no page movement while zooming, unchanged coordinate fields and zero analysis requests. Scrolling outside the map moved the page normally. Visually inspected the zoomed map; JavaScript syntax check passed. No backend changes or tests rerun.

## 2026-09-22 — Arbitrary-cell hourly API integration

- Added a read-only checksummed adapter over the completed hourly cache and connected unindexed map requests to it. Existing indexed cells keep their verified normalized series. No downloads, writable acquisition database, unbounded extraction cache or duplicate global arrays.
- The user's 43.060861, -92.548828 point now returns hourly data, 15 complete modeled winters and two recurring risks. London, Chile, Nairobi and Sydney also worked; measured server analysis times were 0.62–2.04 seconds. Evergreen/chill-not-met results remain explicit rather than invented calendars.
- Server suite: 102 tests passed, including six new actual-Zarr extraction/integrity regressions. All 18 saved production/annual summaries were unchanged; Citra, Papanduva and Waldo raw/indexed hourly parity passed. Offline smoke checks preserved 59,269,420,065 transferred bytes and 35,853 downloaded objects; offshore refusal passed.
- Deployed only the adapter/API/test files and restarted the private API. Restored local preview/tunnel and opened the UI. Browser verified the reported coordinate and an actual new map-click selection, hourly coverage, calendar and source-cell identity without page errors. Updated UI coverage copy and operating/design documentation. Soil, regional planting support, scientific validation and hosted deployment remain separate.

## 2026-09-22 — Map-first UI redesign

- Replaced the long report-first dashboard with a map/location workspace and five assessment views: Overview, Season & exposures, Climate history, Soil & setup, Methods & data. Vendored Leaflet 1.9.4 with its license; OSM supplies attributed geographic tiles only. Search filters saved sites locally; coordinates and map pins support arbitrary-point requests through the existing API.
- Added explicit Analyze, separate draft/committed location states, browser cancel/stale-response guards and an actual-response hourly source-cell outline. Coverage distinguishes global daily access from the 19-cell hourly adapter, regional planting and partial soil. No new backend, acquisition, snapshot generation or scientific formula.
- Recurrence cards show rank, numerator/denominator, uncertainty and excluded reasons. Stage colours identify windows, not severity; selected-winter cards compare with historical means and retain exact values/definitions. Corrected the primary whole-production timeline start to budbreak, matching the already-implemented backend window.
- Browser verification: 18 presets × five views; 270 winter/stage views and 1,350 exact metric values, including 209 zeros and 22 missing values. Keyboard navigation and management-state retention passed; desktop/mobile inspected; all five views fit 320/390/768/1440 px without page overflow. Real daily-only land, shared-cell land and offshore requests passed. Simulated disconnected API, blocked tiles/library and delayed/cancelled responses behaved correctly.
- Actual HTML/JSON downloads preserve winter 2014, fruit, tunnel/pots and selected chart labels. HTML contains all five views with expanded definitions and no inert buttons/selects or map requests; JSON production, planting and analysis ID match the original Homerville snapshot. JavaScript syntax checks passed. No backend test rerun for this frontend-only revision.
- Updated the design plan, runbook and handover. Local preview and archive tunnel are running. GitHub publication follows the standing authorization; hosted Sites is not redeployed. Map tiles disclose IP/origin/viewed area to OSM; no geocoder, paid key or telemetry added. Scientific validation and general hourly extraction remain outstanding.

## 2026-09-22 — GitHub publication authorized

- The user lifted the earlier no-GitHub restriction and requested the verified science/dashboard changes be published with relevant comments. Prepared the implementation, regression tests, 18 derived snapshots, three-site report and method/source notes for the existing `origin/main`; remote and local history matched before preparation.
- Reviewed the selected changes for credentials and private source material. Original R workflows, supplied reports/transcripts, bulk weather data and local caches remain excluded. Replaced the UI runbook's machine-specific checkout path with a project-root instruction.
- Commit notes record scope, prior verification and remaining scientific limits. No tests were rerun for this publication-only step; the implementation checks below are the evidence. The local UI and API were confirmed running during the preceding launch request. Push success must be established from the remote branch, not inferred from this entry.
- No hosted-Sites redeployment, new acquisition, phenology calibration or management/genotype work.

## 2026-09-22 — Stage-aware risks, establishment guidance and dashboards

- Implemented `stage_risks_v2` / `open-field-production-v2` and API `location-evidence-v4`: individual-winter stage exposures; ≥50% recurrence with ≥12 complete winters; qualified headlines only; full `by_id`/`demoted` evidence and reasons; equal ranks for equal frequencies. Evergreen/unknown primary clocks cannot support crop/chill-shortfall headlines.
- Disease-weather now ranks as one family with flowering, fruit-development and harvest evidence. Added cold-or-wet pollination days (with the separate spoken cold/dry hypothesis), fixed-hemisphere >21 °C warm-midwinter hours, fruit Tmin ≤0 °C frost exposure and stage dry spells. Daily-only fallback reports Tmax warm **days**, not hours. No invented seasonal-loss thresholds for pollination, warm weather or dry runs.
- Researched primary blueberry guidance and implemented `regional-establishment-v1`: Florida mid-December–mid-February; Georgia winter, shown approximately December–February; Santa Catarina winter while dormant, shown approximately June–August. UGA/Embrapa do not specify exact endpoints; those months are display conventions. One independent establishment window per covered region; unknown geography declines. The uncited budbreak-offset formula was not adopted. Sources and reasoning: `weather/production/README.md`.
- Updated both dashboard views, per-winter/sensitivity tables, sources and HTML/JSON exports. Regenerated 18 snapshots and the Waldo/Citra/Papanduva production packet from existing data. Deployed only changed science/API files and tests; restarted only `blueberry-ui-api`. No weather/soil acquisition, public hosting update or GitHub commit/push.
- Verification: full backend suite **96 passing**; **39 production/API tests** passed after a browser-discovered missing method field was fixed. All 270 prior preset chill/date/stage-exposure records and all 18 annual summaries/weather hashes preserved. Independent input-level reconstruction matched 29 complete crop-years at River Valley/Papanduva; a daily-only land probe returned 15 warm-day windows. Browser checked 18 presets, 135 winter/stage views, 855 displayed values, empty/evergreen states, keyboard/state retention, real API paths and actual downloaded reports. Desktop/mobile inspected; no overflow at 320/390/768/1440 px. JavaScript syntax checks passed.
- River Valley's unchanged calendar still predicts harvest 23 April–2 June: heavy rain ranks **14/14**, disease-weather **12/14**. The supervisor's early-April expectation needs phenology review. Software/source consistency is not scientific validation; legacy phenology constants, warm grid bias, no calibrated management effects and the indexed-cell API limit remain.

## 2026-09-22 — Land hourly cache complete

- `global_hourly.py` finished at 01:12 UTC: 6,958 / 6,958 land blocks validated (T2M, T2MDEW, 2010–2025), 20,885 cached objects, 40.5 GB on disk against a 28.7 GB pre-run estimate (estimate drew on the smaller pilot chunks; capacity gates unaffected). State `complete`; tmux session exited normally. No rerun, no code change. Any-cell extraction from this cache remains Phase 3.1 of `docs/FUTURE_PLAN.md`.

## 2026-09-21 — Supervisor review recorded, direction research, future plan

- Recorded Paul's River Valley review as decisions only in `docs/weather/SUPERVISOR_REVIEW_RIVER_VALLEY.md`: risks count only when their stage overlaps the production window and they recur often enough; disease must be ranked; add pollination-unfavourable days, warm mid-winter hours, berry-stage freeze, stage-specific dry spell and a single planting window from his R code; frost-at-every-stage, protection feasibility, post-harvest and wet-picking items deprioritised; management layer after field risks.
- Eight parallel research scouts (Paul's new R file, code audit, crop-modelling second opinion, validation data, genotype layer, management layer, weather inputs, product/deployment); reports saved under `docs/research/2026-09-21/`. Findings: planting = budbreak −105…−30 d and the "multiple windows" are a month-day median artefact; Paul's R already computes Dynamic Model chill portions (chillR constants) but never uses them; ten constants differ from `legacy_paul_v1`; metric definitions are spread over seven code locations; UF trial logs are the highest-value validation data; a cited 40-cultivar attribute table can drive a rule-based shortlist; tunnel/pot effects have published parameters; keep NASA POWER with daily→hourly reconstruction and on-demand hourly; deploy behind token auth over Tailscale.
- `docs/FUTURE_PLAN.md`: six phases with de-duplicated builder-day estimates (14 / 18 / 12 / 8 / 6 / 11), milestones (team-usable ≈ 37 days, v1 four outputs ≈ 51 days ≈ 3 months, validated ≈ 69 days gated on UF data), decisions and data requests by person, critical path and risks.
- Plain-language HTML of the risk-factor review (`docs/weather/RISK_FACTOR_RESEARCH.html`, source `RISK_FACTOR_RESEARCH_PLAIN.md`) added from the 2026-09-15 session. Paul's new R file added to `.gitignore` as a private input. No code, formula, acquisition or deployment change.
- Later the same day: user authorized a land-only global hourly cache. Added `pipelines/weather/global_hourly.py` (plan/run/status; land blocks via `LandMask`; same `Downloads.get` checksums, retries and capacity gates; shared `tiles` table) and `tests/weather/test_global_hourly.py` (2 tests, pass on server). Plan: 3,479 land blocks, 6,958 jobs, ≈ 29 GB measured estimate. Worker started in tmux `blueberry-weather-hourly` at 20:33 UTC; 44 jobs in 80 s. `DATA_ACQUISITION_HANDOFF.md` exclusion amended; `SERVER_RUNBOOK.md` gains the monitor/restart section; `FUTURE_PLAN.md` Phase 3 revised (reconstruction and on-demand fetch dropped; −4 builder-days).

## 2026-09-15 — Risk-factor research review and chill-model data check

- Eight parallel literature scouts (chill models, forcing/phenology, freeze, heat/VPD/radiation, rain/disease, water balance, pollination/pests, production-system classification) with primary sources; synthesised in `docs/weather/RISK_FACTOR_RESEARCH.md`: one-page verdict, formula scorecard (keep/change/add with sources), ~35 new computable metrics by stage with inputs, thresholds and confidence, implementation order, open uncertainties.
- Data check `pipelines/weather/chill_comparison.py` on all 18 hourly cells (`docs/weather/chill_comparison.json`): current rule inflates Georgia chill by 60–200 h versus the standard 0–7.2 °C Oct–Feb band; band reproduces FAWN Sebring (104 vs 108 h) and undercounts Gainesville (346/296 vs 503 h) consistent with the +1 °C grid warm bias; CH/CP ratio 12–13.5 in Georgia/north Florida but 4.5–11 in south Florida and 7.0 at Papanduva; Papanduva 183 h but 26 chill portions ≈ Waldo. Negation hours (>21.1 °C mid-winter) 170–940 across the panel.
- Conclusions: chill definition, 50 h anchor, 150 GDD budbreak, single harvest offset, disease-day rule, bloom-only freeze threshold, VPD mean and whole-season dry spell all need revision; pollination weather, stage-aware freeze, bloom heat, leaf-wetness disease rules, stage water balance, evergreen calendar, SWD and post-harvest heat are missing. No formula changed; `legacy_paul_v1` remains the executed profile.

## 2026-09-15 — Southeastern evaluation panel and cell-keyed hourly lookup

- User selected a 15-site panel: 4 Georgia (Georgia/Alma pilot, Homerville, Valdosta, Folkston) and 11 central/south Florida (Dole, Clear Springs, Astin East, Barben, River Valley, PF Berry pilots; Wauchula, Sebring, Lake Placid, Okeechobee, Arcadia towns) and authorized hourly acquisition for cells without a series. Registry and cell index in `pipelines/weather/evaluation_sites.py`; server `config/evaluation_sites.json`, `config/hourly_index.json`, `state/evaluation.json`.
- Acquired five hourly series (Homerville, Valdosta, Folkston, Okeechobee, Arcadia; 140,256 rows each, pilot QC and checksums) through the existing checksummed path under the post-global 200 GiB/500 GiB limits. Transfer counter unchanged at 18,824,365,917 bytes: the cells lay inside 5×5-cell zarr chunks cached for the pilots. Ten panel sites reused stored cells. No global hourly, no daily re-download.
- `location_api.py` → `location-evidence-v3`: hourly resolved by MERRA-2 cell for any pin, with `hourly_source` provenance and a checksum refusal on tampering. Four new tests (cell keys against recorded pilot cells, shared-cell reuse, incomplete series excluded, tampered file refused); server suite 79 passing. API session restarted; unrelated yield jobs untouched.
- UI: 18 snapshots split per site with an index (`scripts/split_snapshots.py`), grouped presets, hourly-cell line in the availability strip. Chromium checks: Arcadia Evergreen → ruler declines, Wauchula "shared with River Valley · 8.2 km", Homerville Deciduous with flowering-freeze 8/15, live pin in Barben's cell gets the packet, live non-cell pin daily-only, no page errors, 390 px no overflow.
- Interpretation limits: town pins are city centres; one series per 0.5°×0.625° cell; assumption-based calendar, not validated phenology; no supervisor pre-registered labels yet. Hosted snapshot not redeployed.

## 2026-09-15 — Growing-cycle ruler and stage exposures

- Built a custom monochrome timeline in `dist/cycle.js`, integrated into `dist/app.js`, `index.html` and `style.css`. Six aligned lanes show winter chill, bud development, flowering, fruit development, harvest and whole-cycle context. The selected stage shows existing freeze, heat, rain, disease-weather, VPD, dry-spell, radiation or heat-unit values as applicable. Detailed tables remain expandable.
- Typical-cycle bars use median boundaries with labelled p10-start to p90-end timing spans. Individual winters show their own dates and exposures. Missing data stays unavailable, event frequency is not presented as crop-loss probability, and evergreen-majority results do not receive a new chill-triggered ruler. No scientific constants, calculations, snapshots or API changed.
- Browser verification: 135 flowering/fruit/harvest windows and exposure values matched the saved records across three sites and 45 winters; all 18 typical stage views checked. Keyboard activation, mouse lane selection, growing-setup note and four synthetic unavailable/incomplete states passed. No page errors during the main smoke sweep. Desktop and 390 px screenshots inspected; 320/390/768 px checks found no page overflow. The scale itself scrolls on narrow screens.
- Downloaded real Chromium HTML and JSON reports. JSON production content matched the original snapshot exactly and retained cycle-view metadata. Found and fixed cloned-select labels reverting to defaults in HTML; confirmed the downloaded report retained winter 2014, Harvest, and selected monthly/annual metric labels. Static HTML removes stage buttons and expands evidence tables. Both frontend scripts passed `node --check`; no new permanent tests or backend test run.
- Updated runbook and handover, removed temporary QA downloads. Local preview only; no hosted redeployment, server-code change, new acquisition or scientific validation. The supplied image was design guidance, not a published asset.

## 2026-09-12 — Open-field production core and three-site packet

- Reviewed the 2026-09-12 supervisor transcript against the adaptation plan and R source. Decision: implement the reviewed chill → forcing → offsets → stage-exposure chain in Python (`pipelines/weather/production.py`) instead of an R subprocess runner; constants live in versioned profiles (`legacy_paul_v1`, 100 h and bounded 0–7.2 °C variants).
- Fixed while porting: one season anchor for offsets and reconstructed dates; fixed typed row per winter with status and per-metric reasons; complete-window refusal for chill, forcing and every stage; suspect/out-of-range rain declines rain, dry-spell and disease metrics; zero requirement refused as `anchor_required`; no query-dependent reference scaling or weighted total.
- Both of Paul's classifiers (chill-only; multi-feature with winter-month Tmin/Tmean and freezing) reported from multi-year means, per-year counts and a two-thirds majority. Risks ranked by frequency of winters with an event under his thresholds, with Wilson 95% intervals; other exposures reported unranked.
- Generated `docs/weather/production/` for Waldo, Citra and Papanduva from existing archives. Waldo/Citra Deciduous majority, median flowering 20/26 Jan and harvest from 31 Mar/6 Apr; Papanduva Semi-evergreen, flowering 6 Aug, harvest from 15 Oct. Citra flips to Transitional under the bounded chill definition. Heavy-rain event saturates at 15/15 everywhere; intensity must be compared instead.
- Verification: 18 new tests, 73 server tests passing; exact parity with all 90 existing 50/100 h scenario records; Papanduva mean chill 199.4 h matches the reconciliation; HTML inspected in headless Chrome. No downloads, soil restart, R execution, deployment or cultivar modelling.
- Same day, UI integration: `location_api.py` now returns `production` (method `location-evidence-v2`), available for pilot coordinates with hourly data and explicitly unavailable elsewhere; `dist/` shows the three outputs as section `00` above the annual cards with per-winter, sensitivity and change lists. Snapshots regenerated; 75 server tests; presets, live-API pilot and non-pilot coordinates, setup note and mobile layout checked in headless Chrome. Hosted snapshot not redeployed.

## 2026-09-11 — Complete R source review

- Read all 5,759 private source lines sequentially, including superseded blocks and optional genotype processing; traced 332 expressions / 51 top-level functions. Added `docs/weather/R_FULL_CODE_REVIEW.md` with full inventory, output dependencies, code defects, scientific limitations and reuse gates.
- Confirmed single-reference-row suitability scoring, session-dependent analogue classification, incomplete-year schema/group splitting, undefined genotype metadata variable and positional master-answer lookup. Separated these from provisional calendar/system assumptions and uncalibrated relative scores. No original R edits or full workflow execution.
- Expanded `scripts/audit_paul_reference.R` to 22 passing local source-pinned checks (17 reviewed helpers plus syntax/scalar diagnostics); mismatched-source refusal verified. These characterize behavior, not corrected functionality or biological accuracy. Prior 55-test server suite not rerun; no package installation, download or deployment.
- Updated the handover/adaptation gates. Existing archives/UI preserved; next implementation remains the network-free R adapter and Waldo open-field calendar/risk packet. Raw source, transcripts, reports and breeding information remain unpublished.

## 2026-09-11 — Supervisor review and R adaptation plan

- Reviewed the latest supplied discussion; prioritize open field + ground production strategy, calendar and stage-specific risks, beginning at Waldo. Soil/tunnel scoring and genotype work remain later layers.
- Parsed the unchanged private 5,759-line R workflow (332 top-level expressions / 51 functions), audited the useful sections and mapped their actual weather inputs to existing archive fields. Identified two classifiers, provisional planting/phenology rules, missingness/score fallbacks and a northern summary-anchor shift of −31 days.
- Added `scripts/audit_paul_reference.R`; eight local characterization checks passed on synthetic inputs after source fingerprint verification. Only nine reviewed helper definitions evaluated; no workflow download/setup/report code executed. Prior 55 backend tests not rerun; no biological validation claimed.
- Added `docs/weather/R_ADAPTATION_PLAN.md` with modules, data contract, configuration, validation/acquisition/UI stages and acceptance gates. Updated requirements and existing plans to resolve priority/runtime conflicts. Production R modules and fixes remain next work; no acquisition or deployment this turn. Original R, transcripts and private reports remain unpublished.

## 2026-09-11 — First connected climate/soil UI

- Built the monochrome coordinate-first dashboard from the supplied style reference: six exposure cards, monthly/annual charts and table, soil uncertainty, four-system qualitative notes, provenance and HTML/JSON export controls.
- Published-source candidates contain three real derived snapshots only. Private loopback Python API and fixed local SSH proxy support new coordinates without acquisition; London returned daily data with chill/soil correctly unavailable. Hosted static mode supports the presets, not arbitrary-coordinate private-network access.
- All 55 server tests pass. The 225 shared annual values match the prior reports exactly. Desktop/mobile layout and primary controls checked; invalid input leaves no fabricated output. Export click had no console errors, but embedded-browser download event/file verification remains incomplete.
- Geographic negative control exposed the source's artificial “Null island” polygon. Excluded only the labelled placeholder, added checksum-backed fixture coverage including null labels, and regenerated summaries. Original mask/weather/soil bytes preserved.
- Added `docs/UI_RUNBOOK.md`; production connectivity, durable jobs/cache, finer availability states, stage overlays, export compatibility and scientific validation remain next-stage work. No new downloads or cultivar modelling. Deployment/publication is verified separately, not assumed by this entry.

## 2026-09-11 — Coordinate dashboard implementation design

- Added `docs/UI_IMPLEMENTATION_PLAN.md`: coordinate/system inputs, six exposure cards, historical evidence, soil context, conditional management comparison and consistent on-page/export report.
- Defined partial-result states, separate evidence/availability labels, durable jobs, versioned cache and private-server access boundary. Reuse existing Python science for the interim slice rather than the earlier unimplemented R-first architecture.
- Plan only: no frontend, API, deployment, download or new runtime tests. Existing 51-test result unchanged; cultivar work remains deferred.

## 2026-09-11 — Soil acquisition and consolidated catalog

- Verified server mount and completed global weather state; preserved existing data and unrelated server work.
- Implemented bounded WCS soil downloader for 630 property/depth/statistic subsets across 14 sites. Downloaded 157 records (Citra/Papanduva/Waldo 45 each; Astin East 22) before three source timeouts stopped acquisition. Remaining 473 records not completed; no duplicate weather workers or downloads.
- Readback/checksum audit passed all 157, with 52 ordered quantile pairs and no source no-data values. WCS output is geographic/reprojected; native-grid parity and field validation remain pending.
- Added catalog/inventory, soil audit and six unit tests. Full server suite 51 passing tests. Rasterio installed in project virtual environment only. Raw soil and weather stay on server.

## 2026-09-11 — Location × growing-system research plan

- Reviewed original architecture and used three parallel research reviews for six weather hazards, protected growing systems and soil/root-zone constraints.
- Added `docs/weather/LOCATION_MANAGEMENT_PLAN.md`: implementation sequence, evidence registry, conditional four-system output, targeted soil acquisition and validation gates.
- Separated direct fruit rain from root-zone water balance; no automatic tunnel freeze protection, pot drought immunity or field drainage inference from soil maps.
- Planning/documentation only: no downloads, runtime changes, new tests or calibrated management recommendations. Prior 45-test result unchanged.

## 2026-09-08 — Exploratory seasonal exposure scenarios

- Implemented and ran 50/100-hour Paul-derived UTC scenarios across three sites and 15 winters, with annual assumed flowering/harvest dates, cold exposure, harvest rainfall and production dry spells.
- Paired harvest rain differences: Citra +44.4 mm, Waldo +35.7 mm (15 winters), Papanduva −12.9 mm (13 winters). Papanduva 2015/2023 never reach 100 hours; no zero-risk substitution.
- Added seven tests; full server suite 45 passing tests. Existing archives only, no new downloads or calibrated cultivar claims.
- Delivered offline HTML/JSON in `docs/weather/climate_evidence/stage_scenarios.*`; broader core gates and independent scientific validation remain unfinished.

## 2026-09-08 — Paul method reconciliation

- Audited executable R definitions and local HTML narrative; original private/reference files remain unpublished.
- Identified below-only vs bounded chill, six- vs four-month seasons, LST vs UTC, crop-year labels, historical baseline and 50-hour configuration vs 100-hour narrative benchmark differences.
- Ran controlled sensitivity on three sites ×15 winters. Papanduva mean 178.9 →199.4 h under changed season/definition on identical UTC data; residual relative to reported 209.4 h remains unresolved.
- Added three known-answer tests; full server suite now 38 passing tests. No downloads, original-data changes, R execution or phenology calibration.
- Deliverable: `docs/weather/PAUL_RECONCILIATION.md` plus derived JSON and reproducible script.

## 2026-09-08 — Supervisor climate evidence report implemented

- Generated self-contained HTML and derived JSON for Papanduva, Citra and Waldo from existing daily/global and hourly/pilot archives. Added six charts, seasonal comparison, 15-year tables, coverage and station limitations.
- Tested complete-window chill (inclusive 0–7.2°C), missingness, cross-year/leap boundaries, dry spells and suspect rain refusal. Server suite: 35 passing tests.
- Reference-window chill medians: Papanduva 168 h, Citra 288 h, Waldo 348 h. These are descriptive estimates under documented UTC windows, not cultivar requirements. No new weather downloads or model fitting.
- Reviewed the opening HTML layout and charts in a Chrome screenshot. Final core audit and broader probes remain pending.

## 2026-09-08 — Supervisor demonstration priority

- User relayed supervisor guidance to complete the first part before requesting cultivar data for Part 3.
- Recorded the immediate deliverable as a reproducible climate evidence report using downloaded data, initially Papanduva versus Citra and Waldo. No cultivar rankings, calibrated phenology, or full application implied.
- This turn plans the demonstration only; no indicator implementation or new scientific tests were performed.

## 2026-09-08 — Continuity baseline

- Added `HANDOVER.md` and `AGENTS.md` to make project state and end-of-request publication expectations explicit.
- Prepared the existing weather pipeline, tests, plans and validation reports for version control; excluded bulk data, credentials, machine caches and supplied private/reference artifacts.
- Recorded the existing 29-test server result; no new weather acquisition or scientific validation performed in this documentation task.
- Core remains incomplete: indicator demonstrations, compressed-source failure tests and final audit outstanding.
