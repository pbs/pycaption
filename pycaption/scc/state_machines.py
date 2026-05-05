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

    def update_positioning(self, positioning):
        """Being notified of a position change, updates the internal state,
        to as to be able to tell if it was a trivial change (a simple line
        break) or not.

        Strategy:
        - Small jumps (1-3 rows): Use line breaks to preserve visual spacing
        - Large jumps (4+ rows): Use repositioning (creates new cue)

        :type positioning: tuple[int]
        :param positioning: a tuple (row, col)
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

        # Threshold for when to use breaks vs repositioning
        # Jumps of 4+ rows will trigger repositioning instead of adding breaks
        MAX_BREAKS_THRESHOLD = 3

        # Handle row jumps
        if new_row > row:
            row_diff = new_row - row

            # Small jumps (1-3 rows): Use line breaks to preserve visual spacing
            if row_diff <= MAX_BREAKS_THRESHOLD:
                self._positions.append((new_row, col))
                # Add breaks equal to row difference
                # Row N -> N+1: 1 break
                # Row N -> N+2: 2 breaks (preserves 1 blank line)
                # Row N -> N+3: 3 breaks (preserves 2 blank lines)
                self._breaks_required = row_diff
                self._last_column = new_col
            # Large jumps (4+ rows): Use repositioning (new cue)
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
        else:
            return self._positions[0]

    def is_repositioning_required(self):
        """Determines whether the current positioning has changed non-trivially

        Trivial would be mean that a line break should suffice.
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

    def update_positioning(self, positioning):
        """If called, sets this positioning as the default, then delegates
        to the super class.

        :param positioning: a tuple of ints (row, col)
        :type positioning: tuple[int]
        """
        if positioning:
            self.default = positioning

        super().update_positioning(positioning)
