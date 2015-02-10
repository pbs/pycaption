import unittest

from bs4 import BeautifulSoup

from pycaption import (
    DFXPReader, DFXPWriter, SRTWriter, SAMIWriter, WebVTTWriter)

from pycaption.dfxp import (
    DFXP_DEFAULT_STYLE, DFXP_DEFAULT_STYLE_ID,
    DFXP_DEFAULT_REGION, DFXP_DEFAULT_REGION_ID, _recreate_style)
from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_DFXP_UTF8, SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE,
    SAMPLE_SRT_UNICODE, SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE)
from .mixins import SRTTestingMixIn, SAMITestingMixIn, DFXPTestingMixIn, WebVTTTestingMixIn

from tests.samples import (
    SAMPLE_WEBVTT_OUTPUT,
    SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT, SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT,
    SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT
)


class DFXPConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))
        cls.captions_utf8 = DFXPReader().read(SAMPLE_DFXP_UTF8.decode(u'utf-8'))
        cls.captions_unicode = DFXPReader().read(SAMPLE_DFXP_UNICODE)
        cls.captions_without_style_and_region = DFXPReader().read(
            SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE.decode(u'utf-8'))


class DFXPtoDFXPTestCase(DFXPConversionTestCase, DFXPTestingMixIn):

    def test_dfxp_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP.decode(u'utf-8'), results)

    def test_dfxp_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)

    def test_dfxp_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)

    def test_default_styling_tag(self):
        w = DFXPWriter()
        result = w.write(self.captions_without_style_and_region)

        default_style = _recreate_style(DFXP_DEFAULT_STYLE, None)
        default_style[u'xml:id'] = DFXP_DEFAULT_STYLE_ID

        soup = BeautifulSoup(result, u'xml')
        style = soup.find(u'style', {u'xml:id': DFXP_DEFAULT_STYLE_ID})

        self.assertTrue(style)
        self.assertEquals(style.attrs, default_style)

    def test_default_styling_p_tags(self):
        w = DFXPWriter()
        result = w.write(self.captions)

        soup = BeautifulSoup(result, u'xml')
        for p in soup.find_all(u'p'):
            self.assertEquals(p.attrs.get(u'style'), 'p')

    def test_default_region_tag(self):
        w = DFXPWriter()
        result = w.write(self.captions)

        default_region = _recreate_style(DFXP_DEFAULT_REGION, None)
        default_region[u'xml:id'] = DFXP_DEFAULT_REGION_ID

        soup = BeautifulSoup(result, u'xml')
        region = soup.find(u'region', {u'xml:id': DFXP_DEFAULT_REGION_ID})

        self.assertTrue(region)
        self.assertEquals(region.attrs, default_region)

    def test_default_region_p_tags(self):
        w = DFXPWriter()
        result = w.write(self.captions)

        soup = BeautifulSoup(result, u'xml')
        for p in soup.find_all(u'p'):
            self.assertEquals(p.attrs.get(u'region'), DFXP_DEFAULT_REGION_ID)

    def test_correct_region_attributes_are_recreated(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT)
        result = DFXPWriter().write(caption_set)
        self.assertDFXPEquals(result, SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

    def test_incorrectly_specified_positioning_is_explicitly_accepted(self):
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT
        )
        result = DFXPWriter().write(caption_set)


class DFXPtoSRTTestCase(DFXPConversionTestCase, SRTTestingMixIn):

    def test_dfxp_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT.decode(u'utf-8'), results)

    def test_dfxp_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

    def test_dfxp_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)


class DFXPtoSAMITestCase(DFXPConversionTestCase, SAMITestingMixIn):

    def test_dfxp_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI.decode(u'utf-8'), results)

    def test_dfxp_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_dfxp_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class DFXPtoWebVTTTestCase(DFXPConversionTestCase, WebVTTTestingMixIn):

    def test_dfxp_to_webvtt_conversion(self):
        results = WebVTTWriter().write(self.captions_utf8)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_OUTPUT.decode(u'utf-8'), results)

    def test_dfxp_to_webvtt_unicode_conversion(self):
        results = WebVTTWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_OUTPUT.decode(u'utf-8'), results)
