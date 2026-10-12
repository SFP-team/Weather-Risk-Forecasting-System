"""Event checks v2 (protocol of astra_ibo_evidence_review.md section 5.5). Read-only use of the archive.
Run from tmp/EventChecksRegistry (a flat copy of code/). Writes event_checks_v2_raw.json here."""
import csv, json, math, sys, time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd, requests, zarr
import location_api as L
from postprocess import LandMask, extract, nearest_indices, km_distance
from hourly_archive import hourly_from_cache, ArchiveGap
from production import analyse, PRIMARY_PROFILE

HERE = Path(__file__).resolve().parent
ROOT = L.ROOT
LAND = LandMask(ROOT)
G = zarr.open_consolidated(str(ROOT / 'data/normalized/global/met_daily'), mode='r')
LATS, LONS = G['lat'][:], G['lon'][:]
UA = {'User-Agent': 'UF-Blueberry-Weather-Research/1.0 (+https://github.com/SFP-team/Weather-Risk-Forecasting-System)'}

CASES = [
    {'id': 'cl-2022-10-31-frost', 'registry_id': 'cl-2022-11-frost-hail', 'tz': 'America/Santiago', 'event_night': '2022-10-31',
     'extra_nights': ['2022-11-01'],
     'pins': {'Coihueco': (-36.6167, -71.8333), 'Chillan (benchmark cl-chillan-nuble)': (-36.6066, -72.1034),
              'Linares (benchmark cl-linares-maule)': (-35.8467, -71.5931), 'Longavi': (-35.9667, -71.6833)},
     'ghcnh': [],
     # INIA network file ids; coordinates and elevation from agrometeorologia.cl assets/db/items-resumen.json.
     'inia': {'EXT-157': ('Aerodromo Gral. Bernardo O\'Higgins, Chillan (DMC)', -36.58722, -72.04, 151, 'Chillan (benchmark cl-chillan-nuble)'),
              'EXT-160': ('Chillan Mayulermo, San Ignacio (MMA-DMC)', -36.82806, -71.86694, 396, 'Coihueco'),
              'EXT-974': ('Escuela de Artilleria, Linares (MMA-DMC)', -35.83694, -71.59278, 160, 'Linares (benchmark cl-linares-maule)'),
              'INIA-227': ('Miraflores, Longavi (INIA)', -35.818051, -71.775019, 124, 'Longavi'),
              'EXT-161': ('Copihue, Retiro (MMA-DMC)', -36.07556, -71.75806, 162, 'Longavi')},
     # RAN Agromet ema_ia_id; coordinates from the agrometR station sheet as listed in regions/chile-argentina-uruguay.md 6.1.
     'ran': {'99': ('Linares 2 (FDF), Longavi', -35.932, -71.567, 'Longavi'),
             '107': ('Coihueco (FDF)', -36.557, -71.817, 'Coihueco'),
             '110': ('San Ignacio (FDF)', -36.844, -72.125, 'Coihueco'),
             '179': ('Santa Rosa (INIA), Chillan', -36.535, -71.916, 'Chillan (benchmark cl-chillan-nuble)'),
             '181': ('Navidad (INIA), El Carmen', -36.907, -71.936, 'Coihueco'),
             '314': ('C.E. Arroz (INIA), San Carlos', -36.409, -72.007, 'Chillan (benchmark cl-chillan-nuble)'),
             '102': ('Parral (FDF)', -36.213, -71.738, 'Longavi'),
             '108': ('Pinto (FDF)', -36.713, -71.876, 'Coihueco'),
             '311': ('Santa Amada (INIA), Linares', -35.761, -71.480, 'Linares (benchmark cl-linares-maule)'),
             '106': ('Niquen (FDF)', -36.294, -71.894, 'Chillan (benchmark cl-chillan-nuble)')}},
    {'id': 'nz-2022-10-07-frost', 'registry_id': 'nz-waikato-2022-10-frost', 'tz': 'Pacific/Auckland', 'event_night': '2022-10-07',
     'extra_nights': [],
     'ran': {},
     'pins': {'Hamilton': (-37.787, 175.279), 'Ohaupo (benchmark nz-waikato-ohaupo)': (-37.9236, 175.3067)},
     'ghcnh': [('NZM00093173', 'Hamilton')], 'inia': {}},
    {'id': 'us-se-2022-03-13-freeze', 'registry_id': 'us-se-freeze-2022-03', 'tz': 'America/New_York', 'event_night': '2022-03-13',
     'extra_nights': ['2022-03-14'],
     'pins': {'Alma (benchmark us-ga-alma)': (31.5396, -82.4624), 'Homerville (benchmark us-ga-homerville)': (31.0366, -82.7471),
              'Elizabethtown (benchmark us-nc-elizabethtown)': (34.6293, -78.6053), 'Burgaw (benchmark us-nc-burgaw)': (34.5527, -77.9261)},
     'ghcnh': [('USW00013870', 'Alma (benchmark us-ga-alma)'), ('USW00000128', 'Homerville (benchmark us-ga-homerville)'),
               ('USW00003705', 'Elizabethtown (benchmark us-nc-elizabethtown)'), ('USW00013748', 'Burgaw (benchmark us-nc-burgaw)')],
     'inia': {}, 'ran': {}},
]
THRESH = (0.0, -1.0, -2.2)
PASS_QC = {'', '0', '1', '4', '5', '9'}  # ISD-style pass codes kept by GHCNh; anything else is treated as suspect.


