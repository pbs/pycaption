"""Specialized collections and node creators for SCC caption processing.

Provides mutable caption builders, timing-correcting lists, instruction-node
buffering, and italics-formatting utilities used by the SCC reader to convert
raw CEA-608 commands into CaptionNode trees.
"""

import collections
import copy

from ..base import Caption, CaptionList, CaptionNode
from ..geometry import (
    Alignment,
    HorizontalAlignmentEnum,
    Layout,
    Point,
    Size,
    UnitEnum,
    VerticalAlignmentEnum,
)
from .constants import (
    BACKGROUND_COLOR_CODES,
    EXTENDED_CHARS,
    ITALICS_COMMANDS,
    MICROSECONDS_PER_CODEWORD,
    MID_ROW_CODES,
    PAC_BYTES_TO_POSITIONING_MAP,
    PAC_TAB_OFFSET_COMMANDS,
    STYLE_SETTING_COMMANDS,
    UNDERLINE_COMMANDS,
)


PopOnCue = collections.namedtuple("PopOnCue", "buffer, start, end")

# First two hex chars of SCC codes that produce punctuation ['.', '!', '?', ',']
PUNCTUATION_PREFIXES = frozenset(["ae", "a1", "bf", "2c"])


class PreCaption:
    """Mutable caption builder for incremental construction during SCC decoding.

    Caption requires valid timing and non-empty nodes at construction.
    SCC commands arrive one at a time, so this builder accumulates state
    and converts to an immutable Caption via to_real_caption() once complete.
    """

    _INTERNAL_STYLE_KEYS = {"caption_mode", "roll_up_rows"}

    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end
        self.nodes = []
        self.style = {}
        self.layout_info = None

    def to_real_caption(self):
        """Convert this mutable holder into an immutable Caption instance.

        :rtype: Caption
        """
        display_style = {
            k: v for k, v in self.style.items() if k not in self._INTERNAL_STYLE_KEYS
        }
        caption = Caption(
            self.start, self.end, self.nodes, display_style, self.layout_info
        )
        caption.caption_mode = self.style.get("caption_mode")
        caption.roll_up_rows = self.style.get("roll_up_rows")
        return caption


