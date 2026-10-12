import contextlib
import fcntl
from collections import namedtuple
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import threading
import types
import unittest
from unittest import mock

CODE = Path(__file__).resolve().parents[2] / 'pipelines'
if not (CODE / 'evidence').exists():
    CODE = Path(__file__).resolve().parent
sys.path.insert(0, str(CODE))
from evidence import runner  # noqa: E402
from evidence.runner import Request  # noqa: E402

Usage = namedtuple('Usage', 'total used free')
PLENTY = Usage(4000 * runner.GIB, 1000 * runner.GIB, 3000 * runner.GIB)


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        pass  # clients abort on purpose in the byte-cap tests


class Server:
    """Local HTTP server. Routes map a path to a callable(handler) -> (status, headers, body).
    A header set to None is not sent, so a body can end at connection close (HTTP/1.0)."""

    def __init__(self):
        self.routes, self.hits = {}, []
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = self.path.split('?')[0]
                owner.hits.append((path, dict(self.headers)))
                route = owner.routes.get(path)
                status, headers, body = route(self) if route else (404, {}, b'not found')
                self.send_response(status)
                for key, value in headers.items():
                    if value is not None:
                        self.send_header(key, value)
                if 'Content-Length' not in headers and status != 304:
                    self.send_header('Content-Length', str(len(body)))
                self.end_headers()
                if status != 304:
                    try:
                        self.wfile.write(body)
                    except (BrokenPipeError, ConnectionResetError):
                        pass

            def log_message(self, *args):
                pass

        self.httpd = QuietServer(('127.0.0.1', 0), Handler)
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def url(self, path):
        return f'http://127.0.0.1:{self.httpd.server_port}{path}'

    def count(self, path):
        return sum(1 for p, _ in self.hits if p == path)

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def static(body, etag=None):
    def route(handler):
        if etag and handler.headers.get('If-None-Match') == etag:
            return 304, {'ETag': etag}, b''
        return 200, {'ETag': etag} if etag else {}, body
    return route


def sequence(*responses):
    responses = list(responses)

    def route(handler):
        return responses.pop(0) if len(responses) > 1 else responses[0]
    return route


def make_job(requests, parse=None, job_id='test-job', **job):
    module = types.ModuleType('test_adapter')
    module.JOB = {'id': job_id, 'source_ids': [], 'schedule': 'manual', 'description': 'test',
                  'max_bytes_per_run': 10_000_000, 'derived_only': False, **job}
    module.parses = []

    def plan(ctx):
        return [r() if callable(r) else r for r in requests]

    def default_parse(ctx, assets):
        import pandas as pd
        module.parses.append({k: (a.status, a.changed) for k, a in assets.items()})
        ctx.write_table('items', pd.DataFrame({'key': sorted(assets)}))
        ctx.state['parsed'] = ctx.state.get('parsed', 0) + 1
        return {'assets': len(assets)}

    module.plan, module.parse = plan, parse or default_parse
    return module


class RunnerTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.root = self.tmp / 'root'
        self.root.mkdir()
        self.server = Server()
        self.sleeps = []
        self.addCleanup(setattr, tempfile, 'tempdir', None)  # runs last, after TMPDIR is restored
        for patcher in (mock.patch.dict(os.environ, {'EVIDENCE_ROOT': str(self.root), 'TMPDIR': os.environ.get('TMPDIR', '/tmp')}),
                        mock.patch.object(runner, 'MIN_HOST_INTERVAL', 0.),
                        mock.patch.object(runner, '_sleep', self.sleeps.append),
                        mock.patch.object(runner.shutil, 'disk_usage', lambda path: PLENTY)):
            patcher.start()
            self.addCleanup(patcher.stop)

    def tearDown(self):
        self.server.close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_job(self, module, **kwargs):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = runner.run_job(module, **kwargs)
        self.last_output = out.getvalue() + err.getvalue()
        return code

    def state(self, job_id='test-job'):
        return json.loads((self.root / 'state/evidence' / f'{job_id}.json').read_text())

    def raw(self, name, job_id='test-job'):
        return self.root / 'data/evidence/raw' / job_id / name


