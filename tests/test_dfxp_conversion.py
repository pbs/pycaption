from bs4 import BeautifulSoup

from pycaption import (
    DFXPReader, SAMIReader, SRTReader, DFXPWriter, WebVTTWriter, MicroDVDWriter,
)
from pycaption.dfxp.extras import LegacyDFXPWriter
from pycaption.dfxp.base import (
    DFXP_DEFAULT_STYLE, DFXP_DEFAULT_STYLE_ID, DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID, _recreate_style, _convert_layout_to_attributes
)

from .mixins import DFXPTestingMixIn, WebVTTTestingMixIn, MicroDVDTestingMixIn

# Arbitrary values used to test relativization
VIDEO_WIDTH = 640
VIDEO_HEIGHT = 360


class TestDFXPtoDFXP(DFXPTestingMixIn):
    def test_dfxp_to_dfxp_conversion(self, sample_dfxp_output, sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        results = DFXPWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(sample_dfxp_output, results)

    def test_empty_cue(self, sample_dfxp_empty_cue_output,
                       sample_dfxp_empty_cue):
        caption_set = DFXPReader().read(sample_dfxp_empty_cue)
        results = DFXPWriter().write(caption_set)

        self.assert_dfxp_equals(sample_dfxp_empty_cue_output, results)

    def test_default_styling_tag(self, sample_dfxp_without_region_and_style):
        caption_set = DFXPReader().read(sample_dfxp_without_region_and_style)
        result = DFXPWriter().write(caption_set)

        default_style = _recreate_style(DFXP_DEFAULT_STYLE, None)
        default_style['xml:id'] = DFXP_DEFAULT_STYLE_ID

        soup = BeautifulSoup(result, 'lxml-xml')
        style = soup.find('style', {'xml:id': DFXP_DEFAULT_STYLE_ID})

        assert style
        assert style.attrs == default_style

    def test_default_styling_p_tags(self, sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, 'lxml')

        for p in soup.find_all('p'):
            assert p.attrs.get('style') == 'p'

    def test_default_region_tag(self, sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, 'lxml-xml')
        region = soup.find('region', {'xml:id': DFXP_DEFAULT_REGION_ID})

        default_region = _convert_layout_to_attributes(DFXP_DEFAULT_REGION)
        default_region['xml:id'] = DFXP_DEFAULT_REGION_ID

        assert region
        assert region.attrs['xml:id'] == DFXP_DEFAULT_REGION_ID
        assert region.attrs == default_region

    def test_default_region_p_tags(self, sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        result = DFXPWriter().write(caption_set)

        soup = BeautifulSoup(result, 'lxml')

        for p in soup.find_all('p'):
            assert p.attrs.get('region') == DFXP_DEFAULT_REGION_ID

    def test_correct_region_attributes_are_recreated(
            self, sample_dfxp_multiple_regions_output,
            sample_dfxp_multiple_regions_input):
        caption_set = DFXPReader().read(sample_dfxp_multiple_regions_input)
        result = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(result, sample_dfxp_multiple_regions_output)

    def test_incorrectly_specified_positioning_is_explicitly_accepted(
            self, sample_dfxp_invalid_but_supported_positioning_output,
            sample_dfxp_invalid_but_supported_positioning_input):
        # The arguments used here illustrate how we will try to read
        # and write incorrectly specified positioning information.
        # By incorrect, I mean the specs say that those attributes should be
        # ignored, not that the attributes themselves are outside of the specs
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            sample_dfxp_invalid_but_supported_positioning_input
        )
        result = DFXPWriter(
            relativize=False,
            fit_to_screen=False,
            write_inline_positioning=True).write(caption_set)

        self.assert_dfxp_equals(
            result, sample_dfxp_invalid_but_supported_positioning_output
        )

    def test_dont_create_style_tags_with_no_id(
            self, sample_dfxp_style_tag_with_no_xml_id_output,
            sample_dfxp_style_tag_with_no_xml_id_input):
        # The <style> tags can have no 'xml:id' attribute. Previously, in this
        # case, the style was copied to the output file, with the 'xml:id'
        # property declared, but no value assigned to it. Since such a style
        # can not be referred anyway, and <style> elements, children of
        # <region> tags shouldn't be referred to anyway, we don't include
        # these styles in the output file
        caption_set = DFXPReader().read(
            sample_dfxp_style_tag_with_no_xml_id_input)
        result = DFXPWriter().write(caption_set)

        assert result == sample_dfxp_style_tag_with_no_xml_id_output

    def test_is_relativized(self, sample_dfxp_with_relativized_positioning,
                            sample_dfxp_with_positioning):
        # Absolute positioning settings (e.g. px) are converted to percentages
        caption_set = DFXPReader().read(sample_dfxp_with_positioning)
        result = DFXPWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)

        assert result == sample_dfxp_with_relativized_positioning

    def test_fit_to_screen(self, sample_dfxp_long_cue_fit_to_screen,
                           sample_dfxp_long_cue):
        # Check if caption width and height are is explicitly set and
        # recalculate it if necessary. This prevents long captions from being
        # cut out of the screen.
        caption_set = DFXPReader().read(sample_dfxp_long_cue)
        result = DFXPWriter().write(caption_set)

        assert result == sample_dfxp_long_cue_fit_to_screen

    def test_proper_xml_entity_escaping(
            self, sample_dfxp_with_escaped_apostrophe):
        caption_set = DFXPReader().read(sample_dfxp_with_escaped_apostrophe)
        cue_text = caption_set.get_captions('en-US')[0].nodes[0].content

        assert cue_text == "<< \"Andy's Caf\xe9 & Restaurant\" this way"
        result = DFXPWriter().write(caption_set)
        assert "&lt;&lt; \"Andy's Café &amp; Restaurant\" this way" in result


