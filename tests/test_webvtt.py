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
        self.assertTrue(self.reader.detect(SAMPLE_WEBVTT.decode(u'utf-8')))

    def test_negative_answer_for_detection(self):
        self.assertFalse(self.reader.detect(SAMPLE_SRT.decode(u'utf-8')))

    def test_caption_length(self):
        captions = self.reader.read(SAMPLE_WEBVTT_2.decode(u'utf-8'))
        self.assertEqual(len(captions.get_captions(u'en-US')), 7)

    def test_read_supports_multiple_languages(self):
        captions = self.reader.read(SAMPLE_WEBVTT.decode(u'utf-8'), lang=u'es')
        self.assertIsNotNone(captions.get_captions(u'es'))

    def test_proper_timestamps(self):
        captions = self.reader.read(SAMPLE_WEBVTT.decode(u'utf-8'))
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
            WebVTTReader().read, SAMPLE_WEBVTT_EMPTY.decode(u'utf-8'))

    def test_invalid_files(self):
        self.assertRaises(
            CaptionReadSyntaxError,
            WebVTTReader().read,
            u"""
            NOTE Cues without text are invalid.

            00:00:20,000 --> 00:00:10,000
            """
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader().read,
            u"""
            00:00:20,000 --> 00:00:10,000
            Start time is greater than end time.
            """
        )

        self.assertRaises(
            CaptionReadError,
            WebVTTReader().read,
            u"""
            00:00:20,000 --> 00:00:30,000
            Start times should be consecutive.

            00:00:10,000 --> 00:00:20,000
            This cue starts before the previous one.
            """
        )


class WebVTTWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.writer = WebVTTWriter()

    def test_double_br(self):
        captions = SAMIReader().read(SAMPLE_SAMI_DOUBLE_BR.decode(u'utf-8'))

        self.assertEqual(SAMPLE_WEBVTT_DOUBLE_BR.decode(u'utf-8'), self.writer.write(captions))
