import re
from xml.etree import ElementTree

from pycaption import (
    DFXPReader,
    DFXPWriter,
    MicroDVDWriter,
    SAMIReader,
    SAMIWriter,
    SCCReader,
    SRTReader,
    SRTWriter,
    WebVTTReader,
    WebVTTWriter,
)
from pycaption.base import Caption, CaptionList, CaptionNode, CaptionSet
from pycaption.geometry import (
    Alignment,
    HorizontalAlignmentEnum,
    Layout,
    Point,
    Size,
    UnitEnum,
    VerticalAlignmentEnum,
)
from tests.mixins import DFXPTestingMixIn, MicroDVDTestingMixIn, WebVTTTestingMixIn


class TestSAMItoWebVTT(WebVTTTestingMixIn):
    def test_conversion(self, sample_webvtt_from_sami, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = WebVTTWriter(video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami, results)

    def test_style_tags_conversion(
        self, sample_webvtt_from_sami_with_style, sample_sami_with_style_tags
    ):
        caption_set = SAMIReader().read(sample_sami_with_style_tags)
        results = WebVTTWriter(video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_style, results)

    def test_css_inline_style_conversion(
        self, sample_webvtt_from_sami_with_style, sample_sami_with_css_inline_style
    ):
        caption_set = SAMIReader().read(sample_sami_with_css_inline_style)
        results = WebVTTWriter(video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_style, results)

    def test_css_id_style_conversion(
        self, sample_webvtt_from_sami_with_id_style, sample_sami_with_css_id_style
    ):
        caption_set = SAMIReader().read(sample_sami_with_css_id_style)
        results = WebVTTWriter(video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_id_style, results)


class TestSRTtoWebVTT(WebVTTTestingMixIn):
    def test_srt_to_webvtt_conversion(self, sample_webvtt_from_srt, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_srt, results)


class TestWebVTTtoWebVTT(WebVTTTestingMixIn):
    def test_webvtt_to_webvtt_conversion(
        self, sample_webvtt_from_webvtt, sample_webvtt
    ):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_webvtt, results)

    def test_cue_settings_are_kept(self, sample_webvtt_with_cue_settings):
        caption_set = WebVTTReader().read(sample_webvtt_with_cue_settings)

        webvtt = WebVTTWriter().write(caption_set)

        assert sample_webvtt_with_cue_settings == webvtt

    def test_positioning_is_kept(self, sample_webvtt_keeps_positioning):
        caption_set = WebVTTReader().read(sample_webvtt_keeps_positioning)
        results = WebVTTWriter().write(caption_set)

        assert sample_webvtt_keeps_positioning == results

    def test_output_timestamps(self, sample_webvtt_timestamps):
        expected_timestamp_line_pattern = re.compile(
            r"^(\d{2,}):(\d{2})(:\d{2})?\.(\d{3}) "
            r"--> (\d{2,}):(\d{2})(:\d{2})?\.(\d{3})"
        )

        caption_set = WebVTTReader().read(sample_webvtt_timestamps)
        results = WebVTTWriter().write(caption_set).splitlines()

        assert re.match(expected_timestamp_line_pattern, results[2])
        assert re.match(expected_timestamp_line_pattern, results[5])


