"""Build the browser's public Natural Earth reference bundle, not weather data.

Requires Python 3 and npx. Run: python3 scripts/build-place-index.py
Mapshaper is pinned below and runs only during reference generation.
Raw inputs live in a temporary directory and are removed automatically. To reuse
server-side inputs, pass --source-dir /path/to/cache. Keep that cache outside the
repository, on the designated data server. Only derived outputs belong in dist.
"""
import argparse
import gzip
import hashlib
import json
import subprocess
import tempfile
import urllib.request
from pathlib import Path

COMMIT = 'f1890d9f152c896d250a77557a5751a93d494776'
BASE = f'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/{COMMIT}/geojson/'
SOURCES = [
    ('ne_10m_admin_0_countries', '5.1.1', '239eec57ac17f100a11e2536cffc56752c318b50ae765b0918ff7aab4ce8f255'),
    ('ne_10m_admin_1_states_provinces', '5.1.1', '22d0e3ad85eb3e27f17cabf8ba2d50e554fbc27a87796ff891d958185da62fb5'),
    ('ne_10m_populated_places', '5.1.2', '9b8e3de09048ef00dfc70357dbb9fa324493f214b5e0ae4daf1aa79a8d10116b'),
]
MAPSHAPER = 'mapshaper@0.6.113'
INTERVAL_METERS = 250
QUANTIZATION = 10000001
EXCLUDED_PLACES = {'scientific station', 'meteorological station', 'historic place'}


