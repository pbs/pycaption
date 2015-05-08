import unittest

from pycaption import (
    SAMIReader, SAMIWriter, SRTWriter, DFXPWriter, WebVTTWriter)

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE,
    SAMPLE_SRT_UNICODE, SAMPLE_SAMI_SYNTAX_ERROR,
    DFXP_FROM_SAMI_WITH_POSITIONING, DFXP_FROM_SAMI_WITH_POSITIONING_UTF8,
    DFXP_FROM_SAMI_WITH_POSITIONING_UNICODE, SAMPLE_WEBVTT_FROM_SAMI,
    SAMPLE_SAMI_PARTIAL_MARGINS, SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED,
    SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS, SAMPLE_SAMI_LANG_MARGIN,
    SAMPLE_DFXP_FROM_SAMI_WITH_LANG_MARGINS, SAMPLE_SAMI_WITH_SPAN,
    SAMPLE_DFXP_FROM_SAMI_WITH_SPAN, SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN,
    SAMPLE_DFXP_FROM_SAMI_WITH_BAD_SPAN_ALIGN,
    SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS
)
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class SAMItoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI.decode(u'utf-8'))
        results = SAMIWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI.decode(u'utf-8'), results)

    def test_sami_to_sami_utf8_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UTF8.decode(u'utf-8'))
        results = SAMIWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_sami_to_sami_unicode_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UNICODE)
        results = SAMIWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_is_relativized(self):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = SAMIReader().read(SAMPLE_SAMI_PARTIAL_MARGINS)
        result = SAMIWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)
        self.assertEqual(result, SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED)


class SAMItoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI.decode(u'utf-8'))
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT.decode(u'utf-8'), results)

    def test_sami_to_srt_utf8_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UTF8.decode(u'utf-8'))
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

    def test_sami_to_srt_unicode_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UNICODE)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)


class SAMItoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_sami_to_dfxp_unicode_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UNICODE)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            DFXP_FROM_SAMI_WITH_POSITIONING_UNICODE,
            results
        )

    def test_sami_to_dfxp_with_margin(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_PARTIAL_MARGINS)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(
            SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS,
            results
        )

    def test_sami_to_dfxp_with_margin_for_language(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_LANG_MARGIN)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(
            SAMPLE_DFXP_FROM_SAMI_WITH_LANG_MARGINS,
            results
        )

    def test_sami_to_dfxp_with_span(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_SPAN)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(
            SAMPLE_DFXP_FROM_SAMI_WITH_SPAN,
            results
        )

    def test_sami_to_dfxp_with_bad_span_align(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(
            SAMPLE_DFXP_FROM_SAMI_WITH_BAD_SPAN_ALIGN,
            results
        )

    def test_sami_to_dfxp_ignores_multiple_span_aligns(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(
            SAMPLE_DFXP_FROM_SAMI_WITH_BAD_SPAN_ALIGN,
            results
        )

    def test_sami_to_dfxp_xml_output(self):
        captions = SAMIReader().read(SAMPLE_SAMI_SYNTAX_ERROR.decode('utf-8'))
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertTrue(u'xmlns="http://www.w3.org/ns/ttml"' in results)
        self.assertTrue(
            u'xmlns:tts="http://www.w3.org/ns/ttml#styling"' in results)


class SAMItoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_sami_to_webvtt_utf8_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UTF8.decode(u'utf-8'))
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI.decode(u'utf-8'),
                                results)

    def test_sami_to_webvtt_unicode_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_UNICODE)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI.decode(u'utf-8'),
                                results)


class SAMIWithMissingLanguage(unittest.TestCase, SAMITestingMixIn):

    def setUp(self):
        self.sample_sami = u"""
        <SAMI>
        <Head><STYLE TYPE="text/css"></Style></Head>
        <BODY>
        <Sync Start=0><P Class=ENCC></p></sync>
        <Sync Start=1301><P Class=ENCC>>> FUNDING FOR OVERHEARD</p></sync>
        </Body>
        </SAMI>
        """

        self.sample_sami_with_lang = u"""
        <sami>
        <head>
        <style type="text/css"><!--.en-US {lang: en-US;}--></style>
        </head>
        <body>
        <sync start="1301"><p class="en-US">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
        </body>
        </sami>
        """

    def test_sami_to_sami_conversion(self):
        captions = SAMIReader().read(self.sample_sami)
        results = SAMIWriter().write(captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(self.sample_sami_with_lang, results)
        self.assertTrue(u"lang: en-US;" in results)
