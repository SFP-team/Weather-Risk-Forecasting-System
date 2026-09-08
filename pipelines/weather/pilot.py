"""Resumable, bounded NASA POWER pilot. Global expansion is a separate gate."""
import argparse
from collections.abc import MutableMapping
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import math
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import subprocess
import time

import numpy as np
import pandas as pd
import requests
import zarr

from discover import BASE, STORES, write_json

MET = ['T2M_MIN', 'T2M_MAX', 'T2M', 'PRECTOTCORR', 'RH2M', 'WS2M', 'T2MDEW']
GROUPS = {'met_daily': MET, 'solar_daily': ['ALLSKY_SFC_SW_DWN'],
          'met_hourly': ['T2M', 'T2MDEW']}
NAMES = dict(zip(MET, ['tmin_c', 'tmax_c', 'tmean_c', 'precip_mm', 'rh_mean_pct',
                      'wind_mean_m_s', 'dewpoint_mean_c']))
NAMES['ALLSKY_SFC_SW_DWN'] = 'shortwave_mj_m2_day'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def retry_delay(header, attempts, now=None):
    """Honor delay-seconds and HTTP-date Retry-After without shortening backoff."""
    delay = 2**attempts
    header = header.strip()
    if header.isdigit():
        return max(delay, int(header))
    try:
        instant = parsedate_to_datetime(header)
        if instant.tzinfo is None:
            instant = instant.replace(tzinfo=timezone.utc)
        return max(delay, math.ceil((instant - (now or datetime.now(timezone.utc))).total_seconds()))
    except (TypeError, ValueError, OverflowError):
        return delay


def parse_sites(script):
    block = script.split('uf_sites <- tibble::tribble(', 1)[1].split(') %>%', 1)[0]
    pattern = r'"([^"\n]+)"\s*,\s*(-?\d+\.\d+)\s*,\s*(-?\d+\.\d+)\s*,\s*"([^"\n]+)"'
    sites = [{'id': 'UF_' + re.sub(r'[^A-Za-z0-9]+', '_', name), 'name': name,
              'lat': float(lat), 'lon': float(lon), 'region': region}
             for name, lat, lon, region in re.findall(pattern, block)]
    target = [float(re.search(rf'{field}\s*=\s*(-?\d+\.\d+)', script)[1])
              for field in ['target_lat', 'target_lon']]
    sites.append({'id': 'TARGET_PAPANDUVA', 'name': 'Papanduva', 'lat': target[0],
                  'lon': target[1], 'region': 'Santa Catarina'})
    if len(sites) != 14 or len({s['id'] for s in sites}) != 14:
        raise ValueError('Expected exactly 14 unique source sites')
    if any(not (-90 <= s['lat'] <= 90 and -180 <= s['lon'] <= 180) for s in sites):
        raise ValueError('Invalid source coordinates')
    return sites


def nearest_indices(latitudes, longitudes, lat, lon):
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Invalid requested coordinate')
    return (int(np.argmin(abs(latitudes - lat))),
            int(np.argmin(abs((longitudes - lon + 180) % 360 - 180))))


def canonical(values, variable, unit):
    values = np.asarray(values, dtype=np.float64)
    if variable == 'ALLSKY_SFC_SW_DWN':
        factors = {'W m-2': 0.0864, 'MJ/m^2/day': 1., 'MJ/m2/day': 1.,
                   'kW-hr/m^2/day': 3.6, 'kWh/m^2/day': 3.6}
        if unit not in factors:
            raise ValueError(f'Unrecognized solar units: {unit}')
        return values * factors[unit]
    expected = ('C',) if variable.startswith('T2M') else {
        'PRECTOTCORR': ('mm', 'mm/day'), 'RH2M': ('%',), 'WS2M': ('m/s',)}[variable]
    if unit not in expected:
        raise ValueError(f'Unrecognized units for {variable}: {unit}')
    return values


def quality(frame):
    result = {}
    for col in frame.select_dtypes(include='number').columns:
        a = frame[col].to_numpy()
        finite = a[np.isfinite(a)]
        bad = np.isinf(a).sum()
        if col in ('rh_mean_pct',):
            bad += ((finite < 0) | (finite > 100)).sum()
        elif col in ('precip_mm', 'wind_mean_m_s', 'shortwave_mj_m2_day'):
            bad += (finite < 0).sum()
        elif col.endswith('_c'):
            bad += ((finite < -125) | (finite > 80)).sum()
        result[col] = {'valid': int(len(finite)), 'missing': int(np.isnan(a).sum()),
                       'invalid': int(bad), 'min': float(finite.min()) if len(finite) else None,
                       'max': float(finite.max()) if len(finite) else None}
    if all(x in frame for x in ['tmin_c', 'tmean_c', 'tmax_c']):
        result['temperature_order'] = {'invalid': int(((frame.tmin_c > frame.tmean_c + .011)
            | (frame.tmean_c > frame.tmax_c + .011)).sum())}
    if any(v['invalid'] for v in result.values()):
        raise ValueError('Physical quality check failed: ' + json.dumps(result))
    return result


