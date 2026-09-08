# Supervisor climate evidence demonstration

Open `climate_evidence.html` in a browser. Self-contained and offline: six SVG charts, coverage, hemisphere-aligned seasons, annual tables and limitations. GitHub's file view shows HTML source; download the file to view the report.

Companion `climate_evidence.json` contains derived summaries and provenance, not bulk weather: three locations, 15 annual rows and 180 monthly rows each. Method: `climate-evidence-v1`.

From `/media/fpt/fpt2/Weather_Claude` on the server, reproduce with:

```sh
env/bin/python code/evidence_report.py
```

Output: `reports/climate_evidence/`. No new weather downloads. Source: `pipelines/weather/evidence_report.py`; deploy into server `code/` when changed.

35 tests passed on 2026-09-08, including six new tests of inclusive chill thresholds, missing hours, cross-year/leap seasons, dry-spell runs, suspect precipitation, missing dates and duplicates. The report's opening layout and charts were visually inspected using headless Chrome.

Chill uses UTC Nov–Feb reference winters in Florida and May–Aug in Brazil; 2010 padding supports Florida's 2011 winter. Neither is a validated cultivar calendar. Do not compare counts with Paul's older results without matching source, years, season and definition. Missing or suspect windows are not valid risk estimates. No cultivar recommendation, bias correction, crop damage or phenology prediction is provided.

Broader global-probe demonstrations, remaining compressed-source corruption tests and the final weather-core audit remain unfinished.

## Exploratory seasonal comparison — 2026-09-08

Open `stage_scenarios.html` for the complementary 50-hour versus 100-hour chill-trigger comparison; `stage_scenarios.json` includes all 90 scenario records, exact dates, metric-specific paired denominators and provenance. Reproduce on the server with `env/bin/python code/stage_scenarios.py`; output is `reports/stage_scenarios/`. This uses Paul-derived assumptions audited in `../PAUL_RECONCILIATION.md`, with explicit UTC timing and stricter completeness handling, not a reproduction of his original reports.

Mean harvest rainfall changes (100 minus 50 hours): Citra +44.4 mm, Waldo +35.7 mm (15 paired winters each), Papanduva −12.9 mm (13 paired winters). Papanduva 2015 and 2023 fail the 100-hour trigger and are excluded from paired means, not assigned zero exposure. These are uncalibrated calendar sensitivities, not cultivar suitability scores. Production dry spells start at the chill-window opening, so they need not change when the chill trigger changes.

45 server tests passed, including known-answer inclusive stage lengths, strict chill boundary, unmet requirements, missing hourly/GDD data, flagged rainfall, archive truncation and paired-denominator handling. No new downloads or original weather modifications.
