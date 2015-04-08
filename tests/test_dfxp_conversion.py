import unittest

from bs4 import BeautifulSoup

from pycaption import (
    DFXPReader, DFXPWriter, SRTWriter, SAMIWriter, WebVTTWriter)

from pycaption.dfxp import (
    DFXP_DEFAULT_STYLE, DFXP_DEFAULT_STYLE_ID,
    DFXP_DEFAULT_REGION, DFXP_DEFAULT_REGION_ID, _recreate_style,
    _convert_layout_to_attributes)
from .samples import (
    SAMPLE_SAMI, SAMPLE_SRT, SAMPLE_DFXP,
    SAMPLE_DFXP_UTF8, SAMPLE_SAMI_UNICODE, SAMPLE_DFXP_UNICODE,
    SAMPLE_SRT_UNICODE, SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE,
    SAMPLE_WEBVTT_FROM_DFXP, SAMPLE_DFXP_WITH_POSITIONING,
    SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING)

from .mixins import (
    SRTTestingMixIn, SAMITestingMixIn, DFXPTestingMixIn, WebVTTTestingMixIn)


class DFXPConversionTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))
        cls.captions_utf8 = DFXPReader().read(SAMPLE_DFXP_UTF8.decode(u'utf-8'))
        cls.captions_unicode = DFXPReader().read(SAMPLE_DFXP_UNICODE)
        cls.captions_without_style_and_region = DFXPReader().read(
            SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE.decode(u'utf-8'))
        cls.captions_with_positioning = DFXPReader().read(
            SAMPLE_DFXP_WITH_POSITIONING.decode('utf-8'))


class DFXPtoDFXPTestCase(DFXPConversionTestCase, DFXPTestingMixIn):

    def test_dfxp_to_dfxp_conversion(self):
        results = DFXPWriter().write(self.captions)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(
            SAMPLE_DFXP_TO_DFXP_OUTPUT.decode(u'utf-8'), results)

    def test_dfxp_to_dfxp_utf8_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_UTF8.decode(u'utf-8'))
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE_OUTPUT, results)

    def test_dfxp_to_dfxp_unicode_conversion(self):
        results = DFXPWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP_UNICODE_OUTPUT, results)

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

        soup = BeautifulSoup(result, u'xml')
        region = soup.find(u'region', {u'xml:id': DFXP_DEFAULT_REGION_ID})

        default_region = _convert_layout_to_attributes(DFXP_DEFAULT_REGION)
        default_region[u'xml:id'] = DFXP_DEFAULT_REGION_ID

        self.assertTrue(region)
        self.assertEquals(region.attrs[u'xml:id'], DFXP_DEFAULT_REGION_ID)
        self.assertEqual(region.attrs, default_region)

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
        # The arguments used here illustrate how we will try to read
        # and write incorrectly specified positioning information.
        # By incorrect, I mean the specs say that those attributes should be
        # ignored, not that the attributes themselves are outside of the specs
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT
        )
        result = DFXPWriter(write_inline_positioning=True).write(caption_set)
        self.assertEqual(result,
                         SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_OUTPUT)

    def test_dont_create_style_tags_with_no_id(self):
        # The <style> tags can have no 'xml:id' attribute. Previously, in this
        # case, the style was copied to the output file, with the 'xml:id'
        # property declared, but no value assigned to it. Since such a style
        # can not be referred anyway, and <style> elements, children of
        # <region> tags shouldn't be referred to anyway, we don't include
        # these styles in the output file
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_INPUT)
        result = DFXPWriter().write(caption_set)
        self.assertEqual(result, SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_OUTPUT)


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
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP.decode(u'utf-8'), results)

    def test_dfxp_to_webvtt_unicode_conversion(self):
        results = WebVTTWriter().write(self.captions_unicode)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP.decode(u'utf-8'), results)

    def test_dfxp_with_positioning_to_webvtt_conversion(self):
        results = WebVTTWriter(
            video_width=638, video_height=360
        ).write(self.captions_with_positioning)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING.decode(u'utf-8'), results)

SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontFamily="Arial"
          tts:fontSize="10pt" tts:textAlign="center"/>
  </styling>
  <layout>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p tts:origin="17.5% 10%" tts:extent="62.5% 5.33%" begin="0:00:02.777" end="0:00:05.700">
   Hello there!
   </p>
   <p tts:origin="20% 15.67%" tts:extent="30% 7.67%" begin="0:00:05.700" end="0:00:06.210">
   How are you?<span tts:origin="1px 2px">>>Fine, thx<<</span>
   </p>
   <p tts:extent="60% 22%" begin="0:00:07.900" end="0:00:08.900" tts:textAlign="right" tts:displayAlign="before">
   Just fine?
   </p>
   <p tts:origin="11% 11%" begin="0:00:09.900" end="0:00:10.800">
    <span weirdAttribute="1" tts:textAlign="right">>>>Lol, yes!</span>
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="62.5% 5.33%" tts:origin="17.5% 10%" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="20% 15.67%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="1px 2px" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="before" tts:extent="60% 22%" tts:textAlign="right" xml:id="r3"/>
   <region tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="center" xml:id="r4"/>
   <region tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="right" xml:id="r5"/>
  </layout>
 </head>
 <body>
  <div region="bottom" tts:displayAlign="after" tts:textAlign="center" xml:lang="en-US">
   <p begin="00:00:02.777" end="00:00:05.700" region="r0" style="p" tts:displayAlign="after" tts:extent="62.5% 5.33%" tts:origin="17.5% 10%" tts:textAlign="center">
    Hello there!
   </p>
   <p begin="00:00:05.700" end="00:00:06.210" region="r1" style="p" tts:displayAlign="after" tts:extent="30% 7.67%" tts:origin="20% 15.67%" tts:textAlign="center">
    How are you? <span region="r2" tts:origin="1px 2px" tts:textAlign="center" tts:extent="30% 7.67%" tts:displayAlign="after">&gt;&gt;Fine, thx&lt;&lt;</span>
   </p>
   <p begin="00:00:07.900" end="00:00:08.900" region="r3" style="p" tts:displayAlign="before" tts:extent="60% 22%" tts:textAlign="right">
    Just fine?
   </p>
   <p begin="00:00:09.900" end="00:00:10.800" region="r4" style="p" tts:displayAlign="after" tts:origin="11% 11%" tts:textAlign="center">
    <span tts:textAlign="right" region="r5" tts:origin="11% 11%" tts:textAlign="right" tts:displayAlign="after">&gt;&gt;&gt;Lol, yes!</span>
   </p>
  </div>
 </body>
