import glob
import tempfile
import unittest
import zipfile
from io import BytesIO

from pycaption import (ScenaristDVDWriter, DFXPReader)
from tests.samples.dfxp import DFXP_FROM_SAMI_WITH_POSITIONING


class ScenaristDVDWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.writer = ScenaristDVDWriter()

    def test_styling(self):
        caption_set = DFXPReader().read(DFXP_FROM_SAMI_WITH_POSITIONING)
        results = self.writer.write(caption_set)
        with tempfile.TemporaryDirectory() as tmpDir:
            with zipfile.ZipFile(BytesIO(results), 'r') as zip_ref:
                zip_ref.extractall(tmpDir)
                self.assertEqual(len(glob.glob(tmpDir + '/*.sst')), 1)
                self.assertEqual(len(glob.glob(tmpDir + '/*.tif')), 7)
