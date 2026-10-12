"""Private, loopback-only prototype API over existing archives; no downloads."""
import contextlib
import hashlib
import io
import json
import math
import os
import re
import sys
import threading
import time
import traceback
from collections import OrderedDict
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import numpy as np
import pandas as pd
from discover import ROOT, write_json
from evidence_report import complete, chill, dry_spell
from evaluation_sites import cell_key
from postprocess import LandMask, extract
from production import analyse, sensitivity, warm_midwinter_daily, PRIMARY_PROFILE, PROFILES, CHANGES, LIMITATIONS
from planting import planting_window
from hourly_archive import ArchiveGap, hourly_from_cache

METHOD='location-evidence-v5'
PRODUCTION_PROFILE=PRIMARY_PROFILE
BENCHMARK=Path(__file__).with_name('benchmark_sites.json')
LAND=None
BUSY=threading.Lock()
BUSY_SINCE=None  # (UTC datetime, monotonic seconds) while an analysis holds BUSY; /api/health reads it without locking.
ARCHIVE_GAP='The hourly archive has no downloaded data for this 0.5 x 0.625 degree cell, so chill, the crop calendar and stage risks are not computed here. Daily weather is shown; no substitute hourly series is generated.'
# ASCII decimal degrees with an optional sign and exponent; one decimal point or comma, no underscores.
NUMBER=re.compile(r'[+-]?(?:\d+(?:[.,]\d*)?|[.,]\d+)(?:[eE][+-]?\d+)?',re.ASCII)
FAILED={'error':'The archive could not analyse this point. No substitute result was generated.','code':'analysis_failed'}
# Only the loopback API and the preview UI may call. A DNS-rebinding page reaches this port under its own host name.
ALLOWED_HOSTS=('127.0.0.1:8787','localhost:8787')
ALLOWED_ORIGINS=('http://127.0.0.1:5173','http://localhost:5173','http://127.0.0.1:8787','http://localhost:8787')
FORBIDDEN_HOST={'error':'Request refused','code':'forbidden_host'}
FORBIDDEN_ORIGIN={'error':'Cross-site API request refused','code':'forbidden_origin'}
ROUTES=('/api/health','/api/analysis')


def code_identity(directory=Path(__file__).parent):
    """sha256 over the files that shape an analysis result, so a code change never serves an old cached result.
    Data are not hashed: clear cache/location_api after an archive, land-mask, soil or config/ update."""
    digest=hashlib.sha256()
    for name in ('production.py','location_api.py','planting.py','hourly_archive.py','postprocess.py','evidence_report.py',
                 'evaluation_sites.py','benchmark_sites.json'):
        digest.update(name.encode()+b'\0'+(directory/name).read_bytes())
    return digest.hexdigest()


CODE_ID=code_identity()


class ResultCache:
    """Serialized 200 responses by key: an in-memory LRU over JSON files. A hit returns the stored bytes unchanged."""
    def __init__(self,directory,size=64,files=2000):
        self.directory,self.size,self.files=Path(directory),size,files
        self.memory=OrderedDict();self.lock=threading.Lock();self.hits=self.misses=0
    def stats(self):
        return {'entries':len(self.memory),'hits':self.hits,'misses':self.misses}  # Plain reads; health never waits.
    def remember(self,key,payload):
        with self.lock:
            self.memory[key]=payload;self.memory.move_to_end(key)
            while len(self.memory)>self.size:self.memory.popitem(last=False)
    def get(self,key):
        with self.lock:
            payload=self.memory.get(key)
            if payload is not None:self.memory.move_to_end(key)
        if payload is None:
            path=self.directory/f'{key}.json'
            try:payload=path.read_bytes()
            except OSError:payload=None
            if payload is not None:
                self.remember(key,payload)
                with contextlib.suppress(OSError):os.utime(path)  # A fresh mtime keeps recently used files when pruning.
        with self.lock:
            if payload is None:self.misses+=1
            else:self.hits+=1
        return payload
    def put(self,key,payload):
        self.remember(key,payload)
        try:
            self.directory.mkdir(parents=True,exist_ok=True)
            partial=self.directory/f'{key}.json.partial'
            with partial.open('wb') as f:f.write(payload);f.flush();os.fsync(f.fileno())
            os.replace(partial,self.directory/f'{key}.json')
            stored=sorted(self.directory.glob('*.json'),key=lambda path:path.stat().st_mtime)
            for old in stored[:max(len(stored)-self.files,0)]:old.unlink(missing_ok=True)
        except OSError:
            print(traceback.format_exc(),file=sys.stderr,flush=True)  # A failed cache write must not fail the analysis.


