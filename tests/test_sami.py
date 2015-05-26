import unittest

from pycaption import SAMIReader, CaptionReadNoCaptions

from .samples.sami import (
    SAMPLE_SAMI, SAMPLE_SAMI_EMPTY, SAMPLE_SAMI_SYNTAX_ERROR,
    SAMPLE_SAMI_PARTIAL_MARGINS, SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN,
    SAMPLE_SAMI_WITH_BAD_DIV_ALIGN, SAMPLE_SAMI_WITH_P_ALIGN,
    SAMPLE_SAMI_WITH_P_AND_SPAN_ALIGN
)

class SAMIReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SAMIReader().detect(SAMPLE_SAMI))

    def test_caption_length(self):
        captions = SAMIReader().read(SAMPLE_SAMI)

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        paragraph = captions.get_captions(u"en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)

    def test_6digit_color_code_from_6digit_input(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        p_style = captions.get_style(u"p")

        self.assertEquals(u"#ffeedd", p_style[u'color'])

    def test_6digit_color_code_from_3digit_input(self):
        captions = SAMIReader().read(
            SAMPLE_SAMI.replace(u"#ffeedd", u"#fed"))
        p_style = captions.get_style(u"p")

        self.assertEquals(u"#ffeedd", p_style[u'color'])

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SAMIReader().read, SAMPLE_SAMI_EMPTY)

    def test_invalid_markup_is_properly_handled(self):
        captions = SAMIReader().read(SAMPLE_SAMI_SYNTAX_ERROR)
        self.assertEquals(2, len(captions.get_captions(u"en-US")))

    def test_partial_margins(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_PARTIAL_MARGINS)
        # Ensure that undefined margins are converted to explicitly nil padding
        # (i.e. "0%")
        self.assertEquals(
            caption_set.layout_info.padding.to_xml_attribute(),
            u'0% 29pt 0% 29pt'
        )

    def test_sami_with_bad_span_align(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_BAD_SPAN_ALIGN)
        caption = caption_set.get_captions('en-US')[0]
        self.assertEquals(caption.layout_info.alignment.horizontal, u'right')

    def test_sami_with_bad_div_align(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_BAD_DIV_ALIGN)
        caption = caption_set.get_captions('en-US')[0]
        self.assertEquals(caption.layout_info.alignment.horizontal, u'right')

    def test_sami_with_p_align(self):
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_P_ALIGN)
        caption = caption_set.get_captions('en-US')[0]
        self.assertEquals(caption.layout_info.alignment.horizontal, u'right')

    def test_sami_with_p_and_span_align(self):
        """ <span> align DOES NOT override <p> align if it is specified inline.
        """
        caption_set = SAMIReader().read(SAMPLE_SAMI_WITH_P_AND_SPAN_ALIGN)
        caption = caption_set.get_captions('en-US')[0]
        self.assertEquals(caption.layout_info.alignment.horizontal, u'right')
