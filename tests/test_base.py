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

    def test_two_row_jump_triggers_repositioning_not_breaks(self):
        # Skips row 2 -> not a simple wrap onto the next line, so it must
        # become a repositioning (new cue), not a break.
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((3, 0))

        assert not tracker.is_linebreak_required()
        assert tracker.is_repositioning_required()
        assert tracker._breaks_required == 0

    def test_three_row_jump_triggers_repositioning_not_breaks(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((4, 0))

        assert not tracker.is_linebreak_required()
        assert tracker.is_repositioning_required()
        assert tracker._breaks_required == 0

    def test_four_row_jump_triggers_repositioning_not_breaks(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((5, 0))

        assert not tracker.is_linebreak_required()
        assert tracker.is_repositioning_required()
        assert tracker._breaks_required == 0

    def test_acknowledge_linebreak_consumed_resets_counter(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((2, 0))
        assert tracker._breaks_required == 1

        tracker.acknowledge_linebreak_consumed()

        assert tracker._breaks_required == 0
        assert not tracker.is_linebreak_required()

    def test_tab_offset_after_break_is_ignored(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((2, 0))
        tracker.update_positioning((2, 2))

        assert not tracker.is_repositioning_required()

    def test_pending_repositioning_is_preserved_across_small_row_jump(self):
        tracker = _PositioningTracker((13, 4))
        # Same-row column jump with no text written: leaves a repositioning
        # pending and unconsumed.
        tracker.update_positioning((13, 24))
        assert tracker.is_repositioning_required()

        # A small row jump on top of that pending, unconsumed repositioning
        # must not be reinterpreted as a trivial line break.
        tracker.update_positioning((15, 8))

        assert tracker.is_repositioning_required()
        assert not tracker.is_linebreak_required()
        assert tracker._breaks_required == 0

    def test_row_jump_without_pending_repositioning_still_creates_breaks(self):
        tracker = _PositioningTracker((14, 10))
        tracker.update_positioning((15, 1))

        assert tracker.is_linebreak_required()
        assert tracker._breaks_required == 1
        assert not tracker.is_repositioning_required()

    def test_paint_on_row_plus_one_with_large_column_jump_forces_reposition(self):
        # A row+1 jump normally stays a break, but a large column jump
        # alongside it in paint-on mode signals an unrelated, independently-
        # positioned region one row below, so it must reposition instead.
        tracker = _PositioningTracker((13, 0))
        tracker.update_positioning((14, 20), column_jump_forces_reposition=True)

        assert tracker.is_repositioning_required()
        assert not tracker.is_linebreak_required()

    def test_row_plus_one_with_large_column_jump_stays_break_outside_paint_on(self):
        # The same large column jump must NOT force a repositioning when
        # column_jump_forces_reposition is left at its default (pop-on and
        # roll-up buffers legitimately use large column shifts between
        # wrapped lines of the same cue).
        tracker = _PositioningTracker((13, 0))
        tracker.update_positioning((14, 20))

        assert not tracker.is_repositioning_required()
        assert tracker.is_linebreak_required()

    def test_paint_on_column_jump_boundary_at_tab_offset_threshold(self):
        """A column jump of exactly 3 (matching the tab-offset threshold
        used elsewhere) alongside a row+1 jump must stay a break; one
        column beyond that, a jump of 4, must force a repositioning.
        Checked in both the positive (rightward) and negative (leftward)
        column directions, since the implementation compares by absolute
        value.
        """
        tracker = _PositioningTracker((13, 0))
        tracker.update_positioning((14, 3), column_jump_forces_reposition=True)
        assert not tracker.is_repositioning_required()
        assert tracker.is_linebreak_required()

        tracker = _PositioningTracker((13, 0))
        tracker.update_positioning((14, 4), column_jump_forces_reposition=True)
        assert tracker.is_repositioning_required()

        tracker = _PositioningTracker((13, 10))
        tracker.update_positioning((14, 7), column_jump_forces_reposition=True)
        assert not tracker.is_repositioning_required()
        assert tracker.is_linebreak_required()

        tracker = _PositioningTracker((13, 10))
        tracker.update_positioning((14, 6), column_jump_forces_reposition=True)
        assert tracker.is_repositioning_required()

    def test_reset_for_new_caption_clears_all_state(self):
        tracker = _PositioningTracker((1, 0))
        tracker.update_positioning((3, 0))

        tracker.reset_for_new_caption()

        assert tracker._breaks_required == 0
        assert not tracker._repositioning_required
        assert tracker._last_column is None
        assert tracker._cursor_column is None
        assert not tracker._origin_locked
        assert not tracker._line_has_text
        assert tracker._pending_padding == 0
        assert tracker._pending_overlap == 0
        assert tracker._positions == [None]

    @pytest.mark.parametrize(
        "new_col,continues",
        [
            (8, True),  # exactly at the cursor: the encoder restating itself
            (11, True),  # a tab offset past it
            (12, False),  # one column beyond a tab offset
            (5, True),  # a tab offset behind it, the common real-world case
            (4, False),  # one column further back than that
        ],
    )
    def test_same_row_pac_continues_the_line_within_a_tab_offset_of_the_cursor(
        self, new_col, continues
    ):
        """Origin (15, 0) with eight characters written, so the cursor is at
        8. A same-row PAC within a tab offset of the cursor in either
        direction continues the line and leaves the origin alone; anything
        further out abandons it. Compared by absolute value, since encoders
        back-correct as often as they skip forward.
        """
        tracker = _PositioningTracker((15, 0))
        tracker.advance_cursor(8)

        tracker.update_positioning((15, new_col))

        assert tracker.is_repositioning_required() is not continues
        assert not tracker.is_linebreak_required()
        assert tracker.get_current_position() == (
            (15, 0) if continues else (15, new_col)
        )

    def test_a_tab_offset_settles_the_columns_the_pac_pointed_back_over(self):
        tracker = _PositioningTracker((15, 0))
        tracker.advance_cursor(8)
        tracker.update_positioning((15, 6))

        # The offset is where the text really starts, so the PAC was never
        # pointing back over anything
        tracker.update_positioning((15, 8), is_offset=True)

        assert tracker.consume_pending_overlap() == 0

    def test_abandoning_the_line_discards_the_columns_it_owed(self):
        tracker = _PositioningTracker((15, 0))
        tracker.advance_cursor(2)
        tracker.update_positioning((15, 4))
        assert tracker._pending_padding == 2

        # A repositioning starts a fresh line elsewhere, so the old line's
        # blank columns must not be indented onto it
        tracker.update_positioning((15, 24))

        assert tracker.is_repositioning_required()
        assert tracker.consume_pending_padding() == 0

    def test_a_line_break_discards_the_columns_a_pac_pointed_back_over(self):
        tracker = _PositioningTracker((14, 0))
        tracker.advance_cursor(8)
        tracker.update_positioning((14, 6))
        assert tracker._pending_overlap == 2

        # Text on the new line lands on a row of its own, so it cannot
        # overwrite what the line above already put on those columns
        tracker.update_positioning((15, 0))

        assert tracker.is_linebreak_required()
        assert tracker.consume_pending_overlap() == 0