class Downloads:
    def __init__(self, root, scope='pilot'):
        self.root = root
        self.disk_limit = (200 if scope == 'global' else 10) * 1024**3
        self.transfer_limit = (500 if scope == 'global' else 10) * 1024**3
        (root / 'state').mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(root / 'state/jobs.sqlite')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.execute('CREATE TABLE IF NOT EXISTS objects (url TEXT PRIMARY KEY, path TEXT, '
                        'status TEXT, attempts INTEGER DEFAULT 0, bytes INTEGER DEFAULT 0, '
                        'sha256 TEXT, etag TEXT, updated TEXT, error TEXT)')
        self.db.execute('CREATE TABLE IF NOT EXISTS counters (name TEXT PRIMARY KEY, value INTEGER)')
        self.db.execute("INSERT OR IGNORE INTO counters VALUES ('received_bytes', 0)")
        self.db.commit()
        self.session = requests.Session()
        self.session.headers['User-Agent'] = 'BlueberryWeatherResearch/0.1'
        self.last_api = 0.

    def safe_space(self):
        mount = subprocess.check_output(['findmnt', '-n', '-o', 'TARGET', '-T', str(self.root)], text=True).strip()
        if mount != '/media/fpt/fpt2':
            raise RuntimeError('Verified project mount unavailable')
        disk = shutil.disk_usage(self.root)
        if disk.free < disk.total * .2:
            raise RuntimeError('Drive free-space floor reached')
        project_bytes = int(subprocess.check_output(['du', '-sb', str(self.root)], text=True).split()[0])
        if project_bytes > self.disk_limit:
            raise RuntimeError('Project disk ceiling reached')
        if self.db.execute("SELECT value FROM counters WHERE name='received_bytes'").fetchone()[0] > self.transfer_limit:
            raise RuntimeError('Transfer safety ceiling reached')

    def get(self, url, path, api=False):
        row = self.db.execute('SELECT status, sha256, attempts FROM objects WHERE url=?', (url,)).fetchone()
        if row and row[0] == 'failed_terminal':
            raise RuntimeError('Persisted terminal failure requires investigation before retry')
        if path.is_file() and row and row[0] == 'downloaded':
            data = path.read_bytes()
            if digest(data) != row[1]:
                raise RuntimeError(f'Cached checksum mismatch: {path}')
            return data
        attempts = row[2] if row else 0
        self.db.execute('INSERT OR IGNORE INTO objects(url,path,status) VALUES (?,?,?)',
                        (url, str(path), 'pending'))
        self.db.commit()
        while attempts < 5:
            self.safe_space()
            if api:
                time.sleep(max(0., self.last_api + 2 - time.monotonic()))
            attempts += 1
            self.db.execute("UPDATE objects SET attempts=?,status='running',updated=? WHERE url=?",
                            (attempts, datetime.now(timezone.utc).isoformat(), url))
            self.db.commit()
            try:
                with self.session.get(url, timeout=(15, 120), stream=True) as response:
                    response.raise_for_status()
                    parts = []
                    nbytes = 0
                    for part in response.iter_content(1024 * 1024):
                        nbytes += len(part)
                        self.db.execute("UPDATE counters SET value=value+? WHERE name='received_bytes'", (len(part),))
                        self.db.commit()
                        if nbytes > 64 * 1024**2:
                            raise RuntimeError('Individual payload exceeds pilot bound')
                        parts.append(part)
                    data = b''.join(parts)
                    if ('text/html' in response.headers.get('Content-Type', '').lower()
                            or data.lstrip()[:32].lower().startswith((b'<!doctype html', b'<html'))):
                        self.db.execute("UPDATE objects SET status='failed_terminal',error=? WHERE url=?",
                                        ('Unexpected HTML response; payload not published', url))
                        self.db.commit()
                        raise ValueError('Unexpected HTML response; payload not published')
                    path.parent.mkdir(parents=True, exist_ok=True)
                    temp = path.with_name(path.name + '.partial')
                    temp.write_bytes(data)
                    os.replace(temp, path)
                    self.db.execute("UPDATE objects SET status='downloaded',bytes=?,sha256=?,etag=?,error=NULL WHERE url=?",
                                    (len(data), digest(data), response.headers.get('ETag'), url))
                    self.db.commit()
                    print(json.dumps({'event': 'downloaded', 'path': str(path), 'bytes': len(data)}), flush=True)
                    return data
            except requests.RequestException as exc:
                status = getattr(getattr(exc, 'response', None), 'status_code', None)
                terminal = status is not None and 400 <= status < 500 and status not in (408, 429)
                self.db.execute("UPDATE objects SET status=?,error=? WHERE url=?",
                                ('failed_terminal' if terminal or attempts == 5 else 'retry_wait', str(exc), url))
                self.db.commit()
                if terminal or attempts == 5:
                    raise
                header = getattr(getattr(exc, 'response', None), 'headers', {}).get('Retry-After', '')
                delay = retry_delay(header, attempts)
                print(json.dumps({'event': 'retry', 'attempt': attempts, 'delay_seconds': delay}), flush=True)
                time.sleep(delay)
            finally:
                if api:
                    self.last_api = time.monotonic()
        raise RuntimeError(f'Persisted retry budget exhausted for {url}')


