# Map-first climate workspace

Design revision: 2026-09-22. This replaces the original coordinate-form specification with the map-first redesign requested by the user. The implementation stays in the existing vanilla-JavaScript frontend; a framework migration does not improve the current user journey. Verification and operating instructions belong in [UI_RUNBOOK.md](UI_RUNBOOK.md).

## Product boundary

Help a user choose a location, understand its historical weather evidence, inspect susceptible crop stages and save a reproducible report. This is not a forecast, orchard-suitability verdict or cultivar recommendation.

Global acquisition and global analysis availability are different. The daily archive can answer supported land-point queries through the connected private API. The land-hourly cache is complete, but the API currently exposes 19 indexed hourly cells. Selecting any point on a map must not imply an applicable crop calendar, available soil or regional planting guidance. The broader adapter and service roadmap remain in [FUTURE_PLAN.md](FUTURE_PLAN.md).

## User journey

1. **Choose a place.** Click or drag a map pin, enter numeric coordinates, or filter the 18 saved locations by name, region or county. The search is explicitly a saved-location filter, not global address geocoding. Keyboard users can enter coordinates, select a saved button, or pan the map and select its center.
2. **Request an analysis.** Map movement never invokes the archive. Analyze is explicit. Distinguish the draft pin from the committed result; a changed pin leaves the previous location's name and coordinates on its assessment with a visible notice.
3. **Read what is available.** Show daily rows, hourly access, applicable calendar, planting-guide availability and soil records separately. Connection status concerns service access, not scientific validity. Missing information never receives a low-risk colour or zero value.
4. **Understand the main evidence.** The overview shows the production-system hypothesis, assumed harvest window, qualifying recurring risks and descriptive signals. No blended suitability score or invented severity categories.
5. **Inspect the season.** Choose a winter and stage. Read its modelled dates, exposure values, historical comparison and missing-data reasons. Keep hourly warm-midwinter context independent of crop timing.
6. **Check context and assumptions.** Climate history, soil/setup and methods/data have their own views. Detailed tables and scientific definitions remain accessible without dominating the initial screen.
7. **Save the same result.** HTML includes all views and expanded definitions, not only the active tab. JSON retains the original analysis with management and selected winter/stage metadata. Neither export recalculates science.

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

Use a warm-white background, dark green text, teal navigation and restrained amber recurrence accents. Stage colours identify categories only. All meaning also appears in words, units and counts. System fonts avoid an external font service. Values use tabular numerals.

Desktop places the location controls alongside the map. The assessment starts below with its identity, setup and evidence coverage. Mobile stacks the controls and map, then the assessment. Tables and the timeline scroll within labelled regions rather than widening the page. Interactive targets are at least 44 px where practical; focus rings, semantic headings, reduced-motion support and a coordinate-entry skip link are part of the design.

Loading states describe the actual request, without invented processing stages or percentages. Cancel aborts the browser request and invalidates stale responses; it does not claim to cancel server computation. A server already calculating may remain busy until that request finishes. Selecting another draft pin also invalidates the earlier browser response. Errors retain the previous clearly identified assessment, never substitute a nearby site.

## Map, privacy and resilience

Leaflet 1.9.4 is vendored with its license. Standard OpenStreetMap raster tiles supply geography, not weather or a risk heatmap. Attribution remains visible. Only ordinary viewport tiles load; no prefetch, bulk download or offline tile cache. See [OSM tile policy](https://operations.osmfoundation.org/policies/tiles/).

Tile requests expose the browser IP, page origin and viewed map area to OpenStreetMap. The interface states this. Saved-location filtering is local; there is no third-party geocoder, location permission, paid key or telemetry. If tiles or the map library fail, coordinates and saved analyses remain usable. A private-API outage leaves saved snapshots usable.

The selected pin is distinct from the dashed hourly source-cell rectangle. The rectangle uses the response's source coordinates and native 0.5° by 0.625° cell, not an invented coverage layer or parcel footprint. Changing the pin removes the previous cell evidence until a matching result is returned.

## Verification contract

Exercise all saved locations and views; compare displayed metric values with the unchanged analysis payload. Include zero and missing values, recurrence ties, unranked and evergreen cases, selected winter/stage retention, keyboard navigation, supported and daily-only land pins, offshore refusal, disconnected and delayed responses, and map failures. Inspect desktop and mobile; check narrow-width overflow. Download actual HTML/JSON, open the HTML independently and check all views, expanded definitions and retained selections. Software consistency does not establish scientific validity.

## What this revision does not deploy

No new archive acquisition, any-cell hourly adapter, weather interpolation, geocoding service, authenticated team gateway, durable jobs/cache, management calibration or cultivar model. The current private API and local preview remain the runtime. GitHub publication does not redeploy the existing hosted Sites application. Future service architecture needs its own implementation and authorization; this design does not claim those components exist.