</tt>"""


SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT = u"""
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style xml:id="p" tts:color="#ffeedd" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
    <style xml:id="referential_style2" tts:extent="3em 4em"/>
    <style xml:id="referential_style1" tts:padding="3px 4px 5px" style="referential_style2"/>
  </styling>
  <layout>
   <region tts:textAlign="center" xml:id="pixel_region">
    <style tts:origin="40px 50px" tts:extent="30px 40px"/>
   </region>
   <region tts:origin="10% 30%" tts:extent="50% 50%" xml:id="percent_region"/>
   <region tts:padding="2c" xml:id="padding_region" />
   <region xml:id="referential_region" style="referential_style1"/>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p region="pixel_region" begin="0:00:02.700" end="0:00:05.700">
   Hello there!
   </p>
   <p region="percent_region" begin="0:00:05.700" end="0:00:06.210">
   How are you?
   </p>
   <p region="padding_region" begin="0:00:07.700" end="0:00:09.210">
   >> I'm fine, thank you << replied someone.
   <span region="percent_region">
    >>And now we're going to have fun<<
    </span>
   </p>
   <p region="referential_region" begin="0:00:10.707" end="0:00:11.210">
   What do you have in mind?
   </p>
   <p begin="0:00:12.900" end="0:00:13.900" tts:textAlign="start"
        tts:displayAlign="after">
   To write random words here!
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:extent="30px 40px" tts:origin="40px 50px" tts:textAlign="center" xml:id="r0"/>
   <region tts:displayAlign="after" tts:extent="50% 50%" tts:origin="10% 30%" tts:textAlign="center" xml:id="r1"/>
   <region tts:displayAlign="after" tts:padding="2c 2c 2c 2c" tts:textAlign="center" xml:id="r2"/>
   <region tts:displayAlign="after" tts:extent="3em 4em" tts:padding="3px 4px 5px 4px" tts:textAlign="center" xml:id="r3"/>
   <region tts:displayAlign="after" tts:textAlign="start" xml:id="r4"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:02.700" end="00:00:05.700" region="r0" style="p">
    Hello there!
   </p>
   <p begin="00:00:05.700" end="00:00:06.210" region="r1" style="p">
    How are you?
   </p>
   <p begin="00:00:07.700" end="00:00:09.210" region="r2" style="p">
    &gt;&gt; I'm fine, thank you &lt;&lt; replied someone. <span region="r1">&gt;&gt;And now we're going to have fun&lt;&lt;</span>
   </p>
   <p begin="00:00:10.707" end="00:00:11.210" region="r3" style="p">
    What do you have in mind?
   </p>
   <p begin="00:00:12.900" end="00:00:13.900" region="r4" style="p" tts:textAlign="start">
    To write random words here!
   </p>
  </div>
 </body>
</tt>"""

##
# When converting from DFXP to DFXP, notice the extra region "r0" is added, to
# support the spam that sets the "tts:textAlign" attribute.
# This attribute is meaningless on the <span> tag, and should affect only <p>
# tags. It's a feature that should affect only only those players that don't
# conform to the specs.
SAMPLE_DFXP_TO_DFXP_OUTPUT = """\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="right" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right" region="r0">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:34.400" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
   <p begin="00:00:34.400" end="00:00:38.400" region="bottom" style="p">
    some more text
   </p>
  </div>
 </body>
</tt>"""


SAMPLE_DFXP_UNICODE_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" tts:textAlign="center" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="right" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    \u266a ...say bow, wow, \u266a
   </p>
   <p begin="00:00:17.000" end="00:00:18.752" region="bottom" style="p">
    <span tts:textAlign="right" region="r0">we have this vision of Einstein</span>
   </p>
   <p begin="00:00:18.752" end="00:00:20.887" region="bottom" style="p">
    <br/>
    as an old, wrinkly man<br/>
    with white hair.
   </p>
   <p begin="00:00:20.887" end="00:00:26.760" region="bottom" style="p">
    MAN 2:<br/>
    E equals m c-squared is<br/>
    not about an old Einstein.
   </p>
   <p begin="00:00:26.760" end="00:00:32.200" region="bottom" style="p">
    MAN 2:<br/>
    It's all about an eternal Einstein.
   </p>
   <p begin="00:00:32.200" end="00:00:36.200" region="bottom" style="p">
    &lt;LAUGHING &amp; WHOOPS!&gt;
   </p>
  </div>
 </body>
</tt>"""

SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_INPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" xml:id="r0">
    <style tts:textAlign="start"/>
   </region>
  </layout>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="r0" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
  </div>
 </body>
</tt>
"""

SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_OUTPUT = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style tts:color="#ffeedd" tts:fontFamily="Arial" tts:fontSize="10pt" xml:id="p"/>
  </styling>
  <layout>
   <region tts:displayAlign="after" tts:textAlign="center" xml:id="bottom"/>
   <region tts:displayAlign="after" tts:textAlign="start" xml:id="r0"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="r0" style="p">
    ( clock ticking )
   </p>
   <p begin="00:00:14.848" end="00:00:17.000" region="bottom" style="p">
    MAN:<br/>
    When we think<br/>
    of "E equals m c-squared",
   </p>
  </div>
 </body>
</tt>"""