class TimingCorrectingCaptionList(list):
    """List of captions. When appending new elements, it will correct the end time
    of the last ones, so they end when the new caption gets added.

    "last ones" could mean the last caption `append`ed or all of the last
    captions with which this list was `extended`

    Also, doesn't allow Nones or empty captions
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_batch = ()

    def append(self, p_object):
        """When appending a new caption to the list, make sure the last one
        has an end. Also, don't add empty captions

        :type p_object: Caption | None
        """
        if p_object is None or not p_object.nodes:
            return

        self._update_last_batch(self._last_batch, p_object)

        self._last_batch = (p_object,)

        super().append(p_object)

    def extend(self, iterable):
        """Adds the elements in the iterable to the list, regarding the first
        caption's start time as the end time for the previously added
        caption(s)

        :param iterable: an iterable of Caption instances
        """
        appendable_items = [item for item in iterable if item and item.nodes]
        self._update_last_batch(self._last_batch, *appendable_items)

        self._last_batch = tuple(appendable_items)

        super().extend(appendable_items)

    @staticmethod
    def _update_last_batch(batch, *new_captions):
        """Given a batch of captions, sets their end time equal to the start
        time of the first caption in *new_captions

        The start time of the first caption in new_captions should never be 0.
        This means an invalid SCC file.

        :type batch: tuple[Caption, ...]
        :type new_captions: Caption
        """
        if not new_captions:
            return
        if not new_captions[0]:
            return
        if not new_captions[0].nodes:
            return

        new_caption = new_captions[0]

        if batch and (
            batch[-1].end == 0
            or new_caption.start - batch[-1].end < 5 * MICROSECONDS_PER_CODEWORD + 1
        ):
            for caption in batch:
                caption.end = new_caption.start


class NotifyingDict(dict):
    """Dictionary-like object, that treats one key as 'active',
    and notifies observers if the active key changed
    """

    # Need an unhashable object as initial value for the active key.
    # That way we're sure this was never a key in the dict.
    _guard = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active_key = self._guard
        self.observers = []

    def set_active(self, key):
        """Sets the active key

        :param key: any hashable object
        """
        if key not in self:
            raise ValueError("No such key present")

        # Notify observers of the change
        if key != self.active_key:
            for observer in self.observers:
                observer(self.active_key, key)

        self.active_key = key

    def get_active(self):
        """Returns the value corresponding to the active key"""
        if self.active_key is self._guard:
            raise KeyError("No active key set")

        return self[self.active_key]

    def add_change_observer(self, observer):
        """Receives a callable function, which it will call if the active
        element changes.

        The observer will receive 2 positional arguments: the old and new key

        :param observer: any callable that can be called with 2 positional
            arguments
        """
        if not callable(observer):
            raise TypeError("The observer should be callable")

        self.observers.append(observer)


class CaptionCreator:
    """Creates and maintains a collection of Captions"""

    def __init__(self):
        self._collection = TimingCorrectingCaptionList()

        # subset of self._collection;
        # captions here will be susceptible to time corrections
        self._still_editing = []

    def correct_last_timing(self, end_time, force=False):
        """Called to set the time on the last Caption(s) stored with no end
        time

        :type force: bool
        :param force: Set the end time even if there's already an end time

        :type end_time: float
        :param end_time: microseconds; the end of the caption;
        """
        if not self._still_editing:
            return

        if force:
            # Select all last captions
            captions_to_correct = self._still_editing
        elif self._still_editing[-1].end == 0:
            # Only select the last captions if they haven't gotten their
            # end time set yet
            captions_to_correct = self._still_editing
        else:
            return

        for caption in captions_to_correct:
            caption.end = end_time

    @staticmethod
    def _new_precaption(start, end, caption_mode, roll_up_rows):
        """Create a PreCaption with timing and optional SCC metadata."""
        caption = PreCaption()
        caption.start = start
        caption.end = end
        if caption_mode:
            caption.style["caption_mode"] = caption_mode
        if roll_up_rows:
            caption.style["roll_up_rows"] = roll_up_rows
        return caption

    def create_and_store(
        self, node_buffer, start, end=0, caption_mode=None, roll_up_rows=None
    ):
        """Interpreter method, will convert the buffer into one or more Caption
        objects, storing them internally.

        This method relies on the InstructionNodeCreator's ability to generate
        InstructionNodes properly, so at this point we can convert
        _InstructionNodes nodes almost 1:1 to CaptionNodes

        :type node_buffer: InstructionNodeCreator

        :type start: float
        :param start: the start time in microseconds
        :type end: float
        :param end: the end time in microseconds
        :type caption_mode: str or None
        :param caption_mode: CEA-608 mode ("pop_on", "roll_up", "paint_on")
        :type roll_up_rows: int or None
        :param roll_up_rows: roll-up depth (2, 3, or 4) when mode is roll_up
        """
        if node_buffer.is_empty():
            return

        caption = self._new_precaption(start, end, caption_mode, roll_up_rows)
        self._still_editing = [caption]

        instructions = list(node_buffer)
        # Only pop-on is widened: roll-up joins its rows onto one line, and
        # paint-on already splits a line that jumps columns into its own cue
        leftmost_columns = (
            _leftmost_line_starts(instructions) if caption_mode == "pop_on" else []
        )
        cue_index = 0
        indenter = _LineIndenter(enabled=bool(leftmost_columns))

        for instruction in instructions:
            if instruction.is_empty():
                continue

            position = instruction.position
            if cue_index < len(leftmost_columns) and position:
                position = (position[0], leftmost_columns[cue_index])

            if instruction.requires_repositioning():
                caption = self._new_precaption(start, end, caption_mode, roll_up_rows)
                self._still_editing.append(caption)
                cue_index += 1
                indenter.start_cue()
                continue

            text = indenter.text_for(instruction, position)
            _append_caption_node(caption, instruction, text, position)

        self._collection.extend(self._still_editing)

    def get_all(self):
        """Returns the Caption collection as a CaptionList

        :rtype: CaptionList
        """
        caption_list = CaptionList()
        for precap in self._collection:
            caption_list.append(precap.to_real_caption())
        return caption_list


class InstructionNodeCreator:
    """Creates _InstructionNode instances from characters and commands, storing
    them internally
    """

    def __init__(self, collection=None, position_tracker=None):
        """
        :param collection: an optional collection of nodes

        :param position_tracker:
        :return:
        """
        if not collection:
            self._collection = []
        else:
            self._collection = collection

        self.last_style = (
            None  # can be italic on or italic off as we only support italics
        )
        self._position_tracer = position_tracker

    def is_empty(self):
        """Whether any text was added to the buffer"""
        return not any(element.text for element in self._collection)

    def add_chars(self, *chars):
        """Adds characters to a text node (last text node, or a new one)

        :param chars: tuple containing text (Unicode string)
        """
        if not chars:
            return

        current_position = self._position_tracer.get_current_position()

        # get or create a usable node
        if (
            self._collection
            and self._collection[-1].is_text_node()
            and not self._position_tracer.is_repositioning_required()
        ):
            node = self._collection[-1]
        else:
            # create first node
            node = _InstructionNode(position=current_position)
            self._collection.append(node)

        # handle line break(s) - may be multiple for multi-row jumps
        if self._position_tracer.is_linebreak_required():
            line_start = self._position_tracer.get_line_start_column()
            for _ in range(self._position_tracer._breaks_required):
                self._collection.append(
                    _InstructionNode.create_break(
                        position=current_position, line_start=line_start
                    )
                )
            self._position_tracer.acknowledge_linebreak_consumed()
            node = _InstructionNode.create_text(current_position)
            self._collection.append(node)
            if self._position_tracer.is_repositioning_required():
                # it means we have a reposition command which was not followed by
                # any text, so we just ignore it and break
                self._position_tracer.acknowledge_position_changed()

        # handle completely new positioning
        elif self._position_tracer.is_repositioning_required():
            self._collection.append(
                _InstructionNode.create_repositioning_command(current_position)
            )
            node = _InstructionNode.create_text(current_position)
            self._collection.append(node)
            self._position_tracer.acknowledge_position_changed()

        overlap = self._position_tracer.consume_pending_overlap()
        if overlap and self._mark_overwrite(overlap, current_position):
            node = _InstructionNode.create_text(current_position)
            self._collection.append(node)

        padding = self._position_tracer.consume_pending_padding()
        if padding:
            node.add_chars(" " * padding)
        node.add_chars(*chars)
        self._position_tracer.advance_cursor(len("".join(chars)))

    def _settle_line_start(self):
        """Record on the break opening this line the column it now starts at

        A break can be emitted before the Tab Offset that indents its line
        arrives (a PAC closing italics emits it), so the column it recorded then
        is not where the line starts.
        """
        for node in reversed(self._collection):
            if node.is_explicit_break():
                node.line_start = self._position_tracer.get_line_start_column()
                return
            if node.is_text_node() and node.text:
                return

    def _mark_overwrite(self, overlap, position):
        """Record that the characters arriving next land on columns a PAC
        pointed back over, and move the cursor back onto them.

        Whether they really replace those columns cannot be settled yet: that
        depends on how much text follows and how long the line gets, which only
        the finished line tells. So the text stays in place and a marker holds
        the question until the buffer is read (see ``_resolve_overwrites``).

        Overlap counts screen columns, not nodes, so it spans however many nodes
        a style change happened to split the line into. It stops at a break or a
        repositioning, which end the line the PAC pointed into.

        :param overlap: how many columns the PAC pointed back over
        :type position: tuple[int]
        :return: whether the line had any text for the PAC to point back over
        :rtype: bool
        """
        columns = min(overlap, _line_length(self._collection))
        if not columns:
            return False
        self._collection.append(_InstructionNode.create_overwrite(position, columns))
        self._position_tracer.advance_cursor(-columns)
        return True

    @staticmethod
    def get_style_for_command(command):
        """Return the style category for a CEA-608 style-setting command.

        :param command: a 4-char hex command string
        :rtype: str
        :return: one of "italic", "underline", or "plaintext"
        """
        if command in ITALICS_COMMANDS:
            return "italic"
        elif command in UNDERLINE_COMMANDS:
            return "underline"
        else:
            # as we only check STYLE_SETTING_COMMANDS,
            # only remaining possibility is plain text
            return "plaintext"

    def interpret_command(self, command, next_is_punctuation=False, is_paint_on=False):
        """Given a command determines whether to turn italics on or off,
        or to set the positioning

        This is mostly used to convert from the legacy-style commands

        :type command: str
        or a PAC_TAB_OFFSET_COMMANDS
        :type next_is_punctuation: bool
        :param next_is_punctuation: whether the command right after this one
            decodes to punctuation (comma, period, etc.)
        :type is_paint_on: bool
        :param is_paint_on: whether this command is being interpreted while
            in paint-on mode, where a row+1 jump paired with a large column
            jump indicates an unrelated, independently-positioned region
        """
        self._update_positioning(command, is_paint_on)

        if command == "94a1":
            self.handle_backspace("94a1")

        if command in BACKGROUND_COLOR_CODES:
            self._handle_background_color()

        if command in STYLE_SETTING_COMMANDS:
            self._handle_style_command(command)

        if command in MID_ROW_CODES and command not in PAC_TAB_OFFSET_COMMANDS:
            # The code itself takes the column a preceding PAC pointed at, so
            # no text is about to overwrite what is already on the line. Has to
            # come before the spacing, which may write a space of its own.
            self._position_tracer.cancel_pending_overlap()
            if not self._handle_mid_row_spacing(next_is_punctuation):
                # A mid-row code occupies its column on screen whether or not
                # a space was emitted for it, and the cursor counts columns,
                # not characters — so the column has to be accounted for here
                # or the next PAC on this row looks one column further on than
                # it really is.
                self._position_tracer.advance_cursor(1)

    def _handle_background_color(self):
        """Strip trailing space before a background color code (CEA-608 rule)."""
        if (
            len(self._collection) > 0
            and self._collection[-1].is_text_node()
            and self._collection[-1].text[-1].isspace()
        ):
            self._collection[-1].text = self._collection[-1].text[:-1]

    def _handle_style_command(self, command):
        """Apply italics on/off based on the style-setting command."""
        current_position = self._position_tracer.get_current_position()
        command_style = self.get_style_for_command(command)

        if command_style == "italic":
            self._open_italics(current_position)
        else:
            self._close_italics(current_position)

    def _open_italics(self, position):
        """Open an italics tag if not already open."""
        if self.last_style is not None and self.last_style != "italics off":
            return
        self._emit_pending_breaks(position)
        self._collection.append(_InstructionNode.create_italics_style(position))
        self.last_style = "italics on"

    def _close_italics(self, position):
        """Close an italics tag if currently open."""
        if self.last_style != "italics on":
            return
        # The closing node belongs to the run of text it closes, which is where
        # the previous text node sits. Taking the tracker's current position
        # instead would stamp it with an origin a PAC has already moved on to,
        # leaving one caption carrying nodes at two different positions.
        previous = self.get_previous_text_node()
        self._collection.append(
            _InstructionNode.create_italics_style(
                previous.position if previous else position, turn_on=False
            )
        )
        self.last_style = "italics off"
        self._emit_pending_breaks(position)

    def _emit_pending_breaks(self, position):
        """Emit any pending line breaks from the position tracer."""
        if not self._position_tracer.is_linebreak_required():
            return
        line_start = self._position_tracer.get_line_start_column()
        for _ in range(self._position_tracer._breaks_required):
            self._collection.append(
                _InstructionNode.create_break(position=position, line_start=line_start)
            )
        self._position_tracer.acknowledge_linebreak_consumed()

    def _handle_mid_row_spacing(self, next_is_punctuation):
        """Insert spacing around mid-row code style transitions.

        :rtype: bool
        :return: whether the space was added through :meth:`add_chars`, which
            already advanced the cursor for it.
        """
        if self._position_tracer.is_repositioning_required():
            # A repositioning is already pending with no text written at the
            # current position — that position is about to be abandoned, so
            # padding it with a decorative space would wrongly consume the
            # pending repositioning before the real content arrives.
            return False
        prev_text_node = self.get_previous_text_node()
        if not prev_text_node:
            return False
        prev_node_is_break = any(
            x.is_explicit_break()
            for x in self._collection[self._collection.index(prev_text_node) :]
        )
        if (
            prev_node_is_break
            or prev_text_node.text[-1].isspace()
            or next_is_punctuation
        ):
            return False

        if self.last_style == "italics off":
            self.add_chars(" ")
            return True

        prev_text_node.text = prev_text_node.text + " "
        return False

    def _update_positioning(self, command, is_paint_on=False):
        """Sets the positioning information to use for the next nodes

        :type command: str
        :type is_paint_on: bool
        """
        is_offset = False
        if command in PAC_TAB_OFFSET_COMMANDS:
            prev_positioning = self._position_tracer.default
            tab_offset = PAC_TAB_OFFSET_COMMANDS[command]
            positioning = (prev_positioning[0], prev_positioning[1] + tab_offset)
            is_offset = True
        else:
            first, second = command[:2], command[2:]
            try:
                # is PAC
                positioning = PAC_BYTES_TO_POSITIONING_MAP[first][second]
            except KeyError:
                # if not PAC or OFFSET we're not changing position
                return
        self._position_tracer.update_positioning(
            positioning,
            column_jump_forces_reposition=is_paint_on,
            is_offset=is_offset,
        )
        if is_offset:
            self._settle_line_start()

    def __iter__(self):
        return iter(_format_italics(_resolve_overwrites(self._collection)))

    @staticmethod
    def has_break_before(collection):
        """Check whether the last non-empty node in collection is a break.

        :type collection: list[_InstructionNode]
        :rtype: bool
        """
        if len(collection) == 0:
            return False
        for element in collection[::-1]:
            if element._type == _InstructionNode.TEXT:
                return False
            elif element._type == _InstructionNode.BREAK:
                return True
        return False

    @classmethod
    def from_list(cls, stash_list, position_tracker):
        """Having received a list of instances of this class, creates a new
        instance that contains all the nodes of the previous instances
        (basically concatenates the many stashes into one)

        :type stash_list: list[InstructionNodeCreator]
        :param stash_list: a list of instances of this class

        :type position_tracker: .state_machines.DefaultProvidingPositionTracker
        :param position_tracker: state machine to be interrogated about the
            positioning when creating a node

        :rtype: InstructionNodeCreator
        """
        instance = cls(position_tracker=position_tracker)
        new_collection = instance._collection

        for idx, stash in enumerate(stash_list):
            # Resolved per stash: each is a row of its own, so an overwrite
            # is measured against its row rather than the rows joined together
            new_collection.extend(_resolve_overwrites(stash._collection))

            # use space to separate the stashes, but don't add final space
            if idx < len(stash_list) - 1:
                try:
                    instance._collection[-1].add_chars(" ")
                except AttributeError:
                    pass

        return instance

    def handle_backspace(self, word):
        """
        Move cursor back one position and delete that character
        """
        node = self.get_previous_text_node()
        # in case of no previous text nodes or
        # if the backspace is required while no character
        # do nothing
        if node is None:
            return
        if (
            self.has_break_before(self._collection)
            or self._position_tracer.is_linebreak_required()
            or self._position_tracer.is_repositioning_required()
        ):
            # The character is the first on its row, so there is nothing to its
            # left to erase — reaching back past the break would eat the last
            # character of the line above, or of another caption entirely. The
            # break is only written out once text arrives, so a break still
            # pending in the tracker counts just as much as one already there.
            return
        last_char = node.text[-1]
        delete_previous_condition = (
            word in EXTENDED_CHARS and last_char not in EXTENDED_CHARS.values()
        ) or word == "94a1"
        # in case extended char, perform backspace
        # only if the previous character in not also extended
        if delete_previous_condition:
            node.text = node.text[:-1]
            self._position_tracer.advance_cursor(-1)

    def get_previous_text_node(self):
        """Return the last non-empty text node in the collection, or None.

        :rtype: _InstructionNode | None
        """
        for node in self._collection[::-1]:
            if node.is_text_node() and node.text:
                return node
        return None


def _append_caption_node(caption, instruction, text, position):
    """Convert one instruction into the CaptionNode it stands for

    :type caption: PreCaption
    :type instruction: _InstructionNode
    :param text: the instruction's text, already indented for its line
    :param position: the position to stamp on the node, (row, column)
    """
    layout_info = _get_layout_from_tuple(position)
    if instruction.is_explicit_break():
        caption.nodes.append(CaptionNode.create_break(layout_info=layout_info))

    elif instruction.sets_italics_on():
        caption.nodes.append(
            CaptionNode.create_style(True, {"italics": True}, layout_info=layout_info)
        )

    elif instruction.sets_italics_off():
        caption.nodes.append(
            CaptionNode.create_style(False, {"italics": True}, layout_info=layout_info)
        )

    elif instruction.is_text_node():
        caption.nodes.append(
            CaptionNode.create_text(
                text=text, layout_info=layout_info, position=position
            )
        )
        caption.layout_info = layout_info


def _leftmost_line_starts(instructions):
    """For each cue in a buffer, the leftmost column any of its lines starts at

    A cue's origin is where its first line starts, but pop-on lines are placed
    one by one, and a later line often starts further left (centred or
    right-justified text). Left at the first line's column, the cue box is too
    narrow for those lines and they wrap.

    :type instructions: list[_InstructionNode]
    :rtype: list[int | None]
    """
    columns = [None]
    for instruction in instructions:
        if instruction.requires_repositioning():
            columns.append(None)
            continue
        candidates = [columns[-1]]
        if instruction.is_text_node() and instruction.text and instruction.position:
            candidates.append(instruction.position[1])
        if instruction.is_explicit_break():
            candidates.append(instruction.line_start)
        candidates = [column for column in candidates if column is not None]
        columns[-1] = min(candidates) if candidates else None
    return columns


def _indent_line(text, line_start, position):
    """Indent a line of a cue by the columns it starts right of the cue's origin

    CEA-608 has no justification command: centred and right-justified text is
    placed by where each line's PAC puts it, so a line's offset from the cue's
    leftmost line is the only record of its alignment. Following SMPTE RP
    2052-10, the cue keeps the leftmost line's position and the others are
    indented with whitespace. Non-breaking spaces, since the writers strip or
    collapse ordinary ones at the start of a line. For the same reason the
    spaces the line itself opens with become non-breaking: they are blank
    columns a PAC skipped or the encoder sent, already counted in where the
    line starts, and stripped they would pull the text left of its column.

    :type text: str
    :type line_start: int | None
    :type position: tuple[int] | None
    :rtype: str
    """
    if line_start is None or not position or position[1] is None:
        return text
    stripped = text.lstrip(" ")
    blank_columns = len(text) - len(stripped)
    return "\xa0" * (max(line_start - position[1], 0) + blank_columns) + stripped


class _LineIndenter:
    """Tracks the line of a cue being converted, indenting its first text
    (see ``_indent_line``)

    Holds the column the line starts at and whether its indentation is still to
    be written. The first line of a cue starts at the cue's own position; a
    later one at the column its break recorded.
    """

    def __init__(self, enabled):
        self._enabled = enabled
        self.start_cue()

    def start_cue(self):
        """Begin the first line of a new cue."""
        self._line_start = None
        self._pending = self._enabled

    def text_for(self, instruction, position):
        """Return the instruction's text, indented if it opens the line.

        :type instruction: _InstructionNode
        :type position: tuple[int] | None
        :rtype: str | None
        """
        text = instruction.text
        if instruction.is_explicit_break():
            self._line_start = instruction.line_start
            self._pending = self._enabled and self._line_start is not None
        elif self._pending and instruction.is_text_node() and text:
            self._pending = False
            if self._line_start is None and instruction.position:
                self._line_start = instruction.position[1]
            text = _indent_line(text, self._line_start, position)
        return text


def _get_layout_from_tuple(position_tuple):
    """Create a Layout object from the positioning information given

    The row can have a value from 1 to 15 inclusive. (vertical positioning)
    The column can have a value from 0 to 31 inclusive. (horizontal)

    :param position_tuple: a tuple of ints (row, col)
    :type position_tuple: tuple
    :rtype: Layout
    """
    if not position_tuple:
        return None

    row, column = position_tuple

    # Horizontal safe area between 10% and 90%
    horizontal = Size(80 * column / 32.0 + 10, UnitEnum.PERCENT)
    # Vertical safe area between 5% and 95%
    vertical = Size(90 * (row - 1) / 15.0 + 5, UnitEnum.PERCENT)
    return Layout(
        origin=Point(horizontal, vertical),
        alignment=Alignment(HorizontalAlignmentEnum.LEFT, VerticalAlignmentEnum.TOP),
    )


class _InstructionNode:
    """Value object, that can contain text information, or interpretable
    commands (such as explicit line breaks or turning italics on/off).

    These nodes will be aggregated into a RepresentableNode, which will then
    be easily converted to a CaptionNode.
    """

    TEXT = 0
    BREAK = 1
    ITALICS_ON = 2
    ITALICS_OFF = 3
    CHANGE_POSITION = 4
    OVERWRITE = 5

    def __init__(
        self, text=None, position=None, type_=0, line_start=None, columns=None
    ):
        """
        :type text: str
        :param position: a tuple of ints (row, column)
        :param type_: self.TEXT | self.BREAK | self.ITALICS
        :type type_: int
        :param line_start: for a break, the column the line it opens starts at
        :type line_start: int
        :param columns: for an overwrite, how many columns of text before it
            the text after it may land on
        :type columns: int
        """
        self.text = text
        self.position = position
        self._type = type_
        # The caption's origin is its first line's column, so a break is the
        # only place a later line's own column survives
        self.line_start = line_start
        self.columns = columns

    def add_chars(self, *args):
        """This being a text node, add characters to it.
        :param args:
        :type args: tuple[str]
        :return:
        """
        if self.text is None:
            self.text = ""

        self.text += "".join(args)

    def is_text_node(self):
        """
        :rtype: bool
        """
        return self._type == self.TEXT

    def is_empty(self):
        """
        :rtype: bool
        """
        if self._type == self.TEXT:
            return not self.text

        return False

    def is_explicit_break(self):
        """
        :rtype: bool
        """
        return self._type == self.BREAK

    def sets_italics_on(self):
        """
        :rtype: bool
        """
        return self._type == self.ITALICS_ON

    def sets_italics_off(self):
        """
        :rtype: bool
        """
        return self._type == self.ITALICS_OFF

    def is_italics_node(self):
        """
        :rtype: bool
        """
        return self._type in (self.ITALICS_OFF, self.ITALICS_ON)

    def is_overwrite(self):
        """Whether the node marks text landing on columns already written

        :rtype: bool
        """
        return self._type == self.OVERWRITE

    def requires_repositioning(self):
        """Whether the node must be interpreted as a change in positioning

        :rtype: bool
        """
        return self._type == self.CHANGE_POSITION

    def get_text(self):
        """A little legacy code."""
        return " ".join(self.text.split())

    @classmethod
    def create_break(cls, position, line_start=None):
        """Create a node, interpretable as an explicit line break

        :type position: tuple[int]
        :param position: a tuple (row, col) containing the positioning info

        :type line_start: int
        :param line_start: the column the line this break opens starts at

        :rtype: _InstructionNode
        """
        return cls(type_=cls.BREAK, position=position, line_start=line_start)

    @classmethod
    def create_text(cls, position, *chars):
        """Create a node interpretable as text

        :type position: tuple[int]
        :param position: a tuple (row, col) to mark the positioning

        :type chars: tuple[str]
        :param chars: characters to add to the text

        :rtype: _InstructionNode
        """
        return cls("".join(chars), position=position)

    @classmethod
    def create_italics_style(cls, position, turn_on=True):
        """Create a node, interpretable as a command to switch italics on/off

        :type position: tuple[int]
        :param position: a tuple (row, col) to mark the positioning

        :type turn_on: bool
        :param turn_on: whether to turn the italics on or off

        :rtype: _InstructionNode
        """
        return cls(
            position=position, type_=cls.ITALICS_ON if turn_on else cls.ITALICS_OFF
        )

    @classmethod
    def create_repositioning_command(cls, position=None):
        """Create node interpretable as a command to change the current
        position

        :type position:
        """
        return cls(type_=cls.CHANGE_POSITION, position=position)

    @classmethod
    def create_overwrite(cls, position, columns):
        """Create a node marking that the text after it may land on the last
        ``columns`` columns of text before it

        :type position: tuple[int]
        :type columns: int
        :rtype: _InstructionNode
        """
        return cls(type_=cls.OVERWRITE, position=position, columns=columns)

    def __repr__(self):  # pragma: no cover
        if self._type == self.BREAK:
            extra = "BR"
        elif self._type == self.OVERWRITE:
            extra = f"overwrite {self.columns}"
        elif self._type == self.TEXT:
            extra = f'"{self.text}"'
        elif self._type in (self.ITALICS_ON, self.ITALICS_OFF):
            extra = "italics {}".format(
                "on" if self._type == self.ITALICS_ON else "off"
            )
        else:
            extra = "change position"

        return f"<INode: {extra} >"


def _ends_line(node):
    """Whether the node ends the line the nodes before it are on

    :type node: _InstructionNode
    :rtype: bool
    """
    return node.is_explicit_break() or node.requires_repositioning()


def _line_length(collection):
    """How many columns of text the line the collection ends on holds

    :type collection: list[_InstructionNode]
    :rtype: int
    """
    length = 0
    for node in reversed(collection):
        if _ends_line(node):
            break
        if node.is_text_node() and node.text:
            length += len(node.text)
    return length


def _resolve_overwrites(collection):
    """Settle each overwrite marker in the collection, returning a new list
    without them

    A PAC pointing back over text already on the row is ambiguous. On screen
    the text that follows replaces what is under it, but encoders also restate
    the position mid-row with the rest of the row still to come, and taking
    that literally erases words the caption meant to keep. So the overwrite is
    only taken where appending is provably wrong and dropping is exact: the
    appended row would run past column 32, and the text arriving covers every
    column it points back over, as when a row is sent again in full. Otherwise
    the text is appended, and a row too long for the screen is left for the
    line length check to reject rather than truncated into one that passes.

    The collection is not modified: a roll-up row is read again in each of the
    captions it rolls through, so its markers have to survive being settled.

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    if not any(node.is_overwrite() for node in collection):
        return collection
    resolved = []
    line = []
    line_start = None
    for node in collection:
        if _ends_line(node):
            resolved.extend(_resolve_line_overwrites(line, line_start))
            resolved.append(node)
            line = []
            line_start = node.line_start if node.is_explicit_break() else None
        else:
            line.append(node)
    resolved.extend(_resolve_line_overwrites(line, line_start))
    return resolved


