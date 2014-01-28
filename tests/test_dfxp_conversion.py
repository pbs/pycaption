import unittest

from pycaption import DFXPReader, DFXPWriter, SRTWriter, SAMIWriter

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8,
    SAMPLE_SAMI_UNICODE, SAMPLE_SRT_UNICODE, SAMPLE_DFXP_UNICODE
)
from .mixins import SRTTestingMixIn, SAMITestingMixIn, DFXPTestingMixIn


class DFXPConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = DFXPReader().read(SAMPLE_DFXP)
        self.captions_utf8 = DFXPReader().read(SAMPLE_DFXP_UTF8)
        self.captions_unicode = DFXPReader().read(SAMPLE_DFXP_UNICODE)


class DFXPtoDFXPTestCase(DFXPConversionTestCase, DFXPTestingMixIn):

    def test_dfxp_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(SAMPLE_DFXP, results)

    def test_dfxp_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertDFXPEquals(SAMPLE_DFXP_UTF8, results)

    def test_dfxp_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)


class DFXPtoSRTTestCase(DFXPConversionTestCase, SRTTestingMixIn):

    def test_dfxp_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)

    def test_dfxp_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)

    def test_dfxp_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)


class DFXPtoSAMITestCase(DFXPConversionTestCase, SAMITestingMixIn):

    def test_dfxp_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_dfxp_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertSAMIEquals(SAMPLE_SAMI_UTF8, results)

    def test_dfxp_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)
