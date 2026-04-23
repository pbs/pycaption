import pytest

from pycaption import CaptionReadError
from pycaption.base import Caption, CaptionList
from pycaption.exceptions import CaptionReadSyntaxError
from pycaption.scc.state_machines import _PositioningTracker



class TestCaptionReadError:
    def test_str_includes_class_name_and_message(self):
        err = CaptionReadError("bad data")

        assert str(err) == "CaptionReadError(bad data)"

    def test_subclass_uses_own_class_name(self):
        err = CaptionReadSyntaxError("oops")

        assert str(err) == "CaptionReadSyntaxError(oops)"


class TestCaption:
    def setup_method(self):
        self.caption = Caption(0, 999999999999, ["test"])

    def test_format_start(self):
        assert self.caption.format_start() == "00:00:00.000"

    def test_format_end(self):
        assert self.caption.format_end() == "13:46:39.999"


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


class TestPositioningTracker:
    def test_single_row_jump_creates_one_break(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((2, 0))

        assert tracker.is_linebreak_required()
        assert tracker._breaks_required == 1
        assert not tracker.is_repositioning_required()

    def test_two_row_jump_creates_two_breaks(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((3, 0))

        assert tracker._breaks_required == 2
        assert tracker.is_linebreak_required()

    def test_three_row_jump_creates_three_breaks(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((4, 0))

        assert tracker._breaks_required == 3
        assert tracker.is_linebreak_required()

    def test_four_row_jump_triggers_repositioning_not_breaks(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((5, 0))

        assert not tracker.is_linebreak_required()
        assert tracker.is_repositioning_required()
        assert tracker._breaks_required == 0

    def test_acknowledge_linebreak_consumed_resets_counter(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((3, 0))
        assert tracker._breaks_required == 2

        tracker.acknowledge_linebreak_consumed()

        assert tracker._breaks_required == 0
        assert not tracker.is_linebreak_required()

    def test_tab_offset_after_break_is_ignored(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((2, 0))
        tracker.update_positioning((2, 2))

        assert not tracker.is_repositioning_required()

    def test_reset_for_new_caption_clears_all_state(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((3, 0))

        tracker.reset_for_new_caption()

        assert tracker._breaks_required == 0
        assert not tracker._repositioning_required
        assert tracker._last_column is None
        assert tracker._positions == [None]
