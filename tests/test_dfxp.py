import unittest

from pycaption import DFXPReader

from .samples import SAMPLE_DFXP


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP)

        self.assertEquals(7, len(captions.get_captions("en-US")))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions.get_captions("en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)
