import unittest

from pycaption import DFXPReader

from .samples import SAMPLE_DFXP


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_proper_pcc_format(self):
        captions = DFXPReader().read(SAMPLE_DFXP)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(7, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions["captions"]["en-US"][2]

        self.assertEquals(17000000, paragraph[0])
        self.assertEquals(18752000, paragraph[1])
