import unittest

from pycaption import DFXPReader
from pycaption.base import merge_concurrent_captions
from .samples.dfxp import DFXP_WITH_CONCURRENT_CAPTIONS


class FunctionsTestCase(unittest.TestCase):

    def test_merge_concurrent_captions(self):
        caption_set = DFXPReader().read(DFXP_WITH_CONCURRENT_CAPTIONS)
        captions = caption_set.get_captions('en-US')
        self.assertEqual(len(captions), 5)

        caption_set = merge_concurrent_captions(caption_set)
        captions = caption_set.get_captions('en-US')
        self.assertEqual(len(captions), 3)
