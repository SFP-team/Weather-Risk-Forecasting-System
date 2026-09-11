import unittest
import hashlib
import json
import tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from location_api import summarize, avg
from postprocess import LandMask


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


if __name__=='__main__':unittest.main()
