"""Write dist/benchmark-calendars.json from the benchmark registry for the Season ribbon tab.

Usage: python3 scripts/build_benchmark_calendars.py   (from the repository root)
The ribbon shows these published bloom, harvest and planting months beside the model for saved benchmark sites and
for points within 10 km of one. Rerun after editing pipelines/weather/benchmark_sites.json.
"""
import json
from pathlib import Path

SOURCE = Path('pipelines/weather/benchmark_sites.json')
TARGET = Path('dist/benchmark-calendars.json')
FIELDS = ('id', 'name', 'admin1', 'country', 'lat', 'lon', 'bloom_months', 'harvest_months', 'planting_months',
          'protection', 'production_system', 'evidence_level', 'confidence')


def main():
    registry = json.loads(SOURCE.read_text())
    sites = [{**{key: site.get(key) for key in FIELDS},
              'sources': [{'title': source.get('title'), 'url': source.get('url')} for source in site.get('sources', [])]}
             for site in sorted(registry['sites'], key=lambda site: site['id'])]
    payload = {'source': SOURCE.as_posix(), 'compiled': registry.get('compiled'), 'sites': sites}
    TARGET.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n')
    print(f'{TARGET}: {len(sites)} sites')


if __name__ == '__main__':
    main()
