"""Read-only archive extraction and bounded audit/report generation."""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import sqlite3
import subprocess

import numpy as np
import pandas as pd
import requests
from shapely.geometry import Point, shape
from shapely import make_valid
from shapely.prepared import prep
import zarr

from discover import write_json
from pilot import GROUPS, NAMES, digest, nearest_indices, quality

ROOT = Path('/media/fpt/fpt2/Weather_Claude')
LAND_API = 'https://api.github.com/repos/nvkelso/natural-earth-vector/contents/geojson/ne_10m_land.geojson'


def fetch_land(root):
    target = root / 'data/reference/ne_10m_land.geojson'
    metadata_path = target.with_suffix('.provenance.json')
    if target.exists() and metadata_path.exists():
        metadata = json.loads(metadata_path.read_text())
        if digest(target.read_bytes()) != metadata['sha256']:
            raise RuntimeError('Land-mask checksum mismatch')
        return metadata
    response = requests.get(LAND_API, timeout=(15, 60))
    response.raise_for_status()
    info = response.json()
    if not re.fullmatch('[0-9a-f]{40}', info['sha']) or info['size'] > 32*1024**2:
        raise ValueError('Invalid/unbounded land-mask metadata')
    url = info['download_url']
    if not url.startswith('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/'):
        raise ValueError('Unexpected land-mask host/path')
    response = requests.get(url, timeout=(15, 120), stream=True)
    response.raise_for_status()
    chunks, size = [], 0
    for chunk in response.iter_content(1024*1024):
        size += len(chunk)
        if size > 32*1024**2:
            raise ValueError('Land-mask payload exceeded bound')
        chunks.append(chunk)
    data = b''.join(chunks)
    blob_sha = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    if blob_sha != info['sha'] or len(data) != info['size']:
        raise ValueError('Land-mask source blob verification failed')
    obj = json.loads(data)
    if obj['type'] != 'FeatureCollection' or not obj['features']:
        raise ValueError('Invalid land-mask GeoJSON')
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix('.partial')
    tmp.write_bytes(data)
    os.replace(tmp, target)
    metadata = {'source': 'Natural Earth 1:10 million land polygons', 'url': url,
                'git_blob_sha': info['sha'], 'sha256': digest(data), 'bytes': len(data),
                'retrieved': datetime.now(timezone.utc).isoformat(),
                'license': 'public domain', 'note': 'Cartographic mask; small islands and coastlines may be imperfect. Not a field boundary.'}
    write_json(metadata_path, metadata)
    return metadata


class LandMask:
    def __init__(self, root):
        path = root / 'data/reference/ne_10m_land.geojson'
        self.metadata = json.loads(path.with_suffix('.provenance.json').read_text())
        data = path.read_bytes()
        if digest(data) != self.metadata['sha256']:
            raise RuntimeError('Land-mask checksum mismatch')
        self.geometries = []
        self.repaired = 0
        self.excluded_placeholders = 0
        for feature in json.loads(data)['features']:
            # Natural Earth includes an explicitly artificial polygon at 0, 0.
            # Exclude its source label, not a coordinate box that could hide land.
            if str((feature.get('properties') or {}).get('featurecla') or '').casefold() == 'null island':
                self.excluded_placeholders += 1
                continue
            geometry = shape(feature['geometry'])
            if not geometry.is_valid:
                geometry = make_valid(geometry)
                self.repaired += 1
            self.geometries.append(prep(geometry))
        self.metadata = {**self.metadata, 'processing_version': 'land-mask-v2',
                         'excluded_null_island_features': self.excluded_placeholders}

    def covers(self, lat, lon):
        point = Point((lon+180) % 360-180, lat)
        return any(g.covers(point) for g in self.geometries)