def night_window(d, tz):
    """Local 18:00 on D-1 to 10:00 on D, as UTC timestamps (DST handled by zoneinfo)."""
    z = ZoneInfo(tz)
    a = datetime.combine(d - timedelta(days=1), datetime.min.time(), z).replace(hour=18)
    b = datetime.combine(d, datetime.min.time(), z).replace(hour=10)
    return pd.Timestamp(a.astimezone(timezone.utc)).tz_localize(None), pd.Timestamp(b.astimezone(timezone.utc)).tz_localize(None)


def night_stats(series, d, tz, wind=None):
    a, b = night_window(d, tz)
    s = series[(series.index >= a) & (series.index <= b)].dropna()
    if s.empty:
        return None
    out = {'night': str(d), 'window_utc': [str(a), str(b)], 'n_obs': int(len(s)), 'min_c': round(float(s.min()), 2),
           'min_time_utc': str(s.idxmin())}
    # Hours below threshold: for hourly series the count of obs; sub-hourly obs are binned by hour first.
    hourly = s.resample('1h').min().dropna()
    for t in THRESH:
        out[f'hours_le_{t:g}_c'.replace('-', 'minus_')] = int((hourly <= t).sum())
    if wind is not None:
        w = wind[(wind.index >= a) & (wind.index <= b)].dropna()
        out['wind_median_m_s'] = None if w.empty else round(float(w.median()), 2)
    return out


def nights(case):
    d = date.fromisoformat(case['event_night'])
    return [d + timedelta(days=k) for k in range(-3, 4)]


_PREV = HERE / 'event_checks_v2_raw.json'
ELEV_CACHE = {(g['lat'], g['lon']): g['power_elevation'] for c in json.loads(_PREV.read_text())['cases'] for g in c['grid_cells']
              if 'elevation_m' in g['power_elevation']} if _PREV.exists() else {}


def power_elevation(lat, lon):
    """Elevation of the POWER (MERRA-2) cell, from one tiny point request; the archive does not store it."""
    if (lat, lon) in ELEV_CACHE:
        return ELEV_CACHE[(lat, lon)]
    url = 'https://power.larc.nasa.gov/api/temporal/daily/point'
    p = dict(parameters='T2M_MIN', community='AG', latitude=lat, longitude=lon, start='20220101', end='20220101', format='JSON',
             **{'time-standard': 'UTC'})
    try:
        r = requests.get(url, params=p, headers=UA, timeout=60)
        r.raise_for_status()
        g = r.json()['geometry']['coordinates']
        return {'power_point_lon': g[0], 'power_point_lat': g[1], 'elevation_m': g[2]}
    except Exception as exc:  # recorded, never substituted
        return {'error': f'{type(exc).__name__}: {exc}'[:200]}
    finally:
        time.sleep(1.5)


