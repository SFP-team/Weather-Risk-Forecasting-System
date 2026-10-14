"""Build dist/enso.json from NOAA CPC's Oceanic Nino Index (ONI v5) for the Year-round planner.

ONI is the 3-month running mean of ERSSTv5 sea-surface temperature anomaly in the Nino 3.4 region. NOAA counts
El Nino (La Nina) conditions when ONI is at or above +0.5 (at or below -0.5) for at least five consecutive
overlapping 3-month seasons. Each season is stored under its centre month (DJF -> January). US Government work,
public domain. Run: python3 scripts/build_enso.py
"""
import json
import urllib.request
from pathlib import Path

URL = 'https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt'
SEASONS = ('DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ')
FIRST_YEAR = 2010
THRESHOLD = 0.5
RUN = 5


def parse(text):
    rows = []
    for line in text.splitlines()[1:]:
        parts = line.split()
        if len(parts) == 4 and parts[0] in SEASONS:
            rows.append({'year': int(parts[1]), 'month': SEASONS.index(parts[0]) + 1, 'oni': float(parts[3])})
    return rows


def phases(rows):
    """El Nino / La Nina label per season under NOAA's five-consecutive-season rule; None otherwise."""
    out = [None] * len(rows)
    for name, hit in (('el_nino', lambda v: v >= THRESHOLD), ('la_nina', lambda v: v <= -THRESHOLD)):
        start = None
        for i, row in enumerate([*rows, {'oni': 0.0}]):
            if i < len(rows) and hit(row['oni']):
                start = i if start is None else start
            elif start is not None:
                if i - start >= RUN:
                    out[start:i] = [name] * (i - start)
                start = None
    return out


def main():
    with urllib.request.urlopen(URL, timeout=60) as response:
        rows = parse(response.read().decode())
    labels = phases(rows)  # the rule needs the full series; filtering comes after
    months = [{**row, 'phase': label} for row, label in zip(rows, labels) if row['year'] >= FIRST_YEAR]
    data = {'source': {'title': 'NOAA CPC Oceanic Nino Index (ONI, ERSSTv5)', 'url': URL,
                       'rule': f'El Nino (La Nina): ONI >= +{THRESHOLD} (<= -{THRESHOLD}) for at least {RUN} consecutive '
                               'overlapping 3-month seasons. Each season is stored under its centre month.'},
            'months': months}
    target = Path(__file__).resolve().parents[1] / 'dist/enso.json'
    target.write_text(json.dumps(data, separators=(',', ':')) + '\n')
    print(json.dumps({'months': len(months), 'last': months[-1]}))


if __name__ == '__main__':
    main()
