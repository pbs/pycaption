import unittest

from builtins import str
import six

from pycaption import (
    WebVTTReader, WebVTTWriter, SRTWriter, SAMIWriter, DFXPWriter)

from tests.samples.dfxp import SAMPLE_DFXP
from tests.samples.sami import SAMPLE_SAMI
from tests.samples.srt import SAMPLE_SRT
from tests.samples.webvtt import (
    SAMPLE_WEBVTT, SAMPLE_WEBVTT_FROM_WEBVTT,
    SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING, SAMPLE_WEBVTT_WITH_CUE_SETTINGS
)
from tests.mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, SRTTestingMixIn
)


class WebVTTtoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_webvtt_to_webvtt_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_WEBVTT, results)

    def test_cue_settings_are_kept(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT_WITH_CUE_SETTINGS)

        webvtt = WebVTTWriter().write(caption_set)

        self.assertEqual(SAMPLE_WEBVTT_WITH_CUE_SETTINGS, webvtt)

    def test_positioning_is_kept(self):
        caption_set = WebVTTReader().read(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING)
        results = WebVTTWriter().write(caption_set)
        self.assertEqual(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING, results)

#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class WebVTTtoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_webvtt_to_sami_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSAMIEquals(SAMPLE_SAMI, results)


class WebVTTtoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_webvtt_to_dfxp_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertDFXPEquals(
            SAMPLE_DFXP, results, ignore_styling=True, ignore_spans=True
        )


class WebVTTtoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_webvtt_to_srt_conversion(self):
        caption_set = WebVTTReader().read(SAMPLE_WEBVTT)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertSRTEquals(SAMPLE_SRT, results)
