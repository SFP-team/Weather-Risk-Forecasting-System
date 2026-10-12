"""Scheduled evidence jobs: guarded, conditional, resumable downloads plus small adapters.

Run from the deployed code folder: ../env/bin/python -m evidence <list|status|run|systemd-units>.
Adapters live in evidence/adapters and expose JOB, plan(ctx) and parse(ctx, assets).
"""
from __future__ import annotations

import argparse
import copy
import fcntl
import hashlib
import importlib
import json
import math
import os
import re
import shutil
import sys
import tempfile
import time
import traceback
import uuid
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path, PurePosixPath
from types import ModuleType, SimpleNamespace
from urllib.parse import urlsplit, urlunsplit

import requests

DEFAULT_ROOT = Path('/media/fpt/fpt2/Weather_Claude')
USER_AGENT = 'UF-Blueberry-Weather-Research/1.0 (+https://github.com/SFP-team/Weather-Risk-Forecasting-System)'
GIB = 1024**3
ROOT_FREE_MIN, ROOT_FREE_SHARE = 10 * GIB, .05
PROJECT_FREE_MIN = 100 * GIB
EVIDENCE_MAX = 25 * GIB
MIN_HOST_INTERVAL = 2.
MAX_ATTEMPTS = 4
MAX_RETRY_WAIT = 600
TIMEOUT = (15, 120)
CHUNK = 1024 * 1024
LOG_MAX_BYTES, LOG_KEEP = 20 * 1024**2, 5
SCHEDULES = {'daily': '*-*-* 04:30:00', 'weekly': 'Mon *-*-* 04:30:00', 'monthly': '*-*-01 04:30:00',
             'quarterly': '*-01,04,07,10-01 04:30:00', 'yearly': '*-01-01 04:30:00', 'manual': None}
# Derived jobs run after the fetch jobs they read (two days later; six hours later for daily jobs), so they see that
# period's downloads.
DERIVED_SCHEDULES = {'daily': '*-*-* 10:30:00', 'weekly': 'Wed *-*-* 04:30:00', 'monthly': '*-*-03 04:30:00',
                     'quarterly': '*-01,04,07,10-03 04:30:00', 'yearly': '*-01-03 04:30:00', 'manual': None}
# A file that claims to be an archive or PDF but starts with HTML is a bot wall or error page.
MAGIC = {'.zip': (b'PK',), '.xlsx': (b'PK',), '.gz': (b'\x1f\x8b',), '.pdf': (b'%PDF',), '.parquet': (b'PAR1',)}
SECRET = re.compile(r'key|token|secret|pass|auth|sig|session', re.I)
NAME = re.compile(r'^[A-Za-z0-9_.-]+$')
_sleep = time.sleep
_monotonic = time.monotonic


@dataclass
class Request:
    key: str
    url: str
    params: dict | None = None
    headers: dict | None = None
    filename: str | None = None
    max_bytes: int = 200_000_000
    optional: bool = False


@dataclass
class Asset:
    key: str
    url: str
    path: Path | None
    sha256: str | None
    bytes: int
    changed: bool
    status: str  # 'fetched' | 'unchanged' | 'missing' | 'failed'
    fetched_at: str | None
    etag: str | None
    last_modified: str | None


class GuardError(RuntimeError):
    pass


class _Terminal(Exception):
    pass


def utcnow():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def project_root():
    return Path(os.environ.get('EVIDENCE_ROOT') or DEFAULT_ROOT)


def retry_delay(header, attempts, now=None):
    """Honor delay-seconds and HTTP-date Retry-After without shortening backoff (as pilot.py)."""
    delay = 2**attempts
    header = (header or '').strip()
    if header.isdigit():
        return max(delay, int(header))
    try:
        instant = parsedate_to_datetime(header)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        return max(delay, math.ceil((instant - (now or datetime.now(timezone.utc))).total_seconds()))
    except (TypeError, ValueError, OverflowError, IndexError):
        return delay


