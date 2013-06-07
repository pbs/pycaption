
import unittest

from pycaption import SRTReader, SRTWriter


SAMPLE_SRT = """1
00:00:09,209 --> 00:00:12,312
( clock ticking )

2
00:00:14,848 --> 00:00:17,000
MAN:
When we think
of E equals m c-squared,

3
00:00:17,000 --> 00:00:18,752
we have this vision of Einstein

4
00:00:18,752 --> 00:00:20,887
as an old, wrinkly man
with white hair.

5
00:00:20,887 --> 00:00:26,760
MAN 2:
E equals m c-squared is
not about an old Einstein.
"""


class SRTReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SRTReader().detect(SAMPLE_SRT))

    def test_proper_pcc_format(self):
        captions = SRTReader().read(SAMPLE_SRT)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(5, len(captions["captions"]["en"]))

    def test_proper_timestamps(self):
        captions = SRTReader().read(SAMPLE_SRT)
        paragraph = captions["captions"]["en"][0]

        self.assertEquals(9209000, paragraph[0])
        self.assertEquals(12312000, paragraph[1])


class SRTWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SRTReader().read(SAMPLE_SRT)

    def assertSRTEquals(self, first, second):
        first_items = _extract_srt_captions(first)
        second_items = _extract_srt_captions(second)
        self.assertEquals(first_items, second_items)

    def test_write(self):
        results = SRTWriter().write(self.captions)
        self.assertSRTEquals(SAMPLE_SRT, results)


def _extract_srt_captions(data):
    return tuple(line.strip() for line in data.splitlines())
