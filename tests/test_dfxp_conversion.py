import unittest

from pycaption import (
    DFXPReader, DFXPWriter, SRTWriter, SAMIWriter, WebVTTWriter)

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8,
    SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE, SAMPLE_WEBVTT,
    SAMPLE_SRT_UNICODE)
from .mixins import SRTTestingMixIn, SAMITestingMixIn, DFXPTestingMixIn, WebVTTTestingMixIn


class DFXPConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = DFXPReader().read(SAMPLE_DFXP.decode('utf-8'))
        cls.captions_utf8 = DFXPReader().read(SAMPLE_DFXP_UTF8.decode('utf-8'))
        cls.captions_unicode = DFXPReader().read(SAMPLE_DFXP_UNICODE)


class DFXPtoDFXPTestCase(DFXPConversionTestCase, DFXPTestingMixIn):

    def test_dfxp_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP.decode('utf-8'), results)

    def test_dfxp_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)

    def test_dfxp_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)


class DFXPtoSRTTestCase(DFXPConversionTestCase, SRTTestingMixIn):

    def test_dfxp_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT.decode('utf-8'), results)

    def test_dfxp_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

    def test_dfxp_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)


class DFXPtoSAMITestCase(DFXPConversionTestCase, SAMITestingMixIn):

    def test_dfxp_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI.decode('utf-8'), results)

    def test_dfxp_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_dfxp_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class DFXPtoWebVTTTestCase(DFXPConversionTestCase, WebVTTTestingMixIn):

    def test_dfxp_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode('utf-8'), results)

    def test_dfxp_to_webvtt_unicode_conversion(self):
        results = WebVTTWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode('utf-8'), results)
