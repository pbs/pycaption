import re

from pycaption import (
    DFXPReader, SAMIReader, SRTReader, SRTWriter, WebVTTReader,
)

from tests.mixins import SRTTestingMixIn


class TestDFXPtoSRT(SRTTestingMixIn):
    def setup_class(self):
        self.reader = DFXPReader()
        self.writer = SRTWriter()

    def test_dfxp_to_srt_conversion(self, sample_srt, sample_dfxp):
        caption_set = self.reader.read(sample_dfxp)
        results = self.writer.write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)

    def test_dfxp_empty_cue_to_srt(self, sample_srt_empty_cue_output,
                                   sample_dfxp_empty_cue):
        caption_set = self.reader.read(sample_dfxp_empty_cue)
        results = self.writer.write(caption_set)

        self.assert_srt_equals(sample_srt_empty_cue_output, results)


class TestSAMItoSRT(SRTTestingMixIn):
    def test_sami_to_srt_conversion(self, sample_srt, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = SRTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)


class TestSRTtoSRT(SRTTestingMixIn):
    def setup_class(self):
        self.reader = SRTReader()
        self.writer = SRTWriter()

    def test_srt_to_srt_conversion(self, sample_srt):
        caption_set = self.reader.read(sample_srt)
        results = self.writer.write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)

    def test_multiple_lines_for_one_sentence(self, samples_srt_same_time):
        caption_set = self.reader.read(samples_srt_same_time)
        results = self.writer.write(caption_set)
        sentences = re.split(r"\n\d\n", results)

        assert 3 == len(sentences)
        assert 4 == len(sentences[0].splitlines())


class TestWebVTTtoSRT(SRTTestingMixIn):
    def test_webvtt_to_srt_conversion(self, sample_srt, sample_webvtt):
        caption_set = WebVTTReader().read(sample_webvtt)
        results = SRTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_srt_equals(sample_srt, results)
