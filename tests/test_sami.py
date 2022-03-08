from copy import deepcopy

import pytest

from pycaption import SAMIReader, CaptionReadNoCaptions, CaptionReadSyntaxError
from pycaption.exceptions import CaptionReadTimingError
from pycaption.geometry import HorizontalAlignmentEnum, Size, UnitEnum  # noqa
from tests.mixins import ReaderTestingMixIn


class TestSAMIReader(ReaderTestingMixIn):
    def setup_method(self):
        self.reader = SAMIReader()

    def test_positive_answer_for_detection(self, sample_sami):
        super().assert_positive_answer_for_detection(sample_sami)

    @pytest.mark.parametrize('different_sample', [
        pytest.lazy_fixture('sample_dfxp'),
        pytest.lazy_fixture('sample_microdvd'),
        pytest.lazy_fixture('sample_scc_pop_on'),
        pytest.lazy_fixture('sample_srt'),
        pytest.lazy_fixture('sample_webvtt')
    ])
    def test_negative_answer_for_detection(self, different_sample):
        super().assert_negative_answer_for_detection(different_sample)

    def test_caption_length(self, sample_sami):
        caption_set = self.reader.read(sample_sami)

        assert 7 == len(caption_set.get_captions("en-US"))

    def test_proper_timestamps(self, sample_sami):
        caption_set = self.reader.read(sample_sami)
        paragraph = caption_set.get_captions("en-US")[2]

        assert 17000000 == paragraph.start
        assert 18752000 == paragraph.end

    def test_missing_start(self, sample_sami_missing_start):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            self.reader.read(sample_sami_missing_start)

        assert exc_info.value.args[0].startswith(
            "Missing start time on the following line: ")

    def test_6digit_color_code_from_6digit_input(self, sample_sami):
        caption_set = self.reader.read(sample_sami)
        p_style = caption_set.get_style("p")

        assert "#ffeedd" == p_style['color']

    def test_6digit_color_code_from_3digit_input(self, sample_sami):
        sample_sami = deepcopy(sample_sami)
        caption_set = self.reader.read(sample_sami.replace("#ffeedd", "#fed"))
        p_style = caption_set.get_style("p")

        assert "#ffeedd" == p_style['color']

    def test_invalid_color_code(self, sample_sami):
        with pytest.raises(CaptionReadSyntaxError) as exc_info:
            self.reader.read(sample_sami.replace("#ffeedd", "ffffff"))
        assert exc_info.value.args[0] == \
               "Invalid color value: ffffff. Check for missing # before hex " \
               "values or misspelled color values."

    def test_empty_file(self, sample_sami_empty):
        with pytest.raises(CaptionReadNoCaptions):
            self.reader.read(sample_sami_empty)

    def test_invalid_markup_is_properly_handled(self, sample_sami_syntax_error):
        caption_set = self.reader.read(sample_sami_syntax_error)

        assert 2 == len(caption_set.get_captions("en-US"))

    def test_partial_margins(self, sample_sami_partial_margins):
        caption_set = self.reader.read(sample_sami_partial_margins)
        # Ensure that undefined margins are converted to explicitly nil padding
        # (i.e. "0%")

        assert caption_set.layout_info.padding.to_xml_attribute() == \
               '0% 29pt 0% 29pt'

    def test_sami_with_bad_span_align(self, sample_sami_with_bad_span_align):
        caption_set = self.reader.read(sample_sami_with_bad_span_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_bad_div_align(self, sample_sami_with_bad_div_align):
        caption_set = self.reader.read(sample_sami_with_bad_div_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_p_align(self, sample_sami_with_p_align):
        caption_set = self.reader.read(sample_sami_with_p_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_p_and_span_align(self,
                                        sample_sami_with_p_and_span_align):
        """<span> align DOES NOT override <p> align if it is specified inline.
        """
        caption_set = self.reader.read(sample_sami_with_p_and_span_align)
        caption = caption_set.get_captions('en-US')[0]

        assert caption.layout_info.alignment.horizontal == \
               HorizontalAlignmentEnum.RIGHT

    def test_sami_with_invalid_inline_style(
            self, sample_sami_with_invalid_inline_style):
        caption_set = self.reader.read(sample_sami_with_invalid_inline_style)
        caption = caption_set.get_captions("en-US")[0]

        assert caption.layout_info.alignment is None

    def test_sami_including_hexadecimal_charref(
            self, sample_sami_including_hexadecimal_charref):
        caption_set = self.reader.read(
            sample_sami_including_hexadecimal_charref)
        paragraph = caption_set.get_captions("en-US")[0]

        assert '> >' == paragraph.get_text()

    def test_sami_including_decimal_charref(
            self, sample_sami_including_decimal_charref):
        caption_set = self.reader.read(sample_sami_including_decimal_charref)
        paragraph = caption_set.get_captions("en-US")[0]

        assert '> >' == paragraph.get_text()

    def test_sami_including_html5_entityref(
            self, sample_sami_including_html5_entityref):
        caption_set = self.reader.read(sample_sami_including_html5_entityref)
        paragraph = caption_set.get_captions("en-US")[0]

        assert '&starf_&starf' == paragraph.get_text()

    def test_html_file(self):
        with pytest.raises(CaptionReadSyntaxError) as exc_info:
            self.reader.read("<html><head></head><body></body></html>")
        assert exc_info.value.args[0] == 'SAMI File seems to be an HTML file.'

    def test_no_cc_available(self):
        no_cc = 'no closed captioning available'
        with pytest.raises(CaptionReadSyntaxError) as exc_info:
            self.reader.read(f"<SAMI>{no_cc}</SAMI>")
        assert exc_info.value.args[0] == f'SAMI File contains "{no_cc}"'

    def test_sami_with_unclosed_tag(self, sample_sami_with_unclosed_tag):
        caption_set = self.reader.read(sample_sami_with_unclosed_tag)
        paragraph = caption_set.get_captions("en-US")[0]

        assert '.' == paragraph.get_text()

    def test_sami_with_inline_lang(self, sample_sami_with_inline_lang):
        caption_set = self.reader.read(sample_sami_with_inline_lang)
        paragraph = caption_set.get_captions("en")[0]

        assert 'Inlined.' == paragraph.get_text()

    def test_proper_with_timestamps_with_multiple_paragraph(
            self, sample_sami_with_multiple_p):
        captions = self.reader.read(sample_sami_with_multiple_p)
        paragraph_1 = captions.get_captions("en-US")[0]
        paragraph_2 = captions.get_captions("en-US")[1]

        assert paragraph_1.start == paragraph_2.start
        assert paragraph_1.end == paragraph_2.end
