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
        self._last_char_position = 0
        self._spaces_to_add = 0

    def update_positioning(self, positioning):
        """Being notified of a position change, updates the internal state,
        to as to be able to tell if it was a trivial change (a simple line
        break) or not.

        :type positioning: tuple[int]
        :param positioning: a tuple (row, col)
        """
        previous = self._positions[-1]
        if not previous:
            if positioning:
                # Set the positioning for the first time
                self._positions = [positioning]
            return

        previous_row, previous_column = previous
        new_row, new_col = positioning
        print("previous", previous)
        print("positioning", positioning)
        if new_row == previous_row + 1:
            self._break_required = True
            self._spaces_to_add = new_col
            self._last_char_position = new_col
            print("break", new_col, self._last_char_position)
        else:
            self._repositioning_required = True
            self._spaces_to_add = new_col - self._last_char_position
            print("repo", new_col, self._last_char_position)

        self._positions = [positioning]
        if new_row == previous_row and new_col < self._last_char_position:
            raise ValueError(
                f"We cannot go back positioning from {self._last_char_position} to  {new_col}")

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
