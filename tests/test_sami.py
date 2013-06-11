import unittest

from bs4 import BeautifulSoup

from pycaption import SAMIReader, SAMIWriter

from .samples import SAMPLE_SAMI


class SAMIReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SAMIReader().detect(SAMPLE_SAMI))

    def test_proper_pcc_format(self):
        captions = SAMIReader().read(SAMPLE_SAMI)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(7, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        paragraph = captions["captions"]["en-US"][2]

        self.assertEquals(17000000, paragraph[0])
        self.assertEquals(18752000, paragraph[1])

    def test_6digit_color_code_from_6digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        p_style = captions["styles"]["p"]

        self.assertEquals("#ffeedd", p_style['color'])

    def test_6digit_color_code_from_3digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI.replace("#ffeedd", "#fed"))
        p_style = captions["styles"]["p"]

        self.assertEquals("#ffeedd", p_style['color'])


class SAMIWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI)

    def assertSAMIEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)

        first_items = _extract_sami_captions(first_soup)
        second_items = _extract_sami_captions(second_soup)
        self.assertEquals(first_items, second_items)

    def test_write(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)


def _extract_sami_captions(soup):
    return tuple(
        (caption.attrs['start'], _normalize_caption_text(caption.p.text))
        for caption in soup.select('sync'))


def _normalize_caption_text(value):
    return value.strip().replace(' ', '')
