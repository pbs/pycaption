import unittest

from pycaption import SRTReader, SRTWriter, SAMIWriter, DFXPWriter

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8,
    SAMPLE_SAMI_UNICODE, SAMPLE_SRT_UNICODE, SAMPLE_DFXP_UNICODE
)
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn


class SRTConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SRTReader().read(SAMPLE_SRT)
        self.captions_utf8 = SRTReader().read(SAMPLE_SRT_UTF8)
        self.captions_unicode = SRTReader().read(SAMPLE_SRT_UNICODE)


class SRTtoSRTTestCase(SRTConversionTestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)

    def test_srt_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)

    def test_srt_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)


class SRTtoSAMITestCase(SRTConversionTestCase, SAMITestingMixIn):

    def test_srt_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_srt_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertSAMIEquals(SAMPLE_SAMI_UTF8, results)

    def test_srt_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class SRTtoDFXPTestCase(SRTConversionTestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(
            SAMPLE_DFXP, results, ignore_styling=True, ignore_spans=True
        )

    def test_srt_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertDFXPEquals(
            SAMPLE_DFXP_UTF8, results, ignore_styling=True, ignore_spans=True
        )

    def test_srt_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertDFXPEquals(
            SAMPLE_DFXP_UNICODE, results,
            ignore_styling=True, ignore_spans=True
        )
