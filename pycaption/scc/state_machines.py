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
        # Column just past the last character written on the current line. The
        # origin in _positions[0] stays put for the life of the caption, so the
        # cursor is what an incoming PAC has to be compared against.
        self._cursor_column = positioning[1] if positioning else None
        # True once text exists at the current origin. Caption-scoped, not
        # line-scoped: a line break starts a new line but does not unlock the
        # origin, since a caption has only one.
        self._origin_locked = False
        # True once text exists on the line currently being written. Unlike
        # _origin_locked this is line-scoped, so it can tell a Tab Offset that
        # indents a line still empty after a break from one that skips forward
        # over columns text has already passed.
        self._line_has_text = False
        # Blank columns skipped by a PAC that landed ahead of the cursor. They
        # are part of the line and have to reach the text, or the words either
        # side of the gap end up run together.
        self._pending_padding = 0
        # Columns a PAC pointed back over, not yet known to be an overwrite.
        self._pending_overlap = 0

    def update_positioning(
        self, positioning, column_jump_forces_reposition=False, is_offset=False
    ):
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
        - A PAC on the same row: compare it against the cursor, not the
          origin. Landing within a tab offset of where the text actually
          ended continues the current line — no new cue, and no change to
          the origin already stamped on this caption's nodes. Landing
          further out abandons the line and repositions, unless it merely
          restates the position already in effect: re-asserting a position
          is not a move, so it cannot start a new cue however much text has
          been written since.
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

        :type is_offset: bool
        :param is_offset: whether the command being interpreted is a Tab
            Offset. A Tab Offset is an adjustment to the PAC that preceded
            it and is never a repositioning, so it is recognised by command
            identity rather than guessed at from its coordinates — the
            column it computes comes from the last position seen, which
            after some text has been written is not the cursor at all.
        """
        current = self._positions[-1]

        if not current:
            if positioning:
                # Set the positioning for the first time
                self._positions = [positioning]
                self._cursor_column = positioning[1]
                self._origin_locked = False
                self._line_has_text = False
            return

        row, col = current
        if self._breaks_required:
            col = self._last_column
        new_row, new_col = positioning
        cursor = self._cursor_column if self._cursor_column is not None else col

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
                # The new line starts where the PAC points and carries no text
                # yet, but the caption keeps _positions[0] as its origin.
                self._cursor_column = new_col
                # Text arriving on the new line cannot overwrite the old one,
                # and blank columns owed to the line being left behind are not
                # indentation for the line the break opens
                self._pending_overlap = 0
                self._pending_padding = 0
                self._line_has_text = False
            # A skipped row, a jump backwards, or a row+1 jump with a large
            # paint-on column jump: use repositioning (new cue)
            else:
                self._reposition(positioning)
        # A jump backwards is never text flowing onto the next line
        elif new_row < row:
            self._reposition(positioning)
        # Same row, and either a Tab Offset, a PAC restating the position
        # already in effect, or a column within a tab offset of where the text
        # ended: a continuation of the line being written
        elif is_offset or positioning == current or abs(new_col - cursor) <= 3:
            if is_offset:
                # The offset resolves the PAC it follows: this, not that PAC's
                # own column, is where the text starts, so there is nothing
                # behind the cursor left to overwrite. An offset that resolves
                # behind the text is moving back over it rather than nudging the
                # PAC onto the cursor, and the overwrite it does own is measured
                # below.
                self._pending_overlap = 0
            if not self._origin_locked and not self._breaks_required:
                # Nothing written at this origin yet, so the command still
                # indents it (a PAC immediately followed by a Tab Offset)
                self._positions = [positioning]
                self._cursor_column = new_col
            elif is_offset and not self._line_has_text:
                # The line the break opened carries no text yet, so the offset
                # still indents it. The caption keeps the origin it already has
                # — only where this line starts moves.
                self._last_column = new_col
                self._cursor_column = new_col
            elif is_offset and new_col >= cursor:
                # A Tab Offset reached part-way through a line skips forward
                # over screen columns the text never filled, so they arrive as
                # spaces rather than closing up against the text before them
                if new_col > cursor:
                    self._pending_padding += new_col - cursor
                    self._cursor_column = new_col
            else:
                overlap = cursor - new_col
                if overlap < 0:
                    # The columns between the text and the PAC are blank
                    # screen columns, not a seam to close up
                    self._pending_padding += -overlap
                # A command pointing back over text already written is either a
                # real overwrite or an evaluation-order artifact: a PAC read
                # before the Tab Offset or mid-row code that nudges it forward
                # onto the cursor. Nothing here can tell them apart, so record
                # what it would cover and let the next command settle it — an
                # offset or mid-row code cancels it, arriving text confirms it.
                # A PAC sets the cursor, so however far back it points is
                # covered, not just the tab-offset window: text following a PAC
                # that restates a column behind the text overwrites from there.
                self._pending_overlap = max(overlap, 0)
                # Never rewind on the PAC alone: the cursor stays where the text
                # left it until text arrives to confirm the overwrite, which is
                # what settles the overlap and moves the cursor back.
                self._cursor_column = max(cursor, new_col)
        else:
            self._reposition(positioning)

    def _reposition(self, positioning):
        """Abandon the current origin for a new one, requiring a new cue.

        :type positioning: tuple[int]
        """
        self._positions = [positioning]
        self._cursor_column = positioning[1]
        self._repositioning_required = True
        # A line that is being abandoned cannot still owe a break: the break was
        # opened for text that never arrived, and carrying it over would let it
        # be consumed first, swallowing this repositioning.
        self._breaks_required = 0
        # The new origin carries no text yet, so a Tab Offset arriving before
        # any text may still indent it
        self._origin_locked = False
        self._line_has_text = False
        # The abandoned line's blank columns are not carried into the new one,
        # and its text is no longer in front of the cursor to be overwritten
        self._pending_padding = 0
        self._pending_overlap = 0

    def advance_cursor(self, count):
        """Notify the tracker that ``count`` columns of text were written.

        Negative counts retract the cursor, as a backspace does.

        :type count: int
        """
        if self._cursor_column is not None:
            self._cursor_column += count
        if count > 0:
            self._origin_locked = True
            self._line_has_text = True

    def consume_pending_padding(self):
        """Return and clear the blank columns owed to the line.

        The cursor has already been moved past them, so the caller adds the
        spaces without advancing it again.

        :rtype: int
        """
        padding, self._pending_padding = self._pending_padding, 0
        return padding

    def consume_pending_overlap(self):
        """Return and clear the columns a PAC pointed back over.

        Called when text arrives, which is what settles the question: nothing
        moved the PAC forward, so it really did point back over the line and the
        characters now landing cover that many columns of it.

        :rtype: int
        """
        overlap, self._pending_overlap = self._pending_overlap, 0
        return overlap

    def cancel_pending_overlap(self):
        """Drop the overlap, the column the PAC pointed at being taken by a
        command rather than by text.
        """
        self._pending_overlap = 0

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
        self._cursor_column = None
        self._origin_locked = False
        self._line_has_text = False
        self._pending_padding = 0
        self._pending_overlap = 0
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

    def update_positioning(
        self, positioning, column_jump_forces_reposition=False, is_offset=False
    ):
        """If called, sets this positioning as the default, then delegates
        to the super class.

        :param positioning: a tuple of ints (row, col)
        :type positioning: tuple[int]
        """
        if positioning:
            self.default = positioning

        super().update_positioning(
            positioning, column_jump_forces_reposition, is_offset
        )
