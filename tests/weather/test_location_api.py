import unittest
import hashlib
import http.client
import io
import json
import os
import tempfile
import threading
import time
from datetime import datetime
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import zarr
import location_api as api
import production
from location_api import summarize, avg, production_block
from hourly_archive import ArchiveGap
from test_place_index import geonames_fixture
from pilot import GROUPS, NAMES
from postprocess import LandMask, extract, km_distance

Q='/api/analysis?latitude=29.4112&longitude=-82.1437'


def isolated(test):
    """Point the result cache and access log of `api` at a temporary folder for one test."""
    directory=tempfile.TemporaryDirectory();test.addCleanup(directory.cleanup);root=Path(directory.name)
    for name,value in (('CACHE',api.ResultCache(root/'cache')),('ACCESS',api.AccessLog(root/'access.jsonl'))):
        patcher=patch.object(api,name,value);patcher.start();test.addCleanup(patcher.stop)
    return root


def land_root(directory):
    """Natural Earth-shaped fixture: one 0.2 degree square of land centred on 0 N, 1 E."""
    root=Path(directory)
    target=root/'data/reference/ne_10m_land.geojson'
    target.parent.mkdir(parents=True)
    data=json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'featurecla':'Land'},
        'geometry':{'type':'Polygon','coordinates':[[[0.9,-0.1],[1.1,-0.1],[1.1,0.1],[0.9,0.1],[0.9,-0.1]]]}}]}).encode()
    target.write_bytes(data)
    target.with_suffix('.provenance.json').write_text(json.dumps({'sha256':hashlib.sha256(data).hexdigest()}))
    return root


class LocationTests(unittest.TestCase):
    def setUp(self):
        self.frame=pd.DataFrame({'tmean_c':20.,'tmin_c':-1.,'tmax_c':36.,'precip_mm':2.,
            'shortwave_mj_m2_day':18.,'precip_suspect_extreme':False},index=pd.date_range('2011-01-01','2025-12-31'))
    def test_known_answer_and_hourly_absence(self):
        a,m,c=summarize(self.frame,None,29.)
        self.assertEqual(a[1]['rain_mm'],732.)
        self.assertEqual(a[1]['cold_days'],366)
        self.assertEqual(a[1]['hot_days'],366)
        self.assertEqual(a[1]['solar'],18.)
        self.assertIsNone(a[1]['chill_hours'])
        self.assertEqual(len(m),180)
    def test_flagged_rain_not_zero(self):
        self.frame.loc['2012-01-01','precip_suspect_extreme']=True
        a,_,c=summarize(self.frame,None,-26.)
        self.assertIsNone(a[1]['rain_mm']);self.assertIsNone(a[1]['dry_spell'])
        self.assertIsNone(c['rain_mm'][0]);self.assertEqual(a[0]['rain_mm'],730.)
    def test_radiation_gap_and_nullable_average(self):
        self.frame.loc['2011-02-01','shortwave_mj_m2_day']=np.nan
        a,_,_=summarize(self.frame,None,29.)
        self.assertIsNone(a[0]['solar']);self.assertIsNone(avg([2.,None]))
    def test_production_unavailable_without_hourly(self):
        block=production_block(None,None,29.,-82.)
        self.assertEqual(block['status'],'unavailable')
        self.assertIn('reason',block)
    def test_no_hourly_keeps_daily_warm_days_distinct_and_excludes_incomplete_winter(self):
        daily=self.frame.rename_axis('time').reset_index()
        block=production_block(None,daily,29.,-82.)
        self.assertEqual(block['status'],'unavailable')
        warm=block['warm_midwinter_fallback']
        self.assertEqual(warm['unit'],'days')
        self.assertIsNone(warm['seasons'][0]['value'])
        self.assertEqual(warm['summary']['n'],14)
        self.assertEqual(warm['seasons'][1]['value'],93)
        self.assertNotIn('calendar',block)
    def test_production_attached_with_hourly(self):
        hourly=pd.DataFrame({'tmean_c':5.,'dewpoint_mean_c':2.},index=pd.date_range('2010-01-01','2026-01-01',freq='h',inclusive='left'))
        padded=pd.DataFrame({'tmean_c':17.,'tmin_c':-2.2,'tmax_c':36.,'precip_mm':2.,'rh_mean_pct':80.,
            'shortwave_mj_m2_day':18.,'precip_suspect_extreme':False},index=pd.date_range('2010-01-01','2025-12-31')).rename_axis('time').reset_index()
        with patch.object(production,'analyse',wraps=production.analyse) as counted:
            block=production_block(hourly,padded,29.,-82.)
        self.assertEqual(counted.call_count,len(api.PROFILES)-1)  # sensitivity reuses the primary result
        self.assertEqual(block['sensitivity'][block['profile']]['flowering_freeze_frequency'],
                         block['risks']['by_id']['flowering_freeze']['frequency'])
        self.assertEqual(block['status'],'available')
        self.assertEqual(block['scope'],'open_ground')
        self.assertEqual(block['status_counts'],{'complete':15})
        self.assertEqual(block['classification']['multi_feature']['majority'],'Deciduous')
        self.assertEqual(block['calendar']['chill']['median_date'],'11-03')  # 50 h at 5 C under the v3 primary
        self.assertEqual(block['profile'],'stage_thermal_v3')
        self.assertEqual(block['managed_cycle']['role'],'comparison')
        frost=block['risks']['by_id']['fruit_frost']
        self.assertEqual((frost['years_with_event'],frost['valid_years']), (15,15))
        self.assertEqual(frost['eligibility'],'ranked')
        self.assertNotIn('chill_shortfall',[r['risk'] for r in block['risks']['ranked']])
        json.dumps(block,allow_nan=False)

    def test_land_mask_excludes_only_marked_placeholder(self):
        def feature(label, x):
            return {'type':'Feature', 'properties':{'featurecla':label},
                    'geometry':{'type':'Polygon', 'coordinates':[
                        [[x-0.1,-0.1],[x+0.1,-0.1],[x+0.1,0.1],[x-0.1,0.1],[x-0.1,-0.1]] ]}}
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            target=root/'data/reference/ne_10m_land.geojson'
            target.parent.mkdir(parents=True)
            data=json.dumps({'type':'FeatureCollection','features':[
                feature('Null island',0),feature('Land',1),feature(None,2)]}).encode()
            target.write_bytes(data)
            target.with_suffix('.provenance.json').write_text(json.dumps({
                'sha256':hashlib.sha256(data).hexdigest()}))
            land=LandMask(root)
            self.assertFalse(land.covers(0,0))
            self.assertTrue(land.covers(0,1))
            self.assertTrue(land.covers(0,2))
            self.assertEqual(land.metadata['excluded_null_island_features'],1)


class CoastTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.root=land_root(self.directory.name);self.land=LandMask(self.root)
        (self.root/'state').mkdir();(self.root/'state/global.json').write_text('{"status":"complete"}')
        for source in ('met_daily','solar_daily'):
            group=zarr.open_group(str(self.root/'data/normalized/global'/source),mode='w')
            group.attrs.update(complete=True,profile='synthetic-test-only')
            for name,values in [('time',np.arange(5844)),('lat',[-0.25,0.25]),('lon',[0.625,1.25])]:group.create_dataset(name,data=np.asarray(values))
            for variable in GROUPS[source]:
                group.create_dataset(NAMES[variable],data=np.full((5844,2,2),10.,dtype='f4')).attrs['units']='synthetic'
            zarr.consolidate_metadata(str(self.root/'data/normalized/global'/source))
    def test_distance_is_great_circle_to_nearest_land(self):
        self.assertEqual(self.land.distance_km(0.,1.),0.)
        self.assertAlmostEqual(self.land.distance_km(0.,1.13),km_distance(0.,1.13,0.,1.1),6)
        self.assertAlmostEqual(self.land.distance_km(0.13,1.13),km_distance(0.13,1.13,0.1,1.1),6)
        self.assertIsNone(self.land.distance_km(0.,1.2))  # About 11 km offshore.
    def test_coastal_pin_kept_with_snap_distance(self):
        frame,meta=extract(self.root,0.,1.13,self.land)
        self.assertEqual(len(frame),5479)
        self.assertEqual(meta['request'],{'latitude':0.,'longitude':1.13})
        self.assertEqual(meta['land_snap_km'],round(km_distance(0.,1.13,0.,1.1),2))
        self.assertEqual(meta['land_snap_km'],3.34)
        # The source cell is chosen from the original pin, not the nearest land point.
        self.assertEqual(meta['sources'][0]['source_longitude'],1.25)
        self.assertEqual(meta['sources'][0]['distance_km'],km_distance(0.,1.13,0.25,1.25))
        _,inland=extract(self.root,0.,1.,self.land)
        self.assertNotIn('land_snap_km',inland)
    def test_far_ocean_refused_plainly(self):
        frame,meta=extract(self.root,0.,1.2,self.land)
        self.assertIsNone(frame)
        self.assertEqual(meta['status'],'unsupported_location')
        self.assertEqual(meta['reason'],'This point is in the sea or more than 5 km from land in our coastline map. Move the pin onto land.')


