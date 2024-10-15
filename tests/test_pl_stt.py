import unittest

from pycaption.exceptions import InvalidInputError
from pycaption.pl_stt import PLSTTReader

from tests.samples.srt import SAMPLE_SRT
from tests.samples.pl_stt import (
    SAMPLE_PL_STT,
    SAMPLE_PL_STT_NO_HEADER,
    SAMPLE_PL_STT_BAD_HEADER_1,
)


class PLSTTReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.reader = PLSTTReader()

    def test_positive_answer_for_detection(self):
        self.assertTrue(self.reader.detect(SAMPLE_PL_STT))

    def test_negative_answer_for_detection(self):
        self.assertFalse(self.reader.detect(SAMPLE_SRT))

    def test_caption_length(self):
        captions = self.reader.read(SAMPLE_PL_STT)
        self.assertEqual(len(captions.get_captions("en-US")), 5)

    def test_proper_timestamps(self):
        captions = self.reader.read(SAMPLE_PL_STT)
        cue = captions.get_captions("en-US")[2]
        self.assertEqual(cue.start, 65000000)
        self.assertEqual(cue.end, 66500000)

    def test_tags_removed_from_text(self):
        captions = self.reader.read(SAMPLE_PL_STT)

        cue = captions.get_captions("en-US")[0]
        self.assertEqual(cue.nodes[0].content, "First caption")

        cue = captions.get_captions("en-US")[1]
        self.assertEqual(cue.nodes[0].content, "Second caption, no line break")

        cue = captions.get_captions("en-US")[2]
        self.assertEqual(cue.nodes[0].content, "Third caption")

    def test_no_header_file(self):
        self.assertRaises(InvalidInputError, self.reader.read, SAMPLE_PL_STT_NO_HEADER)

    def test_bad_header_1(self):
        self.assertRaises(InvalidInputError, self.reader.read, SAMPLE_PL_STT_BAD_HEADER_1)