class CachedStore(MutableMapping):
    def __init__(self, downloads, name):
        self.d = downloads
        self.name = name
        self.cache = downloads.root / 'data/raw/zarr' / name

    def __getitem__(self, key):
        if key.startswith('/') or '..' in key.split('/'):
            raise KeyError(key)
        return self.d.get(BASE + STORES[self.name] + '/' + key, self.cache / key)

    def __setitem__(self, key, value):
        raise TypeError('Read-only source')

    def __delitem__(self, key):
        raise TypeError('Read-only source')

    def __iter__(self):
        return iter(str(p.relative_to(self.cache)) for p in self.cache.rglob('*') if p.is_file())

    def __len__(self):
        return sum(1 for _ in self)


class Source:
    def __init__(self, downloads, name):
        self.name = name
        self.group = zarr.open_consolidated(CachedStore(downloads, name), mode='r')
        self.lat = self.group['lat'][:]
        self.lon = self.group['lon'][:]
        units = self.group['time'].attrs['units']
        unit, origin = units.split(' since ')
        delta = {'days': 'D', 'hours': 'h'}[unit]
        self.times = pd.DatetimeIndex(np.datetime64(origin) + self.group['time'][:].astype(f'timedelta64[{delta}]')).as_unit('ns')
        if not self.times.is_monotonic_increasing or self.times.has_duplicates:
            raise ValueError('Invalid source time axis')

    def point(self, site, start, end):
        ilat, ilon = nearest_indices(self.lat, self.lon, site['lat'], site['lon'])
        hourly = self.name.endswith('hourly')
        stop = pd.Timestamp(end) + pd.Timedelta(days=1)
        a, b = self.times.searchsorted(pd.Timestamp(start)), self.times.searchsorted(stop)
        times = self.times[a:b]
        expected = pd.date_range(start, stop, freq='h' if hourly else 'D', inclusive='left')
        if not times.equals(expected):
            raise ValueError('Source time axis does not cover requested period')
        frame = pd.DataFrame({'time': times})
        for variable in GROUPS[self.name]:
            arr = self.group[variable]
            if arr.attrs['_ARRAY_DIMENSIONS'] != ['time', 'lat', 'lon']:
                raise ValueError('Unexpected source array dimensions')
            values = arr.oindex[a:b, ilat, ilon]
            frame[NAMES[variable]] = canonical(values, variable, arr.attrs['units'])
        qc = quality(frame)
        provenance = {'site': site, 'source': self.name, 'source_url': BASE + STORES[self.name],
                      'source_version': self.group.attrs.get('version'), 'time_standard': 'UTC',
                      'source_lat': float(self.lat[ilat]), 'source_lon': float(self.lon[ilon]),
                      'source_indices': [ilat, ilon], 'start': start, 'end': end,
                      'rows': len(frame), 'qc': qc, 'normalized_schema': 'pilot-v1',
                      'units': {v: self.group[v].attrs['units'] for v in GROUPS[self.name]}}
        return frame, provenance


