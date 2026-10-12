# Evidence jobs runbook

Evidence jobs download source files (insurance losses, storm reports, station data, trade and survey tables), keep a raw copy with a manifest, and build small derived tables for the app and for review. They run on the lab server as systemd user timers. They never run in tmux.

Code lives in `pipelines/evidence/` in Git and is deployed to `code/evidence/` on the server. Every command below runs from the deployed code folder:

```sh
cd /media/fpt/fpt2/Weather_Claude/code
TMPDIR=/media/fpt/fpt2/Weather_Claude/tmp/evidence PYTHONDONTWRITEBYTECODE=1 ../env/bin/python -m evidence <command>
```

## Layout

| Path (under `/media/fpt/fpt2/Weather_Claude`) | What it holds |
|---|---|
| `code/evidence/runner.py` | Runner: guards, lock, downloads, state, logs, CLI |
| `code/evidence/adapters/<module>.py` | One adapter per job: `JOB`, `plan(ctx)`, `parse(ctx, assets)` |
| `code/evidence/adapters/__init__.py` | Job id to module map (`MODULES`) |
| `code/evidence/registry.json` | Sources used by the jobs: id, publisher, URL, licence or terms, allowed use, cadence, languages |
| `data/evidence/raw/<job>/<file>` | Latest downloaded copy of each file |
| `data/evidence/raw/<job>/<file>.manifest.json` | URL, fetch time, SHA-256, bytes, ETag, Last-Modified, HTTP status, previous SHA-256 |
| `data/evidence/derived/<job>/<table>.parquet` | Derived tables |
| `data/evidence/derived/<job>/_run_manifest.json` | Tables and assets of the last run that parsed |
| `state/evidence/<job>.json` | Last run, last success, last change, per-request status, adapter state |
| `state/evidence/<job>.lock` | Per-job `flock` file |
| `logs/evidence/<job>.jsonl` | JSON lines log, rotated at 20 MiB, 5 old files kept |
| `logs/evidence/<job>.stdout.log` | Output of timer runs (one summary line per run) |
| `tmp/evidence/<job>/` | Temporary files. The runner sets `TMPDIR` to `tmp/evidence/` |

Setting `EVIDENCE_ROOT=/some/folder` makes the runner use that folder instead of the project root. Tests do this.

## Commands

| Command | Effect |
|---|---|
| `list` | Jobs, schedules and descriptions. A job whose module fails to import shows as unavailable; the others still work. |
| `status` | Disk guards, then one line per job: last outcome, last run, last change, stored assets, raw size, open failures, tables and row counts. `[running]` means the lock is held. |
| `status --json` | The same as JSON, with error text and the failing request keys. |
| `run <job>` | Run one job now. |
| `run <job> --dry-run` | Show the planned requests and which are already stored. No network and no writes. |
| `run <job> --max-requests N` | Stop after N network requests. The rest are skipped and the run ends as partial. |
| `run <job> --force` | Parse even if nothing changed (for example after an adapter fix). Downloads stay conditional. |
| `systemd-units --out DIR` | Write `blueberry-evidence@.service` and one `blueberry-evidence-<job>.timer` per scheduled job. |

Exit codes: 0 for `ok` or `unchanged`, 2 for `partial` (a required request failed or was skipped), 1 for `fatal` (guard, lock, plan or parse error, unknown job).

## What a run does

1. Checks the guards. If any fails, it prints the reason and exits 1 before writing anything.
2. Takes the job lock. If another run holds it, it exits 1.
3. Calls `plan(ctx)` and fetches each request:
   - sends `If-None-Match` and `If-Modified-Since` from the stored manifest, so unchanged files cost one small request;
   - streams to a hidden `.partial` file next to the target, with a per-file byte cap and a per-run byte cap, then renames it into place;
   - checks magic bytes for `.zip`, `.xlsx`, `.gz`, `.pdf` and `.parquet`, which stops HTML error pages being stored as data;
   - waits at least 2 seconds between requests to the same host;
   - retries timeouts, connection errors, 429 and 5xx up to 4 attempts in total, honouring `Retry-After` (a wait above 10 minutes ends the attempts for this run). Any other 4xx fails that request at once.
4. Calls `parse(ctx, assets)` only if an asset changed since the last successful parse, or with `--force`. A file that was downloaded by a run that later failed still counts as changed next time.
5. Writes tables atomically and records them in `_run_manifest.json`.
6. Saves state. Adapter state and parse records are saved only when the run is not fatal.

## Guards

