import unittest
from copy import deepcopy
from bs4 import BeautifulSoup

from pycaption.dfxp import (SinglePositioningDFXPWriter, DFXPReader,
                            DFXP_DEFAULT_REGION, DFXP_DEFAULT_REGION_ID)
from pycaption.geometry import (
    HorizontalAlignmentEnum, VerticalAlignmentEnum, Layout, Alignment)

from pycaption.dfxp.base import _create_internal_alignment


class SinglePositioningDFXPWRiterTestCase(unittest.TestCase):
    def test_only_the_default_region_is_created(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

        dfxp = SinglePositioningDFXPWriter().write(caption_set)
        layout = BeautifulSoup(dfxp, features='html.parser').findChild('layout')  # noqa

        self.assertEqual(len(layout.findChildren('region')), 1)

    def test_only_the_default_region_is_referenced(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

        dfxp = SinglePositioningDFXPWriter().write(caption_set)

        soup = BeautifulSoup(dfxp, features='html.parser')

        for elem in soup.findAll():
            if 'region' in elem.attrs:
                self.assertEqual(elem['region'], DFXP_DEFAULT_REGION_ID)

    def test_only_the_custom_region_is_created(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

        new_region = Layout(
            alignment=Alignment(
                HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP
            )
        )

        dfxp = SinglePositioningDFXPWriter(new_region).write(caption_set)
        # Using a different parser, because this preserves letter case
        # The output file is ok, but when parsing it, the "regular" parses
        # loses letter case.
        layout = BeautifulSoup(dfxp, features='xml').findChild('layout')

        self.assertEqual(len(layout.findChildren('region')), 1)

        region = layout.findChild('region')
        text_align = region['tts:textAlign']
        display_align = region['tts:displayAlign']

        internal_alignment = _create_internal_alignment(text_align, display_align)  # noqa
        self.assertEqual(internal_alignment.horizontal, HorizontalAlignmentEnum.LEFT)  # noqa
        self.assertEqual(internal_alignment.vertical, VerticalAlignmentEnum.TOP)  # noqa

    def test_only_the_specified_custom_attributes_are_created_for_the_region(self):  # noqa
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

        new_region = Layout(
            alignment=Alignment(
                HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP
            )
        )

        dfxp = SinglePositioningDFXPWriter(new_region).write(caption_set)

        region = BeautifulSoup(dfxp).find('region')
        self.assertTrue('xml:id' in region.attrs)
        self.assertNotEqual(region.attrs['xml:id'], DFXP_DEFAULT_REGION_ID)
        self.assertEqual(len(region.attrs), 3)

    def test_only_the_custom_region_is_referenced(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

        # it's easier to copy this than create a new one
        new_region = deepcopy(DFXP_DEFAULT_REGION)
        new_region.alignment.horizontal = HorizontalAlignmentEnum.LEFT
        new_region.alignment.vertical = VerticalAlignmentEnum.TOP

        dfxp = SinglePositioningDFXPWriter(new_region).write(caption_set)

        soup = BeautifulSoup(dfxp, features='html.parser')

        # get the region_id created, and see it's the one referenced
        created_region_id = soup.find('region')['xml:id']

        referenced_region_ids = set()

        for elem in soup.findAll():
            if 'region' in elem.attrs:
                referenced_region_ids.add(elem.attrs['region'])

        self.assertEqual(len(referenced_region_ids), 1)
        self.assertEqual(referenced_region_ids.pop(), created_region_id)


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
    &gt;&gt; I'm fine, thank you &lt;&lt; replied someone.<span region="r1">&gt;&gt;And now we're going to have fun&lt;&lt;</span>
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