def read_ghcnh(sid):
    f = HERE / 'ghcnh' / f'GHCNh_{sid}_2022.psv'
    df = pd.read_csv(f, sep='|', dtype=str, usecols=lambda c: c in {
        'STATION', 'Station_name', 'DATE', 'LATITUDE', 'LONGITUDE', 'ELEVATION', 'temperature', 'temperature_Quality_Code',
        'wind_speed', 'wind_speed_Quality_Code'})
    meta = {'id': sid, 'name': df.Station_name.iloc[0].strip(), 'lat': float(df.LATITUDE.iloc[0]), 'lon': float(df.LONGITUDE.iloc[0]),
            'elevation_m': float(df.ELEVATION.iloc[0]), 'network': 'NOAA GHCNh (hourly)', 'file': f.name,
            'url': f'https://www.ncei.noaa.gov/oa/global-historical-climatology-network/hourly/access/by-year/2022/psv/{f.name}',
            'licence': 'NOAA NCEI public data (US government work, no restrictions on use)'}
    t = pd.to_datetime(df.DATE)
    q = df.temperature_Quality_Code.fillna('').str.strip()
    temp = pd.to_numeric(df.temperature, errors='coerce').where(q.isin(PASS_QC))
    meta['rows_dropped_qc'] = int((~q.isin(PASS_QC) & df.temperature.notna()).sum())
    wq = df.wind_speed_Quality_Code.fillna('').str.strip() if 'wind_speed_Quality_Code' in df else pd.Series('', index=df.index)
    wind = pd.to_numeric(df.wind_speed, errors='coerce').where(wq.isin(PASS_QC))
    return meta, pd.Series(temp.values, index=t).sort_index(), pd.Series(wind.values, index=t).sort_index()


def read_inia(code):
    """INIA CSV columns follow the request order TA_AVG, VV_AVG, HR_AVG, TS00_AVG (checked against a VV-only query);
    the header labels are in a different order. Times are fixed UTC-4."""
    rows = list(csv.reader(open(HERE / 'inia' / f'{code}.csv', encoding='utf-8')))
    data = [r for r in rows if len(r) > 2 and r[0][:2].isdigit()]
    t = pd.to_datetime([r[0] for r in data], format='%d-%m-%Y %H:%M') + pd.Timedelta(hours=4)
    ta = pd.to_numeric(pd.Series([r[1] for r in data]), errors='coerce').values
    vv = pd.to_numeric(pd.Series([r[2] for r in data]), errors='coerce').values / 3.6  # km/h to m/s
    return pd.Series(ta, index=t), pd.Series(vv, index=t)


def read_ran(sid):
    """RAN Agromet XML (getGraphData.php, the endpoint used by agrometR). Field 7 is the hourly minimum, field 6 the
    hourly maximum wind speed, field 3 mean RH. Timestamps carry no zone; treated as America/Santiago civil time because
    solar radiation rises between the 06:00 and 07:00 rows, which fits CLST (UTC-3) sunrise near 06:50."""
    import re
    t = (HERE / 'ran' / f'{sid}.xml').read_text(encoding='utf-8')
    rows = []
    for d in re.findall(r'<dato>([^<]*)</dato>', t):
        p = d.split('|')
        f = {p[i]: p[i + 1] for i in range(2, len(p) - 1, 2)}
        num = lambda k: float(f[k]) if f.get(k, '') != '' else np.nan
        rows.append((p[1], num('7'), num('6'), num('3')))
    df = pd.DataFrame(rows, columns=['local', 'tmin', 'wind_max', 'rh'])
    # An empty logger row is served as 0.0 C with 0% RH; screen it rather than read it as a frost.
    bad = (df.rh == 0) & (df.tmin == 0)
    df.loc[bad, ['tmin', 'wind_max']] = np.nan
    loc = pd.to_datetime(df.local).dt.tz_localize('America/Santiago', ambiguous='NaT', nonexistent='NaT')
    idx = loc.dt.tz_convert('UTC').dt.tz_localize(None)
    keep = idx.notna()
    return (pd.Series(df.tmin[keep].values, index=idx[keep]).sort_index(),
            pd.Series(df.wind_max[keep].values, index=idx[keep]).sort_index(), int(bad.sum()))


def cell_block(case):
    cells = {}
    for name, (lat, lon) in case['pins'].items():
        y, x = nearest_indices(LATS, LONS, lat, lon)
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                key = (int(y + dy), int(x + dx))
                c = cells.setdefault(key, {'lat': float(LATS[key[0]]), 'lon': float(LONS[key[1]]), 'pins': {}})
                c['pins'][name] = {'distance_km': round(km_distance(lat, lon, c['lat'], c['lon']), 1),
                                   'is_pin_cell': dy == 0 and dx == 0}
    return cells


