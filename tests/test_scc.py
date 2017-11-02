# -*- coding: utf-8 -*-
import unittest
from pycaption.scc.specialized_collections import (InstructionNodeCreator,
                                                   TimingCorrectingCaptionList)

from pycaption import SCCReader, CaptionReadNoCaptions
from pycaption.scc.state_machines import DefaultProvidingPositionTracker

from .samples.scc import (
    SAMPLE_SCC_PRODUCES_CAPTIONS_WITH_START_AND_END_TIME_THE_SAME,
    SAMPLE_SCC_POP_ON, SAMPLE_SCC_MULTIPLE_POSITIONING,
    SAMPLE_SCC_WITH_ITALICS, SAMPLE_SCC_EMPTY, SAMPLE_SCC_ROLL_UP_RU2,
    SAMPLE_SCC_PRODUCES_BAD_LAST_END_TIME, SAMPLE_NO_POSITIONING_AT_ALL_SCC,
    SAMPLE_SCC_NO_EXPLICIT_END_TO_LAST_CAPTION, SAMPLE_SCC_EOC_FIRST_COMMAND
)

TOLERANCE_MICROSECONDS = 500 * 1000


class SCCReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SCCReader().detect(SAMPLE_SCC_POP_ON))

    def test_caption_length(self):
        captions = SCCReader().read(SAMPLE_SCC_POP_ON)

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SCCReader().read(SAMPLE_SCC_POP_ON)
        paragraph = captions.get_captions(u"en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        self.assertTrue(delta_start < TOLERANCE_MICROSECONDS)
        self.assertTrue(delta_end < TOLERANCE_MICROSECONDS)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SCCReader().read, SAMPLE_SCC_EMPTY)

    def test_scc_positioning_is_read(self):
        captions = SCCReader().read(unicode(SAMPLE_SCC_MULTIPLE_POSITIONING))

        # SCC generates only origin, and we always expect it.
        expected_positioning = [
            ((0.0, u'%'), (80.0, u'%')),
            ((37.5, u'%'), (0.0, u'%')),
            ((75.0, u'%'), (20.0, u'%')),
            ((12.5, u'%'), (46.666666666666664, u'%')),
            ((12.5, u'%'), (93.33333333333333, u'%')),
            ((37.5, u'%'), (53.333333333333336, u'%')),
            ((75.0, u'%'), (13.333333333333334, u'%')),
            ((12.5, u'%'), (33.333333333333336, u'%')),
            ((12.5, u'%'), (86.66666666666667, u'%')),
            ((75.0, u'%'), (6.666666666666667, u'%')),
            ((37.5, u'%'), (40.0, u'%')),
            ((12.5, u'%'), (73.33333333333333, u'%'))
        ]
        actual_positioning = [
            caption_.layout_info.origin.serialized() for caption_ in
            captions.get_captions(u'en-US')
        ]

        self.assertEqual(expected_positioning, actual_positioning)

    def test_correct_last_bad_timing(self):
        # This fix was implemented with a hack. The commands for the Pop-on
        # captions will have to be reviewed, but until then this is good enough
        caption_set = SCCReader().read(SAMPLE_SCC_PRODUCES_BAD_LAST_END_TIME)

        expected_timings = [(1408266666.6666667, 1469700000.0),
                            (3208266666.666667, 3269700000.0)]

        actual_timings = [
            (c_.start, c_.end) for c_ in caption_set.get_captions(u'en-US')
        ]
        self.assertEqual(expected_timings, actual_timings)

    def test_italics_are_properly_read(self):
        def switches_italics(node):
            """Determine if the current node switches italics on or off, or
            raise ValueError is it's not a style node

            Style nodes should be deprecated in favor of another model, so this
            function is expected to go away.

            :type node: pycaption.CaptionNode
            :rtype: bool
            """
            if not node.type_ == node.STYLE:
                raise ValueError(u"This should be a style node.")

            return node.start

        caption_set = SCCReader().read(SAMPLE_SCC_WITH_ITALICS)
        nodes = caption_set.get_captions(u'en-US')[0].nodes

        # We assert that the text is specified in italics.
        # If Style nodes are replaced, the way these 3 assertions are made
        # will most likely change
        self.assertEqual(switches_italics(nodes[0]), True)
        self.assertEqual(switches_italics(nodes[2]), False)
        self.assertEqual(nodes[1].content, u'abababab')

    def test_default_positioning_when_no_positioning_is_specified(self):
        caption_set = SCCReader().read(SAMPLE_NO_POSITIONING_AT_ALL_SCC)

        actual_caption_layouts = [
            caption.layout_info.serialized()
            for caption in caption_set.get_captions(u'en-US')
        ]

        expected_caption_layouts = [
            (((0.0, u'%'), (86.66666666666667, u'%')), None, None,
             (u'center', u'top')),
            (((0.0, u'%'), (86.66666666666667, u'%')), None, None,
             (u'center', u'top'))]

        actual_node_layout_infos = [
            {idx: [node.layout_info.serialized() for node in caption.nodes]}
            for idx, caption in enumerate(caption_set.get_captions('en-US'))
        ]

        expected_node_layout_infos = [
            {0: [(((0.0, u'%'), (86.66666666666667, u'%')),
                  None,
                  None,
                  (u'center', u'top'))]},
            {1: [(((0.0, u'%'), (86.66666666666667, u'%')),
                  None,
                  None,
                  (u'center', u'top'))]}
        ]

        self.assertEqual(expected_node_layout_infos, actual_node_layout_infos)
        self.assertEqual(expected_caption_layouts, actual_caption_layouts)

    def test_timing_is_properly_set_on_split_captions(self):
        caption_set = SCCReader().read(
            SAMPLE_SCC_PRODUCES_CAPTIONS_WITH_START_AND_END_TIME_THE_SAME
        )
        expected_timings = [(u'00:01:35.666', u'00:01:40.866'),
                            (u'00:01:35.666', u'00:01:40.866'),
                            (u'00:01:35.666', u'00:01:40.866')]

        actual_timings = [(c_.format_start(), c_.format_end()) for c_ in
                          caption_set.get_captions('en-US')]

        self.assertEqual(expected_timings, actual_timings)


