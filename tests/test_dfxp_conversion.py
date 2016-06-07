# -*- coding: utf-8 -*-

import unittest

from bs4 import BeautifulSoup

from pycaption import (
    DFXPReader, DFXPWriter, SRTWriter, SAMIWriter, WebVTTWriter)

from pycaption.dfxp.extras import LegacyDFXPWriter

from pycaption.dfxp.base import (
    DFXP_DEFAULT_STYLE, DFXP_DEFAULT_STYLE_ID, DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID, _recreate_style, _convert_layout_to_attributes
)

from .samples.dfxp import (
    SAMPLE_DFXP, SAMPLE_DFXP_WITH_INLINE_STYLE, SAMPLE_DFXP_WITH_DEFINED_STYLE,
    SAMPLE_DFXP_WITH_INHERITED_STYLE,
    SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE, SAMPLE_DFXP_WITH_POSITIONING,
    SAMPLE_DFXP_WITH_RELATIVIZED_POSITIONING, SAMPLE_DFXP_LONG_CUE,
    SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS, DFXP_STYLE_REGION_ALIGN_CONFLICT,
    SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT,
    SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_OUTPUT,
    SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT, SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT,
    SAMPLE_DFXP_OUTPUT, SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_INPUT,
    SAMPLE_DFXP_STYLE_TAG_WITH_NO_XML_ID_OUTPUT,
    SAMPLE_DFXP_LONG_CUE_FIT_TO_SCREEN, SAMPLE_DFXP_FOR_LEGACY_WRITER_INPUT,
    SAMPLE_DFXP_FOR_LEGACY_WRITER_OUTPUT, DFXP_WITH_ESCAPED_APOSTROPHE
)
from .samples.sami import SAMPLE_SAMI
from .samples.srt import SAMPLE_SRT
from .samples.webvtt import (
    SAMPLE_WEBVTT_FROM_DFXP, SAMPLE_WEBVTT_FROM_DFXP_WITH_STYLE,
    SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING_AND_STYLE,
    SAMPLE_WEBVTT_OUTPUT_LONG_CUE, WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN
)

from .mixins import (
    SRTTestingMixIn, SAMITestingMixIn, DFXPTestingMixIn, WebVTTTestingMixIn)

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class DFXPtoDFXPTestCase(unittest.TestCase, DFXPTestingMixIn):

    def test_dfxp_to_dfxp_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        results = DFXPWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertDFXPEquals(SAMPLE_DFXP_OUTPUT, results)

    def test_default_styling_tag(self):
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_WITHOUT_REGION_AND_STYLE)
        result = DFXPWriter().write(caption_set)

        default_style = _recreate_style(DFXP_DEFAULT_STYLE, None)
        default_style[u'xml:id'] = DFXP_DEFAULT_STYLE_ID

        soup = BeautifulSoup(result, u'xml')
        style = soup.find(u'style', {u'xml:id': DFXP_DEFAULT_STYLE_ID})

        self.assertTrue(style)
        self.assertEquals(style.attrs, default_style)

    def test_default_styling_p_tags(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, u'xml')
        for p in soup.find_all(u'p'):
            self.assertEquals(p.attrs.get(u'style'), 'p')

    def test_default_region_tag(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, u'xml')
        region = soup.find(u'region', {u'xml:id': DFXP_DEFAULT_REGION_ID})

        default_region = _convert_layout_to_attributes(DFXP_DEFAULT_REGION)
        default_region[u'xml:id'] = DFXP_DEFAULT_REGION_ID

        self.assertTrue(region)
        self.assertEquals(region.attrs[u'xml:id'], DFXP_DEFAULT_REGION_ID)
        self.assertEqual(region.attrs, default_region)

    def test_default_region_p_tags(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, u'xml')
        for p in soup.find_all(u'p'):
            self.assertEquals(p.attrs.get(u'region'), DFXP_DEFAULT_REGION_ID)

    def test_correct_region_attributes_are_recreated(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_MULTIPLE_REGIONS_INPUT)
        result = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)
        self.assertDFXPEquals(result, SAMPLE_DFXP_MULTIPLE_REGIONS_OUTPUT)

    def test_incorrectly_specified_positioning_is_explicitly_accepted(self):
        # The arguments used here illustrate how we will try to read
        # and write incorrectly specified positioning information.
        # By incorrect, I mean the specs say that those attributes should be
        # ignored, not that the attributes themselves are outside of the specs
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_INPUT
        )
        result = DFXPWriter(
            relativize=False,
            fit_to_screen=False,
            write_inline_positioning=True).write(caption_set)
        self.assertDFXPEquals(
            result,
            SAMPLE_DFXP_INVALID_BUT_SUPPORTED_POSITIONING_OUTPUT
        )

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

    def test_is_relativized(self):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_WITH_POSITIONING.decode('utf-8'))
        result = DFXPWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)
        self.assertEqual(result, SAMPLE_DFXP_WITH_RELATIVIZED_POSITIONING)

    def test_fit_to_screen(self):
        # Check if caption width and height are is explicitly set and
        # recalculate it if necessary. This prevents long captions from being
        # cut out of the screen.
        caption_set = DFXPReader().read(SAMPLE_DFXP_LONG_CUE)
        result = DFXPWriter().write(caption_set)
        self.assertEqual(result, SAMPLE_DFXP_LONG_CUE_FIT_TO_SCREEN)

    def test_proper_xml_entity_escaping(self):
        caption_set = DFXPReader().read(DFXP_WITH_ESCAPED_APOSTROPHE)
        cue_text = caption_set.get_captions(u'en-US')[0].nodes[0].content
        self.assertEqual(
            cue_text, u"<< \"Andy's Caf\xe9 & Restaurant\" this way")
        result = DFXPWriter().write(caption_set)
        self.assertIn(
            u"&lt;&lt; \"Andy's Café &amp; Restaurant\" this way",
            result
        )


