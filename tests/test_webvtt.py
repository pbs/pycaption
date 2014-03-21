import unittest

from pycaption import WebVTTReader, CaptionReadNoCaptions

from .samples import SAMPLE_WEBVTT, SAMPLE_SRT, SAMPLE_WEBVTT_EMPTY


class WebVTTReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.reader = WebVTTReader()

    def test_positive_answer_for_detection(self):
        self.assertTrue(self.reader.detect(SAMPLE_WEBVTT))

    def test_negative_answer_for_detection(self):
        self.assertFalse(self.reader.detect(SAMPLE_SRT))

    def test_caption_length(self):
        captions = self.reader.read(SAMPLE_WEBVTT)
        self.assertEqual(len(captions.get_captions('en-US')), 7)

    def test_read_supports_multiple_languages(self):
        captions = self.reader.read(SAMPLE_WEBVTT, lang='es')
        self.assertIsNotNone(captions.get_captions('es'))

    def test_proper_timestamps(self):
        captions = self.reader.read(SAMPLE_WEBVTT)
        cue = captions.get_captions('en-US')[2]
        self.assertEqual(cue.start, 17000000)
        self.assertEqual(cue.end, 18752000)

    def test_webvtt_cue_components_removed_from_text(self):
        result = self.reader._clean(
            "\n"  # the first line is sckipped by the cleaner
            "<c vIntro><b>Wikipedia</b> is a great adventure. <i>It may have "
            "its shortcomings</i>, but it is<u> the largest</u> collective "
            "knowledge construction endevour</c> <ruby>base text <rt>"
            "annotation</rt></ruby> <v Audry><b>Yes</b>, indeed!"
        )
        expected = (
            "Wikipedia is a great adventure. It may have "
            "its shortcomings, but it is the largest collective "
            "knowledge construction endevour base text annotation"
            " Audry: Yes, indeed!"
        )
        self.assertEqual(result, expected)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            WebVTTReader().read, SAMPLE_WEBVTT_EMPTY)
