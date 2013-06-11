import unittest

from pycaption import DFXPReader, DFXPWriter, SRTWriter, SAMIWriter

from .samples import SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP
from .mixins import SRTTestingMixIn, SAMITestingMixIn, XMLTestingMixIn


class DFXPConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = DFXPReader().read(SAMPLE_DFXP)


class DFXPWriterTestCase(DFXPConversionTestCase, XMLTestingMixIn):

    def test_write(self):
        results = DFXPWriter().write(self.captions)
        self.assertXMLEquals(SAMPLE_DFXP, results)


class DFXPtoSRTTestCase(DFXPConversionTestCase, SRTTestingMixIn):

    def test_dfxp_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)


class DFXPtoSAMITestCase(DFXPConversionTestCase, SAMITestingMixIn):

    def test_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)
