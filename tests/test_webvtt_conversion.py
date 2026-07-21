import re

from pycaption import (
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
        self.assert_dfxp_equals(
            sample_dfxp, results, ignore_styling=True, ignore_spans=True
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
        assert "<00:02.500>" in result
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
        assert "font-style:italic" in result

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
