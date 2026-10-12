"""NOAA GHCNh hourly station observations near every app pin, 2010 to the current year.

GHCNh replaced ISD ("global hourly") as NCEI's hourly station product. ISD and GSOD files stopped
updating in late August 2025, so recent station data come from GHCNh. NCEI publishes one file per
station and year under hourly/access/by-year/<YYYY>/parquet/; the station list and a monthly record
inventory sit in hourly/doc/. Terms: CC0-1.0, stated in the NCEI metadata record gov.noaa.ncdc:C01688.
"""
import math
import numpy as np
import pandas as pd
from ..runner import Request

BASE = 'https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/'
STATION_LIST = BASE+'doc/ghcnh-station-list.csv'
INVENTORY = BASE+'doc/ghcnh-inventory.txt'
FIRST_YEAR = 2010
NEAR_KM, FALLBACK_KM = 25., 50.
RAW_CAP = 5_000_000_000
# Planning estimate only: parquet station-years measured 24 to 76 bytes per record (Chile, NZ, US ASOS).
BYTES_PER_RECORD = 100
# The IBO freeze checks (Linares and Chillán 2022, Hamilton 7 October 2022, Penguin chill via Devonport)
# need these stations even when a closer station exists or they sit beyond 25 km of the pin.
EVENT_STATIONS = {'CIA00856571': 'Linares', 'CIU00060023': 'Linares', 'CIU00085657': 'Linares',
                  'CIN00360011': 'Chillán', 'CIU00060032': 'Chillán', 'CIU00085672': 'Chillán',
                  'NZM00093173': 'Hamilton AWS', 'ASN00091126': 'Devonport Airport'}
PIN_FILES = (('benchmark', 'code/benchmark_sites.json'), ('sites', 'config/sites.json'),
             ('evaluation', 'config/evaluation_sites.json'))
COLUMNS = ['STATION', 'DATE', 'temperature', 'temperature_Quality_Code', 'temperature_Source_Code',
           'temperature_Report_Type', 'dew_point_temperature', 'dew_point_temperature_Quality_Code',
           'relative_humidity', 'relative_humidity_Quality_Code']
# GHCNh Table 3: lower-case letters are failed integrated QC checks; legacy 2/3 and 6/7 are suspect or
# erroneous; for sources 220-223, 347 and 348 a legacy '5' means "removed".
BAD_CODES = set('abcdefhiklmnoprstuvwxz') | {'2', '3', '6', '7'}
REMOVED_5_SOURCES = {'220', '221', '222', '223', '347', '348'}

JOB = {'id': 'ghcnh-stations', 'source_ids': ['noaa-ghcnh'], 'schedule': 'monthly',
       'description': 'NOAA GHCNh hourly temperature, dew point and humidity for stations near every app pin, 2010 to now',
       'max_bytes_per_run': RAW_CAP, 'derived_only': False}


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle km; arrays broadcast. Same sphere as location_api.haversine_km."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin(np.radians(np.asarray(lon2)-lon1)/2)**2
    return 2*6371.0088*np.arcsin(np.sqrt(a))


def load_pins(root):
    """Pins from the deployed benchmark registry and the two server site configs; the first file naming an id wins."""
    import json
    pins = {}
    for source, rel in PIN_FILES:
        data = json.loads((root/rel).read_text())
        for s in data['sites'] if isinstance(data, dict) else data:
            pins.setdefault(s['id'], {'pin_id': s['id'], 'pin_name': s['name'], 'pin_source': source,
                                      'pin_lat': float(s['lat']), 'pin_lon': float(s['lon'])})
    return list(pins.values())


def read_station_list(path):
    raw = pd.read_csv(path, dtype=str, keep_default_na=False)
    out = pd.DataFrame({'station_id': raw.GHCN_ID.str.strip(), 'name': raw.NAME.str.strip(),
                        'lat': pd.to_numeric(raw.LATITUDE), 'lon': pd.to_numeric(raw.LONGITUDE),
                        'elevation_m': pd.to_numeric(raw.ELEVATION, errors='coerce'),
                        'wmo_id': raw.WMO_ID.str.strip(), 'country': raw.ISO_CODE.str.strip()})
    out.loc[out.elevation_m <= -999, 'elevation_m'] = np.nan
    return out


