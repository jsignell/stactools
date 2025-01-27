import os.path
import unittest
from contextlib import contextmanager
from tempfile import TemporaryDirectory

import rasterio
from stactools.core import utils
from stactools.core.utils.convert import cogify, cogify_subdatasets

from tests import test_data


class CogifyTest(unittest.TestCase):
    @contextmanager
    def cogify(self, **kwargs):
        infile = test_data.get_path("data-files/core/byte.tif")
        with TemporaryDirectory() as directory:
            outfile = os.path.join(directory, "byte.tif")
            cogify(infile, outfile, **kwargs)
            yield outfile

    def test_default(self):
        with self.cogify() as outfile:
            self.assertTrue(os.path.exists(outfile))
            with rasterio.open(outfile) as dataset:
                self.assertEqual(
                    dataset.compression, rasterio.enums.Compression.deflate
                )

    def test_profile(self):
        with self.cogify(profile={"compress": "lzw"}) as outfile:
            self.assertTrue(os.path.exists(outfile))
            with rasterio.open(outfile) as dataset:
                self.assertEqual(dataset.compression, rasterio.enums.Compression.lzw)

    def test_subdataset(self):
        infile = test_data.get_path("data-files/hdf/AMSR_E_L3_RainGrid_B05_200707.h5")
        with TemporaryDirectory() as directory:
            with utils.ignore_not_georeferenced():
                paths, names = cogify_subdatasets(infile, directory)
            self.assertEqual(
                set(names),
                {
                    "MonthlyRainTotal_GeoGrid_Data_Fields_RrLandRain",
                    "MonthlyRainTotal_GeoGrid_Data_Fields_TbOceanRain",
                },
            )
            for path in paths:
                self.assertTrue(os.path.exists(path))
                with utils.ignore_not_georeferenced():
                    with rasterio.open(path) as dataset:
                        self.assertEqual(
                            dataset.compression, rasterio.enums.Compression.deflate
                        )
