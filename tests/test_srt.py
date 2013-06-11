import unittest

from pycaption import SRTReader, SRTWriter

from .samples import SAMPLE_SRT
from .mixins import SRTTestingMixIn


class SRTReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SRTReader().detect(SAMPLE_SRT))

    def test_proper_pcc_format(self):
        captions = SRTReader().read(SAMPLE_SRT)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(7, len(captions["captions"]["en"]))

    def test_proper_timestamps(self):
        captions = SRTReader().read(SAMPLE_SRT)
        paragraph = captions["captions"]["en"][2]

        self.assertEquals(17000000, paragraph[0])
        self.assertEquals(18752000, paragraph[1])


class SRTWriterTestCase(unittest.TestCase, SRTTestingMixIn):

    def setUp(self):
        self.captions = SRTReader().read(SAMPLE_SRT)

    def test_write(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)
