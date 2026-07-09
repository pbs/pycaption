import pytest

from pycaption import (
    CaptionReadError,
    CaptionReadNoCaptions,
    CaptionReadSyntaxError,
    DFXPReader,
    SAMIReader,
    WebVTTReader,
    WebVTTWriter,
)
from pycaption.base import CaptionNode
from pycaption.geometry import (
    HorizontalAlignmentEnum,
    Size,
    UnitEnum,
    WritingDirectionEnum,
)
from tests.mixins import ReaderTestingMixIn


class TestWebVTTReader(ReaderTestingMixIn):
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_positive_answer_for_detection(self, sample_webvtt):
        super().assert_positive_answer_for_detection(sample_webvtt)

    def test_negative_answer_for_detection_dfxp(self, sample_dfxp):
        super().assert_negative_answer_for_detection(sample_dfxp)

    def test_negative_answer_for_detection_microdvd(self, sample_microdvd):
        super().assert_negative_answer_for_detection(sample_microdvd)

    def test_negative_answer_for_detection_sami(self, sample_sami):
        super().assert_negative_answer_for_detection(sample_sami)

    def test_negative_answer_for_detection_scc_pop_on(self, sample_scc_pop_on):
        super().assert_negative_answer_for_detection(sample_scc_pop_on)

    def test_negative_answer_for_detection_srt(self, sample_srt):
        super().assert_negative_answer_for_detection(sample_srt)

    def test_caption_length(self, sample_webvtt_2):
        captions = self.reader.read(sample_webvtt_2)

        assert len(captions.get_captions("en-US")) == 7

    def test_read_supports_multiple_languages(self, sample_webvtt):
        captions = self.reader.read(sample_webvtt, lang="es")

        assert captions.get_captions("es") is not None

    def test_proper_timestamps(self, sample_webvtt):
        captions = self.reader.read(sample_webvtt)
        cue = captions.get_captions("en-US")[2]

        assert cue.start == 17000000
        assert cue.end == 18752000

    def test_forward_time_shift(self, sample_webvtt):
        captions = WebVTTReader(time_shift_milliseconds=15).read(sample_webvtt)
        cue = captions.get_captions("en-US")[2]

        assert cue.start == 17015000
        assert cue.end == 18767000

    def test_backward_time_shift(self, sample_webvtt):
        captions = WebVTTReader(time_shift_milliseconds=-15).read(sample_webvtt)
        cue = captions.get_captions("en-US")[2]

        assert cue.start == 16985000
        assert cue.end == 18737000

    def test_webvtt_cue_components_parsed_from_text(self):
        nodes = self.reader._parse_cue_text(
            "<c vIntro><b>Wikipedia</b> is a great adventure. <i>It may have "
            "its shortcomings</i>, but it is<u> the largest</u> collective "
            "knowledge construction endevour</c> <ruby>base text <rt>"
            "annotation</rt></ruby> <v Audry><b>Yes</b>, indeed!"
        )
        from pycaption.base import CaptionNode

        text = "".join(
            n.content for n in nodes if n.type_ == CaptionNode.TEXT
        )
        expected = (
            "Wikipedia is a great adventure. It may have "
            "its shortcomings, but it is the largest collective "
            "knowledge construction endevour base text annotation"
            " Audry: Yes, indeed!"
        )
        assert text == expected

    def test_empty_file(self, sample_webvtt_empty):
        with pytest.raises(CaptionReadNoCaptions):
            WebVTTReader().read(sample_webvtt_empty)

    def test_not_ignoring_timing_errors(self):
        # todo: same assert w/ different arguments -> this can be parametrized;
        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "\n" "00:00:20.000 --> 00:00:10.000\n" "foo bar baz"
            )

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.\n"
            )

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )

    def test_ignoring_timing_errors(self):
        # Even if timing errors are ignored, this has to raise an exception
        with pytest.raises(CaptionReadSyntaxError):
            WebVTTReader().read(
                "\nNOTE invalid cue stamp\n" "00:00:20.000 --> \nfoo bar baz\n"
            )

        # And this too
        with pytest.raises(CaptionReadSyntaxError):
            WebVTTReader().read(
                "\n00:00:20,000 --> 00:00:22,000\n" "Note the comma instead of point.\n"
            )

        # todo: at this point it can be split into 2 separate tests
        try:
            WebVTTReader().read(
                "\n"
                "00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.\n"
            )
        except CaptionReadError:
            pytest.fail("Shouldn't raise CaptionReadError")

        try:
            WebVTTReader().read(
                "\n"
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )
        except CaptionReadError:
            pytest.fail("Shouldn't raise CaptionReadError")

    def test_invalid_files(self):
        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:10.000\n" "Start time is greater than end time."
            )

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )

    def test_zero_start(self, sample_webvtt_last_cue_zero_start):
        captions = self.reader.read(sample_webvtt_last_cue_zero_start)
        cue = captions.get_captions("en-US")[0]

        assert cue.start == 0

    def test_webvtt_empty_cue(self, sample_webvtt_empty_cue):
        assert 1 == len(self.reader.read(sample_webvtt_empty_cue).get_captions("en-US"))


