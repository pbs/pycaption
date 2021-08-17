import pytest

from pycaption import DFXPReader, SAMIReader, SCCReader, SRTReader, WebVTTReader

from pycaption.exceptions import InvalidInputError


class TestReader:
    def test_dfxp_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError):
            DFXPReader().read(b'')

    def test_sami_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError):
            SAMIReader().read(b'')

    def test_scc_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError):
            SCCReader().read(b'')

    def test_srt_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError):
            SRTReader().read(b'')

    def test_webvtt_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError):
            WebVTTReader().read(b'')
