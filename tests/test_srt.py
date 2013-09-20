import unittest

from pycaption import SRTReader

from .samples import SAMPLE_SRT


class SRTReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SRTReader().detect(SAMPLE_SRT))

    def test_caption_length(self):
        captions = SRTReader().read(SAMPLE_SRT)

        self.assertEquals(7, len(captions.get_captions("en-US")))

    def test_proper_timestamps(self):
        captions = SRTReader().read(SAMPLE_SRT)
        paragraph = captions.get_captions("en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)