| Guard | Limit |
|---|---|
| Root filesystem free space | at least 10 GiB and at least 5% |
| Project drive free space | at least 100 GiB |
| `data/evidence` total size | at most 25 GiB |

Guards are checked before the run, before each request, every 64 MiB during a download, and before each table write. A guard failure during a run ends it as fatal. The runner never deletes data to make room.

## Jobs and schedules

| Job | Schedule | Source | Table |
|---|---|---|---|
| `rma-col` | monthly | USDA RMA cause of loss with month of loss, `colsom_<year>.zip`, 1989 onward | `rma_col_blueberry` |
| `rma-sobtpu` | monthly | USDA RMA summary of business by type, practice and unit, `sobtpu_<year>.zip`, 1999 onward | `rma_sobtpu_blueberry` |
| `storm-events` | monthly | NOAA Storm Events details CSVs, 1996 onward, newest version per year | `storm_events_selected` |
| `ghcnh-stations` | monthly | NOAA GHCNh hourly station files, 2010 onward, for stations near every app pin | `station_meta`, one `hourly_<station>` table per station |
| `station-truth` | monthly, day 3 (derived from `ghcnh-stations`) | GHCNh tables plus the NASA POWER daily archive, read only | bias and frost-detection tables, `summary.json` |
| `odepa-catastro` | quarterly | CIREN-ODEPA orchard census CSVs (CKAN, CC BY), 1999 onward | `catastro_blueberry_blocks`, `catastro_blueberry_summary` |
| `odepa-exports` | monthly | ODEPA foreign-trade CSVs (CKAN), 1998 onward | `exports_blueberry_monthly`, `exports_blueberry_region_monthly` |
| `comext-blueberry` | monthly | Eurostat Comext DS-045409, CN 08104050 (highbush blueberry and American cranberry together), 2010 onward | `comext_blueberry_monthly` |
| `senamhi-arandano` | weekly | SENAMHI dekadal blueberry bulletins (PDF text through `pdftotext`, which must stay installed) | `senamhi_bulletins`, `senamhi_stage_sentences` |

Timer times: `daily` 04:30, `weekly` Monday 04:30, `monthly` day 1 at 04:30, `quarterly` 1 January, April, July and October at 04:30, `yearly` 1 January at 04:30, all server local time. Derived jobs run two days later (six hours later for `daily`), so they read that period's downloads. Every timer adds a random delay of up to 1 hour so jobs do not start together, and `Persistent=true` runs a missed job after downtime. `manual` jobs get no timer.

### Table notes

- `rma_col_blueberry`: commodity code 0012 rows with the 30 fields of `COL_Summary_of_Business_with_Month_All_Years.pdf`, typed, plus `fips`, `source_file` and `cause_family`. Crosswalk: 41 frost and 42 freeze to `freeze`; 43 cold winter and 44 cold wet weather to `cold`; 31 to `excess_moisture`; 21 to `hail`; 12 heat and 62 hot wind to `heat`; 11 to `drought`; 45 to `chill_shortfall`; 81 to `disease`; 61, 63 and 92, plus 46 tropical storm, 47 hurricane and 64 tornado (found in the data), to `wind_storm`; everything else to `other`. Files before about 1990 leave the plan abbreviation, cause description and year of loss blank. `month_of_loss` 0 means the month was not reported.
- `rma_sobtpu_blueberry`: commodity code 0012 rows with the 27 fields of `SOBTPU_External_All_Years.pdf`, plus `fips`, `insured_acres` (the reporting amount when the unit is acres) and `source_file`. `coverage_level` is a fraction; early files give it as a percent and are converted.
- `storm_events_selected`: FL, GA, SC, NC, AL, MS, NJ, MI, ME, OR, WA and CA; event types Frost/Freeze, Hail, Heavy Rain, Flash Flood, Excessive Heat, Heat, Tropical Storm, Hurricane (Typhoon), Hurricane, Extreme Cold/Wind Chill and Cold/Wind Chill. Times are local standard time (`begin_local`, `end_local`) with `cz_timezone` as published and `utc_offset_hours`; `begin_utc` and `end_utc` apply that offset. Damage strings such as `18.9M` become US dollars; an empty or unreadable value is null, not zero. `county_fips` is filled only for county records (`cz_type` C), because zone numbers are not county codes. `mentions_blueberry` is true when either narrative contains "blueberr".

## Reading status

```sh
../env/bin/python -m evidence status
```

