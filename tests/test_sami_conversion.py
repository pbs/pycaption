from pycaption import (
    DFXPReader, SAMIReader, SAMIWriter, SRTReader, WebVTTReader,
)

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
            self, sample_sami_from_dfxp_with_nested_spans,
            sample_dfxp_with_nested_spans):
        caption_set = self.reader.read(sample_dfxp_with_nested_spans)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami_from_dfxp_with_nested_spans,
                                        result)

    def test_dfxp_to_sami_with_margins(
            self, sample_dfxp_from_sami_with_margins):
        caption_set = self.reader.read(sample_dfxp_from_sami_with_margins)
        result = SAMIWriter(video_width=VIDEO_WIDTH,
                            video_height=VIDEO_HEIGHT).write(caption_set)
        margins = ["margin-right: 6.04%;",
                   "margin-bottom: 0%;",
                   "margin-top: 0%;",
                   "margin-left: 6.04%;"]

        assert all(margin in result for margin in margins)

    def test_dfxp_empty_cue_to_sami(self, sample_sami_empty_cue_output,
                                    sample_dfxp_empty_cue):
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
        result = SAMIWriter(relativize=False,
                            fit_to_screen=False).write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami, result)

    def test_sami_with_multi_lang(self, sample_sami_with_separate_multi_lang):
        caption_set = self.reader.read(sample_sami_with_separate_multi_lang)
        result = self.writer.write(caption_set)

        assert isinstance(result, str)
        self.assert_sami_captions_equal(sample_sami_with_separate_multi_lang,
                                        result)

    def test_is_relativized(self, sample_sami_partial_margins_relativized,
                            sample_sami_partial_margins):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = self.reader.read(sample_sami_partial_margins)
        result = SAMIWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)

        self.assert_sami_captions_equal(sample_sami_partial_margins_relativized,
                                        result)

    def test_missing_language_conversion(self, sample_sami_with_lang,
                                         sample_sami_no_lang):
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
