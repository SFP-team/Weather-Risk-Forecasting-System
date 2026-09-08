"""Bounded anomaly investigation and preliminary, flag-aware station comparisons."""
import argparse
import calendar
import json
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import requests
import zarr
from discover import write_json
from pilot import NAMES, digest, nearest_indices
from postprocess import ROOT, LandMask, km_distance

NOAA = 'https://www.ncei.noaa.gov/pub/data/ghcn/daily/'


def fetch(root, name, url, limit=40*1024**2):
    path = root / 'data/reference/validation' / name
    meta = path.with_suffix(path.suffix + '.json')
    if path.exists() and meta.exists():
        data = path.read_bytes()
        if digest(data) != json.loads(meta.read_text())['sha256']:
            raise ValueError('Cached reference checksum mismatch')
        return data
    response = requests.get(url, timeout=(15, 90), stream=True)
    response.raise_for_status()
    data = bytearray()
    for chunk in response.iter_content(1024*1024):
        data.extend(chunk)
        if len(data) > limit:
            raise ValueError('Reference exceeds size bound')
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.partial')
    tmp.write_bytes(data)
    os.replace(tmp, path)
    write_json(meta, {'url': url, 'bytes': len(data), 'sha256': digest(data),
                     'retrieved': datetime.now(timezone.utc).isoformat()})
    return bytes(data)


def anomalies(root):
    plan = json.loads((root/'state/global_download_plan.json').read_text())
    jobs = {j['id']: j for j in plan['jobs']}
    group = zarr.open_consolidated(str(root/'data/normalized/global/met_daily'), mode='r')
    land = LandMask(root)
    records = []
    with sqlite3.connect(f'file:{root}/state/jobs.sqlite?mode=ro', uri=True) as db:
        tiles = db.execute('SELECT id,qc FROM tiles').fetchall()
    for key, qc in tiles:
        job = jobs[key]
        var = job['variable']
        if var not in ('RH2M', 'PRECTOTCORR'):
            continue
        stats = json.loads(qc)[NAMES[var]]
        if not stats['missing'] and not (var == 'PRECTOTCORR' and stats['max'] > 1000):
            continue
        y, x = job['y'], job['x']
        values = group[NAMES[var]][:, slice(*y), slice(*x)]
        mask = ~np.isfinite(values)
        if var == 'PRECTOTCORR':
            mask |= values > 1000
        for t, dy, dx in np.argwhere(mask):
            lat, lon = float(group['lat'][y[0]+dy]), float(group['lon'][x[0]+dx])
            value = float(values[t,dy,dx])
            records.append({'variable': var, 'date': str((pd.Timestamp('2010-01-01')+pd.Timedelta(days=int(t))).date()),
                            'lat': lat, 'lon': lon, 'value': value if np.isfinite(value) else None,
                            'land_cell_center': bool(land.covers(lat, lon)), 'tile': key})
    # A screening threshold, not a physical impossibility threshold; preserve every source value.
    report = {'screening_rain_mm_day': 1000, 'records': records, 'source_modified': False}
    write_json(root/'reports/anomaly_locations.json', report)
    print(json.dumps(report), flush=True)
    # Verify the maximum and one humidity gap through a separately served API endpoint.
    rain = sorted([r for r in records if r['value'] is not None], key=lambda r:r['value'], reverse=True)
    gaps = [r for r in records if r['value'] is None]
    checks = []
    for record in rain[:1]+gaps[:1]:
        date = record['date'].replace('-', '')
        params = {'parameters':record['variable'], 'community':'AG', 'latitude':record['lat'],
                  'longitude':record['lon'], 'start':date, 'end':date, 'format':'JSON', 'time-standard':'UTC'}
        url = requests.Request('GET','https://power.larc.nasa.gov/api/temporal/daily/point',params=params).prepare().url
        obj = json.loads(fetch(root, f"power_{record['variable']}_{date}.json", url, 2*1024**2))
        raw = obj['properties']['parameter'][record['variable']][date]
        fill = obj.get('header',{}).get('fill_value', -999)
        api = None if raw == fill else raw
        checks.append({**record,'api_value':api,'api_matches': api is None if record['value'] is None else api is not None and abs(api-record['value']) <= .011})
    report['api_checks'] = checks
    write_json(root/'reports/anomaly_locations.json', report)
    print(json.dumps({'api_checks':checks}), flush=True)