class AnalyzeTests(unittest.TestCase):
    def test_archive_gap_falls_back_to_daily_only(self):
        daily=pd.DataFrame({'tmean_c':20.,'tmin_c':-1.,'tmax_c':36.,'precip_mm':2.,'shortwave_mj_m2_day':18.,
            'precip_suspect_extreme':False},index=pd.date_range('2010-01-01','2025-12-31')).rename_axis('time').reset_index()
        meta={'status':'weather_available','limitations':['Gridded weather.']}
        def fake_extract(root,lat,lon,land,padding=False):
            return (daily if padding else daily.loc[daily.time>='2011-01-01'].reset_index(drop=True)),dict(meta)
        with tempfile.TemporaryDirectory() as directory, patch.object(api,'ROOT',Path(directory)), \
                patch.object(api,'LAND',object()), patch.object(api,'extract',fake_extract), \
                patch.object(api,'known_sites',return_value=[]), patch.object(api,'planting_window',return_value={'status':'unavailable'}), \
                patch.object(api,'hourly_for',side_effect=ArchiveGap('never downloaded')):
            result=api.analyze(18.,-66.)
        self.assertEqual(result['production']['status'],'unavailable')
        self.assertEqual(result['production']['reason'],api.ARCHIVE_GAP)
        self.assertIn('warm_midwinter_fallback',result['production'])
        self.assertEqual(result['provenance']['limitations'],['Gridded weather.',api.ARCHIVE_GAP])
        self.assertIsNone(result['hourly_source']);self.assertIsNone(result['hourly_sha256'])
        self.assertIsNone(result['annual'][0]['chill_hours']);self.assertEqual(result['annual'][0]['rain_mm'],730.)
        json.dumps(result,allow_nan=False)
    def test_other_hourly_failures_stay_fatal(self):
        with patch.object(api,'LAND',object()), patch.object(api,'extract',return_value=(pd.DataFrame(),{'limitations':[]})), \
                patch.object(api,'known_sites',return_value=[]), patch.object(api,'hourly_for',side_effect=RuntimeError('checksum mismatch')):
            with self.assertRaises(RuntimeError):api.analyze(18.,-66.)