class CoverageOnlyTestCase(unittest.TestCase):
    """In order to refactor safely, we need coverage of 95% or more.
     This class includes tests that ensure that at the very least, we don't
     break anything that was working, OR fix anything whose faulty behavior
      was accepted.

      All the tests in this suite should only be useful for refactoring. They
      DO NOT ensure functionality. They only ensure nothing changes.
    """
    def test_freeze_rollup_captions_contents(self):
        # There were no tests for ROLL-UP captions, but the library processed
        # Roll-Up captions. Make sure nothing changes during the refactoring
        scc1 = SCCReader().read(SAMPLE_SCC_ROLL_UP_RU2)
        captions = scc1.get_captions(u'en-US')
        actual_texts = [cap_.nodes[0].content for cap_ in captions]
        expected_texts = [u'>>> HI',
                          u"I'M KEVIN CUNNING AND AT",
                          # Notice the missing 'N' at the end. This is because
                          # the input is not OK (should only use 4 byte "words"
                          # (filling in with '80' where only 2 bytes are
                          # meaningful)
                          u"INVESTOR'S BANK WE BELIEVE I",
                          u'HELPING THE LOCAL NEIGHBORHOOD',
                          u'AND IMPROVING THE LIVES OF ALL',
                          u'WE SERVE',
                          # special chars. Last one should be printer 2 times
                          # XXX this is a bug.
                          u'®°½',
                          # special/ extended chars delete last 0-4 chars.
                          # XXX - this is a bug.
                          u'ABû',
                          u'ÁÉÓ¡',
                          u"WHERE YOU'RE STANDING NOW,",
                          u"LOOKING OUT THERE, THAT'S AL",
                          u'THE CROWD.',
                          u'>> IT WAS GOOD TO BE IN TH',
                          u"And restore Iowa's land, water",
                          u'And wildlife.',
                          u'>> Bike Iowa, your source for']
        self.assertEqual(expected_texts, actual_texts)

    def test_freeze_semicolon_spec_time(self):
        scc1 = SCCReader().read(SAMPLE_SCC_ROLL_UP_RU2)
        captions = scc1.get_captions(u'en-US')
        expected_timings = [(766666.6666666667, 2800000.0),
                            (2800000.0, 4600000.0),
                            (4600000.0, 6166666.666666667),
                            (6166666.666666667, 9733333.333333332),
                            (9733333.333333332, 11266666.666666668),
                            (11266666.666666668, 12266666.666666668),
                            (12266666.666666668, 13266666.666666668),
                            (13266666.666666668, 14266666.666666668),
                            (14266666.666666668, 17066666.666666668),
                            (17066666.666666668, 18666666.666666668),
                            (18666666.666666668, 20233333.333333336),
                            (20233333.333333336, 21833333.333333332),
                            (21833333.333333332, 34933333.33333333),
                            (34933333.33333333, 36433333.33333333),
                            (36433333.33333333, 44300000.0),
                            (44300000.0, 44866666.666666664)]

        actual_timings = [(c_.start, c_.end) for c_ in captions]
        self.assertEqual(expected_timings, actual_timings)

    def test_freeze_colon_spec_time(self):
        # Coverage doesn't mean we test that functionality, so assert that
        # all the timing specs that previously had coverage, will actually
        # remain unchanged.
        scc1 = SCCReader().read(SAMPLE_SCC_POP_ON)
        expected_timings = [(9776433.333333332, 12312300.0),
                            (14781433.33333333, 16883533.333333332),
                            (16950266.666666664, 18618600.000000004),
                            (18685333.333333332, 20754066.666666664),
                            (20820800.0, 26626600.0),
                            (26693333.333333332, 32098733.333333332),
                            (32165466.66666666, 36202833.33333332)]

        actual_timings = [
            (c_.start, c_.end) for c_ in scc1.get_captions(u'en-US')]
        self.assertEqual(expected_timings, actual_timings)


