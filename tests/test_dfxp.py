import unittest

from bs4 import BeautifulSoup

from pycaption import DFXPReader, DFXPWriter

from .samples import SAMPLE_DFXP


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_proper_pcc_format(self):
        captions = DFXPReader().read(SAMPLE_DFXP)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(4, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions["captions"]["en-US"][2]

        self.assertEquals(9909000, paragraph[0])
        self.assertEquals(11578000, paragraph[1])


class DFXPWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = DFXPReader().read(SAMPLE_DFXP)

    def assertXMLEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)
        self.assertEquals(first_soup, second_soup)

    def test_write(self):
        results = DFXPWriter().write(self.captions)
        self.assertXMLEquals(SAMPLE_DFXP, results)
