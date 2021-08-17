import re

import pytest

from pycaption import SRTReader, SRTWriter, CaptionReadNoCaptions


class TestSRTReader:
    def test_detection(self, sample_srt):
        assert SRTReader().detect(sample_srt) is True

    def test_caption_length(self, sample_srt):
        captions = SRTReader().read(sample_srt)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_srt):
        captions = SRTReader().read(sample_srt)
        paragraph = captions.get_captions("en-US")[2]

        assert 17000000 == paragraph.start
        assert 18752000 == paragraph.end

    def test_numeric_captions(self, sample_srt_numeric):
        captions = SRTReader().read(sample_srt_numeric)

        assert 7 == len(captions.get_captions("en-US"))

    def test_empty_file(self, sample_srt_empty):
        with pytest.raises(CaptionReadNoCaptions):
            SRTReader().read(sample_srt_empty)

    def test_extra_empty_line(self, sample_srt_blank_lines):
        captions = SRTReader().read(sample_srt_blank_lines)

        assert 2 == len(captions.get_captions("en-US"))

    def test_extra_trailing_empty_line(self, sample_srt_trailing_blanks):
        captions = SRTReader().read(sample_srt_trailing_blanks)

        assert 2 == len(captions.get_captions("en-US"))

    def test_multiple_lines_for_one_sentence(self, samples_srt_same_time):
        caption_set = SRTReader().read(samples_srt_same_time)
        results = SRTWriter().write(caption_set)
        sentences = re.split(r"\d{2}:\d{2}:\d{2},\d{3} -->", results)
        sentences.pop(0)

        assert 3 == len(sentences)
