import pytest

from pycaption.base import CaptionList, Caption


class TestCaption:
    def setup_method(self):
        self.caption = Caption(0, 999999999999, ['test'])

    def test_format_start(self):
        assert self.caption.format_start() == '00:00:00.000'

    def test_format_end(self):
        assert self.caption.format_end() == '13:46:39.999'


class TestCaptionList:
    def setup_method(self):
        self.layout_info = "My Layout"
        self.caps = CaptionList([1, 2, 3], layout_info=self.layout_info)

    def test_splice(self):
        newcaps = self.caps[1:]

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_mul(self):
        newcaps = self.caps * 2

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_rmul(self):
        newcaps = 2 * self.caps

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_add_list_to_caption_list(self):
        newcaps = self.caps + [9, 8, 7]

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

    def test_add_two_caption_lists(self):
        newcaps = self.caps + CaptionList([4], layout_info=None)

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

        newcaps = self.caps + CaptionList([4], layout_info=self.layout_info)

        assert isinstance(newcaps, CaptionList)
        assert newcaps.layout_info == self.layout_info

        with pytest.raises(ValueError):
            newcaps = self.caps + CaptionList([4], layout_info="Other Layout")
