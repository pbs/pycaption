import unittest

from pycaption import SCCReader

from .samples import SAMPLE_SCC

TOLERANCE_MICROSECONDS = 500 * 1000

class SCCReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SCCReader().detect(SAMPLE_SCC))

    def test_caption_length(self):
        captions = SCCReader().read(SAMPLE_SCC)

        self.assertEquals(7, len(captions.get_captions("en-US")))

    def test_proper_timestamps(self):
        captions = SCCReader().read(SAMPLE_SCC)
        paragraph = captions.get_captions("en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        self.assertTrue(delta_start < TOLERANCE_MICROSECONDS)
        self.assertTrue(delta_end < TOLERANCE_MICROSECONDS)

