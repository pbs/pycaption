import pytest

from pycaption import CaptionReadNoCaptions, DFXPReader, SRTWriter
from pycaption.base import merge_concurrent_captions
from pycaption.exceptions import (
    CaptionReadError,
    CaptionReadSyntaxError,
    CaptionReadTimingError,
)
from pycaption.geometry import HorizontalAlignmentEnum, UnitEnum, VerticalAlignmentEnum
from tests.mixins import ReaderTestingMixIn


class TestDFXPReader(ReaderTestingMixIn):
    def setup_class(self):
        self.reader = DFXPReader()

    def test_positive_answer_for_detection(self, sample_dfxp):
        super().assert_positive_answer_for_detection(sample_dfxp)

    def test_negative_answer_for_microdvd(self, sample_microdvd):
        super().assert_negative_answer_for_detection(sample_microdvd)

    def test_negative_answer_for_sami(self, sample_sami):
        super().assert_negative_answer_for_detection(sample_sami)

    def test_negative_answer_for_scc_on_pop_on(self, sample_scc_pop_on):
        super().assert_negative_answer_for_detection(sample_scc_pop_on)

    def test_negative_answer_for_srt(self, sample_srt):
        super().assert_negative_answer_for_detection(sample_srt)

    def test_negative_answer_for_webvtt(self, sample_webvtt):
        super().assert_negative_answer_for_detection(sample_webvtt)

    def test_caption_length(self, sample_dfxp):
        captions = DFXPReader().read(sample_dfxp)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_dfxp):
        captions = DFXPReader().read(sample_dfxp)
        paragraph = captions.get_captions("en-US")[2]

        assert 17000000 == paragraph.start
        assert 18752000 == paragraph.end

    def test_incorrect_time_format(self, sample_dfxp_incorrect_time_format):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            DFXPReader().read(sample_dfxp_incorrect_time_format)

        assert exc_info.value.args[0].startswith("Invalid timestamp: 0:05.")

    def test_missing_begin(self, sample_dfxp_missing_begin):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            DFXPReader().read(sample_dfxp_missing_begin)
        assert exc_info.value.args[0].startswith("Missing begin time on line ")

    def test_missing_end_and_dur(self, sample_dfxp_missing_end_and_dur):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            DFXPReader().read(sample_dfxp_missing_end_and_dur)
        assert exc_info.value.args[0].startswith(
            "Missing end time or duration on line "
        )

    def test_convert_timestamp_to_microseconds(self):
        reader = DFXPReader()

        assert 1 == reader._convert_timestamp_to_microseconds("0.001ms")
        assert 2000 == reader._convert_timestamp_to_microseconds("2ms")
        assert 1000000 == reader._convert_timestamp_to_microseconds("1s")
        assert 1234567 == reader._convert_timestamp_to_microseconds("1.234567s")
        assert 180000000 == reader._convert_timestamp_to_microseconds("3m")
        assert 14400000000 == reader._convert_timestamp_to_microseconds("4h")
        assert 53333 == reader._convert_timestamp_to_microseconds("1.6f")
        # Tick time: default tickRate = frameRate(30) * subFrameRate(1) = 30
        # 2.3 / 30 * 1_000_000 = 76_666
        assert 76666 == reader._convert_timestamp_to_microseconds("2.3t")

    @pytest.mark.parametrize(
        "timestamp, microseconds",
        [
            ("12:23:34", 44614000000),
            ("23:34:45:56", 84886866666),
            ("34:45:56.7", 125156700000),
            ("13:24:35.67", 48275670000),
            ("24:35:46.456", 88546456000),
            ("1:23:34", 5014000000),
        ],
    )
    def test_clock_time(self, timestamp, microseconds):
        assert (
            DFXPReader()._convert_timestamp_to_microseconds(timestamp) == microseconds
        )

    @pytest.mark.parametrize(
        "timestamp",
        [
            "1:1:11",
            "1:11:1",
            "1:11:11:1",
            "11:11:11:11.11",
            "11:11:11,11",
            "11.11.11.11",
            "11:11:11.",
            "o1:11:11",
        ],
    )
    def test_invalid_timestamp(self, timestamp):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            DFXPReader()._convert_timestamp_to_microseconds(timestamp)

    def test_empty_file(self, sample_dfxp_empty):
        with pytest.raises(CaptionReadNoCaptions):
            DFXPReader().read(sample_dfxp_empty)

    def test_invalid_markup_is_properly_handled(self, sample_dfxp_syntax_error):
        captions = DFXPReader().read(sample_dfxp_syntax_error)

        assert 2 == len(captions.get_captions("en"))

    def test_caption_error_for_invalid_positioning_values(
        self, sample_dfxp_invalid_positioning_value_template
    ):
        invalid_value_dfxp = sample_dfxp_invalid_positioning_value_template.format(
            origin="px 5px"
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(invalid_value_dfxp)

    def test_caption_error_for_invalid_or_unsupported_positioning_units(
        self, sample_dfxp_invalid_positioning_value_template
    ):
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
        actual_timings = [(c_.start, c_.end) for c_ in captionset.get_captions("en-US")]

        assert expected_timings == actual_timings

    def test_individual_texts_of_captions_with_matching_timespec_are_kept(
        self, sample_dfxp_multiple_captions_with_the_same_timing
    ):
        captionset = DFXPReader().read(
            sample_dfxp_multiple_captions_with_the_same_timing
        )

        expected_texts = [
            "Some text here",
            "Some text there",
            "Caption texts are everywhere!",
        ]
        actual_texts = [c_.nodes[0].content for c_ in captionset.get_captions("en-US")]

        assert expected_texts == actual_texts

    def test_individual_layouts_of_captions_with_matching_timespec_are_kept(
        self, sample_dfxp_multiple_captions_with_the_same_timing
    ):
        captionset = DFXPReader().read(
            sample_dfxp_multiple_captions_with_the_same_timing
        )
        expected_layouts = [
            (
                ((10, UnitEnum.PERCENT), (10, UnitEnum.PERCENT)),
                None,
                None,
                (HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM),
                None,
            ),
            (
                ((40, UnitEnum.PERCENT), (40, UnitEnum.PERCENT)),
                None,
                None,
                (HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM),
                None,
            ),
            (
                ((10, UnitEnum.PERCENT), (70, UnitEnum.PERCENT)),
                None,
                None,
                (HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM),
                None,
            ),
        ]
        actual_layouts = [
            c_.layout_info.serialized() for c_ in captionset.get_captions("en-US")
        ]

        assert expected_layouts == actual_layouts

    def test_properly_converts_timing(
        self, sample_dfxp_with_alternative_timing_formats
    ):
        caption_set = DFXPReader().read(sample_dfxp_with_alternative_timing_formats)
        caps = caption_set.get_captions("en-US")

        assert caps[0].start == 1900000
        assert caps[0].end == 3050000
        assert caps[1].start == 4000000
        assert caps[1].end == 5200000

    def test_empty_paragraph(self, sample_dfxp_empty_paragraph):
        try:
            DFXPReader().read(sample_dfxp_empty_paragraph)
        except CaptionReadError:
            pytest.fail("Failing on empty paragraph")

    def test_only_spaces_paragraph(self, sample_dfxp_only_spaces_paragraph):
        caption_set = DFXPReader().read(sample_dfxp_only_spaces_paragraph)
        caps = caption_set.get_captions("en-US")

        assert len(caps) == 1

    def test_properly_converts_frametiming(self, sample_dfxp_with_frame_timing):
        caption_set = DFXPReader().read(sample_dfxp_with_frame_timing)
        caps = caption_set.get_captions("en-US")

        assert caps[0].end == 12233333
        assert caps[0].start == 9666666

    def test_properly_converts_custom_framerate(
        self, sample_dfxp_with_custom_framerate
    ):
        caption_set = DFXPReader().read(sample_dfxp_with_custom_framerate)
        caps = caption_set.get_captions("en-US")

        # 24 * (1000/1001) = 23.976023976... fps
        assert caps[0].start == 9834166
        assert caps[0].end == 12291958

    def test_properly_converts_custom_tickrate(self, sample_dfxp_with_custom_tickrate):
        caption_set = DFXPReader().read(sample_dfxp_with_custom_tickrate)
        caps = caption_set.get_captions("en-US")

        # tickRate=10000000: 50000000/10000000 = 5s, 120000000/10000000 = 12s
        assert caps[0].start == 5000000
        assert caps[0].end == 12000000

    def test_convert_timestamp_with_custom_framerate(self):
        reader = DFXPReader()
        reader.framerate = 24.0
        # 1.6 frames at 24fps = 1.6/24 * 1_000_000 = 66666
        assert 66666 == reader._convert_timestamp_to_microseconds("1.6f")
        # clock-time frames: 15 frames at 24fps = 15/24 * 1_000_000 = 625000
        assert 625000 == reader._convert_timestamp_to_microseconds("00:00:00:15")

    def test_convert_timestamp_with_custom_tickrate(self):
        reader = DFXPReader()
        reader.tickrate = 10.0
        # 100 ticks at tickRate=10: 100/10 * 1_000_000 = 10_000_000
        assert 10000000 == reader._convert_timestamp_to_microseconds("100t")

    def test_properly_converts_framerate_without_multiplier(
        self, sample_dfxp_with_framerate_no_multiplier
    ):
        caption_set = DFXPReader().read(sample_dfxp_with_framerate_no_multiplier)
        caps = caption_set.get_captions("en-US")

        # 24fps, no multiplier (defaults to "1 1"):
        # begin 00:00:01:12 = 1s + 12/24 = 1.5s = 1_500_000 µs
        # end   00:00:02:00 = 2s + 0/24  = 2.0s = 2_000_000 µs
        assert caps[0].start == 1500000
        assert caps[0].end == 2000000

    def test_default_tickrate_uses_subframerate(self):
        xml = (
            '<?xml version="1.0"?>'
            '<tt xmlns="http://www.w3.org/ns/ttml"'
            ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
            ' ttp:frameRate="30" ttp:subFrameRate="2">'
            "<body><div xml:lang='en'>"
            '<p begin="60t" end="120t">X</p>'
            "</div></body></tt>"
        )
        caption_set = DFXPReader().read(xml)
        caps = caption_set.get_captions("en")
        # default tickRate = frameRate(30) * subFrameRate(2) = 60
        # 60t / 60 = 1s = 1_000_000 µs; 120t / 60 = 2s = 2_000_000 µs
        assert caps[0].start == 1000000
        assert caps[0].end == 2000000

    def test_invalid_framerate_multiplier_single_value(self):
        xml = (
            '<?xml version="1.0"?>'
            '<tt xmlns="http://www.w3.org/ns/ttml"'
            ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
            ' ttp:frameRate="24" ttp:frameRateMultiplier="1000">'
            "<body><div xml:lang='en'>"
            '<p begin="0s" end="1s">X</p>'
            "</div></body></tt>"
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(xml)

    def test_invalid_framerate_multiplier_zero_denominator(self):
        xml = (
            '<?xml version="1.0"?>'
            '<tt xmlns="http://www.w3.org/ns/ttml"'
            ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
            ' ttp:frameRate="24" ttp:frameRateMultiplier="1000 0">'
            "<body><div xml:lang='en'>"
            '<p begin="0s" end="1s">X</p>'
            "</div></body></tt>"
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(xml)

    def test_invalid_tickrate_zero(self):
        xml = (
            '<?xml version="1.0"?>'
            '<tt xmlns="http://www.w3.org/ns/ttml"'
            ' xmlns:ttp="http://www.w3.org/ns/ttml#parameter"'
            ' ttp:tickRate="0">'
            "<body><div xml:lang='en'>"
            '<p begin="0s" end="1s">X</p>'
            "</div></body></tt>"
        )
        with pytest.raises(CaptionReadSyntaxError):
            DFXPReader().read(xml)

    def test_negative_answer_for_content_with_closing_tt_only(self):
        content = "This has </tt> in it but no opening tag"
        assert self.reader.detect(content) is False

    def test_empty_cue(self, sample_dfxp_empty_cue):
        caption_set = DFXPReader().read(sample_dfxp_empty_cue)
        caps = caption_set.get_captions("en-US")

        assert len(caps) == 1

    def test_concurrent_captions_with_empty_p_no_none_in_list(
        self, sample_dfxp_concurrent_with_empty_p
    ):
        caption_set = DFXPReader().read(sample_dfxp_concurrent_with_empty_p)
        captions = caption_set.get_captions("en")
        assert all(c is not None for c in captions)
        assert len(captions) == 1

    def test_concurrent_captions_with_empty_p_merge_does_not_crash(
        self, sample_dfxp_concurrent_with_empty_p
    ):
        caption_set = DFXPReader().read(sample_dfxp_concurrent_with_empty_p)
        merged = merge_concurrent_captions(caption_set)
        captions = merged.get_captions("en")
        assert len(captions) >= 1
        assert all(c is not None for c in captions)

    def test_concurrent_captions_with_empty_p_srt_writer_does_not_crash(
        self, sample_dfxp_concurrent_with_empty_p
    ):
        caption_set = DFXPReader().read(sample_dfxp_concurrent_with_empty_p)
        output = SRTWriter().write(caption_set)
        assert "Subtitle End" in output

    def test_none_from_convert_p_tag_is_filtered(self, sample_dfxp):
        reader = DFXPReader()
        original = reader._convert_p_tag_to_caption
        call_count = [0]

        def patched(p_tag):
            call_count[0] += 1
            if call_count[0] == 2:
                return None
            return original(p_tag)

        reader._convert_p_tag_to_caption = patched
        caption_set = reader.read(sample_dfxp)
        captions = caption_set.get_captions("en-US")
        assert all(c is not None for c in captions)
        assert len(captions) == 6
