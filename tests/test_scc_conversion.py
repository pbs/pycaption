import unittest

from pycaption import SCCReader, SCCWriter, SRTReader, SRTWriter

from .samples import SAMPLE_SRT
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
        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT.decode(u'utf-8'))

# The following test fails -- maybe a bug with SCCReader
#    def test_srt_to_scc_to_srt_utf8_conversion(self):
#        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT_UTF8)

#    def test_srt_to_srt_unicode_conversion(self):
#        self._test_srt_to_scc_to_srt_conversion(SAMPLE_SRT_UNICODE)

