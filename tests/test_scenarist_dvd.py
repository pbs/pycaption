import unittest

from pycaption import (
    SAMIReader, ScenaristDVDWriter, DFXPReader)
from tests.samples.dfxp import DFXP_FROM_SAMI_WITH_POSITIONING


class ScenaristDVDWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.writer = ScenaristDVDWriter()

    def test_styling(self):
        caption_set = DFXPReader().read(DFXP_FROM_SAMI_WITH_POSITIONING)
        results = self.writer.write(caption_set)
        f = open('a.zip', 'wb+')
        f.write(results)
        f.close()