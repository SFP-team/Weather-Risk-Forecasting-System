# Map-first climate workspace

Design revision: 2026-09-23. The map now uses MapLibre with an English-first OpenFreeMap style and browser-local place context. The assessment remains vanilla JavaScript; the weather and planting contracts are unchanged. Verification and operating instructions belong in [UI_RUNBOOK.md](UI_RUNBOOK.md).

## Product boundary

Help a user choose a location, understand its historical weather evidence, inspect susceptible crop stages and save a reproducible report. This is not a forecast, orchard-suitability verdict or cultivar recommendation.

The connected private API reads daily weather and complete hourly series for supported land points from the existing archives. The hourly adapter verifies cached source objects without network fallback; the 19 previously indexed cells retain their normalized series. Selecting a point still does not imply an applicable crop calendar, available soil or regional planting guidance. Missing/corrupt installed hourly objects fail closed. The remaining service roadmap is in [FUTURE_PLAN.md](FUTURE_PLAN.md).

## User journey

1. **Choose a place.** Search by settlement name, region or country in the local reference, or choose a saved research site. Case/accent-insensitive results include geographic context and support arrows, Enter and Escape. A settlement selects its reference coordinates. A region or country frames its principal polygon and requires a specific map point or coordinates before Analyze is enabled. This is not a worldwide street-address service; many smaller settlements are absent. Saved sites remain a separate search group and browse list.
   A local Natural Earth lookup supplies the containing country/region and nearest represented settlement. Show `Near NAME` within 100 km on represented land; otherwise use the containing area or coordinates. Saved farm names remain primary. Names do not move the pin or assign scientific/planting metadata.
2. **Request an analysis.** Map movement never invokes the archive. Analyze is explicit. Distinguish the draft pin from the committed result; a changed pin leaves the previous location's name and coordinates on its assessment with a visible notice.
3. **Read what is available.** Show daily rows, hourly access, applicable calendar, planting-guide availability and soil records separately. Connection status concerns service access, not scientific validity. Missing information never receives a low-risk colour or zero value.
4. **Understand the main evidence.** The overview shows the production-system hypothesis, assumed harvest window, qualifying recurring risks and descriptive signals. No blended suitability score or invented severity categories.
5. **Inspect the season.** Choose a winter and stage. Read its modelled dates, exposure values, historical comparison and missing-data reasons. Keep hourly warm-midwinter context independent of crop timing.
6. **Check context and assumptions.** Climate history, soil/setup and methods/data have their own views. Detailed tables and scientific definitions remain accessible without dominating the initial screen.
7. **Save the same result.** HTML includes all views, place-name context and expanded definitions. JSON retains the unchanged original analysis plus separate `location_context`, management and winter/stage metadata. Pending name lookup exports keep coordinates and explicitly mark names pending. Neither export recalculates science.

## Information architecture

| View | First screen | Detail layer |
|---|---|---|
| Explore | Global map, saved-location filter, coordinates, explicit Analyze | Basemap attribution, input help, source-cell overlay and archive scope |
| Overview | System hypothesis, assumed harvest, risk count; recurrence cards with k/n; four exposure families; one establishment window | Event definitions, Wilson intervals, sources and excluded-assessment reasons |
| Season & exposures | Winter selector, categorical stage colours, full-width timeline, selected-stage metric cards | Exact values, historical distribution, coverage, eligibility, full calendar and per-winter tables |
| Climate history | Six annual/reference-winter cards and two selectable charts | Annual values and definitions; no confusion with crop-stage windows |
| Soil & setup | Acquired records with property/depth uncertainty and selected setup notes | Missing soil, geographic-grid limitations, pot substrate and irrigation requirements |
| Methods & data | Interpretation limits, source resolution, daily/hourly/soil coverage and all assessments | Analysis ID, method versions, source hashes, quality flags and provenance |

The five assessment views use one tab panel at a time. Tab, arrow keys, Home and End operate the tabs. Stage selection uses native buttons. Details/summary controls provide progressive disclosure without a second data model.

## Metric presentation rules

