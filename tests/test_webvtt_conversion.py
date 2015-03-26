import unittest

from pycaption import (
    WebVTTReader, WebVTTWriter, SRTWriter, SAMIWriter, DFXPWriter)

from .samples import (
    SAMPLE_WEBVTT, SAMPLE_DFXP_UNICODE, SAMPLE_SRT_UNICODE, SAMPLE_SAMI_UNICODE
)
from .mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, SRTTestingMixIn
)
from tests.samples import SAMPLE_WEBVTT_FROM_WEBVTT


class WebVTTConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = WebVTTReader().read(SAMPLE_WEBVTT.decode(u'utf-8'))


class WebVTTtoWebVTTTestCase(WebVTTConversionTestCase, WebVTTTestingMixIn):

    def test_webvtt_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_WEBVTT.decode(u'utf-8'), results)

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