class TestDFXPtoWebVTT(WebVTTTestingMixIn):
    def test_dfxp_to_webvtt_conversion(self, sample_webvtt_from_dfxp,
                                       sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_dfxp, results)

    def test_dfxp_with_inline_style_to_webvtt_conversion(
            self, sample_webvtt_from_dfxp_with_style,
            sample_dfxp_with_inline_style):
        caption_set = DFXPReader().read(sample_dfxp_with_inline_style)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_dfxp_with_style, results)

    def test_dfxp_with_defined_style_to_webvtt_conversion(
            self, sample_webvtt_from_dfxp_with_style,
            sample_dfxp_with_defined_style):
        caption_set = DFXPReader().read(sample_dfxp_with_defined_style)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_dfxp_with_style, results)

    def test_dfxp_with_inherited_style_to_webvtt_conversion(
            self, sample_webvtt_from_dfxp_with_style,
            sample_dfxp_with_inherited_style):
        caption_set = DFXPReader().read(sample_dfxp_with_inherited_style)
        results = WebVTTWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(sample_webvtt_from_dfxp_with_style, results)

    def test_dfxp_with_positioning_to_webvtt_conversion(
            self, sample_webvtt_from_dfxp_with_positioning_and_style,
            sample_dfxp_with_positioning):
        caption_set = DFXPReader().read(sample_dfxp_with_positioning)
        results = WebVTTWriter(
            video_width=VIDEO_WIDTH, video_height=VIDEO_HEIGHT
        ).write(caption_set)

        assert isinstance(results, str)
        self.assert_webvtt_equals(
            sample_webvtt_from_dfxp_with_positioning_and_style, results
        )

    def test_dfxp_to_webvtt_adds_explicit_size(
            self, sample_webvtt_output_long_cue, sample_dfxp_long_cue):
        caption_set = DFXPReader().read(sample_dfxp_long_cue)
        results = WebVTTWriter().write(caption_set)

        assert sample_webvtt_output_long_cue == results

    def test_dfxp_to_webvtt_preserves_proper_alignment(
            self, webvtt_from_dfxp_with_conflicting_align,
            dfxp_style_region_align_conflict):
        # This failed at one point when the CaptionSet had node breaks with
        # different positioning. It was fixed both at the DFXPReader AND the
        # WebVTTWriter.
        caption_set = DFXPReader().read(dfxp_style_region_align_conflict)
        results = WebVTTWriter().write(caption_set)

        assert webvtt_from_dfxp_with_conflicting_align == results

    def test_dfxp_empty_cue_to_webvtt(self, sample_webvtt_empty_cue_output,
                                      sample_dfxp_empty_cue):
        caption_set = DFXPReader().read(sample_dfxp_empty_cue)
        results = WebVTTWriter().write(caption_set)

        self.assert_webvtt_equals(sample_webvtt_empty_cue_output, results)


