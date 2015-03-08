# -*- coding: utf-8 -*-
import unittest

from pycaption import SCCReader, CaptionReadNoCaptions

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
                          # Notige the missing 'N' at the end. This is because
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
                          # u'ÁÉÓ¡',  # extended chars
                          # - this is how it actually looks like.
                          # Therefore we're freezing a bug
                          u'{break}<$¡',
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

