import re

from pycaption import (
    DFXPWriter,
    MicroDVDWriter,
    SAMIReader,
    SAMIWriter,
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
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>colored</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<c.yellow>colored</c>" in result

    def test_lang_roundtrip(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<lang fr>Bonjour</lang>\n"
        )
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
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:05.000\n"
            "Hello <00:00:02.500>world\n"
        )
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
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<i>line one\nline two</i>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = WebVTTWriter().write(caption_set)
        assert "<i>line one\nline two</i>" in result

    def test_unrecognized_tag_preserved_roundtrip(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "He said <LAUGHING> something\n"
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
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>Hello</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SRTWriter().write(caption_set)
        assert "<c" not in result
        assert "Hello" in result

    def test_structural_tags_stripped_in_dfxp(self):
        vtt = (
            "WEBVTT\n\n00:00:01.000 --> 00:00:03.000\n"
            "<lang fr>Bonjour</lang>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = DFXPWriter().write(caption_set)
        assert "<lang" not in result
        assert "Bonjour" in result
