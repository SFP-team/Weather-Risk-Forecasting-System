import tempfile
import unittest
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import numpy as np
import rasterio
from rasterio.transform import from_origin
from soil_pilot import sample, url_for


class SoilTests(unittest.TestCase):
    def fixture(self, value, prop='phh2o', lon=0.5):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'test.tif'
            with rasterio.open(path,'w',driver='GTiff',height=1,width=1,count=1,
                dtype='int16',crs='EPSG:4326',transform=from_origin(0,1,1,1),nodata=-32768) as dst:
                dst.write(np.array([[value]],dtype='int16'),1)
            return sample(path,{'lat':0.5,'lon':lon},prop)
    def test_ph_units(self):
        self.assertEqual(self.fixture(55)['value'],5.5)
    def test_texture_percent(self):
        self.assertEqual(self.fixture(650,'sand')['value'],65)
    def test_nodata(self):
        self.assertIsNone(self.fixture(-32768)['value'])
    def test_invalid_range(self):
        with self.assertRaises(ValueError):self.fixture(200)
    def test_no_nearest_land_snap(self):
        with self.assertRaises(ValueError):self.fixture(55,lon=2)
    def test_request_preserves_quantile(self):
        args=parse_qs(urlparse(url_for({'lat':29,'lon':-82},'phh2o','0-5cm','Q0.05')).query)
        self.assertEqual(args['COVERAGEID'],['phh2o_0-5cm_Q0.05'])
        self.assertEqual(len(args['SUBSET']),2)


if __name__=='__main__':unittest.main()
