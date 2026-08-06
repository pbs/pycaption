"""Tests for bytes input support across all readers.

All readers should accept bytes (raw file content) and decode as UTF-8
internally, preventing the double-encoding gibberish that occurs when
callers decode with the wrong system encoding (e.g., cp1252).
"""

from pycaption import (
    DFXPReader,
    MicroDVDReader,
    SAMIReader,
    SCCReader,
    SRTReader,
    WebVTTReader,
)


class TestSRTReaderBytes:
    def setup_class(self):
        self.reader = SRTReader()

    def test_read_bytes_produces_same_result_as_str(self, sample_srt):
        from_str = self.reader.read(sample_srt)
        from_bytes = self.reader.read(sample_srt.encode("utf-8"))
        str_captions = from_str.get_captions("en-US")
        bytes_captions = from_bytes.get_captions("en-US")
        assert len(str_captions) == len(bytes_captions)
        for s, b in zip(str_captions, bytes_captions):
            assert s.get_text() == b.get_text()
            assert s.start == b.start
            assert s.end == b.end

    def test_read_bytes_preserves_music_notes(self, sample_srt):
        captions = self.reader.read(sample_srt.encode("utf-8"))
        texts = [c.get_text() for c in captions.get_captions("en-US")]
        assert any("♪" in t for t in texts)

    def test_read_bytes_with_bom(self, sample_srt):
        content_with_bom = b"\xef\xbb\xbf" + sample_srt.encode("utf-8")
        captions = self.reader.read(content_with_bom)
        assert len(captions.get_captions("en-US")) == 7

    def test_detect_bytes(self, sample_srt):
        assert self.reader.detect(sample_srt.encode("utf-8")) is True


class TestWebVTTReaderBytes:
    def setup_class(self):
        self.reader = WebVTTReader()

    def test_read_bytes_produces_same_result_as_str(self, sample_webvtt):
        from_str = self.reader.read(sample_webvtt)
        from_bytes = self.reader.read(sample_webvtt.encode("utf-8"))
        str_captions = from_str.get_captions("en-US")
        bytes_captions = from_bytes.get_captions("en-US")
        assert len(str_captions) == len(bytes_captions)
        for s, b in zip(str_captions, bytes_captions):
            assert s.get_text() == b.get_text()

    def test_read_bytes_with_bom(self, sample_webvtt):
        content_with_bom = b"\xef\xbb\xbf" + sample_webvtt.encode("utf-8")
        captions = self.reader.read(content_with_bom)
        assert len(captions.get_captions("en-US")) > 0

    def test_detect_bytes(self, sample_webvtt):
        assert self.reader.detect(sample_webvtt.encode("utf-8")) is True


class TestDFXPReaderBytes:
    def setup_class(self):
        self.reader = DFXPReader()

    def test_read_bytes_produces_same_result_as_str(self, sample_dfxp):
        from_str = self.reader.read(sample_dfxp)
        from_bytes = self.reader.read(sample_dfxp.encode("utf-8"))
        for lang in from_str.get_languages():
            str_captions = from_str.get_captions(lang)
            bytes_captions = from_bytes.get_captions(lang)
            assert len(str_captions) == len(bytes_captions)
            for s, b in zip(str_captions, bytes_captions):
                assert s.get_text() == b.get_text()

    def test_read_bytes_with_bom(self, sample_dfxp):
        content_with_bom = b"\xef\xbb\xbf" + sample_dfxp.encode("utf-8")
        captions = self.reader.read(content_with_bom)
        assert not captions.is_empty()

    def test_detect_bytes(self, sample_dfxp):
        assert self.reader.detect(sample_dfxp.encode("utf-8")) is True


class TestSAMIReaderBytes:
    def setup_class(self):
        self.reader = SAMIReader()

    def test_read_bytes_produces_same_result_as_str(self, sample_sami):
        from_str = self.reader.read(sample_sami)
        from_bytes = self.reader.read(sample_sami.encode("utf-8"))
        for lang in from_str.get_languages():
            str_captions = from_str.get_captions(lang)
            bytes_captions = from_bytes.get_captions(lang)
            assert len(str_captions) == len(bytes_captions)
            for s, b in zip(str_captions, bytes_captions):
                assert s.get_text() == b.get_text()

    def test_read_bytes_preserves_music_notes(self, sample_sami):
        captions = self.reader.read(sample_sami.encode("utf-8"))
        langs = list(captions.get_languages())
        texts = [c.get_text() for c in captions.get_captions(langs[0])]
        assert any("♪" in t for t in texts)

    def test_read_bytes_with_bom(self, sample_sami):
        content_with_bom = b"\xef\xbb\xbf" + sample_sami.encode("utf-8")
        captions = self.reader.read(content_with_bom)
        assert not captions.is_empty()

    def test_detect_bytes(self, sample_sami):
        assert self.reader.detect(sample_sami.encode("utf-8")) is True


class TestSCCReaderBytes:
    def test_read_bytes_produces_same_result_as_str(self, sample_scc_pop_on):
        from_str = SCCReader().read(sample_scc_pop_on)
        from_bytes = SCCReader().read(sample_scc_pop_on.encode("utf-8"))
        str_captions = from_str.get_captions("en-US")
        bytes_captions = from_bytes.get_captions("en-US")
        assert len(str_captions) == len(bytes_captions)
        for s, b in zip(str_captions, bytes_captions):
            assert s.get_text() == b.get_text()

    def test_read_bytes_with_bom(self, sample_scc_pop_on):
        content_with_bom = b"\xef\xbb\xbf" + sample_scc_pop_on.encode("utf-8")
        captions = SCCReader().read(content_with_bom)
        assert len(captions.get_captions("en-US")) > 0

    def test_detect_bytes(self, sample_scc_pop_on):
        assert SCCReader().detect(sample_scc_pop_on.encode("utf-8")) is True


class TestMicroDVDReaderBytes:
    def setup_class(self):
        self.reader = MicroDVDReader()

    def test_read_bytes_produces_same_result_as_str(self, sample_microdvd):
        from_str = self.reader.read(sample_microdvd)
        from_bytes = self.reader.read(sample_microdvd.encode("utf-8"))
        str_captions = from_str.get_captions("und")
        bytes_captions = from_bytes.get_captions("und")
        assert len(str_captions) == len(bytes_captions)
        for s, b in zip(str_captions, bytes_captions):
            assert s.get_text() == b.get_text()

    def test_read_bytes_with_bom(self, sample_microdvd):
        content_with_bom = b"\xef\xbb\xbf" + sample_microdvd.encode("utf-8")
        captions = self.reader.read(content_with_bom)
        assert not captions.is_empty()

    def test_detect_bytes(self, sample_microdvd):
        assert self.reader.detect(sample_microdvd.encode("utf-8")) is True


