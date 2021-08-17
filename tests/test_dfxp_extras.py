from copy import deepcopy
from bs4 import BeautifulSoup

from pycaption.dfxp.base import _create_internal_alignment
from pycaption.dfxp import (
    SinglePositioningDFXPWriter, DFXPReader, DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID, LegacyDFXPWriter,
)
from pycaption.geometry import (
    HorizontalAlignmentEnum, VerticalAlignmentEnum, Layout, Alignment,
)


class TestSinglePositioningDFXPWRiter:
    def test_only_the_default_region_is_created(
            self, sample_dfxp_to_render_with_only_default_positioning_input):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

        dfxp = SinglePositioningDFXPWriter().write(caption_set)
        layout = BeautifulSoup(dfxp, features='html.parser').findChild('layout')

        assert len(layout.findChildren('region')) == 1

    def test_only_the_default_region_is_referenced(
            self, sample_dfxp_to_render_with_only_default_positioning_input):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

        dfxp = SinglePositioningDFXPWriter().write(caption_set)

        soup = BeautifulSoup(dfxp, features='html.parser')

        for elem in soup.findAll():
            if 'region' in elem.attrs:
                assert elem['region'] == DFXP_DEFAULT_REGION_ID

    def test_only_the_custom_region_is_created(
            self, sample_dfxp_to_render_with_only_default_positioning_input):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

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

        region = layout.findChild('region')
        text_align = region['tts:textAlign']
        display_align = region['tts:displayAlign']

        internal_alignment = _create_internal_alignment(
            text_align, display_align
        )

        assert len(layout.findChildren('region')) == 1
        assert internal_alignment.horizontal == HorizontalAlignmentEnum.LEFT
        assert internal_alignment.vertical == VerticalAlignmentEnum.TOP

    def test_only_the_specified_custom_attributes_are_created_for_the_region(
        self, sample_dfxp_to_render_with_only_default_positioning_input
    ):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

        new_region = Layout(
            alignment=Alignment(
                HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP
            )
        )

        dfxp = SinglePositioningDFXPWriter(new_region).write(caption_set)

        region = BeautifulSoup(dfxp).find('region')

        assert 'xml:id' in region.attrs
        assert region.attrs['xml:id'] != DFXP_DEFAULT_REGION_ID
        assert len(region.attrs) == 3

    def test_only_the_custom_region_is_referenced(
            self, sample_dfxp_to_render_with_only_default_positioning_input):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

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

        assert len(referenced_region_ids) == 1
        assert referenced_region_ids.pop() == created_region_id

    def test_styles_dont_contain_text_align_attribute(
            self, sample_dfxp_to_render_with_only_default_positioning_input):
        caption_set = DFXPReader().read(
            sample_dfxp_to_render_with_only_default_positioning_input
        )

        result = SinglePositioningDFXPWriter().write(caption_set)

        caption_set = DFXPReader().read(result)

        for _, style in caption_set.get_styles():
            assert 'text-align' not in style


class TestLegacyDFXPWriter:
    def test_default_style_is_written_to_output_file(
            self, sample_dfxp_with_templated_style):
        caption_set = DFXPReader(read_invalid_positioning=True).read(
            sample_dfxp_with_templated_style.format(
                style_name="foxy_the_squirrel"))

        result = LegacyDFXPWriter().write(caption_set)

        assert result.count('foxy_the_squirrel') == 2
