"""Position-tracking state machines for CEA-608 caption decoding.

These trackers determine when cursor movements represent simple line breaks
versus full repositioning commands that require splitting into a new cue.
"""

from ..exceptions import CaptionReadSyntaxError


class _PositioningTracker:
    """Helps determine the positioning of a node, having kept track of
    positioning-related commands.
    """

    def __init__(self, positioning=None):
        """
        :param positioning: positioning information (row, column)
        :type positioning: tuple[int]
        """
        self._positions = [positioning]
        self._breaks_required = 0
        self._repositioning_required = False
        # Since the actual column is not applied when encountering a line break
        # this attribute is used to store it and determine by comparison if the
        # next positioning is actually a Tab Offset
        self._last_column = None

    def update_positioning(self, positioning, column_jump_forces_reposition=False):
        """Being notified of a position change, updates the internal state,
        to as to be able to tell if it was a trivial change (a simple line
        break) or not.

        Strategy:
        - A jump to the very next row (row + 1): Use a single line break —
          this is simple text wrapping onto the next line. Exception: if
          paired with a column jump bigger than a tab offset in paint-on
          mode (see ``column_jump_forces_reposition``), it's treated as a
          repositioning instead, since paint-on is the only mode that can
          display independent, simultaneously-timed regions one row apart.
        - Any other row jump (a skipped row, or a jump backwards): Use
          repositioning (creates new cue). A skipped row is not an
          intentional blank line to preserve — CEA-608 PACs only declare an
          absolute row position; nothing in the spec says a gap between two
          rows must be rendered as a blank line downstream, and WebVTT/HTML
          renderers draw a real, often background-filled line for each
          break, which previously produced a visible black bar between two
          lines of text that were never meant to have a gap between them.

        :type positioning: tuple[int]
        :param positioning: a tuple (row, col)

        :type column_jump_forces_reposition: bool
        :param column_jump_forces_reposition: when True, a row+1 jump
            paired with a column jump larger than a tab offset (>3 columns)
            is treated as a repositioning rather than a break. Only
            paint-on mode can display independent, simultaneously-timed
            regions at unrelated columns, so callers should only set this
            for paint-on buffers — pop-on and roll-up buffers legitimately
            use large column shifts between buffered/wrapped lines of the
            same cue.
        """
        current = self._positions[-1]

        if not current:
            if positioning:
                # Set the positioning for the first time
                self._positions = [positioning]
            return

        row, col = current
        if self._breaks_required:
            col = self._last_column
        new_row, new_col = positioning
        is_tab_offset = new_row == row and col + 1 <= new_col <= col + 3

        # Handle row jumps
        if new_row > row:
            is_large_column_jump = (
                column_jump_forces_reposition and abs(new_col - col) > 3
            )

            # A jump to the very next row: use a line break. But if a
            # repositioning was already pending and unconsumed (no text was
            # ever written at the current position), this row jump is
            # continuing that same unresolved position change, not wrapping
            # text — so it must stay a repositioning rather than become a
            # break. Likewise, in paint-on mode, pairing the row+1 jump
            # with a column jump bigger than a tab offset means the new PAC
            # almost certainly targets an unrelated, independently-positioned
            # region rather than wrapping the current text.
            if (
                new_row == row + 1
                and not self._repositioning_required
                and not is_large_column_jump
            ):
                self._positions.append((new_row, col))
                self._breaks_required = 1
                self._last_column = new_col
            # A skipped row, a jump backwards, or a row+1 jump with a large
            # paint-on column jump: use repositioning (new cue)
            else:
                # Reset position - this triggers repositioning
                self._positions = [positioning]
                self._repositioning_required = True
        # Tab offsets after line breaks will be ignored to avoid repositioning
        elif self._breaks_required and is_tab_offset:
            return
        # force not to reposition on the same coordinates
        elif positioning == current:
            return
        else:
            # Reset the "current" position altogether.
            self._positions = [positioning]
            # Tab offsets are not interpreted as repositioning, but adjustments
            # to the previous PAC command
            if not is_tab_offset:
                self._repositioning_required = True

    def get_current_position(self):
        """Returns the current usable position

        :rtype: tuple[int]

        :raise: CaptionReadSyntaxError
        """
        if not any(self._positions):
            raise CaptionReadSyntaxError("No Preamble Address Code [PAC] was provided")
        return self._positions[0]

    def is_repositioning_required(self):
        """Determines whether the current positioning has changed non-trivially

        Trivial would mean that a line break should suffice.
        :rtype: bool
        """
        return self._repositioning_required

    def acknowledge_position_changed(self):
        """Acknowledge the position tracer that the position was changed"""
        self._repositioning_required = False

    def is_linebreak_required(self):
        """If the current position is simply one line below the previous.
        :rtype: bool
        """
        return self._breaks_required > 0

    def acknowledge_linebreak_consumed(self):
        """Call to acknowledge that the line required was consumed"""
        self._breaks_required = 0

    def reset_for_new_caption(self):
        """Reset positioning state for a new caption boundary (e.g., EOC).

        This ensures that breaks and repositioning state from the previous
        caption do not bleed into the new caption. The position list is reset
        to allow the next caption to set its position independently.
        """
        self._breaks_required = 0
        self._repositioning_required = False
        self._last_column = None
        # Reset positions to None so the next PAC sets position fresh
        self._positions = [None]


class DefaultProvidingPositionTracker(_PositioningTracker):
    """A _PositioningTracker that provides if needed a default value (14, 0), or
    uses the last positioning value set anywhere in the document
    """

    default = (14, 0)

    def __init__(self, positioning=None, default=None):
        """
        :type positioning: tuple[int]
        :param positioning: a tuple of ints (row, column)

        :type default: tuple[int]
        :param default: a tuple of ints (row, column) to use as fallback
        """
        super().__init__(positioning)

        if default:
            self.default = default

    def get_current_position(self):
        """Returns the currently tracked positioning, the last positioning that
        was set (anywhere), or the default it was initiated with

        :rtype: tuple[int]
        """
        try:
            return super().get_current_position()
        except CaptionReadSyntaxError:
            return self.default

    def update_positioning(self, positioning, column_jump_forces_reposition=False):
        """If called, sets this positioning as the default, then delegates
        to the super class.

        :param positioning: a tuple of ints (row, col)
        :type positioning: tuple[int]
        """
        if positioning:
            self.default = positioning

        super().update_positioning(positioning, column_jump_forces_reposition)
