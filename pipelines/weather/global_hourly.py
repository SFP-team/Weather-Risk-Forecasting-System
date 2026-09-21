"""Finite, resumable land-only hourly cache: NASA POWER MERRA-2 T2M/T2MDEW, 2010-2025.

Fills the raw chunk cache (data/raw/zarr/met_hourly) for every 5x5-cell block that
contains land, through the same checksummed, resumable Downloads.get path the pilot
and global daily runs used. No normalized copy is written: per-cell extraction reads
the cache through Source. Ocean-only blocks are skipped.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import json
from pathlib import Path
import os

import numpy as np
import pandas as pd

from discover import write_json
from pilot import Downloads, Source, GROUPS, NAMES, canonical, quality, digest
from postprocess import LandMask

ROOT = Path('/media/fpt/fpt2/Weather_Claude')
SOURCE = 'met_hourly'
START, END = '2010-01-01', '2026-01-01'
HOURS = 140256
PROFILE = 'power-native-hourly-land-utc-v1'


def now():
    return datetime.now(timezone.utc).isoformat()


def land_blocks(mask, lat, lon, cy, cx):
    """Yield (y, yend, x, xend) for every spatial chunk with at least one land cell."""
    for y in range(0, len(lat), cy):
        for x in range(0, len(lon), cx):
            yend, xend = min(y + cy, len(lat)), min(x + cx, len(lon))
            if any(mask.covers(float(lat[i]), float(lon[j]))
                   for i in range(y, yend) for j in range(x, xend)):
                yield y, yend, x, xend


def build_plan(root, downloads):
    source = Source(downloads, SOURCE)
    a = int(source.times.searchsorted(pd.Timestamp(START)))
    b = int(source.times.searchsorted(pd.Timestamp(END)))
    if b - a != HOURS:
        raise RuntimeError('Hourly time extent mismatch')
    variables = GROUPS[SOURCE]
    chunks = {v: source.group[v].chunks for v in variables}
    if len({chunks[v] for v in variables}) != 1:
        raise RuntimeError('Hourly variables have different chunking')
    ct, cy, cx = chunks[variables[0]]
    for v in variables:
        arr = source.group[v]
        if arr.attrs['_ARRAY_DIMENSIONS'] != ['time', 'lat', 'lon']:
            raise RuntimeError('Unexpected dimension order')
        canonical([0.], v, arr.attrs['units'])
    mask = LandMask(root)
    blocks = list(land_blocks(mask, source.lat, source.lon, cy, cx))
    time_chunks = (b - 1) // ct - a // ct + 1
    jobs = [{'id': f'{SOURCE}/{v}/{y}/{x}', 'variable': v, 'y': [y, yend], 'x': [x, xend], 't': [a, b]}
            for y, yend, x, xend in blocks for v in variables]
    raw_bound = len(jobs) * time_chunks * ct * cy * cx * 4
    # Same conservative decoded-size gate as the daily plan. Measured compression on the
    # already cached hourly objects gives the expected on-disk size for information.
    row = downloads.db.execute("SELECT AVG(bytes) FROM objects WHERE path LIKE ? AND status='downloaded'",
                               (f'%/raw/zarr/{SOURCE}/%',)).fetchone()
    measured = int(row[0] * len(jobs) * time_chunks) if row and row[0] else None
    storage_bound = int(raw_bound * 1.15 + 10 * 1024**3)
    transfer_bound = int(raw_bound * 1.15)
    plan = {'profile': PROFILE, 'created': now(), 'jobs': jobs, 'start': START, 'end': END,
            'time_slice': [a, b], 'time_chunks_per_job': time_chunks, 'land_blocks': len(blocks),
            'total_blocks': -(-len(source.lat) // cy) * -(-len(source.lon) // cx),
            'source_version': source.group.attrs.get('version'), 'job_count': len(jobs),
            'raw_uncompressed_chunk_bytes': raw_bound, 'estimated_compressed_bytes': measured,
            'storage_bound_bytes': storage_bound, 'transfer_bound_bytes': transfer_bound,
            'status': 'ready' if storage_bound <= 200*1024**3 and transfer_bound <= 500*1024**3 else 'blocked_capacity',
            'coverage': 'Land-containing native 5x5 blocks only; ocean cells inside those blocks are retained',
            'land_mask': mask.metadata}
    write_json(root / 'state/global_hourly_plan.json', plan)
    print(json.dumps({k: v for k, v in plan.items() if k != 'jobs'}), flush=True)
    if plan['status'] != 'ready':
        raise RuntimeError('Hourly capacity bounds exceeded')
    return plan


def run(root, downloads, plan):
    if plan['status'] != 'ready':
        raise RuntimeError('Hourly plan not authorized by gates')
    db = downloads.db
    db.execute('CREATE TABLE IF NOT EXISTS tiles (id TEXT PRIMARY KEY,status TEXT,sha256 TEXT,qc TEXT,updated TEXT)')
    db.executemany("INSERT OR IGNORE INTO tiles(id,status) VALUES (?,'pending')", [(j['id'],) for j in plan['jobs']])
    db.commit()
    source = Source(downloads, SOURCE)
    state = {'status': 'running', 'profile': PROFILE, 'started': now(), 'pid': os.getpid(),
             'total_jobs': len(plan['jobs'])}
    write_json(root / 'state/global_hourly.json', state)
    try:
        for n, job in enumerate(plan['jobs'], 1):
            if db.execute('SELECT status FROM tiles WHERE id=?', (job['id'],)).fetchone()[0] != 'validated':
                db.execute("UPDATE tiles SET status='running',updated=? WHERE id=?", (now(), job['id']))
                db.commit()
                src = source.group[job['variable']]
                # Reading through the cached store downloads, checksums and caches the chunks.
                values = canonical(src.oindex[slice(*job['t']), slice(*job['y']), slice(*job['x'])],
                                   job['variable'], src.attrs['units']).astype('f4')
                if values.shape[0] != HOURS:
                    raise RuntimeError('Decoded hourly extent mismatch')
                qc = quality(pd.DataFrame({NAMES[job['variable']]: values.reshape(-1)}))
                db.execute("UPDATE tiles SET status='validated',sha256=?,qc=?,updated=? WHERE id=?",
                           (digest(values.tobytes()), json.dumps(qc), now(), job['id']))
                db.commit()
                print(json.dumps({'event': 'validated_hourly_block', 'completed': n,
                                  'total': len(plan['jobs']), 'id': job['id']}), flush=True)
            state.update(completed_jobs=n, updated=now())
            if n % 20 == 0 or n == len(plan['jobs']):
                write_json(root / 'state/global_hourly.json', state)
        state.update(status='complete', completed=now(),
                     note='Land hourly cache complete; grid data, not station-validated')
    except Exception as exc:
        state.update(status='blocked', error=str(exc), updated=now())
        raise
    finally:
        write_json(root / 'state/global_hourly.json', state)


def status(root, downloads):
    plan_path = root / 'state/global_hourly_plan.json'
    total = len(json.loads(plan_path.read_text())['jobs']) if plan_path.exists() else None
    counts = dict(downloads.db.execute(
        "SELECT status, COUNT(*) FROM tiles WHERE id LIKE ? GROUP BY status", (f'{SOURCE}/%',)).fetchall())
    objects = downloads.db.execute(
        "SELECT COUNT(*), COALESCE(SUM(bytes),0) FROM objects WHERE path LIKE ? AND status='downloaded'",
        (f'%/raw/zarr/{SOURCE}/%',)).fetchone()
    state_path = root / 'state/global_hourly.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    print(json.dumps({'planned_jobs': total, 'tiles': counts, 'cached_objects': objects[0],
                      'cached_bytes': objects[1], 'state': state}, indent=1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['plan', 'run', 'status'])
    args = parser.parse_args()
    downloads = Downloads(ROOT, scope='global')
    if args.action == 'status':
        status(ROOT, downloads)
        return
    lock = (ROOT / 'state/worker.lock').open('a')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    if args.action == 'plan':
        build_plan(ROOT, downloads)
    else:
        run(ROOT, downloads, json.loads((ROOT / 'state/global_hourly_plan.json').read_text()))


if __name__ == '__main__':
    main()
