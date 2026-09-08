"""Gated geographic probes and a finite, resumable native-grid daily archive."""
import argparse
from datetime import datetime, timezone
import fcntl
import json
import math
from pathlib import Path
import os
import sqlite3

import numpy as np
import pandas as pd
from numcodecs import Blosc
import zarr

from discover import write_json
from pilot import Downloads, Source, GROUPS, NAMES, canonical, quality, parity, digest, save_point

ROOT = Path('/media/fpt/fpt2/Weather_Claude')
DAILY = ('met_daily', 'solar_daily')
# Source/QC probes only. These are NOT breeding trials or adaptation evidence.
PROBES = [
    ('florida_north', 29.65, -82.32), ('florida_south', 25.76, -80.19),
    ('georgia', 31.5, -82.5), ('carolina', 35.7, -78.6),
    ('michigan', 43., -86.), ('oregon', 45., -123.),
    ('california', 36.7, -119.8), ('mexico', 19.7, -103.5),
    ('brazil_south', -26.3, -50.1), ('brazil_tropical', -3.1, -60.),
    ('chile', -35.4, -71.7), ('peru', -8.1, -79.),
    ('argentina', -31.4, -64.2), ('uruguay', -34.9, -56.2),
    ('spain', 37.3, -6.9), ('portugal', 38.7, -9.1),
    ('france', 44.8, -.6), ('germany', 52.5, 13.4),
    ('poland', 52.2, 21.), ('scotland', 56.5, -3.),
    ('morocco', 30.4, -9.6), ('south_africa', -33.9, 18.4),
    ('kenya', -.3, 36.1), ('ethiopia_highland', 9., 38.7),
    ('india_north', 30.7, 76.8), ('india_highland', 31.1, 77.2),
    ('india_south', 12.9, 77.6), ('china', 25., 102.7),
    ('japan', 35.7, 139.7), ('vietnam', 11.9, 108.4),
    ('australia_east', -30.3, 153.1), ('tasmania', -42.9, 147.3),
    ('new_zealand', -37.8, 175.3), ('dateline_west', -17.7, 179.9),
    ('dateline_east', -17.7, -179.9), ('alaska', 64.8, -147.7),
    ('northern_norway', 69.6, 18.9), ('antarctica', -80., 0.),
    ('equatorial_africa', 0., 30.), ('ocean_negative_control', 0., -140.),
]


def now():
    return datetime.now(timezone.utc).isoformat()


def run_probes(root, downloads):
    audit = json.loads((root / 'reports/pilot_audit.json').read_text())
    if audit['status'] != 'complete' or audit['missing_weather_values']:
        raise RuntimeError('Pilot acquisition/audit gate not satisfied')
    result = {'status': 'running', 'started': now(), 'probes': [],
              'purpose': 'Engineering/source QC, not independent station or cultivar validation'}
    write_json(root / 'state/probes.json', result)
    try:
        for name in DAILY:
            source = Source(downloads, name)
            for label, lat, lon in PROBES:
                site = {'id': 'PROBE_' + label, 'name': label, 'lat': lat, 'lon': lon,
                        'role': 'source_test_only'}
                frame, provenance = source.point(site, '2010-01-01', '2025-12-31')
                save_point(root, 'probes', frame, provenance)
                # A spread of hemispheres and climates gets independent API-path parity.
                if label in ('chile', 'germany', 'india_highland', 'new_zealand'):
                    short, short_prov = source.point(site, '2020-01-01', '2020-12-31')
                    parity(downloads, source, short, short_prov)
                result['probes'].append({'id': site['id'], 'source': name, 'rows': len(frame), 'qc': provenance['qc']})
                write_json(root / 'state/probes.json', result)
        result.update(status='complete', completed=now())
    except Exception as exc:
        result.update(status='blocked', error=str(exc))
        raise
    finally:
        write_json(root / 'state/probes.json', result)


