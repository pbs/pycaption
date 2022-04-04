import pytest

from pycaption import SCCReader, CaptionReadNoCaptions, CaptionNode
from pycaption.exceptions import CaptionReadTimingError
from pycaption.geometry import (
    UnitEnum, HorizontalAlignmentEnum, VerticalAlignmentEnum,
)
from pycaption.scc.constants import MICROSECONDS_PER_CODEWORD
from pycaption.scc.specialized_collections import (
    InstructionNodeCreator, TimingCorrectingCaptionList,
)
from pycaption.scc.state_machines import DefaultProvidingPositionTracker
from tests.mixins import ReaderTestingMixIn

TOLERANCE_MICROSECONDS = 500 * 1000


class TestSCCReader(ReaderTestingMixIn):
    def setup_method(self):
        self.reader = SCCReader()

    def test_positive_answer_for_detection(self, sample_scc_pop_on):
        super().assert_positive_answer_for_detection(sample_scc_pop_on)

    @pytest.mark.parametrize('different_sample', [
        pytest.lazy_fixture('sample_dfxp'),
        pytest.lazy_fixture('sample_microdvd'),
        pytest.lazy_fixture('sample_sami'),
        pytest.lazy_fixture('sample_srt'),
        pytest.lazy_fixture('sample_webvtt')
    ])
    def test_negative_answer_for_detection(self, different_sample):
        super().assert_negative_answer_for_detection(different_sample)

    def test_caption_length(self, sample_scc_pop_on):
        captions = SCCReader().read(sample_scc_pop_on)

        assert 7 == len(captions.get_captions("en-US"))

    def test_proper_timestamps(self, sample_scc_pop_on):
        captions = SCCReader().read(sample_scc_pop_on)
        paragraph = captions.get_captions("en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        assert delta_start < TOLERANCE_MICROSECONDS
        assert delta_end < TOLERANCE_MICROSECONDS

    def test_invalid_timestamps(self, sample_scc_pop_on):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            SCCReader().read(sample_scc_pop_on.replace(':', '.'))
        assert exc_info.value.args[0].startswith(
            "Timestamps should follow the hour:minute:seconds;frames or "
            "hour:minute:seconds:frames format. Please correct the following "
            "time:")

    def test_empty_file(self, sample_scc_empty):
        with pytest.raises(CaptionReadNoCaptions):
            SCCReader().read(sample_scc_empty)

    def test_positioning(self, sample_scc_multiple_positioning):
        captions = SCCReader().read(sample_scc_multiple_positioning)

        # SCC generates only origin, and we always expect it.
        expected_positioning = [
            ((10.0, UnitEnum.PERCENT), (77.0, UnitEnum.PERCENT)),
            ((40.0, UnitEnum.PERCENT), (5.0, UnitEnum.PERCENT)),
            ((70.0, UnitEnum.PERCENT), (23.0, UnitEnum.PERCENT)),
            ((20.0, UnitEnum.PERCENT), (47.0, UnitEnum.PERCENT)),
            ((20.0, UnitEnum.PERCENT), (89.0, UnitEnum.PERCENT)),
            ((40.0, UnitEnum.PERCENT), (53.0, UnitEnum.PERCENT)),
            ((70.0, UnitEnum.PERCENT), (17.0, UnitEnum.PERCENT)),
            ((20.0, UnitEnum.PERCENT), (35.0, UnitEnum.PERCENT)),
            ((20.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
            ((70.0, UnitEnum.PERCENT), (11.0, UnitEnum.PERCENT)),
            ((40.0, UnitEnum.PERCENT), (41.0, UnitEnum.PERCENT)),
            ((20.0, UnitEnum.PERCENT), (71.0, UnitEnum.PERCENT))
        ]

        actual_positioning = [
            caption_.layout_info.origin.serialized()
            for caption_ in captions.get_captions('en-US')
        ]

        assert expected_positioning == actual_positioning

    def test_tab_offset(self, sample_scc_tab_offset):
        captions = SCCReader().read(sample_scc_tab_offset)

        # SCC generates only origin, and we always expect it.
        expected_positioning = [
            ((37.5, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
            ((17.5, UnitEnum.PERCENT), (89.0, UnitEnum.PERCENT)),
            ((12.5, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
            ((27.5, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
            ((30.0, UnitEnum.PERCENT), (89.0, UnitEnum.PERCENT)),
            ((35.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
            ((17.5, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT))
        ]

        actual_positioning = [
            caption_.layout_info.origin.serialized()
            for caption_ in captions.get_captions('en-US')
        ]

        assert expected_positioning == actual_positioning

    def test_italics_are_properly_read(self, sample_scc_with_italics):
        def switches_italics(node):
            """Determine if the current node switches italics on or off, or
            raise ValueError is it's not a style node

            Style nodes should be deprecated in favor of another model, so this
            function is expected to go away.

            :type node: pycaption.CaptionNode
            :rtype: bool
            """
            if not node.type_ == node.STYLE:
                raise ValueError("This should be a style node.")

            return node.start

        caption_set = SCCReader().read(sample_scc_with_italics)
        nodes = caption_set.get_captions('en-US')[0].nodes

        # We assert that the text is specified in italics.
        # If Style nodes are replaced, the way these 3 assertions are made
        # will most likely change
        assert switches_italics(nodes[0]) is True
        assert switches_italics(nodes[2]) is False
        assert nodes[1].content == 'abababab'

    def test_default_positioning_when_no_positioning_is_specified(
            self, sample_no_positioning_at_all_scc):
        caption_set = SCCReader().read(sample_no_positioning_at_all_scc)

        actual_caption_layouts = [
            caption.layout_info.serialized()
            for caption in caption_set.get_captions('en-US')
        ]

        expected_caption_layouts = [
            (((10.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
             None, None,
             (HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP)),
            (((10.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
             None, None,
             (HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP))
        ]

        actual_node_layout_infos = [
            {idx: [node.layout_info.serialized() for node in caption.nodes]}
            for idx, caption in enumerate(caption_set.get_captions('en-US'))
        ]

        expected_node_layout_infos = [
            {0: [(
                ((10.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
                None, None,
                (HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP)
            )]},
            {1: [(
                ((10.0, UnitEnum.PERCENT), (83.0, UnitEnum.PERCENT)),
                None, None,
                (HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP)
            )]}
        ]

        assert expected_node_layout_infos == actual_node_layout_infos
        assert expected_caption_layouts == actual_caption_layouts

    def test_timing_is_properly_set_on_split_captions(
            self, sample_scc_produces_captions_with_start_and_end_time_the_same
    ):
        caption_set = SCCReader().read(
            sample_scc_produces_captions_with_start_and_end_time_the_same
        )
        expected_timings = [
            ('00:01:35.633', '00:01:40.833'),
            ('00:01:35.633', '00:01:40.833'),
            ('00:01:35.633', '00:01:40.833'),
        ]

        actual_timings = [
            (c_.format_start(), c_.format_end())
            for c_ in caption_set.get_captions('en-US')
        ]

        assert expected_timings == actual_timings

    def test_skip_extended_characters_ascii_duplicate(
            self, sample_scc_with_extended_characters):
        caption_set = SCCReader().read(sample_scc_with_extended_characters)
        nodes = caption_set.get_captions('en-US')[0].nodes

        assert nodes[0].content == 'MÄRTHA:'

    def test_skip_duplicate_tab_offset(self, sample_scc_duplicate_tab_offset):
        expected_lines = [
            '[Radio reporter]',
            'The I-10 Santa Monica Freeway',
            'westbound is jammed,',
            'due to a three-car accident',
            'blocking lanes 1 and 2',
        ]

        caption_set = SCCReader().read(sample_scc_duplicate_tab_offset)
        actual_lines = [
            node.content
            for cap_ in caption_set.get_captions('en-US')
            for node in cap_.nodes
            if node.type_ == CaptionNode.TEXT
        ]

        assert expected_lines == actual_lines

    def test_skip_duplicate_special_characters(
            self, sample_scc_duplicate_special_characters):
        expected_lines = ['®°½¿™¢£♪à èâêîôû', '®°½¿™¢£♪à èâêîôû']

        caption_set = SCCReader().read(sample_scc_duplicate_special_characters)
        actual_lines = [
            node.content
            for cap_ in caption_set.get_captions('en-US')
            for node in cap_.nodes
            if node.type_ == CaptionNode.TEXT
        ]

        assert expected_lines == actual_lines

    def test_flashing_cue(self, sample_scc_flashing_cue):
        with pytest.raises(CaptionReadTimingError) as exc_info:
            SCCReader().read(sample_scc_flashing_cue)

        assert exc_info.value.args[0].startswith(
            "Unsupported cue duration around 00:00:20.433")


class TestCoverageOnly:
    """In order to refactor safely, we need coverage of 95% or more.
     This class includes tests that ensure that at the very least, we don't
     break anything that was working, OR fix anything whose faulty behavior
      was accepted.

      All the tests in this suite should only be useful for refactoring. They
      DO NOT ensure functionality. They only ensure nothing changes.
    """

    def test_freeze_rollup_captions_contents(self, sample_scc_roll_up_ru2):
        # There were no tests for ROLL-UP captions, but the library processed
        # Roll-Up captions. Make sure nothing changes during the refactoring
        scc1 = SCCReader().read(sample_scc_roll_up_ru2)
        captions = scc1.get_captions('en-US')
        actual_texts = [cap_.nodes[0].content for cap_ in captions]
        expected_texts = [
            '>>> HI.',
            "I'M KEVIN CUNNING AND AT",
            "INVESTOR'S BANK WE BELIEVE IN",
            'HELPING THE LOCAL NEIGHBORHOODS',
            'AND IMPROVING THE LIVES OF ALL',
            'WE SERVE.',
            '®°½',
            'ABû',
            'ÁÁÉÓ¡',
            "WHERE YOU'RE STANDING NOW,",
            "LOOKING OUT THERE, THAT'S AL",
            'THE CROWD.',
            '>> IT WAS GOOD TO BE IN TH',
            "And restore Iowa's land, water",
            'And wildlife.',
            '>> Bike Iowa, your source for',
        ]

        assert expected_texts == actual_texts

    def test_multiple_formats(self, sample_scc_multiple_formats):
        # Test for captions that contain both pop on and paint on formats to
        # ensure the paint on lines are not repeated
        expected_text_lines = [
            "(Client's Voice)",
            'Remember that degree',
            'you got in taxation?',
            '(Danny)',
            "Of course you don't",
            "because you didn't!",
            "Your job isn't doing hard",
            'work...',
            "...it's making them do hard",
            'work...',
            '...and getting paid for it.',
            '(VO)',
            'Snap and sort your expenses to',
            'save over $4,600 at tax time.',
            'QUICKBOOKS. BACKING YOU.',
        ]

        captions = SCCReader().read(sample_scc_multiple_formats) \
            .get_captions('en-US')
        text_lines = [
            node.content
            for caption in captions
            for node in caption.nodes
            if node.type_ == CaptionNode.TEXT
        ]

        assert expected_text_lines == text_lines

    def test_freeze_semicolon_spec_time(self, sample_scc_roll_up_ru2):
        scc1 = SCCReader().read(sample_scc_roll_up_ru2)
        captions = scc1.get_captions('en-US')
        expected_timings = [
            (733333.3333333333, 2766666.6666666665),
            (2766666.6666666665, 4566666.666666666),
            (4566666.666666666, 6133333.333333334),
            (6133333.333333334, 9700000.0),
            (9700000.0, 11233333.333333332),
            (11233333.333333332, 12233333.333333332),
            (12233333.333333332, 13233333.333333332),
            (13233333.333333332, 14233333.333333332),
            (14233333.333333332, 17033333.333333336),
            (17033333.333333336, 18633333.333333332),
            (18633333.333333332, 20200000.0),
            (20200000.0, 21800000.0),
            (21800000.0, 34900000.0),
            (34900000.0, 36400000.0),
            (36400000.0, 44266666.666666664),
            (44266666.666666664, 44866666.666666664),
        ]

        actual_timings = [(c_.start, c_.end) for c_ in captions]

        assert expected_timings == actual_timings

    def test_freeze_colon_spec_time(self, sample_scc_pop_on):
        # Coverage doesn't mean we test that functionality, so assert that
        # all the timing specs that previously had coverage, will actually
        # remain unchanged.
        scc1 = SCCReader().read(sample_scc_pop_on)
        expected_timings = [
            (9743066.666666664, 12278933.333333332),
            (14748066.666666666, 16916899.999999996),
            (16916899.999999996, 18651966.666666664),
            (18651966.666666664, 20787433.333333332),
            (20787433.333333332, 26659966.666666664),
            (26659966.666666664, 32132100.000000004),
            (32132100.000000004, 36169466.666666664),
        ]

        actual_timings = [
            (c_.start, c_.end) for c_ in scc1.get_captions('en-US')]

        assert expected_timings == actual_timings


class TestInterpretableNodeCreator:
    def test_italics_commands_are_formatted_properly(self):
        node_creator = InstructionNodeCreator(
            position_tracker=(DefaultProvidingPositionTracker())
        )

        # We expect
        # 1. all the initial italics closing nodes to be removed
        # 2. all the redundant italic nodes to be trimmed
        # 3. to get new closing italic nodes before changing position,
        # 4. to get new opening italic nodes after changing position, if 3
        # happened
        # 5. to get a final italic closing node, if one is needed
        node_creator.interpret_command('9470')  # row 15, col 0
        node_creator.interpret_command('9120')  # italics off
        node_creator.interpret_command('9120')  # italics off
        node_creator.add_chars('a')

        node_creator.interpret_command('9770')  # row 10 col 0
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.add_chars('b')
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.interpret_command('9120')  # italics OFF
        node_creator.interpret_command('9120')  # italics OFF
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.add_chars('b')
        node_creator.interpret_command('91ae')  # italics ON again
        node_creator.add_chars('b')
        node_creator.interpret_command('9120')  # italics OFF
        node_creator.interpret_command('9120')  # italics OFF

        node_creator.interpret_command('1570')  # row 6 col 0
        node_creator.add_chars('c')
        node_creator.interpret_command('91ae')  # italics ON

        node_creator.interpret_command('9270')  # row 4 col 0
        node_creator.add_chars('d')

        node_creator.interpret_command('15d0')  # row 5 col 0 - creates BR
        node_creator.add_chars('e')

        node_creator.interpret_command('1570')  # row 6 col 0 - creates BR
        node_creator.add_chars('f')

        result = list(node_creator)

        assert result[0].is_text_node()
        assert result[1].requires_repositioning()
        assert result[2].is_italics_node()
        assert result[2].sets_italics_on()

        assert result[3].is_text_node()
        assert result[4].is_text_node()
        assert result[5].is_text_node()

        assert result[6].is_italics_node()
        assert result[6].sets_italics_off()

        assert result[7].requires_repositioning()
        assert result[8].is_text_node()

        assert result[9].requires_repositioning()
        assert result[10].is_italics_node()
        assert result[10].sets_italics_on()

        assert result[11].is_text_node()
        assert result[12].is_explicit_break()
        assert result[13].is_text_node()
        assert result[14].is_explicit_break()
        assert result[15].is_text_node()

        assert result[16].is_italics_node()
        assert result[16].sets_italics_off()


class CaptionDummy:
    """Mock for pycaption.base.Caption"""

    def __init__(self, start=0, end=0, nodes=(1, 2)):
        self.nodes = nodes
        self.start = start
        self.end = end

    def __repr__(self):
        return f'{self.start}-->{self.end}'


class TestTimingCorrectingCaptionList:
    def test_appending_then_appending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=3))
        caption_list.append(CaptionDummy(start=6))

        assert caption_list[0].end == 6

    def test_appending_then_extending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=3))
        caption_list.extend([CaptionDummy(start=7), CaptionDummy(start=7)])

        assert caption_list[0].end == 7

    def test_extending_then_appending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([CaptionDummy(start=4), CaptionDummy(start=4)])
        caption_list.append(CaptionDummy(start=9))

        assert caption_list[0].end == 9
        assert caption_list[1].end == 9

    def test_extending_then_extending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([CaptionDummy(start=4), CaptionDummy(start=4)])
        caption_list.extend([CaptionDummy(start=7), CaptionDummy(start=7)])

        assert caption_list[0].end == 7
        assert caption_list[1].end == 7

    def test_not_appending_none_or_empty_captions(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(None)
        caption_list.extend([CaptionDummy(nodes=[])])

        assert len(caption_list) == 0

    def test_not_extending_list_with_nones_or_empty_captions(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([None, CaptionDummy(nodes=[])])

        assert len(caption_list) == 0

    def test_not_overwriting_end_time(self):
        second = 1000 * 1000  # in microseconds
        # Test here all the 4 cases:
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=1 * second, end=3 * second))
        caption_list.append(CaptionDummy(start=3.167 * second, end=6 * second))

        # Append then append
        assert caption_list[-2].end == 3 * second

        caption_list.extend([CaptionDummy(start=7 * second, end=8 * second)])

        # Append then extend
        assert caption_list[-2].end == 6 * second

        caption_list.extend([CaptionDummy(start=9 * second, end=10 * second)])

        # extend then extend
        assert caption_list[-2].end == 8 * second

        caption_list.append(CaptionDummy(start=11 * second, end=12 * second))

        # extend then append
        assert caption_list[-2].end == 10 * second

    def test_overwriting_end_time_difference_under_5_frames(self):
        second = 1000 * 1000  # in microseconds
        # Test here all the 4 cases:
        caption_list = TimingCorrectingCaptionList()
        expected_end_1 = 3 * second + 5 * MICROSECONDS_PER_CODEWORD

        caption_list.append(CaptionDummy(start=1 * second, end=3 * second))
        caption_list.append(CaptionDummy(start=expected_end_1, end=6 * second))
        # Append then append
        assert caption_list[-2].end == expected_end_1

        expected_end_2 = 6 * second + 4 * MICROSECONDS_PER_CODEWORD

        caption_list.extend([CaptionDummy(start=expected_end_2,
                                          end=8 * second)])
        # Append then extend
        assert caption_list[-2].end == expected_end_2

        expected_end_3 = 8 * second + 3 * MICROSECONDS_PER_CODEWORD

        caption_list.extend([CaptionDummy(start=expected_end_3,
                                          end=10 * second)])
        # Extend then extend
        assert caption_list[-2].end == expected_end_3

        expected_end_4 = 10 * second + 1 * MICROSECONDS_PER_CODEWORD

        caption_list.append(CaptionDummy(start=expected_end_4, end=12 * second))
        # Extend then append
        assert caption_list[-2].end == expected_end_4

    def test_last_caption_zero_end_time_is_corrected(
            self, sample_scc_no_explicit_end_to_last_caption):
        caption_set = SCCReader().read(
            sample_scc_no_explicit_end_to_last_caption
        )

        last_caption = caption_set.get_captions('en-US')[-1]

        assert last_caption.end == last_caption.start + 4 * 1000 * 1000

    def test_eoc_first_command(self, sample_scc_eoc_first_command):
        # TODO First caption should be ignored because it doesn't start with
        #  a pop/roll/paint on command
        caption_set = SCCReader().read(sample_scc_eoc_first_command)

        # just one caption, first EOC disappears
        num_captions = len(caption_set.get_captions('en-US'))

        assert num_captions == 2
