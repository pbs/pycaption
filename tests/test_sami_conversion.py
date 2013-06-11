import unittest

from pycaption import SAMIReader, SRTWriter, DFXPWriter

from .samples import SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP
from .mixins import SRTTestingMixIn, XMLTestingMixIn


class SAMIConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI)


class SAMItoSRTTestCase(SAMIConversionTestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)


class SAMItoDFXPTestCase(SAMIConversionTestCase, XMLTestingMixIn):

    def test_sami_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertXMLEquals(SAMPLE_DFXP, results)
