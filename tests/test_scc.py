# -*- coding: utf-8 -*-
import unittest
from pycaption.scc.specialized_collections import (InstructionNodeCreator,
                                                   TimingCorrectingCaptionList)

from pycaption import SCCReader, CaptionReadNoCaptions
from pycaption.scc.state_machines import DefaultProvidingPositionTracker

TOLERANCE_MICROSECONDS = 500 * 1000


class SCCReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SCCReader().detect(SAMPLE_SCC_POP_ON.decode(u'utf-8')))

    def test_caption_length(self):
        captions = SCCReader().read(SAMPLE_SCC_POP_ON.decode(u'utf-8'))

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SCCReader().read(SAMPLE_SCC_POP_ON.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        self.assertTrue(delta_start < TOLERANCE_MICROSECONDS)
        self.assertTrue(delta_end < TOLERANCE_MICROSECONDS)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SCCReader().read, SAMPLE_SCC_EMPTY.decode(u'utf-8'))

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
             (u'left', u'top')),
            (((0.0, u'%'), (86.66666666666667, u'%')), None, None,
             (u'left', u'top'))]

        actual_node_layout_infos = [
            {idx: [node.layout_info.serialized() for node in caption.nodes]}
            for idx, caption in enumerate(caption_set.get_captions('en-US'))
        ]

        expected_node_layout_infos = [
            {0: [(((0.0, u'%'), (86.66666666666667, u'%')),
                  None,
                  None,
                  (u'left', u'top'))]},
            {1: [(((0.0, u'%'), (86.66666666666667, u'%')),
                  None,
                  None,
                  (u'left', u'top'))]}
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
        scc1 = SCCReader().read(unicode(SAMPLE_SCC_POP_ON))
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

        # positioning 1
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
        node_creator.interpret_command('91ae')  # italics ON
        node_creator.interpret_command('91ae')  # italics ON again
        node_creator.add_chars('b')
        node_creator.interpret_command('91ae')  # italics ON again
        node_creator.add_chars('b')
        node_creator.interpret_command('9120')  # italics OFF

        node_creator.interpret_command('1570')  # row 6 col 0
        node_creator.add_chars('c')
        node_creator.interpret_command('91ae')  # italics ON

        node_creator.interpret_command('9270')  # row 6 col 0
        node_creator.add_chars('d')

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
        self.assertTrue(result[12].is_italics_node())
        self.assertTrue(result[12].sets_italics_off())


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


SAMPLE_SCC_PRODUCES_CAPTIONS_WITH_START_AND_END_TIME_THE_SAME = u"""\
Scenarist_SCC V1.0

00:01:31;18 9420 9454 6162 9758 97a1 91ae 6261 9170 97a1 e362

00:01:35;18 9420 942f 94ae

00:01:40;25 942c
"""

SAMPLE_SCC_POP_ON = """Scenarist_SCC V1.0

00:00:09:05 94ae 94ae 9420 9420 9470 9470 a820 e3ec efe3 6b20 f4e9 e36b e96e 6720 2980 942c 942c 942f 942f

00:00:12:08 942c 942c

00:00:13:18 94ae 94ae 9420 9420 1370 1370 cdc1 ceba 94d0 94d0 5768 e56e 20f7 e520 f468 e96e 6b80 9470 9470 efe6 20a2 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 a22c 942c 942c 942f 942f

00:00:16:03 94ae 94ae 9420 9420 9470 9470 f7e5 2068 6176 e520 f468 e973 2076 e973 e9ef 6e20 efe6 2045 e96e 73f4 e5e9 6e80 942c 942c 942f 942f

00:00:17:20 94ae 94ae 9420 9420 94d0 94d0 6173 2061 6e20 efec 642c 20f7 f2e9 6e6b ec79 206d 616e 9470 9470 f7e9 f468 20f7 68e9 f4e5 2068 61e9 f2ae 942c 942c 942f 942f

00:00:19:13 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 4520 e5f1 7561 ec73 206d 20e3 ad73 f175 61f2 e564 20e9 7380 9470 9470 6eef f420 6162 ef75 f420 616e 20ef ec64 2045 e96e 73f4 e5e9 6eae 942c 942c 942f 942f

00:00:25:16 94ae 94ae 9420 9420 1370 1370 cdc1 ce20 32ba 94d0 94d0 49f4 a773 2061 ecec 2061 62ef 75f4 2061 6e20 e5f4 e5f2 6e61 ec80 9470 9470 45e9 6e73 f4e5 e96e ae80 942c 942c 942f 942f

00:00:31:15 94ae 94ae 9420 9420 9470 9470 bc4c c1d5 c7c8 49ce c720 2620 57c8 4f4f d0d3 a13e 942c 942c 942f 942f

00:00:36:04 942c 942c

"""

# 6 captions
#   2 Pop-On captions.
#       The first has 3 random positions, and thus 3 captions
#       The second should be interpreted as 1 caption with 2 line breaks
#   2 Roll-Up captions - same comment
#   2 Paint-on captions - same comment
#       - the TAB OVER commands are not interpreted (97A1, 97A2, 9723)
SAMPLE_SCC_MULTIPLE_POSITIONING = u"""Scenarist_SCC V1.0

00:00:00:16 94ae 94ae 9420 9420 1370 1370 6162 6162 91d6 91d6 e364 e364 927c 927c e5e6 e5e6 942c 942c 942f 942f

00:00:02:16 94ae 94ae 9420 9420 16f2 16f2 6768 6768 9752 9752 e9ea e9ea 97f2 97f2 6bec 6bec 942c 942c 942f 942f

00:00:09:21	9425 9425 94ad 94ad 94f2 94f2 6d6e 6d6e 97d6 97d6 ef70 ef70 92dc 92dc f1f2 f1f2

00:00:11:21 9425 9425 94ad 94ad 15f2 15f2 73f4 73f4 1652 1652 7576 7576 16f2 f7f8 f7f8

00:00:20;02	9429 9429 9452 9452 97A2 97A2 797A 797A 917c 917c B031 B031 16d6 16d6 32B3 32B3

00:00:22;02	9429 9429 1352 1352 97A2 97A2 34B5 34B5 13f2 13f2 B637 B637 9452 9452 38B9 38B9

00:00:36:04 942c 942c

"""

SAMPLE_SCC_WITH_ITALICS_BKUP = u"""\
Scenarist_SCC V1.0

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""

SAMPLE_SCC_WITH_ITALICS = u"""\

00:00:00:01 9420 10d0 97a2 91ae 6162 6162 6162 6162 942c 8080 8080 942f
"""


SAMPLE_SCC_EMPTY = """Scenarist_SCC V1.0
"""

SAMPLE_SCC_ROLL_UP_RU2 = u"""\
Scenarist_SCC V1.0
00:00:00;22	9425 9425 94ad 94ad 9470 9470 3e3e 3e20 c849 ae

00:00:02;23	9425 9425 94ad 94ad 9470 9470 49a7 cd20 cb45 d649 ce20 43d5 cece 49ce c720 c1ce c420 c154

00:00:04;17	9425 9425 94ad 94ad 9470 9470 49ce d645 d354 4f52 a7d3 20c2 c1ce cb20 5745 20c2 454c 4945 d645 2049 ce

00:00:06;04	9425 9425 94ad 94ad 9470 9470 c845 4cd0 49ce c720 54c8 4520 4c4f 43c1 4c20 ce45 49c7 c8c2 4f52 c84f 4fc4 d3

00:00:09;21	9425 9425 94ad 94ad 9470 9470 c1ce c420 49cd d052 4fd6 49ce c720 54c8 4520 4c49 d645 d320 4f46 20c1 4c4c

00:00:11;07	9425 9425 94ad 94ad 9470 9470 5745 20d3 4552 d645 ae

00:00:12;07	9425 9425 94ad 94ad 9470 9470 91b0 9131 9132 9132

00:00:13;07	9425 9425 94ad 94ad 9470 9470 c1c2 c3c4 c580 91bf

00:00:14;07	9425 9425 94ad 94ad 9470 9470 9220 9220 92a1 92a2 92a7

00:00:17;01	9426 9426 94ad 94ad 9470 9470 57c8 4552 4520 d94f d5a7 5245 20d3 54c1 cec4 49ce c720 ce4f 572c

00:00:18;19	9426 9426 94ad 94ad 9470 9470 4c4f 4fcb 49ce c720 4fd5 5420 54c8 4552 452c 2054 c8c1 54a7 d320 c14c 4c

00:00:20;06	9426 9426 94ad 94ad 9470 9470 54c8 4520 4352 4f57 c4ae

00:00:21;24	9426 9426 94ad 94ad 9470 9470 3e3e 2049 5420 57c1 d320 c74f 4fc4 2054 4f20 c245 2049 ce20 54c8 45

00:00:34;27	94a7 94ad 9470 c16e 6420 f2e5 73f4 eff2 e520 49ef f761 a773 20ec 616e 642c 20f7 61f4 e5f2

00:00:36;12	94a7 94ad 9470 c16e 6420 f7e9 ec64 ece9 e6e5 ae80

00:00:44;08	94a7 94ad 9470 3e3e 20c2 e96b e520 49ef f761 2c20 79ef 75f2 2073 ef75 f2e3 e520 e6ef f280
"""


SAMPLE_SCC_PRODUCES_BAD_LAST_END_TIME = u"""\
Scenarist_SCC V1.0

00:23:28;01	9420 94ae 9154 5245 91f4 c1c2 942c

00:24:29;21	942f

00:53:28;01	9420 94ae 9154 4552 91f4 aeae 942c

00:54:29;21	942f
"""

SAMPLE_NO_POSITIONING_AT_ALL_SCC = u"""\
Scenarist_SCC V1.0

00:23:28;01	9420 94ae 5245 c1c2 942c

00:24:29;21	942f

00:53:28;01	9420 94ae 4552 aeae 942c

00:54:29;21	942f
"""

SAMPLE_SCC_NOT_EXPLICITLY_SWITCHING_ITALICS_OFF = u"""\
Scenarist_SCC V1.0

00:01:28;09	9420 942f 94ae 9420 9452 97a2 b031 6161 9470 9723 b031 6262

00:01:31;10	9420 942f 94ae

00:01:31;18	9420 9454 b032 e3e3 9458 97a1 91ae b032 6464 9470 97a1 b032 e5e5

00:01:35;18	9420 942f 94ae

00:01:40;25	942c

00:01:51;18	9420 9452 97a1 b0b3 6161 94da 97a2 91ae b0b3 6262 9470 97a1 b0b3 e3e3

00:01:55;22	9420 942f b034 6161 94f4 9723 b034 6262

00:01:59;14	9420 942f 94ae 9420 94f4 b034 3180 e3e3

00:02:02;01	9420 942f 94ae 9420 94d0 b0b5 6161 94f2 97a2 b0b5 6262

00:02:04;05	9420 942f 94ae

00:09:53;06	942c 9420 13f4 9723 b0b6 e3e3 9454 97a2 b0b6 6464 9470 97a2 b0b6 e5e5

00:09:56;09	9420 942f 94ae 9420 94f2 b037 6161

00:09:58;18	9420 942f 94ae 9420 9454 b038 6262 9454 97a2 91ae b038 e3e3 94f2 97a1 94f2 97a1 91ae b038 6162 6464

00:09:59;28	9420 942f 94ae 9420 9452 97a2 e5e5 94f4 b0b9 6161

00:10:02;22	9420 942f 94ae 9420 9452 97a1 31b0 e5e5 9470 97a2 31b0 6262

00:10:04;10	9420 942f 94ae

00:52:03;02	9420 9470 97a2 3131 e3e3

00:52:18;20	9420 91d0 9723 3132 6464 9158 97a1 91ae 3132 e5e5 91da 97a2 9120 3132 6161 91f2 9723 3132 6262

00:52:22;22	9420 942c 942f 9420 9152 97a2 31b3 e3e3

00:52:25;04	9420 942c 942f 9420 91d0 97a2 3134 6464 91f2 e5e5

00:52:26;28	9420 942c 942f

00:52:27;18	9420 9152 9152 9152 91ae 31b5 6161 9154 97a1 9120 31b5 6262 9170 9723 31b5 e3e3

00:52:31;22	9420 942c 942f

00:52:34;14	942c

00:53:03;15	9420 94f4 97a1 94f4 97a1 91ae 31b6 6464
"""