def parse_daily(text):
    records=[]
    for line in text.splitlines():
        year, month, element = int(line[11:15]), int(line[15:17]), line[17:21]
        if not 2011 <= year <= 2025 or element not in ('TMIN','TMAX','PRCP'):
            continue
        for day in range(1,calendar.monthrange(year,month)[1]+1):
            block=line[21+8*(day-1):21+8*day]
            raw=int(block[:5]); m,q,s=block[5:8]
            accepted=raw != -9999 and q == ' ' and m not in ('P','L') and s != ' '
            records.append({'time':pd.Timestamp(year,month,day),'element':element,
                            'value':raw/10 if raw != -9999 else np.nan,
                            'mflag':m,'qflag':q,'sflag':s,'accepted':accepted})
    return pd.DataFrame(records)


def stations(root):
    text=fetch(root,'ghcnd-stations.txt',NOAA+'ghcnd-stations.txt').decode()
    inventory=fetch(root,'ghcnd-inventory.txt',NOAA+'ghcnd-inventory.txt',80*1024**2).decode()
    fetch(root,'ghcnd-readme.txt',NOAA+'readme.txt')
    coverage={}
    for line in inventory.splitlines():
        if line[31:35] in ('TMIN','TMAX','PRCP') and int(line[36:40]) <= 2011 and int(line[41:45]) >= 2020:
            coverage.setdefault(line[:11],set()).add(line[31:35])
    catalog=[]
    for line in text.splitlines():
        if len(coverage.get(line[:11],set()))==3:
            catalog.append({'id':line[:11],'lat':float(line[12:20]),'lon':float(line[21:30]),
                            'elevation_m':float(line[31:37]),'name':line[41:71].strip()})
    group=zarr.open_consolidated(str(root/'data/normalized/global/met_daily'),mode='r')
    results=[]
    for region,lat,lon in [('Florida',29.410918,-82.143678),('Southern Brazil',-26.312389,-50.080639)]:
        candidates=sorted(catalog,key=lambda s:km_distance(lat,lon,s['lat'],s['lon']))
        for station in candidates[:2]:
            distance=km_distance(lat,lon,station['lat'],station['lon'])
            if distance > 250:
                continue
            data=parse_daily(fetch(root,station['id']+'.dly',NOAA+'all/'+station['id']+'.dly').decode())
            out=root/'data/normalized/stations'/ (station['id']+'.parquet')
            out.parent.mkdir(parents=True,exist_ok=True)
            data.to_parquet(out,index=False)
            y,x=nearest_indices(group['lat'][:],group['lon'][:],station['lat'],station['lon'])
            result={'region':region,'station':station,'distance_to_project_site_km':distance,
                    'grid_lat':float(group['lat'][y]),'grid_lon':float(group['lon'][x]),'metrics':{}}
            for element,var in [('TMIN','tmin_c'),('TMAX','tmax_c'),('PRCP','precip_mm')]:
                subset=data[data.element==element]
                obs=subset[subset.accepted].set_index('time').value
                model=pd.Series(group[var][:,y,x],index=pd.date_range('2010-01-01','2025-12-31'))
                pairs=pd.concat({'station':obs,'grid':model.reindex(obs.index)},axis=1).dropna()
                error=pairs.grid-pairs.station
                result['metrics'][element]={'pairs':len(pairs),'baseline_days':5479,'rejected_or_missing_records':int((~subset.accepted).sum()),
                    'bias_grid_minus_station':float(error.mean()) if len(error) else None,
                    'mae':float(error.abs().mean()) if len(error) else None,
                    'rmse':float(np.sqrt((error**2).mean())) if len(error) else None}
            results.append(result)
            print(json.dumps(result),flush=True)
    write_json(root/'reports/station_comparison.json',{'status':'preliminary','results':results,
        'selection': 'Nearest two stations within 250 km with inventory extent covering 2011–2020 for all three fields; compare available 2011–2025 records.',
        'regions_without_matches':[r for r in ['Florida','Southern Brazil'] if not any(x['region']==r for x in results)],
        'limitations':['Same-date screening only: observation day boundaries may differ from NASA UTC days.',
        'Station observations are separate from the NASA API, but may not be independent of reanalysis assimilation.',
        'No gap filling or bias correction performed. Measurement, quality and source flags retained.',
        'Stations chosen by distance and inventory extent, not by favorable error. Actual valid-pair coverage reported.',
        'Does not validate site-level frost events or cultivar suitability.']})


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['anomalies','stations'])
    args=parser.parse_args()
    globals()[args.action](ROOT)
