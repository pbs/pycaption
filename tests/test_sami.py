from copy import deepcopy

import pytest

from pycaption import SAMIReader, CaptionReadNoCaptions
from pycaption.geometry import HorizontalAlignmentEnum, Size, UnitEnum  # noqa


class TestSAMIReader:
    def test_detection(self, sample_sami):
        assert SAMIReader().detect(sample_sami) is True

    def test_caption_length(self, sample_sami):
        captions = SAMIReader().read(sample_sami)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_sami):
        captions = SAMIReader().read(sample_sami)
        paragraph = captions.get_captions("en-US")[2]

        assert 17000000 == paragraph.start
        assert 18752000 == paragraph.end

    def test_6digit_color_code_from_6digit_input(self, sample_sami):
        captions = SAMIReader().read(sample_sami)
        p_style = captions.get_style("p")

        assert "#ffeedd" == p_style['color']

    def test_6digit_color_code_from_3digit_input(self, sample_sami):
        sample_sami = deepcopy(sample_sami)
        captions = SAMIReader().read(sample_sami.replace("#ffeedd", "#fed"))
        p_style = captions.get_style("p")

        assert "#ffeedd" == p_style['color']

    def test_empty_file(self, sample_sami_empty):
        with pytest.raises(CaptionReadNoCaptions):
            SAMIReader().read(sample_sami_empty)

    def test_invalid_markup_is_properly_handled(self, sample_sami_syntax_error):
        captions = SAMIReader().read(sample_sami_syntax_error)

        assert 2 == len(captions.get_captions("en-US"))

    def test_partial_margins(self, sample_sami_partial_margins):
        caption_set = SAMIReader().read(sample_sami_partial_margins)
        # Ensure that undefined margins are converted to explicitly nil padding
        # (i.e. "0%")

        assert caption_set.layout_info.padding.to_xml_attribute() == \
               '0% 29pt 0% 29pt'

    def test_sami_with_bad_span_align(self, sample_sami_with_bad_span_align):
        caption_set = SAMIReader().read(sample_sami_with_bad_span_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_bad_div_align(self, sample_sami_with_bad_div_align):
        caption_set = SAMIReader().read(sample_sami_with_bad_div_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_p_align(self, sample_sami_with_p_align):
        caption_set = SAMIReader().read(sample_sami_with_p_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_p_and_span_align(self,
                                        sample_sami_with_p_and_span_align):
        """<span> align DOES NOT override <p> align if it is specified inline.
        """
        caption_set = SAMIReader().read(sample_sami_with_p_and_span_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_proper_with_timestamps_with_multiple_paragraph(
            self, sample_sami_with_multiple_p):
        captions = SAMIReader().read(sample_sami_with_multiple_p)
        paragraph_1 = captions.get_captions("en-US")[0]
        paragraph_2 = captions.get_captions("en-US")[1]

        assert paragraph_1.start == paragraph_2.start
        assert paragraph_1.end == paragraph_2.end
