import pytest
from bs4 import BeautifulSoup

from pycaption import CaptionReadNoCaptions, DFXPReader, DFXPWriter, SRTWriter
from pycaption.base import (
    Caption,
    CaptionList,
    CaptionNode,
    CaptionSet,
    merge_concurrent_captions,
)
from pycaption.exceptions import (
    CaptionReadError,
    CaptionReadSyntaxError,
    CaptionReadTimingError,
)
from pycaption.geometry import (
    Alignment,
    HorizontalAlignmentEnum,
    Layout,
    LineAlignmentEnum,
    Point,
    Size,
    UnitEnum,
    VerticalAlignmentEnum,
    WritingDirectionEnum,
)
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
        with pytest.raises(CaptionReadTimingError):
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
                None,
                None,
            ),
            (
                ((40, UnitEnum.PERCENT), (40, UnitEnum.PERCENT)),
                None,
                None,
                (HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM),
                None,
                None,
                None,
            ),
            (
                ((10, UnitEnum.PERCENT), (70, UnitEnum.PERCENT)),
                None,
                None,
                (HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM),
                None,
                None,
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

    def test_background_color_is_read(self):
        dfxp = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="bg" tts:backgroundColor="yellow"/>
  </styling>
  <layout/>
 </head>
 <body>
  <div>
   <p begin="00:00:01.000" end="00:00:02.000" style="bg"
      tts:backgroundColor="black">Hello</p>
  </div>
 </body>
</tt>"""
        caption_set = DFXPReader().read(dfxp)
        styles = dict(caption_set.get_styles())
        assert styles["bg"]["background-color"] == "yellow"
        caption = caption_set.get_captions("en")[0]
        assert caption.style["background-color"] == "black"

    def test_writing_mode_is_read(self):
        dfxp = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling/>
  <layout>
   <region xml:id="vertical" tts:writingMode="tbrl"
           tts:origin="10% 10%" tts:extent="20% 80%"/>
  </layout>
 </head>
 <body>
  <div>
   <p begin="00:00:01.000" end="00:00:02.000"
      region="vertical">Vertical text</p>
  </div>
 </body>
</tt>"""
        caption_set = DFXPReader().read(dfxp)
        caption = caption_set.get_captions("en")[0]
        assert caption.layout_info.writing_direction == (
            WritingDirectionEnum.VERTICAL_RL
        )


def _layout_at(x, y):
    """Build a top-left anchored Layout at the given percentage origin."""
    return Layout(
        origin=Point(Size(x, UnitEnum.PERCENT), Size(y, UnitEnum.PERCENT)),
        alignment=Alignment(HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP),
    )


def _caption_set(nodes, layout_info=None):
    """Wrap nodes in a single-caption, single-language CaptionSet."""
    caption = Caption(1000000, 2000000, nodes, layout_info=layout_info)
    return CaptionSet({"en-US": CaptionList([caption])})


class TestDFXPWriterNodePositioning:
    def setup_class(self):
        self.nodes = [
            CaptionNode.create_text("left side", layout_info=_layout_at(10, 80)),
            CaptionNode.create_text("right side", layout_info=_layout_at(70, 20)),
        ]

    def test_text_nodes_are_wrapped_in_their_own_spans(self):
        dfxp = DFXPWriter().write(_caption_set(self.nodes))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {
            region["xml:id"]: region.get("tts:origin")
            for region in soup.find_all("region")
        }
        spans = soup.find_all("span")
        assert len(spans) == 2
        assert origins[spans[0]["region"]] == "10% 80%"
        assert origins[spans[1]["region"]] == "70% 20%"
        assert "left sideright side" not in dfxp

    def test_text_node_layouts_survive_a_round_trip(self):
        dfxp = DFXPWriter().write(_caption_set(self.nodes))

        caption = DFXPReader().read(dfxp).get_captions("en-US")[0]
        recovered = {
            node.content: str(node.layout_info.origin)
            for node in caption.nodes
            if node.type_ == CaptionNode.TEXT and node.content.strip()
        }
        assert recovered == {
            "left side": "<Point (10%, 80%)>",
            "right side": "<Point (70%, 20%)>",
        }

    def test_nodes_sharing_the_caption_layout_are_not_wrapped(self):
        layout = _layout_at(10, 80)
        nodes = [
            CaptionNode.create_text("one line", layout_info=layout),
            CaptionNode.create_break(layout_info=layout),
            CaptionNode.create_text("and another", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=layout))

        assert not BeautifulSoup(dfxp, "lxml-xml").find_all("span")

    def test_layout_without_positioning_data_is_not_wrapped(self):
        nodes = [CaptionNode.create_text("no position", layout_info=Layout())]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        assert not BeautifulSoup(dfxp, "lxml-xml").find_all("span")

    def test_a_whitespace_only_node_keeps_the_region_in_effect(self):
        nodes = [
            CaptionNode.create_text("visible"),
            CaptionNode.create_text("  ", layout_info=_layout_at(30, 40)),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {region.get("tts:origin") for region in soup.find_all("region")}
        assert not soup.find_all("span")
        assert "30% 40%" not in origins

    def test_wrapping_span_can_carry_inline_positioning(self):
        writer = DFXPWriter(write_inline_positioning=True)
        dfxp = writer.write(_caption_set(self.nodes))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert [span["tts:origin"] for span in spans] == ["10% 80%", "70% 20%"]

    def test_inline_positioning_survives_a_run_starting_at_a_closing_tag(self):
        layout = _layout_at(10, 80)
        nodes = [
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout),
            CaptionNode.create_text("inside", layout_info=_layout_at(70, 20)),
            CaptionNode.create_style(False, {"italics": True}),
            CaptionNode.create_text("after", layout_info=layout),
        ]
        writer = DFXPWriter(write_inline_positioning=True)
        dfxp = writer.write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        last = BeautifulSoup(dfxp, "lxml-xml").find_all("span")[-1]
        assert last.get_text(strip=True) == "after"
        assert last["tts:origin"] == "10% 80%"

    def test_a_text_node_without_a_layout_inherits_its_enclosing_span(self):
        nodes = [
            CaptionNode.create_style(
                True, {"italics": True}, layout_info=_layout_at(70, 20)
            ),
            CaptionNode.create_text("inherited"),
            CaptionNode.create_style(False, {"italics": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert len(spans) == 1
        assert spans[0].get_text(strip=True) == "inherited"

    def test_a_style_span_without_a_layout_keeps_the_region_around_it(self):
        nodes = [
            CaptionNode.create_style(
                True, {"italics": True}, layout_info=_layout_at(70, 20)
            ),
            CaptionNode.create_style(True, {"bold": True}),
            CaptionNode.create_text("one"),
            CaptionNode.create_style(False, {"bold": True}),
            CaptionNode.create_style(True, {"underline": True}),
            CaptionNode.create_text("two"),
            CaptionNode.create_style(False, {"underline": True}),
            CaptionNode.create_style(False, {"italics": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {
            region["xml:id"]: region.get("tts:origin")
            for region in soup.find_all("region")
        }
        carrying = [span for span in soup.find_all("span") if span.get("region")]
        assert len(carrying) == 1
        assert origins[carrying[0]["region"]] == "70% 20%"
        assert list(carrying[0].stripped_strings) == ["one", "two"]

    def test_a_text_node_without_a_layout_stays_with_the_paragraph(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_text("positioned", layout_info=layout),
            CaptionNode.create_text("bare"),
            CaptionNode.create_text("positioned again", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        paragraph = BeautifulSoup(dfxp, "lxml-xml").find("p")
        assert [span.get_text() for span in paragraph.find_all("span")] == [
            "positioned",
            "positioned again",
        ]
        loose = paragraph.find_all(string=True, recursive=False)
        assert "bare" in [text.strip() for text in loose]

    def test_a_closing_tag_with_nothing_open_does_not_split_a_region(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_text("hello", layout_info=layout),
            CaptionNode.create_style(False, {"italics": True}),
            CaptionNode.create_text(" world", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert len(spans) == 1
        assert spans[0].get_text() == "hello world"

    def test_a_break_between_two_nodes_of_one_region_stays_in_the_span(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_text("first line", layout_info=layout),
            CaptionNode.create_break(),
            CaptionNode.create_text("second line", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert len(spans) == 1
        assert spans[0].find("br") is not None
        assert spans[0].get_text(strip=True) == "first linesecond line"

    def test_a_style_span_joins_the_run_sharing_its_region(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_text("plain", layout_info=layout),
            CaptionNode.create_break(),
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout),
            CaptionNode.create_text("emphasis", layout_info=layout),
            CaptionNode.create_style(False, {"italics": True}, layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        wrapper = soup.find("p").find("span")
        assert wrapper.find("br") is not None
        assert wrapper.find("span")["tts:fontStyle"] == "italic"
        assert wrapper.get_text(strip=True) == "plainemphasis"

    def test_a_style_span_carrying_a_layout_gains_no_extra_wrapper(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout),
            CaptionNode.create_text("emphasis", layout_info=layout),
            CaptionNode.create_style(False, {"italics": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert len(spans) == 1
        assert spans[0]["tts:fontStyle"] == "italic"

    def test_text_after_a_positioned_style_span_keeps_its_region(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_style(True, {"bold": True}, layout_info=layout),
            CaptionNode.create_text("inside", layout_info=layout),
            CaptionNode.create_style(False, {"bold": True}),
            CaptionNode.create_text("after", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(30, 40)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {
            region["xml:id"]: region.get("tts:origin")
            for region in soup.find_all("region")
        }
        paragraph = soup.find("p")
        wrapper = paragraph.find("span")
        assert "tts:fontWeight" not in wrapper.attrs
        assert origins[wrapper["region"]] == "70% 20%"
        assert wrapper.get_text(strip=True) == "insideafter"
        loose = paragraph.find_all(string=True, recursive=False)
        assert not [text for text in loose if text.strip()]

    def test_a_region_already_in_effect_is_not_repeated(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout),
            CaptionNode.create_text("first", layout_info=layout),
            CaptionNode.create_text("elsewhere", layout_info=_layout_at(30, 40)),
            CaptionNode.create_text("third", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find_all("span")
        assert len(spans) == 2
        assert spans[1].get_text(strip=True) == "elsewhere"

    def test_a_style_span_crossing_a_region_boundary_stays_well_formed(self):
        nodes = [
            CaptionNode.create_style(
                True, {"italics": True}, layout_info=_layout_at(70, 20)
            ),
            CaptionNode.create_text("here", layout_info=_layout_at(70, 20)),
            CaptionNode.create_text("there", layout_info=_layout_at(30, 40)),
            CaptionNode.create_style(False, {"italics": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        outer = soup.find("p").find("span")
        assert outer["tts:fontStyle"] == "italic"
        assert outer.find("span").get_text(strip=True) == "there"
        assert dfxp.count("<span") == dfxp.count("</span>")

    def test_nested_style_spans_are_searched_from_the_innermost_out(self):
        layout = _layout_at(10, 80)
        nodes = [
            CaptionNode.create_style(True, {"underline": True}, layout_info=layout),
            CaptionNode.create_style(
                True, {"bold": True}, layout_info=_layout_at(30, 40)
            ),
            CaptionNode.create_text("deep", layout_info=layout),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(70, 20)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {
            region["xml:id"]: region.get("tts:origin")
            for region in soup.find_all("region")
        }
        innermost = soup.find_all("span")[-1]
        assert innermost.get_text(strip=True) == "deep"
        assert origins[innermost["region"]] == "10% 80%"
        assert dfxp.count("<span") == dfxp.count("</span>")

    def test_text_beside_a_crossing_style_span_keeps_its_own_region(self):
        nodes = [
            CaptionNode.create_text("first", layout_info=_layout_at(70, 20)),
            CaptionNode.create_style(
                True, {"italics": True}, layout_info=_layout_at(70, 20)
            ),
            CaptionNode.create_text("inside", layout_info=_layout_at(30, 40)),
            CaptionNode.create_style(False, {"italics": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        soup = BeautifulSoup(dfxp, "lxml-xml")
        origins = {
            region["xml:id"]: region.get("tts:origin")
            for region in soup.find_all("region")
        }
        wrapper = soup.find("p").find("span")
        assert wrapper.get_text(strip=True) == "first"
        assert origins[wrapper["region"]] == "70% 20%"
        assert dfxp.count("<span") == dfxp.count("</span>")

    def test_text_beside_an_unclosed_style_span_keeps_its_own_region(self):
        nodes = [
            CaptionNode.create_text("first", layout_info=_layout_at(70, 20)),
            CaptionNode.create_style(
                True, {"italics": True}, layout_info=_layout_at(70, 20)
            ),
            CaptionNode.create_text("inside", layout_info=_layout_at(30, 40)),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        caption = DFXPReader().read(dfxp).get_captions("en-US")[0]
        recovered = {
            node.content: str(node.layout_info.origin)
            for node in caption.nodes
            if node.type_ == CaptionNode.TEXT and node.content.strip()
        }
        assert recovered == {
            "first": "<Point (70%, 20%)>",
            "inside": "<Point (30%, 40%)>",
        }

    def test_a_trailing_break_stays_outside_the_last_region_span(self):
        nodes = [
            CaptionNode.create_text("one line", layout_info=_layout_at(70, 20)),
            CaptionNode.create_break(),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        paragraph = BeautifulSoup(dfxp, "lxml-xml").find("p")
        spans = paragraph.find_all("span")
        assert len(spans) == 1
        assert spans[0].get_text(strip=True) == "one line"
        assert paragraph.find("br").parent is paragraph
        assert dfxp.count("<span") == dfxp.count("</span>")

    def test_style_node_without_attributes_emits_no_closing_tag(self):
        nodes = [
            CaptionNode.create_style(True, {}),
            CaptionNode.create_text("hello"),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes))

        assert "</span>" not in dfxp
        assert BeautifulSoup(dfxp, "lxml-xml").find("p").get_text(strip=True) == "hello"

    def test_a_run_holding_no_visible_text_gets_no_wrapper(self):
        layout = _layout_at(70, 20)
        nodes = [
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout),
            CaptionNode.create_style(False, {"italics": True}),
            CaptionNode.create_style(True, {"bold": True}, layout_info=layout),
            CaptionNode.create_style(False, {"bold": True}),
        ]
        dfxp = DFXPWriter().write(_caption_set(nodes, layout_info=_layout_at(10, 80)))

        spans = BeautifulSoup(dfxp, "lxml-xml").find("p").find_all("span")
        styling = [
            span.get("tts:fontStyle") or span.get("tts:fontWeight") for span in spans
        ]
        assert styling == ["italic", "bold"]


class TestDFXPWriterLineAlignment:
    """A layout holding only a line alignment gets no region of its own.

    A WebVTT ``line`` setting leaves one behind when its value yields no line
    to place the cue at: ``line:auto,start``, where the value is valid but
    names no line, or a value the grammar discards outright.  Either way the
    cue keeps the default placement instead of taking a vertical one from the
    qualifier alone.
    """

    def setup_class(self):
        self.nodes = [CaptionNode.create_text("hello")]

    @staticmethod
    def _regions(dfxp):
        soup = BeautifulSoup(dfxp, "lxml-xml")
        by_id = {
            region["xml:id"]: region.get("tts:displayAlign")
            for region in soup.find_all("region")
        }
        return by_id, soup.find("p")["region"]

    def test_a_line_alignment_alone_mints_no_region(self):
        layout = Layout(line_alignment=LineAlignmentEnum.START)
        dfxp = DFXPWriter().write(_caption_set(self.nodes, layout_info=layout))

        by_id, paragraph_region = self._regions(dfxp)
        assert list(by_id) == [paragraph_region]

    def test_a_line_alignment_alone_keeps_the_default_placement(self):
        layout = Layout(line_alignment=LineAlignmentEnum.START)
        dfxp = DFXPWriter().write(_caption_set(self.nodes, layout_info=layout))

        by_id, paragraph_region = self._regions(dfxp)
        assert by_id[paragraph_region] == "after"

    def test_an_empty_layout_still_gets_no_region_of_its_own(self):
        dfxp = DFXPWriter().write(_caption_set(self.nodes, layout_info=Layout()))

        by_id, paragraph_region = self._regions(dfxp)
        assert list(by_id) == [paragraph_region]