def read_inventory(path, first=FIRST_YEAR, last=None):
    """{station_id: {year: records}} for years in [first, last] with at least one record."""
    inv = pd.read_csv(path, sep=r'\s+', dtype={'GHCNh_ID': str})
    inv = inv[(inv.YEAR >= first) & ((inv.YEAR <= last) if last else True)]
    inv = inv.assign(records=inv.iloc[:, 2:14].sum(axis=1))
    inv = inv[inv.records > 0]
    out = {}
    for sid, year, n in zip(inv.GHCNh_ID, inv.YEAR, inv.records):
        out.setdefault(sid, {})[int(year)] = int(n)
    return out


def select(stations, pins, inventory, events=EVENT_STATIONS, exclude=()):
    """One row per (station, pin): stations with data within 25 km, else the nearest one with data within 50 km.
    `exclude` holds stations whose files had no temperature (precipitation-only networks), so the fallback
    moves on to the next station. Event stations join every pin within 50 km (or their nearest pin), with or without data."""
    have = stations[stations.station_id.isin(inventory.keys()) & ~stations.station_id.isin(set(exclude))]
    rows = []
    for pin in pins:
        d = haversine_km(pin['pin_lat'], pin['pin_lon'], have.lat.to_numpy(), have.lon.to_numpy())
        near = np.flatnonzero(d <= NEAR_KM)
        rule = 'within_25km'
        if not len(near):
            near, rule = ([int(np.argmin(d))] if len(d) and d.min() <= FALLBACK_KM else []), 'nearest_within_50km'
        rows += [{**have.iloc[i].to_dict(), **pin, 'distance_km': float(d[i]), 'rule': rule} for i in near]
    seen = {(r['station_id'], r['pin_id']) for r in rows}
    for sid in events:
        match = stations[stations.station_id == sid]
        if match.empty:
            continue
        st = match.iloc[0].to_dict()
        d = np.array([haversine_km(st['lat'], st['lon'], p['pin_lat'], p['pin_lon']) for p in pins])
        for i in (np.flatnonzero(d <= FALLBACK_KM) if (d <= FALLBACK_KM).any() else [int(np.argmin(d))]):
            if (sid, pins[i]['pin_id']) not in seen:
                rows.append({**st, **pins[i], 'distance_km': float(d[i]), 'rule': 'event_station'})
    meta = pd.DataFrame(rows, columns=[*stations.columns, 'pin_id', 'pin_name', 'pin_source', 'pin_lat', 'pin_lon',
                                       'distance_km', 'rule'])
    meta['event_station'] = meta.station_id.isin(events.keys())
    meta['inventory_years'] = [len(inventory.get(s, {})) for s in meta.station_id]
    meta['inventory_records'] = [sum(inventory.get(s, {}).values()) for s in meta.station_id]
    return meta.sort_values(['pin_id', 'distance_km'], kind='stable').reset_index(drop=True)


def year_plan(meta, inventory, today, cap=RAW_CAP):
    """[(station_id, year)] nearest pairs first: inventory years, plus the last two years for stations that
    reported within the last two years (the inventory lags the data files). Stops once the estimated raw
    size would pass the cap."""
    plan, seen, estimate = [], set(), 0
    for sid in meta.sort_values('distance_km', kind='stable').station_id.drop_duplicates():
        listed = set(inventory.get(sid, {}))
        recent = {today.year-1, today.year} if listed and max(listed) >= today.year-2 else set()
        years = sorted(listed | recent)
        for year in years:
            size = inventory[sid].get(year, 8784)*BYTES_PER_RECORD
            if estimate+size > cap:
                return plan, estimate, True
            if (sid, year) not in seen:
                seen.add((sid, year))
                plan.append((sid, year))
                estimate += size
    return plan, estimate, False


