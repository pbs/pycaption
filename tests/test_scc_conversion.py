import unittest

from pycaption import SCCReader, SCCWriter, SRTReader, SRTWriter, DFXPWriter

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

    def test_dfxp_is_valid_xml_when_scc_source_has_weird_italic_commands(self):
        caption_set = SCCReader().read(
            SAMPLE_SCC_CREATED_DFXP_WITH_WRONGLY_CLOSING_SPANS)

        dfxp = DFXPWriter().write(caption_set)
        self.assertEqual(dfxp, SAMPLE_DFXP_WITH_PROPERLY_CLOSING_SPANS_OUTPUT)


SAMPLE_DFXP_FROM_SCC_OUTPUT = u"""<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:origin="0.0% 80.0%" xml:id="r0"/>
   <region tts:origin="37.5% 0.0%" xml:id="r1"/>
   <region tts:origin="75.0% 20.0%" xml:id="r2"/>
   <region tts:origin="12.5% 46.6666666667%" xml:id="r3"/>
   <region tts:origin="12.5% 93.3333333333%" xml:id="r4"/>
   <region tts:origin="37.5% 53.3333333333%" xml:id="r5"/>
   <region tts:origin="75.0% 13.3333333333%" xml:id="r6"/>
   <region tts:origin="12.5% 33.3333333333%" xml:id="r7"/>
   <region tts:origin="12.5% 86.6666666667%" xml:id="r8"/>
   <region tts:origin="75.0% 6.66666666667%" xml:id="r9"/>
   <region tts:origin="37.5% 40.0%" xml:id="r10"/>
   <region tts:origin="12.5% 73.3333333333%" xml:id="r11"/>
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

SAMPLE_SCC_CREATED_DFXP_WITH_WRONGLY_CLOSING_SPANS = u"""\
Scenarist_SCC V1.0

00:01:28;09 9420 942f 94ae 9420 9452 97a2 e3e3 e3e3 e3e3 9470 9723 e3a1 e3a1

00:01:31;10 9420 942f 94ae

00:01:31;18 9420 9454 6262 6262 9458 97a1 91ae e3e3 e3e3 9470 97a1 6262 6161

00:01:35;18 9420 942f 94ae

00:01:40;25 942c

00:01:51;18 9420 9452 97a1 6161 94da 97a2 91ae 6262 9470 97a1 e3e3

00:01:55;22 9420 942f 6162 e364 94f4 9723 6162 e364

00:01:59;14 9420 942f 94ae 9420 94f4 6464 6464
"""

SAMPLE_DFXP_WITH_PROPERLY_CLOSING_SPANS_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="white" tts:fontFamily="monospace" tts:fontSize="1c" xml:id="default"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:origin="12.5% 86.6666666667%" xml:id="r0"/>
   <region tts:origin="25.0% 86.6666666667%" xml:id="r1"/>
   <region tts:origin="50.0% 86.6666666667%" xml:id="r2"/>
   <region tts:origin="62.5% 86.6666666667%" xml:id="r3"/>
   <region tts:origin="25.0% 93.3333333333%" xml:id="r4"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:01:31.400" end="00:01:35.666" region="r0" style="default">
    cccccc<br/>
    c!c!
   </p>
   <p begin="00:01:35.666" end="00:01:35.666" region="r1" style="default">
    bbbb
   </p>
   <p begin="00:01:35.666" end="00:01:40.866" region="r2" style="default">
    <span tts:fontStyle="italic" region="r2">cccc<br/>
    bbaa</span>
   </p>
   <p begin="00:01:55.800" end="00:01:55.800" region="r0" style="default">
    aa
   </p>
   <p begin="00:01:55.800" end="00:01:59.533" region="r3" style="default">
    <span tts:fontStyle="italic" region="r3">bb<br/>
    cc</span>
   </p>
   <p begin="00:01:59.533" end="00:01:59.533" region="r3" style="default">
    abcd
   </p>
   <p begin="00:01:59.533" end="00:01:59.533" region="r4" style="default">
    abcd
   </p>
   <p begin="00:01:59.533" end="00:01:59.700" region="r4" style="default">
    dddd
   </p>
  </div>
 </body>
</tt>"""