class RespondTests(unittest.TestCase):
    def setUp(self):
        self.root=isolated(self)
    def call(self,query,**kw):
        with patch.object(api,'analyze',**(kw or {'side_effect':lambda lat,lon:{'lat':lat,'lon':lon}})):
            status,payload,_=api.respond('/api/analysis?'+query)
        return status,json.loads(payload)
    def test_accepted_spellings(self):
        for query,expected in [('latitude=29,41&longitude=-82.14',(29.41,-82.14)),('latitude=%2029.41%20&longitude=%2B5',(29.41,5.)),
                               ('latitude=-.5&longitude=1e1',(-.5,10.)),('latitude=90&longitude=-180',(90.,-180.))]:
            self.assertEqual(self.call(query),(200,{'lat':expected[0],'lon':expected[1]}),query)
    def test_rejections_name_the_parameter(self):
        for query,message in [('longitude=1','Missing latitude.'),
                              ('lat=1&lon=2','Missing latitude. Use latitude= and longitude= (not lat, lon or lng).'),
                              ('latitude=1&lng=2','Missing longitude. Use latitude= and longitude= (not lat, lon or lng).'),
                              ('latitude=91&longitude=0','Latitude must be between -90 and 90 degrees.'),
                              ('latitude=1&longitude=-180.5','Longitude must be between -180 and 180 degrees.'),
                              ('latitude=1e999&longitude=0','Latitude must be between -90 and 90 degrees.'),
                              ('latitude=2_9&longitude=1','Latitude is not a number. Use decimal degrees such as 29.41.'),
                              ('latitude=%D9%A1&longitude=1','Latitude is not a number. Use decimal degrees such as 29.41.'),
                              ('latitude=1,2,3&longitude=1','Latitude is not a number. Use decimal degrees such as 29.41.'),
                              ('latitude=nan&longitude=1','Latitude is not a number. Use decimal degrees such as 29.41.'),
                              ('latitude=&longitude=1','Latitude is not a number. Use decimal degrees such as 29.41.'),
                              ('latitude=1&latitude=2&longitude=1','Give latitude only once.')]:
            self.assertEqual(self.call(query),(400,{'error':message}),query)
    def test_analysis_failure_is_json_and_query_not_logged(self):
        stderr=io.StringIO()
        with patch('sys.stderr',stderr):
            failed=self.call('latitude=29.4112&longitude=-82.1437',side_effect=RuntimeError('boom'))
            nan=self.call('latitude=29.4112&longitude=-82.1437',return_value={'x':float('nan')})
        self.assertEqual(failed,(500,{'error':'The archive could not analyse this point. No substitute result was generated.','code':'analysis_failed'}))
        self.assertEqual(nan,failed)
        self.assertIn('RuntimeError: boom',stderr.getvalue());self.assertNotIn('29.4112',stderr.getvalue())
        self.assertFalse(api.BUSY.locked());self.assertIsNone(api.BUSY_SINCE)
    def test_unsupported_location_is_422(self):
        self.assertEqual(self.call('latitude=0&longitude=-140',return_value={'error':'sea','status':'unsupported_location'}),
                         (422,{'error':'sea','status':'unsupported_location'}))
    def test_health_reports_busy(self):
        self.assertEqual(json.loads(api.respond('/api/health')[1])['status'],'ready')
        with api.BUSY:
            self.assertEqual(json.loads(api.respond('/api/health')[1])['status'],'busy')
            status,_,log=api.respond('/api/analysis?latitude=1&longitude=1')
            self.assertEqual((status,log),(503,{'cache':'miss','busy_rejected':True}))
    def test_health_fields_and_busy_clock(self):
        health=json.loads(api.respond('/api/health')[1])
        self.assertEqual(health,{'status':'ready','mode':'private-read-only-prototype','method':api.METHOD,
                                 'busy_since':None,'busy_seconds':None,'cache':{'entries':0,'hits':0,'misses':0}})
        started,release=threading.Event(),threading.Event()
        def slow(lat,lon):
            started.set();release.wait(10);return {'lat':lat}
        with patch.object(api,'analyze',side_effect=slow):
            worker=threading.Thread(target=api.respond,args=(Q,));worker.start()
            self.assertTrue(started.wait(10))
            busy=json.loads(api.respond('/api/health')[1])
            release.set();worker.join(10)
        self.assertEqual(busy['status'],'busy')
        self.assertEqual(datetime.fromisoformat(busy['busy_since']).utcoffset().total_seconds(),0)
        self.assertIsInstance(busy['busy_seconds'],float);self.assertGreaterEqual(busy['busy_seconds'],0)
        self.assertEqual(busy['cache'],{'entries':0,'hits':0,'misses':1})
        after=json.loads(api.respond('/api/health')[1])
        self.assertEqual((after['status'],after['busy_since'],after['busy_seconds']),('ready',None,None))
        self.assertEqual(after['cache']['entries'],1)


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.root=isolated(self)
    def test_hit_is_byte_identical_to_a_fresh_result(self):
        result={'site':{'name':'Selected location'},'value':1.25,'unicode':'Ñuble'}
        with patch.object(api,'analyze',return_value=result) as analyze:
            fresh=api.respond(Q);hit=api.respond(Q)
        analyze.assert_called_once()
        self.assertEqual((fresh[0],fresh[2]['cache'],hit[0],hit[2]['cache']),(200,'miss',200,'hit'))
        self.assertEqual(hit[1],fresh[1])
        # Another process reads the stored file; an uncached recomputation gives the same bytes again.
        disk=api.ResultCache(self.root/'cache')
        with patch.object(api,'CACHE',disk), patch.object(api,'analyze',side_effect=AssertionError('not cached')):
            self.assertEqual(api.respond(Q)[1],fresh[1])
        self.assertEqual(disk.stats(),{'entries':1,'hits':1,'misses':0})
        with patch.object(api,'CACHE',api.ResultCache(self.root/'other')), patch.object(api,'analyze',return_value=result):
            self.assertEqual(api.respond(Q)[1],fresh[1])
        self.assertEqual([path.name for path in (self.root/'cache').iterdir()],[api.cache_key(29.4112,-82.1437)+'.json'])
    def test_only_successful_analyses_are_stored(self):
        for kw in ({'return_value':{'error':'sea','status':'unsupported_location'}},{'side_effect':RuntimeError('boom')},
                   {'return_value':{'x':float('nan')}}):
            with patch.object(api,'analyze',**kw), patch('sys.stderr',io.StringIO()):
                self.assertNotEqual(api.respond(Q)[0],200)
        api.respond('/api/analysis?latitude=91&longitude=0');api.respond('/api/health')
        self.assertFalse((self.root/'cache').exists())
        self.assertEqual(api.CACHE.stats()['entries'],0)
    def test_key_covers_method_profile_code_and_coordinates(self):
        base=api.cache_key(29.4112,-82.1437)
        self.assertEqual(api.CODE_ID,api.code_identity())
        self.assertNotEqual(base,api.cache_key(29.4112,-82.1438))
        for name,value in (('METHOD','location-evidence-test'),('PRODUCTION_PROFILE','stage_risks_v2'),('CODE_ID','0'*64)):
            with patch.object(api,name,value):
                self.assertNotEqual(api.cache_key(29.4112,-82.1437),base,name)
    def test_memory_lru_and_files_are_bounded(self):
        cache=api.ResultCache(self.root/'bounded',size=2,files=3)
        for i in range(5):
            cache.put(f'k{i}',b'{"i":%d}'%i)
            os.utime(self.root/f'bounded/k{i}.json',(1000+i,1000+i))  # Deterministic ages for the mtime prune.
        self.assertEqual(list(cache.memory),['k3','k4'])
        self.assertEqual(sorted(path.name for path in (self.root/'bounded').iterdir()),['k2.json','k3.json','k4.json'])
        self.assertEqual(cache.get('k2'),b'{"i":2}')  # From disk, then remembered.
        self.assertEqual(list(cache.memory),['k4','k2'])
        self.assertIsNone(cache.get('k0'))
        self.assertEqual((cache.hits,cache.misses),(1,1))