def grid_for_case(case):
    tz = case['tz']
    ns = nights(case)
    utc_days = pd.date_range(ns[0] - timedelta(days=1), ns[-1])
    out = []
    hourly_cache = {}
    for key, c in sorted(cell_block(case).items()):
        rec = {'cell_index': list(key), 'lat': c['lat'], 'lon': c['lon'], 'pins': c['pins'],
               'cell_center_on_land': bool(LAND.covers(c['lat'], c['lon']))}
        frame, meta = extract(ROOT, c['lat'], c['lon'], LAND)
        if frame is None:
            rec['daily'] = {'status': meta.get('status'), 'reason': meta.get('reason')}
        else:
            src = meta['sources'][0]
            assert abs(src['source_latitude'] - c['lat']) < 1e-6 and abs(src['source_longitude'] - c['lon']) < 1e-6
            d = frame.set_index('time').tmin_c.reindex(utc_days)
            rec['daily'] = {'profile': src['profile'], 'tmin_c_by_utc_day': {str(k.date()): None if pd.isna(v) else round(float(v), 2)
                                                                             for k, v in d.items()}}
        try:
            h, prov = hourly_from_cache(ROOT, c['lat'], c['lon'])
            if h is None:
                rec['hourly'] = {'status': 'no_hourly_archive'}
            else:
                assert abs(prov['source_lat'] - c['lat']) < 1e-6 and abs(prov['source_lon'] - c['lon']) < 1e-6
                hourly_cache[key] = h.tmean_c
                rec['hourly'] = {'source_version': prov['source_version'], 'nights': [night_stats(h.tmean_c, n, tz) for n in ns]}
        except ArchiveGap as exc:
            rec['hourly'] = {'status': 'archive_gap', 'reason': str(exc)}
        rec['power_elevation'] = power_elevation(c['lat'], c['lon'])
        out.append(rec)
    return out, hourly_cache


def stage_at(lat, lon, d):
    h, src = L.hourly_for(lat, lon)
    pad, _ = extract(ROOT, lat, lon, LAND, padding=True)
    r = analyse(h.tmean_c, pad.set_index('time'), lat, PRIMARY_PROFILE, dewpoint=h.dewpoint_mean_c, lon=lon)
    ds = str(d)
    best = None
    for s in r['seasons']:
        if not s.get('flowering'):
            continue
        span = [s.get('budbreak_date') or s['flowering'][0], s['harvest'][1] if s.get('harvest') else s['flowering'][1]]
        if span[0] <= ds <= span[1]:
            best = s
    if best is None:
        return {'profile': PRIMARY_PROFILE, 'stage_on_event_day': 'no season spans the event day'}
    stage = 'before budbreak'
    if best.get('budbreak_date') and ds >= best['budbreak_date']:
        stage = 'budbreak to flowering'
    for k in ('flowering', 'fruit', 'harvest'):
        if best.get(k) and best[k][0] <= ds <= best[k][1]:
            stage = k
    return {'profile': PRIMARY_PROFILE, 'winter_year': best['winter_year'], 'status': best['status'],
            'budbreak_date': best.get('budbreak_date'), 'flowering': best.get('flowering'), 'fruit': best.get('fruit'),
            'harvest': best.get('harvest'), 'stage_on_event_day': stage, 'hourly_source_distance_km': src.get('distance_km')}


def station_vs_grid(series, grid_series, tz, month_start, wind=None):
    """Station minus pin-cell grid local-night minimum for every night in the event month of 2022."""
    d0 = date.fromisoformat(month_start)
    rows = []
    d = d0
    while d.month == d0.month:
        s = night_stats(series, d, tz, wind)
        g = night_stats(grid_series, d, tz)
        if s and g and s['n_obs'] >= 10:
            rows.append({'night': str(d), 'diff_c': round(s['min_c'] - g['min_c'], 2), 'wind_median_m_s': s.get('wind_median_m_s')})
        d += timedelta(days=1)
    diffs = [r['diff_c'] for r in rows]
    calm = [r['diff_c'] for r in rows if r['wind_median_m_s'] is not None and r['wind_median_m_s'] <= 2.0]
    q = lambda v: None if not v else {'n': len(v), 'median': round(float(np.median(v)), 2), 'p10': round(float(np.percentile(v, 10)), 2),
                                       'p90': round(float(np.percentile(v, 90)), 2)}
    return {'all_nights': q(diffs), 'calm_nights_wind_median_le_2_m_s': q(calm), 'per_night': rows}


