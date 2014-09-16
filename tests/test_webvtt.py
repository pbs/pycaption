import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SAMIReader,
    CaptionReadNoCaptions, CaptionReadError, CaptionReadSyntaxError
)

from .samples import *  # noqa


class WebVTTReaderTestCase(unittest.TestCase):

    def setUp(self):
        self.reader = WebVTTReader()

    def test_positive_answer_for_detection(self):
        self.assertTrue(self.reader.detect(SAMPLE_WEBVTT))

    def test_negative_answer_for_detection(self):
        self.assertFalse(self.reader.detect(SAMPLE_SRT))

    def test_caption_length(self):
        captions = self.reader.read(SAMPLE_WEBVTT_2)
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
        result = self.reader._remove_styles(
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

    def test_invalid_files(self):
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            """
            NOTE Cues without text are invalid.

            00:00:20,000 --> 00:00:10,000
            """
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader().read,
            """
            00:00:20,000 --> 00:00:10,000
            Start time is greater than end time.
            """
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader().read,
            """
            00:00:20,000 --> 00:00:30,000
            Start times should be consecutive.

            00:00:10,000 --> 00:00:20,000
            This cue starts before the previous one.
            """
        )

    def test_webvtt_empty_cue(self):
        self.assertEqual(1, len(self.reader.read(
                SAMPLE_WEBVTT_EMPTY_CUE).get_captions('en-US')))


class WebVTTWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.writer = WebVTTWriter()

    def test_double_br(self):
        captions = SAMIReader().read(SAMPLE_SAMI_DOUBLE_BR)

        self.assertEqual(SAMPLE_WEBVTT_DOUBLE_BR, self.writer.write(captions))
