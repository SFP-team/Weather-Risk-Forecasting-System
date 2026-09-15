"""Bounded southeastern-US evaluation panel: registry, hourly-cell index and missing-cell acquisition.

Hourly temperature/dewpoint is keyed by MERRA-2 source cell (0.5 x 0.625 degrees). A site whose
cell already has a stored hourly series reuses it; only genuinely new cells are fetched, through the
same checksummed pilot path. No global hourly acquisition, no daily re-download.
"""
import argparse
import fcntl
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from discover import ROOT, write_json
from pilot import Downloads, Source, nearest_indices, save_point

# name, lat, lon, region, county, role. Town pins are city centres, not orchard centroids.
PANEL = [
    ('Georgia', 31.511125, -82.460729, 'Georgia', 'Bacon', 'pilot'),
    ('Homerville', 31.037, -82.747, 'Georgia', 'Clinch', 'town'),
    ('Valdosta', 30.833, -83.279, 'Georgia', 'Lowndes', 'town'),
    ('Folkston', 30.831, -82.010, 'Georgia', 'Charlton', 'town'),
    ('Dole', 28.055620, -81.561220, 'Central Florida', 'Polk', 'pilot'),
    ('Clear Springs', 27.820500, -81.825980, 'Central Florida', 'Polk', 'pilot'),
    ('Astin East', 27.733835, -82.236874, 'Central Florida', 'Hillsborough', 'pilot'),
    ('Barben', 27.599210, -81.518480, 'South Florida', 'Highlands', 'pilot'),
    ('Wauchula', 27.547, -81.811, 'South Florida', 'Hardee', 'town'),
    ('Sebring', 27.495, -81.441, 'South Florida', 'Highlands', 'town'),
    ('Lake Placid', 27.297, -81.367, 'South Florida', 'Highlands', 'town'),
    ('River Valley', 27.257661, -82.167300, 'South Florida', 'Sarasota', 'pilot'),
    ('Okeechobee', 27.244, -80.830, 'South Florida', 'Okeechobee', 'town'),
    ('Arcadia', 27.221, -81.868, 'South Florida', 'DeSoto', 'town'),
    ('PF Berry', 27.047660, -81.488100, 'South Florida', 'Highlands', 'pilot'),
]
SCOPES = ('pilot', 'evaluation')


def slug(name):
    return re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')


def registry(root=ROOT):
    pilots = {s['name']: s for s in json.loads((root / 'config/sites.json').read_text())}
    sites = []
    for name, lat, lon, region, county, role in PANEL:
        if role == 'pilot':
            p = pilots[name]
            if abs(p['lat'] - lat) > 1e-7 or abs(p['lon'] - lon) > 1e-7:
                raise ValueError(f'Registry pin for {name} disagrees with the stored pilot coordinate')
            sites.append({**p, 'county': county, 'role': 'pilot'})
        else:
            sites.append({'id': 'EVAL_' + slug(name), 'name': name, 'lat': lat, 'lon': lon,
                          'region': region, 'county': county, 'role': 'town'})
    return sites


def hourly_index(root=ROOT, axes=None):
    """Map source cell -> stored hourly series. Axes come from the source when fetching; otherwise cached."""
    cells = {}
    for scope in SCOPES:
        for meta in sorted((root / 'data/normalized/pilot' / scope).glob('*/met_hourly.json')):
            p = json.loads(meta.read_text())
            if p['rows'] != 140256 or p['start'] != '2010-01-01' or p['end'] != '2025-12-31':
                continue  # only complete 2010-2025 series are usable for winter windows
            key = f"{p['source_indices'][0]},{p['source_indices'][1]}"
            cells.setdefault(key, {'site': p['site']['name'], 'site_id': p['site']['id'], 'scope': scope,
                                   'source_lat': p['source_lat'], 'source_lon': p['source_lon'],
                                   'path': str(meta.with_suffix('.parquet').relative_to(root)),
                                   'parquet_sha256': p['parquet_sha256']})
    index = {'generated': datetime.now(timezone.utc).isoformat(), 'cells': cells}
    if axes is not None:
        index['axes'] = axes
    else:
        previous = root / 'config/hourly_index.json'
        if previous.exists():
            index['axes'] = json.loads(previous.read_text())['axes']
    return index


def cell_key(axes, lat, lon):
    import numpy as np
    ilat, ilon = nearest_indices(np.asarray(axes['lat']), np.asarray(axes['lon']), lat, lon)
    return f'{ilat},{ilon}'


def fetch(root=ROOT):
    """Acquire met_hourly for registry sites whose cell has no stored series. Cached chunks are reused."""
    lock = (root / 'state/worker.lock').open('a')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    sites = registry(root)
    write_json(root / 'config/evaluation_sites.json', sites)
    downloads = Downloads(root, scope='global')  # post-global limits: 200 GiB disk, 500 GiB transfer
    downloads.safe_space()
    before = downloads.db.execute("SELECT value FROM counters WHERE name='received_bytes'").fetchone()[0]
    source = Source(downloads, 'met_hourly')
    axes = {'lat': [float(v) for v in source.lat], 'lon': [float(v) for v in source.lon]}
    index = hourly_index(root, axes)
    state = {'scope': 'evaluation', 'status': 'running', 'pid': os.getpid(),
             'started': datetime.now(timezone.utc).isoformat(), 'fetched': [], 'reused': []}
    write_json(root / 'state/evaluation.json', state)
    try:
        for site in sites:
            key = cell_key(axes, site['lat'], site['lon'])
            if key in index['cells']:
                state['reused'].append({'site': site['name'], 'cell': key, 'from': index['cells'][key]['site']})
                continue
            frame, provenance = source.point(site, '2010-01-01', '2025-12-31')
            save_point(root, 'evaluation', frame, provenance)
            index = hourly_index(root, axes)
            state['fetched'].append({'site': site['name'], 'cell': key})
        after = downloads.db.execute("SELECT value FROM counters WHERE name='received_bytes'").fetchone()[0]
        state.update(status='complete', completed=datetime.now(timezone.utc).isoformat(),
                     transferred_bytes=after - before)
    except Exception as exc:
        state.update(status='blocked', error=str(exc), updated=datetime.now(timezone.utc).isoformat())
        raise
    finally:
        write_json(root / 'state/evaluation.json', state)
        write_json(root / 'config/hourly_index.json', index)
    print(json.dumps(state), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['registry', 'index', 'fetch'])
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    if args.action == 'registry':
        write_json(args.root / 'config/evaluation_sites.json', registry(args.root))
        print(json.dumps(registry(args.root)))
    elif args.action == 'index':
        index = hourly_index(args.root)
        write_json(args.root / 'config/hourly_index.json', index)
        print(json.dumps({k: v['site'] for k, v in index['cells'].items()}))
    else:
        fetch(args.root)
