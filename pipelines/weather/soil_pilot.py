"""Bounded SoilGrids WCS pilot; raw rasters stay on the project server."""
import hashlib
import json
import os
import shutil
import time
import fcntl
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
import requests
import rasterio
from rasterio.warp import transform
from discover import ROOT, write_json

PROPS = {'phh2o': (10, 'pH', 0, 14), 'soc': (10, 'g/kg', 0, 1000),
         'sand': (10, 'percent', 0, 100), 'silt': (10, 'percent', 0, 100),
         'clay': (10, 'percent', 0, 100)}
DEPTHS = ('0-5cm', '5-15cm', '15-30cm')
STATS = ('mean', 'Q0.05', 'Q0.95')


def url_for(site, prop, depth, stat):
    # Tiny geographic window. WCS returns a geographic grid in the live pilot;
    # record returned CRS/resolution, never claim native pixel extraction.
    x,y = site['lon'],site['lat']
    args = [('map',f'/map/{prop}.map'),('SERVICE','WCS'),('VERSION','2.0.1'),
            ('REQUEST','GetCoverage'),('COVERAGEID',f'{prop}_{depth}_{stat}'),
            ('FORMAT','image/tiff'),('SUBSETTINGCRS','http://www.opengis.net/def/crs/EPSG/0/4326'),
            ('SUBSET',f'x({x-.005},{x+.005})'),('SUBSET',f'y({y-.005},{y+.005})')]
    return 'https://maps.isric.org/mapserv?' + urlencode(args)


def sample(path, site, prop):
    with rasterio.open(path) as src:
        if src.count != 1 or src.width * src.height > 10000 or src.crs is None:
            raise ValueError('Unexpected raster layout')
        x,y = transform('EPSG:4326', src.crs, [site['lon']], [site['lat']])
        row,col = src.index(x[0],y[0])
        if not (0 <= row < src.height and 0 <= col < src.width):
            raise ValueError('Requested point outside returned raster')
        raw = src.read(1,masked=True)[row,col]
        center = src.xy(row,col)
        lon,lat = transform(src.crs,'EPSG:4326',[center[0]],[center[1]])
        missing = bool(getattr(raw,'mask',False))
        factor,unit,low,high = PROPS[prop]
        value = None if missing else float(raw)/factor
        if value is not None and not low <= value <= high:
            raise ValueError('Out-of-range soil value')
        return {'raw_value':None if missing else float(raw),'value':value,'unit':unit,
                'status':'source_nodata' if missing else 'valid',
                'cell_lon':lon[0],'cell_lat':lat[0],'crs':src.crs.to_string(),
                'resolution':list(src.res),'width':src.width,'height':src.height}


def run():
    if not os.path.ismount('/media/fpt/fpt2'):
        raise RuntimeError('Project drive not mounted')
    if shutil.disk_usage(ROOT).free < 100 * 1024**3:
        raise RuntimeError('Disk floor')
    lock = (ROOT/'state/soil_pilot.lock').open('a')
    fcntl.flock(lock,fcntl.LOCK_EX | fcntl.LOCK_NB)
    statepath = ROOT/'state/soil_pilot.json'
    state = json.loads(statepath.read_text()) if statepath.exists() else {
        'profile':'soilgrids-wcs-pilot-v1','jobs':{},'response_bytes':0}
    sites = json.loads((ROOT/'config/sites.json').read_text())
    # Three-site smoke first; then remaining existing pilot sites, no global rasters.
    sites.sort(key=lambda s:(s['name'] not in ('Citra','Waldo','Papanduva'),s['name']))
    state.update(status='running',pid=os.getpid(),total_jobs=len(sites)*len(PROPS)*len(DEPTHS)*len(STATS))
    out = ROOT/'data/raw/soilgrids'; out.mkdir(parents=True,exist_ok=True)
    normalized = ROOT/'data/normalized/soilgrids'; normalized.mkdir(parents=True,exist_ok=True)
    def save():
        state['updated'] = datetime.now(timezone.utc).isoformat()
        state['completed_jobs'] = sum(j.get('status') in ('valid','source_nodata') for j in state['jobs'].values())
        write_json(statepath,state)
        write_json(normalized/'pilot_soil.json',{'profile':state['profile'],
            'source':'ISRIC SoilGrids 2.0 WCS','license':'CC-BY-4.0',
            'limitations':['Static predicted soil, not field samples or current moisture.',
                'WCS returned grid may be reprojected; cell coordinates describe returned pixels, not native SoilGrids pixels.',
                'Q0.05/Q0.95 are marginal prediction bounds; not joint uncertainty or field drainage.',
                'Three surface depths only; no root-zone averaging or suitability classification.'],
            'records':[j for j in state['jobs'].values() if j.get('status') in ('valid','source_nodata')]})
    save()
    for site in sites:
        for prop in PROPS:
            for depth in DEPTHS:
                for stat in STATS:
                    key = '_'.join((site['id'],prop,depth,stat)); path = out/(key+'.tif')
                    old = state['jobs'].get(key,{})
                    if old.get('status') in ('valid','source_nodata'):
                        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest()!=old['sha256']:
                            raise RuntimeError('Existing soil cache checksum mismatch')
                        continue
                    if old.get('attempts',0) >= 3:
                        state['status']='blocked_source'; save(); return
                    url = url_for(site,prop,depth,stat)
                    job = {'site_id':site['id'],'site_name':site['name'],'lat':site['lat'],'lon':site['lon'],
                           'property':prop,'depth':depth,'statistic':stat,'url':url,
                           'attempts':old.get('attempts',0),'status':'pending'}
                    state['jobs'][key]=job
                    for attempt in range(job['attempts'],3):
                        job.update(attempts=attempt+1,status='running'); save()
                        try:
                            if state['response_bytes'] > 256*1024**2: raise RuntimeError('Pilot transfer cap')
                            with requests.get(url,stream=True,timeout=(15,45)) as response:
                                response.raise_for_status()
                                payload=bytearray()
                                for block in response.iter_content(65536):
                                    state['response_bytes']+=len(block);payload.extend(block)
                                    if len(payload)>2*1024**2:raise ValueError('Oversized subset')
                            if payload[:4] not in (b'II*\x00',b'MM\x00*'):raise ValueError('Non-TIFF response')
                            partial=path.with_suffix('.partial');partial.write_bytes(payload)
                            result=sample(partial,site,prop)
                            partial.replace(path)
                            job.update(result,sha256=hashlib.sha256(payload).hexdigest(),bytes=len(payload),
                                       raw_path=str(path.relative_to(ROOT)),retrieved=datetime.now(timezone.utc).isoformat())
                            job.pop('error',None);save()
                            print(json.dumps({'completed':state['completed_jobs'],'total':state['total_jobs'],'key':key}),flush=True)
                            break
                        except Exception as exc:
                            job.update(status='failed',error=type(exc).__name__+': '+str(exc)[:250]);save()
                            if attempt < 2:time.sleep(2**(attempt+1))
                    if job['status']=='failed':
                        state['status']='blocked_source';save();return
    state['status']='complete';save()


if __name__=='__main__':run()
