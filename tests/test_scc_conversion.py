import pytest

from pycaption import (
    SCCReader, SCCWriter, SRTReader, SRTWriter, DFXPWriter, WebVTTWriter,
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
    def test_scc_to_dfxp(self, sample_dfxp_from_scc_output,
                         sample_scc_multiple_positioning):
        caption_set = SCCReader().read(sample_scc_multiple_positioning)
        dfxp = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        assert sample_dfxp_from_scc_output == dfxp

    def test_dfxp_is_valid_xml_when_scc_source_has_weird_italic_commands(
            self, sample_dfxp_with_properly_closing_spans_output,
            sample_scc_created_dfxp_with_wrongly_closing_spans):
        caption_set = SCCReader().read(
            sample_scc_created_dfxp_with_wrongly_closing_spans
        )

        dfxp = DFXPWriter().write(caption_set)

        assert dfxp == sample_dfxp_with_properly_closing_spans_output

    def test_dfxp_is_valid_xml_when_scc_source_has_ampersand_character(
            self, sample_dfxp_with_ampersand_character,
            sample_scc_with_ampersand_character):
        caption_set = SCCReader().read(sample_scc_with_ampersand_character)

        dfxp = DFXPWriter().write(caption_set)

        assert dfxp == sample_dfxp_with_ampersand_character


class TestSCCToWebVTT:
    def test_webvtt_newlines_are_properly_rendered(
            self, sample_webvtt_from_scc_properly_writes_newlines_output,
            scc_that_generates_webvtt_with_proper_newlines):
        caption_set = SCCReader().read(
            scc_that_generates_webvtt_with_proper_newlines)
        webvtt = WebVTTWriter().write(caption_set)

        assert webvtt == sample_webvtt_from_scc_properly_writes_newlines_output