def compact(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def source(name, checksum, directory):
    path = directory / f'{name}.geojson'
    if not path.exists():
        with urllib.request.urlopen(BASE + path.name, timeout=180) as response:
            path.write_bytes(response.read())
    data = path.read_bytes()
    if hashlib.sha256(data).hexdigest() != checksum:
        raise ValueError(f'Source checksum differs: {name}')
    return json.loads(data)['features']


def polygons(feature):
    geometry = feature['geometry']
    if geometry['type'] == 'Polygon':
        return [geometry['coordinates']]
    if geometry['type'] == 'MultiPolygon':
        return geometry['coordinates']
    raise ValueError(f'Unexpected geometry: {geometry["type"]}')


def name(properties, *keys):
    for key in keys:
        value = properties.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def build(source_directory, work, output):
    countries, regions, settlements = [source(n, h, source_directory) for n, _, h in SOURCES]
    country_ids = {feature['properties']['ADM0_A3']: i for i, feature in enumerate(countries)}
    entities = []
    features = []
    for index, feature in enumerate(countries + regions):
        props = feature['properties']
        country = index if index < len(countries) else country_ids[props['adm0_a3']]
        entities.append([name(props, 'NAME_EN', 'name_en', 'NAME_LONG', 'name', 'NAME'), country])
        # Explode before simplification so keep-shapes protects each island,
        # rather than only the largest polygon of a multi-island country.
        for rings in polygons(feature):
            features.append({'type': 'Feature', 'properties': {'entity': index},
                             'geometry': {'type': 'Polygon', 'coordinates': rings}})
    area_source = work / 'areas.geojson'
    area_source.write_text(compact({'type': 'FeatureCollection', 'features': features}))
    topology_path = work / 'areas.topojson'
    subprocess.run(['npx', '--yes', MAPSHAPER, '-i', str(area_source),
                    '-simplify', 'dp', f'interval={INTERVAL_METERS}', 'keep-shapes',
                    '-o', 'format=topojson', f'quantization={QUANTIZATION}', str(topology_path)],
                   check=True)
    topology = json.loads(topology_path.read_text())
    arc_bounds = []
    for arc in topology['arcs']:
        x = y = 0
        xs, ys = [], []
        for dx, dy in arc:
            x += dx
            y += dy
            xs.append(x)
            ys.append(y)
        arc_bounds.append([min(xs), min(ys), max(xs), max(ys)])
    areas = []
    for geometry in topology['objects']['areas']['geometries']:
        if not geometry['type']:
            continue
        parts = [geometry['arcs']] if geometry['type'] == 'Polygon' else geometry['arcs']
        for rings in parts:
            bounds = [arc_bounds[arc if arc >= 0 else ~arc] for ring in rings for arc in ring]
            bbox = [min(b[0] for b in bounds), min(b[1] for b in bounds),
                    max(b[2] for b in bounds), max(b[3] for b in bounds)]
            areas.append([geometry['properties']['entity'], bbox, rings])
    places = []
    for feature in settlements:
        props = feature['properties']
        if props['FEATURECLA'].lower() in EXCLUDED_PLACES:
            continue
        display_name = name(props, 'NAME_EN', 'NAMEASCII', 'NAME')
        if display_name:
            lon, lat = feature['geometry']['coordinates'][:2]
            places.append([display_name, round(lon, 5), round(lat, 5)])
    metadata = {
        'title': 'Local place reference',
        'format_version': 1,
        'attribution': 'Made with Natural Earth. Public domain.',
        'license': 'Public domain',
        'license_url': 'https://www.naturalearthdata.com/about/terms-of-use/',
        'source_commit': COMMIT,
        'source_release': 'Natural Earth vector v5.1.2',
        'sources': [{'dataset': n, 'version': v, 'url': BASE + n + '.geojson', 'sha256': h}
                    for n, v, h in SOURCES],
        'processing': {
            'tool': MAPSHAPER,
            'simplification': 'Shared-topology spherical Douglas-Peucker, each polygon part protected by keep-shapes',
            'interval_m': INTERVAL_METERS,
            'quantization': QUANTIZATION,
            'settlement_coordinates_decimal_places': 5,
            'excluded_place_classes': sorted(EXCLUDED_PLACES),
            'english_names': 'NAME_EN/name_en, then dataset romanized or ASCII name',
            'compression': 'Minified UTF-8 JSON with shared delta-encoded quantized arcs, gzip level 9',
        },
        'coverage': {
            'countries_and_territories': len(countries),
            'admin1_areas': len(regions),
            'settlements': len(places),
            'input_polygon_parts': len(features),
            'output_polygon_parts': len(areas),
        },
        'limitations': [
            'Cartographic reference at 1:10 million, not an address lookup or legal boundary determination.',
            'Country and region come only from polygon containment, never from the nearest settlement.',
            'Source coastlines and borders are generalized; 250 m simplification and coordinate quantization add approximation. Small islands and near-shore or border points can be unresolved or misclassified.',
            'Natural Earth uses de facto boundaries and may not reflect current administrative changes or every jurisdictional viewpoint.',
            'Admin-1 coverage and naming vary by country. Some territories and tiny countries have no named admin-1 area.',
            'Nearest means nearest represented settlement, not nearest village, address, farm or inhabited point. Natural Earth samples smaller towns and favors regional significance.',
            'Distances are great-circle estimates on a sphere of radius 6371.0088 km, not road distances.',
            'A Near label requires a containing country and a represented settlement within 100 km. Offshore points retain coordinate labels even when a city is nearby.',
            'No containing polygon means ocean or unrepresented land; it does not prove the point is ocean. Exact shared boundaries remain unresolved rather than selecting a side.',
            'Source polygons are split at the antimeridian. Longitude -180 and 180 are checked at both seams; no nearest-city country fallback is used.',
            'Reference polygons are not topology-certified. Review mapshaper intersection diagnostics; border/coast and overlap classifications need independent validation for legal or operational use.',
        ],
        'boundary_policy_url': 'https://www.naturalearthdata.com/about/disputed-boundaries-policy/',
        'schema': {
            'entities': '[display name or null, containing country entity index]; country entities come first',
            'areas': '[entity index, quantized bounds [xmin,ymin,xmax,ymax], polygon rings of TopoJSON arc indexes]',
            'arcs': 'TopoJSON delta-encoded arcs; a negative ring index reverses arc ~index',
            'places': '[English or romanized name, longitude, latitude]',
            'transform': 'TopoJSON scale and translate from quantized positions to longitude/latitude',
        },
    }
    bundle = {'version': 1, 'metadata': metadata, 'country_count': len(countries),
              'entities': entities, 'areas': areas, 'arcs': topology['arcs'],
              'transform': topology['transform'], 'places': places}
    encoded = compact(bundle).encode('utf-8')
    compressed = gzip.compress(encoded, compresslevel=9, mtime=0)
    output.mkdir(parents=True, exist_ok=True)
    (output / 'places-v1.json.gz').write_bytes(compressed)
    metadata['artifact'] = {'file': 'places-v1.json.gz', 'bytes': len(compressed),
                            'uncompressed_bytes': len(encoded), 'sha256': hashlib.sha256(compressed).hexdigest()}
    (output / 'provenance.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'coverage': metadata['coverage'], 'artifact': metadata['artifact']}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, help='Existing raw reference cache, outside the repository')
    parser.add_argument('--output', type=Path, default=Path(__file__).resolve().parents[1] / 'dist' / 'geography')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='weather-place-index-') as temporary:
        work = Path(temporary)
        build(args.source_dir or work, work, args.output)