class ServerTests(unittest.TestCase):
    """A real Handler on an ephemeral loopback port."""
    def setUp(self):
        self.root=isolated(self)
        patcher=patch.object(api,'analyze',side_effect=lambda lat,lon:{'lat':lat,'lon':lon})
        self.analyze=patcher.start();self.addCleanup(patcher.stop)
        self.server=ThreadingHTTPServer(('127.0.0.1',0),api.Handler)
        threading.Thread(target=self.server.serve_forever,daemon=True).start()
        self.addCleanup(self.server.server_close);self.addCleanup(self.server.shutdown)
    def lines(self):
        path=self.root/'access.jsonl'
        return path.read_text().splitlines() if path.exists() else []
    def get(self,path,headers=None):
        """GET with exact headers (Host defaults to the API address; None omits it); waits for the access-log line."""
        headers={'Host':'127.0.0.1:8787',**(headers or {})};logged=len(self.lines())
        connection=http.client.HTTPConnection(*self.server.server_address,timeout=10)
        try:
            connection.putrequest('GET',path,skip_host=True,skip_accept_encoding=True)
            for name,value in headers.items():
                if value is not None:connection.putheader(name,value)
            connection.endheaders();response=connection.getresponse();body=json.loads(response.read())
        finally:connection.close()
        deadline=time.monotonic()+5
        while len(self.lines())==logged and time.monotonic()<deadline:time.sleep(.01)
        return response.status,body
    def test_host_must_name_the_loopback_api(self):
        for host in ('127.0.0.1:8787','localhost:8787','LOCALHOST:8787'):
            self.assertEqual(self.get('/api/health',{'Host':host})[0],200,host)
        for host in ('evil.example:8787','127.0.0.1:5173','127.0.0.1','localhost',None):
            self.assertEqual(self.get(Q,{'Host':host}),(403,api.FORBIDDEN_HOST),host)
        self.analyze.assert_not_called()
    def test_cross_site_requests_are_refused_before_analysis(self):
        for headers in ({'Sec-Fetch-Site':'cross-site'},{'Sec-Fetch-Site':'same-site'},{'Origin':'http://evil.example'},
                        {'Origin':'null'},{'Origin':'http://localhost:5173','Sec-Fetch-Site':'cross-site'}):
            self.assertEqual(self.get(Q,headers),(403,{'error':'Cross-site API request refused','code':'forbidden_origin'}),headers)
        self.analyze.assert_not_called()
        for headers in ({'Sec-Fetch-Site':'same-origin'},{'Sec-Fetch-Site':'none'},{'Origin':'http://localhost:5173'},
                        {'Origin':'http://127.0.0.1:5173'},{'Origin':'http://127.0.0.1:8787'},{'Origin':'http://localhost:8787'},{}):
            self.assertEqual(self.get('/api/health',headers)[0],200,headers)
        self.assertEqual(self.get(Q,{'Origin':'http://127.0.0.1:5173','Sec-Fetch-Site':'same-origin'})[0],200)
    def test_health_over_http(self):
        status,health=self.get('/api/health')
        self.assertEqual((status,sorted(health)),(200,['busy_seconds','busy_since','cache','method','mode','status']))
        self.assertEqual(health['method'],api.METHOD)
    def test_access_log_has_fields_but_no_coordinates(self):
        self.get(Q);self.get(Q);self.get('/api/29.4112/-82.1437');self.get(Q,{'Origin':'http://evil.example'})
        self.get('/api/analysis?latitude=29.4112&longitude=181')
        with api.BUSY:self.get('/api/analysis?latitude=29.4112&longitude=-82.1438')
        text=(self.root/'access.jsonl').read_text()
        for fragment in ('29.4112','82.1437','82.1438','latitude','longitude','?'):
            self.assertNotIn(fragment,text)
        records=[json.loads(line) for line in text.splitlines()]
        self.assertTrue(all(sorted(r)==['busy_rejected','cache','duration_ms','path','status','ts'] for r in records))
        self.assertEqual([(r['path'],r['status'],r['cache'],r['busy_rejected']) for r in records],
                         [('/api/analysis',200,'miss',False),('/api/analysis',200,'hit',False),('other',404,None,False),
                          ('/api/analysis',403,None,False),('/api/analysis',400,None,False),('/api/analysis',503,'miss',True)])
        self.assertTrue(all(datetime.fromisoformat(r['ts']).utcoffset().total_seconds()==0 for r in records))
    def test_place_queries_are_not_logged(self):
        with patch.object(api,'PLACES',geonames_fixture(self.root)):
            self.assertEqual(self.get('/api/places?q=Jaiba')[0],200)
        text=(self.root/'access.jsonl').read_text()
        self.assertNotIn('aiba',text)
        self.assertEqual(json.loads(text.splitlines()[-1])['path'],'/api/places')


