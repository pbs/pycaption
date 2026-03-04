import re

import pytest

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
    def test_scc_to_dfxp(
        self, sample_dfxp_from_scc_output, sample_scc_multiple_positioning
    ):
        caption_set = SCCReader().read(sample_scc_multiple_positioning)
        dfxp = DFXPWriter(relativize=False, fit_to_screen=False).write(caption_set)
        assert sample_dfxp_from_scc_output == dfxp

    def test_dfxp_is_valid_xml_when_scc_source_has_weird_italic_commands(
        self,
        sample_dfxp_with_properly_closing_spans_output,
        sample_scc_created_dfxp_with_wrongly_closing_spans,
    ):
        caption_set = SCCReader().read(
            sample_scc_created_dfxp_with_wrongly_closing_spans
        )

        dfxp = DFXPWriter().write(caption_set)

        assert dfxp == sample_dfxp_with_properly_closing_spans_output

    def test_dfxp_is_valid_xml_when_scc_source_has_ampersand_character(
        self, sample_dfxp_with_ampersand_character, sample_scc_with_ampersand_character
    ):
        caption_set = SCCReader().read(sample_scc_with_ampersand_character)

        dfxp = DFXPWriter().write(caption_set)

        assert dfxp == sample_dfxp_with_ampersand_character


class TestSCCTimestampOrdering:
    def test_scc_captions_are_in_order_when_short_text_followed_by_long(self):
        """When short caption text is followed by longer caption text,
        the SCC output timestamps should remain in chronological order.
        See: https://github.com/pbs/pycaption/issues/XXX
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
        timestamps = re.findall(r"(\d+:\d+:\d+:\d+)", scc_output)
        for i in range(1, len(timestamps)):
            assert timestamps[i] >= timestamps[i - 1], (
                f"Timestamps out of order: {timestamps[i - 1]} > {timestamps[i]}"
            )


class TestSCCToWebVTT:
    def test_webvtt_newlines_are_properly_rendered(
        self,
        sample_webvtt_from_scc_properly_writes_newlines_output,
        scc_that_generates_webvtt_with_proper_newlines,
    ):
        caption_set = SCCReader().read(scc_that_generates_webvtt_with_proper_newlines)
        webvtt = WebVTTWriter().write(caption_set)

        assert webvtt == sample_webvtt_from_scc_properly_writes_newlines_output