def _resolve_line_overwrites(line, line_start):
    """Settle the overwrite markers of one line (see ``_resolve_overwrites``)

    :type line: list[_InstructionNode]
    :param line_start: the column the line starts at, if its break recorded it
    :type line_start: int | None
    :rtype: list[_InstructionNode]
    """
    if not any(node.is_overwrite() for node in line):
        return line
    line = [copy.copy(node) if node.is_text_node() else node for node in line]
    if line_start is None:
        line_start = next(
            (
                node.position[1]
                for node in line
                if node.is_text_node() and node.text and node.position
            ),
            0,
        )
    for index, marker in enumerate(line):
        if not marker.is_overwrite():
            continue
        arriving = 0
        for node in line[index + 1 :]:
            if node.is_overwrite():
                break
            if node.is_text_node() and node.text:
                arriving += len(node.text)
        if line_start + _line_length(line) > 32 and arriving >= marker.columns:
            _drop_last_columns(line[:index], marker.columns)
    return _join_across_markers(line)


def _join_across_markers(line):
    """Drop the overwrite markers, joining the text nodes each one split

    The marker opened a text node of its own for the text that followed it,
    but once settled that text just continues the line, and writers that
    separate text nodes with a space would break the word it lands in.

    :type line: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    joined = []
    after_marker = False
    for node in line:
        if node.is_overwrite():
            after_marker = True
            continue
        if (
            after_marker
            and node.is_text_node()
            and joined
            and joined[-1].is_text_node()
        ):
            if node.text:
                joined[-1].add_chars(node.text)
        else:
            joined.append(node)
        after_marker = False
    return joined


def _drop_last_columns(line, columns):
    """Drop the last ``columns`` columns of text from the nodes of a line

    :type line: list[_InstructionNode]
    :type columns: int
    """
    for node in reversed(line):
        if not columns:
            return
        if not node.is_text_node() or not node.text:
            continue
        dropped = min(columns, len(node.text))
        node.text = node.text[: len(node.text) - dropped]
        columns -= dropped


def _format_italics(collection):
    """Given a raw list of _InstructionNodes, returns a new equivalent list
    where all the italics nodes properly close and open.

    The list is equivalent in the sense that the SCC commands that would have
    generated the output list, would have had the exact same visual effect
    as the ones that generated the output, as far as italics are concerned.

    This is useful because the raw commands read from the SCC can't be used
    the way they are by the writers for the other formats. Those other writers
    require the list of CaptionNodes to be formatted in a certain way.

    Note: Using state machines to manage the italics didn't work well because
    we're using state machines already to track the position, and their
    interactions got crazy.

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = _skip_empty_text_nodes(collection)

    # after this step we're guaranteed a proper ordering of the nodes
    # (also removes initial italics-off nodes that precede any italics-on)
    new_collection = _skip_redundant_italics_nodes(new_collection)

    # after this, we're guaranteed that the italics are properly contained
    # within their context
    new_collection = _close_italics_before_repositioning(new_collection)

    # all nodes will be closed after this step
    new_collection = _ensure_final_italics_node_closes(new_collection)

    # removes pairs of italics nodes that don't do anything noticeable
    new_collection = _remove_noop_italics(new_collection)

    # remove spaces to the end of the lines
    new_collection = _remove_spaces_at_end_of_the_line(new_collection)

    return new_collection


