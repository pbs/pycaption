import unittest

from pycaption import (
    SRTReader, SRTWriter, SAMIWriter, DFXPWriter, WebVTTWriter)

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SRT_UTF8, SAMPLE_SAMI_UNICODE, SAMPLE_SRT_UNICODE,
    SAMPLE_DFXP_UNICODE, SAMPLE_WEBVTT
)
from .mixins import (
    SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn)


class SRTConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = SRTReader().read(SAMPLE_SRT.decode(u'utf-8'))
        cls.captions_utf8 = SRTReader().read(SAMPLE_SRT_UTF8.decode(u'utf-8'))
        cls.captions_unicode = SRTReader().read(SAMPLE_SRT_UNICODE)


class SRTtoSRTTestCase(SRTConversionTestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT.decode(u'utf-8'), results)

    def test_srt_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

    def test_srt_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)


class SRTtoSAMITestCase(SRTConversionTestCase, SAMITestingMixIn):

    def test_srt_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI.decode(u'utf-8'), results)

    def test_srt_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_srt_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class SRTtoDFXPTestCase(SRTConversionTestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP.decode(u'utf-8'), results, ignore_styling=True, ignore_spans=True
        )

    def test_srt_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP_UNICODE, results, ignore_styling=True, ignore_spans=True
        )

    def test_srt_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP_UNICODE, results,
            ignore_styling=True, ignore_spans=True
        )


class SRTtoWebVTTTestCase(SRTConversionTestCase, WebVTTTestingMixIn):

    def test_srt_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode(u'utf-8'), results)

    def test_srt_to_webvtt_unicode_conversion(self):
        results = WebVTTWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode(u'utf-8'), results)
