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
        self._break_required = False
        self._repositioning_required = False
        # Since the actual column is not applied when encountering a line break
        # this attribute is used to store it and determine by comparison if the
        # next positioning is actually a Tab Offset
        self._last_column = None

    def update_positioning(self, positioning):
        """Being notified of a position change, updates the internal state,
        to as to be able to tell if it was a trivial change (a simple line
        break) or not.

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
        if self._break_required:
            col = self._last_column
        new_row, new_col = positioning
        is_tab_offset = new_row == row and col + 1 <= new_col <= col + 3

        # One line below will be treated as line break, not repositioning
        if new_row == row + 1:
            self._positions.append((new_row, col))
            self._break_required = True
            self._last_column = new_col
        # Tab offsets after line breaks will be ignored to avoid repositioning
        elif self._break_required and is_tab_offset:
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
            raise CaptionReadSyntaxError(
                'No Preamble Address Code [PAC] was provided'
            )
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
        return self._break_required

    def acknowledge_linebreak_consumed(self):
        """Call to acknowledge that the line required was consumed"""
        self._break_required = False


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
