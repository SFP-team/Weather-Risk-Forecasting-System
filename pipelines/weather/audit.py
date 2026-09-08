"""Audit pilot artifacts and write truthful stage-specific completion reports."""
import json
from pathlib import Path
import sqlite3
import subprocess

import pandas as pd

from discover import write_json
from pilot import digest, quality

ROOT = Path('/media/fpt/fpt2/Weather_Claude')


def audit(root=ROOT):
    sites = json.loads((root / 'config/sites.json').read_text())
    state = json.loads((root / 'state/pilot.json').read_text())
    if state['status'] != 'complete':
        raise RuntimeError('Pilot worker has not completed')
    results = []
    for site in sites:
        for source in ('met_daily', 'solar_daily', 'met_hourly'):
            path = root / 'data/normalized/pilot/pilot' / site['id'] / (source + '.parquet')
            metadata = json.loads(path.with_suffix('.json').read_text())
            if digest(path.read_bytes()) != metadata['parquet_sha256']:
                raise RuntimeError(f'Checksum mismatch: {path}')
            frame = pd.read_parquet(path)
            hourly = source == 'met_hourly'
            expected = pd.date_range('2010-01-01', '2026-01-01', freq='h' if hourly else 'D', inclusive='left')
            if not pd.DatetimeIndex(frame.time).equals(expected):
                raise RuntimeError('Saved calendar mismatch')
            qc = quality(frame.drop(columns='is_baseline'))
            results.append({'site': site['id'], 'source': source, 'rows': len(frame),
                            'baseline_rows': int(frame.is_baseline.sum()), 'qc': qc,
                            'source_lat': metadata['source_lat'], 'source_lon': metadata['source_lon']})
    missing = sum(q.get('missing', 0) for r in results for q in r['qc'].values())
    with sqlite3.connect(f'file:{root}/state/jobs.sqlite?mode=ro', uri=True) as db:
        counters = dict(db.execute('SELECT name,value FROM counters'))
        objects = db.execute('SELECT status,count(*),sum(bytes) FROM objects GROUP BY status').fetchall()
    report = {'stage': 'pilot_archive', 'status': 'complete', 'sites': len(sites),
              'files': len(results), 'missing_weather_values': missing, 'results': results,
              'downloads': objects, 'counters': counters,
              'global_archive': 'not_started', 'station_validation': 'not_yet_performed',
              'copernicus': 'not_configured' if not Path('/home/fpt/.cdsapirc').is_file() else 'not_tested'}
    write_json(root / 'reports/pilot_audit.json', report)
    lock = subprocess.check_output([str(root / 'env/bin/pip'), 'freeze'], text=True)
    (root / 'reports/environment.lock.txt').write_text(lock)
    lines = ['# Pilot weather archive audit', '', f'Sites: {len(sites)}. Validated files: {len(results)}.',
             f'Missing weather values: {missing}.', '',
             'Acquired period: 2010–2025. Analysis baseline: 2011–2025; 2010 is boundary padding.',
             'Time convention: UTC. Meteorology and solar remain on separate source grids.',
             'The smoke test compared NASA bulk data with its point API; that is consistency testing, not independent station validation.',
             'Global acquisition and independent station validation are not declared complete by this report.', '',
             '| Site | Daily meteorology rows | Daily solar rows | Hourly rows |',
             '|---|---:|---:|---:|']
    for site in sites:
        rows = [r['rows'] for r in results if r['site'] == site['id']]
        lines.append(f'| {site["name"]} | {rows[0]} | {rows[1]} | {rows[2]} |')
    (root / 'reports/PILOT_AUDIT.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'results'}), flush=True)


if __name__ == '__main__':
    audit()
