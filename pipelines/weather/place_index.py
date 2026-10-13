"""Place-name search over GeoNames populated places (CC BY 4.0), served by location_api.py at /api/places.

`build` turns a GeoNames dump folder (allCountries.zip, countryInfo.txt, admin1CodesASCII.txt, admin2Codes.txt) into
one SQLite file. Rows are numbered by prominence, so full-text matches read in rowid order list the most prominent
places first and a LIMIT stops early even for a two-letter prefix. `search` matches every query word as a word prefix,
ignoring case and accents, across a place's name, alternate names, second-level area, first-level area and country.

    python place_index.py build <geonames folder> <out.sqlite>
    python place_index.py search <index.sqlite> <query>
"""
import hashlib
import io
import json
import math
import os
import re
import sqlite3
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

FORMAT = 'geonames-places-v1'
SOURCE = {'name': 'GeoNames', 'url': 'https://www.geonames.org/', 'license': 'CC BY 4.0',
          'license_url': 'https://creativecommons.org/licenses/by/4.0/'}
# Abandoned, destroyed and historical places, and historical capitals, are not current settlements.
EXCLUDED = frozenset({'PPLQ', 'PPLW', 'PPLH', 'PPLCH'})
# Ordering only: population, raised to a floor for administrative seats whose population GeoNames lacks.
FLOOR = {'PPLC': 1_000_000, 'PPLA': 100_000, 'PPLG': 100_000, 'PPLA2': 10_000, 'PPLA3': 2_000, 'PPLA4': 1_000,
         'PPLA5': 500}
CODE_ORDER = ('PPLC', 'PPLA', 'PPLG', 'PPLA2', 'PPLA3', 'PPLA4', 'PPLA5', 'PPL', 'PPLS', 'PPLF', 'PPLR', 'STLMT',
              'PPLL', 'PPLX')
MAX_LIMIT = 25
CANDIDATES = 400
SAME_PLACE_KM = 10.0
# Penalty per match tier from `search`, in powers of ten of prominence: an exact 'New York' village loses to New York
# City, 'alma' keeps Alma, Quebec ahead of Almaty, about 70 times larger, and a place that leaves a typed word
# unmatched comes last.
PENALTY = (0.0, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0, 8.0)
COLUMNS = ('id', 'geonameid', 'name', 'norm', 'anorm', 'lat', 'lon', 'country_code', 'county', 'region', 'country',
           'population', 'score')
_SEPARATORS = re.compile(r'[\W_]+')


def fold(text):
    """Case- and accent-free words separated by single spaces, the same rule as the browser's normalizeSearch."""
    text = ''.join(c for c in unicodedata.normalize('NFD', str(text or '')) if not unicodedata.category(c).startswith('M'))
    text = text.lower().replace('.', '').replace("'", '').replace('\u2019', '')
    return _SEPARATORS.sub(' ', text).strip()


def words(*fields):
    """Distinct folded words of names, alternate names and areas: the full-text row of one place."""
    return ' '.join(dict.fromkeys(fold(' '.join(f for f in fields if f)).split()))


