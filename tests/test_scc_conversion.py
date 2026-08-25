import re

from bs4 import BeautifulSoup

from pycaption import (
    DFXPWriter,
    SCCReader,
    SCCWriter,
    SRTReader,
    SRTWriter,
    WebVTTReader,
    WebVTTWriter,
)
from tests.mixins import CaptionSetTestingMixIn

# This is quite fuzzy at the moment.
TOLERANCE_MICROSECONDS = 600 * 1000


class TestSRTtoSCCtoSRT(CaptionSetTestingMixIn):
    def _test_srt_to_scc_to_srt_conversion(self, srt_captions):
        captions_1 = SRTReader().read(srt_captions)
        scc_results = SCCWriter().write(captions_1)
        scc_captions = SCCReader().read(scc_results)
        srt_results = SRTWriter().write(scc_captions)
        captions_2 = SRTReader().read(srt_results)
        self.assert_captionset_almost_equals(
            captions_1, captions_2, TOLERANCE_MICROSECONDS
        )

    def test_srt_to_scc_to_srt_conversion(self, sample_srt_ascii):
        self._test_srt_to_scc_to_srt_conversion(sample_srt_ascii)


# The following test fails -- maybe a bug with SCCReader
#    def test_srt_to_srt_unicode_conversion(self):
#        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT_UNICODE)


class TestSCCtoDFXP:
    def test_scc_to_dfxp(self, sample_scc_multiple_positioning):
        caption_set = SCCReader().read(sample_scc_multiple_positioning)
        dfxp = DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)

        assert 'tts:textAlign="left"' in dfxp
        assert "tts:origin" in dfxp
        assert "abab" in dfxp
        assert "ghgh" in dfxp

    def test_dfxp_is_valid_xml_when_scc_source_has_weird_italic_commands(
        self,
        sample_scc_created_dfxp_with_wrongly_closing_spans,
    ):
        caption_set = SCCReader().read(
            sample_scc_created_dfxp_with_wrongly_closing_spans
        )

        dfxp = DFXPWriter().write(caption_set)

        assert 'tts:textAlign="left"' in dfxp
        assert 'tts:fontStyle="italic"' in dfxp
        from bs4 import BeautifulSoup

        BeautifulSoup(dfxp, "lxml-xml")

    def test_dfxp_is_valid_xml_when_scc_source_has_ampersand_character(
        self, sample_scc_with_ampersand_character
    ):
        caption_set = SCCReader().read(sample_scc_with_ampersand_character)

        dfxp = DFXPWriter().write(caption_set)

        assert 'tts:textAlign="left"' in dfxp
        assert "&amp;" in dfxp
        from bs4 import BeautifulSoup

        BeautifulSoup(dfxp, "lxml-xml")

    def test_row_jump_with_pending_reposition_splits_into_two_regions(
        self, sample_scc_row_jump_with_pending_reposition
    ):
        caption_set = SCCReader().read(sample_scc_row_jump_with_pending_reposition)
        dfxp = DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)

        soup = BeautifulSoup(dfxp, "lxml-xml")
        paragraphs = soup.find_all("p")

        assert len(paragraphs) == 2, (
            "A row jump landing on a pending, unconsumed reposition must "
            "split into two cues, not stay joined by a BREAK"
        )
        assert not soup.find_all("br"), "Cues must not be joined by a phantom BREAK"

        first, second = paragraphs
        assert first["begin"] == second["begin"] == "00:00:25.091"
        assert first["end"] == second["end"] == "00:00:29.091"
        assert first["region"] != second["region"]

        first_region = soup.find("region", {"xml:id": first["region"]})
        second_region = soup.find("region", {"xml:id": second["region"]})
        assert first_region["tts:origin"] == "20% 77%"
        assert second_region["tts:origin"] == "37.5% 89%"

        assert "Always by her side" in first.get_text()
        assert second.get_text(strip=True) == "And Trini!"

    def test_row_skip_does_not_preserve_blank_line_splits_into_two_regions(
        self, sample_scc_row_skip_does_not_preserve_blank_line
    ):
        caption_set = SCCReader().read(sample_scc_row_skip_does_not_preserve_blank_line)
        dfxp = DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)

        soup = BeautifulSoup(dfxp, "lxml-xml")
        paragraphs = soup.find_all("p")

        assert len(paragraphs) == 2, (
            "A skipped row must split into two cues; the gap must not be "
            "preserved as a blank line joining them"
        )
        assert not soup.find_all("br"), "Cues must not be joined by a phantom BREAK"

        first, second = paragraphs
        assert first["begin"] == second["begin"] == "00:00:20.420"
        assert first["end"] == second["end"] == "00:00:24.420"
        assert first["region"] != second["region"]

        first_region = soup.find("region", {"xml:id": first["region"]})
        second_region = soup.find("region", {"xml:id": second["region"]})
        assert first_region["tts:origin"] == "20% 5%"
        assert second_region["tts:origin"] == "10% 17%"

        assert first.get_text(strip=True) == "AB"
        assert second.get_text(strip=True) == "CD"

    def test_paint_on_row_plus_one_large_column_jump_splits_into_two_regions(
        self, sample_scc_paint_on_row_plus_one_large_column_jump
    ):
        caption_set = SCCReader().read(
            sample_scc_paint_on_row_plus_one_large_column_jump
        )
        dfxp = DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)

        soup = BeautifulSoup(dfxp, "lxml-xml")
        paragraphs = soup.find_all("p")

        assert len(paragraphs) == 2, (
            "A row+1 jump paired with a large paint-on column jump must "
            "split into two cues, since it targets an unrelated region"
        )
        assert not soup.find_all("br"), "Cues must not be joined by a phantom BREAK"

        first, second = paragraphs
        assert first["begin"] == second["begin"] == "00:00:20.020"
        assert first["end"] == second["end"] == "00:00:20.286"
        assert first["region"] != second["region"]

        first_region = soup.find("region", {"xml:id": first["region"]})
        second_region = soup.find("region", {"xml:id": second["region"]})
        assert first_region["tts:origin"] == "10% 29%"
        assert second_region["tts:origin"] == "60% 35%"

        assert first.get_text(strip=True) == "AB"
        assert second.get_text(strip=True) == "CD"


