"""Preflight for the private weather API service: create working folders and refuse to start on a full project drive.

Run by systemd (ExecStartPre) before location_api.py. The root filesystem only gets a warning: the service keeps its
temporary files, cache and logs on the project drive, so a full root disk (the 2026-10-05 tmux failure) must not
stop it.
"""
import json
import shutil
import sys
import time
from pathlib import Path

PROJECT = Path('/media/fpt/fpt2/Weather_Claude')
GIB = 1024 ** 3
PROJECT_FLOOR_GIB = 5
ROOT_WARNING_GIB = 10


def main(project=PROJECT):
    for folder in ('tmp/api', 'logs', 'cache/location_api'):
        (project / folder).mkdir(parents=True, exist_ok=True)
    root_free = shutil.disk_usage('/').free / GIB
    project_free = shutil.disk_usage(project).free / GIB
    report = {'ts': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'root_free_gib': round(root_free, 1),
              'project_free_gib': round(project_free, 1)}
    if root_free < ROOT_WARNING_GIB:
        report['warning'] = 'root filesystem below 10 GiB free; the API still starts because it writes only to the project drive'
    print(json.dumps({'preflight': report}), flush=True)
    if project_free < PROJECT_FLOOR_GIB:
        print(json.dumps({'preflight_refused': f'project drive below {PROJECT_FLOOR_GIB} GiB free'}), file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
