import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SRTWriter, SAMIWriter, DFXPWriter)

from .samples import (
    SAMPLE_WEBVTT, SAMPLE_DFXP_UNICODE, SAMPLE_SRT_UNICODE, SAMPLE_SAMI_UNICODE,
    SAMPLE_WEBVTT_FROM_WEBVTT, SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING
)
from .mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, SRTTestingMixIn
)


class WebVTTConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = WebVTTReader().read(SAMPLE_WEBVTT.decode(u'utf-8'))


class WebVTTtoWebVTTTestCase(WebVTTConversionTestCase, WebVTTTestingMixIn):

    def test_webvtt_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_WEBVTT.decode(u'utf-8'), results)

    def test_cues_are_kept(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT_WITH_SETTINGS_CUE)

        webvtt = WebVTTWriter().write(caption_set)

        self.assertEqual(SAMPLE_WEBVTT_WITH_SETTINGS_CUE, webvtt)

    def test_positioning_is_kept(self):
        caption_set = WebVTTReader().read(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING.decode(u'utf-8'))
        results = WebVTTWriter().write(caption_set)
        self.assertEquals(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING.decode(u'utf-8'), results)

#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class WebVTTtoSAMITestCase(WebVTTConversionTestCase, SAMITestingMixIn):

    def test_webvtt_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class WebVTTtoDFXPTestCase(WebVTTConversionTestCase, DFXPTestingMixIn):

    def test_webvtt_to_dfxp_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT.decode(u'utf-8'))
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP_UNICODE, results, ignore_styling=True, ignore_spans=True
        )


class WebVTTtoSRTTestCase(WebVTTConversionTestCase, SRTTestingMixIn):

    def test_webvtt_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

SAMPLE_WEBVTT_WITH_SETTINGS_CUE = u"""\
WEBVTT

00:01.000 --> 00:06.000 align:middle position:37%,start line:74%
37% 74% - NARRATOR:

00:01.000 --> 00:06.000 this is invalid, but will also be kept
They built the largest,
"""