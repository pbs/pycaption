from pycaption import DFXPReader
from pycaption.base import merge_concurrent_captions


class TestFunctions:
    def test_merge_concurrent_captions(self, dfxp_with_concurrent_captions):
        initial_caption_set = DFXPReader().read(dfxp_with_concurrent_captions)
        initial_captions = initial_caption_set.get_captions('en-US')
        caption_set = merge_concurrent_captions(initial_caption_set)
        captions = caption_set.get_captions('en-US')

        assert len(initial_captions) == 5
        assert len(captions) == 3