class FetchTests(RunnerTestCase):
    def test_fetch_then_304_is_unchanged_and_skips_parse(self):
        self.server.routes['/a.txt'] = static(b'alpha', etag='"v1"')
        job = make_job([Request('a', self.server.url('/a.txt'))])
        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(self.raw('a.txt').read_bytes(), b'alpha')
        manifest = json.loads(self.raw('a.txt.manifest.json').read_text())
        self.assertEqual((manifest['etag'], manifest['bytes'], manifest['http_status']), ('"v1"', 5, 200))
        self.assertEqual(job.parses, [{'a': ('fetched', True)}])
        self.assertEqual(self.state()['last_run']['outcome'], 'ok')

        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(self.server.hits[-1][1].get('If-None-Match'), '"v1"')
        self.assertEqual(len(job.parses), 1, 'parse must not run when nothing changed')
        state = self.state()
        self.assertEqual(state['last_run']['outcome'], 'unchanged')
        self.assertEqual(state['adapter'], {'parsed': 1})
        self.assertEqual(state['requests']['a']['http_status'], 304)

    def test_identical_bytes_without_validators_are_unchanged(self):
        self.server.routes['/b.txt'] = static(b'beta')
        job = make_job([Request('b', self.server.url('/b.txt'))])
        self.run_job(job)
        mtime = self.raw('b.txt').stat().st_mtime_ns
        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(self.raw('b.txt').stat().st_mtime_ns, mtime)
        self.assertEqual(len(job.parses), 1)
        self.assertEqual(self.state()['last_run']['outcome'], 'unchanged')

    def test_changed_content_reparses_and_force_reparses(self):
        route = {'body': b'one'}
        self.server.routes['/c.txt'] = lambda h: (200, {}, route['body'])
        job = make_job([Request('c', self.server.url('/c.txt'))])
        self.run_job(job)
        route['body'] = b'two'
        self.run_job(job)
        self.assertEqual(job.parses[-1], {'c': ('fetched', True)})
        manifest = json.loads(self.raw('c.txt.manifest.json').read_text())
        self.assertIsNotNone(manifest['previous_sha256'])
        self.run_job(job, force=True)
        self.assertEqual(len(job.parses), 3)
        self.assertEqual(job.parses[-1], {'c': ('unchanged', False)})

    def test_conditional_get_sends_user_agent(self):
        self.server.routes['/u.txt'] = static(b'u')
        self.run_job(make_job([Request('u', self.server.url('/u.txt'))]))
        self.assertEqual(self.server.hits[0][1]['User-Agent'], runner.USER_AGENT)


class LimitTests(RunnerTestCase):
    def test_content_length_over_cap_is_refused(self):
        self.server.routes['/big.bin'] = static(b'x' * 5000)
        job = make_job([Request('big', self.server.url('/big.bin'), max_bytes=1000)])
        self.assertEqual(self.run_job(job), 2)
        self.assertFalse(self.raw('big.bin').exists())
        self.assertEqual(list(self.raw('').glob('.*partial')), [])
        self.assertEqual(self.server.count('/big.bin'), 1, 'a byte-cap failure is terminal')
        self.assertIn('max_bytes', self.state()['requests']['big']['error'])

    def test_streamed_body_over_cap_is_refused(self):
        # No Content-Length: the body ends when the connection closes, so only the stream counter can stop it.
        def route(handler):
            handler.protocol_version = 'HTTP/1.0'
            return 200, {'Content-Length': None}, b'y' * (3 * runner.CHUNK)
        self.server.routes['/stream.bin'] = route
        job = make_job([Request('s', self.server.url('/stream.bin'), max_bytes=runner.CHUNK)])
        self.assertEqual(self.run_job(job), 2)
        self.assertFalse(self.raw('stream.bin').exists())
        self.assertEqual(list(self.raw('').glob('.*partial')), [])

    def test_run_byte_budget_and_max_requests(self):
        for name in 'xyz':
            self.server.routes[f'/{name}.txt'] = static(name.encode() * 10)
        job = make_job([Request(n, self.server.url(f'/{n}.txt')) for n in 'xyz'])
        self.assertEqual(self.run_job(job, max_requests=2), 2)
        self.assertEqual(self.state()['last_run']['skipped'], ['z'])
        self.assertEqual(job.parses[-1]['z'], ('missing', False))
        self.assertEqual(self.run_job(job), 0, 'the next full run completes the backfill')
        self.assertEqual(job.parses[-1]['z'], ('fetched', True))
        capped = make_job([Request(n, self.server.url(f'/{n}.txt')) for n in 'xyz'], job_id='cap-job',
                          max_bytes_per_run=15)
        self.assertEqual(self.run_job(capped), 2)
        state = self.state('cap-job')
        self.assertEqual([state['requests'][k]['status'] for k in 'xyz'], ['fetched', 'failed', 'missing'])
        self.assertIn('max_bytes_per_run', state['requests']['y']['error'])
        self.assertEqual(state['last_run']['skipped'], ['z'])

    def test_magic_bytes_reject_html_error_page(self):
        self.server.routes['/file.zip'] = static(b'<!doctype html><title>blocked</title>')
        job = make_job([Request('z', self.server.url('/file.zip'))])
        self.assertEqual(self.run_job(job), 2)
        self.assertFalse(self.raw('file.zip').exists())

    def test_unsafe_filename_is_fatal(self):
        job = make_job([Request('a', self.server.url('/a'), filename='../escape.txt')])
        self.assertEqual(self.run_job(job), 1)
        self.assertFalse((self.root / 'data/evidence/raw/escape.txt').exists())