def km_distance(lat1, lon1, lat2, lon2):
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dl = math.radians((lon2-lon1+180) % 360-180)
    a = math.sin((p2-p1)/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 6371.0088*2*math.asin(math.sqrt(min(1., max(0., a))))


def extract(root, lat, lon, land, padding=False):
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError('Latitude/longitude must be finite and in range')
    request = {'latitude': lat, 'longitude': lon}
    if not land.covers(lat, lon):
        return None, {'status': 'unsupported_location', 'request': request,
                      'reason': 'Not land in the supplied cartographic mask; ocean or unresolved small island/coastline. No inland snapping.'}
    state = json.loads((root / 'state/global.json').read_text())
    if state['status'] != 'complete':
        raise RuntimeError('Global archive has not completed validation')
    index = pd.date_range('2010-01-01', '2025-12-31')
    frame = pd.DataFrame({'time': index})
    provenance = []
    for source in ('met_daily', 'solar_daily'):
        group = zarr.open_consolidated(str(root / 'data/normalized/global' / source), mode='r')
        if not group.attrs.get('complete') or not np.array_equal(group['time'][:], np.arange(5844)):
            raise RuntimeError('Incomplete or inconsistent archive group')
        lats, lons = group['lat'][:], group['lon'][:]
        y, x = nearest_indices(lats, lons, lat, lon)
        for variable in GROUPS[source]:
            frame[NAMES[variable]] = group[NAMES[variable]][:, y, x]
        provenance.append({'source': source, 'profile': group.attrs['profile'],
                           'source_latitude': float(lats[y]), 'source_longitude': float(lons[x]),
                           'source_cell_center_on_land': bool(land.covers(float(lats[y]), float(lons[x]))),
                           'distance_km': km_distance(lat, lon, float(lats[y]), float(lons[x])),
                           'units': {NAMES[v]: group[NAMES[v]].attrs['units'] for v in GROUPS[source]}})
    if not padding:
        frame = frame.loc[frame.time >= '2011-01-01'].reset_index(drop=True)
    qc = quality(frame)
    # Preserve source values; expose screening separately from acquisition QC.
    # 1,000 mm/day is an investigation threshold, not a universal physical bound.
    suspect_rain = frame.precip_mm > 1000
    frame['precip_suspect_extreme'] = suspect_rain
    metadata = {'status': 'weather_available', 'request': request, 'rows': len(frame),
                'start': str(frame.time.min().date()), 'end': str(frame.time.max().date()),
                'time_standard': 'UTC', 'sources': provenance, 'qc': qc,
                'screening': {'version': 'rain-extreme-screen-v1',
                              'precip_suspect_threshold_mm_day': 1000,
                              'precip_suspect_days': int(suspect_rain.sum()),
                              'precip_missing_days': int(frame.precip_mm.isna().sum()),
                              'rainfall_risk_admissible': not bool(suspect_rain.any() or frame.precip_mm.isna().any()),
                              'policy': 'Preserve source values and boolean flag; decline rainfall-risk metrics for windows containing suspect or missing precipitation. Passing this screen is not scientific validation.'},
                'land_mask': land.metadata, 'land_geometry_repairs': land.repaired,
                'limitations': ['Gridded weather, not on-farm observations or a cultivar recommendation.',
                                'Coastal source cells may represent mixed land/ocean.',
                                'UTC daily aggregation is not a local biological day.']}
    return frame, metadata


def global_report(root):
    state = json.loads((root / 'state/global.json').read_text())
    if state['status'] != 'complete':
        raise RuntimeError('Global worker not complete')
    plan = json.loads((root / 'state/global_download_plan.json').read_text())
    summary = defaultdict(lambda: {'tiles': 0, 'valid': 0, 'missing': 0, 'invalid': 0, 'min': None, 'max': None})
    with sqlite3.connect(f'file:{root}/state/jobs.sqlite?mode=ro', uri=True) as db:
        rows = db.execute('SELECT id,status,qc FROM tiles').fetchall()
        if {r[0] for r in rows} != {j['id'] for j in plan['jobs']}:
            raise RuntimeError('Tile inventory does not match download plan')
        for key, status, qc in rows:
            if status != 'validated':
                raise RuntimeError(f'Unvalidated tile: {key}')
            variable = key.split('/')[1]
            stats = json.loads(qc)[NAMES[variable]]
            out = summary[variable]
            out['tiles'] += 1
            for field in ('valid', 'missing', 'invalid'):
                out[field] += stats[field]
            if stats['min'] is not None:
                out['min'] = stats['min'] if out['min'] is None else min(out['min'], stats['min'])
                out['max'] = stats['max'] if out['max'] is None else max(out['max'], stats['max'])
        transfer = db.execute("SELECT value FROM counters WHERE name='received_bytes'").fetchone()[0]
    for source in ('met_daily', 'solar_daily'):
        dimensions = plan['sources'][source]
        expected = 5844*dimensions['lat_count']*dimensions['lon_count']
        for variable in GROUPS[source]:
            count = summary[variable]
            if count['valid']+count['missing'] != expected or count['invalid']:
                raise RuntimeError('Global coverage/QC count mismatch')
    report = {'acquisition_status': 'complete', 'core_handoff_status': 'in_progress',
              'validated_tiles': len(rows), 'variables': dict(summary), 'received_weather_bytes': transfer,
              'project_disk_bytes': int(subprocess.check_output(['du', '-sb', str(root)], text=True).split()[0]),
              'start': '2010-01-01', 'baseline_start': '2011-01-01', 'end': '2025-12-31',
              'missing_count_scope': 'All native cells, including oceans; not a land-only coverage percentage.',
              'independent_station_validation': 'pending', 'copernicus_comparison': 'pending_user_setup',
              'source': 'https://power.larc.nasa.gov/docs/services/aws/'}
    write_json(root / 'reports/global_coverage.json', report)
    lines = ['# Global daily weather coverage audit', '',
             f'Validated tiles: {len(rows):,}. Acquisition: complete. Full core handoff: still in progress.', '',
             'Acquisition 2010–2025; analysis baseline 2011–2025. NASA POWER native grids, UTC days.', '',
             '| Variable | Valid values | Missing values | Invalid values |', '|---|---:|---:|---:|']
    for name, q in summary.items():
        lines.append(f'| {name} | {q["valid"]:,} | {q["missing"]:,} | {q["invalid"]:,} |')
    lines += ['', 'Counts include oceans. Missingness is retained, never converted to zero.',
              f'Recorded weather response bytes: {transfer:,}. This excludes dependency installation and metadata discovery outside the tracked client.',
              'Independent station comparison, complete interruption testing and final core sign-off remain pending.',
              '[NASA POWER source documentation](https://power.larc.nasa.gov/docs/services/aws/)']
    (root / 'reports/GLOBAL_COVERAGE.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps(report), flush=True)


def demos(root, land):
    sites = json.loads((root / 'config/sites.json').read_text())
    tests = []
    for site in sites:
        frame, metadata = extract(root, site['lat'], site['lon'], land)
        if frame is None or len(frame) != 5479:
            raise RuntimeError('Pilot coordinate extraction failed')
        tests.append({'site': site['id'], 'rows': len(frame), 'status': metadata['status']})
        if site['name'] not in ('Citra', 'Waldo', 'Papanduva'):
            continue
        lines = [f'# {site["name"]}: historical weather demonstration', '',
                 '2011–2025, UTC days. Gridded estimates, not station measurements. No cultivar or flowering/harvest recommendation.', '',
                 '| Year | Mean temperature °C | Rain mm | Days Tmin < 0°C | Days Tmax ≥ 35°C |',
                 '|---|---:|---:|---:|---:|']
        for year, rows in frame.groupby(frame.time.dt.year):
            complete = rows[['tmean_c', 'precip_mm', 'tmin_c', 'tmax_c']].notna().all().all()
            if not complete:
                lines.append(f'| {year} | unavailable | unavailable | unavailable | unavailable |')
            else:
                lines.append(f'| {year} | {rows.tmean_c.mean():.2f} | {rows.precip_mm.sum():.1f} | {(rows.tmin_c < 0).sum()} | {(rows.tmax_c >= 35).sum()} |')
        lines += ['', 'These calendar-year cold/heat counts are descriptive thresholds, not stage-specific damage probabilities.',
                  'Flowering and harvest windows are deliberately not invented; phenology calibration remains separate.']
        path = root / 'reports/demos' / site['id']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.with_suffix('.md').write_text('\n'.join(lines)+'\n')
        write_json(path.with_suffix('.json'), metadata)
    ocean_frame, ocean = extract(root, 0., -140., land)
    if ocean_frame is not None or ocean['status'] != 'unsupported_location':
        raise RuntimeError('Ocean negative control failed')
    tests.append({'case': 'ocean_negative_control', 'status': ocean['status']})
    for lat, lon in [(91., 0.), (0., 181.), (float('nan'), 0.)]:
        try:
            extract(root, lat, lon, land)
        except ValueError:
            continue
        raise RuntimeError('Invalid-coordinate test failed')
    write_json(root / 'reports/extraction_tests.json', {'passed': True, 'results': tests, 'invalid_coordinate_cases': 3})
    print(json.dumps({'extraction_tests': 'passed', 'pilot_locations': 14, 'ocean_control': 'passed', 'invalid_coordinates': 3}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['land', 'report', 'demos', 'extract'])
    parser.add_argument('--latitude', type=float)
    parser.add_argument('--longitude', type=float)
    parser.add_argument('--include-padding', action='store_true')
    parser.add_argument('--export', action='store_true', help='Write a project-scoped Parquet extract; otherwise read-only summary')
    args = parser.parse_args()
    if args.action == 'land':
        print(json.dumps(fetch_land(ROOT)))
    elif args.action == 'report':
        global_report(ROOT)
    elif args.action == 'demos':
        demos(ROOT, LandMask(ROOT))
    else:
        if args.latitude is None or args.longitude is None:
            parser.error('extract requires --latitude and --longitude')
        frame, metadata = extract(ROOT, args.latitude, args.longitude, LandMask(ROOT), args.include_padding)
        if args.export and frame is not None:
            key = digest(json.dumps(metadata['request'], sort_keys=True).encode())[:24]
            path = ROOT / 'data/derived/extractions' / (key + ('_padding' if args.include_padding else '_baseline') + '.parquet')
            path.parent.mkdir(parents=True, exist_ok=True)
            tmp = path.with_suffix('.partial')
            frame.to_parquet(tmp, index=False)
            os.replace(tmp, path)
            write_json(path.with_suffix('.json'), metadata)
            metadata['export'] = str(path)
        print(json.dumps(metadata, allow_nan=False))


if __name__ == '__main__':
    main()