def temperature_ok(codes, sources):
    """True where a temperature passed GHCNh QC, per documentation Table 3. Blank and 'Null' codes pass."""
    codes = codes.astype('string').str.strip().fillna('')
    sources = sources.astype('string').str.strip().fillna('')
    return ~(codes.isin(BAD_CODES) | ((codes == '5') & sources.isin(REMOVED_5_SOURCES)))


def read_station_file(path):
    """One GHCNh by-year file (parquet or psv) as the tidy hourly table."""
    path = str(path)
    if path.endswith('.parquet'):
        import pyarrow.parquet as pq
        names = set(pq.read_schema(path).names)
        raw = pd.read_parquet(path, columns=[c for c in COLUMNS if c in names])
    else:
        raw = pd.read_csv(path, sep='|', usecols=lambda c: c in COLUMNS, dtype=str, keep_default_na=False)
    return tidy(raw.reindex(columns=COLUMNS))


def tidy(raw):
    def code(c):
        v = raw[c].astype('string').str.strip()
        return v.mask(v.isin(['', 'Null', 'None', 'nan']))
    out = pd.DataFrame({'station_id': raw.STATION.astype('string').str.strip(),
                        'time_utc': pd.to_datetime(raw.DATE, utc=True, format='ISO8601'),
                        'temperature_c': pd.to_numeric(raw.temperature, errors='coerce'),
                        'temperature_qc': code('temperature_Quality_Code'),
                        'temperature_source': code('temperature_Source_Code'),
                        'report_type': code('temperature_Report_Type'),
                        'dew_point_c': pd.to_numeric(raw.dew_point_temperature, errors='coerce'),
                        'dew_point_qc': code('dew_point_temperature_Quality_Code'),
                        'relative_humidity_pct': pd.to_numeric(raw.relative_humidity, errors='coerce'),
                        'relative_humidity_qc': code('relative_humidity_Quality_Code')})
    out = out[out[['temperature_c', 'dew_point_c', 'relative_humidity_pct']].notna().any(axis=1)]
    out['temperature_qc_pass'] = out.temperature_c.notna() & temperature_ok(out.temperature_qc, out.temperature_source)
    return out.drop_duplicates().sort_values('time_utc', kind='stable').reset_index(drop=True)


def plan(ctx):
    listing = ctx.fetch(Request('station-list', STATION_LIST, filename='doc/ghcnh-station-list.csv', max_bytes=50_000_000))
    inv_asset = ctx.fetch(Request('inventory', INVENTORY, filename='doc/ghcnh-inventory.txt', max_bytes=400_000_000))
    if listing.path is None or inv_asset.path is None:  # dry run before the first fetch
        ctx.log('ghcnh_plan_skipped', reason='station list or inventory not yet downloaded')
        return []
    inventory = read_inventory(inv_asset.path, FIRST_YEAR, ctx.today.year)
    # Learned from earlier runs: the inventory counts any element, and COOP precipitation stations have no temperature.
    lacking = sorted(sid for sid, v in ctx.state.get('stations', {}).items() if v.get('files') and not v.get('temperature_rows'))
    meta = select(read_station_list(listing.path), load_pins(ctx.root), inventory, exclude=lacking)
    years, estimate, capped = year_plan(meta, inventory, ctx.today)
    ctx.state['selection'] = {'meta': meta.astype(object).where(meta.notna(), None).to_dict('records'),
                              'estimate_bytes': estimate, 'capped': capped}
    ctx.log('ghcnh_plan', stations=int(meta.station_id.nunique()), pins=int(meta.pin_id.nunique()),
            station_years=len(years), estimate_bytes=estimate, capped=capped, excluded_no_temperature=len(lacking))
    return [Request(f'{sid}.{year}', f'{BASE}access/by-year/{year}/parquet/GHCNh_{sid}_{year}.parquet',
                    filename=f'by-year/{year}/GHCNh_{sid}_{year}.parquet', max_bytes=100_000_000, optional=True)
            for sid, year in years]


