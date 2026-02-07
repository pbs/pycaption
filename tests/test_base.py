import pytest

from pycaption.base import CaptionList, Caption, BaseWriter
from pycaption.geometry import Layout, Point, Size, UnitEnum


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


class TestBaseWriter:
    def setup_method(self):
        # Create a mock layout_info for testing
        self.layout_info = Layout(
            origin=Point(Size(10, UnitEnum.PERCENT), Size(20, UnitEnum.PERCENT))
        )

    def test_include_positioning_default_true(self):
        """Test that include_positioning defaults to True"""
        writer = BaseWriter()
        assert writer.include_positioning is True

    def test_include_positioning_false(self):
        """Test that include_positioning can be set to False"""
        writer = BaseWriter(include_positioning=False)
        assert writer.include_positioning is False

    def test_relativize_and_fit_to_screen_with_include_positioning_true(self):
        """Test that layout_info is processed when include_positioning=True"""
        writer = BaseWriter(include_positioning=True, video_width=640, video_height=360)
        result = writer._relativize_and_fit_to_screen(self.layout_info)
        # Should return processed layout_info, not None
        assert result is not None

    def test_relativize_and_fit_to_screen_with_include_positioning_false(self):
        """Test that layout_info is ignored when include_positioning=False"""
        writer = BaseWriter(include_positioning=False, video_width=640, video_height=360)
        result = writer._relativize_and_fit_to_screen(self.layout_info)
        # Should return None when positioning is disabled
        assert result is None

    def test_relativize_and_fit_to_screen_with_none_layout_info(self):
        """Test that None layout_info is handled correctly"""
        writer = BaseWriter(include_positioning=True)
        result = writer._relativize_and_fit_to_screen(None)
        assert result is None

    def test_relativize_and_fit_to_screen_with_none_layout_info_and_positioning_false(self):
        """Test that None layout_info returns None even when include_positioning=False"""
        writer = BaseWriter(include_positioning=False)
        result = writer._relativize_and_fit_to_screen(None)
        assert result is None

    def test_backward_compatibility_default_parameters(self):
        """Test that all BaseWriter parameters have appropriate defaults for backward compatibility"""
        writer = BaseWriter()
        assert writer.relativize is True
        assert writer.video_width is None
        assert writer.video_height is None
        assert writer.fit_to_screen is True
        assert writer.include_positioning is True