class AccessLog:
    """One JSON line per request, never with coordinates; rotated at `limit` bytes, keeping `keep` older files."""
    def __init__(self,path,limit=10*2**20,keep=5):
        self.path,self.limit,self.keep,self.lock=Path(path),limit,keep,threading.Lock()
    def write(self,**fields):
        line=json.dumps({'ts':datetime.now(timezone.utc).isoformat(timespec='milliseconds'),**fields})+'\n'
        older=lambda i:self.path.with_name(f'{self.path.name}.{i}')
        try:
            with self.lock:
                self.path.parent.mkdir(parents=True,exist_ok=True)
                if self.path.exists() and self.path.stat().st_size+len(line)>self.limit:
                    older(self.keep).unlink(missing_ok=True)
                    for i in range(self.keep-1,0,-1):
                        if older(i).exists():os.replace(older(i),older(i+1))
                    os.replace(self.path,older(1))
                with self.path.open('a',encoding='utf-8') as f:f.write(line)
        except OSError:
            print(traceback.format_exc(),file=sys.stderr,flush=True)


CACHE=ResultCache(ROOT/'cache/location_api')
ACCESS=AccessLog(ROOT/'logs/location_api_access.jsonl')


def avg(values):
    values=list(values)
    return float(np.mean(values)) if values and all(v is not None and math.isfinite(v) for v in values) else None


def known_sites():
    """Pilot sites, enriched by the evaluation registry (same id/pin, plus county and role), then literature-benchmark sites."""
    sites={s['name']:s for s in json.loads((ROOT/'config/sites.json').read_text())}
    ev=ROOT/'config/evaluation_sites.json'
    if ev.exists():
        sites.update({s['name']:s for s in json.loads(ev.read_text())})
    if BENCHMARK.exists():
        for s in json.loads(BENCHMARK.read_text())['sites']:
            sites.setdefault(s['name'],{'id':s['id'],'name':s['name'],'lat':s['lat'],'lon':s['lon'],'region':s['admin1'],
                'country':s['country'],'group':'Benchmark · '+s['group'],'role':'benchmark','benchmark_id':s['id']})
    return list(sites.values())