class DFXPtoSRTTestCase(unittest.TestCase, SRTTestingMixIn):

    def test_dfxp_to_srt_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        results = SRTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSRTEquals(SAMPLE_SRT, results)


class DFXPtoSAMITestCase(unittest.TestCase, SAMITestingMixIn):

    def test_dfxp_to_sami_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        results = SAMIWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertSAMIEquals(SAMPLE_SAMI, results)

    def test_dfxp_to_sami_with_margins(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_FROM_SAMI_WITH_MARGINS)
        results = SAMIWriter(video_width=VIDEO_WIDTH,
                             video_height=VIDEO_HEIGHT).write(caption_set)
        margins = [u"margin-right: 6.04%;",
                   u"margin-bottom: 0%;",
                   u"margin-top: 0%;",
                   u"margin-left: 6.04%;"]
        for margin in margins:
            self.assertIn(margin, results)


class DFXPtoWebVTTTestCase(unittest.TestCase, WebVTTTestingMixIn):

    def test_dfxp_to_webvtt_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP, results)

    def test_dfxp_with_inline_style_to_webvtt_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_WITH_INLINE_STYLE)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP_WITH_STYLE, results)

    def test_dfxp_with_defined_style_to_webvtt_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_WITH_DEFINED_STYLE)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP_WITH_STYLE, results)

    def test_dfxp_with_inherited_style_to_webvtt_conversion(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_WITH_INHERITED_STYLE)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(SAMPLE_WEBVTT_FROM_DFXP_WITH_STYLE, results)

    def test_dfxp_with_positioning_to_webvtt_conversion(self):
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_WITH_POSITIONING.decode('utf-8'))
        results = WebVTTWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertWebVTTEquals(
            SAMPLE_WEBVTT_FROM_DFXP_WITH_POSITIONING_AND_STYLE, results)

    def test_dfxp_to_webvtt_adds_explicit_size(self):
        caption_set = DFXPReader().read(SAMPLE_DFXP_LONG_CUE)
        results = WebVTTWriter().write(caption_set)
        self.assertTrue(isinstance(results, unicode))
        self.assertEquals(
            SAMPLE_WEBVTT_OUTPUT_LONG_CUE, results)

    def test_dfxp_to_webvtt_preserves_proper_alignment(self):
        # This failed at one point when the CaptionSet had node breaks with
        # different positioning. It was fixed both at the DFXPReader AND the
        # WebVTTWriter.
        caption_set = DFXPReader().read(DFXP_STYLE_REGION_ALIGN_CONFLICT)
        results = WebVTTWriter().write(caption_set)
        self.assertEquals(
            WEBVTT_FROM_DFXP_WITH_CONFLICTING_ALIGN, results)


class LegacyDFXPTestCase(unittest.TestCase):
    def test_legacy_convert(self):
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            SAMPLE_DFXP_FOR_LEGACY_WRITER_INPUT)

        result = LegacyDFXPWriter().write(caption_set)

        self.assertEqual(result, SAMPLE_DFXP_FOR_LEGACY_WRITER_OUTPUT)