class TestWebVTTWriter:
    def setup_method(self):
        self.writer = WebVTTWriter()

    def test_double_br(self, sample_webvtt_double_br, sample_sami_double_br):
        caption_set = SAMIReader().read(sample_sami_double_br)
        results = WebVTTWriter().write(caption_set)

        assert sample_webvtt_double_br == results

    def test_break_node_positioning_is_ignored(
        self, webvtt_from_dfxp_with_conflicting_align, dfxp_style_region_align_conflict
    ):
        caption_set = DFXPReader().read(dfxp_style_region_align_conflict)
        results = WebVTTWriter().write(caption_set)

        assert webvtt_from_dfxp_with_conflicting_align == results

    def test_lang_option(
        self,
        sample_webvtt_multi_lang_en,
        sample_webvtt_multi_lang_de,
        sample_sami_with_multi_lang,
    ):
        caption_set = SAMIReader().read(sample_sami_with_multi_lang)
        results = WebVTTWriter().write(caption_set, "de-DE")

        assert sample_webvtt_multi_lang_de == results
        results = WebVTTWriter().write(caption_set, "en-US")
        assert sample_webvtt_multi_lang_en == results


class TestWebVTTRegionParsing:
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_region_block_parsed_into_layout(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:subtitle_area\n"
            "width:50%\n"
            "lines:3\n"
            "regionanchor:0%,100%\n"
            "viewportanchor:10%,90%\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:subtitle_area\n"
            "Hello world\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info is not None
        assert cue.layout_info.origin is not None
        assert cue.layout_info.extent is not None

    def test_region_origin_calculation(self):
        """origin_x = viewportanchor_x - (regionanchor_x / 100 * width)
        origin_y = viewportanchor_y - (regionanchor_y / 100 * height)
        height = lines * 5.33
        """
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:box\n"
            "width:50%\n"
            "lines:3\n"
            "regionanchor:0%,100%\n"
            "viewportanchor:10%,90%\n\n"
            "00:00:01.000 --> 00:00:03.000 region:box\n"
            "Test\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info
        # origin_x = 10 - (0/100 * 50) = 10.0
        assert layout.origin.x.value == pytest.approx(10.0)
        # height = 3 * 5.33 = 15.99
        # origin_y = 90 - (100/100 * 15.99) = 74.01
        assert layout.origin.y.value == pytest.approx(74.01)
        # extent = width=50%, height=15.99%
        assert layout.extent.horizontal.value == pytest.approx(50.0)
        assert layout.extent.vertical.value == pytest.approx(15.99)

    def test_region_defaults(self):
        """width=100%, lines=3, regionanchor=0%,100%, viewportanchor=0%,100%"""
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:minimal\n\n"
            "00:00:01.000 --> 00:00:03.000 region:minimal\n"
            "Test\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info
        # width=100, lines=3, height=15.99
        # regionanchor=0,100 viewportanchor=0,100
        # origin_x = 0 - (0/100 * 100) = 0
        # origin_y = 100 - (100/100 * 15.99) = 84.01
        assert layout.origin.x.value == pytest.approx(0.0)
        assert layout.origin.y.value == pytest.approx(84.01)
        assert layout.extent.horizontal.value == pytest.approx(100.0)
        assert layout.extent.vertical.value == pytest.approx(15.99)

    def test_region_webvtt_positioning_passthrough(self):
        """VTT->VTT round-trip: cue settings string preserved."""
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:r1\n"
            "width:50%\n\n"
            "00:00:01.000 --> 00:00:03.000 region:r1\n"
            "Hello\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info.webvtt_positioning == "region:r1"

    def test_invalid_region_reference_ignored(self):
        vtt = (
            "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 region:nonexistent\n" "Hello\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        # Falls back to raw positioning passthrough
        assert cue.layout_info.webvtt_positioning == "region:nonexistent"
        assert cue.layout_info.origin is None

    def test_duplicate_region_id_first_wins(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:dup\n"
            "width:40%\n\n"
            "REGION\n"
            "id:dup\n"
            "width:80%\n\n"
            "00:00:01.000 --> 00:00:03.000 region:dup\n"
            "Test\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info.extent.horizontal.value == pytest.approx(40.0)

    def test_multiple_regions(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:top\n"
            "width:100%\n"
            "lines:2\n"
            "viewportanchor:0%,10%\n"
            "regionanchor:0%,0%\n\n"
            "REGION\n"
            "id:bottom\n"
            "width:100%\n"
            "lines:2\n"
            "viewportanchor:0%,90%\n"
            "regionanchor:0%,0%\n\n"
            "00:00:01.000 --> 00:00:03.000 region:top\n"
            "Top caption\n\n"
            "00:00:01.000 --> 00:00:03.000 region:bottom\n"
            "Bottom caption\n"
        )
        captions = self.reader.read(vtt)
        cues = captions.get_captions("en-US")
        # top: origin_y = 10 - (0/100 * 10.66) = 10.0
        assert cues[0].layout_info.origin.y.value == pytest.approx(10.0)
        # bottom: origin_y = 90 - (0/100 * 10.66) = 90.0
        assert cues[1].layout_info.origin.y.value == pytest.approx(90.0)

    def test_region_without_id_ignored(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "width:50%\n"
            "lines:3\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "No region reference\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info is None

    def test_duplicate_setting_in_region_first_wins(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:r1\n"
            "width:40%\n"
            "width:80%\n\n"
            "00:00:01.000 --> 00:00:03.000 region:r1\n"
            "Test\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info.extent.horizontal.value == pytest.approx(40.0)

    def test_cue_without_region_unaffected(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:r1\n"
            "width:50%\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "No region\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        assert cue.layout_info is None


class TestWebVTTInlineMarkupParsing:
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_italic_tags_produce_style_nodes(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("Hello <i>world</i>")
        assert len(nodes) == 4
        assert nodes[0].type_ == CaptionNode.TEXT
        assert nodes[0].content == "Hello "
        assert nodes[1].type_ == CaptionNode.STYLE
        assert nodes[1].start is True
        assert nodes[1].content == {"italics": True}
        assert nodes[2].type_ == CaptionNode.TEXT
        assert nodes[2].content == "world"
        assert nodes[3].type_ == CaptionNode.STYLE
        assert nodes[3].start is False
        assert nodes[3].content == {"italics": True}

    def test_bold_tags(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<b>bold text</b>")
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"bold": True}
        assert nodes[0].start is True
        assert nodes[1].type_ == CaptionNode.TEXT
        assert nodes[1].content == "bold text"
        assert nodes[2].type_ == CaptionNode.STYLE
        assert nodes[2].content == {"bold": True}
        assert nodes[2].start is False

    def test_underline_tags(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<u>underlined</u>")
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"underline": True}
        assert nodes[0].start is True

    def test_nested_tags(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<b><i>nested</i></b>")
        assert len(nodes) == 5
        assert nodes[0].content == {"bold": True}
        assert nodes[0].start is True
        assert nodes[1].content == {"italics": True}
        assert nodes[1].start is True
        assert nodes[2].type_ == CaptionNode.TEXT
        assert nodes[2].content == "nested"
        assert nodes[3].content == {"italics": True}
        assert nodes[3].start is False
        assert nodes[4].content == {"bold": True}
        assert nodes[4].start is False

    def test_class_tag(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<c.yellow>text</c>")
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"classes": ["yellow"]}
        assert nodes[0].start is True
        assert nodes[2].type_ == CaptionNode.STYLE
        assert nodes[2].content == {"classes": []}
        assert nodes[2].start is False

    def test_class_tag_multiple_classes(self):
        nodes = self.reader._parse_cue_text("<c.yellow.bg_blue>text</c>")
        assert nodes[0].content == {"classes": ["yellow", "bg_blue"]}

    def test_lang_tag(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<lang en>English</lang>")
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"lang": "en"}
        assert nodes[0].start is True
        assert nodes[2].content == {"lang": ""}
        assert nodes[2].start is False

    def test_ruby_and_rt_tags(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text(
            "<ruby>base<rt>annotation</rt></ruby>"
        )
        assert nodes[0].content == {"ruby": True}
        assert nodes[0].start is True
        assert nodes[1].type_ == CaptionNode.TEXT
        assert nodes[1].content == "base"
        assert nodes[2].content == {"ruby_text": True}
        assert nodes[2].start is True
        assert nodes[3].type_ == CaptionNode.TEXT
        assert nodes[3].content == "annotation"
        assert nodes[4].content == {"ruby_text": True}
        assert nodes[4].start is False
        assert nodes[5].content == {"ruby": True}
        assert nodes[5].start is False

    def test_timestamp_tag(self):
        from pycaption.webvtt import microseconds

        nodes = self.reader._parse_cue_text("text <00:01:23.456> more")
        ts_nodes = [
            n for n in nodes
            if n.type_ == 2 and "timestamp" in n.content
        ]
        assert len(ts_nodes) == 1
        assert ts_nodes[0].content["timestamp"] == microseconds(0, 1, 23, 456)
        assert ts_nodes[0].start is True

    def test_timestamp_tag_without_hours(self):
        from pycaption.webvtt import microseconds

        nodes = self.reader._parse_cue_text("text <01:23.456> more")
        ts_nodes = [
            n for n in nodes
            if n.type_ == 2 and "timestamp" in n.content
        ]
        assert len(ts_nodes) == 1
        assert ts_nodes[0].content["timestamp"] == microseconds(0, 1, 23, 456)

    def test_entity_decoding_in_text(self):
        nodes = self.reader._parse_cue_text("A &amp; B &lt;C&gt;")
        assert len(nodes) == 1
        assert nodes[0].content == "A & B <C>"

    def test_plain_text_no_tags(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("No tags here")
        assert len(nodes) == 1
        assert nodes[0].type_ == CaptionNode.TEXT
        assert nodes[0].content == "No tags here"

    def test_unrecognized_angle_brackets_preserved(self):
        nodes = self.reader._parse_cue_text("<LAUGHING & WHOOPS!>")
        assert len(nodes) == 1
        assert nodes[0].content == "<LAUGHING & WHOOPS!>"

    def test_voice_tag_still_baked_into_text(self):
        nodes = self.reader._parse_cue_text("<v Roger>Hello</v>")
        text_nodes = [n for n in nodes if n.type_ == 1]
        combined = "".join(n.content for n in text_nodes)
        assert "Roger: " in combined
        assert "Hello" in combined

    def test_full_caption_read_with_styles(
        self, sample_webvtt_with_inline_style
    ):
        from pycaption.base import CaptionNode

        captions = self.reader.read(sample_webvtt_with_inline_style)
        cues = captions.get_captions("en-US")
        assert len(cues) == 3

        # First cue: "Hello <i>world</i>"
        nodes = cues[0].nodes
        text_nodes = [n for n in nodes if n.type_ == CaptionNode.TEXT]
        style_nodes = [n for n in nodes if n.type_ == CaptionNode.STYLE]
        assert any(n.content == "Hello " for n in text_nodes)
        assert any(n.content == "world" for n in text_nodes)
        assert any(
            n.content == {"italics": True} and n.start is True
            for n in style_nodes
        )
        assert any(
            n.content == {"italics": True} and n.start is False
            for n in style_nodes
        )

    def test_full_caption_read_with_structural_tags(
        self, sample_webvtt_with_structural_tags
    ):
        from pycaption.base import CaptionNode

        captions = self.reader.read(sample_webvtt_with_structural_tags)
        cues = captions.get_captions("en-US")
        assert len(cues) == 4

        # First cue: "<c.yellow>colored text</c>"
        nodes = cues[0].nodes
        style_nodes = [n for n in nodes if n.type_ == CaptionNode.STYLE]
        assert style_nodes[0].content == {"classes": ["yellow"]}
        assert style_nodes[0].start is True

        # Second cue: "<lang fr>Bonjour le monde</lang>"
        nodes = cues[1].nodes
        style_nodes = [n for n in nodes if n.type_ == CaptionNode.STYLE]
        assert style_nodes[0].content == {"lang": "fr"}
        assert style_nodes[0].start is True

    def test_multiline_cue_with_style_spanning_lines(self):
        from pycaption.base import CaptionNode

        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<i>line one\nline two</i>\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        nodes = cue.nodes
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"italics": True}
        assert nodes[0].start is True
        assert nodes[1].type_ == CaptionNode.TEXT
        assert nodes[1].content == "line one"
        assert nodes[2].type_ == CaptionNode.BREAK
        assert nodes[3].type_ == CaptionNode.TEXT
        assert nodes[3].content == "line two"
        assert nodes[4].type_ == CaptionNode.STYLE
        assert nodes[4].content == {"italics": True}
        assert nodes[4].start is False

    def test_tag_with_class_on_known_style_tag(self):
        from pycaption.base import CaptionNode

        nodes = self.reader._parse_cue_text("<i.highlight>text</i>")
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"italics": True}
        assert nodes[0].start is True
        assert nodes[1].type_ == CaptionNode.TEXT
        assert nodes[1].content == "text"
        assert nodes[2].type_ == CaptionNode.STYLE
        assert nodes[2].content == {"italics": True}
        assert nodes[2].start is False

    def test_empty_cue_text(self):
        nodes = self.reader._parse_cue_text("")
        assert nodes == []

    def test_whitespace_only_cue_text(self):
        nodes = self.reader._parse_cue_text("   ")
        assert nodes == []

    def test_adjacent_different_style_tags(self):
        nodes = self.reader._parse_cue_text(
            "<i>italic</i><b>bold</b><u>underline</u>"
        )
        assert len(nodes) == 9
        assert nodes[0].content == {"italics": True}
        assert nodes[0].start is True
        assert nodes[1].content == "italic"
        assert nodes[2].content == {"italics": True}
        assert nodes[2].start is False
        assert nodes[3].content == {"bold": True}
        assert nodes[3].start is True
        assert nodes[4].content == "bold"
        assert nodes[5].content == {"bold": True}
        assert nodes[5].start is False
        assert nodes[6].content == {"underline": True}
        assert nodes[6].start is True
        assert nodes[7].content == "underline"
        assert nodes[8].content == {"underline": True}
        assert nodes[8].start is False

    def test_unclosed_tag_auto_closed_at_cue_end(self):
        from pycaption.base import CaptionNode

        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<i>no close\n"
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        nodes = cue.nodes
        assert nodes[0].type_ == CaptionNode.STYLE
        assert nodes[0].content == {"italics": True}
        assert nodes[0].start is True
        assert nodes[1].type_ == CaptionNode.TEXT
        assert nodes[1].content == "no close"
        # Auto-closed at cue end
        assert nodes[2].type_ == CaptionNode.STYLE
        assert nodes[2].content == {"italics": True}
        assert nodes[2].start is False

    def test_multiple_unclosed_tags_closed_in_reverse_order(self):
        from pycaption.base import CaptionNode

        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i>text\n"
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        nodes = cue.nodes
        # open bold, open italic, text, auto-close italic, auto-close bold
        assert nodes[0].content == {"bold": True}
        assert nodes[0].start is True
        assert nodes[1].content == {"italics": True}
        assert nodes[1].start is True
        assert nodes[2].content == "text"
        assert nodes[3].content == {"italics": True}
        assert nodes[3].start is False
        assert nodes[4].content == {"bold": True}
        assert nodes[4].start is False

    def test_partially_closed_tags_only_unclosed_auto_closed(self):
        from pycaption.base import CaptionNode

        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i>text</i>\n"
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        nodes = cue.nodes
        # open bold, open italic, text, close italic, auto-close bold
        assert nodes[0].content == {"bold": True}
        assert nodes[0].start is True
        assert nodes[1].content == {"italics": True}
        assert nodes[1].start is True
        assert nodes[2].content == "text"
        assert nodes[3].content == {"italics": True}
        assert nodes[3].start is False
        assert nodes[4].content == {"bold": True}
        assert nodes[4].start is False

    def test_unclosed_tag_spanning_multiline_cue(self):
        from pycaption.base import CaptionNode

        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<i>line one\nline two\n"
        )
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        nodes = cue.nodes
        assert nodes[0].content == {"italics": True}
        assert nodes[0].start is True
        assert nodes[1].content == "line one"
        assert nodes[2].type_ == CaptionNode.BREAK
        assert nodes[3].content == "line two"
        # Auto-closed at cue end
        assert nodes[4].content == {"italics": True}
        assert nodes[4].start is False


class TestWebVTTCueSettingsParsing:
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_position_and_line_percent(
        self, sample_webvtt_with_position_and_line
    ):
        captions = self.reader.read(
            sample_webvtt_with_position_and_line
        )
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.origin is not None
        assert layout.origin.x == Size(50, UnitEnum.PERCENT)
        assert layout.origin.y == Size(75, UnitEnum.PERCENT)

    def test_line_integer_positive(self, sample_webvtt_with_line_integer):
        captions = self.reader.read(sample_webvtt_with_line_integer)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.origin is not None
        assert layout.origin.y == Size(20.0, UnitEnum.PERCENT)

    def test_line_integer_negative(self, sample_webvtt_with_line_integer):
        captions = self.reader.read(sample_webvtt_with_line_integer)
        cue = captions.get_captions("en-US")[1]
        layout = cue.layout_info

        expected_pct = (15 + (-1)) / 15 * 100  # ~93.33
        assert layout.origin is not None
        assert layout.origin.y.unit == UnitEnum.PERCENT
        assert abs(layout.origin.y.value - expected_pct) < 0.01

    def test_size_percent(self, sample_webvtt_with_size_and_align):
        captions = self.reader.read(sample_webvtt_with_size_and_align)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.extent is not None
        assert layout.extent.horizontal == Size(80, UnitEnum.PERCENT)

    def test_align_center(self, sample_webvtt_with_size_and_align):
        captions = self.reader.read(sample_webvtt_with_size_and_align)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.alignment is not None
        assert layout.alignment.horizontal == HorizontalAlignmentEnum.CENTER

    def test_vertical_rl(self, sample_webvtt_with_vertical):
        captions = self.reader.read(sample_webvtt_with_vertical)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.writing_direction == WritingDirectionEnum.VERTICAL_RL

    def test_combined_settings(self, sample_webvtt_with_combined_settings):
        captions = self.reader.read(sample_webvtt_with_combined_settings)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.origin.x == Size(10, UnitEnum.PERCENT)
        assert layout.origin.y == Size(80, UnitEnum.PERCENT)
        assert layout.extent.horizontal == Size(60, UnitEnum.PERCENT)
        assert layout.alignment.horizontal == HorizontalAlignmentEnum.START

    def test_raw_string_preserved(self, sample_webvtt_with_combined_settings):
        captions = self.reader.read(sample_webvtt_with_combined_settings)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        expected = "position:10% line:80% size:60% align:start"
        assert layout.webvtt_positioning == expected

    def test_position_only_no_origin(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000 position:50%\nHello\n"
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.origin is None
        assert layout.webvtt_positioning == "position:50%"

    def test_region_with_cue_override(self):
        vtt = """\
WEBVTT

REGION
id:region1
width:50%
viewportanchor:25%,75%
regionanchor:0%,0%

00:00:01.000 --> 00:00:03.000 region:region1 align:end
Hello
"""
        captions = self.reader.read(vtt)
        cue = captions.get_captions("en-US")[0]
        layout = cue.layout_info

        assert layout.alignment.horizontal == HorizontalAlignmentEnum.END
        assert layout.origin is not None


class TestWebVTTStyleBlockParsing:
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_class_style_parsed(self, sample_webvtt_with_style_block_class):
        captions = self.reader.read(sample_webvtt_with_style_block_class)
        styles = dict(captions.get_styles())

        assert "yellow" in styles
        assert styles["yellow"] == {"color": "yellow"}

    def test_base_style_parsed(self, sample_webvtt_with_style_block_base):
        captions = self.reader.read(sample_webvtt_with_style_block_base)
        styles = dict(captions.get_styles())

        assert "::cue" in styles
        assert styles["::cue"] == {
            "color": "white", "background-color": "black"
        }

    def test_multiple_properties(self, sample_webvtt_with_style_and_class_span):
        captions = self.reader.read(sample_webvtt_with_style_and_class_span)
        styles = dict(captions.get_styles())

        assert "yellow" in styles
        assert styles["yellow"] == {"color": "yellow", "italics": True}

    def test_cascade_specificity(self, sample_webvtt_with_style_block_cascade):
        captions = self.reader.read(sample_webvtt_with_style_block_cascade)
        cue = captions.get_captions("en-US")[0]

        for node in cue.nodes:
            if node.type_ == CaptionNode.STYLE and node.start:
                assert node.content.get("color") == "red"
                break

    def test_base_style_applied_to_all_classes(
        self, sample_webvtt_with_style_block_cascade
    ):
        captions = self.reader.read(sample_webvtt_with_style_block_cascade)
        cue = captions.get_captions("en-US")[1]

        for node in cue.nodes:
            if node.type_ == CaptionNode.STYLE and node.start:
                assert node.content.get("color") == "white"
                break

    def test_class_resolved_into_node(
        self, sample_webvtt_with_style_block_class
    ):
        captions = self.reader.read(
            sample_webvtt_with_style_block_class
        )
        cue = captions.get_captions("en-US")[0]

        for node in cue.nodes:
            if node.type_ == CaptionNode.STYLE and node.start:
                assert "color" in node.content
                assert node.content["color"] == "yellow"
                assert node.content["classes"] == ["yellow"]
                break

    def test_tag_selector_ignored(
        self, sample_webvtt_with_style_block_tag_selector
    ):
        captions = self.reader.read(
            sample_webvtt_with_style_block_tag_selector
        )
        styles = dict(captions.get_styles())

        assert "b" not in styles
        assert "::cue(b)" not in styles
