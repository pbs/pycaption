import pytest

from pycaption import SRTReader, CaptionReadNoCaptions
from tests.mixins import ReaderTestingMixIn


class TestSRTReader(ReaderTestingMixIn):
    def setup_class(self):
        self.reader = SRTReader()

    def test_positive_answer_for_detection(self, sample_srt):
        super().assert_positive_answer_for_detection(sample_srt)

    @pytest.mark.parametrize('different_sample', [
        pytest.lazy_fixture('sample_dfxp'),
        pytest.lazy_fixture('sample_microdvd'),
        pytest.lazy_fixture('sample_sami'),
        pytest.lazy_fixture('sample_scc_pop_on'),
        pytest.lazy_fixture('sample_webvtt')
    ])
    def test_negative_answer_for_detection(self, different_sample):
        super().assert_negative_answer_for_detection(different_sample)

    def test_caption_length(self, sample_srt):
        captions = self.reader.read(sample_srt)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_srt):
        captions = self.reader.read(sample_srt)
        third_paragraph = captions.get_captions("en-US")[2]

        assert 17000000 == third_paragraph.start
        assert 18752000 == third_paragraph.end

    def test_numeric_captions(self, sample_srt_numeric):
        captions = self.reader.read(sample_srt_numeric)
        paragraphs = captions.get_captions("en-US")

        assert 7 == len(captions.get_captions("en-US"))
        assert paragraphs[-3].get_text() == "NUMBER  IS  662-429-84-77."
        assert paragraphs[-1].get_text() == "3"

    def test_empty_file(self, sample_srt_empty):
        with pytest.raises(CaptionReadNoCaptions) as exc_info:
            self.reader.read(sample_srt_empty)
        assert exc_info.value.args[0] == 'empty caption file'

    def test_extra_empty_line(self, sample_srt_blank_lines):
        captions = self.reader.read(sample_srt_blank_lines)
        paragraphs = captions.get_captions("en-US")

        assert 2 == len(paragraphs)
        assert '\n' not in paragraphs[0].get_text()
        assert '\n' not in paragraphs[1].get_text()

    def test_extra_trailing_empty_line(self, sample_srt_trailing_blanks):
        captions = self.reader.read(sample_srt_trailing_blanks)
        paragraphs = captions.get_captions("en-US")

        assert 2 == len(paragraphs)
        assert '\n' not in paragraphs[0].get_text()
        assert '\n' not in paragraphs[1].get_text()

    def test_timestamps_without_micro(
            self, sample_srt_timestamps_without_microseconds):
        captions = self.reader.read(sample_srt_timestamps_without_microseconds)
        first_paragraph = captions.get_captions("en-US")[0]

        assert 13000000 == first_paragraph.start
        assert 16000000 == first_paragraph.end