- Recurrence cards show the backend rank, frequency, event winters / valid winters, total winters and uncertainty. Thresholds remain at least 50% recurrence and 12 assessable winters. Ties remain ties. Recurrence is not severity or probability of loss.
- Disease weather stays one ranked family. Flowering, fruit-development and harvest components remain available in stage details.
- Pollination cold-or-wet days, warm-midwinter hours and dry-run lengths are descriptive signals, not assigned loss-event thresholds. The separate cold-and-dry hypothesis remains in the full flowering view.
- Fruit frost retains its units, stage window and exposure-not-injury caveat. Zero stays distinct from unavailable.
- Daily-only warm context says **days**, never estimated hours. Hourly windows cannot be synthesized from that fallback.
- The new primary production-window timeline starts at budbreak, matching its existing backend dry-spell/radiation/GDD window. Legacy profiles retain their season-start interval. This is a presentation correction, not a formula change.
- Establishment is separate from the bearing-plant timeline. Display the source's regional precision and nursery assumptions. Unsupported geography declines; sharing a weather cell does not assign a planting region.
- Evergreen and unclassified results do not get an applicable chill-triggered crop timeline. Hypothetical calculated exposures are explicitly labelled. Independent winter weather remains useful.

## Visual and interaction system

Use the supplied Blueberry Breeding Lab logo and gallery reference: white canvas, #f5f5f7 section surfaces, #1d1d1f text, #0066cc links and compact #0071e3 primary actions. Center the 80px/600 desktop heading with responsive smaller type. Map and feature cards use 28px corners without gradients or cast shadows; inputs/actions are pill-shaped. System fonts avoid external font services. Scientific stage colours remain categorical, values retain units and tabular numerals, and tables scroll within their sections. The map takes the visual role of product imagery; no unrelated device or shopping elements are added.

Desktop places location controls alongside the map; compact screens stack them. Heading, gutters and map height adapt to both width and height, with a shorter landscape header and bounded content on large displays. Search lists use viewport-relative height. Narrow coordinate/action/stage controls stack. Form text stays at least 16 px; focusable chart/table/timeline regions scroll locally rather than widening the page or shrinking labels. Safe-area insets protect content and the viewport permits browser zoom. Map canvas sizing follows its container through ResizeObserver. Touch targets remain at least 44 px, with focus rings, semantic headings, reduced-motion support and a coordinate-entry skip link.

Loading states describe the actual request, without invented processing stages or percentages. Cancel aborts the browser request and invalidates stale responses; it does not claim to cancel server computation. A server already calculating may remain busy until that request finishes. Selecting another draft pin also invalidates the earlier browser response. Errors retain the previous clearly identified assessment, never substitute a nearby site.

## Map, privacy and resilience

MapLibre GL JS 5.24.0 is vendored with its license. A locally adapted OpenFreeMap Positron vector style supplies geographic context, not weather risk. Labels prefer English, then romanized names; local names remain only when those are absent. Country/region borders are clearer and incidental labels quieter. Attribution stays visible. Ordinary viewport tiles, fonts and sprites load from OpenFreeMap; no bulk tile download.

OpenFreeMap and its CDN receive IP and viewed map area; see its [privacy policy](https://openfreemap.org/privacy/). No paid key or external geocoder is used. Place naming loads a single 2.97 MB compressed public Natural Earth reference bundle, then uses coordinates only in browser memory. Coverage is 258 countries/territories, 4,596 administrative areas and 7,295 represented settlements. Boundaries are generalized and may be inaccurate near coasts/borders; this is not street addressing or a legal jurisdiction service. The flat map stops at Mercator latitude limits without altering supplied coordinates. WebGL, tile or naming failure retains coordinate entry and saved reports.

The selected pin is distinct from the dashed hourly source-cell rectangle. The rectangle uses the response's source coordinates and native 0.5° by 0.625° cell, not an invented coverage layer or parcel footprint. Changing the pin removes the previous cell evidence until a matching result is returned.

## Verification contract

Exercise all saved locations and views; compare displayed metric values with the unchanged analysis payload. Include zero and missing values, recurrence ties, unranked and evergreen cases, selected winter/stage retention, keyboard navigation, supported and daily-only land pins, offshore refusal, disconnected and delayed responses, and map failures. Inspect desktop and mobile; check narrow-width overflow. Download actual HTML/JSON, open the HTML independently and check all views, expanded definitions and retained selections. Software consistency does not establish scientific validity.

## What this revision does not deploy

No new weather acquisition, weather interpolation, external geocoding service, authenticated team gateway, durable jobs/cache, management calibration or cultivar model. The existing private API and local preview remain the runtime. GitHub publication does not redeploy the hosted Sites application.
