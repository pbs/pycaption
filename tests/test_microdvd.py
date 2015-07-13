import unittest

from pycaption import MicroDVDReader, CaptionReadNoCaptions

from .samples.microdvd import SAMPLE_MICRODVD, SAMPLE_MICRODVD_EMPTY


class MicroDVDReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(MicroDVDReader().detect(SAMPLE_MICRODVD))

    def test_caption_length(self):
        captions = MicroDVDReader().read(SAMPLE_MICRODVD)

        self.assertEquals(12, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = MicroDVDReader().read(SAMPLE_MICRODVD)
        paragraph = captions.get_captions(u"en-US")[2]

        # due to lossy nature of microsec -> frame# we check that
        # conversion is within a second of expected value
        # (fyi: timestamps in examples/ and test/samples/ differ)
        self.assertTrue(abs(17350000 - paragraph.start) < 10**6)
        self.assertTrue(abs(18752000 - paragraph.end) < 10**6)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            MicroDVDReader().read, SAMPLE_MICRODVD_EMPTY)
