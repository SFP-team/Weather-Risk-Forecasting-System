"""Private, loopback-only prototype API over existing archives; no downloads."""
import hashlib
import json
import math
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
import numpy as np
import pandas as pd
from discover import ROOT, write_json
from evidence_report import complete, chill, dry_spell
from evaluation_sites import cell_key
from postprocess import LandMask, extract
from production import analyse, sensitivity, PROFILES, CHANGES, LIMITATIONS

METHOD='location-evidence-v3'
PRODUCTION_PROFILE='legacy_paul_v1'
LAND=None
BUSY=threading.Lock()


def avg(values):
    values=list(values)
    return float(np.mean(values)) if values and all(v is not None and math.isfinite(v) for v in values) else None


def known_sites():
    """Pilot sites, enriched by the evaluation registry (same id/pin, plus county and role)."""
    sites={s['name']:s for s in json.loads((ROOT/'config/sites.json').read_text())}
    ev=ROOT/'config/evaluation_sites.json'
    if ev.exists():
        sites.update({s['name']:s for s in json.loads(ev.read_text())})
    return list(sites.values())


def haversine_km(lat1,lon1,lat2,lon2):
    a=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(a))


def hourly_for(lat,lon,root=ROOT):
    """Stored hourly series for the MERRA-2 cell containing the pin, or None. Never fetches."""
    ip=root/'config/hourly_index.json'
    if not ip.exists():return None,None
    index=json.loads(ip.read_text())
    entry=index['cells'].get(cell_key(index['axes'],lat,lon))
    if not entry:return None,None
    path=root/entry['path']
    if not path.exists():return None,None
    if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['parquet_sha256']:
        raise RuntimeError('Stored hourly checksum mismatch; refusing to analyse')
    source={'sha256':entry['parquet_sha256'],'site':entry['site'],'source_lat':entry['source_lat'],'source_lon':entry['source_lon'],
        'cell_degrees':[0.5,0.625],'distance_km':round(haversine_km(lat,lon,entry['source_lat'],entry['source_lon']),1),
        'note':'Hourly temperature is one series per 0.5 x 0.625 degree source cell; every pin inside the cell receives the same chill and calendar.'}
    return pd.read_parquet(path).set_index('time').tmean_c,source


def summarize(frame,hourly,lat):
    annual=[];monthly=[]
    # Respect the upstream investigation flag without modifying original data.
    rain=frame.precip_mm.mask(frame.precip_suspect_extreme.fillna(True))
    for year in range(2011,2026):
        start,end=f'{year}-01-01',f'{year+1}-01-01'
        p=complete(rain,start,end,'D');ok=p is not None and not ((p<0)|(p>1000)).any()
        cold=complete(frame.tmin_c,start,end,'D');hot=complete(frame.tmax_c,start,end,'D')
        solar=complete(frame.shortwave_mj_m2_day,start,end,'D')
        cs,ce=(f'{year}-05-01',f'{year}-09-01') if lat<0 else (f'{year-1}-11-01',f'{year}-03-01')
        annual.append({'year':year,'rain_mm':float(p.sum()) if ok else None,
            'cold_days':None if cold is None else int((cold<0).sum()),
            'hot_days':None if hot is None else int((hot>=35).sum()),
            'dry_spell':dry_spell(rain,start,end),'solar':None if solar is None else float(solar.mean()),
            'chill_hours':None if hourly is None else chill(hourly,cs,ce),
            'chill_start':cs,'chill_end_exclusive':ce})
        for month in range(1,13):
            a=pd.Timestamp(year,month,1);b=a+pd.offsets.MonthBegin(1)
            mp=complete(rain,a,b,'D');good=mp is not None and not ((mp<0)|(mp>1000)).any()
            mt=complete(frame.tmean_c,a,b,'D');ms=complete(frame.shortwave_mj_m2_day,a,b,'D')
            monthly.append({'year':year,'month':month,'rain_mm':float(mp.sum()) if good else None,
                            'tmean':None if mt is None else float(mt.mean()),'solar':None if ms is None else float(ms.mean())})
    climatology={k:[avg(r[k] for r in monthly if r['month']==m) for m in range(1,13)] for k in ('rain_mm','tmean','solar')}
    return annual,monthly,climatology