def _remove_spaces_at_end_of_the_line(collection):
    """Strip trailing whitespace from text nodes that precede line breaks.

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    if not collection:
        return collection
    for idx, node in enumerate(collection):
        if (
            idx > 0
            and node._type == _InstructionNode.BREAK
            and collection[idx - 1].is_text_node()
            and collection[idx - 1].text
        ):
            collection[idx - 1].text = collection[idx - 1].text.rstrip()
    # handle last node
    if collection[-1].is_text_node():
        collection[-1].text = collection[-1].text.rstrip()
    return collection


def _remove_noop_italic_pairs(collection, opening_is_on):
    """Remove adjacent italics on/off (or off/on) pairs with nothing between them.

    :param collection: list of _InstructionNode
    :param opening_is_on: if True, removes on→off pairs; if False, removes off→on pairs
    :rtype: list[_InstructionNode]
    """
    new_collection = []
    pending = None

    for node in collection:
        if not node.is_italics_node():
            if pending:
                new_collection.append(pending)
                pending = None
            new_collection.append(node)
            continue

        is_opener = node.sets_italics_on() if opening_is_on else node.sets_italics_off()
        if is_opener:
            pending = node
        elif pending:
            pending = None
        else:
            new_collection.append(node)

    if pending:
        new_collection.append(pending)

    return new_collection


def _remove_noop_italics(collection):
    """Return an equivalent list to `collection`. It removes the italics node
     pairs that don't surround text nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = _remove_noop_italic_pairs(collection, opening_is_on=True)
    new_collection = _remove_noop_italic_pairs(new_collection, opening_is_on=False)
    return new_collection