class PlaceRouteTests(unittest.TestCase):
    def setUp(self):
        self.root=isolated(self)
        patcher=patch.object(api,'PLACES',geonames_fixture(self.root));patcher.start();self.addCleanup(patcher.stop)
    def call(self,target):
        status,payload,_=api.respond(target)
        return status,json.loads(payload)
    def test_search_answers_during_an_analysis_with_attribution(self):
        with api.BUSY:
            status,body=self.call('/api/places?q=Jaiba')
        self.assertEqual(status,200)
        self.assertEqual([(r['name'],r['region'],r['country']) for r in body['results']],[('Jaíba','Minas Gerais','Brazil')])
        self.assertEqual((body['source']['name'],body['source']['license'],body['source']['data_date']),('GeoNames','CC BY 4.0','2026-10-01'))
    def test_bad_queries_are_refused_with_the_reason(self):
        limit='limit must be a whole number from 1 to 25.'
        for target,message in [('/api/places','Missing q. Type a place name.'),('/api/places?q=%20,.','Type a place name.'),
                               ('/api/places?q=a&q=b','Give q only once.'),('/api/places?q='+'x'*101,'The place name is longer than 100 characters.'),
                               ('/api/places?q=alma&limit=0',limit),('/api/places?q=alma&limit=26',limit),('/api/places?q=alma&limit=x',limit)]:
            self.assertEqual(self.call(target),(400,{'error':message}),target)
    def test_missing_index_is_503_not_an_empty_result(self):
        with patch.object(api,'PLACES',self.root/'absent.sqlite'):
            self.assertEqual(self.call('/api/places?q=Jaiba'),(503,api.PLACE_UNAVAILABLE))


class AccessLogTests(unittest.TestCase):
    def test_rotates_at_the_limit_and_keeps_a_fixed_number_of_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'access.jsonl';log=api.AccessLog(path,limit=300,keep=2)
            for i in range(40):log.write(path='/api/health',status=200,duration_ms=1.,busy_rejected=False,cache=None)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()),['access.jsonl','access.jsonl.1','access.jsonl.2'])
            self.assertTrue(all(p.stat().st_size<=300 for p in Path(directory).iterdir()))
            self.assertEqual(api.AccessLog(path).limit,10*2**20)


if __name__=='__main__':unittest.main()
