from pycaption import (
    SRTReader, SRTWriter, SAMIWriter, DFXPWriter, WebVTTWriter, MicroDVDWriter,
)

from tests.mixins import (
    SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn,
    MicroDVDTestingMixIn,
)


class TestSRTtoSRT(SRTTestingMixIn):
    def test_srt_to_srt_conversion(self, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = SRTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)


class TestSRTtoSAMI(SAMITestingMixIn):
    def test_srt_to_sami_conversion(self, sample_sami, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = SAMIWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_sami_equals(sample_sami, results)


class TestSRTtoDFXP(DFXPTestingMixIn):
    def test_srt_to_dfxp_conversion(self, sample_dfxp, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = DFXPWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(
            sample_dfxp, results,
            ignore_styling=True, ignore_spans=True
        )


class TestSRTtoWebVTT(WebVTTTestingMixIn):
    def test_srt_to_webvtt_conversion(self, sample_webvtt_from_srt, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_srt, results)


class TestSRTtoMicroDVD(MicroDVDTestingMixIn):
    def test_srt_to_microdvd_conversion(self, sample_microdvd, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd, results)