class RetryTests(RunnerTestCase):
    def test_503_with_retry_after_then_success(self):
        self.server.routes['/r.txt'] = sequence((503, {'Retry-After': '7'}, b'busy'), (200, {}, b'ok'))
        job = make_job([Request('r', self.server.url('/r.txt'))])
        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(self.server.count('/r.txt'), 2)
        self.assertIn(7, self.sleeps)

    def test_429_gives_up_after_four_attempts(self):
        self.server.routes['/t.txt'] = sequence((429, {'Retry-After': '1'}, b'slow down'))
        job = make_job([Request('t', self.server.url('/t.txt'))])
        self.assertEqual(self.run_job(job), 2)
        self.assertEqual(self.server.count('/t.txt'), runner.MAX_ATTEMPTS)
        self.assertEqual(self.sleeps, [2, 4, 8])

    def test_retry_after_beyond_limit_stops_retrying(self):
        self.server.routes['/l.txt'] = sequence((503, {'Retry-After': '99999'}, b'later'))
        job = make_job([Request('l', self.server.url('/l.txt'))])
        self.assertEqual(self.run_job(job), 2)
        self.assertEqual(self.server.count('/l.txt'), 1)
        self.assertEqual(self.sleeps, [])

    def test_404_is_terminal_and_optional_is_tolerated(self):
        job = make_job([Request('gone', self.server.url('/gone.txt'))])
        self.assertEqual(self.run_job(job), 2)
        self.assertEqual(self.server.count('/gone.txt'), 1)
        self.assertEqual(self.state()['requests']['gone']['status'], 'missing')
        self.assertEqual(self.state()['last_run']['failed'], ['gone'])

        self.server.routes['/here.txt'] = static(b'here')
        optional = make_job([Request('here', self.server.url('/here.txt')),
                             Request('later', self.server.url('/later.txt'), optional=True)], job_id='opt-job')
        self.assertEqual(self.run_job(optional), 0)
        self.assertEqual(optional.parses[0]['later'], ('missing', False))

    def test_retry_delay_honours_http_date(self):
        from datetime import datetime, timezone
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.assertEqual(runner.retry_delay('Thu, 01 Jan 2026 00:01:00 GMT', 1, now), 60)
        self.assertEqual(runner.retry_delay('garbage', 3, now), 8)