- `outcome` `ok`: something changed and was parsed. `unchanged`: every file answered 304 or had the same bytes. `partial`: look at `open_failures` in `status --json`, then at `logs/evidence/<job>.jsonl` (`request_failed`, `request_terminal` and `request_retry` events). `fatal`: `last_error` in `status --json` gives the reason.
- `last change` is the last run that downloaded new bytes or parsed.
- A job whose last success is older than twice its schedule needs a look.

Useful log queries:

```sh
grep -h '"event": "run_end"' ../logs/evidence/rma-col.jsonl | tail -3
grep -h -E 'request_(failed|terminal)' ../logs/evidence/*.jsonl | tail -20
```

## Backfill

The first run of a job is the backfill. It downloads every planned file:

```sh
df -h /    # keep at least 10 GiB free on the root disk
../env/bin/python -m evidence run rma-col --dry-run | less
../env/bin/python -m evidence run rma-col
../env/bin/python -m evidence run rma-col    # second run should be "unchanged" and fast
```

To spread a large backfill over several sessions, use `--max-requests N` and repeat the command until the outcome is `ok` or `unchanged`. Stored files are not downloaded again.

To rebuild tables after changing an adapter, deploy it and run with `--force`. Downloads stay conditional, so this does not refetch unchanged files.

## Adding a job

1. Pick the source id from `docs/research/2026-10-11/source_catalog.json` and add an entry to `pipelines/evidence/registry.json` (id, name, publisher, url, licence_or_terms, allowed_use `private_research` or `public_display_ok`, cadence, languages, job_ids).
2. Write `pipelines/evidence/adapters/<module>.py`:

   ```python
   from ..runner import Request

   JOB = {'id': 'my-job', 'source_ids': ['catalog-id'], 'schedule': 'monthly',
          'description': 'one line', 'max_bytes_per_run': 500_000_000, 'derived_only': False}

   def plan(ctx):
       return [Request('file_2024', 'https://example.org/file_2024.zip', max_bytes=50_000_000)]

   def parse(ctx, assets):
       frames = [read(a.path) for a in assets.values() if a.path is not None]
       ctx.write_table('my_table', pd.concat(frames))
       return {'rows': ...}
   ```

   - `parse()` receives every planned asset, changed or not, so it can rebuild the whole table. `missing` assets have no path; `failed` assets keep the previous copy if one exists.
   - Request keys and table names use letters, digits, `_`, `.` and `-`. `filename` may include a subfolder but not `..`.
   - `ctx.fetch(Request)` inside `plan()` fetches a listing or index first (see `storm_events.py`).
   - Derived jobs set `derived_only: True` and `inputs: ['other-job']`, return `[]` from `plan()`, and read tables with `ctx.read_table('other-job', 'table')`. They parse when an input job's `_run_manifest.json` changes. Without `inputs` they parse on every run.
   - `ctx.state` is a dict saved after non-fatal runs. Keep it small.
3. Add the job id and module to `MODULES` in `adapters/__init__.py`.
4. Add `tests/evidence/test_evidence_<name>.py` with small fixtures in `tests/evidence/fixtures/` (under 200 KB each, no network).
5. Deploy, run the backfill by hand, then regenerate and install the units.

## Installing or updating timers (coordinator)

The generated units are in `ops/systemd/`. Regenerate them after adding or rescheduling a job:

```sh
../env/bin/python -m evidence systemd-units --out ../tmp/evidence/units
```

Install as the `fpt` user (lingering is enabled). The account also runs other projects' user units (`ceres-*`, `weed-*`), so this project's units all start with `blueberry-`; never edit or restart units without that prefix.

```sh
mkdir -p ~/.config/systemd/user
cp /media/fpt/fpt2/Weather_Claude/ops/systemd/blueberry-evidence@.service /media/fpt/fpt2/Weather_Claude/ops/systemd/blueberry-evidence-*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now $(cd /media/fpt/fpt2/Weather_Claude/ops/systemd && ls blueberry-evidence-*.timer)
systemctl --user list-timers 'blueberry-evidence-*'
```

Run one job through systemd to test the unit: `systemctl --user start blueberry-evidence@rma-col.service`, then check `logs/evidence/rma-col.stdout.log`. To pause a job, `systemctl --user disable --now blueberry-evidence-<job>.timer`.

The service is `Type=oneshot` with `Nice=10`, `IOSchedulingClass=idle`, `TimeoutStartSec=4h` and `ConditionPathIsMountPoint=/media/fpt/fpt2`, so nothing runs if the project drive is not mounted. systemd does not start a second instance while one is active, and the runner lock covers manual runs.
