import unittest

from pycaption import SAMIReader, CaptionReadNoCaptions

from .samples import (
    SAMPLE_SAMI, SAMPLE_SAMI_EMPTY, SAMPLE_SAMI_SYNTAX_ERROR,
    SAMPLE_SAMI_PARTIAL_MARGINS
)

class SAMIReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SAMIReader().detect(SAMPLE_SAMI.decode(u'utf-8')))

    def test_caption_length(self):
        captions = SAMIReader().read(SAMPLE_SAMI.decode(u'utf-8'))

        self.assertEquals(8, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SAMIReader().read(SAMPLE_SAMI.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)

    def test_6digit_color_code_from_6digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI.decode(u'utf-8'))
        p_style = captions.get_style(u"p")

        self.assertEquals(u"#ffeedd", p_style[u'color'])

    def test_6digit_color_code_from_3digit_input(self):
        captions = SAMIReader().read(
            SAMPLE_SAMI.decode(u'utf-8').replace(u"#ffeedd", u"#fed"))
        p_style = captions.get_style(u"p")

        self.assertEquals(u"#ffeedd", p_style[u'color'])

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SAMIReader().read, SAMPLE_SAMI_EMPTY.decode(u'utf-8'))

    def test_invalid_markup_is_properly_handled(self):
        captions = SAMIReader().read(SAMPLE_SAMI_SYNTAX_ERROR.decode(u'utf-8'))
        self.assertEquals(2, len(captions.get_captions(u"en-US")))

    def test_partial_margins(self):
        captions = SAMIReader().read(SAMPLE_SAMI_PARTIAL_MARGINS)
        # Ensure that undefined margins are converted to explicitly nil padding
        # (i.e. "0%")
        self.assertEquals(
            captions.get_layout_info('en-US').padding.to_xml_attribute(),
            u'0% 29pt 0% 29pt'
        )