def on_disk(asset):
    """A usable local copy; a failed refresh keeps the previous file."""
    return asset.path is not None and asset.status != 'missing' and asset.path.exists()


def station_year(key):
    """('NZM00093173', 2022) for request key 'NZM00093173.2022', else None."""
    sid, _, year = key.rpartition('.')
    return (sid, int(year)) if sid and year.isdigit() and len(year) == 4 else None


def parse(ctx, assets):
    selection = ctx.state['selection']
    meta = pd.DataFrame(selection['meta'])
    files = {}
    for key, asset in assets.items():
        if station_year(key):
            sid, year = station_year(key)
            files.setdefault(sid, {})[year] = asset
    done = ctx.state.setdefault('stations', {})
    for sid, years in sorted(files.items()):
        if not (ctx.force or 'temperature_rows' not in done.get(sid, {}) or any(a.changed for a in years.values())):
            continue
        frames = [read_station_file(a.path) for _, a in sorted(years.items()) if on_disk(a)]
        read = len(frames)
        frames = [f for f in frames if len(f)]
        if frames:
            table = pd.concat(frames, ignore_index=True).drop_duplicates()
            ctx.write_table(f'hourly_{sid}', table.sort_values('time_utc', kind='stable').reset_index(drop=True))
            rows, span, temps = len(table), sorted(table.time_utc.dt.year.unique().tolist()), int(table.temperature_c.notna().sum())
        else:
            rows, span, temps = 0, [], 0
        done[sid] = {'rows': rows, 'temperature_rows': temps, 'files': read, 'years': span,
                     'missing_years': sorted(y for y, a in years.items() if a.status == 'missing')}
        ctx.log('ghcnh_station', station=sid, rows=rows, temperature_rows=temps, files=read, years=len(span))
    raw_bytes = sum(a.path.stat().st_size for a in assets.values() if on_disk(a))
    raw_dir_bytes = sum(p.stat().st_size for p in ctx.paths.raw.rglob('*') if p.is_file())
    meta['rows'] = [done.get(s, {}).get('rows', 0) for s in meta.station_id]
    meta['temperature_rows'] = [done.get(s, {}).get('temperature_rows', 0) for s in meta.station_id]
    meta['years_with_data'] = [len(done.get(s, {}).get('years', [])) for s in meta.station_id]
    meta['first_year'] = [min(done.get(s, {}).get('years') or [np.nan]) for s in meta.station_id]
    meta['last_year'] = [max(done.get(s, {}).get('years') or [np.nan]) for s in meta.station_id]
    ctx.write_table('station_meta', meta)
    used = {s for s in meta.station_id if done.get(s, {}).get('temperature_rows')}
    pins = load_pins(ctx.root)
    served = set(meta.loc[meta.station_id.isin(used), 'pin_id'])
    summary = {'stations_selected': int(meta.station_id.nunique()), 'stations_with_temperature': len(used),
               'stations_excluded_no_temperature': sum(1 for v in done.values() if v.get('files') and not v.get('temperature_rows')),
               'pins': len(pins), 'pins_without_station': sorted(p['pin_id'] for p in pins if p['pin_id'] not in served),
               'station_years_files': sum(on_disk(a) for k, a in assets.items() if station_year(k)),
               'station_years_missing': sum(a.status == 'missing' for k, a in assets.items() if station_year(k)),
               'rows': int(sum(done.get(s, {}).get('rows', 0) for s in used)),
               'raw_bytes': int(raw_bytes), 'raw_dir_bytes': int(raw_dir_bytes),
               'estimate_bytes': selection['estimate_bytes'], 'capped': selection['capped'],
               'years': [int(min(meta.first_year.dropna(), default=0)), int(max(meta.last_year.dropna(), default=0))],
               'event_stations': {sid: {'name': EVENT_STATIONS[sid], 'rows': done.get(sid, {}).get('rows', 0),
                                        'years': done.get(sid, {}).get('years', [])} for sid in EVENT_STATIONS}}
    ctx.state['summary'] = summary
    return summary