def haversine_km(lat1,lon1,lat2,lon2):
    a=math.sin(math.radians(lat2-lat1)/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(math.radians(lon2-lon1)/2)**2
    return 2*6371.0088*math.asin(math.sqrt(a))


def hourly_for(lat,lon,root=ROOT):
    """Stored hourly temperature and dewpoint for the MERRA-2 cell containing the pin, or None. Never fetches."""
    ip=root/'config/hourly_index.json'
    if not ip.exists():return hourly_from_cache(root,lat,lon)
    index=json.loads(ip.read_text())
    entry=index['cells'].get(cell_key(index['axes'],lat,lon))
    if not entry:return hourly_from_cache(root,lat,lon)
    path=root/entry['path']
    if not path.exists():raise RuntimeError('Indexed hourly file is missing; refusing analysis')
    data=path.read_bytes()  # Hash and parse the same bytes, so the checked file is the analysed file.
    if hashlib.sha256(data).hexdigest()!=entry['parquet_sha256']:
        raise RuntimeError('Stored hourly checksum mismatch; refusing to analyse')
    source={'sha256':entry['parquet_sha256'],'site':entry['site'],'source_lat':entry['source_lat'],'source_lon':entry['source_lon'],
        'cell_degrees':[0.5,0.625],'distance_km':round(haversine_km(lat,lon,entry['source_lat'],entry['source_lon']),1),
        'note':'Hourly temperature is one series per 0.5 x 0.625 degree source cell; every pin inside the cell receives the same chill and calendar.'}
    return pd.read_parquet(io.BytesIO(data)).set_index('time')[['tmean_c','dewpoint_mean_c']],source


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


def production_block(hourly,padded,lat,lon,reason=None):
    """Existing-data production analysis; daily warm-weather context is not an hourly calendar substitute."""
    if hourly is None or padded is None:
        result={'status':'unavailable','reason':reason or 'Complete hourly temperature is not exposed for this coordinate by the current location adapter. The chill-triggered calendar and stage risks require a complete extracted hourly series; no substitute calendar is generated.'}
        if padded is not None:
            result['warm_midwinter_fallback']=warm_midwinter_daily(padded.set_index('time'),lat)
        return result
    daily=padded.set_index('time')
    weather=dict(dewpoint=hourly.dewpoint_mean_c,lon=lon)
    result=analyse(hourly.tmean_c,daily,lat,PRODUCTION_PROFILE,**weather)
    result.update(status='available',scope='open_ground',
        sensitivity=sensitivity(hourly.tmean_c,daily,lat,list(PROFILES),**weather,primary=result,primary_profile=PRODUCTION_PROFILE),
        changes=CHANGES,limitations=LIMITATIONS)
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
    gap=None
    try:hourly,hourly_source=hourly_for(lat,lon)
    except ArchiveGap:hourly=hourly_source=None;gap=ARCHIVE_GAP;provenance['limitations']=[*provenance['limitations'],gap]
    # 2010 padding also covers the first northern daily warm-weather fallback.
    padded,_=extract(ROOT,lat,lon,LAND,padding=True)
    sp=ROOT/'data/normalized/soilgrids/pilot_soil.json'
    soil=[r for r in json.loads(sp.read_text())['records']
          if abs(r['lat']-lat)<1e-7 and abs(r['lon']-lon)<1e-7] if sp.exists() else []
    # Public, derived point summaries only. Raw paths/requests stay server-side.
    soil=[{k:r[k] for k in ('property','depth','statistic','value','unit','status','cell_lon','cell_lat','sha256')} for r in soil]
    annual,monthly,climatology=summarize(frame.set_index('time'),None if hourly is None else hourly.tmean_c,lat)
    result={'site':site,'annual':annual,'monthly':monthly,'climatology':climatology,
        'soil':soil,'production':production_block(hourly,padded,lat,lon,gap),'hourly_source':hourly_source,
        'planting':planting_window(site),
        'method_version':METHOD,'provenance':provenance,'hourly_sha256':hourly_source['sha256'] if hourly_source else None,
        'weather_content_sha256':hashlib.sha256(pd.util.hash_pandas_object(frame,index=False).values.tobytes()).hexdigest()}
    result['analysis_id']=hashlib.sha256(json.dumps(result,sort_keys=True,allow_nan=False).encode()).hexdigest()[:20]
    return result


def coordinate(query,name,bound):
    """One strictly parsed decimal-degree value, or ValueError with a message naming the parameter."""
    values=query.get(name)
    if not values:
        hint=' Use latitude= and longitude= (not lat, lon or lng).' if any(k in query for k in ('lat','lon','lng')) else ''
        raise ValueError(f'Missing {name}.{hint}')
    if len(values)>1:raise ValueError(f'Give {name} only once.')
    text=values[0].strip()
    if not NUMBER.fullmatch(text):raise ValueError(f'{name.capitalize()} is not a number. Use decimal degrees such as 29.41.')
    value=float(text.replace(',','.'))
    if not -bound<=value<=bound:raise ValueError(f'{name.capitalize()} must be between -{bound} and {bound} degrees.')
    return value


def reply(status,result):
    return status,json.dumps(result,allow_nan=False).encode()


def cache_key(lat,lon):
    """Identity of one analysis result: method, primary profile, code and coordinates (read at call time)."""
    return hashlib.sha256('\0'.join((METHOD,PRODUCTION_PROFILE,CODE_ID,repr(float(lat)),repr(float(lon)))).encode()).hexdigest()


def health():
    """Cheap and lock-free: plain reads of the busy flag, the start stamp and the cache counters."""
    since=BUSY_SINCE
    return {'status':'busy' if since or BUSY.locked() else 'ready','mode':'private-read-only-prototype','method':METHOD,
        'busy_since':since[0].isoformat(timespec='seconds') if since else None,
        'busy_seconds':round(time.monotonic()-since[1],3) if since else None,'cache':CACHE.stats()}


def respond(target):
    """HTTP status, serialized JSON and access-log fields for one GET; serialization failures become 500 JSON, not dropped connections.

    Only 200 analyses are cached, and a hit is served even while another analysis holds BUSY."""
    global BUSY_SINCE
    parsed=urlsplit(target);log={'cache':None,'busy_rejected':False}
    if parsed.path=='/api/health':return (*reply(200,health()),log)
    if parsed.path!='/api/analysis':return (*reply(404,{'error':'Not found'}),log)
    query=parse_qs(parsed.query,keep_blank_values=True)
    try:lat,lon=coordinate(query,'latitude',90),coordinate(query,'longitude',180)
    except ValueError as exc:return (*reply(400,{'error':str(exc)}),log)
    key=cache_key(lat,lon);payload=CACHE.get(key);log['cache']='miss' if payload is None else 'hit'
    if payload is not None:return 200,payload,log
    if not BUSY.acquire(blocking=False):
        log['busy_rejected']=True
        return (*reply(503,{'error':'Another analysis is running. Please try again shortly.'}),log)
    BUSY_SINCE=(datetime.now(timezone.utc),time.monotonic())
    try:
        result=analyze(lat,lon)
        status,payload=reply(422 if result.get('status')=='unsupported_location' else 200,result)
        if status==200:CACHE.put(key,payload)
        return status,payload,log
    except Exception:
        print(traceback.format_exc(),file=sys.stderr,flush=True)  # Traceback only; the query is never logged.
        return (*reply(500,FAILED),log)
    finally:
        BUSY_SINCE=None;BUSY.release()


def refusal(headers):
    """403 body unless the request targets this API by a loopback name and comes from no page or an allowed one.
    Missing Origin and Sec-Fetch-Site are allowed: command-line clients send neither."""
    if (headers.get('Host') or '').lower() not in ALLOWED_HOSTS:return FORBIDDEN_HOST
    site,origin=headers.get('Sec-Fetch-Site'),headers.get('Origin')
    if (site is not None and site not in ('same-origin','none')) or (origin is not None and origin not in ALLOWED_ORIGINS):
        return FORBIDDEN_ORIGIN
    return None


class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):pass  # Do not log user coordinates; ACCESS writes a coordinate-free line instead.
    def do_GET(self):
        started=time.monotonic();refused=refusal(self.headers)
        status,payload,log=(*reply(403,refused),{'cache':None,'busy_rejected':False}) if refused else respond(self.path)
        try:
            self.send_response(status);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store')
            self.send_header('Content-Length',str(len(payload)));self.end_headers();self.wfile.write(payload)
        finally:
            path=urlsplit(self.path).path  # Unknown paths could carry coordinates, so they are logged as 'other'.
            ACCESS.write(path=path if path in ROUTES else 'other',status=status,
                duration_ms=round((time.monotonic()-started)*1000,1),**log)


if __name__=='__main__':
    if '--snapshots' in sys.argv:
        sites=[s for s in known_sites() if s['name'] in ('Papanduva','Citra','Waldo') or s.get('role')]
        snapshots={s['name']:analyze(s['lat'],s['lon']) for s in sites}
        write_json(ROOT/'reports/ui_snapshots.json',{'sites':snapshots})
        print(json.dumps({'snapshots':len(snapshots),'production_available':[n for n,r in snapshots.items() if r['production']['status']=='available']}))
    else:
        print('Private API: http://127.0.0.1:8787',flush=True)
        ThreadingHTTPServer(('127.0.0.1',8787),Handler).serve_forever()
