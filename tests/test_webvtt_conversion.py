import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SRTWriter, SAMIWriter, DFXPWriter)

from .samples.dfxp import SAMPLE_DFXP
from .samples.sami import SAMPLE_SAMI
from .samples.srt import SAMPLE_SRT
from .samples.webvtt import (
    SAMPLE_WEBVTT, SAMPLE_WEBVTT_FROM_WEBVTT,
    SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING, SAMPLE_WEBVTT_WITH_CUE_SETTINGS,
    SAMPLE_WEBVTT_EMPTY_CUE, SAMPLE_WEBVTT_FROM_EMPTY_CUE,
)
from .mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, SRTTestingMixIn
)


class WebVTTtoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_webvtt_to_webvtt_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_WEBVTT, results)

    def test_cue_settings_are_kept(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT_WITH_CUE_SETTINGS)

        webvtt = WebVTTWriter().write(caption_set)

        self.assertEqual(SAMPLE_WEBVTT_WITH_CUE_SETTINGS, webvtt)

    def test_positioning_is_kept(self):
        caption_set = WebVTTReader().read(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING)
        results = WebVTTWriter().write(caption_set)
        self.assertEquals(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING, results)

    def test_empty_cues_are_deleted(self):
        caption_set = WebVTTReader().read(
            SAMPLE_WEBVTT_EMPTY_CUE)
        results = WebVTTWriter().write(caption_set)
        self.assertEquals(
            SAMPLE_WEBVTT_FROM_EMPTY_CUE, results)

#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class WebVTTtoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_webvtt_to_sami_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI, results)


class WebVTTtoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_webvtt_to_dfxp_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP, results, ignore_styling=True, ignore_spans=True
        )


class WebVTTtoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_webvtt_to_srt_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT, results)