def build_plan(root, downloads):
    if json.loads((root / 'state/probes.json').read_text())['status'] != 'complete':
        raise RuntimeError('Geographic probe gate not satisfied')
    jobs = []
    source_inventory = {}
    normalized_bytes = raw_bound = 0
    for name in DAILY:
        source = Source(downloads, name)
        a = int(source.times.searchsorted(pd.Timestamp('2010-01-01')))
        b = int(source.times.searchsorted(pd.Timestamp('2026-01-01')))
        if b - a != 5844:
            raise RuntimeError('Global time extent mismatch')
        source_inventory[name] = {'time_slice': [a, b], 'lat_count': len(source.lat),
                                  'lon_count': len(source.lon), 'version': source.group.attrs.get('version')}
        for variable in GROUPS[name]:
            arr = source.group[variable]
            ct, cy, cx = arr.chunks
            if arr.attrs['_ARRAY_DIMENSIONS'] != ['time', 'lat', 'lon']:
                raise RuntimeError('Unexpected dimension order')
            canonical([0.], variable, arr.attrs['units'])
            for y in range(0, len(source.lat), cy):
                for x in range(0, len(source.lon), cx):
                    yend, xend = min(y+cy, len(source.lat)), min(x+cx, len(source.lon))
                    key = f'{name}/{variable}/{y}/{x}'
                    jobs.append({'id': key, 'source': name, 'variable': variable,
                                 'y': [y, yend], 'x': [x, xend], 't': [a, b]})
                    raw_bound += (int((b-1)//ct) - int(a//ct) + 1) * ct * cy * cx * 4
            normalized_bytes += (b-a) * len(source.lat) * len(source.lon) * 4
    # Raw decoded-size allowance is conservative for observed compressed float32 stores.
    # Include 15% overhead and a 10 GiB allowance for pilot/env/reports/temporary work.
    storage_bound = int((raw_bound + normalized_bytes) * 1.15 + 10 * 1024**3)
    transfer_bound = int(raw_bound * 1.15)
    plan = {'profile': 'power-native-daily-utc-v1', 'created': now(), 'jobs': jobs,
            'sources': source_inventory, 'normalized_float32_bytes': normalized_bytes,
            'raw_uncompressed_chunk_bytes': raw_bound, 'storage_bound_bytes': storage_bound,
            'transfer_bound_bytes': transfer_bound, 'job_count': len(jobs),
            'status': 'ready' if storage_bound <= 200*1024**3 and transfer_bound <= 500*1024**3 else 'blocked_capacity',
            'coverage': 'Native global rectangular weather grids including ocean; no land-suitability claim',
            'station_validation': 'not_complete; source parity is not station validation'}
    write_json(root / 'state/global_download_plan.json', plan)
    print(json.dumps({k: v for k, v in plan.items() if k != 'jobs'}), flush=True)
    if plan['status'] != 'ready':
        raise RuntimeError('Global capacity bounds exceeded')
    return plan


def output_group(root, source):
    path = root / 'data/normalized/global' / source.name
    group = zarr.open_group(str(path), mode='a')
    group.attrs.update({'profile': 'power-native-daily-utc-v1', 'source': source.name,
                        'source_version': source.group.attrs.get('version'), 'time_standard': 'UTC',
                        'baseline_start': '2011-01-01', 'padding_start': '2010-01-01',
                        'end': '2025-12-31', 'complete': False})
    for name, values in [('lat', source.lat), ('lon', source.lon), ('time', np.arange(5844))]:
        if name not in group:
            group.array(name, values, overwrite=False)
        elif not np.array_equal(group[name][:], values):
            raise RuntimeError('Existing output coordinates conflict with profile')
        group[name].attrs['_ARRAY_DIMENSIONS'] = [name]
    group['time'].attrs.update({'units': 'days since 2010-01-01 00:00:00', 'calendar': 'proleptic_gregorian'})
    for variable in GROUPS[source.name]:
        src = source.group[variable]
        arr = group.require_dataset(NAMES[variable], shape=(5844, len(source.lat), len(source.lon)),
                                    chunks=(366, src.chunks[1], src.chunks[2]), dtype='f4',
                                    fill_value=np.nan, compressor=Blosc(cname='zstd', clevel=3, shuffle=2))
        arr.attrs.update({'_ARRAY_DIMENSIONS': ['time', 'lat', 'lon'], 'source_variable': variable,
                          'units': 'MJ/m^2/day' if variable == 'ALLSKY_SFC_SW_DWN' else src.attrs['units']})
    return group


def run_global(root, downloads, plan):
    if plan['status'] != 'ready':
        raise RuntimeError('Global plan not authorized by gates')
    db = downloads.db
    db.execute('CREATE TABLE IF NOT EXISTS tiles (id TEXT PRIMARY KEY,status TEXT,sha256 TEXT,qc TEXT,updated TEXT)')
    db.executemany("INSERT OR IGNORE INTO tiles(id,status) VALUES (?,'pending')", [(j['id'],) for j in plan['jobs']])
    db.commit()
    sources = {name: Source(downloads, name) for name in DAILY}
    outputs = {name: output_group(root, source) for name, source in sources.items()}
    state = {'status': 'running', 'started': now(), 'pid': os.getpid(), 'total_tiles': len(plan['jobs'])}
    write_json(root / 'state/global.json', state)
    try:
        for n, job in enumerate(plan['jobs'], 1):
            source, variable = sources[job['source']], job['variable']
            ys, xs = slice(*job['y']), slice(*job['x'])
            target = outputs[job['source']][NAMES[variable]]
            previous = db.execute('SELECT status,sha256 FROM tiles WHERE id=?', (job['id'],)).fetchone()
            if previous[0] == 'validated':
                if digest(target[:, ys, xs].tobytes()) != previous[1]:
                    raise RuntimeError('Previously validated output tile checksum mismatch')
            else:
                downloads.safe_space()
                db.execute("UPDATE tiles SET status='running',updated=? WHERE id=?", (now(), job['id']))
                db.commit()
                src = source.group[variable]
                values = canonical(src.oindex[slice(*job['t']), ys, xs], variable, src.attrs['units']).astype('f4')
                qc = quality(pd.DataFrame({NAMES[variable]: values.reshape(-1)}))
                target[:, ys, xs] = values
                actual = digest(target[:, ys, xs].tobytes())
                if actual != digest(values.tobytes()):
                    raise RuntimeError('Output read-back checksum mismatch')
                db.execute("UPDATE tiles SET status='validated',sha256=?,qc=?,updated=? WHERE id=?",
                           (actual, json.dumps(qc), now(), job['id']))
                db.commit()
                print(json.dumps({'event': 'validated_global_tile', 'completed': n,
                                  'total': len(plan['jobs']), 'id': job['id']}), flush=True)
            state.update(completed_tiles=n, updated=now())
            write_json(root / 'state/global.json', state)
        # Cross-variable temperature ordering is checked after all three fields exist.
        met = outputs['met_daily']
        for y in range(0, len(sources['met_daily'].lat), 15):
            for x in range(0, len(sources['met_daily'].lon), 15):
                values = {name: met[name][:, y:y+15, x:x+15].reshape(-1)
                          for name in ('tmin_c', 'tmean_c', 'tmax_c')}
                quality(pd.DataFrame(values))
        for name, group in outputs.items():
            # Original pilot extraction consistency, using exact source indices.
            for site in json.loads((root / 'config/sites.json').read_text()):
                path = root / 'data/normalized/pilot/pilot' / site['id'] / (name + '.parquet')
                metadata = json.loads(path.with_suffix('.json').read_text())
                frame = pd.read_parquet(path)
                y, x = metadata['source_indices']
                for variable in GROUPS[name]:
                    np.testing.assert_allclose(group[NAMES[variable]][:, y, x], frame[NAMES[variable]],
                                               rtol=1e-6, atol=1e-5, equal_nan=True)
            group.attrs['complete'] = True
            zarr.consolidate_metadata(group.store)
        state.update(status='complete', completed=now(),
                     note='Global daily acquisition/QC complete; not a claim of station or cultivar validation')
    except Exception as exc:
        state.update(status='blocked', error=str(exc), updated=now())
        raise
    finally:
        write_json(root / 'state/global.json', state)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['probes', 'plan', 'run', 'all'])
    args = parser.parse_args()
    lock = (ROOT / 'state/worker.lock').open('a')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    if args.action in ('probes', 'all'):
        run_probes(ROOT, Downloads(ROOT))
    downloads = Downloads(ROOT, scope='global')
    if args.action in ('plan', 'all'):
        plan = build_plan(ROOT, downloads)
    elif args.action == 'run':
        plan = json.loads((ROOT / 'state/global_download_plan.json').read_text())
    if args.action in ('run', 'all'):
        run_global(ROOT, downloads, plan)


if __name__ == '__main__':
    main()
