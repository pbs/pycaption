from pycaption import DFXPReader, SAMIReader, SAMIWriter, SRTReader, WebVTTReader

from .mixins import SAMITestingMixIn

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class TestDFXPtoSAMI(SAMITestingMixIn):
    def setup_method(self):
        self.reader = DFXPReader()
        self.writer = SAMIWriter()

    def test_dfxp_to_sami_conversion(self, sample_sami, sample_dfxp):
        caption_set = self.reader.read(sample_dfxp)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami, result)

    def test_dfxp_to_sami_with_nested_spans(
        self, sample_sami_from_dfxp_with_nested_spans, sample_dfxp_with_nested_spans
    ):
        caption_set = self.reader.read(sample_dfxp_with_nested_spans)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami_from_dfxp_with_nested_spans, result)

    def test_dfxp_to_sami_with_margins(self, sample_dfxp_from_sami_with_margins):
        caption_set = self.reader.read(sample_dfxp_from_sami_with_margins)
        result = SAMIWriter(video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT).write(
            caption_set
        )
        margins = [
            "margin-right: 6.04%;",
            "margin-bottom: 0%;",
            "margin-top: 0%;",
            "margin-left: 6.04%;",
        ]

        assert all(margin in result for margin in margins)

    def test_dfxp_empty_cue_to_sami(
        self, sample_sami_empty_cue_output, sample_dfxp_empty_cue
    ):
        caption_set = self.reader.read(sample_dfxp_empty_cue)
        result = self.writer.write(caption_set)

        self.assert_sami_captions_equal(sample_sami_empty_cue_output, result)


class TestSRTtoSAMI(SAMITestingMixIn):
    def test_srt_to_sami_conversion(self, sample_sami, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        result = SAMIWriter().write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami, result)


class TestSAMItoSAMI(SAMITestingMixIn):
    def setup_method(self):
        self.reader = SAMIReader()
        self.writer = SAMIWriter()

    def test_sami_to_sami_conversion(self, sample_sami):
        caption_set = self.reader.read(sample_sami)
        result = SAMIWriter(relativize=False, fit_to_screen=False).write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami, result)

    def test_sami_with_multi_lang(self, sample_sami_with_separate_multi_lang):
        caption_set = self.reader.read(sample_sami_with_separate_multi_lang)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami_with_separate_multi_lang, result)

    def test_is_relativized(
        self, sample_sami_partial_margins_relativized, sample_sami_partial_margins
    ):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = self.reader.read(sample_sami_partial_margins)
        result = SAMIWriter(video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT).write(
            caption_set
        )

        self.assert_sami_captions_equal(sample_sami_partial_margins_relativized, result)

    def test_missing_language_conversion(
        self, sample_sami_with_lang, sample_sami_no_lang
    ):
        caption_set = self.reader.read(sample_sami_no_lang)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami_with_lang, result)
        assert "lang: und;" in result


class TestWebVTTtoSAMI(SAMITestingMixIn):
    def test_webvtt_to_sami_conversion(self, sample_sami, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        result = SAMIWriter().write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami, result)


class TestWebVTTtoSAMIStyles(SAMITestingMixIn):
    """Tests for WebVTT structured style/layout → SAMI conversion."""

    def test_class_span(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.yellow) {\n  color: yellow;\n}\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "<c.yellow>Hello yellow</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert 'class="yellow"' in result
        assert "classes" not in result

    def test_multiple_css_properties(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.fancy) {\n  color: red;\n}\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "<c.fancy>Fancy text</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "color:red;" in result or "color: red;" in result

    def test_positioning_alignment(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:04.000 align:left\n" "Left aligned\n"
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "text-align:left;" in result or "text-align: left;" in result

    def test_writing_direction_dropped(self):
        vtt = (
            "WEBVTT\n\n" "00:00:01.000 --> 00:00:04.000 vertical:rl\n" "Vertical text\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "writing-mode" not in result
        assert "vertical" not in result
        assert "Vertical text" in result

    def test_plain_cue_regression(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:04.000\n" "Plain caption text\n"
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert "Plain caption text" in result
        assert "<sync" in result.lower()

    def test_stylesheet_output(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.yellow) {\n  color: yellow;\n}\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "<c.yellow>Styled</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert ".yellow" in result
        assert "color: yellow;" in result

    def test_multiple_classes(self):
        vtt = (
            "WEBVTT\n\n"
            "STYLE\n"
            "::cue(.red) {\n  color: red;\n}\n\n"
            "STYLE\n"
            "::cue(.blue) {\n  color: blue;\n}\n\n"
            "00:00:01.000 --> 00:00:04.000\n"
            "<c.red>Red</c>\n\n"
            "00:00:05.000 --> 00:00:08.000\n"
            "<c.blue>Blue</c>\n"
        )
        caption_set = WebVTTReader().read(vtt)
        result = SAMIWriter().write(caption_set)

        assert ".red" in result
        assert ".blue" in result
        assert 'class="red"' in result
        assert 'class="blue"' in result
