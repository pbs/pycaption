import unittest

from pycaption import DFXPReader, DFXPWriter

from .samples import SAMPLE_DFXP
from .mixins import XMLTestingMixIn


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_proper_pcc_format(self):
        captions = DFXPReader().read(SAMPLE_DFXP)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(7, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions["captions"]["en-US"][2]

        self.assertEquals(17000000, paragraph[0])
        self.assertEquals(18752000, paragraph[1])


class DFXPWriterTestCase(unittest.TestCase, XMLTestingMixIn):

    def setUp(self):
        self.captions = DFXPReader().read(SAMPLE_DFXP)

    def test_write(self):
        results = DFXPWriter().write(self.captions)
        self.assertXMLEquals(SAMPLE_DFXP, results)
