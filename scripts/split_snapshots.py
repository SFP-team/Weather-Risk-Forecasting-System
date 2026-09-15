"""Split the server's reports/ui_snapshots.json into dist/snapshots.json (index) plus one file per site.

Usage: python3 scripts/split_snapshots.py /path/to/ui_snapshots.json
The index carries only site identity, group, production status and the hourly source site; the full
record is fetched by the frontend when a preset is selected. Review the public fields before committing.
"""
import json
import re
import sys
from pathlib import Path

REFERENCE = ('Citra', 'Waldo', 'Papanduva')


def main(source):
    sites = json.loads(Path(source).read_text())['sites']
    out = Path('dist/snapshots')
    out.mkdir(exist_ok=True)
    for stale in out.glob('*.json'):
        stale.unlink()
    index = {}
    for name, record in sites.items():
        slug = re.sub(r'[^A-Za-z0-9]+', '-', name).strip('-').lower()
        (out / f'{slug}.json').write_text(json.dumps(record, separators=(',', ':'), allow_nan=False))
        site = record['site']
        index[name] = {'site': {k: site[k] for k in ('name', 'lat', 'lon', 'region', 'county') if k in site},
                       'file': f'snapshots/{slug}.json',
                       'group': 'Reference' if name in REFERENCE else site.get('region', 'Panel'),
                       'production': record['production']['status'],
                       'hourly_source': record['hourly_source']['site'] if record.get('hourly_source') else None}
    Path('dist/snapshots.json').write_text(json.dumps({'sites': index}, indent=1, allow_nan=False))
    print(json.dumps({'sites': len(index), 'groups': sorted({v['group'] for v in index.values()})}))


if __name__ == '__main__':
    main(sys.argv[1])
