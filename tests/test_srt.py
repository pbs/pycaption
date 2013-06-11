import unittest

from pycaption import SRTReader, SRTWriter

from .samples import SAMPLE_SRT


class SRTReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SRTReader().detect(SAMPLE_SRT))

    def test_proper_pcc_format(self):
        captions = SRTReader().read(SAMPLE_SRT)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(7, len(captions["captions"]["en"]))

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
