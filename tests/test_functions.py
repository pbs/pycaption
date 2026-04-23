from bs4 import BeautifulSoup

from pycaption import DFXPReader
from pycaption.base import merge_concurrent_captions
from pycaption.utils import is_leaf


class TestFunctions:
    def test_merge_concurrent_captions(self, dfxp_with_concurrent_captions):
        initial_caption_set = DFXPReader().read(dfxp_with_concurrent_captions)
        initial_captions = initial_caption_set.get_captions("en-US")
        caption_set = merge_concurrent_captions(initial_caption_set)
        captions = caption_set.get_captions("en-US")

        assert len(initial_captions) == 5
        assert len(captions) == 3


class TestIsLeaf:
    def test_navigable_string_is_leaf(self):
        soup = BeautifulSoup("<p>hello</p>", "html.parser")

        assert is_leaf(soup.p.string)

    def test_br_tag_is_leaf(self):
        soup = BeautifulSoup("<br/>", "html.parser")

        assert is_leaf(soup.br)

    def test_non_br_tag_is_not_leaf(self):
        soup = BeautifulSoup("<p>x</p>", "html.parser")

        assert not is_leaf(soup.p)
