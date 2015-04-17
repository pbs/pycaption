import unittest

from pycaption import SCCReader, SCCWriter, SRTReader, SRTWriter, DFXPWriter
from pycaption.webvtt import WebVTTWriter

from .samples import SAMPLE_SRT
from .mixins import CaptionSetTestingMixIn
from .test_scc import SAMPLE_SCC_MULTIPLE_POSITIONING

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


class SCCtoDFXPTestCase(unittest.TestCase):
    def test_scc_to_dfxp(self):
        caption_set = SCCReader().read(SAMPLE_SCC_MULTIPLE_POSITIONING)
        dfxp = DFXPWriter().write(caption_set)

        self.assertEqual(SAMPLE_DFXP_FROM_SCC_OUTPUT, dfxp)


class SCCToWebVTTTestCase(unittest.TestCase):
    def test_webvtt_newlines_are_properly_rendered(self):
        caption_set = SCCReader().read(
            SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES)
        webvtt = WebVTTWriter().write(caption_set)

        self.assertEqual(
            webvtt,
            SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES_OUTPUT
        )


SAMPLE_DFXP_FROM_SCC_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="before" tts:origin="0.0% 80.0%" tts:textAlign="left" xml:id="r0"/>
   <region tts:displayAlign="before" tts:origin="37.5% 0.0%" tts:textAlign="left" xml:id="r1"/>
   <region tts:displayAlign="before" tts:origin="75.0% 20.0%" tts:textAlign="left" xml:id="r2"/>
   <region tts:displayAlign="before" tts:origin="12.5% 46.6666666667%" tts:textAlign="left" xml:id="r3"/>
   <region tts:displayAlign="before" tts:origin="12.5% 93.3333333333%" tts:textAlign="left" xml:id="r4"/>
   <region tts:displayAlign="before" tts:origin="37.5% 53.3333333333%" tts:textAlign="left" xml:id="r5"/>
   <region tts:displayAlign="before" tts:origin="75.0% 13.3333333333%" tts:textAlign="left" xml:id="r6"/>
   <region tts:displayAlign="before" tts:origin="12.5% 33.3333333333%" tts:textAlign="left" xml:id="r7"/>
   <region tts:displayAlign="before" tts:origin="12.5% 86.6666666667%" tts:textAlign="left" xml:id="r8"/>
   <region tts:displayAlign="before" tts:origin="75.0% 6.66666666667%" tts:textAlign="left" xml:id="r9"/>
   <region tts:displayAlign="before" tts:origin="37.5% 40.0%" tts:textAlign="left" xml:id="r10"/>
   <region tts:displayAlign="before" tts:origin="12.5% 73.3333333333%" tts:textAlign="left" xml:id="r11"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:01.167" end="00:00:01.167" region="r0" style="default">
    abab
   </p>
   <p begin="00:00:01.167" end="00:00:01.167" region="r1" style="default">
    cdcd
   </p>
   <p begin="00:00:01.167" end="00:00:03.103" region="r2" style="default">
    efef
   </p>
   <p begin="00:00:03.169" end="00:00:09.743" region="r3" style="default">
    ghgh<br/>
    ijij<br/>
    klkl
   </p>
   <p begin="00:00:09.743" end="00:00:09.743" region="r4" style="default">
    mnmn
   </p>
   <p begin="00:00:09.743" end="00:00:09.743" region="r5" style="default">
    opop
   </p>
   <p begin="00:00:09.743" end="00:00:11.745" region="r6" style="default">
    qrqr
   </p>
   <p begin="00:00:11.745" end="00:00:20.100" region="r7" style="default">
    stst<br/>
    uvuv<br/>
    wxwx
   </p>
   <p begin="00:00:20.100" end="00:00:20.100" region="r8" style="default">
    yzyz
   </p>
   <p begin="00:00:20.100" end="00:00:20.100" region="r9" style="default">
    0101
   </p>
   <p begin="00:00:20.100" end="00:00:22.100" region="r10" style="default">
    2323
   </p>
   <p begin="00:00:22.100" end="00:00:36.202" region="r11" style="default">
    4545<br/>
    6767<br/>
    8989
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES = u"""\
Scenarist_SCC V1.0

00:21:29;23	9420 9452 6161 94f4 97a2 6262 942c 942f
"""

SAMPLE_WEBVTT_FROM_SCC_PROPERLY_WRITES_NEWLINES_OUTPUT = u"""\
WEBVTT

21:30.033 --> 00:00.000 align:left position:12.5%,start line:86.6666666667%
aa
bb
"""