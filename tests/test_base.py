import unittest

from pycaption import SUPPORTED_READERS, SUPPORTED_WRITERS
from pycaption.base import CaptionList
from .samples.sami import SAMPLE_SAMI_WITH_LAYOUT, SAMPLE_SAMI_IGNORE_LAYOUT
from .samples.scc import SAMPLE_SCC_WITH_LAYOUT, SAMPLE_SCC_IGNORE_LAYOUT
from .samples.dfxp import SAMPLE_DFXP_WITH_LAYOUT, SAMPLE_DFXP_IGNORE_LAYOUT
from .samples.srt import SAMPLE_SRT_WITH_LAYOUT, SAMPLE_SRT_IGNORE_LAYOUT
from .samples.webvtt import SAMPLE_WEBVTT_WITH_LAYOUT, SAMPLE_WEBVTT_IGNORE_LAYOUT


class CaptionListTestCase(unittest.TestCase):

    def setUp(self):
        self.layout_info = "My Layout"
        self.caps = CaptionList([1, 2, 3], layout_info=self.layout_info)

    def test_splice(self):
        newcaps = self.caps[1:]
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

    def test_mul(self):
        newcaps = self.caps * 2
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

    def test_rmul(self):
        newcaps = 2 * self.caps
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

    def test_add_list_to_caption_list(self):
        newcaps = self.caps + [9, 8, 7]
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

    def test_add_two_caption_lists(self):
        newcaps = self.caps + CaptionList([4], layout_info=None)
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

        newcaps = self.caps + CaptionList([4], layout_info=self.layout_info)
        self.assertTrue(isinstance(newcaps, CaptionList))
        self.assertTrue(newcaps.layout_info == self.layout_info)

        with self.assertRaises(ValueError):
            newcaps = self.caps + CaptionList([4], layout_info="Other Layout")


class TestReaderLayoutIgnore(unittest.TestCase):

    def test_(self):
        samples_with_layout = [SAMPLE_DFXP_WITH_LAYOUT, SAMPLE_WEBVTT_WITH_LAYOUT, SAMPLE_SAMI_WITH_LAYOUT,
                               SAMPLE_SRT_WITH_LAYOUT, SAMPLE_SCC_WITH_LAYOUT]
        samples_no_layout = [SAMPLE_DFXP_IGNORE_LAYOUT, SAMPLE_WEBVTT_IGNORE_LAYOUT, SAMPLE_SAMI_IGNORE_LAYOUT,
                             SAMPLE_SRT_IGNORE_LAYOUT, SAMPLE_SCC_IGNORE_LAYOUT]

        for Reader, Writer, sample_with_layout, sample_no_layout in zip(SUPPORTED_READERS,
                                                                        SUPPORTED_WRITERS,
                                                                        samples_with_layout,
                                                                        samples_no_layout):
            reader = Reader(ignore_layout=True)
            writer = Writer()

            caption_set = reader.read(sample_with_layout.decode('utf-8'))
            result = writer.write(caption_set)

            self.assertEqual(sample_no_layout, result)

            for caption in caption_set._captions['en-US']:
                self.assertIsNone(caption.layout_info)
