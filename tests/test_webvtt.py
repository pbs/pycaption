import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SAMIReader, DFXPReader,
    CaptionReadNoCaptions, CaptionReadError, CaptionReadSyntaxError
)

from .samples.dfxp import DFXP_STYLE_REGION_ALIGN_CONFLICT
from .samples.sami import SAMPLE_SAMI_DOUBLE_BR
from .samples.srt import SAMPLE_SRT
from .samples.webvtt import (
    SAMPLE_WEBVTT, SAMPLE_WEBVTT_2, SAMPLE_WEBVTT_EMPTY, SAMPLE_WEBVTT_DOUBLE_BR,
    WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN, SAMPLE_WEBVTT_LAST_CUE_ZERO_START
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
        self.assertEqual(len(captions.get_captions(u'en-US')), 7)

    def test_read_supports_multiple_languages(self):
        captions = self.reader.read(SAMPLE_WEBVTT, lang=u'es')
        self.assertIsNotNone(captions.get_captions(u'es'))

    def test_proper_timestamps(self):
        captions = self.reader.read(SAMPLE_WEBVTT)
        cue = captions.get_captions(u'en-US')[2]
        self.assertEqual(cue.start, 17000000)
        self.assertEqual(cue.end, 18752000)

    def test_webvtt_cue_components_removed_from_text(self):
        result = self.reader._remove_styles(
            u"<c vIntro><b>Wikipedia</b> is a great adventure. <i>It may have "
            u"its shortcomings</i>, but it is<u> the largest</u> collective "
            u"knowledge construction endevour</c> <ruby>base text <rt>"
            u"annotation</rt></ruby> <v Audry><b>Yes</b>, indeed!"
        )
        expected = (
            u"Wikipedia is a great adventure. It may have "
            u"its shortcomings, but it is the largest collective "
            u"knowledge construction endevour base text annotation"
            u" Audry: Yes, indeed!"
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
            (u"\n"
             u"00:00:20.000 --> 00:00:10.000\n"
             u"foo bar baz")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            (u"00:00:20.000 --> 00:00:10.000\n"
             u"Start time is greater than end time.\n")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            (u"00:00:20.000 --> 00:00:30.000\n"
             u"Start times should be consecutive.\n"
             u"\n"
             u"00:00:10.000 --> 00:00:20.000\n"
             u"This cue starts before the previous one.\n")
        )

    def test_ignoring_timing_errors(self):
        # Even if timing errors are ignored, this has to raise an exception
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            (u"\nNOTE invalid cue stamp\n"
             u"00:00:20.000 --> \n"
             u"foo bar baz\n")
        )

        # And this too
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            (u"\n00:00:20,000 --> 00:00:22,000\n"
             u"Note the comma instead of point.\n")
        )

        try:
            WebVTTReader().read(
                (u"\n"
                 u"00:00:20.000 --> 00:00:10.000\n"
                 u"Start time is greater than end time.\n")
            )
        except CaptionReadError:
            self.fail(u"Shouldn't raise CaptionReadError")

        try:
            WebVTTReader().read(
                (u"\n"
                 u"00:00:20.000 --> 00:00:30.000\n"
                 u"Start times should be consecutive.\n"
                 u"\n"
                 u"00:00:10.000 --> 00:00:20.000\n"
                 u"This cue starts before the previous one.\n")

            )
        except CaptionReadError:
            self.fail(u"Shouldn't raise CaptionReadError")

    def test_invalid_files(self):
        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            (u"00:00:20.000 --> 00:00:10.000\n"
                u"Start time is greater than end time.")
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader(ignore_timing_errors=False).read,
            (u"00:00:20.000 --> 00:00:30.000\n"
                u"Start times should be consecutive.\n"
                u"\n"
                u"00:00:10.000 --> 00:00:20.000\n"
                u"This cue starts before the previous one.\n")
        )

    def test_zero_start(self):
        captions = self.reader.read(SAMPLE_WEBVTT_LAST_CUE_ZERO_START)
        cue = captions.get_captions(u'en-US')[0]
        self.assertEquals(cue.start, 0)


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
        self.assertEquals(
            WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN, results)
