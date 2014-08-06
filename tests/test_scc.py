import unittest

from pycaption import SCCReader, CaptionReadNoCaptions

from .samples import SAMPLE_SCC, SAMPLE_SCC_EMPTY

TOLERANCE_MICROSECONDS = 500 * 1000

class SCCReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SCCReader().detect(SAMPLE_SCC.decode(u'utf-8')))

    def test_caption_length(self):
        captions = SCCReader().read(SAMPLE_SCC.decode(u'utf-8'))

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SCCReader().read(SAMPLE_SCC.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        self.assertTrue(delta_start < TOLERANCE_MICROSECONDS)
        self.assertTrue(delta_end < TOLERANCE_MICROSECONDS)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SCCReader().read, SAMPLE_SCC_EMPTY.decode(u'utf-8'))

