# Critical review: Astra's IBO report collection and the regional evidence layer

Reviewed 2026-10-11. Scope: the IBO collection and integration review of 2026-10-05 (`docs/research/2026-10-05/`), the 91-record registry `dist/evidence/ibo-regional-v1.json`, its client code (`dist/evidence.js`, the regional functions in `dist/app.js`, the polygon lookup in `dist/places.js`) and the Regional evidence section of `docs/UI_RUNBOOK.md`. Research only. No repository file other than this one was written. The lab server was used read-only (cat, grep, sha256sum and read-only Python).

## 1. Summary

Astra's collection work is careful and mostly honest about its limits. The registry is accurate at the level of paraphrase. The weak parts are the event-check method, the record design (it does not yet follow the review's own design) and some geography choices.

Top findings:

1. **The registry is faithful to its sources.** I checked 53 of 91 records against the extracted text of the cited pages, spread over 21 countries, all three record kinds and all three editions. 47 are supported, 5 are partly supported, 1 has a page mismatch, and none is unsupported. An automated sweep of every number in all 91 summaries found only one number missing from its cited pages (the South Africa "north about 40%" figure, which is on 2025 p.253, not on the cited pp.239 and 255). PDF hashes on the server match the inventory and the registry.
2. **The Chile event check used the wrong window.** It compared 1 to 30 November 2022. The frost was on the nights of 31 October and 1 November 2022, centred on Coihueco (Ñuble) ([El Tipógrafo relaying ASOEX and iQonsulting](https://eltipografo.cl/2022/11/arandanos-lluvia-y-granizo-de-noviembre-tuvo-minimo-efecto-sobre-la-produccion); [Portal Frutícola](https://www.portalfruticola.com/noticias/2022/11/09/chilecomo-se-han-afectado-los-arandanos-de-nuble-por-las-heladas/)). In the stored NASA POWER archive the coldest days of that cold spell are 30 and 31 October UTC. So the window left out the coldest grid days. On 30 October UTC the Chillán cell (which contains Coihueco) reached +2.24 °C and the Andean cell next to it reached -6.15 °C. In the window Astra used, the minimum was +7.66 °C.
3. **The Waikato check picked a coastal cell on a boundary.** Ohaupo is 28.2 km from the chosen cell centre (-38.0, 175.0) and 29.2 km from the inland cell (-38.0, 175.625). On the frost night, the UTC day of 6 October 2022 (dawn on 7 October local time), the chosen cell had +5.15 °C and the inland cell had +0.06 °C. Orchards reported -5 °C on 7 October ([Te Awamutu News, citing Blueberries New Zealand](https://www.teawamutunews.nz/2022/10/how-tunnel-vision-paid-off/)). Daily grid Tmin catches the timing of these cold outbreaks but misses their size by 5 to 10 °C. That is expected behaviour of a 55 km grid, not a location puzzle.
4. **The registry does not follow the review's own record design.** It has no separate claim records, no structured quantities, no edition revision handling, no reviewer or date per record and no allowed-use field. Each `event_id` is unique (39 of 39), so the UI's "same event in other records" grouping never runs. Numbers such as "15 million lb" or "20-30% of acreage" exist only inside prose.
5. **Region matching is safe but brittle and partly out of date.** Hash binding prevents silent wrong matches, which is good. But the region IDs are array positions in one bundle, and country matching still uses names. Natural Earth uses pre-2015 Moroccan regions and the pre-2013 Namibian "Kavango". A test pin at Kenitra (Gharb) gets no northern Morocco records. A pin at Curicó gets the "Linares to Chillán" frost. When a record is tagged with both a region and its country (for example the Chile frost), a Santiago pin shows it labelled only as "Chile, country context". The original "Linares to Chillán" scope label disappears.
6. **Inventory gaps are small but real.** I found no legitimate public full copy of IBO 2021 or 2024. Both official pages now show a free lead form (name, company, job title, email, phone, sector, country). Not in Astra's inventory: 15 IBO Summit 2025 presentations and 11 Morocco Berry Conference 2025 presentations hosted by IBO, a 2023 Brazelton and Fain summit deck, and third-party Scribd uploads of the 2024 and 2025 reports (marked "All Rights Reserved", so not usable).

## 2. Method and limits

- Text source: the server's `pdftotext -layout` outputs (`2023/report.txt`, `2025/report_pages.txt` split by printed page, `2026/report.txt`), copied read-only to a temporary folder outside the repository. 2023 and 2025 are two-page spreads. I rebuilt reading order with a column splitter and checked the page arithmetic: for every citation, printed page = 2k-2 or 2k-1 for PDF page k in 2023 and 2025, and printed = PDF page in 2026. All 172 citations pass that check.
- I did not render page images. Image-only tables and charts were not checked. On spreads, the text layer cannot always show which half a sentence sits on. Printed-page assignments inside a spread are therefore confirmed at the spread level only.
- Grid values in Section 5 come from a read-only query of `data/normalized/global/met_daily` (profile `power-native-daily-utc-v1`).
- Region tests in Section 7 ran `dist/places.js` unchanged under Node 20 against the committed bundle. The test coordinates are approximate town points, and I label them as such.

## 3. Registry verification (53 records)

Verdicts: supported; partly supported; unsupported; page mismatch; date mismatch; geography too broad. "Date encoding" notes mean the record matches the source, but its machine-readable period is looser or tighter than the text.

| # | Record | Country | Kind | Editions cited | Verdict | Notes |
|---|---|---|---|---|---|---|
| 1 | us-se-freeze-2022-03 | US | event | 2023 | supported | "wiped out almost half of the industry", "15 million pounds ... night of March 12" and the rabbiteye shares (15-25% NC, about 30% GA) are on PDF p.45. |
| 2 | us-nc-2025-harvest-rain | US | event | 2026 | supported | 2026 p.113: rain at early picking and at the start of the peak for "the state's biggest cultivar, Legacy". |
| 3 | us-ga-helene-2024-09 | US | event | 2025, 2026 | supported | 2026 p.113 is explicit. In 2025 the sentence starts on p.103 and ends on p.104; only p.104 is cited. |
| 4 | us-ga-2025-01-cold-snow | US | event | 2026 | supported | "very cold weather and snow in January" on p.113. The year 2025 comes from context. That is reasonable, but it is an inference. |
| 5 | us-fl-2026-frost | US | event | 2026 | supported | pp.19, 112-113. Start 2026-01-01 with no end; the "outside baseline" tag fires correctly. |
| 6 | us-fl-chill-winters | US | event | 2023, 2025 | supported | "unprecedented temperatures over Christmas", "delayed and short" (2025 p.103); hurricanes and late-2022 cold (2023 PDF p.45). |
| 7 | us-ca-freeze-2022 | US | event | 2023 | supported | 24% below forecast; "Madera County (north of Fresno) and to the north"; 20-30% of acreage. Date encoding: "late February-early March" is stored as 1 Feb to 31 Mar. |
| 8 | us-pnw-2021-2022 | US | event | 2023 | supported | Text says a "dieback pollination problem"; the record drops "dieback". 10-60%; Liberty and Bluecrop worse than Duke. |
| 9 | ca-bc-harvest | CA | practice | 2023, 2025 | supported | Duke hand harvest about 11 July, machine about 20 July (2023 PDF p.47); first week of July 2024 (2025 p.109). |
| 10 | mx-protected-share | MX | practice | 2023, 2025, 2026 | supported | 77.00% and 78.00% hydroponics (2023 PDF p.51); 80.00% and "Not Reported" (2025 p.117, 2026 p.127). |
| 11 | mx-2023-24-heat | MX | event | 2025 | supported | p.125: high temperatures and a wet fall, delayed flower and fruit set, Sinaloa hit harder; heat-stress plant deaths not repeated after delayed pruning. |
| 12 | mx-central-tunnels | MX | practice | 2023, 2025, 2026 | supported | "radiation has the potential to burn the berries" (2023 PDF p.52); "tropicalize" (2025 p.126). |
| 13 | pe-2024-delayed-pruning | PE | event | 2025 | supported | p.71: "producers delayed the pruning of bushes to capitalize on ongoing shortages". ProArándanos late start on p.63. |
| 14 | pe-el-nino-2023 | PE | event | 2025, 2026 | supported | Ventura susceptibility (p.71); Lima less affected (p.72); 299.67 and 233.87 kt (p.54); "not truly zero-chill" (2026 p.81). |
| 15 | pe-2025-cloudy-winter | PE | event | 2026 | supported | p.81: unusual temperatures and many cloudy days in June and July 2025, smaller fruit. |
| 16 | pe-water-ro | PE | constraint | 2023 | partly supported | Reverse osmosis is on PDF p.30 and the 150 mm rainfall on PDF p.29. The names Chavimochic and Olmos are on PDF p.31, which is not cited. The cited page only says "key irrigation project zones". |
| 17 | pe-lambayeque-early | PE | practice | 2023, 2025 | supported | 29% of hectares and an earlier window (2023 PDF p.31). 2025 p.72 gives 27%, which the record omits. |
| 18 | pe-ica-south | PE | practice | 2025 | supported | p.72: Ica, Chincha and Pisco; cooler nights and warmer days. |
| 19 | cl-2022-11-frost-hail | CL | event | 2023 | partly supported | The text matches PDF pp.33-34. But the crop context "Mostly northern highbush" is not on the cited pages, and frost and hail are merged into one event. Outside sources date the frost to 31 Oct to 1 Nov and the hail to 10-12 Nov ([El Tipógrafo](https://eltipografo.cl/2022/11/arandanos-lluvia-y-granizo-de-noviembre-tuvo-minimo-efecto-sobre-la-produccion)). Also tagged `CL`, so it shows at every Chilean pin. |
| 20 | cl-2022-12-heat | CL | event | 2023 | supported | PDF p.33. Date encoding: December 2022 is stated, but start and end are null. |
| 21 | cl-chill-zones | CL | practice | 2025 | supported | p.77: Maule as the southern limit, "about 100km north of" Chillán; Santiago and Ovalle; since about 2014 in pots and tunnels. |
| 22 | cl-2025-26-early-ripening | CL | event | 2026 | supported | p.87: high growing-degree-day accumulation; Duke 20 days earlier. |
| 23 | co-three-peaks | CO | practice | 2023, 2025 | supported | 2,600-3,000 m; peaks December, April, September (2023 PDF p.26); November-December, May-June, September (2025 p.57); daylight and pruning. |
| 24 | ar-harvest | AR | practice | 2023, 2025, 2026 | supported | 2023 PDF p.36: September to early October, earlier than Chile. I checked the 2023 part only. |
| 25 | cn-yunnan-calendar | CN | practice | 2023, 2025 | supported | December start, February to mid-April peak, May end; late May and June at altitude (2023 PDF p.58); November to June (2025 p.143). |
| 26 | cn-yunnan-2024-dry-heat | CN | event | 2025 | supported | p.144: dry spring, "as is often the case" high temperatures in April and May, 10-15% volume increase. |
| 27 | cn-liaoning-monsoon-undated | CN | event | 2026 | supported | pp.152-153. The year is not stated. The passage follows a 2025-26 Yunnan sentence, so the 2025 summer is likely [inference]. |
| 28 | cn-guizhou-rabbiteye | CN | practice | 2023, 2025, 2026 | supported | 2023 PDF p.58: largest province, small rabbiteye growers, juice-grade processing. I checked the 2023 part. |
| 29 | es-huelva-tunnels | ES | practice | 2023 | supported | "almost 90% of Spanish production", macro-tunnels (PDF p.76); "around 97% ... under tunnels" (PDF p.77). |
| 30 | es-huelva-2023-cold | ES | event | 2023 | supported | PDF p.77: 0-3 °C normal, below 0 °C in mountains, abnormal persistence. Date encoding: "late January" is stored as starting 1 January. |
| 31 | es-2026-rain-cold | ES | event | 2026 | supported | pp.197-198: January-February rain, tunnels destroyed in isolated cases, April exports -28%, southern Portugal and Morocco similar. |
| 32 | es-north-highchill | ES | practice | 2023, 2025 | supported | 2023 PDF p.76: Galicia and Asturias, open fields, small parcels. |
| 33 | ma-agadir-water | MA | constraint | 2023, 2025 | supported | Drought, reverse osmosis and desalination of "variable" reliability (2023 PDF p.79); desalination (2025 p.193). |
| 34 | ma-2023-cold | MA | event | 2023, 2025 | supported | Three-week delay (2023 PDF p.79); "first volume decline" in more than a decade (2025 p.193). |
| 35 | ma-north-system | MA | practice | 2025 | supported | p.193: Larache and Rabat, mid-2000s. The polygon choice leaves out the Gharb region between them (Section 7). |
| 36 | pl-2024-05-frost | PL | event | 2025, 2026 | supported | Season 3 weeks early, green fruit, over 50% losses locally (p.207); Lublin, central Poland and 20% on established farms (p.208); "devastating" (2026 p.214). |
| 37 | pl-bialystok-2021-cold | PL | event | 2023 | supported | PDF p.88 does say -41 °C in 2021 and over 30% of the crop destroyed. The value is implausible as a 2021 air temperature [inference]. The record's limitation flags it as uncorroborated, which is correct. |
| 38 | de-2024-frost | DE | event | 2025 | supported | p.222: green fruit on Duke; damage depended on water for overhead irrigation. |
| 39 | rs-water | RS | constraint | 2025, 2026 | partly supported | Reverse osmosis and anti-hail nets are supported. But the crop context "Duke predominant" refers to Romania in the source, not Serbia. The 2026 hail-net sentence is on p.232, which is not cited. |
| 40 | za-limpopo-2024-frost | ZA | event | 2025, 2026 | supported | "over July and August ... up to 30% ... just 3%" (2025 p.247). 2026 p.251 calls them "spring frosts". The two editions disagree on the season, and the record does not flag it. |
| 41 | za-north-2025-minor-frost | ZA | event | 2026 | supported | "extremely minor" (p.251); Berries ZA "substantially fewer frost events" (p.249). |
| 42 | za-north-harvest | ZA | practice | 2025 | page mismatch | The June, July and August sequence is on p.255. "The north about 40% of the industry" is on p.253, which is not cited. |
| 43 | za-wc-2024-weather | ZA | event | 2025 | supported | p.247: late Aug to early Sep frost on one farm, floods, wind. Date encoding: the frost dates are stated, but the period is null. |
| 44 | zw-2024-compressed | ZW | event | 2025 | supported | p.241: weeks 37-40; a cold snap triggered induction; mild winter with fewer chill units. |
| 45 | na-kavango-frost | NA | event | 2025, 2026 | supported | "true frost" in 30 years; 2023 near wipe-out; Rundu hit in 2024 (2025 p.242, 2026 p.244). Polygon vintage issue (Section 7). |
| 46 | au-nnsw-2022-floods | AU | event | 2023 | supported | PDF p.65: two La Niñas, two floods in Northern NSW, down 16% to 19,600 MT. |
| 47 | au-alfred-2025 | AU | event | 2025 | supported | p.156: Ex-Tropical Cyclone Alfred, Moreton Bay, March 2025. |
| 48 | au-wa-pruning | AU | practice | 2023, 2025 | partly supported | 2025 p.156 describes one Western Australia-based breeder's farms (Gingin to Manjimup), with harvest from March to January. The record turns this into "Western Australian growers". |
| 49 | nz-waikato-2022-10-frost | NZ | event | 2023, 2025 | supported | PDF p.67: polar blast, rabbiteye, helicopters, Waikato about 40% of the crop. The day (7 October) is available from BBNZ via [Te Awamutu News](https://www.teawamutunews.nz/2022/10/how-tunnel-vision-paid-off/). |
| 50 | nz-hb-2023-floods | NZ | event | 2023 | supported | PDF p.67: "15% of what they would have usually produced". Date encoding: "late January" is stored from 1 January. |
| 51 | nz-2024-25-heat | NZ | event | 2025 | partly supported | 28 days above 27 °C and shrivelled late varieties (p.160) are supported. But cited p.159 is the BBNZ summary, which says the season had "relative calm climatic conditions ... without major weather impacts" and similar yields. The record does not surface this conflict. |
| 52 | in-monsoon | IN | practice | 2023, 2025 | supported | Monsoon, low-chill SHB, mid-February to early June (2023 PDF p.69, 2025 p.166). The "protected systems" point appears only in 2023. |
| 53 | ke-year-round | KE | practice | 2025, 2026 | supported | Equator, pruning, year-round (2025 p.243); January-March window (2026 p.246). |

Totals: 47 supported, 5 partly supported, 1 page mismatch. The sample covers 21 countries, 33 events, 17 practice records and 3 constraints, with 2023, 2025 and 2026 citations.

What the sample shows about the curation pattern:
- Errors come in where curators add context (crop context, actor scope) or merge statements across pages. They do not come from misquoted numbers.
- Dates are often looser than the source (month starts instead of "late January") or missing when the source gives them (December 2022 heat, late August frost).
- Conflicts between an association's summary and the report team's narrative are not flagged (NZ 2024-25, South Africa 2024 frost season).

## 4. Inventory and rights

### 4.1 Status of the editions Astra could not get

| Edition | What exists today (checked 2026-10-11) | Rights position | Verification |
|---|---|---|---|
| 2021 | [Official page](https://www.internationalblueberry.org/2021-report/) returns HTTP 200 with the IBO access form. The [Berries ZA page](https://www.berriesza.co.za/ibo-state-of-the-industryreport2021/) is live and still links `IBO-2021-Final-interactive.pdf`, but that file returns 404. The Wayback CDX index has only two captures of the file: 20240225094136 (truncated, as Astra reported) and 20240714150135 (701 bytes). | Unknown. The 2021 licence text is not available to check. | opened-limited |
| 2024 | The [official page](https://www.internationalblueberry.org/2024-report/) shows the form "Complete this form to access the content" (first and last name, company, job title, email, phone, sector, country). IBO's [2024 announcement](https://www.internationalblueberry.org/2024/07/25/ibo-announces-2024-global-state-of-the-blueberry-industry-report/) says the report "will be accessible to the public for free on the IBO's website". A [Scribd upload](https://www.scribd.com/document/868719668/report-2024) (121 pages, uploader "Mitra Taj") shows the 2024 contents. | The Scribd page states "© All Rights Reserved" and is a third-party upload, so it is not usable. In the Scribd preview text I could not see whether the 2024 PDF carries the same reuse licence as 2023, 2025 and 2026. | opened-limited |
| 2022 | Berries ZA [page](https://www.berriesza.co.za/global-state-of-the-blueberry-industry-report-2022/) is live; its PDF link returns 404. The archived copy Astra used is on the server, and its SHA-256 matches the inventory. | I searched the server's 2022 text layer and found no licence or copyright clause. Astra was right to exclude 2022 from the public registry. | opened |
| 2023 | Berries ZA [page](https://www.berriesza.co.za/global-state-of-the-industry-report-2023/) is live; PDF link 404. The registry links to a Wayback copy of the mirror. | Reuse licence confirmed on PDF p.112 (printed 223). | opened |
| 2025 | [FlippingBook viewer](https://online.flippingbook.com/view/768531494/) is reachable without login. The [official page](https://www.internationalblueberry.org/2025-report/) shows the form. A [Scribd upload](https://www.scribd.com/document/994478343/Ibo-Report-2025) also exists. | Licence confirmed on p.280. The Scribd copy should be ignored. | opened (FlippingBook); search-only (Scribd) |
| 2026 | The [official page](https://www.internationalblueberry.org/report-2026/) shows the form. The server copy is a "previously supplied PDF" with no public download URL in its manifest. | Licence confirmed on p.285. The provenance of the supplied copy (who supplied it, from which channel) is not recorded. | opened-limited |
| 2008/2010 precursor | [Oregon Blueberry Commission PDF](https://www.oregonblueberry.com/update/USHBC-report.pdf) is live. A third-party [FlipHTML5 copy](https://fliphtml5.com/lxsr/kdyw/basic/51-51) also appears in search results. | Copyright USHBC, no reuse grant (per inventory). Use as reference only. | opened (Oregon PDF); search-only (FlipHTML5) |

The licence wording in 2023, 2025 and 2026 is the same. IBO grants "a worldwide, non-exclusive, royalty-free, sublicensable and transferable license to use, reproduce, distribute, prepare derivative works of, display, and perform the Content ... for any purposes", provided there is "clear and unambiguous attribution to the IBO, or its partner organizations". IBO also asks users to "use the same source that is used within the publication itself to reference data" (2026 p.285, 2025 p.280, 2023 PDF p.112).

### 4.2 Sources missing from the inventory

| Source | What it holds | Rights position | Verification |
|---|---|---|---|
| [IBO Summit SA Presentations](https://www.internationalblueberry.org/ibo-summit-sa-presentations/) (Cape Town, 25-27 Sept 2025) | 15 PDFs, including [Colin Fain, IBO Global Production Report](https://www.internationalblueberry.org/wp-content/uploads/2025/10/10.15-Colin-Fain-IBO-Global-Production-Report.pdf) (2024 global totals: 282,193 ha planted, 2,150.61 thousand t, 2028 projection 3,208 thousand t), [Stephen Taylor, Global Production](https://www.internationalblueberry.org/wp-content/uploads/2025/10/11.30-Stephen-Taylor-Global-Production.pdf), and talks by Herman van Dyk (South Africa), Louw Pienaar, Guy Midgley (climate) and Marcel Beelen (machine harvesting). | Page footer says "Copyright © 2025 IBO". The IBO [terms page](https://www.internationalblueberry.org/terms-and-conditions/) says "In progress". The decks are third-party authored, and no reuse licence is stated. Treat as citation-only. | opened (page and Fain deck); HTTP 200 (Taylor deck) |
| [Morocco Berry Conference 2025 Presentations](https://www.internationalblueberry.org/morocco-berry-conference-2025-presentations/) | 11 PDFs (Agadir, Nov 2025), including Lisa DeVetter and an IBO presentation. | No licence stated. Citation-only. | opened (link list) |
| [Brazelton and Fain 2023 deck](https://www.internationalblueberry.org/assets/uploads/2023/09/Cort-Brazelton-Colin-Fain_State-of-the-Global-Blueberry-Industry.pdf) | State of the global industry slides from 2023. The IBO Summit 2023 was held in Poland (per the [IBO library menu](https://www.internationalblueberry.org/library/)). The live 2023 presentations page returns 404, but Wayback holds captures from 2023-08 to 2024-12. | No licence stated. | opened (PDF, partial range) |
| Historical IBO library (2011-2015 country presentations, IBO 2019 talks) | Wayback captures of `internationalblueberry.org/downloads/...` list items such as "Evolution of Evergreening 2015" (Coffs Harbour summit). | The archived listing shows "Member Price $0.00 USD Non-Member Price $100.00 USD". Paid for non-members, so out of scope. | opened (one archived item) |
| IBO news feed | For example "Weather challenges hit Argentine blueberry production" (28 Sept 2026), linked from IBO post pages. | News reposts. Rights unknown. | opened (links seen on IBO pages) |

What Astra got right: the inventory records gates honestly, refuses truncated or partial copies, and does not submit forms. What it misses: the Summit and conference decks above, the Scribd copies (worth recording as "seen, rejected" so that nobody re-imports them later), and the fact that the 2024 gate is a free lead form, not a payment. The 2024 gate is a human decision. Rohit or Paul can fill in IBO's free form, or email IBO, and record the terms they receive. The research agents must not do that.

### 4.3 A citation error in the integration review

The review cites Mexico 2021/22 production of 74.20 thousand t to "2023 PDF p.51". In the server's text layer, 74.20 appears with Mexico on 2023 PDF pp.18 and 48, not on p.51. The 2022 value of 84.70 is on 2022 PDF p.84 as stated, and also on pp.28 and 80. A visual check of p.51 is still needed, because the figure may be inside an image there.

## 5. Event-check method

### 5.1 Comparison windows

| Case | Window used (UTC) | Problem | Evidence |
|---|---|---|---|
| US Southeast, March 2022 | 12-13 March | Fine. US dawn on 13 March falls on UTC 13 March. The report calls the NC event "windborne", so it was an advective freeze, which grids represent well. | Stored Tmin -2.53 to -5.47 °C. |
| Chile, "November 2022" | 1-30 November | **Misses the event.** The frost was on 31 Oct and 1 Nov local time ([Portal Frutícola](https://www.portalfruticola.com/noticias/2022/11/09/chilecomo-se-han-afectado-los-arandanos-de-nuble-por-las-heladas/): "los días 31 octubre y 1 de Noviembre"). The grid's coldest days were 30 and 31 Oct UTC. | Chillán cell (-36.5, -71.875): 30 Oct +2.24, 31 Oct +4.56, 1 Nov +10.08 °C. Andean neighbour (-36.5, -71.25): 30 Oct -6.15, 31 Oct -0.74 °C. Linares-east cell (-36.0, -71.25): 30 Oct -1.57 °C. |
| Waikato, "October 2022" | 1-31 October | The window contains the event, but by luck. The 7 Oct dawn (NZDT, UTC+13) falls on UTC 6 October. The check found that day as the month's minimum but did not say so. | Chosen cell 6 Oct +5.15 °C. |

Calendar-month windows built from the report's month label are the wrong unit. An event window should be the local night of the event, with a margin of a few days, and should account for the UTC offset of the daily product. NASA POWER offers both UTC and local solar time daily data ([Daily API docs](https://power.larc.nasa.gov/docs/services/api/temporal/daily/): "Daily API defaults to providing LST"). The project archive uses UTC days.

### 5.2 Coordinates against the places named

- The checks used benchmark pins (Linares city, Chillán city, Ohaupo). They did not use the places the event sources name. For Chile, ASOEX named Coihueco, then San Ignacio and El Carmen, and "Maule-Sur hacia la cordillera". The IBO text only says "between Linares and Chillan". Astra did not look for a corroborating source for the day or the place.
- In Chile, the coordinate was not the main fault. The Chillán cell spans about -36.75 to -36.25 and -72.19 to -71.56, so it contains Coihueco (approximately -36.63, -71.83; 15 km from the cell centre) [inference from the cell bounds]. The failures were the window and grid physics.
- In Waikato, the coordinate choice does matter. Ohaupo lies almost exactly between two cell centres (28.2 km against 29.2 km). The nearest-cell rule picked the western cell, which reaches the Tasman coast, and that cell was 5 °C warmer on the frost night than the inland cell.
- None of the cases records the cell's elevation, land fraction or neighbouring cells. Without them, a reader cannot tell whether a miss comes from the data, the cell or the event.

### 5.3 Could daily grid Tmin be expected to show these events?

Only partly.
- The cells are about 55 km by 55 km at 37° S (0.5° by 0.625°) [inference from the grid spacing]. Frost damage in Ñuble foothills and Waikato orchards most likely came from radiative cooling in calm, clear air after the cold air arrived [inference; station wind and cloud data would confirm it]. Such frost is strongest in hollows and on valley floors. A cell average with a warm-biased reanalysis 2 m temperature cannot reproduce -5 °C orchard minima. Project station checks already found a Tmin bias near +1 °C and missed frosts (shared brief).
- The grid did catch the timing. In NZ, 6 October UTC was the coldest day of 4 to 9 October in all four nearby cells, and Astra's check found it was the October minimum of the chosen cell. In Chile, 30 October was the coldest day of 29 October to 3 November in all five cells checked. The size was off by 5 to 10 °C against the orchard reports.
- Advective freezes, such as the US March 2022 windborne freeze, show up clearly.
- So "not represented at this sample cell" is the expected result for radiative frosts. The interpretation "unresolved location/grid/species mismatch" mixes three things. Species does not affect whether the weather data show freezing.

### 5.4 Other method issues

- The event-check file predates the registry and does not link to registry event IDs. It records only PDF pages.
- The metrics are daily counts at 0 °C and -2.2 °C. The file has no hourly duration, no local-night minimum and no neighbourhood statistics.
- The saved 2022 model stages are useful context. They put Chile at the end of flowering or early fruit on 1 Nov, and Waikato in flowering on 7 Oct. Both agree with the news reports ("huertos en fruto cuajado"; "when the flowers were the most open"). The file does not draw this conclusion.

### 5.5 Proposed station-based event-check protocol (v2)

1. **Register the case first.** Give it a case ID linked to the registry event, the claims it rests on, the reported hazard, the reported stage, the crop and protection system, and the source date precision. Write down the expected result before looking at the data.
2. **Corroborate the date and place.** Find at least one source from a different family (association bulletin, ministry, extension service, local news) that gives a day and named places. Chile: ASOEX via El Tipógrafo (1 Nov 2022, Coihueco). NZ: BBNZ via Te Awamutu News (7 Oct 2022, Waikato, -5 °C). Store these as separate claims.
3. **Geocode the named places.** Use municipality points or polygons with an uncertainty radius. Where an orchard or land-use mask exists, use it.
4. **Select stations.** Take every station within 30 km of a named place and within about 200 m of its elevation. Prefer hourly data. Record sensor height, network, licence and data version. Candidate networks (all opened 2026-10-11):
   - Chile: [INIA Agrometeorología](https://agrometeorologia.cl/) (its page lists Ñuble products) and [DMC Servicios Climáticos](https://climatologia.meteochile.gob.cl/).
   - New Zealand: NIWA's climate database, now at [CLIDB on DataHub](https://cliflo.niwa.co.nz/) (the old CliFlo address redirects there).
   - United States: [GHCNd](https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily), [ISD hourly](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database), [Georgia AEMN](http://www.georgiaweather.net/), [NC ECONet](https://econet.climate.ncsu.edu/), [FAWN](https://fawn.ifas.ufl.edu/) and [IEM ASOS](https://mesonet.agron.iastate.edu/request/download.phtml).
   - Elsewhere: ISD or [Meteostat](https://dev.meteostat.net/).
   - Terms differ by network and must be recorded for each station.
5. **Use local-night windows.** For the event night D, use 18:00 on D-1 to 10:00 on D, local time. Add three nights either side. Compute the minimum, the hours below 0, -1 and -2.2 °C, and wind and cloud where available.
6. **Compare the grid fairly.** Use the nearest cell plus the 3 by 3 neighbourhood. Re-aggregate the MERRA-2 hourly cache into the same local-night windows. Record each cell's elevation and land fraction. Compare the station-minus-grid difference on the event night with its distribution on all clear, calm nights in the same month from 2010 to 2025. This separates the normal bias from an event-specific miss.
7. **Classify the mechanism.** Use station wind and cloud to label the event advective, radiative or mixed. Set the expected detectability from that label.
8. **Check the stage.** Compare the modelled stage on date D with the reported stage (fruit set, open flower, green fruit).
9. **Report outcomes as categories, not a score.** Use: hazard seen at the station (yes/no); hazard seen in the grid (yes/no); size difference (°C); timing offset (days); stage agreement. Do not compute an accuracy rate until there are enough independent events.
10. **Store the check.** Write it as an event-check record (Section 6) with code commit, data versions and station IDs. Run it first on the registry's 39 events that have day or month precision and a station within reach.

## 6. Schema: current state, gaps and a v2 proposal

### 6.1 v1 against the review's own design

| Review design element (integration review, "Record design") | Registry v1 | Gap |
|---|---|---|
| Separate document, claim and event records | One record per event or practice, with citations nested inside. `event_id` is unique for each record (39 of 39). | No claim layer. One record merges claims from several editions with different numbers, for example Poland 2024 (20% vs over 50%). |
| Document: publication date, revision, acquisition status, licence | `sources[]` has title, edition, URL, SHA-256, PDF pages, attribution and a licence label with pages. | No publication date, licence text or URL, landing vs retrieved URL, acquisition status or revision link. |
| Locator: section or table, extraction method, short excerpt | Pages plus a free-text locator. | No table ID, spread side, excerpt or excerpt hash, or extraction method. |
| Geography: identifiers, precision, place text as stated | Geography IDs mapped to bundle polygon IDs; precision is region or country. | No stable codes (Natural Earth `adm1_code` or ISO 3166-2), no stated place text, no point or municipality precision, no uncertainty radius. |
| Time: observation season, event date precision, publication date, forecast target | One `period` (label, start, end, precision). | Observation, event, publication and forecast time are mixed together. No time zone or local-night flag. |
| Crop and management | Free-text `crop_context`. | No structured species, cultivar, system or stage. Curators added unsupported context (rows 19 and 39). |
| Quantity: original value, unit, basis | None. | Numbers exist only in prose, so they cannot be queried, converted or compared across editions. |
| Evidence type | 3 values. | No chart approximation, forecast, derived calculation, secondary excerpt or news. |
| Review: lineage, duplicates, conflicts, corroboration, reviewer, allowed use | `review_status` = "source_checked" for all records; limitations as text. | No reviewer, date, conflict links, independent-source count or allowed use. |

### 6.2 Schema v2 proposal

Aims: hold several source families (IBO reports, official statistics series, extension bulletins, news, station-based checks); keep every current IBO record valid through a deterministic migration; keep the UI working during the change.

Entities (JSON arrays, or SQLite tables with the same columns):

- `source_families`: id, name, publisher, family_type (`industry_report`, `statistics_series`, `extension_bulletin`, `news`, `station_network`, `conference_deck`), default rights.
- `documents`: id, family_id, title, edition, issue_date, revision_of, language, urls {landing, retrieved, archived}, retrieved_on, sha256, page_model (`single`, `spread_2k-2`), access (`open`, `free_registration`, `member`, `paid`), rights {status: `open_licence_verified` | `permission_granted` | `citation_only` | `unknown`, licence_name, licence_url, statement_locator, attribution_template, redistribution, excerpt_max_chars}.
- `claims`: one atomic statement at one locator. Fields: id, document_id, locator {pdf_pages, printed_pages, section, table_id, spread_side, excerpt, excerpt_sha256}, statement, claim_type (`event_occurrence`, `impact_estimate`, `practice`, `calendar`, `constraint`, `statistic`, `forecast`, `cultivar_trait`), stated_by, evidence_type, geography {ids, stated_text, precision, uncertainty_km}, time {observation, event {start, end, precision, tz, local_night}, publication, forecast_target}, crop {species[], cultivars[], system[], stage}, quantities[], links {event_id, supersedes, conflicts_with[], corroborates[]}, extraction {method, tool_version}, review {status, reviewer, reviewed_on, note}, allowed_use[].
- `quantities` (inside a claim): name, value, low, high, unit, basis (fresh, processed, total, planted, bearing, export), denominator, as_reported.
- `events`: id, hazard, mechanism, start, end, precision, tz, geography_ids, reported_stage, claim_ids, independent_family_count, check_ids.
- `subjects`: the display unit, replacing v1 records. Fields: id, kind (`event`, `practice`, `constraint`), title, summary, claim_ids, event_id, limitations[]. The UI renders subjects. Exports carry claims.
- `series_observations` (for statistics families): series_id, document_id (the vintage), variable, unit, geography_id, period, value, status (`observed`, `estimated`, `forecast`, `regression_filled`). This holds revisions, for example Mexico 2021/22 at 84.70 (2022 edition) and 74.20 (2023 edition), as two vintages of one observation.
- `event_checks`: id, event_id, protocol_version, stations[] {network, id, distance_km, elev_m, licence}, grid_cells[], windows, metrics, outcome {station_hazard, grid_hazard, magnitude_diff_c, timing_offset_days, stage_agreement}, code_commit.
- `geography_crosswalk`: geography_id, bundle_sha256, polygon_ids[], stable_codes[] (`adm1_code`, ISO 3166-2), boundary_vintage_note.

Example: one migrated IBO subject with two claims and a corroborating news claim. The values come from the sources checked above.

```json
{
  "schema_version": 2,
  "documents": [
    {"id": "ibo-2023", "family_id": "ibo-global-reports", "edition": 2023, "page_model": "spread_2k-2",
     "sha256": "ecdb37aef241b17bcb944171b363184bf917bbe3e4c90fd02b4f4bd0097fc229",
     "rights": {"status": "open_licence_verified", "statement_locator": {"pdf_pages": [112], "printed_pages": [223]},
                "attribution_template": "Source: International Blueberry Organization (IBO)", "redistribution": true}},
    {"id": "eltipografo-2022-11-17-arandanos", "family_id": "news-cl", "issue_date": "2022-11-17",
     "urls": {"landing": "https://eltipografo.cl/2022/11/arandanos-lluvia-y-granizo-de-noviembre-tuvo-minimo-efecto-sobre-la-produccion"},
     "rights": {"status": "citation_only", "redistribution": false, "excerpt_max_chars": 200}}
  ],
  "claims": [
    {"id": "c-ibo2023-cl-frost-asoex", "document_id": "ibo-2023",
     "locator": {"pdf_pages": [33], "printed_pages": [64], "section": "Chile country member summary (ASOEX)"},
     "claim_type": "event_occurrence", "stated_by": "ASOEX blueberry committee", "evidence_type": "association_report",
     "geography": {"ids": ["CL"], "stated_text": "Chile", "precision": "country"},
     "time": {"event": {"start": "2022-11-01", "end": "2022-11-30", "precision": "month", "tz": "America/Santiago"}},
     "links": {"event_id": "ev-cl-2022-11-01-frost"}, "allowed_use": ["display", "export", "rag_answer"]},
    {"id": "c-ibo2023-cl-frost-team", "document_id": "ibo-2023",
     "locator": {"pdf_pages": [34], "printed_pages": [66], "section": "Chile report team narrative"},
     "claim_type": "event_occurrence", "stated_by": "IBO report team", "evidence_type": "industry_narrative",
     "geography": {"ids": ["CL-LINARES-CHILLAN"], "stated_text": "between Linares and Chillan", "precision": "multi_admin1"},
     "links": {"event_id": "ev-cl-2022-11-01-frost"}, "allowed_use": ["display", "export", "rag_answer"]},
    {"id": "c-news-cl-frost-coihueco", "document_id": "eltipografo-2022-11-17-arandanos",
     "claim_type": "impact_estimate", "stated_by": "ASOEX blueberry committee with iQonsulting", "evidence_type": "news_secondary",
     "geography": {"ids": ["CL-NUBLE"], "stated_text": "Coihueco; San Ignacio and El Carmen less; Maule-Sur toward the cordillera", "precision": "municipality"},
     "time": {"event": {"start": "2022-11-01", "end": "2022-11-01", "precision": "day", "tz": "America/Santiago", "local_night": true}},
     "quantities": [{"name": "fresh_export_loss", "value": 900, "unit": "t", "as_reported": "en torno a 900 toneladas, equivalente a 0,9%"}],
     "links": {"event_id": "ev-cl-2022-11-01-frost", "conflicts_with": ["c-ibo2023-cl-frost-team"]},
     "allowed_use": ["display_link", "model_validation_date"]}
  ],
  "events": [
    {"id": "ev-cl-2022-11-01-frost", "hazard": "frost", "mechanism": "unknown",
     "start": "2022-10-31", "end": "2022-11-01", "precision": "day", "tz": "America/Santiago",
     "geography_ids": ["CL-LINARES-CHILLAN"], "reported_stage": "fruit set",
     "claim_ids": ["c-ibo2023-cl-frost-asoex", "c-ibo2023-cl-frost-team", "c-news-cl-frost-coihueco"],
     "independent_family_count": 2}
  ],
  "subjects": [
    {"id": "cl-2022-11-frost-hail", "kind": "event", "event_id": "ev-cl-2022-11-01-frost",
     "claim_ids": ["c-ibo2023-cl-frost-asoex", "c-ibo2023-cl-frost-team", "c-news-cl-frost-coihueco"]}
  ]
}
```

Notes on the example: `CL-NUBLE` is a proposed new geography ID. The conflict link records that ASOEX's early estimate (0.9% of exports) and the report team's later "larger than initially estimated" statement disagree. The hail of 10-12 November would become its own event.

How other families fit:
- **Statistics series.** One document per vintage (release), one `series_observations` row per cell, and quantities in the original units. Claims are needed only for footnotes and methods.
- **Extension bulletins.** Claims of type `practice`, `calendar`, `cultivar_trait` or `advisory`. Rights default to the publisher's terms, and many US land-grant works are not public domain, so check each one.
- **News.** `citation_only` rights. Allowed use: link display and use of the date for validation only after a second family corroborates it. Never redistribute full text.

Compatibility with v1:
- Every v1 record becomes one `subject` with the same ID. Each v1 citation becomes one claim. The v1 summary and limitations stay on the subject. v1 `period` moves to the event (for events) or to claim observation time. `crop_context` is kept as `crop.note` until it is parsed.
- A build script produces `ibo-regional-v1.json` from v2 until the client reads v2. This is needed because `validate()` rejects any `schema_version` other than 1 (`dist/evidence.js:73`).
- Keep `geography_reference.region_ids`, and add stable codes next to them, so a new Natural Earth bundle can be re-crosswalked by code.

## 7. Region matching, UI, exports and rights: defects and risks

Region test results (unchanged `dist/places.js`, committed bundle, hash matched in every case; coordinates approximate):

| Test point | Resolved region | Registry geography | Comment |
|---|---|---|---|
| Coihueco, Linares, Chillán | Ñuble / Maule | CL-LINARES-CHILLAN | Correct. |
| Curicó (-34.98, -71.24) | Maule | CL-LINARES-CHILLAN | About 100 km north of Linares, but still gets the "Linares to Chillán" frost. Geography too broad. |
| Santiago | Santiago | none (country records only) | Gets the Chile frost labelled "Chile, country context". |
| Kenitra (34.26, -6.58) | Gharb-Chrarda-Béni Hssen | none | Lies between Larache and Rabat, but gets no northern Morocco records. |
| Biougra (30.21, -9.37) | Suss-Massa-Draa | MA-SMD | Correct, but this pre-2015 polygon reaches far inland to the Draa. |
| Rundu | Kavango | NA-KAV | Correct. |
| Divundu (approx. -18.10, 21.55) | Zambezi | none | Possible miss for a place the record names. Needs a verified coordinate [inference]. |
| Chao, La Libertad | La Libertad | none | The largest Peruvian region (45% of plantings, 2023 PDF p.31) has no regional records. |
| Washington, DC | "Washington" (polygon 2340) | none | The polygon-ID fix works. |
| Moguer, Palos, Lepe | Huelva | ES-H | Correct. |
| Ohaupo, Hamilton | Waikato | NZ-WKO | Correct. |

Defects and risks:

| ID | Defect or risk | Evidence | Severity |
|---|---|---|---|
| D1 | Chile event window missed the grid's coldest days. | Section 5.1, stored Tmin for 29 Oct to 3 Nov. | High |
| D2 | Waikato check used a coast-touching boundary cell. | 28.2 vs 29.2 km; +5.15 vs +0.06 °C. | High |
| D3 | When a record has region and country tags, the "Report scope" label shows only the geography matched at the pin. At a Santiago pin, the Linares to Chillán frost appears as "Chile, country context". | `select()` keeps only matched geographies (`evidence.js:255-258`); `contextOf()` labels from those (`evidence.js:512-518`). | Medium |
| D4 | No claim layer; event grouping is dead code. | 39 unique `event_id` values; grouping in `evidence.js:497-511`. | Medium |
| D5 | No structured quantities or edition revisions. | v1 field list (Section 6.1). | Medium |
| D6 | Unsupported crop context and actor scope added by curators. | Rows 19, 39, 48. | Medium |
| D7 | Dates looser than the sources, or missing. | Rows 7, 20, 30, 43, 50. | Medium |
| D8 | Region IDs are bundle array positions; country match is by name. | `evidence.js:228-231`; bundle `entities` indexes. | Medium |
| D9 | Boundary vintages: Morocco pre-2015 regions, Namibia pre-2013 Kavango; Maule region is wider than "Linares to Chillán"; Gharb is excluded from northern Morocco. | Region tests above. | Medium |
| D10 | Attribution is "Source: International Blueberry Organization (IBO)" for every record, including sections IBO marks as adapted from ASOEX, ProArándanos, ABGA, Freshuelva or Berries ZA. The licence asks users to cite the source used within the publication. Licence text and URL are not in the registry or exports. | `sources[].attribution`; licence text, 2026 p.285. | Medium |
| D11 | Source links are hard to verify: 2026 goes to a lead-form page, 2023 to a Wayback copy of a third-party mirror, and the 2025 FlippingBook link has no page anchor. | `sources[].url`; `citationList()` adds `#page=` only for `.pdf` paths (`evidence.js:338-340`). | Low |
| D12 | "source_checked" cannot be audited: no reviewer, date or excerpt hash per record. No test or build script references the registry (search of the repository). | `evidence.js:240` filter; grep results. | Medium |
| D13 | The sort key mixes observation dates with edition years, so undated 2023-edition records sort as "2023". | `evidence.js:234-235`. | Low |
| D14 | The summary line says "N source-checked regional records" but counts country-context records too. | `app.js:140-141`. | Low |
| D15 | The strict `schema_version === 1` check means any v2 file disables the panel. | `evidence.js:73`. | Low (plan for it) |
| D16 | Event-check file is not linked to registry IDs and uses PDF pages only. | `ibo_event_checks.json` cases. | Low |
| D17 | Integration review cites the wrong page for Mexico 74.20. | Section 4.3. | Low |
| D18 | Conflicts between association summaries and report-team text are not flagged. | Rows 40, 51. | Medium |

What works well:
- All text is rendered through `textContent`.
- The library loads same-origin only, with a timeout.
- A hash mismatch yields "no evidence", never a name fallback.
- Loading, unavailable, unresolved, no-match and pending states are kept apart, and none of them alters weather values.
- HTML exports render every matched record with details open.
- The baseline tag flags post-2025 records.
- Coverage and absence notes are clear and repeated.

## 8. Prioritised recommendations

P1 (do first):
1. Re-run the Chile and Waikato checks with the Section 5.5 protocol. Use local-night windows, 3 by 3 cells, MERRA-2 hourly re-aggregation, and station data from INIA Agrometeorología or DMC (Chile) and NIWA CLIDB (NZ). Register both cases before looking. Re-label the old results as "window or cell choice inconclusive", not "not represented".
2. Add the day-precise corroborating claims to the registry: 1 Nov 2022 at Coihueco from ASOEX via El Tipógrafo, and 7 Oct 2022 in Waikato from BBNZ via Te Awamutu News. Use a citation-only news family. Split the Chile frost from the 10-12 Nov rain and hail.
3. Fix the six record issues found:
   - za-north-harvest: add p.253.
   - pe-water-ro: add PDF p.31 (printed 60 or 61).
   - rs-water: correct the crop context and add 2026 p.232.
   - cl-2022-11-frost-hail: remove "Mostly northern highbush" or cite a page that supports it.
   - au-wa-pruning: narrow the actor to one breeder's farms.
   - nz-2024-25-heat: add a conflict note.
   - Also tighten the date fields in rows 7, 20, 30, 43 and 50.
4. Show the report's own scope label on every card, even when the pin matched only the country tag.

P2:

5. Add stable admin-1 codes to the crosswalk. Document the Morocco and Namibia boundary vintages. Decide whether MA-NORTH should include Gharb and whether CL-LINARES-CHILLAN should stay at whole-region scale.
6. Adopt schema v2 with a build script, a validator and unit tests. Generate the v1 file from it until the client moves to v2.
7. Ask Rohit or Paul to request the 2024 report (and 2021 if IBO still holds it) through IBO's free form or by email, and to record the terms. Record the provenance of the supplied 2026 PDF.
8. Add the 2025 Summit and Morocco conference decks as a citation-only "conference_deck" family. The Fain deck gives 2024 global totals and projections.
9. Use per-item attribution as the licence asks, and include the licence text or locator in exports.

P3:

10. Fix the sort key and the summary count text, and make the schema check accept v1 and v2.
11. Render the spread pages once, and confirm the left or right printed-page side for the 2023 and 2025 citations.
12. Record rejected copies (the Scribd uploads) in the inventory so they are not re-imported.

## 9. URL verification log (checked_on 2026-10-11)

| URL | Status | Note |
|---|---|---|
| https://www.internationalblueberry.org/global-satet-of-the-blueberry-industry-report/ | opened | Lists 2021 to 2025 editions. |
| https://www.internationalblueberry.org/2021-report/ | opened-limited | HTTP 200; access form. |
| https://www.internationalblueberry.org/2022-report/ | opened-limited | Access form. |
| https://www.internationalblueberry.org/2023-report/ | opened-limited | Access form. |
| https://www.internationalblueberry.org/2024-report/ | opened-limited | Form fields listed in Section 4.1. |
| https://www.internationalblueberry.org/2025-report/ | opened-limited | Access form. |
| https://www.internationalblueberry.org/report-2026/ | opened-limited | Access form. |
| https://www.internationalblueberry.org/2024/07/25/ibo-announces-2024-global-state-of-the-blueberry-industry-report/ | opened | "accessible to the public for free". |
| https://online.flippingbook.com/view/768531494/ | opened | Viewer HTML. |
| https://www.scribd.com/document/868719668/report-2024 | opened-limited | Third-party upload, "© All Rights Reserved". |
| https://www.scribd.com/document/994478343/Ibo-Report-2025 | search-only | Third-party upload. |
| https://fliphtml5.com/lxsr/kdyw/basic/51-51 | search-only | Third-party copy of the 2008/2010 precursor. |
| https://www.oregonblueberry.com/update/USHBC-report.pdf | opened | PDF (range request). |
| https://www.berriesza.co.za/ibo-state-of-the-industryreport2021/ | opened | Page live; linked PDF returns 404. |
| https://www.berriesza.co.za/wp-content/uploads/2021/08/IBO-2021-Final-interactive.pdf | opened-limited | HTTP 404. |
| https://www.berriesza.co.za/global-state-of-the-blueberry-industry-report-2022/ | opened | PDF link 404. |
| https://www.berriesza.co.za/global-state-of-the-industry-report-2023/ | opened | PDF link 404. |
| https://www.berriesza.co.za/ibo-summit-2025-presentations/ | opened-limited | Page fetched; no PDF links found in static HTML. |
| https://web.archive.org/cdx/search/cdx?url=berriesza.co.za/wp-content/uploads/2021/08/IBO-2021-Final-interactive.pdf | opened | Two captures. |
| https://www.internationalblueberry.org/ibo-summit-sa-presentations/ | opened | 15 PDF links; "Copyright © 2025 IBO". |
| https://www.internationalblueberry.org/wp-content/uploads/2025/10/10.15-Colin-Fain-IBO-Global-Production-Report.pdf | opened | Slide text read. |
| https://www.internationalblueberry.org/wp-content/uploads/2025/10/11.30-Stephen-Taylor-Global-Production.pdf | opened-limited | HEAD 200, 77,101 bytes; not read. |
| https://www.internationalblueberry.org/morocco-berry-conference-2025-presentations/ | opened | 11 PDF links. |
| https://www.internationalblueberry.org/assets/uploads/2023/09/Cort-Brazelton-Colin-Fain_State-of-the-Global-Blueberry-Industry.pdf | opened | PDF (range request). |
| https://www.internationalblueberry.org/library/ | opened | Summit list, including 2023 (Poland). |
| https://www.internationalblueberry.org/terms-and-conditions/ | opened | "In progress". |
| https://eltipografo.cl/2022/11/arandanos-lluvia-y-granizo-de-noviembre-tuvo-minimo-efecto-sobre-la-produccion | opened | ASOEX: frost of 1 Nov, Coihueco; about 900 t. |
| https://www.portalfruticola.com/noticias/2022/11/09/chilecomo-se-han-afectado-los-arandanos-de-nuble-por-las-heladas/ | opened | Frost on 31 Oct and 1 Nov; fruit-set orchards. |
| https://www.teawamutunews.nz/2022/10/how-tunnel-vision-paid-off/ | opened | BBNZ: 1,500-1,800 t lost on 7 Oct; -5 °C. |
| https://agrometeorologia.cl/ | opened | INIA network; Ñuble products listed. |
| https://climatologia.meteochile.gob.cl/ | opened | DMC climate services. |
| https://cliflo.niwa.co.nz/ | opened | Now "CLIDB on DataHub". |
| https://www.ncei.noaa.gov/products/land-based-station/global-historical-climatology-network-daily | opened | GHCNd. |
| https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database | opened | ISD hourly. |
| http://www.georgiaweather.net/ | opened | Georgia AEMN. |
| https://econet.climate.ncsu.edu/ | opened | NC ECONet. |
| https://fawn.ifas.ufl.edu/ | opened | FAWN. |
| https://dev.meteostat.net/ | opened | Meteostat developers. |
| https://mesonet.agron.iastate.edu/request/download.phtml | opened | IEM ASOS download. |
| https://power.larc.nasa.gov/docs/services/api/temporal/daily/ | opened | UTC and LST daily. |

## 10. What was run

- Server, read-only: `ls`, `cat` of the extracted text files, `sha256sum` of the PDFs (all six match the inventory), `grep` of 2022 and 2010 text for licence terms, and one read-only Python query of `met_daily` Tmin for 9 cells.
- Local: Python page parsing and an automated numeric sweep of all 91 records; a Node run of the unchanged `dist/places.js` for 23 test points. Temporary copies live in `/tmp/ibo/`, outside the repository.
- No repository file other than this review was written. No git command, form submission or bulk download was made.
