import unittest

from pycaption import SRTReader, SRTWriter, SAMIWriter, DFXPWriter

from .samples import SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn


class SRTConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SRTReader().read(SAMPLE_SRT)


class SRTtoSRTTestCase(SRTConversionTestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)


class SRTtoSAMITestCase(SRTConversionTestCase, SAMITestingMixIn):

    def test_srt_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)


class SRTtoDFXPTestCase(SRTConversionTestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(
            SAMPLE_DFXP,
            results,
            ignore_styling=True,
            ignore_spans=True)
