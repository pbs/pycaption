import pytest

from pycaption import DFXPReader, CaptionReadNoCaptions
from pycaption.exceptions import (
    CaptionReadSyntaxError, InvalidInputError, CaptionReadError,
)
from pycaption.geometry import (
    UnitEnum, HorizontalAlignmentEnum, VerticalAlignmentEnum,
)
from tests.mixins import ReaderTestingMixIn


class TestDFXPReader(ReaderTestingMixIn):
    def setup_class(self):
        self.reader = DFXPReader()

    def test_positive_answer_for_detection(self, sample_dfxp):
        super().assert_positive_answer_for_detection(sample_dfxp)

    @pytest.mark.parametrize('different_sample', [
        pytest.lazy_fixture('sample_microdvd'),
        pytest.lazy_fixture('sample_sami'),
        pytest.lazy_fixture('sample_scc_pop_on'),
        pytest.lazy_fixture('sample_srt'),
        pytest.lazy_fixture('sample_webvtt')
    ])
    def test_negative_answer_for_detection(self, different_sample):
        super().assert_negative_answer_for_detection(different_sample)

    def test_caption_length(self, sample_dfxp):
        captions = DFXPReader().read(sample_dfxp)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_dfxp):
        captions = DFXPReader().read(sample_dfxp)
        paragraph = captions.get_captions("en-US")[2]

        assert 17000000 == paragraph.start
        assert 18752000 == paragraph.end

    def test_incorrect_time_format(self, sample_dfxp_incorrect_time_format):
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(sample_dfxp_incorrect_time_format)

    def test_offset_time(self):
        reader = DFXPReader()

        assert 1 == reader._translate_time("0.001ms")
        assert 2000 == reader._translate_time("2ms")
        assert 1000000 == reader._translate_time("1s")
        assert 1234567 == reader._translate_time("1.234567s")
        assert 180000000 == reader._translate_time("3m")
        assert 14400000000 == reader._translate_time("4h")
        # Tick values are not supported
        with pytest.raises(InvalidInputError):
            reader._translate_time("2.3t")

    def test_empty_file(self, sample_dfxp_empty):
        with pytest.raises(CaptionReadNoCaptions):
            DFXPReader().read(sample_dfxp_empty)

    def test_invalid_markup_is_properly_handled(self, sample_dfxp_syntax_error):
        captions = DFXPReader().read(sample_dfxp_syntax_error)

        assert 2 == len(captions.get_captions("en"))

    def test_caption_error_for_invalid_positioning_values(
            self, sample_dfxp_invalid_positioning_value_template):
        invalid_value_dfxp = (
            sample_dfxp_invalid_positioning_value_template.
            format(origin="px 5px")
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(invalid_value_dfxp)

    def test_caption_error_for_invalid_or_unsupported_positioning_units(
            self, sample_dfxp_invalid_positioning_value_template):
        invalid_dfxp = sample_dfxp_invalid_positioning_value_template.format(
            origin="6foo 7bar"
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(invalid_dfxp)

    def test_individual_timings_of_captions_with_matching_timespec_are_kept(
        self, sample_dfxp_multiple_captions_with_the_same_timing
    ):
        captionset = DFXPReader().read(
            sample_dfxp_multiple_captions_with_the_same_timing
        )
        expected_timings = [(9209000, 12312000)] * 3
        actual_timings = [(c_.start, c_.end) for c_ in
                          captionset.get_captions('en-US')]

        assert expected_timings == actual_timings

    def test_individual_texts_of_captions_with_matching_timespec_are_kept(
            self, sample_dfxp_multiple_captions_with_the_same_timing):
        captionset = DFXPReader().read(
            sample_dfxp_multiple_captions_with_the_same_timing
        )

        expected_texts = ['Some text here',
                          'Some text there',
                          'Caption texts are everywhere!']
        actual_texts = [c_.nodes[0].content for c_ in
                        captionset.get_captions("en-US")]

        assert expected_texts == actual_texts

    def test_individual_layouts_of_captions_with_matching_timespec_are_kept(
        self, sample_dfxp_multiple_captions_with_the_same_timing
    ):
        captionset = DFXPReader().read(
            sample_dfxp_multiple_captions_with_the_same_timing
        )
        expected_layouts = [
            (((10, UnitEnum.PERCENT), (10, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM)),
            (((40, UnitEnum.PERCENT), (40, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM)),
            (((10, UnitEnum.PERCENT), (70, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM))]
        actual_layouts = [c_.layout_info.serialized() for c_ in
                          captionset.get_captions('en-US')]

        assert expected_layouts == actual_layouts

    def test_properly_converts_timing(
            self, sample_dfxp_with_alternative_timing_formats):
        caption_set = DFXPReader().read(
            sample_dfxp_with_alternative_timing_formats)
        caps = caption_set.get_captions('en-US')

        assert caps[0].start == 1900000
        assert caps[0].end == 3050000
        assert caps[1].start == 4000000
        assert caps[1].end == 5200000

    def test_empty_paragraph(self, sample_dfxp_empty_paragraph):
        try:
            DFXPReader().read(sample_dfxp_empty_paragraph)
        except CaptionReadError:
            pytest.fail("Failing on empty paragraph")

    def test_properly_converts_frametiming(self, sample_dfxp_with_frame_timing):
        caption_set = DFXPReader().read(sample_dfxp_with_frame_timing)
        caps = caption_set.get_captions('en-US')

        assert caps[0].end == 12233333
        assert caps[0].start == 9666666

    def test_empty_cue(self, sample_dfxp_empty_cue):
        caption_set = DFXPReader().read(sample_dfxp_empty_cue)
        caps = caption_set.get_captions('en-US')

        assert len(caps) == 1