#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class TestWebVTTtoDFXP(DFXPTestingMixIn):
    def test_conversion(self, sample_dfxp, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = DFXPWriter().write(caption_set)

        assert isinstance(results, str)
        assert 'tts:textAlign="center"' in results

        expected = sample_dfxp.replace(
            'tts:textAlign="start"', 'tts:textAlign="center"'
        )
        self.assert_dfxp_equals(
            expected, results, ignore_styling=True, ignore_spans=True
        )


class TestWebVTTtoMicroDVD(MicroDVDTestingMixIn):
    def test_webvtt_to_microdvd_conversion(self, sample_microdvd, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd, results)


class TestWebVTTInlineMarkupRoundTrip:
    def test_italic_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nHello <i>world</i>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<i>world</i>" in result

    def test_bold_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b>bold</b> text\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<b>bold</b>" in result

    def test_underline_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<u>underlined</u>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<u>underlined</u>" in result

    def test_nested_style_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i>both</i></b>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<b><i>both</i></b>" in result

    def test_class_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "<c.yellow>colored</c>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<c.yellow>colored</c>" in result

    def test_lang_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "<lang fr>Bonjour</lang>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<lang fr>Bonjour</lang>" in result

    def test_ruby_roundtrip(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<ruby>base<rt>annotation</rt></ruby>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<ruby>base<rt>annotation</rt></ruby>" in result

    def test_timestamp_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\n" "Hello <00:00:02.500>world\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<00:00:02.500>" in result
        assert "Hello" in result
        assert "world" in result

    def test_mixed_style_and_text_roundtrip(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "Normal <i>italic</i> <b>bold</b> end\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "Normal <i>italic</i> <b>bold</b> end" in result

    def test_multiline_style_spanning_lines_roundtrip(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "<i>line one\nline two</i>\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<i>line one\nline two</i>" in result

    def test_unrecognized_tag_preserved_roundtrip(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "He said <LAUGHING> something\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "LAUGHING" in result
        assert "He said" in result
        assert "something" in result

    def test_writer_encodes_illegal_characters(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "A &amp; B &lt; C\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "A &amp; B &lt; C" in result

        assert WebVTTWriter._encode_illegal_characters("-->") == "--&gt;"

    def test_writer_encodes_entities_nbsp_lrm_rlm(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "word gap ‎ltr ‏rtl\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "word&nbsp;gap" in result
        assert "&lrm;ltr" in result
        assert "&rlm;rtl" in result

    def test_writer_timestamp_always_has_hours(self):
        vtt = "WEBVTT\n\n00:01.000 --> 00:05.000\nShort\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        lines = result.strip().splitlines()
        timing_line = next(line for line in lines if "-->" in line)
        parts = timing_line.split(" --> ")
        for ts in parts:
            ts_clean = ts.split()[0]
            assert re.match(
                r"\d{2}:\d{2}:\d{2}\.\d{3}$", ts_clean
            ), f"Timestamp {ts_clean} missing hours component"


class TestWebVTTStyleCrossFormat:
    def test_italic_to_dfxp(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<i>italic</i>\n"
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)
        assert 'tts:fontStyle="italic"' in result

    def test_italic_to_sami(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<i>italic</i>\n"
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)
        assert "<i>" in result and "</i>" in result

    def test_italic_to_srt(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<i>italic</i>\n"
        caption_set = WebVTTReader().read(vtt)
        result = SRTWriter().write(caption_set)
        assert "italic" in result
        assert "<i>" not in result

    def test_structural_tags_stripped_in_srt(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "<c.yellow>Hello</c>\n"
        caption_set = WebVTTReader().read(vtt)
        result = SRTWriter().write(caption_set)
        assert "<c" not in result
        assert "Hello" in result

    def test_structural_tags_stripped_in_dfxp(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n" "<lang fr>Bonjour</lang>\n"
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)
        assert "<lang" not in result
        assert "Bonjour" in result

    def test_structural_tags_produce_well_formed_dfxp(
        self, sample_webvtt_with_structural_tags
    ):
        caption_set = WebVTTReader().read(sample_webvtt_with_structural_tags)
        result = DFXPWriter().write(caption_set)

        ElementTree.fromstring(result)


class TestWebVTTCueSettingsConversion:
    def test_cue_settings_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 position:50% line:80% align:center\n"
            "Hello world\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert "tts:origin" in result
        assert "tts:textAlign" in result

    def test_cue_settings_to_dfxp_text_align(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 line:50% align:end\n"
            "Hello world\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert "end" in result

    def test_vtt_roundtrip_preserves_positioning(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 position:50% line:80% align:center\n"
            "Hello world\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)

        assert "position:50% line:80% align:center" in result

    def test_line_alignment_center_to_dfxp(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:50%,center\n" "Hello\n"
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:displayAlign="center"' in result

    def test_line_alignment_vtt_non_passthrough_roundtrip(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:80%,center\n" "Hello\n"
        caption_set = WebVTTReader().read(vtt)
        for caption in caption_set.get_captions("en-US"):
            caption.layout_info.webvtt_positioning = None
        result = WebVTTWriter().write(caption_set)

        assert "line:80%,center" in result

    def test_line_alignment_absent_no_qualifier_in_vtt_output(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:80%\n" "Hello\n"
        caption_set = WebVTTReader().read(vtt)
        for caption in caption_set.get_captions("en-US"):
            caption.layout_info.webvtt_positioning = None
        result = WebVTTWriter().write(caption_set)

        assert "line:80%" in result
        assert "line:80%," not in result

    def test_style_block_to_sami_no_invalid_selector(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>Hello world</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert ".::cue" not in result
        assert "yellow" in result.lower()

    def test_style_class_to_sami(self, sample_webvtt_with_style_block_class):
        caption_set = WebVTTReader().read(sample_webvtt_with_style_block_class)
        result = SAMIWriter().write(caption_set)

        assert "yellow" in result.lower()

    def test_style_block_to_dfxp_valid_xml(self, sample_webvtt_with_style_block_class):
        from lxml import etree

        caption_set = WebVTTReader().read(sample_webvtt_with_style_block_class)
        result = DFXPWriter().write(caption_set)

        etree.fromstring(result.encode("utf-8"))
        assert "::cue" not in result

    def test_style_class_to_webvtt_preserves_tag(
        self, sample_webvtt_with_style_block_class
    ):
        caption_set = WebVTTReader().read(sample_webvtt_with_style_block_class)
        result = WebVTTWriter().write(caption_set)

        assert "<c.yellow>" in result


class TestWebVTTWriterStyleBlocks:
    def test_style_block_roundtrip(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>Hello world</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)

        assert "STYLE\n" in result
        assert "::cue(.yellow)" in result
        assert "color: yellow" in result

    def test_global_cue_style_roundtrip(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>Hello</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)

        style_section = result.split("\n\n")[1]
        lines = style_section.strip().split("\n")
        assert lines[0] == "STYLE"
        assert "::cue {" in lines[1]
        assert "::cue(.yellow)" in lines[2]

    def test_writing_direction_from_layout(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:rl line:50%\n"
            "Hello vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        lang = caption_set.get_languages()[0]
        captions = caption_set.get_captions(lang)
        captions[0].layout_info.webvtt_positioning = None

        result = WebVTTWriter().write(caption_set)

        assert "vertical:rl" in result

    def test_no_duplicate_vertical_with_passthrough(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:rl line:50%\n"
            "Hello vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)

        assert result.count("vertical:rl") == 1

    def test_no_style_block_when_no_styles(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "Plain text\n"
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)

        assert "STYLE" not in result

    def test_sami_lang_style_not_emitted(self):
        sami = (
            '<sami><head><style type="text/css">\n'
            "<!--\n"
            ".en { lang: en-US; color: white; }\n"
            "-->\n"
            "</style></head><body>\n"
            '<sync start="1000"><p class="en">Hello</p></sync>\n'
            "</body></sami>"
        )
        caption_set = SAMIReader().read(sami)
        result = WebVTTWriter().write(caption_set)

        assert "::cue(.en)" not in result
        assert "STYLE" not in result

    def test_scc_to_vtt_no_style_block(self):
        scc = (
            "Scenarist_SCC V1.0\n\n"
            "00:00:00:13\t94ae 94ae 9420 9420 9470 9470 "
            "c8e5 ecec ef80 942c 942c 942f 942f\n\n"
            "00:00:02:29\t942c 942c\n\n"
        )
        caption_set = SCCReader().read(scc)
        result = WebVTTWriter().write(caption_set)

        assert "STYLE" not in result
        assert "Hello" in result


class TestWebVTTtoDFXPWritingDirection:
    def test_vertical_rl_to_dfxp_writing_mode(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:rl line:50%\n"
            "Hello vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:writingMode="tbrl"' in result

    def test_vertical_lr_to_dfxp_writing_mode(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:lr line:50%\n"
            "Hello vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:writingMode="tblr"' in result

    def test_vertical_only_creates_region(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:rl\n"
            "Hello vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:writingMode="tbrl"' in result
        assert "region" in result

    def test_combined_positioning_and_writing_direction(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 vertical:rl position:25% line:10%\n"
            "Positioned vertical\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:writingMode="tbrl"' in result
        assert "tts:origin" in result

    def test_horizontal_omits_writing_mode(self):
        vtt = (
            "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:50%\n" "Hello horizontal\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert "tts:writingMode" not in result


class TestWebVTTtoDFXPStyles:
    def test_background_color_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.bg) { background-color: black }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.bg>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:backgroundColor="black"' in result

    def test_bold_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.strong) { font-weight: bold }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.strong>Bold text</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontWeight="bold"' in result

    def test_underline_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.uline) { text-decoration: underline }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.uline>Underlined text</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:textDecoration="underline"' in result

    def test_font_family_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.fancy) { font-family: Arial }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.fancy>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontFamily="Arial"' in result

    def test_quoted_font_family_to_valid_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            '::cue(.fancy) { font-family: "Helvetica Neue", Arial, sans-serif }\n\n'
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.fancy>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontFamily="Helvetica Neue, Arial, sans-serif"' in result
        from lxml import etree

        etree.fromstring(result.encode("utf-8"))

    def test_font_size_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.big) { font-size: 120% }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.big>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontSize="120%"' in result

    def test_text_shadow_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.shadow) { text-shadow: 2px 2px 4px black }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.shadow>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:textOutline="black 4px"' in result

    def test_text_shadow_no_blur_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.shadow) { text-shadow: 1px 1px black }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.shadow>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:textOutline="black 1px"' in result

    def test_opacity_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.faded) { opacity: 0.8 }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.faded>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:opacity="0.8"' in result

    def test_line_height_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.spaced) { line-height: 1.5 }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.spaced>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:lineHeight="1.5"' in result

    def test_compound_selector_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.bold.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.bold.yellow>Hello styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:color="yellow"' in result

    def test_classes_not_in_dfxp_output(self):
        from lxml import etree

        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>Colored text</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        etree.fromstring(result.encode("utf-8"))
        assert "classes" not in result


class TestNestedSpanSupport:
    def test_nested_bold_italic_to_dfxp(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i>both</i></b>\n"
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontWeight="bold"' in result
        assert 'tts:fontStyle="italic"' in result
        assert "both" in result

    def test_nested_bold_italic_to_sami(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i>both</i></b>\n"
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "<b>" in result and "</b>" in result
        assert "<i>" in result and "</i>" in result
        assert "both" in result

    def test_nested_class_and_italic_to_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow><i>styled</i></c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:color="yellow"' in result
        assert 'tts:fontStyle="italic"' in result
        assert "styled" in result

    def test_nested_class_and_italic_to_sami(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.yellow) { color: yellow }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow><i>styled</i></c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert 'class="yellow"' in result
        assert "<i>" in result and "</i>" in result
        assert "styled" in result

    def test_triple_nesting_to_dfxp(self):
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n<b><i><u>all</u></i></b>\n"
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:fontWeight="bold"' in result
        assert 'tts:fontStyle="italic"' in result
        assert 'tts:textDecoration="underline"' in result
        assert "all" in result


class TestGlobalCueColorPropagation:
    def test_global_color_reaches_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Plain text\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:color="white"' in result
        assert "Plain text" in result

    def test_global_color_reaches_sami(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Plain text\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "color:white;" in result
        assert "Plain text" in result

    def test_global_background_color_reaches_dfxp(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { background-color: black }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Text on black\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)

        assert 'tts:backgroundColor="black"' in result

    def test_class_override_not_double_wrapped(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue { color: white }\n"
            "::cue(.highlight) { color: red }\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.highlight>Highlighted</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        nodes = caption_set.get_captions("en-US")[0].nodes
        from pycaption.base import CaptionNode

        style_opens = [n for n in nodes if n.type_ == CaptionNode.STYLE and n.start]
        assert len(style_opens) == 1
        assert style_opens[0].content.get("color") == "red"


class TestYouTubeKaraokeEmptyClassRoundtrip:
    def test_empty_class_vtt_to_sami_roundtrip(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "<c> Hello</c><c> world</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        sami_output = SAMIWriter().write(caption_set)

        assert 'class=""' not in sami_output
        assert "Hello" in sami_output
        assert "world" in sami_output

        reread_set = SAMIReader().read(sami_output)
        captions = reread_set.get_captions(reread_set.get_languages()[0])
        assert len(captions) == 1
        text = captions[0].get_text()
        assert "Hello" in text
        assert "world" in text


class TestMultipleLayoutsPerCaption:
    """A Caption whose nodes carry different layout_info must become one
    valid, independent cue per layout — same timing, different placement."""

    LAYOUT_A = Layout(
        origin=Point(Size(35, UnitEnum.PERCENT), Size(77, UnitEnum.PERCENT)),
        alignment=Alignment(HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP),
    )
    LAYOUT_B = Layout(
        origin=Point(Size(30, UnitEnum.PERCENT), Size(89, UnitEnum.PERCENT)),
        alignment=Alignment(HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP),
    )

    @staticmethod
    def _write(nodes, style=None):
        caption = Caption(1000000, 2000000, nodes, style=style or {})
        caption_set = CaptionSet({"en-US": CaptionList([caption])})
        return WebVTTWriter().write(caption_set)

    @classmethod
    def _cues(cls, nodes, style=None):
        """Return [(cue_settings, [text_line, ...]), ...] for the nodes."""
        return cls._split_cues(cls._write(nodes, style))

    @staticmethod
    def _split_cues(webvtt):
        """Return [(cue_settings, [text_line, ...]), ...] for VTT output."""
        blocks = [
            block
            for block in webvtt.split("WEBVTT\n\n", 1)[1].split("\n\n")
            if block.strip()
        ]
        cues = []
        for block in blocks:
            lines = block.strip("\n").split("\n")
            assert lines[0].count("-->") == 1, f"fused cues in block: {block!r}"
            cues.append((lines[0], lines[1:]))
        return cues

    @staticmethod
    def _italics(is_start, layout):
        return CaptionNode.create_style(is_start, {"italics": True}, layout_info=layout)

    @staticmethod
    def _underline(is_start, layout):
        return CaptionNode.create_style(
            is_start, {"underline": True}, layout_info=layout
        )

    def test_independent_italic_spans_split_into_two_cues(self):
        """The reported repro: an italic span on each side of the boundary."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("Come on", layout_info=self.LAYOUT_A),
                self._italics(False, self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                self._italics(True, self.LAYOUT_B),
                CaptionNode.create_text("Let's go!", layout_info=self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert "position:35% line:77%" in cues[0][0]
        assert "position:30% line:89%" in cues[1][0]
        assert cues[0][1] == ["<i>Come on</i>"]
        assert cues[1][1] == ["<i>Let's go!</i>"]

    def test_closing_tag_stays_with_its_opening_tag_group(self):
        """A closing tag placed after the next group's text must still
        close the span it opened, rather than following the text next to
        it into the second cue and leaving both cues unbalanced."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("Ha", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("there", layout_info=self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>Ha</i>"]
        assert cues[1][1] == ["there"]
        for _, lines in cues:
            text = "".join(lines)
            assert text.count("<i>") == text.count("</i>")

    def test_crossed_spans_each_close_their_own_tag(self):
        """Overlapping spans — <i>a<u>b</i></u> — pair by tag identity.
        Pairing by stack position hands each closing tag the other span's
        group, so both cues close a tag they never opened."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("a", layout_info=self.LAYOUT_A),
                self._underline(True, self.LAYOUT_B),
                CaptionNode.create_text("b", layout_info=self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
                self._underline(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>a</i>"]
        assert cues[1][1] == ["<u>b</u>"]

    def test_mid_cue_timestamp_does_not_consume_a_closing_tag(self):
        """A karaoke timestamp opens with no closing counterpart — the
        shape WebVTTReader gives <00:00:01.500>. Keyed on stack position it
        took a slot, so the next closing tag inherited its group and left
        the italic span unclosed."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("a", layout_info=self.LAYOUT_A),
                CaptionNode.create_style(
                    True, {"timestamp": 1500000}, layout_info=self.LAYOUT_B
                ),
                CaptionNode.create_text("b", layout_info=self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>a</i>"]
        assert cues[1][1] == ["<00:00:01.500>b"]

    def test_nested_dfxp_spans_pair_innermost_first(self):
        """Nested spans sharing keys but not values pair innermost-first,
        which searching from the top of the stack buys. DFXPReader gives
        both spans the key set {'classes', 'class'}, and each closing tag
        renders from its own style — </i> outer, </b> inner."""
        dfxp = """<?xml version="1.0" encoding="utf-8"?>
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="it" tts:fontStyle="italic"/>
   <style xml:id="bo" tts:fontWeight="bold"/>
  </styling>
  <layout>
   <region xml:id="top" tts:origin="10% 10%" tts:extent="80% 20%"/>
   <region xml:id="bottom" tts:origin="10% 70%" tts:extent="80% 20%"/>
  </layout>
 </head>
 <body><div>
  <p begin="00:00:01.000" end="00:00:03.000" region="bottom"><span
    style="it">x<span style="bo" region="top">y</span></span></p>
 </div></body>
</tt>
"""
        caption_set = DFXPReader().read(dfxp)
        cues = self._split_cues(
            WebVTTWriter(video_width=640, video_height=360).write(caption_set)
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>x</i>"]
        assert cues[1][1] == ["<b>y</b>"]

    def test_class_span_pairs_on_its_keys_not_its_value(self):
        """A class span's open and close nodes share a key but not a value
        — WebVTTReader gives <c.loud> {'classes': ['loud']} and </c>
        {'classes': []}. Pairing on whole content finds no match for </c>,
        which then closes the italic span instead."""
        cues = self._cues(
            [
                CaptionNode.create_style(
                    True, {"classes": ["loud"]}, layout_info=self.LAYOUT_A
                ),
                CaptionNode.create_text("x", layout_info=self.LAYOUT_A),
                self._italics(True, self.LAYOUT_B),
                CaptionNode.create_text("y", layout_info=self.LAYOUT_B),
                CaptionNode.create_style(
                    False, {"classes": []}, layout_info=self.LAYOUT_B
                ),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<c.loud>x</c>"]
        assert cues[1][1] == ["<i>y</i>"]

    def test_closing_tag_with_no_opener_resolves_to_a_group(self):
        """A closing tag with no opener cannot be balanced. The guarantee
        is only that it lands in a group instead of raising, and that the
        text around it survives."""
        cues = self._cues(
            [
                CaptionNode.create_text("x", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("y", layout_info=self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["x"]
        assert cues[1][1] == ["y</i>"]

    def test_closing_tag_with_no_opener_spares_an_open_span(self):
        """A closing tag with no opener must not take an open span's slot.
        Popping the stack top leaves the italic span's own </i> unmatched
        in turn, spreading one stray tag over both cues."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("a", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("b", layout_info=self.LAYOUT_B),
                self._underline(False, self.LAYOUT_B),
                self._italics(False, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>a</i>"]
        assert cues[1][1] == ["b</u>"]

    def test_caption_style_does_not_swallow_the_boundary_newline(self):
        """A style on the whole Caption must not leave a cue whose last
        line is nothing but a closing tag."""
        cues = self._cues(
            [
                CaptionNode.create_text("Come on", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("Let's go!", layout_info=self.LAYOUT_B),
            ],
            style={"italics": True},
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>Come on</i>"]
        assert cues[1][1] == ["<i>Let's go!</i>"]
        for _, lines in cues:
            assert lines[-1] != "</i>"

    def test_first_text_node_without_layout_still_splits(self):
        """layout_info=None on the first text node must not collapse the
        split, which would make the caption adopt the second position."""
        cues = self._cues(
            [
                CaptionNode.create_text("Come on", layout_info=None),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("Let's go!", layout_info=self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["Come on"]
        assert cues[1][1] == ["Let's go!"]
        assert "position:30% line:89%" not in cues[0][0]
        assert "position:30% line:89%" in cues[1][0]

    def test_italic_line_wrap_emits_no_nbsp_guard(self):
        """A BREAK after a closing tag, with text earlier on the line, is
        an ordinary wrap and needs no guard. This is also the shape the
        caption-merging path in skylab produces when it joins two
        same-layout italic captions with a BREAK."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("Come on", layout_info=self.LAYOUT_A),
                self._italics(False, self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("second line", layout_info=self.LAYOUT_A),
            ]
        )

        assert len(cues) == 1
        assert cues[0][1] == ["<i>Come on</i>", "second line"]

    def test_line_of_only_tags_still_gets_the_nbsp_guard(self):
        """The line before a BREAK can hold tags and no text — an empty
        span between two breaks, which SAMI, DFXP and WebVTT input all
        produce. Looking past the tags has to stop at the earlier BREAK
        rather than reach the text on the line before it, or the line
        keeps no placeholder and collapses."""
        cues = self._cues(
            [
                CaptionNode.create_text("Line one", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                self._italics(True, self.LAYOUT_A),
                self._italics(False, self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("Line two", layout_info=self.LAYOUT_A),
            ]
        )

        assert len(cues) == 1
        assert cues[0][1] == ["Line one", "<i></i>&nbsp;", "Line two"]

    def test_break_behind_a_closing_tag_is_still_trailing(self):
        """A group can end with a BREAK sitting *before* the tag that
        closes a span over it. That break is still trailing, and leaving
        it in would make the cue's last line a bare closing tag."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("only line", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                self._italics(False, self.LAYOUT_A),
            ]
        )

        assert len(cues) == 1
        assert cues[0][1] == ["<i>only line</i>"]

    def test_whitespace_only_first_group_leaves_only_the_next_cue(self):
        """A leading blank group must not become a cue of its own at the
        blank group's position: it renders nothing there, and WebVTTReader
        drops it on the way back in, so it would survive no round trip.
        The surviving cue keeps the following group's layout."""
        cues = self._cues(
            [
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("Come on", layout_info=self.LAYOUT_B),
            ]
        )

        assert len(cues) == 1
        assert "position:30% line:89%" in cues[0][0]
        assert cues[0][1] == ["Come on"]

    def test_whitespace_only_last_group_leaves_only_the_previous_cue(self):
        """A trailing space left by a style code must not become a cue of
        its own at near-zero width, nor a trailing space on the cue that
        precedes it."""
        cues = self._cues(
            [
                self._italics(True, self.LAYOUT_A),
                CaptionNode.create_text("Ha.é!", layout_info=self.LAYOUT_A),
                self._italics(False, self.LAYOUT_A),
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_B),
            ]
        )

        assert len(cues) == 1
        assert "position:35% line:77%" in cues[0][0]
        assert cues[0][1] == ["<i>Ha.é!</i>"]

    def test_blank_group_holding_a_break_adds_no_line(self):
        """A blank group can hold a break of its own. Dropping the group
        has to take that break with it: the line the break would add is
        blank, and a caption-level style would then close itself on a
        line of its own."""
        cues = self._cues(
            [
                CaptionNode.create_text("first", layout_info=self.LAYOUT_A),
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_B),
                CaptionNode.create_break(layout_info=self.LAYOUT_B),
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_B),
                CaptionNode.create_text("second", layout_info=self.LAYOUT_A),
            ],
            style={"italics": True},
        )

        assert len(cues) == 2
        assert cues[0][1] == ["<i>first</i>"]
        assert cues[1][1] == ["<i>second</i>"]

    def test_trailing_break_leaves_no_blank_last_line(self):
        """Asserted on the raw output, since splitting on blank lines
        would hide the very trailing newline under test."""
        webvtt = self._write(
            [
                CaptionNode.create_text("only line", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
            ]
        )

        assert webvtt.endswith("\nonly line\n")

    def test_consecutive_trailing_breaks_are_all_dropped(self):
        """More than one break can end a group — each renders nothing at
        the end of a cue, so stopping after the first would leave a blank
        last line behind."""
        cues = self._cues(
            [
                CaptionNode.create_text("only line", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("next cue", layout_info=self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["only line"]
        assert cues[1][1] == ["next cue"]

    def test_caption_without_text_emits_no_cue(self):
        """A caption holding no text node is not a cue, in any of the
        shapes that can produce one: tags draw nothing on their own, and
        writing them would put markup on screen as the whole of a cue's
        content, while breaks with no text are trailing by definition and
        leave nothing behind once dropped."""
        assert self._write([CaptionNode.create_style(True, {})]) == "WEBVTT\n\n"
        assert (
            self._write(
                [self._italics(True, self.LAYOUT_A), self._italics(False, None)]
            )
            == "WEBVTT\n\n"
        )
        assert (
            self._write([CaptionNode.create_break(), CaptionNode.create_break()])
            == "WEBVTT\n\n"
        )

    def test_missing_node_layout_resolves_to_the_caption_position(self):
        """A text node without layout_info is placed at the caption's own
        position, so it belongs to that group rather than opening one of
        its own — which would emit two cues at the same position, drawn
        on top of each other."""
        caption = Caption(
            1000000,
            2000000,
            [
                CaptionNode.create_text("Come on", layout_info=None),
                CaptionNode.create_break(layout_info=None),
                CaptionNode.create_text("Let's go!", layout_info=self.LAYOUT_B),
            ],
            layout_info=self.LAYOUT_B,
        )
        webvtt = WebVTTWriter().write(CaptionSet({"en-US": CaptionList([caption])}))

        assert webvtt.count("-->") == 1
        assert webvtt.endswith("\nCome on\nLet's go!\n")

    def test_split_leaves_no_padding_and_round_trips_unchanged(self):
        """The text run before a layout change usually ends in the space
        that separated it from the next word. Across a cue boundary that
        space renders as nothing and WebVTTReader drops it, so leaving it
        in would only stop the output from being a fixed point."""
        webvtt = self._write(
            [
                CaptionNode.create_text("A ", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("new pair", layout_info=self.LAYOUT_B),
            ]
        )

        assert "\nA\n" in webvtt
        assert " \n" not in webvtt
        assert WebVTTWriter().write(WebVTTReader().read(webvtt)) == webvtt

    def test_padding_is_stripped_from_lines_inside_a_cue(self):
        """Every line of a cue is stripped, not just the cue's first and
        last: the space a line break leaves behind sits in the middle of
        the text, where a whole-cue strip would never reach it."""
        cues = self._cues(
            [
                CaptionNode.create_text("first ", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text(" second", layout_info=self.LAYOUT_A),
            ]
        )

        assert len(cues) == 1
        assert cues[0][1] == ["first", "second"]

    def test_line_emptied_by_stripping_keeps_a_placeholder(self):
        """A line of nothing but a space is blank once stripped, and an
        empty line inside cue text is the blank line that ends the cue —
        it would drop every line after it. The placeholder the guard uses
        for an empty line has to stand in here too."""
        cues = self._cues(
            [
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_A),
                CaptionNode.create_break(layout_info=self.LAYOUT_A),
                CaptionNode.create_text("visible", layout_info=self.LAYOUT_A),
            ]
        )

        assert len(cues) == 1
        assert cues[0][1] == ["&nbsp;", "visible"]

    def test_lone_blank_group_is_still_a_cue(self):
        """Dropping a blank group only makes sense against a group that
        survives it. A caption that is blank all through is a deliberately
        empty cue — an empty line in an SRT source — and has to keep its
        place in the timeline."""
        cues = self._cues([CaptionNode.create_text(" ", layout_info=self.LAYOUT_A)])

        assert len(cues) == 1
        assert cues[0][1] == ["&nbsp;"]

    def test_caption_blank_at_every_layout_is_still_one_cue(self):
        """Blankness spread over two layouts is the same deliberately
        empty cue as blankness at one, so the caption must not vanish for
        having been split. It keeps the first group's position, the one it
        would have had unsplit."""
        cues = self._cues(
            [
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_A),
                CaptionNode.create_text(" ", layout_info=self.LAYOUT_B),
            ]
        )

        assert len(cues) == 1
        assert "position:35% line:77%" in cues[0][0]
        assert cues[0][1] == ["&nbsp;"]

    def test_caption_with_no_cue_leaves_no_extra_blank_line(self):
        """A caption that renders to nothing must not contribute a cue
        separator either — the neighbouring cues would then be split by
        two blank lines instead of one."""
        webvtt = WebVTTWriter().write(
            CaptionSet(
                {
                    "en-US": CaptionList(
                        [
                            Caption(
                                1000000,
                                2000000,
                                [CaptionNode.create_text("one", layout_info=None)],
                            ),
                            Caption(3000000, 4000000, [CaptionNode.create_break()]),
                            Caption(
                                5000000,
                                6000000,
                                [CaptionNode.create_text("two", layout_info=None)],
                            ),
                        ]
                    )
                }
            )
        )

        assert webvtt.count("-->") == 2
        assert "\n\n\n" not in webvtt

    def test_dangling_opening_tag_stays_with_the_preceding_text(self):
        """An opening tag joins the text that follows it, but unbalanced
        input can leave it with none. It then belongs to the group of the
        text it was written after, not to the caption's first group, which
        it may have nothing to do with."""
        cues = self._cues(
            [
                CaptionNode.create_text("plain", layout_info=self.LAYOUT_A),
                CaptionNode.create_text("styled", layout_info=self.LAYOUT_B),
                self._italics(True, self.LAYOUT_B),
            ]
        )

        assert len(cues) == 2
        assert cues[0][1] == ["plain"]
        assert cues[1][1] == ["styled<i>"]

    def test_scc_mid_row_code_splits_into_two_parsable_cues(self):
        """End to end on the shape that occurs in real SCC: a mid-row
        italics code that also moves the column, leaving one Caption with
        two positions. This is the caption at 00:05:50.800 of
        examples/2000370803_Original_en.txt, which was emitted as a single
        fused block of two timing lines."""
        scc = (
            "Scenarist_SCC V1.0\n\n"
            "00:00:01:00\t9420 942f 94ae 9420 94f4 9723 c180 "
            "9476 91ae 7961 61f2 75e9 6ebf\n\n"
            "00:00:03:00\t9420 942f\n\n"
            "00:00:05:00\t942c\n\n"
        )
        webvtt = WebVTTWriter().write(SCCReader().read(scc))

        blocks = [
            block.strip("\n")
            for block in webvtt.split("WEBVTT\n\n", 1)[1].split("\n\n")
            if block.strip()
        ]
        assert [b.count("-->") for b in blocks] == [1, 1]
        assert blocks[0].split("\n")[1:] == ["A"]
        assert blocks[1].split("\n")[1:] == ["<i>yaaruin?</i>"]
        assert "position:37.5%" in blocks[0]
        assert "position:40%" in blocks[1]
        assert WebVTTWriter().write(WebVTTReader().read(webvtt)) == webvtt