def redact(url, params=None):
    """URL without query string plus parameters with secret-looking values masked."""
    parts = urlsplit(url)
    query = dict(p.split('=', 1) if '=' in p else (p, '') for p in parts.query.split('&') if p)
    query.update(params or {})
    return (urlunsplit((parts.scheme, parts.netloc, parts.path, '', '')),
            {k: ('***' if SECRET.search(str(k)) else v) for k, v in query.items()})


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as handle:
        for block in iter(lambda: handle.read(CHUNK), b''):
            digest.update(block)
    return digest.hexdigest()


def tree_bytes(path):
    total = 0
    for folder, _, files in os.walk(path):
        for name in files:
            try:
                total += os.lstat(os.path.join(folder, name)).st_size
            except FileNotFoundError:
                pass
    return total


def read_json(path, default=None):
    try:
        return json.loads(Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def atomic_write_text(path, text):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name('.' + path.name + '.partial')
    with open(partial, 'w') as handle:
        handle.write(text)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(partial, path)


def write_json(path, value):
    atomic_write_text(path, json.dumps(value, indent=1, sort_keys=True, default=str) + '\n')


def guard_report(root, evidence_bytes=None):
    """Disk guards. Evaluated before any write; never deletes anything to make room."""
    system = shutil.disk_usage('/')
    project = shutil.disk_usage(root if root.exists() else root.parent)
    if evidence_bytes is None:
        evidence_bytes = tree_bytes(root / 'data/evidence')
    violations = []
    if system.free < ROOT_FREE_MIN or system.free < system.total * ROOT_FREE_SHARE:
        violations.append(f'root filesystem free {system.free / GIB:.1f} GiB is below 10 GiB or 5%')
    if project.free < PROJECT_FREE_MIN:
        violations.append(f'project drive free {project.free / GIB:.1f} GiB is below 100 GiB')
    if evidence_bytes > EVIDENCE_MAX:
        violations.append(f'data/evidence holds {evidence_bytes / GIB:.2f} GiB, above 25 GiB')
    return {'ok': not violations, 'violations': violations, 'root_free_bytes': system.free,
            'root_total_bytes': system.total, 'project_free_bytes': project.free,
            'evidence_bytes': evidence_bytes}


class JsonLog:
    """JSON lines, size-rotated (current file plus LOG_KEEP numbered files)."""

    def __init__(self, path, job, run_id):
        self.path, self.job, self.run_id = Path(path), job, run_id

    def __call__(self, event, **fields):
        line = json.dumps({'ts': utcnow(), 'job': self.job, 'run_id': self.run_id, 'event': event, **fields},
                          default=str) + '\n'
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists() and self.path.stat().st_size + len(line) > LOG_MAX_BYTES:
            self.rotate()
        with open(self.path, 'a') as handle:
            handle.write(line)

    def rotate(self):
        for index in range(LOG_KEEP - 1, 0, -1):
            source = self.path.with_name(f'{self.path.name}.{index}')
            if source.exists():
                os.replace(source, self.path.with_name(f'{self.path.name}.{index + 1}'))
        os.replace(self.path, self.path.with_name(self.path.name + '.1'))


def registry():
    return read_json(Path(__file__).with_name('registry.json'), {'sources': []})


def job_paths(root, job_id):
    return SimpleNamespace(raw=root / 'data/evidence/raw' / job_id, derived=root / 'data/evidence/derived' / job_id,
                           tmp=root / 'tmp/evidence' / job_id, state=root / 'state/evidence' / f'{job_id}.json',
                           lock=root / 'state/evidence' / f'{job_id}.lock', log=root / 'logs/evidence' / f'{job_id}.jsonl')


def load_job(job):
    if isinstance(job, ModuleType):
        return job
    from . import adapters
    return adapters.load(job)


class Context:
    """What adapters see. State changes persist only when the run does not end fatally."""

    def __init__(self, run):
        self._run = run
        self.state = run.adapter_state
        self.today = date.today()
        self.force = run.force
        self.config = run.config
        self.root = run.root
        self.paths = SimpleNamespace(raw=run.paths.raw, derived=run.paths.derived, tmp=run.paths.tmp)

    def log(self, event, **fields):
        self._run.log(event, **fields)

    def fetch(self, request):
        return self._run.fetch(request)

    def write_table(self, name, frame):
        return self._run.write_table(name, frame)

    def read_table(self, job_id, name):
        import pandas as pd
        return pd.read_parquet(self.root / 'data/evidence/derived' / job_id / f'{name}.parquet')

    def weather_root(self):
        return Path(os.environ.get('EVIDENCE_WEATHER_ROOT') or DEFAULT_ROOT)


class Run:
    def __init__(self, module, root=None, force=False, dry_run=False, max_requests=None):
        self.module, self.job = module, module.JOB
        self.job_id = self.job['id']
        self.root = Path(root or project_root())
        self.force, self.dry_run, self.max_requests = force, dry_run, max_requests
        self.paths = job_paths(self.root, self.job_id)
        sources = {s['id']: s for s in registry().get('sources', [])}
        self.config = {**self.job, 'sources': [sources[s] for s in self.job.get('source_ids', []) if s in sources]}
        self.run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:6]
        self._log = JsonLog(self.paths.log, self.job_id, self.run_id)
        self.saved = read_json(self.paths.state, {}) or {}
        self.adapter_state = copy.deepcopy(self.saved.get('adapter', {}))
        self.parsed = dict(self.saved.get('parsed', {}))
        self.assets, self.requests, self.records, self.tables = {}, {}, {}, {}
        self.filenames, self.skipped, self.last_host = {}, [], {}
        self.requests_made = self.bytes_received = self.table_bytes = 0
        self.evidence_bytes = 0
        self.session = None

    # -- logging and guards
    def log(self, event, **fields):
        if not self.dry_run:
            self._log(event, **fields)

    def guard(self):
        report = guard_report(self.root, self.evidence_bytes + self.bytes_received + self.table_bytes)
        if not report['ok']:
            raise GuardError('; '.join(report['violations']))

    # -- fetching
    def _dest(self, request):
        name = request.filename or PurePosixPath(urlsplit(request.url).path).name
        rel = PurePosixPath(name)
        if (not name or rel.is_absolute() or '..' in rel.parts or name.endswith(('.manifest.json', '.partial'))):
            raise ValueError(f'Unsafe or empty raw filename for {request.key!r}: {name!r}')
        if self.filenames.setdefault(str(rel), request.key) != request.key:
            raise ValueError(f'Two requests share the raw filename {rel}')
        return self.paths.raw / rel

    def _stored(self, request, dest, prev, status, error=None, http_status=None):
        keep = prev is not None and status != 'missing'
        sha = prev.get('sha256') if keep else None
        asset = Asset(request.key, request.url, dest if keep else None, sha, prev.get('bytes', 0) if keep else 0,
                      keep and self.parsed.get(request.key) != sha, status,
                      prev.get('fetched_at') if keep else None, prev.get('etag') if keep else None,
                      prev.get('last_modified') if keep else None)
        return self._record(request, asset, error, http_status)

    def _record(self, request, asset, error=None, http_status=None):
        self.assets[request.key] = asset
        self.requests[request.key] = request
        self.records[request.key] = {'url': redact(request.url)[0], 'status': asset.status, 'http_status': http_status,
                                     'error': error, 'sha256': asset.sha256, 'bytes': asset.bytes,
                                     'optional': request.optional, 'checked_at': utcnow()}
        return asset

    def _wait_host(self, host):
        last = self.last_host.get(host)
        if last is not None:
            wait = last + MIN_HOST_INTERVAL - _monotonic()
            if wait > 0:
                _sleep(wait)

    def fetch(self, request):
        if request.key in self.assets:
            return self.assets[request.key]
        if not NAME.match(request.key):
            raise ValueError(f'Request key must match {NAME.pattern}: {request.key!r}')
        dest = self._dest(request)
        manifest = dest.with_name(dest.name + '.manifest.json')
        prev = read_json(manifest) if dest.is_file() else None
        if prev and prev.get('bytes') != dest.stat().st_size:
            prev = None  # the stored copy does not match its manifest; fetch it again unconditionally
        if prev and self.force and sha256_file(dest) != prev.get('sha256'):
            prev = None
        if self.dry_run:
            return self._stored(request, dest, prev, 'unchanged' if prev else 'missing')
        spent = self.max_requests is not None and self.requests_made >= self.max_requests
        if spent or self.bytes_received >= self.job.get('max_bytes_per_run', 2 * GIB):
            self.skipped.append(request.key)
            self.log('request_skipped', key=request.key, reason='max_requests' if spent else 'max_bytes_per_run')
            return self._stored(request, dest, prev, 'unchanged' if prev else 'missing', 'skipped: run budget spent')
        self.requests_made += 1
        url, params = redact(request.url, request.params)
        headers = {'User-Agent': USER_AGENT, **(request.headers or {})}
        if prev and prev.get('etag'):
            headers['If-None-Match'] = prev['etag']
        if prev and prev.get('last_modified'):
            headers['If-Modified-Since'] = prev['last_modified']
        host = urlsplit(request.url).netloc
        error = http_status = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            self.guard()
            self._wait_host(host)
            started = _monotonic()
            delay = retry_delay('', attempt)
            try:
                with self.session.get(request.url, params=request.params, headers=headers, stream=True,
                                      timeout=TIMEOUT) as response:
                    http_status = response.status_code
                    if http_status == 304 and prev:
                        self.log('request_unchanged', key=request.key, url=url, http_status=304, attempt=attempt)
                        self._touch_manifest(manifest, prev, response, 304)
                        return self._stored(request, dest, prev, 'unchanged', http_status=304)
                    if http_status == 429 or http_status >= 500:
                        error = f'HTTP {http_status}'
                        delay = retry_delay(response.headers.get('Retry-After', ''), attempt)
                    elif http_status >= 300:
                        status = 'missing' if http_status in (404, 410) else 'failed'
                        self.log('request_terminal', key=request.key, url=url, http_status=http_status,
                                 optional=request.optional)
                        return self._stored(request, dest, prev, status, f'HTTP {http_status}', http_status)
                    else:
                        asset = self._download(request, response, dest, prev, manifest, url, params)
                        self.log('request_done', key=request.key, url=url, http_status=http_status,
                                 status=asset.status, bytes=asset.bytes, sha256=asset.sha256, attempt=attempt,
                                 duration_ms=round((_monotonic() - started) * 1000))
                        return asset
            except _Terminal as exc:
                self.log('request_terminal', key=request.key, url=url, error=str(exc), optional=request.optional)
                return self._stored(request, dest, prev, 'failed', str(exc), http_status)
            except (requests.Timeout, requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as exc:
                error, http_status = type(exc).__name__, None
            finally:
                self.last_host[host] = _monotonic()
            if attempt == MAX_ATTEMPTS:
                break
            if delay > MAX_RETRY_WAIT:
                error += f'; Retry-After {delay} s exceeds the {MAX_RETRY_WAIT} s limit'
                break
            self.log('request_retry', key=request.key, url=url, attempt=attempt, delay_s=delay, error=error)
            _sleep(delay)
        self.log('request_failed', key=request.key, url=url, error=error, http_status=http_status,
                 optional=request.optional)
        return self._stored(request, dest, prev, 'failed', error, http_status)

    def _touch_manifest(self, path, prev, response, http_status):
        updated = {**prev, 'checked_at': utcnow(), 'http_status': http_status}
        updated['etag'] = response.headers.get('ETag') or prev.get('etag')
        updated['last_modified'] = response.headers.get('Last-Modified') or prev.get('last_modified')
        write_json(path, updated)
        prev.update(updated)

    def _download(self, request, response, dest, prev, manifest, url, params):
        length = response.headers.get('Content-Length')
        if length and length.isdigit() and int(length) > request.max_bytes:
            raise _Terminal(f'Content-Length {length} exceeds max_bytes {request.max_bytes}')
        dest.parent.mkdir(parents=True, exist_ok=True)
        partial = dest.with_name('.' + dest.name + '.partial')
        digest, size, head = hashlib.sha256(), 0, b''
        cap = self.job.get('max_bytes_per_run', 2 * GIB)
        try:
            with open(partial, 'wb') as handle:
                for block in response.iter_content(CHUNK):
                    size += len(block)
                    self.bytes_received += len(block)
                    if size > request.max_bytes:
                        raise _Terminal(f'Download exceeded max_bytes {request.max_bytes}')
                    if self.bytes_received > cap:
                        raise _Terminal(f'Run exceeded max_bytes_per_run {cap}')
                    if len(head) < 64:
                        head += block[:64]
                    digest.update(block)
                    handle.write(block)
                    if size % (64 * CHUNK) < len(block):
                        self.guard()
                handle.flush()
                os.fsync(handle.fileno())
            magic = MAGIC.get(dest.suffix.lower())
            if magic and not head.startswith(magic):
                raise _Terminal(f'Unexpected content for {dest.suffix}: starts with {head[:16]!r}')
            sha = digest.hexdigest()
            record = {'key': request.key, 'job': self.job_id, 'url': url, 'params': params,
                      'final_url': redact(response.url)[0], 'http_status': response.status_code,
                      'content_type': response.headers.get('Content-Type'), 'etag': response.headers.get('ETag'),
                      'last_modified': response.headers.get('Last-Modified'), 'bytes': size, 'sha256': sha,
                      'checked_at': utcnow()}
            if prev and prev.get('sha256') == sha:
                partial.unlink()
                record.update(fetched_at=prev.get('fetched_at'), previous_sha256=prev.get('previous_sha256'))
                write_json(manifest, record)
                return self._stored(request, dest, record, 'unchanged', http_status=response.status_code)
            record.update(fetched_at=utcnow(), previous_sha256=prev.get('sha256') if prev else None)
            os.replace(partial, dest)
            write_json(manifest, record)
            return self._stored(request, dest, record, 'fetched', http_status=response.status_code)
        finally:
            if partial.exists():
                partial.unlink()

    # -- tables
    def write_table(self, name, frame):
        if not NAME.match(name) or name.startswith('_'):
            raise ValueError(f'Table name must match {NAME.pattern} and not start with _: {name!r}')
        self.guard()
        self.paths.derived.mkdir(parents=True, exist_ok=True)
        path = self.paths.derived / f'{name}.parquet'
        partial = path.with_name('.' + path.name + '.partial')
        try:
            frame.to_parquet(partial, index=False)
            os.replace(partial, path)
        finally:
            if partial.exists():
                partial.unlink()
        size = path.stat().st_size
        self.table_bytes += size
        self.tables[name] = {'rows': int(len(frame)), 'columns': [str(c) for c in frame.columns], 'bytes': size,
                             'sha256': sha256_file(path), 'written_at': utcnow()}
        self.log('table_written', table=name, rows=int(len(frame)), bytes=size)
        return path

    # -- orchestration
    def _inputs_fingerprint(self):
        inputs = self.job.get('inputs') or []
        if not inputs:
            return None
        digest = hashlib.sha256()
        for job_id in sorted(inputs):
            path = self.root / 'data/evidence/derived' / job_id / '_run_manifest.json'
            digest.update(job_id.encode() + (path.read_bytes() if path.exists() else b'-'))
        return digest.hexdigest()

    def execute(self):
        report = guard_report(self.root)
        if not report['ok']:
            print(json.dumps({'job': self.job_id, 'outcome': 'fatal', 'error': 'guard',
                              'violations': report['violations']}), file=sys.stderr)
            return 1
        self.evidence_bytes = report['evidence_bytes']
        if self.dry_run:
            return self._dry_run()
        for folder in (self.paths.raw, self.paths.derived, self.paths.tmp, self.paths.state.parent,
                       self.paths.log.parent):
            folder.mkdir(parents=True, exist_ok=True)
        os.environ['TMPDIR'] = str(self.paths.tmp.parent)
        tempfile.tempdir = None
        lock = open(self.paths.lock, 'a')
        try:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                self.log('lock_busy')
                print(json.dumps({'job': self.job_id, 'outcome': 'fatal', 'error': 'another run holds the lock'}),
                      file=sys.stderr)
                return 1
            return self._execute_locked()
        finally:
            lock.close()

    def _dry_run(self):
        ctx = Context(self)
        try:
            planned = list(self.module.plan(ctx))
        except Exception as exc:
            print(json.dumps({'job': self.job_id, 'dry_run': True, 'error': f'{type(exc).__name__}: {exc}'}))
            return 1
        rows = []
        for request in planned:
            asset = self.fetch(request)
            rows.append({'key': request.key, 'url': redact(request.url, request.params)[0],
                         'file': str(self._dest_name(request)), 'optional': request.optional,
                         'max_bytes': request.max_bytes, 'stored': asset.path is not None})
        print(json.dumps({'job': self.job_id, 'dry_run': True, 'requests': rows}, indent=1))
        return 0

    @staticmethod
    def _dest_name(request):
        return request.filename or PurePosixPath(urlsplit(request.url).path).name

    def _execute_locked(self):
        started, clock = utcnow(), _monotonic()
        # Re-read under the lock: a run that just finished may have saved newer state.
        self.saved = read_json(self.paths.state, {}) or {}
        self.adapter_state = copy.deepcopy(self.saved.get('adapter', {}))
        self.parsed = dict(self.saved.get('parsed', {}))
        self.session = requests.Session()
        self.log('run_start', force=self.force, max_requests=self.max_requests)
        summary, error, parsed_run = None, None, False
        inputs_fp = self.saved.get('inputs_fingerprint')
        try:
            ctx = Context(self)
            for request in self.module.plan(ctx):
                self.fetch(request)
            fingerprint = self._inputs_fingerprint()
            derived_trigger = bool(self.job.get('derived_only')) and (fingerprint is None or fingerprint != inputs_fp)
            if self.force or derived_trigger or any(a.changed for a in self.assets.values()):
                self.log('parse_start', assets=len(self.assets))
                summary = self.module.parse(ctx, dict(self.assets)) or {}
                parsed_run = True
                for key, asset in self.assets.items():
                    if asset.path is not None:
                        self.parsed[key] = asset.sha256
                inputs_fp = fingerprint
                write_json(self.paths.derived / '_run_manifest.json', {
                    'job': self.job_id, 'run_id': self.run_id, 'written_at': utcnow(), 'summary': summary,
                    'tables': self.tables,
                    'assets': {k: {'status': a.status, 'sha256': a.sha256, 'bytes': a.bytes,
                                   'file': str(a.path.relative_to(self.root)) if a.path else None}
                               for k, a in sorted(self.assets.items())}})
        except GuardError as exc:
            error = f'guard: {exc}'
        except Exception as exc:
            error = f'{type(exc).__name__}: {exc}'
            self.log('error', error=error, traceback=traceback.format_exc(limit=8))
        finally:
            self.session.close()
        failed = sorted(k for k, a in self.assets.items()
                        if not self.requests[k].optional and (a.status in ('failed', 'missing') or k in self.skipped))
        fetched = sorted(k for k, a in self.assets.items() if a.status == 'fetched')
        outcome = 'fatal' if error else 'partial' if failed else 'ok' if fetched or parsed_run else 'unchanged'
        finished = utcnow()
        last_run = {'run_id': self.run_id, 'started': started, 'finished': finished, 'outcome': outcome,
                    'duration_s': round(_monotonic() - clock, 1), 'requests_made': self.requests_made,
                    'bytes_received': self.bytes_received, 'fetched': fetched, 'failed': failed,
                    'skipped': self.skipped, 'parsed': parsed_run, 'summary': summary, 'error': error,
                    'tables': {k: v['rows'] for k, v in self.tables.items()}}
        state = dict(self.saved, job=self.job_id, last_run=last_run)
        if outcome != 'fatal':
            state.update(adapter=self.adapter_state, parsed=self.parsed, inputs_fingerprint=inputs_fp,
                         requests={**self.saved.get('requests', {}), **self.records},
                         last_success=finished)
            if fetched or parsed_run:
                state['last_change'] = finished
            if self.tables:
                state['tables'] = {**self.saved.get('tables', {}), **self.tables}
        write_json(self.paths.state, state)
        self.log('run_end', outcome=outcome, requests_made=self.requests_made, bytes_received=self.bytes_received,
                 fetched=len(fetched), failed=failed, parsed=parsed_run, error=error)
        print(json.dumps({'job': self.job_id, 'outcome': outcome, 'requests_made': self.requests_made,
                          'bytes_received': self.bytes_received, 'fetched': len(fetched), 'failed': failed,
                          'parsed': parsed_run, 'summary': summary, 'error': error}, default=str))
        return {'ok': 0, 'unchanged': 0, 'partial': 2}.get(outcome, 1)


def run_job(job, force=False, dry_run=False, max_requests=None, root=None):
    try:
        module = load_job(job)
    except Exception as exc:
        print(json.dumps({'job': str(job), 'outcome': 'fatal', 'error': f'{type(exc).__name__}: {exc}'}),
              file=sys.stderr)
        return 1
    return Run(module, root, force, dry_run, max_requests).execute()


def job_table(include_errors=True):
    from . import adapters
    rows = []
    for job_id in adapters.MODULES:
        try:
            job = adapters.load(job_id).JOB
            rows.append({'id': job_id, 'schedule': job.get('schedule', 'manual'), 'description': job.get('description', ''),
                         'source_ids': job.get('source_ids', []), 'derived_only': bool(job.get('derived_only')),
                         'available': True})
        except Exception as exc:
            if include_errors:
                rows.append({'id': job_id, 'schedule': None, 'description': '', 'source_ids': [],
                             'derived_only': False, 'available': False, 'error': f'{type(exc).__name__}: {exc}'})
    return rows


def status(root=None):
    root = Path(root or project_root())
    jobs = []
    for row in job_table():
        paths = job_paths(root, row['id'])
        state = read_json(paths.state, {}) or {}
        last = state.get('last_run') or {}
        failures = sorted(k for k, r in state.get('requests', {}).items()
                          if r.get('status') in ('failed', 'missing') and not r.get('optional'))
        jobs.append({**row, 'last_run': last.get('finished'), 'outcome': last.get('outcome'),
                     'last_error': last.get('error'), 'last_success': state.get('last_success'),
                     'last_change': state.get('last_change'), 'open_failures': failures,
                     'assets': len(state.get('requests', {})), 'raw_bytes': tree_bytes(paths.raw),
                     'tables': {k: v.get('rows') for k, v in state.get('tables', {}).items()},
                     'locked': _locked(paths.lock)})
    return {'generated_at': utcnow(), 'root': str(root), 'guards': guard_report(root), 'jobs': jobs}


def _locked(path):
    if not path.exists():
        return False
    with open(path, 'a') as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return True
        fcntl.flock(handle, fcntl.LOCK_UN)
    return False


def print_status(report):
    guards = report['guards']
    print(f"root {report['root']}  guards {'ok' if guards['ok'] else 'VIOLATED: ' + '; '.join(guards['violations'])}"
          f"  root free {guards['root_free_bytes'] / GIB:.0f} GiB  project free {guards['project_free_bytes'] / GIB:.0f} GiB"
          f"  evidence {guards['evidence_bytes'] / GIB:.2f} GiB")
    print(f"{'job':18} {'schedule':9} {'outcome':9} {'last run':25} {'last change':25} {'assets':>6} {'raw MB':>8} "
          f"{'fail':>4}  tables")
    for job in report['jobs']:
        if not job['available']:
            print(f"{job['id']:18} unavailable: {job['error']}")
            continue
        tables = ', '.join(f'{k}={v}' for k, v in sorted(job['tables'].items())[:4])
        more = len(job['tables']) - 4
        print(f"{job['id']:18} {job['schedule']:9} {job['outcome'] or '-':9} {job['last_run'] or '-':25} "
              f"{job['last_change'] or '-':25} {job['assets']:>6} {job['raw_bytes'] / 1e6:>8.1f} "
              f"{len(job['open_failures']):>4}  {tables}{f' (+{more} more)' if more > 0 else ''}"
              f"{'  [running]' if job['locked'] else ''}")


def systemd_units(out, root=None):
    root = Path(root or project_root())
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    service = f"""[Unit]
Description=Blueberry evidence job %i
ConditionPathIsMountPoint=/media/fpt/fpt2

[Service]
Type=oneshot
WorkingDirectory={root}/code
Environment=TMPDIR={root}/tmp/evidence
Environment=PYTHONDONTWRITEBYTECODE=1
ExecStart={root}/env/bin/python -m evidence run %i
Nice=10
IOSchedulingClass=idle
TimeoutStartSec=4h
StandardOutput=append:{root}/logs/evidence/%i.stdout.log
StandardError=append:{root}/logs/evidence/%i.stdout.log
"""
    # The fpt account also runs other projects' user units, so every unit name carries the project prefix.
    written = [out / 'blueberry-evidence@.service']
    written[0].write_text(service)
    for job in job_table(include_errors=False):
        calendar = (DERIVED_SCHEDULES if job['derived_only'] else SCHEDULES).get(job['schedule'])
        if not calendar:
            continue
        path = out / f"blueberry-evidence-{job['id']}.timer"
        path.write_text(f"""[Unit]
Description={job['schedule'].capitalize()} blueberry evidence job {job['id']}

[Timer]
OnCalendar={calendar}
RandomizedDelaySec=1h
Persistent=true
Unit=blueberry-evidence@{job['id']}.service

[Install]
WantedBy=timers.target
""")
        written.append(path)
    return written


def main(argv=None):
    parser = argparse.ArgumentParser(prog='python -m evidence', description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list', help='list registered jobs')
    status_parser = commands.add_parser('status', help='last run, failures and guards per job')
    status_parser.add_argument('--json', action='store_true')
    run_parser = commands.add_parser('run', help='run one job now')
    run_parser.add_argument('job_id')
    run_parser.add_argument('--force', action='store_true', help='parse even when no asset changed')
    run_parser.add_argument('--dry-run', action='store_true', help='plan only; no network fetches and no writes')
    run_parser.add_argument('--max-requests', type=int, help='stop fetching after N requests (partial run)')
    units_parser = commands.add_parser('systemd-units', help='write the service template and one timer per job')
    units_parser.add_argument('--out', required=True)
    args = parser.parse_args(argv)
    if args.command == 'list':
        for job in job_table():
            note = '' if job['available'] else f"  (unavailable: {job['error']})"
            print(f"{job['id']:18} {job['schedule'] or '-':9} {job['description']}{note}")
        return 0
    if args.command == 'status':
        report = status()
        if args.json:
            print(json.dumps(report, indent=1, default=str))
        else:
            print_status(report)
        return 0
    if args.command == 'systemd-units':
        for path in systemd_units(args.out):
            print(path)
        return 0
    return run_job(args.job_id, args.force, args.dry_run, args.max_requests)
