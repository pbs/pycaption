import unittest
import os

from pycaption import MicroDVDReader, CaptionReadNoCaptions
from pycaption.exceptions import InvalidFormatError

from .samples.microdvd import SAMPLE_MICRODVD, SAMPLE_MICRODVD_EMPTY, INVALID_FORMAT_SAMPLE_MICRODVD

from pycaption.base import DEFAULT_LANGUAGE_CODE


class MicroDVDReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(MicroDVDReader().detect(SAMPLE_MICRODVD))

    def test_caption_length(self):
        captions = MicroDVDReader().read(SAMPLE_MICRODVD)
        self.assertEquals(7, len(captions.get_captions(DEFAULT_LANGUAGE_CODE)))

    def test_proper_timestamps(self):
        captions = MicroDVDReader().read(SAMPLE_MICRODVD)
        paragraph = captions.get_captions(DEFAULT_LANGUAGE_CODE)[2]

        # due to lossy nature of microsec -> frame# we check that
        # conversion is within a second of expected value
        # (fyi: timestamps in examples/ and test/samples/ differ)
        self.assertTrue(abs(17350000 - paragraph.start) < 10**6)
        self.assertTrue(abs(18752000 - paragraph.end) < 10**6)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            MicroDVDReader().read, SAMPLE_MICRODVD_EMPTY)

    def test_invalid_format(self):
        self.assertRaises(
            InvalidFormatError,
            MicroDVDReader().read, INVALID_FORMAT_SAMPLE_MICRODVD)

