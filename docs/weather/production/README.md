# Open field + ground production packet — 2026-09-12

Open `production_open_field.html` in a browser (download it; GitHub shows HTML source). `production_open_field.json` holds every site-year row, both classifier results, calendar offsets, ranked risks, sensitivity runs, provenance and the code hash. Method `open-field-production-v1`, source `pipelines/weather/production.py`.

For Waldo, Citra and Papanduva, winters 2011–2025, the packet gives the three outputs the supervisor asked for on 2026-09-11:

1. Production-system hypothesis under Paul's chill-only and multi-feature rules, shown three ways: from multi-year means (R behaviour), as per-year counts, and as a two-thirds majority vote with "Transitional" when no class reaches that share.
2. Assumption-based calendar: chill fulfilment, budbreak, flowering and harvest as per-year dates plus median and p10–p90, reconstructed from the same season anchor used for the offsets.
3. Stage risks ranked by the frequency of winters with an event under Paul's thresholds (chill shortfall, flowering day ≤ −2.2 °C, fruit day ≥ 35 °C, harvest day ≥ 10 mm) with Wilson 95% intervals, plus unranked exposures (dry spell, disease-favourable days, VPD, radiation, GDD).

Primary profile `legacy_paul_v1`: T < 7.2 °C chill, 50 h requirement, 7 °C base, 150 °C·d to budbreak, +14/+35 flowering, +70/+110 harvest. Sensitivity profiles change the definition to 0–7.2 °C and the requirement to 100 h.

Reproduce on the server from `/media/fpt/fpt2/Weather_Claude`:

```sh
env/bin/python code/production.py
```

Output: `reports/production/`. Existing archive only; no downloads.

Verification on 2026-09-12: 73 server tests passed (55 prior plus 18 new). All 90 site-year scenario records for 50 h and 100 h match `../climate_evidence/stage_scenarios.json` exactly (dates, freeze days, harvest rain, heavy-rain days, dry spell). Papanduva mean chill 199.4 h equals the value in `../PAUL_RECONCILIATION.md`. HTML layout inspected in headless Chrome.

What this is not: a validated phenology model, a cultivar recommendation, a soil or tunnel assessment, or a reproduction of Paul's HTML reports. The constants are his provisional assumptions for a UF-type low-chill cultivar. POWER grid temperatures showed a warm minimum bias against stations in 2020, so chill and freeze counts are likely undercounted. The heavy-rain event saturates at 15/15 for all three humid sites; compare heavy-day counts and harvest millimetres across sites, not that frequency.
