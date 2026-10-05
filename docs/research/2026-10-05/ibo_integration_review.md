# IBO reports and the weather app: collection, findings and integration decision

Reviewed 2026-10-05. The review itself was research and document acquisition only: no application code, model constants, benchmark expectations, saved assessments or weather archives changed, and the prior full review of the supplied 2026 report was reused. The regional evidence layer recommended below was built later the same day; see the implementation section.

## Decision

Build a versioned regional evidence layer first. Use it for source-cited context and historical event checks beside the existing weather results. Add retrieval-assisted question answering after the evidence records can be retrieved and verified reliably. Do not ask an LLM to replace the weather calculations, estimate crop loss from report prose, or choose a cultivar automatically.

The strongest new finding is that reported harvest shifts can come from management, not temperature. The 2025 report explicitly attributes Peru's delayed 2024 start to delayed pruning. Another useful finding is methodological: reports revise earlier numbers, change season labels and repeat text. A searchable pile of PDFs without those distinctions would produce plausible but wrong analytics.

The evidence layer is now implemented; see the next section. There is still no RAG service or calibrated crop model.

## Implementation (2026-10-05)

The first step of the decision is built. `dist/evidence/ibo-regional-v1.json` holds 91 records checked against the complete 2023, 2025 and 2026 reports: 39 events, 42 practice records and 10 constraints across 51 geographic scopes in 23 countries. Statements repeated across editions are extra citations on one record (172 citations in total), not extra events. A new Regional evidence tab shows the records for the pin's country and region next to the calculated risks, not mixed into them, with category filters and page citations. HTML and JSON exports keep every matched record.

