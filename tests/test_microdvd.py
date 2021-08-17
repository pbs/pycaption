import pytest

from pycaption import MicroDVDReader, CaptionReadNoCaptions
from pycaption.exceptions import CaptionReadSyntaxError, CaptionReadTimingError
from pycaption.base import DEFAULT_LANGUAGE_CODE


class TestMicroDVDReader:
    def test_detection(self, sample_microdvd):
        assert MicroDVDReader().detect(sample_microdvd) is True

    def test_caption_length(self, sample_microdvd):
        captions = MicroDVDReader().read(sample_microdvd)

        assert 7 == len(captions.get_captions(DEFAULT_LANGUAGE_CODE))

    def test_proper_timestamps(self, sample_microdvd):
        captions = MicroDVDReader().read(sample_microdvd)
        paragraph = captions.get_captions(DEFAULT_LANGUAGE_CODE)[2]

        # due to lossy nature of microsec -> frame# we check that
        # conversion is within a second of expected value
        # (fyi: timestamps in examples/ and tests/fixtures/ differ)
        assert abs(17350000 - paragraph.start) < 10 ** 6
        assert abs(18752000 - paragraph.end) < 10 ** 6

    def test_empty_file(self, sample_microdvd_empty):
        with pytest.raises(CaptionReadNoCaptions):
            MicroDVDReader().read(sample_microdvd_empty)

    def test_invalid_format(self, sample_microdvd_invalid_format):
        with pytest.raises(CaptionReadSyntaxError):
            MicroDVDReader().read(sample_microdvd_invalid_format)

    def test_no_fps_provided(self, missing_fps_sample_microdvd):
        with pytest.raises(CaptionReadTimingError):
            MicroDVDReader().read(missing_fps_sample_microdvd)