def production_block(hourly,padded,lat):
    """Open-field production analysis for pilot coordinates with hourly temperature; explicit unavailability otherwise."""
    if hourly is None or padded is None:
        return {'status':'unavailable','reason':'Hourly temperature has not been acquired for this coordinate; chill-triggered calendar and stage risks need complete hourly winters.'}
    daily=padded.set_index('time')
    result=analyse(hourly,daily,lat,PRODUCTION_PROFILE)
    result.update(status='available',scope='open_ground',
        sensitivity=sensitivity(hourly,daily,lat,list(PROFILES)),changes=CHANGES,limitations=LIMITATIONS)
    return result


def analyze(lat,lon):
    global LAND
    if not (math.isfinite(lat) and math.isfinite(lon) and -90<=lat<=90 and -180<=lon<=180):
        raise ValueError('Coordinates must be finite and within latitude/longitude bounds')
    if LAND is None:LAND=LandMask(ROOT)
    frame,provenance=extract(ROOT,lat,lon,LAND)
    if frame is None:return {'error':provenance['reason'],'status':'unsupported_location'}
    match=next((s for s in known_sites() if abs(s['lat']-lat)<1e-7 and abs(s['lon']-lon)<1e-7),None)
    site=match or {'name':'Selected location','lat':lat,'lon':lon}
    hourly,hourly_source=hourly_for(lat,lon)
    padded=None
    if hourly is not None:
        padded,_=extract(ROOT,lat,lon,LAND,padding=True)  # 2010 padding for the first northern winter
    sp=ROOT/'data/normalized/soilgrids/pilot_soil.json'
    soil=[r for r in json.loads(sp.read_text())['records']
          if abs(r['lat']-lat)<1e-7 and abs(r['lon']-lon)<1e-7] if sp.exists() else []
    # Public, derived point summaries only. Raw paths/requests stay server-side.
    soil=[{k:r[k] for k in ('property','depth','statistic','value','unit','status','cell_lon','cell_lat','sha256')} for r in soil]
    annual,monthly,climatology=summarize(frame.set_index('time'),hourly,lat)
    result={'site':site,'annual':annual,'monthly':monthly,'climatology':climatology,
        'soil':soil,'production':production_block(hourly,padded,lat),'hourly_source':hourly_source,
        'method_version':METHOD,'provenance':provenance,'hourly_sha256':hourly_source['sha256'] if hourly_source else None,
        'weather_content_sha256':hashlib.sha256(pd.util.hash_pandas_object(frame,index=False).values.tobytes()).hexdigest()}
    result['analysis_id']=hashlib.sha256(json.dumps(result,sort_keys=True,allow_nan=False).encode()).hexdigest()[:20]
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass  # Do not log user coordinates.
    def do_GET(self):
        parsed=urlsplit(self.path)
        status=200
        if parsed.path=='/api/health':result={'status':'ready','mode':'private-read-only-prototype'}
        elif parsed.path!='/api/analysis':status,result=404,{'error':'Not found'}
        elif not BUSY.acquire(blocking=False):status,result=503,{'error':'Another analysis is running. Please try again shortly.'}
        else:
            try:
                q=parse_qs(parsed.query)
                result=analyze(float(q['latitude'][0]),float(q['longitude'][0]))
            except (ValueError,KeyError,IndexError):status,result=400,{'error':'Invalid coordinate input'}
            except Exception:status,result=500,{'error':'Archive analysis failed. No substitute result was generated.'}
            finally:BUSY.release()
        payload=json.dumps(result,allow_nan=False).encode()
        self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store')
        self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)


if __name__=='__main__':
    import sys
    if '--snapshots' in sys.argv:
        sites=[s for s in known_sites() if s['name'] in ('Papanduva','Citra','Waldo') or s.get('role')]
        snapshots={s['name']:analyze(s['lat'],s['lon']) for s in sites}
        write_json(ROOT/'reports/ui_snapshots.json',{'sites':snapshots})
        print(json.dumps({'snapshots':len(snapshots),'production_available':[n for n,r in snapshots.items() if r['production']['status']=='available']}))
    else:
        print('Private API: http://127.0.0.1:8787',flush=True)
        ThreadingHTTPServer(('127.0.0.1',8787),Handler).serve_forever()
