import unittest

from pycaption import SAMIReader, SAMIWriter, SRTWriter, DFXPWriter

from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_SAMI_UTF8, SAMPLE_SRT_UTF8, SAMPLE_DFXP_UTF8,
    SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE
)
from .mixins import SRTTestingMixIn, DFXPTestingMixIn, SAMITestingMixIn


class SAMIConversionTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI)
        self.captions_utf8 = SAMIReader().read(SAMPLE_SAMI_UTF8)
        self.captions_unicode = SAMIReader().read(SAMPLE_SAMI_UNICODE)


class SAMItoSAMITestCase(SAMIConversionTestCase, SAMITestingMixIn):

    def test_sami_to_sami_conversion(self):
        results = SAMIWriter().write(self.captions)
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_sami_to_sami_utf8_conversion(self):
        results = SAMIWriter().write(self.captions_utf8)
        self.assertSAMIEquals(SAMPLE_SAMI_UTF8, results)

    def test_sami_to_sami_unicode_conversion(self):
        results = SAMIWriter().write(self.captions_unicode)
        self.assertSAMIEquals(SAMPLE_SAMI_UNICODE, results)


class SAMItoSRTTestCase(SAMIConversionTestCase, SRTTestingMixIn):

    def test_sami_to_srt_conversion(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)

    def test_sami_to_srt_utf8_conversion(self):
        results = SRTWriter().write(self.captions_utf8)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)

    def test_sami_to_srt_unicode_conversion(self):
        results = SRTWriter().write(self.captions_unicode)
        self.assertSRTEquals(SAMPLE_SRT_UTF8, results)


class SAMItoDFXPTestCase(SAMIConversionTestCase, DFXPTestingMixIn):

    def test_sami_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertDFXPEquals(SAMPLE_DFXP, results)

    def test_sami_to_dfxp_utf8_conversion(self):
        results = DFXPWriter().write(self.captions_utf8)
        self.assertDFXPEquals(SAMPLE_DFXP_UTF8, results)

    def test_sami_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE, results)


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
        <style type="text/css"><!--.unknown {lang: unknown;}--></style>
        </head>
        <body>
        <sync start="1301"><p class="unknown">&gt;&gt; FUNDING FOR OVERHEARD</p></sync>
        </body>
        </sami>
        """

    def test_sami_to_sami_conversion(self):
        captions = SAMIReader().read(self.sample_sami)
        results = SAMIWriter().write(captions)
        self.assertSAMIEquals(self.sample_sami_with_lang, results)
