from pycaption import (
    SAMIReader, SAMIWriter, SRTWriter, DFXPWriter, WebVTTWriter, MicroDVDWriter,
)

from .mixins import (
    SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn,
    MicroDVDTestingMixIn,
)

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class TestSAMItoSAMI(SAMITestingMixIn):
    def test_sami_to_sami_conversion(self, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = SAMIWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)

        assert isinstance(results, str)
        self.assert_sami_equals(sample_sami, results)

    def test_is_relativized(self, sample_sami_partial_margins_relativized,
                            sample_sami_partial_margins):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = SAMIReader().read(sample_sami_partial_margins)
        result = SAMIWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)

        self.assert_sami_equals(result, sample_sami_partial_margins_relativized)


class TestSAMItoSRT(SRTTestingMixIn):
    def test_sami_to_srt_conversion(self, sample_srt, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = SRTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)


class TestSAMItoDFXP(DFXPTestingMixIn):
    def test_sami_to_dfxp_conversion(
            self, sample_dfxp_from_sami_with_positioning, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(sample_dfxp_from_sami_with_positioning, results)

    def test_sami_to_dfxp_with_margin(self, sample_dfxp_from_sami_with_margins,
                                      sample_sami_partial_margins):
        caption_set = SAMIReader().read(sample_sami_partial_margins)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(sample_dfxp_from_sami_with_margins, results)

    def test_sami_to_dfxp_with_margin_for_language(
            self, sample_dfxp_from_sami_with_lang_margins,
            sample_sami_lang_margin):
        caption_set = SAMIReader().read(sample_sami_lang_margin)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_lang_margins,
            results
        )

    def test_sami_to_dfxp_with_span(self, sample_dfxp_from_sami_with_span,
                                    sample_sami_with_span):
        caption_set = SAMIReader().read(sample_sami_with_span)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(sample_dfxp_from_sami_with_span, results)

    def test_sami_to_dfxp_with_bad_span_align(
            self, sample_dfxp_from_sami_with_bad_span_align,
            sample_sami_with_bad_span_align):
        caption_set = SAMIReader().read(sample_sami_with_bad_span_align)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_bad_span_align,
            results
        )

    def test_sami_to_dfxp_ignores_multiple_span_aligns(
            self, sample_dfxp_from_sami_with_bad_span_align,
            sample_sami_with_multiple_span_aligns):
        caption_set = SAMIReader().read(sample_sami_with_multiple_span_aligns)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_bad_span_align,
            results
        )

    def test_sami_to_dfxp_xml_output(self, sample_sami_syntax_error):
        captions = SAMIReader().read(sample_sami_syntax_error)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(captions)

        assert isinstance(results, str)
        assert 'xmlns="http://www.w3.org/ns/ttml"' in results
        assert 'xmlns:tts="http://www.w3.org/ns/ttml#styling"' in results


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


class TestSAMItoMicroDVD(MicroDVDTestingMixIn):
    def test_sami_to_micro_dvd_conversion(self, sample_microdvd_2, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd_2, results)


class TestSAMIWithMissingLanguage(SAMITestingMixIn):
    def test_sami_to_sami_conversion(self, sample_sami_with_lang,
                                     sample_sami_no_lang):
        caption_set = SAMIReader().read(sample_sami_no_lang)
        results = SAMIWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_sami_equals(sample_sami_with_lang, results)
        assert "lang: und;" in results
