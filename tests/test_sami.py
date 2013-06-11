import unittest

from pycaption import SAMIReader

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
