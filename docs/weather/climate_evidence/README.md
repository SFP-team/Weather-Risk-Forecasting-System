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
