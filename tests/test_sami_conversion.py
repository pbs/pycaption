import unittest

from builtins import str
import six

from pycaption import (
    SAMIReader, SAMIWriter, SRTWriter, DFXPWriter, WebVTTWriter, MicroDVDWriter, MicroDVDWriter)

from .samples.dfxp import (
    DFXP_FROM_SAMI_WITH_POSITIONING, SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS,
    SAMPLE_DFXP_FROM_SAMI_WITH_LANG_MARGINS, SAMPLE_DFXP_FROM_SAMI_WITH_SPAN,
    SAMPLE_DFXP_FROM_SAMI_WITH_BAD_SPAN_ALIGN
)
from .samples.sami import (
    SAMPLE_SAMI, SAMPLE_SAMI_WITH_STYLE_TAGS, SAMPLE_SAMI_WITH_CSS_INLINE_STYLE,
    SAMPLE_SAMI_WITH_CSS_ID_STYLE, SAMPLE_SAMI_SYNTAX_ERROR,
    SAMPLE_SAMI_PARTIAL_MARGINS, SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED,
    SAMPLE_SAMI_LANG_MARGIN, SAMPLE_SAMI_WITH_SPAN, SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN,
    SAMPLE_SAMI_WITH_MULTIPLE_SPAN_ALIGNS, SAMPLE_SAMI_NO_LANG,
    SAMPLE_SAMI_WITH_LANG
)
from .samples.srt import SAMPLE_SRT
from .samples.webvtt import (
    SAMPLE_WEBVTT_FROM_SAMI, SAMPLE_WEBVTT_FROM_SAMI_WITH_STYLE,
    SAMPLE_WEBVTT_FROM_SAMI_WITH_ID_STYLE
)

from .samples.microdvd import SAMPLE_MICRODVD_2

from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn, MicroDVDTestingMixIn

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class SAMItoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI)
        results = SAMIWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_is_relativized(self):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = SAMIReader().read(SAMPLE_SAMI_PARTIAL_MARGINS)
        result = SAMIWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)
        self.assertSAMIEquals(result, SAMPLE_SAMI_PARTIAL_MARGINS_RELATIVIZED)


class SAMItoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSRTEquals(SAMPLE_SRT, results)


class SAMItoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_sami_to_dfxp_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertDFXPEquals(
            DFXP_FROM_SAMI_WITH_POSITIONING,
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
        captions = SAMIReader().read(SAMPLE_SAMI_SYNTAX_ERROR)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(captions)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertTrue('xmlns="http://www.w3.org/ns/ttml"' in results)
        self.assertTrue(
            'xmlns:tts="http://www.w3.org/ns/ttml#styling"' in results)


class SAMItoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_sami_to_webvtt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI, results)

    def test_sami_with_style_tags_to_webvtt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_STYLE_TAGS)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI_WITH_STYLE, results)

    def test_sami_with_css_inline_style_to_webvtt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_CSS_INLINE_STYLE)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI_WITH_STYLE, results)

    def test_sami_with_css_id_style_to_webvtt_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_CSS_ID_STYLE)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SAMI_WITH_ID_STYLE, results)


class SAMItoMicroDVDTestCase(unittest.TestCase, MicroDVDTestingMixIn):

    def test_sami_to_micro_dvd_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI)
        results = MicroDVDWriter().write(caption_set)

        self.assertTrue(isinstance(results, six.text_type))
        self.assertMicroDVDEquals(SAMPLE_MICRODVD_2, results)


class SAMIWithMissingLanguage(unittest.TestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_NO_LANG)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSAMIEquals(SAMPLE_SAMI_WITH_LANG, results)
        self.assertTrue("lang: und;" in results)
