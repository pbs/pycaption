import unittest

from pycaption import (
    SRTReader, SRTWriter, SAMIWriter, DFXPWriter, WebVTTWriter)

from .samples.dfxp import SAMPLE_DFXP
from .samples.srt import SAMPLE_SRT
from .samples.sami import SAMPLE_SAMI
from .samples.webvtt import SAMPLE_WEBVTT_FROM_SRT

from .mixins import (
    SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn)


class SRTConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions_unicode = SRTReader().read(SAMPLE_SRT)


class SRTtoSRTTestCase(SRTConversionTestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT, results)


class SRTtoSAMITestCase(SRTConversionTestCase, SAMITestingMixIn):

    def test_srt_to_sami_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI, results)


class SRTtoDFXPTestCase(SRTConversionTestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP, results,
            ignore_styling=True, ignore_spans=True
        )


class SRTtoWebVTTTestCase(SRTConversionTestCase, WebVTTTestingMixIn):

    def test_srt_to_webvtt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SRT, results)