class InterpretableNodeCreatorTestCase(unittest.TestCase):
    def test_italics_commands_are_formatted_properly(self):
        node_creator = InstructionNodeCreator(
            position_tracker=(DefaultProvidingPositionTracker()))

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

        self.assertTrue(result[0].is_text_node())
        self.assertTrue(result[1].requires_repositioning())
        self.assertTrue(result[2].is_italics_node())
        self.assertTrue(result[2].sets_italics_on())

        self.assertTrue(result[3].is_text_node())
        self.assertTrue(result[4].is_text_node())
        self.assertTrue(result[5].is_text_node())

        self.assertTrue(result[6].is_italics_node())
        self.assertTrue(result[6].sets_italics_off())

        self.assertTrue(result[7].requires_repositioning())
        self.assertTrue(result[8].is_text_node())

        self.assertTrue(result[9].requires_repositioning())
        self.assertTrue(result[10].is_italics_node())
        self.assertTrue(result[10].sets_italics_on())

        self.assertTrue(result[11].is_text_node())
        self.assertTrue(result[12].is_explicit_break())
        self.assertTrue(result[13].is_text_node())
        self.assertTrue(result[14].is_explicit_break())
        self.assertTrue(result[15].is_text_node())

        self.assertTrue(result[16].is_italics_node())
        self.assertTrue(result[16].sets_italics_off())


class CaptionDummy(object):
    """Mock for pycaption.base.Caption
    """
    def __init__(self, start=0, end=0, nodes=(1, 2)):
        self.nodes = nodes
        self.start = start
        self.end = end

    def __repr__(self):
        return u"{start}-->{end}".format(start=self.start, end=self.end)


class TimingCorrectingCaptionListTestCase(unittest.TestCase):
    def test_appending_then_appending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=3))
        caption_list.append(CaptionDummy(start=6))

        self.assertEqual(caption_list[0].end, 6)

    def test_appending_then_extending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=3))
        caption_list.extend([CaptionDummy(start=7), CaptionDummy(start=7)])

        self.assertEqual(caption_list[0].end, 7)

    def test_extending_then_appending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([CaptionDummy(start=4), CaptionDummy(start=4)])
        caption_list.append(CaptionDummy(start=9))

        self.assertEqual(caption_list[0].end, 9)
        self.assertEqual(caption_list[1].end, 9)

    def test_extending_then_extending(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([CaptionDummy(start=4), CaptionDummy(start=4)])
        caption_list.extend([CaptionDummy(start=7), CaptionDummy(start=7)])

        self.assertEqual(caption_list[0].end, 7)
        self.assertEqual(caption_list[1].end, 7)

    def test_not_appending_none_or_empty_captions(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(None)
        caption_list.extend([CaptionDummy(nodes=[])])

        self.assertEqual(len(caption_list), 0)

    def test_not_extending_list_with_nones_or_empty_captions(self):
        caption_list = TimingCorrectingCaptionList()

        caption_list.extend([None, CaptionDummy(nodes=[])])

        self.assertEqual(len(caption_list), 0)

    def test_not_overwriting_end_time(self):
        # Test here all the 4 cases:
        caption_list = TimingCorrectingCaptionList()

        caption_list.append(CaptionDummy(start=1, end=3))
        caption_list.append(CaptionDummy(start=5, end=6))

        # Append then append
        self.assertEqual(caption_list[-2].end, 3)

        caption_list.extend([CaptionDummy(start=7, end=8)])

        # Append then extend
        self.assertEqual(caption_list[-2].end, 6)

        caption_list.extend([CaptionDummy(start=9, end=10)])

        # extend then extend
        self.assertEqual(caption_list[-2].end, 8)

        caption_list.append(CaptionDummy(start=11, end=12))

        # extend then append
        self.assertEqual(caption_list[-2].end, 10)

    def test_last_caption_zero_end_time_is_corrected(self):
        caption_set = SCCReader().read(SAMPLE_SCC_NO_EXPLICIT_END_TO_LAST_CAPTION)  # noqa

        last_caption = caption_set.get_captions('en-US')[-1]
        self.assertEqual(
            last_caption.end, last_caption.start + 4 * 1000 * 1000
        )

    def test_eoc_first_command(self):
        caption_set = SCCReader().read(SAMPLE_SCC_EOC_FIRST_COMMAND)

        # just one caption, first EOC disappears
        num_captions = len(caption_set.get_captions('en-US'))
        self.assertEqual(num_captions, 1)
