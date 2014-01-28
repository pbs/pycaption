import unittest

from pycaption import SAMIReader, SAMIWriter, SRTWriter, DFXPWriter

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8
)
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn


class SAMIConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI)
        self.captions_utf8 = SAMIReader().read(SAMPLE_SAMI_UTF8)


class SAMItoSAMITestCase(SAMIConversionTestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_sami_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertSAMIEquals(SAMPLE_SAMI_UTF8, results)


class SAMItoSRTTestCase(SAMIConversionTestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)

    def test_sami_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)


class SAMItoDFXPTestCase(SAMIConversionTestCase, DFXPTestingMixIn):

    def test_sami_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(SAMPLE_DFXP, results)

    def test_sami_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertDFXPEquals(SAMPLE_DFXP_UTF8, results)