def main():
    result = {'generated_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'root': str(ROOT),
              'primary_profile': PRIMARY_PROFILE, 'cases': []}
    for case in CASES:
        tz = case['tz']
        ns = nights(case)
        grid, hc = grid_for_case(case)
        pin_cell = {}
        for name, (lat, lon) in case['pins'].items():
            y, x = nearest_indices(LATS, LONS, lat, lon)
            pin_cell[name] = (int(y), int(x))
        stations = []
        for sid, pin in case['ghcnh']:
            meta, temp, wind = read_ghcnh(sid)
            meta['pin'] = pin
            meta['distance_to_pin_km'] = round(km_distance(meta['lat'], meta['lon'], *case['pins'][pin]), 1)
            meta['nights'] = [night_stats(temp, n, tz, wind) for n in ns]
            sc = tuple(int(v) for v in nearest_indices(LATS, LONS, meta['lat'], meta['lon']))
            g = hc.get(sc)
            meta['compared_cell_index'] = list(sc) if g is not None else None
            if g is not None:
                month = case['event_night'][:8] + '01'
                meta['station_minus_station_cell_grid_month_2022'] = station_vs_grid(temp, g, tz, month, wind)
            stations.append(meta)
        for sid, (name, lat, lon, pin) in case['ran'].items():
            temp, wind, screened = read_ran(sid)
            meta = {'id': f'RAN-{sid}', 'name': name, 'network': 'Red Agroclimatica Nacional (RAN Agromet, agromet.cl)', 'pin': pin,
                    'lat': lat, 'lon': lon, 'distance_to_pin_km': round(km_distance(lat, lon, *case['pins'][pin]), 1),
                    'url': f'https://www.agromet.cl/ext/aux/getGraphData.php?ema_ia_id={sid}&dateFrom=2022-10-01+00:00:00&dateTo=2022-11-07+23:00:00&portada=false',
                    'variable': 'hourly minimum air temperature (field 7); wind is hourly maximum speed',
                    'time_basis': 'local civil time assumed [inference from solar radiation onset]',
                    'licence': 'Not stated on the endpoint; agromet.cl is a public MINAGRI service. Cite RAN Agromet and the station operator.',
                    'rows_screened_empty': screened,
                    'nights': [night_stats(temp, n, tz, wind) for n in ns]}
            sc = tuple(int(v) for v in nearest_indices(LATS, LONS, lat, lon))
            g = hc.get(sc)
            meta['compared_cell_index'] = list(sc) if g is not None else None
            if g is not None:
                meta['station_minus_station_cell_grid_month_2022'] = station_vs_grid(temp, g, tz, '2022-10-01', wind)
            stations.append(meta)
        for code, (name, lat, lon, elev, pin) in case['inia'].items():
            temp, wind = read_inia(code)
            meta = {'id': code, 'name': name, 'network': 'Red Agrometeorologica INIA (agrometeorologia.cl)', 'pin': pin,
                    'lat': lat, 'lon': lon, 'elevation_m': elev, 'distance_to_pin_km': round(km_distance(lat, lon, *case['pins'][pin]), 1),
                    'variable': 'hourly mean air temperature (TA_AVG); hourly minimum is not offered for hourly queries',
                    'time_basis': 'fixed UTC-4 in source file; converted to UTC here',
                    'licence': 'Use in publications must cite the data source as a collaboration between INIA and partner institutions (CSV footer).',
                    'nights': [night_stats(temp, n, tz, wind) for n in ns]}
            sc = tuple(int(v) for v in nearest_indices(LATS, LONS, lat, lon))
            g = hc.get(sc)
            meta['compared_cell_index'] = list(sc) if g is not None else None
            if g is not None:
                diffs = []
                for n in ns:
                    s, gg = night_stats(temp, n, tz), night_stats(g, n, tz)
                    if s and gg:
                        diffs.append({'night': str(n), 'diff_c': round(s['min_c'] - gg['min_c'], 2)})
                meta['station_minus_station_cell_grid_event_nights'] = diffs
            stations.append(meta)
        stages = {}
        for name, (lat, lon) in case['pins'].items():
            try:
                stages[name] = stage_at(lat, lon, date.fromisoformat(case['event_night']))
            except Exception as exc:
                stages[name] = {'error': f'{type(exc).__name__}: {exc}'[:200]}
        result['cases'].append({'id': case['id'], 'registry_id': case['registry_id'], 'tz': tz, 'event_night': case['event_night'],
                                'nights': [str(n) for n in ns],
                                'pins': {k: list(v) for k, v in case['pins'].items()},
                                'pin_cells': {k: list(v) for k, v in pin_cell.items()},
                                'grid_cells': grid, 'stations': stations, 'model_stage': stages})
        print('done', case['id'], file=sys.stderr, flush=True)
    (HERE / 'event_checks_v2_raw.json').write_text(json.dumps(result, indent=1, allow_nan=False))


if __name__ == '__main__':
    main()
