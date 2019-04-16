from __future__ import unicode_literals
import unittest

from pycaption import SRTReader, CaptionReadNoCaptions

from .samples.srt import (
    SAMPLE_SRT, SAMPLE_SRT_NUMERIC,
    SAMPLE_SRT_EMPTY, SAMPLE_SRT_BLANK_LINES, SAMPLE_SRT_TRAILING_BLANKS)


class SRTReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SRTReader().detect(SAMPLE_SRT))

    def test_caption_length(self):
        captions = SRTReader().read(SAMPLE_SRT)

        self.assertEqual(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SRTReader().read(SAMPLE_SRT)
        paragraph = captions.get_captions(u"en-US")[2]

        self.assertEqual(17000000, paragraph.start)
        self.assertEqual(18752000, paragraph.end)

    def test_numeric_captions(self):
        captions = SRTReader().read(SAMPLE_SRT_NUMERIC)
        self.assertEqual(7, len(captions.get_captions(u"en-US")))

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SRTReader().read, SAMPLE_SRT_EMPTY)

    def test_extra_empty_line(self):
        captions = SRTReader().read(SAMPLE_SRT_BLANK_LINES)
        self.assertEqual(2, len(captions.get_captions(u"en-US")))

    def test_extra_trailing_empty_line(self):
        captions = SRTReader().read(SAMPLE_SRT_TRAILING_BLANKS)
        self.assertEqual(2, len(captions.get_captions(u"en-US")))
