import unittest

from pycaption import (
    SRTReader, SRTWriter, SAMIWriter, DFXPWriter, WebVTTWriter, MicroDVDWriter)

from tests.samples.dfxp import SAMPLE_DFXP
from tests.samples.srt import SAMPLE_SRT
from tests.samples.sami import SAMPLE_SAMI
from tests.samples.webvtt import SAMPLE_WEBVTT_FROM_SRT

from tests.mixins import (
    SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn, MicroDVDTestingMixIn)

from .samples.microdvd import SAMPLE_MICRODVD


class SRTtoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_srt_to_srt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, str))
        self.assertSRTEquals(SAMPLE_SRT, results)


class SRTtoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_srt_to_sami_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, str))
        self.assertSAMIEquals(SAMPLE_SAMI, results)


class SRTtoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_srt_to_dfxp_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, str))
        self.assertDFXPEquals(
            SAMPLE_DFXP, results,
            ignore_styling=True, ignore_spans=True
        )


class SRTtoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_srt_to_webvtt_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, str))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_SRT, results)


class SRTtoMicroDVDTestCase(unittest.TestCase, MicroDVDTestingMixIn):

    def test_srt_to_microdvd_conversion(self):
        caption_set = SRTReader().read(SAMPLE_SRT)
        results = MicroDVDWriter().write(caption_set)
        self.assertTrue(isinstance(results, str))
        self.assertMicroDVDEquals(SAMPLE_MICRODVD, results)