Matching uses polygon IDs tied to the hash of the existing Natural Earth bundle instead of names. Testing showed why: by name, Washington, DC received the Pacific Northwest heat-dome record, because the reference labels both places "Washington". Browser checks covered all 71 presets, six live coordinates, failure and stale-lookup states and real exports; the weather payloads did not change. Details are in the [UI runbook](../../UI_RUNBOOK.md#regional-evidence). Question answering over the reports, report-derived model parameters and further downloads were not added.

## 1. What was acquired and read

Raw sources, extracted text and per-edition manifests are on the designated server under `data/reference/ibo_reports/`. Raw documents are not in Git. Public source URLs, checksums, access limits and review coverage are in [the inventory](ibo_report_inventory.json).

| Edition or data year | What we have | Reading and access limits |
|---|---|---|
| 2007 and 2008 | References confirming predecessors | Full reports not located. The 2010 report identifies the 2008 predecessor; IBO's 2017 announcement identifies the 2007 launch. |
| 2010, published 2011 | Complete 51-page USHBC precursor PDF from Oregon Blueberry Commission | Full text reviewed. This is not an IBO-branded annual edition. |
| 2012, published 2013 | Public Scribd HTML transcript saved | Narrative reviewed, but original PDF not acquired. Upload permission and completeness are unverified; the platform says 73 pages while headers say 76. Scrambled tables excluded from quantitative evidence. |
| 2014 data, published 2015 | Archived IBO product listing | Full study not acquired; historical member/paid access. |
| 2016 data, published 2017 | Complete 38-slide public GBC preview, preserved through Internet Archive | Text and extraction-empty slides inspected. Not the full annual report, which remains unavailable. |
| 2018 | Search record only | No distinct edition established. A 2018 industry write-up uses 2016 data. This is not proof that no edition existed. |
| 2019 | Publisher announcement and archived listings | Full 158-page report not acquired. Historical paid/member access; free preview requires checkout, not submitted. |
| 2020 | Original release announcement and archived app shell | Americas-only digital special edition. The original host fails TLS or returns 404; the archived Dash shell does not contain the report data. Not read as a complete report. |
| 2021 | Official/mirror listings and a rejected archived fragment | Full text unavailable. The mirror is now 404; the captured PDF stops at 1 MiB although its header declares about 33.8 MB. No readable full report. |
| 2022 | Complete 198-page PDF and text | Downloaded an archived public Berries ZA association copy. All extracted pages reviewed and selected substantive charts inspected. |
| 2023 | Complete 114-PDF-page report in two-page spreads | Archived Berries ZA copy. All extracted text reviewed in layout and raw order; selected charts inspected. PDF and printed page numbers differ. |
| 2024 | Seven public Italian Berry excerpts published with IBO | Abridged country/production articles, not the full report. No complete ungated PDF located. Full-report registration form not submitted. |
| 2025 | Complete 145-PDF-page report, 288 printed pages | Public FlippingBook viewer permits unauthenticated PDF download. Full substantive text and key image tables reviewed. Remaining sparse pages also inspected; printed p.22 contains a price chart, not just an advertisement. |
| 2026 | Existing supplied 294-page PDF, now preserved on server | Prior full review reused, with targeted cross-edition checks. Not counted as a new internet download. |

The complete annual IBO editions available for this synthesis are **2022, 2023, 2025 and 2026**. With the 2010 precursor, there are five complete reports totaling 802 physical PDF pages, plus the separate 38-slide preview. Some PDF pages hold two printed pages. These totals do not count partial documents as complete.

The search covered official IBO pages and releases, author/publisher material, public industry-association mirrors, indexed copies and Internet Archive captures. No membership was purchased, no access controls were bypassed and no personal details were submitted. Failure to locate a public copy does not establish that none exists. The most useful missing inputs are complete copies of 2021 and 2024.

### Reading coverage

Readers covered the country narratives, statistical tables, methods and forecasts in the complete reports. Relevant image tables and selected seasonal charts were inspected. This was not a digitization of every plotted point. Approximate chart readings were not promoted to exact numeric evidence. The 2012 transcript and 2024 excerpts remain separately labelled secondary/limited-access sources.

The 2016 preview's extraction-empty pages were inspected visually: pages 1-12 are membership material, pages 14 and 20 are maps/headings, and page 35 is a qualitative planting-growth map. The 2025 sparse-page check covered printed pages 14, 22, 30, 264, 270, 274 and 285. Publisher promotion, forecasts and observed production are kept separate.

## 2. Findings that matter for the app

Page numbers below are printed pages unless explicitly marked as PDF pages. Interpret narrative loss figures as reported industry estimates, not verified farm measurements.

### Management changes the calendar

- **Peru, 2024.** Growers delayed pruning to sell into shortages following El Nino, producing another delayed season start. The 2025 report states this directly on p.71, PDF p.36. A temperature-only model cannot explain a deliberate management delay. The managed-cycle scan should remain a feasible-weather scenario, not a prediction of the date growers will prune.
- **Colombia.** The 2022 edition describes two production peaks; the 2023 edition describes three; the 2025 edition gives November-December, May-June and September. Pruning is part of the explanation. Keep each edition's calendar and qualifiers rather than forcing one permanent country calendar. Sources: 2022 pp.42-43; 2023 PDF p.26; 2025 p.57.
- **Protection and species matter.** Mexico reports 80% under structure in 2025, p.117. In China, greenhouse spring production and open-field summer production have different windows, 2025 p.144. Chile's low-chill production and higher-chill southern production are distinguished, 2025 p.77. Country-level proportions do not tell us the system at an arbitrary pin.

**App use:** show reported regional practice beside the modeled scenario. Ask for the actual cultivar group, protection and pruning date when a field prediction is required. Do not automatically replace an unknown field's management with its country's dominant system.

### Reported damage creates useful event cases

| Event | Report evidence | Useful model check | Limit |
|---|---|---|---|
| Georgia and North Carolina freeze, night of 12 March / 13 March 2022 | 2023 PDF p.45, printed pp.88-89. Georgia reportedly lost almost half its crop; NC reportedly lost 15 million lb in one windborne freeze. | Does the stored weather show freezing, and which modeled stage contains it? | State-level narrative and industry estimates, not field losses at our pins. |
| British Columbia heat dome, 25-29 June 2021 | 2022 pp.76-78. Different damage to ripening and green fruit across cultivars; November flooding also documented. | Heat exposure during the reported crop stage, separately from later flood damage. | No province-wide dose-response; no BC benchmark site currently. |
| Chile frost and hail, November 2022, then December heat | 2023 PDF pp.33-34, printed pp.64-67. Association summary gives November; narrative locates damage between Linares and Chillan. | Freeze versus hail and later accelerated ripening must be separate mechanisms. | Production decline also includes cultivar removal and crop switching. |
| Waikato frost, October 2022; NZ floods and cyclone, early 2023 | 2023 PDF p.67, printed p.132. Rabbiteye particularly affected; surveys describe severe losses across the compound season. | Check freeze exposure without assigning all later loss to that event. | Our default is low-chill SHB, not the reported rabbiteye crop. |
| Poland May 2024 frost after an early season | 2025 pp.207-208. Green fruit affected; losses reported as about 20% on established farms and over 50% locally. | Does a cultivar-appropriate stage calendar expose green fruit during the event? | Estimates and protection effects vary; not a universal temperature-to-loss curve. |
| Peru El Nino 2023 | 2025 pp.54, 71-72 and 2026 p.81; 2024 material available only as excerpts. | Investigate heat effects on floral induction and cultivar response, not only fruit heat. | No transferable initiation-failure threshold or farm training set supplied. |
| Zimbabwe 2024 compressed season | 2025 p.241 attributes timing to a mild winter and a later cold snap concentrating induction. | Identify initiation and management assumptions missing from the scan. | Causal interpretation from industry narrative, not an experiment. |

Reports also identify water access, irrigation restrictions, salinity treatment, soil conditions, labor and transport constraints. Examples include Agadir desalination, Serbia water treatment and Romania's high-pH clay soils in the 2025 regional chapters. These are useful feasibility warnings. Rainfall alone cannot establish whether a farm has irrigation water or suitable water chemistry.

The reports do not supply planting dates for arbitrary land points. Harvest calendars, pruning dates and nursery establishment windows are different fields.

### Yield and market numbers provide context, not farm loss labels

Annual volume changes combine bearing area, orchard age, cultivar turnover, protection, labor, weather, grading and market decisions. Exports additionally depend on transport, domestic consumption and re-exports. Country production divided by estimated bearing area is an industry yield ratio, not a field measurement.

The 2025 report says some unverified cells are filled by regression, pp.277-278. Its forecasts project area and yield rather than simulating weather injury, pp.281-283. The later 2026 edition explicitly adds a Peru El Nino judgment, p.288. Forecast methods therefore need edition-specific provenance too.

**App use:** a separate historical regional production and supply view, with fresh/processed, export/production, currency and price basis shown explicitly. Do not turn a national decline into a local crop-loss probability, or border-crossing prices into farm profit. Market ranking would require a separate user objective and economic inputs.

## 3. Why raw RAG would be unsafe

### Year labels and document layout are unreliable without metadata

The 2010 precursor's cover says 2010 and publication February 2011, but later running headers say 2008. Its Southern Hemisphere default is 2009/10. The 2016 preview labels 2015/16 as 2016, PDF p.21. Modern reports use the season's starting year when comparing split seasons, such as 2022/23 labelled 2022. Publication year, crop season and event date must be separate.

The 2023 report is a spread PDF; PDF p.45 contains printed pp.88-89. Its foreword retains a 2022 label. The 2025 back cover says 2024. An LLM matching the closest header could attach a valid statement to the wrong year or page.

### Later editions revise the same historical observation

These are changes in reported values, not biological changes in the past:

| Observation | 2022 edition | 2023 edition | Source |
|---|---:|---:|---|
| Global cultivated production, 2021 | 1,789.59 thousand tonnes | 1,769.53 thousand tonnes | 2022 p.23; 2023 PDF p.15, printed p.29 |
| Mexico production, 2021/22 | 84.70 thousand tonnes | 74.20 thousand tonnes | Country tables, 2022 p.84; 2023 PDF p.51 |
| Georgia US planted area, 2021 | 9,712 ha | 7,810 ha | US state tables, 2022 and 2023 editions |

The global revision is -20,060 tonnes, about -1.12%. Mexico changes by -10,500 tonnes, about -12.40%. The global values and arithmetic were checked directly during this review. Preserve all vintages and choose one explicitly for an analysis; never append each report's latest column into a supposedly consistent historical series.

There are also within-edition disagreements. The 2022 global acreage table on p.22 associates production values with different regional rows than the production table on p.23. The 2025 report has different totals in its main production table and forecast-error section. Store the exact table/page and a discrepancy flag. Do not silently choose a value, average disagreements or label all cells observed.

### Repeated sources are not independent validation

The existing 53-site benchmark already cites IBO-related material for Mengzi and an IBO 2024 excerpt for Zimbabwe. Later IBO editions share authors, contributor networks and sometimes identical prose. Ten mentions of the same event are not ten observations. A missing mention is not evidence that no damage occurred.

This prevents using report-mention counts as the denominator for the app's 50% recurrence rule. It also prevents testing the benchmark against a source from which its expected answer was already derived.

### Rights differ by source and edition

Explicit broad reuse with attribution was located in the 2023 report, printed p.223; 2025, p.280; and 2026, p.285. Credit the source named in each item, such as IBO or Agronometrics and IBO. Equivalent permission was not established for the older material, 2022 or unavailable 2024 full text. Free reading does not by itself establish redistribution rights. The Scribd transcript and Italian Berry excerpts require their own source/rights review before inclusion in a public retrieval corpus. Original files remain private on the server.

## 4. Read-only comparison actually run

Newly read cases were checked against the existing NASA POWER daily archive and the already saved `stage_thermal_v3` seasons. No service startup, downloads, recalibration or source changes were needed. Complete coordinates, source-cell displacement, windows and outputs are in [ibo_event_checks.json](ibo_event_checks.json).

| Sample cell | Reported window checked | Stored daily Tmin | Existing model context |
|---|---|---:|---|
| Alma, Georgia | 12-13 March 2022 UTC | -3.12 C on 13 March | Modeled fruit development; one fruit-frost day that season |
| Homerville, Georgia | Same window | -2.53 C on 13 March | Modeled fruit development; one fruit-frost day |
| Elizabethtown, North Carolina | Same window | -5.47 C on 13 March | Modeled flowering; two flowering-freeze days in the season |
| Burgaw, North Carolina | Same window | -5.24 C on 13 March | Modeled flowering; four flowering-freeze days in the season |
| Linares, Chile | November 2022 | Monthly minimum +7.59 C | No modeled flowering/fruit freeze |
| Chillan, Chile | November 2022 | Monthly minimum +7.66 C | No modeled flowering/fruit freeze |
| Ohaupo, Waikato | October 2022 | Monthly minimum +5.15 C | Modeled flowering; no flowering freeze |

The four US cells agree with a freeze episode. They are not four independent events. The two Chile cells and the NZ cell do not reproduce the reported regional freezing. Those discrepancies require station, exact-location, date and crop-system checks. They are not proof that the reports or the model are wrong. In NZ, the narrative especially concerns rabbiteye, while the app uses a low-chill SHB scenario.

This demonstrates a useful workflow: reports identify cases worth investigating; stored weather tests a specific part of the claim. It does not establish detection accuracy, loss accuracy or future forecast skill. No application test suite was run for this research request.

## 5. Proposed integration

### First deliverable: regional evidence beside existing results

Keep the existing numerical weather response intact. Add a separate, versioned evidence view with:

- Reported production systems, species and protection, retaining region and season.
- Reported commercial harvest months, separate from modeled dates and export months.
- A dated timeline of reported weather impacts.
- Water, soil, labor and logistics constraints that are not inferred from the weather grid.
- Source edition, PDF and printed page, original attribution and evidence status.

A Peru pin should show the computed weather scenario beside the report's pruning and irrigation context. A NC pin can show the reported 2022 freeze alongside the model's exposure. Neither result should imply that a report described that exact farm. For an unrepresented region, say that no applicable regional evidence was found.

This also addresses the user's concern about missing data: an evidence panel can remain readable when hourly data are unavailable, but it must not disguise a missing calendar as a successful forecast.

### Record design

Use separate document, claim and event records. One claim can occur in several editions; one event can affect several regions or cultivars. The record needs:

| Field group | Required distinctions |
|---|---|
| Document | Stable ID, title, edition, publication/revision date, PDF SHA256, public URL, acquisition status, license |
| Locator | PDF page, printed page, section/table, extraction method, optional short supporting excerpt |
| Geography | Country plus region identifiers, spatial precision, location text as stated; Georgia US is not Georgia the country |
| Time | Observation period/crop season, event date precision, publication date, forecast target period when relevant |
| Crop and management | SHB/NHB/rabbiteye/wild, cultivar if named, open field/tunnel/greenhouse/net, pruning or treatment context; unknown remains unknown |
| Quantity | Original value and unit, fresh/processed/total, planted/bearing/certified area, production/export/arrival/price basis; normalized value only by deterministic conversion |
| Evidence | Association report, interview estimate, chart approximation, secondary excerpt, forecast or derived calculation |
| Review | Source lineage, duplicate/event ID, conflicts, corroborating source, reviewer status, allowed use |

A real first record would be Peru's reported deliberate pruning delay in 2024, cited to IBO 2025 printed p.71 / PDF p.36. It belongs to a management-timing claim, not a measured temperature response. The March 2022 US freeze described in the 2023 report can be a region-level event record with a local-night date, not four copies created from our four benchmark pins.

Retain source units such as pounds/acres or thousand tonnes before conversion. Keep complete original tables privately for audit. Do not use the model's own dates to invent a missing observed stage.

### How it fits the present files

These are proposed integration points, not changes made in this request:

- `pipelines/weather/location_api.py:analyze` already separates `production`, `planting`, provenance and raw weather summaries. A future regional-evidence field or separately versioned endpoint should remain independent of `production_block` and its calculations. Report-library failure must not prevent a weather analysis.
- `dist/places.js` already resolves country/region context for display. Reuse an explicit geographic crosswalk for evidence retrieval, with resolution warnings. Do not promote a nearby city label into a field observation or infer cultivar from geography.
- `dist/app.js:renderOverview` and Methods & data are natural places for a regional-evidence panel. Keep modeled scenario, reported regional practice and future forecasts visually separate. HTML/JSON exports should retain evidence IDs and source-library version.
- `pipelines/weather/benchmark.py:assess` currently compares literature month sets with model windows. Keep that benchmark intact until independently reviewed observed-calendar records justify a change. Build an event-comparison dataset separately and track source overlap.
- `pipelines/weather/production.py` should not consume report prose or generated coefficients. Any new induction, species or protection model requires primary physiological/field evidence, an explicit model revision and held-out site/year checks.

### RAG and the LLM's role

Start with ordinary structured storage and full-text search, for example SQLite and FTS5. Filter by geography, crop type, event/season and evidence status before ranking text. At this collection size a separate vector-database service is not the first dependency. Add embeddings and reranking only if a held-out retrieval comparison shows better answers to real breeder questions.

Use the LLM offline to propose structured extractions, then review them. Online, let it explain retrieved evidence and already-computed weather results. Numerical totals, unit conversions, trend comparisons and date overlaps belong in deterministic code or database queries. The answer should cite both the report edition/page and the weather analysis version when it combines them.

Suggested flow:

1. Versioned source files and permission records on the server.
2. Layout-aware extraction preserving tables, spread sides and page identifiers.
3. Proposed claims with human review, conflict handling and deduplication.
4. Structured regional search plus optional semantic retrieval.
5. Cited answer from retrieved claims and read-only weather-result JSON.

Do not fine-tune an LLM on these reports as the first investment. Fine-tuning does not solve table revisions, stale seasons or citation accuracy. Do not let source text act as instructions, grant tool access or write to the weather model. Keep private breeding material out of third-party services without institutional approval.

### Questions the integration should answer, and decline

| Question | Required behavior |
|---|---|
| Why might Peru's 2024 harvest differ from the climate-only scan? | Retrieve the pruning decision and label management as an omitted input; do not invent a revised date. |
| What happened in NC in March 2022? | Cite the report's local-night event, show the sampled weather separately, and distinguish reported losses from calculated exposure. |
| What was Mexico's 2021/22 production? | Ask for or state the chosen edition; expose 84.70 versus 74.20 thousand tonnes instead of silently mixing them. |
| Do reports prove a universal heat threshold for failed flower induction? | No. Retrieve the cases and state the missing experimental/field parameter evidence. |
| Does the report show that my field uses tunnels? | No, unless the exact field is documented. Country share is not field identity. |
| Does no report mention mean no frost happened? | No. Missing reporting is not a negative event label. |
| How profitable will this pin be next season? | Decline a precise estimate without costs, management, cultivar, market objective and current-season inputs. |
| Can the library fill missing hourly temperatures? | No. It can show regional context, not manufacture weather or a crop calendar. |

Before release, evaluate retrieval on a breeder-reviewed question set with held-out years and source families. Check geographic disambiguation, source/page support, original units, observation-versus-forecast classification, conflict visibility and correct abstention. These are proposed acceptance checks; no RAG quality score was measured in this task.

## 6. Implementation order and remaining prerequisites

1. Complete source/rights review and recover the 2021 and 2024 full reports if the user can supply them or complete IBO's legitimate access process. This need not block a clearly bounded library from the verified complete sources.
2. Curate regional claims and dated events, starting with the existing benchmark regions. Publish the evidence view before a chat interface. Keep the old benchmark and numerical model unchanged during this step.
3. Investigate the regional freeze discrepancies with exact locations and suitable station or field observations. Register evaluation cases before tuning anything.
4. Add a citation-first question interface when retrieval and evidence records meet the checks above.
5. Consider cultivar/management model changes only after the corresponding field data and scientific review exist.

No new vector service, LLM API subscription, crop model, weather acquisition or hosted deployment was installed. The missing older reports are access gaps, not permission to synthesize their contents.

## Sources and reproducible artifacts

- [Machine-readable source inventory, checksums and acquisition gaps](ibo_report_inventory.json)
- [Seven read-only event comparisons](ibo_event_checks.json)
- [IBO current archive](https://www.internationalblueberry.org/global-satet-of-the-blueberry-industry-report/)
- [2010 USHBC precursor PDF](https://www.oregonblueberry.com/update/USHBC-report.pdf)
- [2016 report release](https://www.internationalblueberry.org/2017/05/03/2016-global-blueberry-statistics-and-intelligence-report-is-now-available-at-the-ibos-library/)
- [2019 author/publisher announcement](https://stories.agronometrics.com/agronometrics-co-authors-ibo-2019-state-of-the-global-blueberry-industry-report/)
- [2020 Americas special-edition announcement](https://www.internationalblueberry.org/2020/11/24/agronometrics-in-charts-ibo-releases-the-blueberry-data-for-the-americas/)
- [2022 complete archived association copy](https://web.archive.org/web/20240714175843id_/https://www.berriesza.co.za/wp-content/uploads/2022/11/IBO-2022.pdf)
- [2023 complete archived association copy](https://web.archive.org/web/20240807150457id_/https://www.berriesza.co.za/wp-content/uploads/2023/08/Global-State-IBO2023.pdf)
- [2024 abridged excerpt index, not the full report](https://italianberry.it/tag/ibo-report-2024)
- [2025 public viewer and download](https://online.flippingbook.com/view/768531494/)
- [2026 official landing page, supplied PDF reviewed previously](https://www.internationalblueberry.org/report-2026/)
- [Existing 43-source phenology review](../../weather/GLOBAL_PHENOLOGY_REVIEW.md)
- [Current production methods](../../weather/production/README.md)

Attribution: International Blueberry Organization, Agronometrics and the country associations identified in the individual reports. Precursor attribution: Cort Brazelton and USHBC/NABC. Secondary excerpts: Italian Berry. Analysis and integration recommendations here are this project's conclusions, not IBO endorsements.
