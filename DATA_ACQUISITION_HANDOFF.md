# Weather-data acquisition: execution handoff

Date: 2026-09-07. Original execution specification. **Execution has now begun; see [SERVER_RUNBOOK.md](/Users/whiterose/Documents/Weather_Claude/docs/weather/SERVER_RUNBOOK.md) for implemented milestones, live-status commands and remaining work.**

## 1. Assignment and completion boundary

Implement, run, test and document the weather-data foundation for Global Blueberry Recommendation. Start with the existing reference locations, validate the pipeline, and then acquire a bounded global daily archive. Make the work durable across SSH disconnects and agent turns.

This assignment does **not** include building the full web application, training genotype models, publishing private breeding data, or establishing globally validated cultivar recommendations. Those remain governed by [IMPLEMENTATION_PLAN.md](/Users/whiterose/Documents/Weather_Claude/IMPLEMENTATION_PLAN.md) and [REQUIREMENTS.md](/Users/whiterose/Documents/Weather_Claude/REQUIREMENTS.md).

The user has requested this plan before switching to another executor. When instructed to execute it, proceed through safe implementation, downloading, tests and repair without repeatedly asking permission for ordinary in-scope steps. Do not start downloads merely because this planning document exists.

### Fixed decisions

- Remote host: `fpt@10.248.22.167`.
- Remote project root: `/media/fpt/fpt2/Weather_Claude`. `/fpt2` does not exist. The folder was created successfully in the preceding task.
- Local source repository: `/Users/whiterose/Documents/Weather_Claude`, on `main`.
- Keep source development in that repository; transfer only explicitly selected project files to the remote project. Do not overwrite unrelated remote files or clone old branches.
- Analysis baseline: 2011-01-01 through 2025-12-31 inclusive.
- Acquisition includes 2010-01-01 through 2010-12-31 as separate boundary padding. No partial 2026 data in baseline statistics.
- Initial locations: the 13 reference entries in Paul's R workflow plus Papanduva: 14 named sites. Source-grid deduplication may reduce the number of distinct weather cells.
- Global backbone: **NASA POWER daily weather at each variable's published native grid**, acquired using the public bulk datastore. Do not upsample it into invented higher-resolution observations.
- Hourly layer: NASA POWER temperature and dewpoint for pilot sites initially; extend to actual requested sites through the same cache. Copernicus supplies a separately versioned optional comparison/enhancement when authorized credentials are available.
- Do not download global satellite imagery or full global soil rasters in this assignment. The original exclusion of global hourly weather was lifted by the user on 2026-09-21 for a bounded land-only temperature/dewpoint cache (`global_hourly.py`, ≈ 29 GB); no other hourly variables are authorized.
- No paid services, new cloud compute, system-wide package changes or public server exposure.

## 2. Access: what is automatic and what needs the user

| Service | Account/key requirement | Executor action |
|---|---|---|
| NASA POWER point API | Public access; no personal key needed | Write and run the client |
| NASA POWER public bulk datastore | Anonymous access; no AWS account needed | Read documented metadata and download required chunks only |
| Copernicus CDS | User account, personal access token, accepted dataset terms | Check configuration without exposing it; use only after the user completes setup |
| FAWN/public station archives | Use public files where available | Fetch relevant records with flags and source attribution |
| SoilGrids | Public map access; service availability varies | Optional pilot subsets, not a core weather completion dependency |

The APIs already exist. The executor writes clients to use them; it cannot manufacture someone else's API token or account. Never paste credentials into code, manifests, logs, Git or this plan. Do not automatically accept terms or create accounts in the user's name.

NASA's registry documents anonymous access to the `nasa-power` bucket. The official POWER guidance recommends its analysis-ready Zarr datastore for direct access. Sources: [NASA POWER open-data registry](https://registry.opendata.aws/nasa-power/), [POWER bulk-access documentation](https://power.larc.nasa.gov/docs/services/aws/).

