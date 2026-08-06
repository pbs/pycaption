import logging

import pytest

from pycaption import SAMIReader, SRTReader
from pycaption.base import BaseReader
from pycaption.dfxp import DFXPReader


def _double_encode(text):
    """Simulate double-encoding: UTF-8 bytes misread as CP-1252, re-encoded."""
    return text.encode("utf-8").decode("cp1252")


ORIGINAL_CHARS = ["♪", "—", "’", "é"]


class TestRepairDoubleEncoding:
    @pytest.mark.parametrize("original", ORIGINAL_CHARS)
    def test_fixes_double_encoded(self, original):
        garbled = _double_encode(original)
        assert BaseReader._repair_double_encoding(garbled) == original

    def test_leaves_clean_utf8_alone(self):
        clean = "♪ This is — perfectly fine é text"
        assert BaseReader._repair_double_encoding(clean) == clean

    def test_logs_warning_on_repair(self, caplog):
        garbled = _double_encode("♪")
        with caplog.at_level(logging.WARNING, logger="pycaption.base"):
            BaseReader._repair_double_encoding(garbled)
        assert "double-encoded" in caplog.text.lower()

    def test_no_warning_for_clean_input(self, caplog):
        with caplog.at_level(logging.WARNING, logger="pycaption.base"):
            BaseReader._repair_double_encoding("♪ Music ♪")
        assert caplog.text == ""


class TestDoubleEncodingEndToEnd:
    def test_srt_reader(self):
        garbled_note = _double_encode("♪")
        content = (
            "1\n"
            "00:00:01,000 --> 00:00:02,000\n"
            f"{garbled_note} Music {garbled_note}\n"
        )
        captions = SRTReader().read(content)
        nodes = captions.get_captions("en-US")[0].nodes
        text = "".join(n.content for n in nodes)
        assert "♪" in text
        assert garbled_note not in text

    def test_dfxp_reader(self):
        garbled = _double_encode("élève")
        content = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">\n'
            "  <body><div>\n"
            f'    <p begin="00:00:01.000" end="00:00:02.000">'
            f"{garbled}</p>\n"
            "  </div></body>\n"
            "</tt>\n"
        )
        captions = DFXPReader().read(content)
        nodes = captions.get_captions("en")[0].nodes
        text = "".join(n.content for n in nodes)
        assert "élève" in text
        assert garbled not in text

    def test_sami_reader(self):
        garbled_dash = _double_encode("—")
        content = (
            "<SAMI>\n"
            "<Body>\n"
            "  <Sync Start=1000>\n"
            f"    <P Class=enCC>{garbled_dash} Hello</P>\n"
            "  </Sync>\n"
            "  <Sync Start=2000>\n"
            "    <P Class=enCC>&nbsp;</P>\n"
            "  </Sync>\n"
            "</Body>\n"
            "</SAMI>\n"
        )
        captions = SAMIReader().read(content)
        lang = list(captions.get_languages())[0]
        nodes = captions.get_captions(lang)[0].nodes
        text = "".join(n.content for n in nodes)
        assert "—" in text
