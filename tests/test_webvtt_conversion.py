from pycaption import (
    SRTReader, WebVTTReader, WebVTTWriter, SAMIWriter, DFXPWriter,
    MicroDVDWriter,
)

from tests.mixins import (
    WebVTTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn,
    MicroDVDTestingMixIn,
)


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

#     # TODO: Write a test that includes a WebVTT file with style tags
#     # That will fail because the styles used in the cues are not tracked.


class TestWebVTTtoSAMI(SAMITestingMixIn):
    def test_webvtt_to_sami_conversion(self, sample_sami, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = SAMIWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_sami_equals(sample_sami, results)


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