Copernicus documents account/token configuration and manual acceptance of dataset terms. If `/home/fpt/.cdsapirc` exists, report only presence, permissions and whether authentication works; never print its contents. If it is absent or unauthorized, continue NASA work and record the enhancement as `blocked_credentials`. Source: [CDS API setup](https://cds.climate.copernicus.eu/how-to-api).

## 3. Data products to produce

### A. Pilot daily archive — mandatory

All 14 locations, acquisition period 2010–2025. Retain the eight canonical daily variables below, subject to a verified source-variable mapping.

| Canonical field | Canonical unit | Intended use |
|---|---|---|
| `tmin_c` | degrees Celsius | Daily cold exposure |
| `tmax_c` | degrees Celsius | Daily heat exposure |
| `tmean_c` | degrees Celsius | Thermal-time indicators |
| `precip_mm` | mm/day total | Rain, wet days and dry spells |
| `rh_mean_pct` | percent | Humidity context |
| `shortwave_mj_m2_day` | MJ/m²/day total | Light exposure |
| `wind_mean_m_s` | m/s, height recorded | Wind context |
| `dewpoint_mean_c` | degrees Celsius | Moisture context and cross-checks |

Likely POWER parameter names include `T2M_MIN`, `T2M_MAX`, `T2M`, `PRECTOTCORR`, `RH2M`, `ALLSKY_SFC_SW_DWN`, `WS2M` and `T2MDEW`. These are a discovery checklist, **not permission to assume that every API field maps directly to a bulk-store field**. Verify availability, height, units, day convention, derivation and version for each. If a required field is unavailable, document it and use a proven equivalent from the same product family only through an explicit mapping.

Do not derive a missing mean temperature from `(min + max)/2` without labeling it as a separate derived quantity. Do not substitute uncorrected rainfall for corrected rainfall under the same variable name. Never assume API community units equal Zarr native units.

### B. Pilot hourly archive — mandatory NASA path

For the same sites and dates, obtain hourly air temperature and dewpoint from POWER after checking parameter metadata. Preserve UTC timestamps where offered and explicit conversion to local biological dates. If the source is local solar time, preserve that fact; do not label it UTC.

This supports a tested chill calculation and cold/heat duration analysis, but remains gridded reanalysis rather than observed canopy weather. Daily humidity alone cannot support an hourly wet-warm exposure count.

### C. Global daily backbone — mandatory after pilot gates

Acquire the same daily fields globally at their actual source grids. Retain meteorological and solar grids separately. A global rectangular array may retain ocean cells for efficient storage; identify land/offshore applicability in the query layer. Do not duplicate full arrays for every requested location.

Use bulk Zarr reads organized by actual source chunk layout, not tens of thousands of point API calls. Avoid rereading the same remote chunk for adjacent regions or years. Retain global daily history sufficient for subsequent phase-window calculations, not merely monthly normals.

This is global **weather coverage**, not a promise of field-scale precision, resolved microclimates, hourly coverage everywhere, or globally supported genotype rankings. Small islands/coasts may need an exact-point enhancement or an explicit unsuitable-grid response.

### D. Quality-controlled climate demonstration — mandatory

Produce a repeatable report for Papanduva, Citra, Waldo and diverse global probes containing coverage, annual/monthly weather summaries, chill where hourly data exist, illustrative frost/heat counts and dry spells.

A harvest-rain or flowering-freeze calculation must identify its stage-window source. Until genotype phenology is supplied, use a clearly provisional reference calendar; do not present it as a validated cultivar calendar. No invented candidate rankings.

### E. Copernicus comparison — conditional enhancement

If access exists, request AgERA5 daily and ERA5-Land hourly temperature/dewpoint for the pilot panel. Compare them separately with NASA and available stations. Do not replace the NASA global backbone silently; issue a source-selection report and retain profile-specific provenance.

Both datasets have point time-series products. Sources: [AgERA5 time series](https://cds.climate.copernicus.eu/datasets/sis-agrometeorological-indicators-timeseries?tab=overview), [ERA5-Land time series](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-timeseries?tab=overview).

### F. Soil pilot — optional, separately reported

For ground scenarios, test limited pH, organic carbon and texture subsets with depth and uncertainty. SoilGrids REST is currently documented as paused; use documented WCS/WebDAV alternatives if functioning. Do not retry the paused endpoint indefinitely. No global soil download and no claims of measured drainage or disease. Source: [SoilGrids access](https://docs.isric.org/globaldata/soilgrids/).

## 4. Durable layout and implementation contracts

Use an isolated Python environment under the remote project. A minimal implementation can use standard-library HTTP/SQLite plus pinned NumPy, pandas, PyArrow, xarray, fsspec/s3fs, Zarr and test dependencies as actually required. Verify compatibility with the inspected source format before locking versions. Avoid installing everything in Paul's monolithic R script just to retrieve weather.

Proposed local code paths, to be created by the executor:

```text
pipelines/weather/           CLI, source adapters, normalization, QC, extraction
config/weather/              site registry, source mapping, limits, profiles
tests/weather/               known-answer, retry, integration and parity tests
docs/weather/                methods, source decisions, remote runbook
```

Remote runtime layout, all under `/media/fpt/fpt2/Weather_Claude`:

```text
code/                        explicitly deployed source snapshot
env/                         isolated runtime
config/                      non-secret run configuration
data/raw/                    immutable pilot responses / bounded source cache
data/normalized/pilot/       daily and hourly Parquet
data/normalized/global/      chunked daily arrays at source grids
data/derived/                versioned indicators and point extractions
state/jobs.sqlite            durable work queue, attempts, checksums, leases
state/source_inventory.json metadata snapshot / source identifiers
logs/                        redacted structured logs
reports/                     QC, benchmarks, coverage and completion report
```

Never use `/tmp`, the OS root disk or the SSH user's home for bulk temporary weather files. Explicitly route temporary files and caches to the project drive. Do not write credentials under this tree.

### Job record

Include dataset/profile, version, variable group, spatial chunk or source cell, time interval, time convention, request hash, status, attempts, next retry, lease owner/expiry, expected/fetched bytes, checksum, source revision metadata and error category.

Statuses: `pending`, `running`, `retry_wait`, `downloaded`, `validated`, `published`, `quarantined`, `blocked_credentials`, `failed_terminal`. Acquisition success alone is not validation success.

### Normalized point record

Include site ID, requested coordinate, source coordinates/cell per variable group, source/profile, date or timestamp, canonical units/values, validity flags, raw reference, transformation version and baseline/padding indicator. Preserve exact requested coordinates independently of shared source-cell caches.

### CLI contract to implement

These commands are **planned interfaces, not currently existing commands**:

```text
weather preflight
weather discover-sources
weather plan --scope pilot
weather run --scope pilot
weather validate --scope pilot
weather benchmark-bulk
weather plan --scope global
weather run --scope global
weather validate --scope global
weather extract --latitude ... --longitude ... --profile ...
weather status
weather report --final
```

`plan` writes a finite manifest without downloading weather payloads. `run` executes only that manifest. `status` is read-only. Exit codes distinguish success, retryable failure, data-quality failure and missing authorization. A supervisor script may orchestrate commands only after these individual steps are tested.

## 5. Execution phases and gates

### Phase 0 — preflight, no bulk transfer

1. Read this handoff, the weather-relevant sections of the project plan, and any applicable `AGENTS.md`.
2. Inspect the dirty worktree and preserve supplied reports/R code. Do not commit or push unless separately requested.
3. Connect to the specified host. Use the password only through secure authentication; never include it in scripts or persist it. If connectivity fails, diagnose the specific route/SSH port and report a genuine network blocker.
4. Confirm `findmnt`/filesystem identity for the project path. A missing mount must not redirect bulk writes onto `/`.
5. Record free disk, RAM, CPU, existing relevant runtimes and project contents. Do not inspect unrelated user data.
6. Check outbound HTTPS access and read source metadata. Check whether CDS configuration exists without displaying secrets.
7. Write a preflight report and establish the project-specific environment, limits and state database.

Gate: correct writable mount; safe runtime; public metadata reachable; no unauthorized changes.

### Phase 1 — source discovery and software tests

1. Extract the 13 named sites from the `uf_sites` table in Paul's R file and the target coordinate from configuration. Do not source the full R workflow. Validate 14 unique site IDs and latitude/longitude ranges.
2. Inspect the documented `nasa-power` bucket/catalog and current Zarr stores. Discover actual **daily/hourly**, not monthly, datasets. Save metadata snapshots.
3. Resolve variable mappings, units, source grids, chunk shapes, calendars, time standards, fill values and available non-fill dates. A Zarr time axis can extend into future placeholder dates; array length is not evidence that observations exist. Source: [POWER bulk Python tutorial](https://power.larc.nasa.gov/docs/tutorials/service-data-request/aws/).
4. Build adapters, manifests, normalizers, atomic writes and retry logic, using small synthetic fixtures for unit tests. Synthetic fixtures must remain labeled and outside real-data releases.
5. Test serialization, checksums and crash recovery before lengthy acquisition.

Gate: mappings are explicit, required fields resolved, tests pass, no guessed source URLs or date validity.

### Phase 2 — small real-data smoke test

Download Citra and Papanduva for a short interval crossing a relevant boundary, then one complete leap year (2020). Test daily API and bulk extraction for identical cells, product versions and time definitions. Add a short hourly sample.

Verify temperature/rain/radiation units, duplicate/missing dates, source-cell mapping and API/bulk parity after justified transformations. Investigate differences before increasing scope; do not paper over them with a generous numerical tolerance. Establish variable-specific tolerances based on representation precision and transformation behavior.

Gate: successful scientific/technical parity explanation, known-answer checks, measured transfer/memory and no invalid zeros.

### Phase 3 — complete pilot acquisition and quality report

Download 2010–2025 daily and hourly pilot data with rate-limited requests and cell deduplication. Produce one matrix of site × variable × period completeness. Confirm baseline counts: 5,479 dates for 2011–2025; 5,844 dates including the 2010 buffer, for a standard Gregorian daily calendar.

Check weather against available relevant station observations after time alignment and station metadata review. Station disagreement measures source limitations; it is not necessarily a downloader defect. Missing suitable stations must be reported, not replaced with fabricated validation. FAWN is a useful Florida starting point: [FAWN archives](https://fawn.ifas.ufl.edu/data/).

Calculate a small set of weather indicators with isolated reviewed functions. Compare with Paul only under matching sources/periods/thresholds; his older report values need not match a 2011–2025 baseline.

Gate: every planned pilot job has an audited outcome, all usable records meet schema/QC, critical scientific differences are explained, no hidden data repair. An unavailable mandatory field or broken transformation blocks expansion. A genuine source gap is flagged rather than retried forever.

### Phase 4 — diverse geographic probes and global dry run

Build a deterministic probe registry covering both hemispheres, wet/dry climates, warm/cold winters, elevation contrasts, coastlines, the antimeridian and high latitudes. Use approximately 30–50 points. Clearly distinguish these software/source probes from actual breeding-trial sites.

Test points across Florida/Georgia, southern Brazil, Chile, western Europe, Morocco, India, East Africa, Australia and New Zealand, plus edge cases. Use a documented public land mask/coastline source or validated source mask; record its version. An offshore request must not quietly become an inland farm.

Benchmark a few representative global source chunks, including different variable groups and periods. Estimate unique remote bytes, local normalized bytes, quality-mask overhead, temporary/cache requirements, runtime and memory using actual chunk geometry. Count all planned chunks and bound download amplification.

Write `global_download_plan.json` and a human-readable estimate. Proceed automatically only within Section 7 resource limits and after mandatory pilot gates pass. No need to seek another approval just because the normal bounded global phase is ready.

### Phase 5 — global daily acquisition

Consume the finite global manifest with the durable worker. Save provenance, validate each chunk and publish only validated outputs. Use lazy chunked reads; never call `.load()` or convert to a dataframe on an unbounded global dataset.

Keep variables on their source grids. Do not equate native source resolution with interpolated output pixel spacing. Extract a point using a documented variable-specific lookup and preserve lookup distance and grid identity.

If a field cannot be retrieved through the verified bulk product, investigate its documented equivalent or a bounded provider-supported alternative. Do not silently launch a global point-API crawl, omit the field, or derive a non-equivalent replacement. Report a blocker when no valid bounded path exists.

Gate: manifest complete; every chunk validated or accounted for as an explicit source gap; no outstanding unexplained transfer failures; coverage and QC reports generated. Source gaps remain gaps, not invented data.

### Phase 6 — end-to-end audit and handoff

1. Extract the original 14 sites from the global backbone and compare against the pilot results under identical profiles.
2. Test the geographically diverse probes and edge cases. Generate human-readable reports for Papanduva, Citra and Waldo.
3. Interrupt/restart a bounded test worker and prove completed files are not downloaded again.
4. Verify date/variable/spatial coverage, checksums, artifact versions, resource usage and no credentials in project outputs.
5. Produce a read-only coordinate-extraction command and documentation for downstream risk/model work.
6. Produce the completion report, limitations, source attribution and exact reproduction commands.

Do not declare completion merely because a background process started, files exist or the queue is empty after failures. Use Section 9.

## 6. Quality rules and required tests

- Full expected date/time grid; duplicates rejected, missing values explicit.
- Preserve precipitation/temperature fill values as missing, not zeros or extreme observations.
- Check `tmin <= tmean <= tmax` with a documented rounding tolerance; investigate violations.
- Check precipitation nonnegativity, RH bounds, valid temperature/radiation/wind domains, without replacing plausible climate extremes with averages.
- Preserve local-solar, UTC and local-day distinctions. Test New Year, leap day, dateline and cross-year crop seasons. No undocumented DST shifts.
- Global polar low-light or snow conditions may be real. Do not diagnose them as acquisition failures solely because they are unsuitable for blueberries.
- For bounded chill hours, test `0 <= T <= 7.2°C` with an explicitly chosen boundary convention. Keep below-7.2-only counts as a different metric. Validate the Dynamic Model against an established implementation before using it.
- No concatenation across missing hourly gaps in stateful calculations. No freeze-free claim from an incomplete cold-risk window.
- Radiation in kWh/m²/day versus MJ/m²/day differs by a factor of 3.6; in J/m²/day versus MJ/m²/day by one million. Apply conversion only after confirming source units.
- Wind height is part of the variable identity. Daily mean dewpoint and daily mean RH need not reproduce each other exactly under nonlinear conversion.
- Test API/bulk equivalence at matching source cells and profile versions. Cache keys include source, period, variable group, transformation and time standard.
- Test corrupt payloads, HTML error pages with HTTP 200, partial writes, throttling, timeouts, retry exhaustion, mount loss, disk quota and concurrent duplicate work.
- Invalid derived metrics return `null` and a reason. Do not replace absence with a benign risk classification.

Use coverage as a measurable diagnostic. A 95% threshold can be a provisional warning threshold, but it does not prove valid extreme-event estimation. Publish full coverage flags and make stage-specific admissibility explicit.

## 7. Resource and failure limits

These are conservative project defaults, not claims about institutional policy. Use lower source/institutional limits whenever applicable.

| Resource | Initial bound |
|---|---|
| Point API concurrency | 1 outstanding request per provider; at least 2 seconds between completed POWER requests |
| Bulk transfer concurrency | 2 concurrent reads initially, with any library-level parallel reads bounded too |
| Worker RAM target | 8 GiB; measure actual peak and reduce chunk size if exceeded |
| Project pilot disk ceiling | 10 GiB before global-phase authorization in the manifest |
| Entire acquisition disk ceiling | 200 GiB, including caches, temporary files and retained copies |
| Global transfer ceiling | 500 GiB measured/planned remote bytes |
| Drive free-space floor | Preserve at least 20% of the measured filesystem capacity; use the stricter limit alongside project quota |
| Retryable request attempts | Maximum 5 attempts per work item, with exponential backoff/jitter and `Retry-After` respected |
| Persistent source outage | Pause that provider after repeated failures across different items; do other independent work |

Track attempted/repeated transfer bytes, not just final file size. If exact HTTP byte accounting is unavailable, use conservative chunk-size accounting and document it. Do not claim precise network usage from normalized file size.

The global native-grid daily product should be far smaller than a global hourly high-resolution archive, but the exact size depends on metadata/chunks. A rough uncompressed-value calculation can be included in the dry run; it is not a substitute for measured transfer/cache estimates.

Pause and request direction if projected or actual requirements exceed limits, paid access is required, a mounting/permission change needs administration, or safe scientifically valid alternatives are exhausted. Do not delete the user's files or grow the scope to solve capacity issues.

Use a project-specific lock/lease to prevent two executors from running duplicate global jobs. A mounted path must remain verified before writes after restart. Use atomic `.partial` to validated-final publication on the same filesystem; quarantine corrupt downloads within the project rather than overwriting good artifacts.

## 8. Looping and persistence

The server worker, not the chat model, performs the download loop. Run it under an available durable mechanism such as a project-specific `tmux` session or existing job manager, with logs and SQLite state. Verify it remains running after the launching SSH session exits.

The executor's loop is:

```text
read persisted state and recent errors
    → select the next unmet gate
    → implement or run its bounded work
    → test and inspect results
    → repair defects with regression tests
    → update state and reports
    → advance only when the gate passes
```

Continue while meaningful authorized work remains. Retry temporary faults under the fixed policy; do not loop endlessly on authentication, an unavailable source or the same failed assumption. Continue independent NASA tasks if Copernicus is blocked.

At an agent-turn/context boundary, leave progress, current worker identity, resume command and next action on disk. Use the product's available follow-up/monitoring mechanism if asked to resume later; never promise a stopped chat will keep thinking. Do not create duplicate workers or expose the SSH password in scheduled prompts.

Record overall status independently from optional enhancements:

```text
core_weather: pending | running | complete | blocked
copernicus_comparison: pending | running | complete | blocked_credentials | blocked_source
soil_pilot: not_started | running | complete | blocked_source
```

“Core complete, Copernicus blocked on user setup” is acceptable and honest. “Everything complete” is not acceptable while conditional requested work is blocked. Actual interruption is not a successful completion.

## 9. Definition of completion

Core weather acquisition is complete only when all are true:

1. The versioned site registry contains the 14 intended locations with source provenance.
2. The pilot daily and hourly acquisition manifests are fulfilled, with source missingness explicit and no unexplained mandatory-job failures.
3. The global daily manifest covers all requested dates, variables and source-grid chunks, with an audited gap report and no silently omitted chunks.
4. Unit, integration, API/bulk parity, geographic edge-case and resume tests pass.
5. QC identifies which records/metrics are usable; quarantined invalid data are not served as valid observations.
6. Pilot/global extraction comparisons pass or have an explicit scientifically justified difference, not an unexplained tolerance increase.
7. The extraction CLI returns reproducible weather for a land coordinate, preserving actual source location and resolution; unsupported/offshore cases are explicit.
8. Papanduva/Citra/Waldo demonstration reports exist and distinguish baseline from padding, measured/station observations from gridded estimates, and provisional windows from validated phenology.
9. The final report lists datasets, versions, dates, variables, coverage/gaps, storage, transfer estimate, source limitations, test results, run commands and unresolved optional dependencies.
10. No private breeding predictions, invented trial outcomes, unapproved cloud costs or credentials have been published.

The final handoff must say exactly what is ready for downstream modeling. A fully downloaded dataset with a known climate-source bias is not a validated crop model. An array containing missing cells is not necessarily a failed transfer, but the application must retain the missingness and decline unsupported calculations.

## 10. Short executor prompt

> Read `DATA_ACQUISITION_HANDOFF.md` fully and implement its weather-data assignment. Develop in the existing local repository and run downloads on `fpt@10.248.22.167` under `/media/fpt/fpt2/Weather_Claude`. Preserve existing files and do not use old application branches. Start with preflight and tested NASA pilot acquisition, then proceed automatically to the bounded global daily bulk-download phase only after the specified gates pass. Implement a durable resumable worker, QC, point extraction and final reports. Keep executing and repairing until the core completion criteria pass or a genuine external blocker is reached. Never manufacture credentials, silently change datasets/units, download global hourly data, exceed resource caps, or declare completion merely because a job was launched. Copernicus is conditional on authorized account setup; keep NASA work moving if it is unavailable. Record all progress on disk so execution survives context changes and SSH disconnects.