def parity(downloads, source, frame, provenance):
    temporal = 'hourly' if source.name.endswith('hourly') else 'daily'
    params = {'parameters': ','.join(GROUPS[source.name]), 'community': 'AG',
              'latitude': provenance['source_lat'], 'longitude': provenance['source_lon'],
              'start': provenance['start'].replace('-', ''), 'end': provenance['end'].replace('-', ''),
              'format': 'JSON', 'time-standard': 'UTC'}
    url = requests.Request('GET', f'https://power.larc.nasa.gov/api/temporal/{temporal}/point', params=params).prepare().url
    obj = json.loads(downloads.get(url, downloads.root / 'data/raw/api' / (digest(url.encode()) + '.json'), api=True))
    fill = obj['header']['fill_value']
    report = {}
    for variable in GROUPS[source.name]:
        records = obj['properties']['parameter'][variable]
        index = frame.time.dt.strftime('%Y%m%d%H' if temporal == 'hourly' else '%Y%m%d')
        if set(records) != set(index):
            raise ValueError('API date coverage differs from bulk source')
        api_values = np.array([records[t] for t in index], dtype=float)
        api_values[api_values == fill] = np.nan
        api_values = canonical(api_values, variable, obj['parameters'][variable]['units'])
        bulk = frame[NAMES[variable]].to_numpy()
        missing_match = bool(np.array_equal(np.isnan(api_values), np.isnan(bulk)))
        max_error = float(np.nanmax(abs(api_values - bulk))) if np.isfinite(bulk).any() else None
        # Each source rounds to .01 source units; API solar rounds to .01 MJ/day.
        tolerance = .011 if variable != 'ALLSKY_SFC_SW_DWN' else .006
        passed = missing_match and max_error is not None and max_error <= tolerance
        report[variable] = {'max_absolute_error': max_error, 'tolerance': tolerance,
                            'missing_masks_match': missing_match, 'passed': passed,
                            'api_unit': obj['parameters'][variable]['units']}
    name = f'{provenance["site"]["id"]}_{source.name}_{provenance["start"]}'
    write_json(downloads.root / f'reports/parity/{name}.json', report)
    if not all(r['passed'] for r in report.values()):
        raise ValueError('API/bulk parity failed: ' + json.dumps(report))
    return report


def save_point(root, scope, frame, provenance):
    directory = root / 'data/normalized/pilot' / scope / provenance['site']['id']
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / (provenance['source'] + '.parquet')
    frame['is_baseline'] = frame.time >= pd.Timestamp('2011-01-01')
    partial = path.with_name(path.name + '.partial')
    frame.to_parquet(partial, index=False)
    check = pd.read_parquet(partial)
    pd.testing.assert_frame_equal(frame, check)
    os.replace(partial, path)
    provenance['parquet_sha256'] = digest(path.read_bytes())
    write_json(path.with_suffix('.json'), provenance)
    print(json.dumps({'event': 'validated_point', 'scope': scope, 'site': provenance['site']['id'],
                      'source': provenance['source'], 'rows': len(frame)}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path('/media/fpt/fpt2/Weather_Claude'))
    parser.add_argument('--sites-script', type=Path)
    parser.add_argument('--scope', choices=['smoke', 'pilot', 'status'], default='smoke')
    args = parser.parse_args()
    root = args.root
    if args.scope == 'status':
        with sqlite3.connect(f'file:{root}/state/jobs.sqlite?mode=ro', uri=True) as db:
            print(json.dumps({'objects': db.execute('SELECT status,count(*),sum(bytes) FROM objects GROUP BY status').fetchall(),
                              'counters': db.execute('SELECT * FROM counters').fetchall()}))
        return
    (root / 'state').mkdir(parents=True, exist_ok=True)
    lock = (root / 'state/worker.lock').open('a')
    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    if args.sites_script:
        sites = parse_sites(args.sites_script.read_text())
        write_json(root / 'config/sites.json', sites)
    else:
        sites = json.loads((root / 'config/sites.json').read_text())
    downloads = Downloads(root)
    downloads.safe_space()
    state = {'scope': args.scope, 'status': 'running', 'pid': os.getpid(), 'started': datetime.now(timezone.utc).isoformat()}
    write_json(root / f'state/{args.scope}.json', state)
    try:
        if args.scope == 'pilot':
            smoke = json.loads((root / 'state/smoke.json').read_text())
            if smoke['status'] != 'complete':
                raise RuntimeError('Smoke gate has not passed')
        for name in GROUPS:
            source = Source(downloads, name)
            selected = [s for s in sites if s['name'] in ('Citra', 'Papanduva')] if args.scope == 'smoke' else sites
            for site in selected:
                start, end = ('2020-01-01', '2020-12-31') if args.scope == 'smoke' else ('2010-01-01', '2025-12-31')
                frame, provenance = source.point(site, start, end)
                if args.scope == 'smoke':
                    parity(downloads, source, frame, provenance)
                save_point(root, args.scope, frame, provenance)
        state.update(status='complete', completed=datetime.now(timezone.utc).isoformat())
    except Exception as exc:
        state.update(status='blocked', error=str(exc), updated=datetime.now(timezone.utc).isoformat())
        raise
    finally:
        write_json(root / f'state/{args.scope}.json', state)


if __name__ == '__main__':
    main()
