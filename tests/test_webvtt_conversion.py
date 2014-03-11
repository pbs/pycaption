import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SRTWriter, SAMIWriter, DFXPWriter)

from .samples import (
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8, SAMPLE_WEBVTT
)
from .mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, SRTTestingMixIn
)


class WebVTTConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = WebVTTReader().read(SAMPLE_WEBVTT)


class WebVTTtoWebVTTTestCase(WebVTTConversionTestCase, WebVTTTestingMixIn):

    def test_webvtt_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions)
        self.assertWebVTTEquals(SAMPLE_WEBVTT, results)

    # TODO: Write a test that includes a WebVTT file with style tags
    # That will fail because the styles used in the cues are not tracked.


class WebVTTtoSAMITestCase(WebVTTConversionTestCase, SAMITestingMixIn):

    def test_webvtt_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI_UTF8, results)


class WebVTTtoDFXPTestCase(WebVTTConversionTestCase, DFXPTestingMixIn):

    def test_webvtt_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(
            SAMPLE_DFXP_UTF8, results, ignore_styling=True, ignore_spans=True
        )


class WebVTTtoSRTTestCase(WebVTTConversionTestCase, SRTTestingMixIn):

    def test_webvtt_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)
