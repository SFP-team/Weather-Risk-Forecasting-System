"""Watchdog for the private weather API service, run every 5 minutes by a systemd user timer.

It never starts a stopped service: an intentional stop stays stopped. When the service is active it:
- restarts it after two consecutive failed health checks, or when one analysis has held the busy lock longer than
  BUSY_LIMIT_S (a hung request would otherwise block every user until someone notices);
- rotates the API's stdout log, which systemd appends to without rotation.
Standard library only, so it also runs with the system python3.
"""
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

PROJECT = Path('/media/fpt/fpt2/Weather_Claude')
SERVICE = 'blueberry-ui-api.service'
HEALTH = 'http://127.0.0.1:8787/api/health'
BUSY_LIMIT_S = 900
FAILURES_BEFORE_RESTART = 2
LOG_LIMIT_BYTES = 20 * 1024 ** 2
LOG_KEEP = 5


def systemctl(*args):
    return subprocess.run(['systemctl', '--user', *args], capture_output=True, text=True, timeout=60)


def health(timeout=10):
    """Parsed health JSON, or None when the API does not answer."""
    request = urllib.request.Request(HEALTH, headers={'Host': '127.0.0.1:8787', 'User-Agent': 'api-watchdog'})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except Exception:
        return None


def rotate(path, limit=LOG_LIMIT_BYTES, keep=LOG_KEEP):
    """Copy-and-truncate rotation: systemd keeps its append handle open, so the file must not be renamed away."""
    if not path.exists() or path.stat().st_size <= limit:
        return False
    for index in range(keep - 1, 0, -1):
        older = path.with_name(f'{path.name}.{index}')
        if older.exists():
            os.replace(older, path.with_name(f'{path.name}.{index + 1}'))
    shutil.copyfile(path, path.with_name(f'{path.name}.1'))
    with open(path, 'r+b') as handle:
        handle.truncate(0)
    return True


def decide(active, status, failures):
    """Pure decision: (action, failures). action is 'none', 'restart_unreachable' or 'restart_busy'."""
    if not active:
        return 'none', 0
    if status is None:
        failures += 1
        return ('restart_unreachable', 0) if failures >= FAILURES_BEFORE_RESTART else ('none', failures)
    if (status.get('busy_seconds') or 0) > BUSY_LIMIT_S:
        return 'restart_busy', 0
    return 'none', 0


def main(project=PROJECT):
    state_path = project / 'state/ops/api_watchdog.json'
    log_path = project / 'logs/ops/api_watchdog.jsonl'
    state_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    active = systemctl('is-active', SERVICE).stdout.strip() == 'active'
    status = health() if active else None
    action, failures = decide(active, status, state.get('failures', 0))
    entry = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'active': active, 'action': action,
             'failures': failures, 'status': status.get('status') if status else None,
             'busy_seconds': status.get('busy_seconds') if status else None}
    if action != 'none':
        entry['restart_returncode'] = systemctl('restart', SERVICE).returncode
    entry['rotated_api_log'] = rotate(project / 'logs/location_api.log')
    rotate(log_path, limit=5 * 1024 ** 2)
    with open(log_path, 'a') as handle:
        handle.write(json.dumps(entry) + '\n')
    state_path.write_text(json.dumps({'failures': failures, 'last': entry}))
    return 0


if __name__ == '__main__':
    sys.exit(main())
