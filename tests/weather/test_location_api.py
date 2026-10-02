import unittest
import hashlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import numpy as np
import pandas as pd
import zarr
import location_api as api
from location_api import summarize, avg, production_block
from hourly_archive import ArchiveGap
from pilot import GROUPS, NAMES
from postprocess import LandMask, extract, km_distance


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
        block=production_block(hourly,padded,29.,-82.)
        self.assertEqual(block['status'],'available')
        self.assertEqual(block['scope'],'open_ground')
        self.assertEqual(block['status_counts'],{'complete':15})
        self.assertEqual(block['classification']['multi_feature']['majority'],'Deciduous')
        self.assertEqual(block['calendar']['chill']['median_date'],'11-05')  # 100 h at 5 C under the v3 primary
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
    def call(self,query,**kw):
        with patch.object(api,'analyze',**(kw or {'side_effect':lambda lat,lon:{'lat':lat,'lon':lon}})):
            status,payload=api.respond('/api/analysis?'+query)
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
        self.assertFalse(api.BUSY.locked())
    def test_unsupported_location_is_422(self):
        self.assertEqual(self.call('latitude=0&longitude=-140',return_value={'error':'sea','status':'unsupported_location'}),
                         (422,{'error':'sea','status':'unsupported_location'}))
    def test_health_reports_busy(self):
        self.assertEqual(json.loads(api.respond('/api/health')[1])['status'],'ready')
        with api.BUSY:
            self.assertEqual(json.loads(api.respond('/api/health')[1])['status'],'busy')
            self.assertEqual(api.respond('/api/analysis?latitude=1&longitude=1')[0],503)


if __name__=='__main__':unittest.main()
