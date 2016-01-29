import unittest

from pycaption import DFXPReader, CaptionReadNoCaptions
from pycaption.exceptions import CaptionReadSyntaxError, InvalidInputError, \
    CaptionReadError
from pycaption.geometry import UnitEnum, HorizontalAlignmentEnum, \
    VerticalAlignmentEnum
from tests.samples.dfxp import (
    SAMPLE_DFXP, SAMPLE_DFXP_EMPTY, SAMPLE_DFXP_SYNTAX_ERROR,
    SAMPLE_DFXP_EMPTY_PARAGRAPH,
    SAMPLE_DFXP_INCORRECT_TIME_FORMAT,
    SAMPLE_DFXP_WITH_ALTERNATIVE_TIMING_FORMATS,
    SAMPLE_DFXP_EMPTY_CUE, SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING,
    SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE,
    SAMPLE_DFXP_WITH_FRAME_TIMING
)


class DFXPReaderTestCase(unittest.TestCase):
    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        self.assertEqual(7, len(captions.get_captions("en-US")))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions.get_captions("en-US")[2]

        self.assertEqual(17000000, paragraph.start)
        self.assertEqual(18752000, paragraph.end)

    def test_incorrect_time_format(self):
        self.assertRaises(CaptionReadSyntaxError,
                          DFXPReader().read,
                          SAMPLE_DFXP_INCORRECT_TIME_FORMAT)

    def test_offset_time(self):
        reader = DFXPReader()
        self.assertEqual(1, reader._translate_time("0.001ms"))
        self.assertEqual(2000, reader._translate_time("2ms"))
        self.assertEqual(1000000, reader._translate_time("1s"))
        self.assertEqual(1234567, reader._translate_time("1.234567s"))
        self.assertEqual(180000000, reader._translate_time("3m"))
        self.assertEqual(14400000000, reader._translate_time("4h"))
        # Tick values are not supported
        self.assertRaises(
            InvalidInputError, reader._translate_time, "2.3t")

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            DFXPReader().read, SAMPLE_DFXP_EMPTY)

    def test_invalid_markup_is_properly_handled(self):
        captions = DFXPReader().read(SAMPLE_DFXP_SYNTAX_ERROR)
        self.assertEquals(2, len(captions.get_captions("en")))

    def test_caption_error_for_invalid_positioning_values(self):
        invalid_value_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
                .format(origin="px 5px")
        )
        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_value_dfxp
        )

    def test_caption_error_for_invalid_or_unsupported_positioning_units(self):
        invalid_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
                .format(origin="6foo 7bar")
        )
        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_dfxp
        )

    def test_individual_timings_of_captions_with_matching_timespec_are_kept(
            self):  # noqa
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )
        expected_timings = [(9209000, 12312000)] * 3
        actual_timings = [(c_.start, c_.end) for c_ in
                          captionset.get_captions('en-US')]
        self.assertEqual(expected_timings, actual_timings)

    def test_individual_texts_of_captions_with_matching_timespec_are_kept(
            self):  # noqa
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )

        expected_texts = ['Some text here',
                          'Some text there',
                          'Caption texts are everywhere!']
        actual_texts = [c_.nodes[0].content for c_ in
                        captionset.get_captions("en-US")]

        self.assertEqual(expected_texts, actual_texts)

    def test_individual_layouts_of_captions_with_matching_timespec_are_kept(
            self):  # noqa
        captionset = DFXPReader().read(
            SAMPLE_DFXP_MULTIPLE_CAPTIONS_WITH_THE_SAME_TIMING
        )
        expected_layouts = [
            (((10, UnitEnum.PERCENT), (10, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM)),
            (((40, UnitEnum.PERCENT), (40, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM)),
            (((10, UnitEnum.PERCENT), (70, UnitEnum.PERCENT)), None, None,
             (HorizontalAlignmentEnum.CENTER, VerticalAlignmentEnum.BOTTOM))]
        actual_layouts = [c_.layout_info.serialized() for c_ in
                          captionset.get_captions('en-US')]

        self.assertEqual(expected_layouts, actual_layouts)

    def test_properly_converts_timing(self):
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_WITH_ALTERNATIVE_TIMING_FORMATS)
        caps = caption_set.get_captions('en-US')
        self.assertEqual(caps[0].start, 1900000)
        self.assertEqual(caps[0].end, 3050000)
        self.assertEqual(caps[1].start, 4000000)
        self.assertEqual(caps[1].end, 5200000)

    def test_empty_paragraph(self):
        try:
            DFXPReader().read(SAMPLE_DFXP_EMPTY_PARAGRAPH)
        except CaptionReadError:
            self.fail("Failing on empty paragraph")

    def test_properly_converts_frametiming(self):
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_WITH_FRAME_TIMING)
        caps = caption_set.get_captions('en-US')
        self.assertEquals(caps[0].end, 12233333)
        self.assertEquals(caps[0].start, 9666666)

    def test_empty_cue(self):
        caption_set = DFXPReader().read(
            SAMPLE_DFXP_EMPTY_CUE)
        caps = caption_set.get_captions('en-US')
        self.assertEquals(caps[1], [])