class TestDFXPtoMicroDVD(MicroDVDTestingMixIn):
    def test_dfxp_to_microdvd_conversion(self, sample_microdvd_2, sample_dfxp):
        caption_set = DFXPReader().read(sample_dfxp)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd_2, results)

    def test_dfxp_empty_cue_to_microdvd(
            self, sample_microdvd_empty_cue_output, sample_dfxp_empty_cue):
        caption_set = DFXPReader().read(sample_dfxp_empty_cue)
        results = MicroDVDWriter().write(caption_set)

        self.assert_microdvd_equals(sample_microdvd_empty_cue_output, results)


class TestLegacyDFXP:
    def test_legacy_convert(self, sample_dfxp_for_legacy_writer_output,
                            sample_dfxp_for_legacy_writer_input):
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            sample_dfxp_for_legacy_writer_input
        )

        result = LegacyDFXPWriter().write(caption_set)

        assert result == sample_dfxp_for_legacy_writer_output


class TestSAMItoDFXP(DFXPTestingMixIn):
    def test_sami_to_dfxp_conversion(
            self, sample_dfxp_from_sami_with_positioning, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(sample_dfxp_from_sami_with_positioning, results)

    def test_sami_to_dfxp_with_margin(self, sample_dfxp_from_sami_with_margins,
                                      sample_sami_partial_margins):
        caption_set = SAMIReader().read(sample_sami_partial_margins)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(sample_dfxp_from_sami_with_margins, results)

    def test_sami_to_dfxp_with_margin_for_language(
            self, sample_dfxp_from_sami_with_lang_margins,
            sample_sami_lang_margin):
        caption_set = SAMIReader().read(sample_sami_lang_margin)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_lang_margins,
            results
        )

    def test_sami_to_dfxp_with_span(self, sample_dfxp_from_sami_with_span,
                                    sample_sami_with_span):
        caption_set = SAMIReader().read(sample_sami_with_span)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(sample_dfxp_from_sami_with_span, results)

    def test_sami_to_dfxp_with_bad_span_align(
            self, sample_dfxp_from_sami_with_bad_span_align,
            sample_sami_with_bad_span_align):
        caption_set = SAMIReader().read(sample_sami_with_bad_span_align)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_bad_span_align,
            results
        )

    def test_sami_to_dfxp_ignores_multiple_span_aligns(
            self, sample_dfxp_from_sami_with_bad_span_align,
            sample_sami_with_multiple_span_aligns):
        caption_set = SAMIReader().read(sample_sami_with_multiple_span_aligns)
        results = DFXPWriter(
            relativize=False, fit_to_screen=False).write(caption_set)

        self.assert_dfxp_equals(
            sample_dfxp_from_sami_with_bad_span_align,
            results
        )

    def test_sami_to_dfxp_xml_output(self, sample_sami_syntax_error):
        captions = SAMIReader().read(sample_sami_syntax_error)
        results = DFXPWriter(relativize=False,
                             fit_to_screen=False).write(captions)

        assert isinstance(results, str)
        assert 'xmlns="http://www.w3.org/ns/ttml"' in results
        assert 'xmlns:tts="http://www.w3.org/ns/ttml#styling"' in results


class TestSRTtoDFXP(DFXPTestingMixIn):
    def test_srt_to_dfxp_conversion(self, sample_dfxp, sample_srt):
        caption_set = SRTReader().read(sample_srt)
        results = DFXPWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_dfxp_equals(
            sample_dfxp, results,
            ignore_styling=True, ignore_spans=True
        )