def _rows(path):
    with open(path, encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                yield line.rstrip('\n').split('\t')


def _sha256(path):
    digest = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


def build(source, out):
    """Write the index to `out` atomically; returns the metadata stored in it."""
    source, out = Path(source), Path(out)
    countries = {r[0]: r[4] for r in _rows(source / 'countryInfo.txt')}
    admin1 = {r[0]: r[1] for r in _rows(source / 'admin1CodesASCII.txt')}
    admin2 = {r[0]: r[1] for r in _rows(source / 'admin2Codes.txt')}
    rank = {code: i for i, code in enumerate(CODE_ORDER)}
    tmp = out.with_name(out.name + '.building')
    tmp.unlink(missing_ok=True)
    db = sqlite3.connect(tmp)
    db.create_function('fold', 1, fold, deterministic=True)
    db.create_function('words', 6, words, deterministic=True)
    db.executescript('''
        PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF;
        CREATE TABLE stage(gid INTEGER, name TEXT, ascii TEXT, alts TEXT, lat REAL, lon REAL, cc TEXT, county TEXT,
                           region TEXT, country TEXT, population INTEGER, score INTEGER, code_rank INTEGER);''')
    kept, excluded, batch, latest = Counter(), Counter(), [], ''
    with zipfile.ZipFile(source / 'allCountries.zip') as z, z.open('allCountries.txt') as f:
        for line in io.TextIOWrapper(f, encoding='utf-8'):
            r = line.rstrip('\n').split('\t')
            if r[6] != 'P':
                continue
            code = r[7]
            if code in EXCLUDED:
                excluded[code] += 1
                continue
            kept[code] += 1
            latest = max(latest, r[18])
            cc, population = r[8], int(r[14] or 0)
            batch.append((int(r[0]), r[1], r[2], r[3], float(r[4]), float(r[5]), cc,
                          admin2.get(f'{cc}.{r[10]}.{r[11]}'), admin1.get(f'{cc}.{r[10]}'), countries.get(cc),
                          population, max(population, FLOOR.get(code, 0)), rank.get(code, len(CODE_ORDER))))
            if len(batch) == 50_000:
                db.executemany('INSERT INTO stage VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
                batch.clear()
    db.executemany('INSERT INTO stage VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)', batch)
    db.executescript('''
        CREATE TABLE place(id INTEGER PRIMARY KEY, geonameid INTEGER NOT NULL, name TEXT NOT NULL, norm TEXT NOT NULL,
                           anorm TEXT, lat REAL NOT NULL, lon REAL NOT NULL, country_code TEXT, county TEXT,
                           region TEXT, country TEXT, population INTEGER NOT NULL, score INTEGER NOT NULL);
        INSERT INTO place(geonameid, name, norm, anorm, lat, lon, country_code, county, region, country, population,
                          score)
            SELECT gid, name, fold(name), NULLIF(fold(ascii), fold(name)), lat, lon, cc, county, region, country,
                   population, score
            FROM stage ORDER BY score DESC, code_rank, name, gid;
        CREATE INDEX stage_gid ON stage(gid);
        CREATE VIRTUAL TABLE place_fts USING fts5(words, content='', prefix='2 3');
        INSERT INTO place_fts(rowid, words)
            SELECT p.id, words(s.name, s.ascii, s.alts, s.county, s.region, s.country)
            FROM place p JOIN stage s ON s.gid = p.geonameid;
        DROP TABLE stage;
        CREATE INDEX place_norm ON place(norm);
        CREATE INDEX place_anorm ON place(anorm) WHERE anorm IS NOT NULL;
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);''')
    meta = {'format': FORMAT, 'source': SOURCE, 'data_date': latest,
            'built_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'places': sum(kept.values()), 'feature_codes': dict(kept.most_common()), 'excluded': dict(excluded),
            'files': {name: _sha256(source / name) for name in
                      ('allCountries.zip', 'countryInfo.txt', 'admin1CodesASCII.txt', 'admin2Codes.txt')}}
    db.executemany('INSERT INTO meta VALUES (?, ?)', [(k, json.dumps(v)) for k, v in meta.items()])
    db.commit()
    db.execute('VACUUM')
    db.close()
    os.replace(tmp, out)
    return meta


def connect(path):
    """Read-only connection; a missing file raises instead of creating an empty index."""
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(path)
    return sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True)


def km(a, b):
    """Great-circle distance between two (lat, lon) pairs."""
    lat1, lon1, lat2, lon2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 12742.0 * math.asin(min(1.0, math.sqrt(h)))


def search(db, query, limit=15):
    """Up to `limit` places for a free-text query, best first.

    Match tiers: 0 exact name; 1 name starts with the query; 2 name starts with the first word and contains the others;
    3 name starts with the first word and the others name its county, region or country ('alma g' finds Alma, Georgia);
    4 name contains every word; 5 name contains the first word and the area the rest; 6 matched only through alternate
    names or areas; 7 a one-letter word matched nothing. A place ranks by its tier's PENALTY minus log10 of its
    prominence. A second entry with the same name and country is dropped when it is within SAME_PLACE_KM or carries
    the same county and region, since the list could not tell the two apart. One-letter words rank results but do not
    filter them."""
    q = fold(query)
    terms = q.split()
    filters = [t for t in terms if len(t) > 1]
    if not filters:
        return []
    limit = max(1, min(int(limit), MAX_LIMIT))
    match = ' '.join(f'"{t}"*' for t in filters)
    ids = [r[0] for r in db.execute('SELECT rowid FROM place_fts WHERE place_fts MATCH ? ORDER BY rowid LIMIT ?',
                                    (match, CANDIDATES))]
    ids += [r[0] for r in db.execute('SELECT id FROM place WHERE norm = ? OR anorm = ? ORDER BY id LIMIT 50', (q, q))]
    ids = list(dict.fromkeys(ids))
    if not ids:
        return []
    rows = [dict(zip(COLUMNS, r)) for r in db.execute(
        f'SELECT {", ".join(COLUMNS)} FROM place WHERE id IN ({",".join("?" * len(ids))})', ids)]

    def tier(row):
        names = [row['norm']] + ([row['anorm']] if row['anorm'] else [])
        if q in names:
            return 0
        if any(n.startswith(q) for n in names):
            return 1
        name_words = [w for n in names for w in n.split()]
        area_words = fold(' '.join(a for a in (row['county'], row['region'], row['country']) if a)).split()
        leads = any(n.split()[0].startswith(terms[0]) for n in names if n)
        first = any(w.startswith(terms[0]) for w in name_words)
        in_name = [any(w.startswith(t) for w in name_words) for t in terms[1:]]
        in_area = [hit or any(w.startswith(t) for w in area_words) for t, hit in zip(terms[1:], in_name)]
        if leads and all(in_name):
            return 2
        if leads and all(in_area):
            return 3
        if first and all(in_name):
            return 4
        if first and all(in_area):
            return 5
        unmatched = [t for t in terms if len(t) == 1 and not any(w.startswith(t) for w in name_words + area_words)]
        return 7 if unmatched else 6

    # A county that repeats the place name says nothing, so it is dropped before the list labels are compared.
    for row in rows:
        if row['county'] and fold(row['county']) == row['norm']:
            row['county'] = None
    chosen = []
    for row in sorted(rows, key=lambda r: (PENALTY[tier(r)] - math.log10(1 + r['score']), r['id'])):
        if any(c['norm'] == row['norm'] and c['country_code'] == row['country_code']
               and ((c['county'], c['region']) == (row['county'], row['region'])
                    or km((c['lat'], c['lon']), (row['lat'], row['lon'])) < SAME_PLACE_KM) for c in chosen):
            continue
        chosen.append(row)
        if len(chosen) == limit:
            break
    return [{'id': f'geonames:{r["geonameid"]}', 'type': 'place', 'source': 'GeoNames', 'name': r['name'],
             'lat': round(r['lat'], 5), 'lon': round(r['lon'], 5), 'county': r['county'], 'region': r['region'],
             'country': r['country'], 'country_code': r['country_code'], 'population': r['population'] or None}
            for r in chosen]


def info(db):
    """The metadata written by `build`."""
    return {k: json.loads(v) for k, v in db.execute('SELECT key, value FROM meta')}


if __name__ == '__main__':
    if len(sys.argv) == 4 and sys.argv[1] == 'build':
        meta = build(sys.argv[2], sys.argv[3])
        print(json.dumps({k: meta[k] for k in ('places', 'excluded', 'built_utc')}))
    elif len(sys.argv) >= 4 and sys.argv[1] == 'search':
        with connect(sys.argv[2]) as connection:
            for place in search(connection, ' '.join(sys.argv[3:])):
                print(json.dumps(place, ensure_ascii=False))
    else:
        sys.exit(__doc__)
