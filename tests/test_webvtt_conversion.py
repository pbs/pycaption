import re

from pycaption import (
    SAMIReader, SRTReader, WebVTTReader, WebVTTWriter, DFXPWriter,
    MicroDVDWriter,
)

from tests.mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, MicroDVDTestingMixIn,
)


class TestSAMItoWebVTT(WebVTTTestingMixIn):
    def test_sami_to_webvtt_conversion(
            self, sample_webvtt_from_sami, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami, results)

    def test_sami_with_style_tags_to_webvtt_conversion(
            self, sample_webvtt_from_sami_with_style,
            sample_sami_with_style_tags):
        caption_set = SAMIReader().read(sample_sami_with_style_tags)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_style, results)

    def test_sami_with_css_inline_style_to_webvtt_conversion(
            self, sample_webvtt_from_sami_with_style,
            sample_sami_with_css_inline_style):
        caption_set = SAMIReader().read(sample_sami_with_css_inline_style)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_style, results)

    def test_sami_with_css_id_style_to_webvtt_conversion(
            self, sample_webvtt_from_sami_with_id_style,
            sample_sami_with_css_id_style):
        caption_set = SAMIReader().read(sample_sami_with_css_id_style)
        results = WebVTTWriter(
            video_width=640, video_height=360).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_sami_with_id_style,
                                  results)


class TestSRTtoWebVTT(WebVTTTestingMixIn):
    def test_srt_to_webvtt_conversion(self, sample_webvtt_from_srt, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_srt, results)


class TestWebVTTtoWebVTT(WebVTTTestingMixIn):
    def test_webvtt_to_webvtt_conversion(self, sample_webvtt_from_webvtt,
                                         sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_webvtt, results)

    def test_cue_settings_are_kept(self, sample_webvtt_with_cue_settings):
        caption_set = WebVTTReader().read(sample_webvtt_with_cue_settings)

        webvtt = WebVTTWriter().write(caption_set)

        assert sample_webvtt_with_cue_settings == webvtt

    def test_positioning_is_kept(self,
                                 sample_webvtt_from_dfxp_with_positioning):
        caption_set = WebVTTReader().read(
            sample_webvtt_from_dfxp_with_positioning)
        results = WebVTTWriter().write(caption_set)

        assert sample_webvtt_from_dfxp_with_positioning == results

    def test_output_timestamps(self, sample_webvtt_timestamps):
        expected_timestamp_line_pattern = re.compile(
            r'^(\d{2,}):(\d{2})(:\d{2})?\.(\d{3}) '
            r'--> (\d{2,}):(\d{2})(:\d{2})?\.(\d{3})')

        caption_set = WebVTTReader().read(sample_webvtt_timestamps)
        results = WebVTTWriter().write(caption_set).splitlines()

        assert re.match(expected_timestamp_line_pattern, results[2])
        assert re.match(expected_timestamp_line_pattern, results[5])

#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class TestWebVTTtoDFXP(DFXPTestingMixIn):
    def test_webvtt_to_dfxp_conversion(self, sample_dfxp, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = DFXPWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(
            sample_dfxp, results, ignore_styling=True, ignore_spans=True
        )


class TestWebVTTtoMicroDVD(MicroDVDTestingMixIn):
    def test_webvtt_to_microdvd_conversion(self, sample_microdvd,
                                           sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd, results)