def _skip_empty_text_nodes(collection):
    """Return an iterable containing all the nodes in the previous
    collection except for the empty text nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    return [
        node for node in collection if not (node.is_text_node() and node.is_empty())
    ]


def _skip_redundant_italics_nodes(collection):
    """Return a list where the <Italics On> nodes only appear after
    <Italics OFF>, and vice versa. This ignores the other node types, and
    only removes redundant italic nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = []
    state = None

    for node in collection:
        if node.is_italics_node():
            if state is None:
                state = node.sets_italics_on()
                if node.sets_italics_on():
                    new_collection.append(node)
                continue
            # skip the nodes that are like the previous
            if node.sets_italics_on() is state:
                continue
            else:
                state = node.sets_italics_on()
        new_collection.append(node)

    return new_collection


def _track_italics_state(collection):
    """Track italics on/off state through a collection of nodes.

    :rtype: tuple[bool, _InstructionNode | None]
    :returns: (italics_on, last_italics_on_node)
    """
    italics_on = False
    last_italics_on_node = None
    for node in collection:
        if node.is_italics_node() and node.sets_italics_on():
            italics_on = True
            last_italics_on_node = node
        elif node.is_italics_node() and node.sets_italics_off():
            italics_on = False
    return italics_on, last_italics_on_node


def _close_italics_before_repositioning(collection):
    """Make sure that for every opened italic node, there's a corresponding
    closing node.

    Will insert a closing italic node, before each repositioning node

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = []
    italics_on = False
    last_italics_on_node = None

    for node in collection:
        if node.is_italics_node() and node.sets_italics_on():
            italics_on = True
            last_italics_on_node = node
        elif node.is_italics_node() and node.sets_italics_off():
            italics_on = False

        if node.requires_repositioning() and italics_on:
            new_collection.append(
                _InstructionNode.create_italics_style(
                    position=last_italics_on_node.position,
                    turn_on=False,
                )
            )
            new_collection.append(node)
            new_collection.append(
                _InstructionNode.create_italics_style(position=node.position)
            )
            continue

        new_collection.append(node)

    return new_collection


def _ensure_final_italics_node_closes(collection):
    """The final italics command needs to be closed

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    italics_on, last_italics_on_node = _track_italics_state(collection)

    if not italics_on:
        return list(collection)

    new_collection = list(collection)
    new_collection.append(
        _InstructionNode.create_italics_style(
            position=last_italics_on_node.position, turn_on=False
        )
    )
    return new_collection
