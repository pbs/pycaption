import unittest

from pycaption import (
    SCCReader, SCCWriter, SRTReader, SRTWriter, DFXPWriter, WebVTTWriter)

from .samples.dfxp import (
    SAMPLE_DFXP_FROM_SCC_OUTPUT, SAMPLE_DFXP_WITH_PROPERLY_CLOSING_SPANS_OUTPUT
)
from .samples.scc import (
    SAMPLE_SCC_CREATED_DFXP_WITH_WRONGLY_CLOSING_SPANS,
    SCC_THAT_GENERATES_WEBVTT_WITH_PROPER_NEWLINES,
    SAMPLE_SCC_MULTIPLE_POSITIONING,
    SAMPLE_SCC_FLASHING_CAPTIONS,
)
from .samples.srt import SAMPLE_SRT_ASCII
from .samples.webvtt import (
    SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES_OUTPUT
)

from .mixins import CaptionSetTestingMixIn

# This is quite fuzzy at the moment.
TOLERANCE_MICROSECONDS = 600 * 1000


class SRTtoSCCtoSRTTestCase(unittest.TestCase, CaptionSetTestingMixIn):

    def _test_srt_to_scc_to_srt_conversion(self, srt_captions):
        captions_1 = SRTReader().read(srt_captions)
        scc_results = SCCWriter().write(captions_1)
        scc_captions = SCCReader().read(scc_results)
        srt_results = SRTWriter().write(scc_captions)
        captions_2 = SRTReader().read(srt_results)
        self.assertCaptionSetAlmostEquals(captions_1, captions_2,
                                          TOLERANCE_MICROSECONDS)

    def test_srt_to_scc_to_srt_conversion(self):
        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT_ASCII)

# The following test fails -- maybe a bug with SCCReader
#    def test_srt_to_srt_unicode_conversion(self):
#        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT_UNICODE)


class SCCtoDFXPTestCase(unittest.TestCase):
    def test_scc_to_dfxp(self):
        caption_set = SCCReader().read(SAMPLE_SCC_MULTIPLE_POSITIONING)
        dfxp = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertEqual(SAMPLE_DFXP_FROM_SCC_OUTPUT, dfxp)

    def test_dfxp_is_valid_xml_when_scc_source_has_weird_italic_commands(self):
        caption_set = SCCReader().read(
            SAMPLE_SCC_CREATED_DFXP_WITH_WRONGLY_CLOSING_SPANS)

        dfxp = DFXPWriter().write(caption_set)
        self.assertEqual(dfxp, SAMPLE_DFXP_WITH_PROPERLY_CLOSING_SPANS_OUTPUT)


class SCCToWebVTTTestCase(unittest.TestCase):
    def test_webvtt_newlines_are_properly_rendered(self):
        caption_set = SCCReader().read(
            SCC_THAT_GENERATES_WEBVTT_WITH_PROPER_NEWLINES)
        webvtt = WebVTTWriter().write(caption_set)

        self.assertEqual(
            webvtt,
            SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES_OUTPUT
        )


class SCCEOCNewlineTest(unittest.TestCase):
    def test_eoc_on_newline_rejection(self):
        with self.assertRaises(ValueError):
            caption_set = SCCReader().read(SAMPLE_SCC_FLASHING_CAPTIONS)
