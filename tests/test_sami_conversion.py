import unittest

from pycaption import (
    SAMIReader, SAMIWriter, SRTWriter, DFXPWriter, WebVTTWriter)

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8,
    SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE, SAMPLE_WEBVTT,
    SAMPLE_SRT_UNICODE, SAMPLE_SAMI_SYNTAX_ERROR)
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn, WebVTTTestingMixIn


class SAMIConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI.decode('utf-8'))
        self.captions_utf8 = SAMIReader().read(SAMPLE_SAMI_UTF8.decode('utf-8'))
        self.captions_unicode = SAMIReader().read(SAMPLE_SAMI_UNICODE)


class SAMItoSAMITestCase(SAMIConversionTestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI.decode('utf-8'), results)

    def test_sami_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)

    def test_sami_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class SAMItoSRTTestCase(SAMIConversionTestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT.decode('utf-8'), results)

    def test_sami_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)

    def test_sami_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertSRTEquals(SAMPLE_SRT_UNICODE, results)


class SAMItoDFXPTestCase(SAMIConversionTestCase, DFXPTestingMixIn):

    def test_sami_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP.decode('utf-8'), results)

    def test_sami_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)

    def test_sami_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)

    def test_sami_to_dfxp_xml_output(self):
        captions = SAMIReader().read(SAMPLE_SAMI_SYNTAX_ERROR)
        results = DFXPWriter().write(captions)
        self.assertEquals(type(results), unicode)
        self.assertTrue('xmlns="http://www.w3.org/ns/ttml"' in results)
        self.assertTrue(
            'xmlns:tts="http://www.w3.org/ns/ttml#styling"' in results)


class SAMItoWebVTTTestCase(SAMIConversionTestCase, WebVTTTestingMixIn):

    def test_sami_to_webvtt_utf8_conversion(self):
        results = WebVTTWriter().write(self.captions_utf8)
        self.assertEquals(type(results), unicode)
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode('utf-8'), results)

    def test_sami_to_webvtt_unicode_conversion(self):
        results = WebVTTWriter().write(self.captions_unicode)
        self.assertEquals(type(results), unicode)
        self.assertWebVTTEquals(SAMPLE_WEBVTT.decode('utf-8'), results)


class SAMIWithMissingLanguage(unittest.TestCase, SAMITestingMixIn):

    def setUp(self):
        self.sample_sami = """
        <SAMI>
        <Head><STYLE TYPE="text/css"></Style></Head>
        <BODY>
        <Sync Start=0><P Class=ENCC></p></sync>
        <Sync Start=1301><P Class=ENCC>>> FUNDING FOR OVERHEARD</p></sync>
        </Body>
        </SAMI>
        """

        self.sample_sami_with_lang = """
        <sami>
        <head>
        <style type="text/css"><!--.en-US {lang: en-US;}--></style>
        </head>
        <body>
        <sync start="1301"><p class="en-US">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
        </body>
        </sami>
        """

    def test_sami_to_sami_conversion(self):
        captions = SAMIReader().read(self.sample_sami)
        results = SAMIWriter().write(captions)
        self.assertEquals(type(results), unicode)
        self.assertSAMIEquals(self.sample_sami_with_lang, results)
        self.assertTrue("lang: en-US;" in results)
