import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SAMIReader, DFXPReader,
    CaptionReadNoCaptions, CaptionReadError, CaptionReadSyntaxError
)

from tests.samples.dfxp import DFXP_STYLE_REGION_ALIGN_CONFLICT
from tests.samples.sami import SAMPLE_SAMI_DOUBLE_BR
from tests.samples.srt import SAMPLE_SRT
from tests.samples.webvtt import (
    SAMPLE_WEBVTT, SAMPLE_WEBVTT_2, SAMPLE_WEBVTT_EMPTY,
    SAMPLE_WEBVTT_DOUBLE_BR,
    WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN, SAMPLE_WEBVTT_LAST_CUE_ZERO_START,
    SAMPLE_WEBVTT_EMPTY_CUE
)


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

    def test_not_ignoring_timing_errors(self):
        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            ("\n"
             "00:00:20.000 --> 00:00:10.000\n"
             "foo bar baz")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            ("00:00:20.000 --> 00:00:10.000\n"
             "Start time is greater than end time.\n")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            ("00:00:20.000 --> 00:00:30.000\n"
             "Start times should be consecutive.\n"
             "\n"
             "00:00:10.000 --> 00:00:20.000\n"
             "This cue starts before the previous one.\n")
        )

    def test_ignoring_timing_errors(self):
        # Even if timing errors are ignored, this has to raise an exception
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            ("\nNOTE invalid cue stamp\n"
             "00:00:20.000 --> \n"
             "foo bar baz\n")
        )

        # And this too
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            ("\n00:00:20,000 --> 00:00:22,000\n"
             "Note the comma instead of point.\n")
        )

        try:
            WebVTTReader().read(
                ("\n"
                 "00:00:20.000 --> 00:00:10.000\n"
                 "Start time is greater than end time.\n")
            )
        except CaptionReadError:
            self.fail("Shouldn't raise CaptionReadError")

        try:
            WebVTTReader().read(
                ("\n"
                 "00:00:20.000 --> 00:00:30.000\n"
                 "Start times should be consecutive.\n"
                 "\n"
                 "00:00:10.000 --> 00:00:20.000\n"
                 "This cue starts before the previous one.\n")

            )
        except CaptionReadError:
            self.fail("Shouldn't raise CaptionReadError")

    def test_invalid_files(self):
        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            ("00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            ("00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n")
        )

    def test_zero_start(self):
        captions = self.reader.read(SAMPLE_WEBVTT_LAST_CUE_ZERO_START)
        cue = captions.get_captions('en-US')[0]
        self.assertEqual(cue.start, 0)

    def test_webvtt_empty_cue(self):
        self.assertEqual(1, len(self.reader.read(
                SAMPLE_WEBVTT_EMPTY_CUE).get_captions('en-US')))


class WebVTTWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.writer = WebVTTWriter()

    def test_double_br(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_DOUBLE_BR)
        results = WebVTTWriter().write(caption_set)
        self.assertEqual(SAMPLE_WEBVTT_DOUBLE_BR, results)

    def test_break_node_positioning_is_ignored(self):
        caption_set = DFXPReader().read(DFXP_STYLE_REGION_ALIGN_CONFLICT)
        results = WebVTTWriter().write(caption_set)
        self.assertEqual(WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN, results)
