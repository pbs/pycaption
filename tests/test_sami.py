import unittest

from pycaption import SAMIReader, CaptionReadNoCaptions

from .samples import SAMPLE_SAMI, SAMPLE_SAMI_EMPTY


class SAMIReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SAMIReader().detect(SAMPLE_SAMI))

    def test_caption_length(self):
        captions = SAMIReader().read(SAMPLE_SAMI)

        self.assertEquals(7, len(captions.get_captions("en-US")))

    def test_proper_timestamps(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        paragraph = captions.get_captions("en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)

    def test_6digit_color_code_from_6digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        p_style = captions.get_style("p")

        self.assertEquals("#ffeedd", p_style['color'])

    def test_6digit_color_code_from_3digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI.replace("#ffeedd", "#fed"))
        p_style = captions.get_style("p")

        self.assertEquals("#ffeedd", p_style['color'])

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SAMIReader().read, SAMPLE_SAMI_EMPTY)