class GuardLockTests(RunnerTestCase):
    def test_guard_abort_writes_nothing(self):
        low = Usage(1000 * runner.GIB, 995 * runner.GIB, 5 * runner.GIB)
        self.server.routes['/g.txt'] = static(b'g')
        job = make_job([Request('g', self.server.url('/g.txt'))])
        with mock.patch.object(runner.shutil, 'disk_usage', lambda path: low):
            self.assertEqual(self.run_job(job), 1)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.server.hits, [])
        self.assertIn('below 10 GiB', self.last_output)

    def test_guard_evidence_quota(self):
        report = runner.guard_report(self.root, evidence_bytes=26 * runner.GIB)
        self.assertFalse(report['ok'])
        self.assertIn('above 25 GiB', report['violations'][0])

    def test_guard_failure_mid_run_is_fatal_and_keeps_state(self):
        self.server.routes['/m.txt'] = static(b'm')
        job = make_job([Request('m', self.server.url('/m.txt'))])
        calls = {'n': 0}

        def shrinking(path):
            calls['n'] += 1
            return PLENTY if calls['n'] <= 2 else Usage(1000 * runner.GIB, 999 * runner.GIB, runner.GIB)
        with mock.patch.object(runner.shutil, 'disk_usage', shrinking):
            self.assertEqual(self.run_job(job), 1)
        self.assertEqual(self.state()['last_run']['outcome'], 'fatal')
        self.assertNotIn('adapter', self.state())

    def test_lock_contention(self):
        self.server.routes['/k.txt'] = static(b'k')
        job = make_job([Request('k', self.server.url('/k.txt'))])
        lock_path = self.root / 'state/evidence/test-job.lock'
        lock_path.parent.mkdir(parents=True)
        with open(lock_path, 'a') as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.assertEqual(self.run_job(job), 1)
            self.assertTrue(runner.status(self.root)['jobs'] is not None)
        self.assertEqual(self.server.hits, [])
        self.assertIn('lock', self.last_output)
        self.assertEqual(self.run_job(job), 0)

    def test_tmpdir_forced_to_project(self):
        seen = {}

        def parse(ctx, assets):
            seen['tmp'] = tempfile.gettempdir()
            return {}
        self.server.routes['/p.txt'] = static(b'p')
        self.run_job(make_job([Request('p', self.server.url('/p.txt'))], parse=parse))
        self.assertEqual(Path(seen['tmp']), self.root / 'tmp/evidence')
        tempfile.tempdir = None


class AtomicTests(RunnerTestCase):
    def test_failed_table_write_keeps_previous_table(self):
        import pandas as pd
        bodies = [b'v1', b'v2']
        self.server.routes['/w.txt'] = lambda h: (200, {}, bodies[0] if len(bodies) == 2 else bodies[-1])
        job = make_job([Request('w', self.server.url('/w.txt'))])
        self.run_job(job)
        bodies.pop(0)
        table = self.root / 'data/evidence/derived/test-job/items.parquet'
        before = table.read_bytes()

        def broken(self, path, **kwargs):
            Path(path).write_bytes(b'half written')
            raise OSError('disk full')
        with mock.patch.object(pd.DataFrame, 'to_parquet', broken):
            self.assertEqual(self.run_job(job), 1)
        self.assertEqual(table.read_bytes(), before)
        self.assertEqual(list(table.parent.glob('.*partial')), [])
        self.assertEqual(self.state()['last_run']['outcome'], 'fatal')
        self.assertEqual(self.state()['adapter'], {'parsed': 1}, 'state is saved only after success')
        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(job.parses[-1]['w'], ('unchanged', True),
                         'bytes fetched by a failed run are still parsed by the next run')

    def test_interrupted_download_keeps_previous_raw_file(self):
        state = {'body': b'first'}

        def route(handler):
            if state['body'] is None:
                return 200, {'Content-Length': '1000'}, b'short'
            return 200, {}, state['body']
        self.server.routes['/i.txt'] = route
        job = make_job([Request('i', self.server.url('/i.txt'))])
        self.run_job(job)
        state['body'] = None
        self.assertEqual(self.run_job(job), 2)
        self.assertEqual(self.raw('i.txt').read_bytes(), b'first')
        self.assertEqual(list(self.raw('').glob('.*partial')), [])
        self.assertEqual(self.server.count('/i.txt'), 1 + runner.MAX_ATTEMPTS)

    def test_atomic_write_text_leaves_no_partial(self):
        target = self.tmp / 'x/state.json'
        runner.write_json(target, {'a': 1})
        runner.write_json(target, {'a': 2})
        self.assertEqual(json.loads(target.read_text()), {'a': 2})
        self.assertEqual([p.name for p in target.parent.iterdir()], ['state.json'])