class TestSCCTimestampOrdering:
    def test_scc_captions_are_in_order_when_short_text_followed_by_long(self):
        """When short caption text is followed by longer caption text,
        the SCC output timestamps should remain in chronological order.
        """
        vtt_input = (
            "WEBVTT\n\n"
            "0\n"
            "00:00:02.200 --> 00:00:02.359\n"
            "you know,\n\n"
            "1\n"
            "00:00:02.400 --> 00:00:03.760\n"
            "the way he kind of looked at me.\n\n"
            "2\n"
            "00:00:04.700 --> 00:00:05.169\n"
            "And I said,\n\n"
            "3\n"
            "00:00:05.210 --> 00:00:05.520\n"
            "oh\n"
        )
        captions = WebVTTReader().read(vtt_input)
        scc_output = SCCWriter().write(captions)
        # SCC timestamps use HH:MM:SS:FF format (FF = frames)
        timestamps = re.findall(r"(\d+:\d+:\d+:\d+)", scc_output)
        for i in range(1, len(timestamps)):
            assert (
                timestamps[i] >= timestamps[i - 1]
            ), f"Timestamps out of order: {timestamps[i - 1]} > {timestamps[i]}"


class TestSCCToWebVTT:
    def test_webvtt_newlines_are_properly_rendered(
        self,
        sample_webvtt_from_scc_properly_writes_newlines_output,
        scc_that_generates_webvtt_with_proper_newlines,
    ):
        caption_set = SCCReader().read(scc_that_generates_webvtt_with_proper_newlines)
        webvtt = WebVTTWriter().write(caption_set)

        assert webvtt == sample_webvtt_from_scc_properly_writes_newlines_output

    @staticmethod
    def _cue_blocks(webvtt):
        return [
            block
            for block in webvtt.strip().split("\n\n")
            if block.strip() and "WEBVTT" not in block
        ]

    def test_row_jump_with_pending_reposition_splits_into_two_cues(
        self, sample_scc_row_jump_with_pending_reposition
    ):
        caption_set = SCCReader().read(sample_scc_row_jump_with_pending_reposition)
        webvtt = WebVTTWriter().write(caption_set)

        cues = self._cue_blocks(webvtt)
        assert len(cues) == 2, (
            "A row jump landing on a pending, unconsumed reposition must "
            "split into two cues, not stay joined by a BREAK"
        )

        first, second = cues
        assert first.startswith("00:00:25.091 --> 00:00:29.091")
        assert second.startswith("00:00:25.091 --> 00:00:29.091")
        assert "position:20%" in first and "line:77%" in first
        assert "position:37.5%" in second and "line:89%" in second
        assert "Always by her side" in first
        assert second.split("\n", 1)[1].strip() == "And Trini!"

    def test_row_skip_does_not_preserve_blank_line_splits_into_two_cues(
        self, sample_scc_row_skip_does_not_preserve_blank_line
    ):
        caption_set = SCCReader().read(sample_scc_row_skip_does_not_preserve_blank_line)
        webvtt = WebVTTWriter().write(caption_set)

        cues = self._cue_blocks(webvtt)
        assert len(cues) == 2, (
            "A skipped row must split into two cues; the gap must not be "
            "preserved as a blank/nbsp-only line joining them"
        )

        first, second = cues
        assert first.startswith("00:00:20.420 --> 00:00:24.420")
        assert second.startswith("00:00:20.420 --> 00:00:24.420")
        assert "position:20%" in first and "line:5%" in first
        assert "position:10%" in second and "line:17%" in second
        assert first.split("\n", 1)[1].strip() == "AB"
        assert second.split("\n", 1)[1].strip() == "CD"

    def test_paint_on_row_plus_one_large_column_jump_splits_into_two_cues(
        self, sample_scc_paint_on_row_plus_one_large_column_jump
    ):
        caption_set = SCCReader().read(
            sample_scc_paint_on_row_plus_one_large_column_jump
        )
        webvtt = WebVTTWriter().write(caption_set)

        cues = self._cue_blocks(webvtt)
        assert len(cues) == 2, (
            "A row+1 jump paired with a large paint-on column jump must "
            "split into two cues, since it targets an unrelated region"
        )

        first, second = cues
        assert first.startswith("00:00:20.020 --> 00:00:20.286")
        assert second.startswith("00:00:20.020 --> 00:00:20.286")
        assert "position:10%" in first and "line:29%" in first
        assert "position:60%" in second and "line:35%" in second
        assert first.split("\n", 1)[1].strip() == "AB"
        assert second.split("\n", 1)[1].strip() == "CD"
