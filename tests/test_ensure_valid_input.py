import pytest

from pycaption import DFXPReader, SAMIReader, SCCReader, SRTReader, WebVTTReader

from pycaption.exceptions import InvalidInputError


class TestReader:
    def test_dfxp_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            DFXPReader().read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'

    def test_sami_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            SAMIReader().read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'

    def test_scc_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            SCCReader().read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'

    def test_srt_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            SRTReader().read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'

    def test_webvtt_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            WebVTTReader().read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'