class LogStatusUnitTests(RunnerTestCase):
    def test_log_rotation_keeps_five(self):
        path = self.tmp / 'logs/job.jsonl'
        log = runner.JsonLog(path, 'job', 'run')
        with mock.patch.object(runner, 'LOG_MAX_BYTES', 300):
            for index in range(200):
                log('event', index=index, padding='z' * 40)
        names = sorted(p.name for p in path.parent.iterdir())
        self.assertEqual(names, ['job.jsonl'] + [f'job.jsonl.{i}' for i in range(1, 6)])
        self.assertTrue(all(p.stat().st_size <= 300 for p in path.parent.iterdir()))
        last = json.loads(path.read_text().splitlines()[-1])
        self.assertEqual(last['index'], 199)

    def test_secrets_are_redacted(self):
        url, params = runner.redact('https://x.org/api?token=abc&year=2020', {'api_key': 'k', 'q': 'blue'})
        self.assertEqual(url, 'https://x.org/api')
        self.assertEqual(params, {'token': '***', 'year': '2020', 'api_key': '***', 'q': 'blue'})

    def test_dry_run_writes_nothing(self):
        self.server.routes['/d.txt'] = static(b'd')
        job = make_job([Request('d', self.server.url('/d.txt'))])
        self.assertEqual(self.run_job(job, dry_run=True), 0)
        self.assertEqual(list(self.root.iterdir()), [])
        self.assertEqual(self.server.hits, [])
        self.assertIn('"key": "d"', self.last_output)

    def test_plan_fetch_and_derived_inputs(self):
        self.server.routes['/list.txt'] = static(b'/one.txt\n')
        self.server.routes['/one.txt'] = static(b'one')

        def two_stage(ctx):
            listing = ctx.fetch(Request('listing', self.server.url('/list.txt')))
            return [Request('item', self.server.url(listing.path.read_text().strip()))]
        job = make_job([])
        job.plan = two_stage
        self.assertEqual(self.run_job(job), 0)
        self.assertEqual(set(job.parses[0]), {'listing', 'item'})

        derived = make_job([], job_id='derived-job', derived_only=True, inputs=['test-job'])
        self.assertEqual(self.run_job(derived), 0)
        self.assertEqual(self.run_job(derived), 0)
        self.assertEqual(len(derived.parses), 1, 'derived job reparses only when its inputs change')
        self.run_job(job, force=True)
        self.run_job(derived)
        self.assertEqual(len(derived.parses), 2)

    def test_status_and_systemd_units(self):
        out = self.tmp / 'units'
        fake = types.SimpleNamespace(MODULES={'rma-col': 'rma_col'},
                                     load=lambda job_id: types.SimpleNamespace(JOB={'id': job_id, 'schedule': 'monthly',
                                                                                     'description': 'd'}))
        with mock.patch.dict(sys.modules, {'evidence.adapters': fake}), mock.patch('evidence.adapters', fake, create=True):
            written = runner.systemd_units(out, root=Path('/srv/project'))
            report = runner.status(self.root)
        self.assertEqual(sorted(p.name for p in written), ['blueberry-evidence-rma-col.timer', 'blueberry-evidence@.service'])
        service = (out / 'blueberry-evidence@.service').read_text()
        for line in ('Type=oneshot', 'Nice=10', 'IOSchedulingClass=idle', 'Environment=TMPDIR=/srv/project/tmp/evidence',
                     'Environment=PYTHONDONTWRITEBYTECODE=1', 'ExecStart=/srv/project/env/bin/python -m evidence run %i',
                     'WorkingDirectory=/srv/project/code'):
            self.assertIn(line, service)
        timer = (out / 'blueberry-evidence-rma-col.timer').read_text()
        for line in ('OnCalendar=*-*-01 04:30:00', 'Persistent=true', 'RandomizedDelaySec=1h',
                     'Unit=blueberry-evidence@rma-col.service'):
            self.assertIn(line, timer)
        self.assertEqual(report['jobs'][0]['id'], 'rma-col')
        self.assertIsNone(report['jobs'][0]['outcome'])


if __name__ == '__main__':
    unittest.main()
