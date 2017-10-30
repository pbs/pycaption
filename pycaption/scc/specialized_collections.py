from ..base import CaptionList, Caption, CaptionNode
from ..geometry import (UnitEnum, Size, Layout, Point, Alignment,
                        VerticalAlignmentEnum, HorizontalAlignmentEnum)

from .constants import PAC_BYTES_TO_POSITIONING_MAP, COMMANDS


class PreCaption(object):
    """
    The Caption class has been refactored and now its instances must be used as
    immutable objects. Some of the code in this module, however, relied on the
    fact that Caption instances were mutable. For backwards compatibility,
    therefore, this class was created to work as a mutable caption data holder
    used to eventually instantiate an actual Caption object.
    """

    def __init__(self, start=0, end=0):
        self.start = start
        self.end = end
        self.nodes = []
        self.style = {}
        self.layout_info = None

    def to_real_caption(self):
        return Caption(
            self.start, self.end, self.nodes, self.style, self.layout_info
        )


class TimingCorrectingCaptionList(list):
    """List of captions. When appending new elements, it will correct the end time
    of the last ones, so they end when the new caption gets added.

    "last ones" could mean the last caption `append`ed or all of the last
    captions with which this list was `extended`

    Also, doesn't allow Nones or empty captions
    """
    def __init__(self, *args, **kwargs):
        super(TimingCorrectingCaptionList, self).__init__(*args, **kwargs)
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

        super(TimingCorrectingCaptionList, self).append(p_object)

    def extend(self, iterable):
        """Adds the elements in the iterable to the list, regarding the first
        caption's start time as the end time for the previously added
        caption(s)

        :param iterable: an iterable of Caption instances
        """
        appendable_items = [item for item in iterable if item and item.nodes]
        self._update_last_batch(self._last_batch, *appendable_items)

        self._last_batch = tuple(appendable_items)

        super(TimingCorrectingCaptionList, self).extend(appendable_items)

    @staticmethod
    def _update_last_batch(batch, *new_captions):
        """Given a batch of captions, sets their end time equal to the start
        time of the first caption in *new_captions

        The start time of the first caption in new_captions should never be 0.
        This means an invalid SCC file.

        :type batch: tuple[Caption]
        :type new_captions: tuple[Caption]
        """
        if not new_captions:
            return
        if not new_captions[0]:
            return
        if not new_captions[0].nodes:
            return

        new_caption = new_captions[0]

        if batch and batch[-1].end == 0:
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
        super(NotifyingDict, self).__init__(*args, **kwargs)
        self.active_key = self._guard
        self.observers = []

    def set_active(self, key):
        """Sets the active key

        :param key: any hashable object
        """
        if key not in self:
            raise ValueError(u'No such key present')

        # Notify observers of the change
        if key != self.active_key:
            for observer in self.observers:
                observer(self.active_key, key)

        self.active_key = key

    def get_active(self):
        """Returns the value corresponding to the active key
        """
        if self.active_key is self._guard:
            raise KeyError(u'No active key set')

        return self[self.active_key]

    def add_change_observer(self, observer):
        """Receives a callable function, which it will call if the active
        element changes.

        The observer will receive 2 positional arguments: the old and new key

        :param observer: any callable that can be called with 2 positional
            arguments
        """
        if not callable(observer):
            raise TypeError(u'The observer should be callable')

        self.observers.append(observer)


class CaptionCreator(object):
    """Creates and maintains a collection of Captions
    """
    def __init__(self, ignore_layout=False):
        self.ignore_layout = ignore_layout

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

    def create_and_store(self, node_buffer, start):
        """Interpreter method, will convert the buffer into one or more Caption
        objects, storing them internally.

        This method relies on the InstructionNodeCreator's ability to generate
        InstructionNodes properly, so at this point we can convert
        _InstructionNodes nodes almost 1:1 to CaptionNodes

        :type node_buffer: InstructionNodeCreator

        :type start: float
        :param start: the start time in microseconds
        """
        if node_buffer.is_empty():
            return

        caption = PreCaption()
        caption.start = start
        caption.end = 0  # Not yet known; filled in later
        self._still_editing = [caption]

        for instruction in node_buffer:
            layout_info = _get_layout_from_tuple(instruction.position) if not self.ignore_layout else None

            # skip empty elements
            if instruction.is_empty():
                continue

            elif instruction.requires_repositioning():
                caption = PreCaption()
                caption.start = start
                caption.end = 0
                self._still_editing.append(caption)

            # handle line breaks
            elif instruction.is_explicit_break():
                caption.nodes.append(CaptionNode.create_break(
                    layout_info=layout_info
                ))

            # handle open italics
            elif instruction.sets_italics_on():
                caption.nodes.append(
                    CaptionNode.create_style(
                        True, {u'italics': True},
                        layout_info=layout_info)
                )

            # handle clone italics
            elif instruction.sets_italics_off():
                caption.nodes.append(
                    CaptionNode.create_style(
                        False, {u'italics': True},
                        layout_info=layout_info)
                    )

            # handle text
            elif instruction.is_text_node():
                caption.nodes.append(
                    CaptionNode.create_text(
                        instruction.get_text(), layout_info=layout_info),
                )
                caption.layout_info = layout_info

        self._collection.extend(self._still_editing)

    def get_all(self):
        """Returns the Caption collection as a CaptionList

        :rtype: CaptionList
        """
        caption_list = CaptionList()
        for precap in self._collection:
            caption_list.append(precap.to_real_caption())
        return caption_list


class InstructionNodeCreator(object):
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

        self._position_tracer = position_tracker

    def is_empty(self):
        """Whether any text was added to the buffer
        """
        return not any(element.text for element in self._collection)

    def add_chars(self, *chars):
        """Adds characters to a text node (last text node, or a new one)

        :param chars: tuple containing text (unicode)
        """
        if not chars:
            return

        current_position = self._position_tracer.get_current_position()

        # get or create a usable node
        if (self._collection and self._collection[-1].is_text_node()
                and not self._position_tracer.is_repositioning_required()):
            node = self._collection[-1]
        else:
            # create first node
            node = _InstructionNode(position=current_position)
            self._collection.append(node)

        # handle a simple line break
        if self._position_tracer.is_linebreak_required():
            # must insert a line break here
            self._collection.append(_InstructionNode.create_break(
                position=current_position))
            node = _InstructionNode.create_text(current_position)
            self._collection.append(node)
            self._position_tracer.acknowledge_linebreak_consumed()

        # handle completely new positioning
        elif self._position_tracer.is_repositioning_required():
            self._collection.append(
                _InstructionNode.create_repositioning_command(
                    current_position
                )
            )
            node = _InstructionNode.create_text(current_position)
            self._collection.append(node)
            self._position_tracer.acknowledge_position_changed()

        node.add_chars(*chars)

    def interpret_command(self, command):
        """Given a command determines whether tu turn italics on or off,
        or to set the positioning

        This is mostly used to convert from the legacy-style commands

        :type command: unicode
        """
        self._update_positioning(command)

        text = COMMANDS.get(command, u'')

        if u'italic' in text:
            if u'end' not in text:
                self._collection.append(
                    _InstructionNode.create_italics_style(
                        self._position_tracer.get_current_position())
                )
            else:
                self._collection.append(
                    _InstructionNode.create_italics_style(
                        self._position_tracer.get_current_position(),
                        turn_on=False
                    )
                )

    def _update_positioning(self, command):
        """Sets the positioning information to use for the next nodes

        :type command: unicode
        """
        if len(command) != 4:
            return

        first, second = command[:2], command[2:]

        try:
            positioning = PAC_BYTES_TO_POSITIONING_MAP[first][second]
        except KeyError:
            pass
        else:
            self._position_tracer.update_positioning(positioning)

    def __iter__(self):
        return iter(_format_italics(self._collection))

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
            new_collection.extend(stash._collection)

            # use space to separate the stashes, but don't add final space
            if idx < len(stash_list) - 1:
                try:
                    instance._collection[-1].add_chars(u' ')
                except AttributeError:
                    pass

        return instance


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

    horizontal = Size(100 * column / 32.0, UnitEnum.PERCENT)
    vertical = Size(100 * (row - 1) / 15.0, UnitEnum.PERCENT)
    return Layout(origin=Point(horizontal, vertical),
                  alignment=Alignment(HorizontalAlignmentEnum.CENTER,
                                      VerticalAlignmentEnum.TOP)
                  )


class _InstructionNode(object):
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

    def __init__(self, text=None, position=None, type_=0):
        """
        :type text: unicode
        :param position: a tuple of ints (row, column)
        :param type_: self.TEXT | self.BREAK | self.ITALICS
        :type type_: int
        """
        self.text = text
        self.position = position
        self._type = type_

    def add_chars(self, *args):
        """This being a text node, add characters to it.
        :param args:
        :type args: tuple[unicode]
        :return:
        """
        if self.text is None:
            self.text = u''

        self.text += u''.join(args)

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

    def requires_repositioning(self):
        """Whether the node must be interpreted as a change in positioning

        :rtype: bool
        """
        return self._type == self.CHANGE_POSITION

    def get_text(self):
        """A little legacy code.
        """
        return u' '.join(self.text.split())

    @classmethod
    def create_break(cls, position):
        """Create a node, interpretable as an explicit line break

        :type position: tuple[int]
        :param position: a tuple (row, col) containing the positioning info

        :rtype: _InstructionNode
        """
        return cls(type_=cls.BREAK, position=position)

    @classmethod
    def create_text(cls, position, *chars):
        """Create a node interpretable as text

        :type position: tuple[int]
        :param position: a tuple (row, col) to mark the positioning

        :type chars: tuple[unicode]
        :param chars: characters to add to the text

        :rtype: _InstructionNode
        """
        return cls(u''.join(chars), position=position)

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
            position=position,
            type_=cls.ITALICS_ON if turn_on else cls.ITALICS_OFF
        )

    @classmethod
    def create_repositioning_command(cls, position=None):
        """Create node interpretable as a command to change the current
        position

        :type position:
        """
        return cls(type_=cls.CHANGE_POSITION, position=position)

    def __repr__(self):         # pragma: no cover
        if self._type == self.BREAK:
            extra = u'BR'
        elif self._type == self.TEXT:
            extra = u'"{}"'.format(self.text)
        elif self._type in (self.ITALICS_ON, self.ITALICS_OFF):
            extra = u'italics {}'.format(
                u'on' if self._type == self.ITALICS_ON else u'off'
            )
        else:
            extra = u'change position'

        return u'<INode: {extra} >'.format(extra=extra)


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
    new_collection = _skip_initial_italics_off_nodes(collection)

    new_collection = _skip_empty_text_nodes(new_collection)

    # after this step we're guaranteed a proper ordering of the nodes
    new_collection = _skip_redundant_italics_nodes(new_collection)

    # after this, we're guaranteed that the italics are properly contained
    # within their context
    new_collection = _close_italics_before_repositioning(new_collection)

    # all nodes will be closed after this step
    new_collection = _ensure_final_italics_node_closes(new_collection)

    # removes pairs of italics nodes that don't do anything noticeable
    new_collection = _remove_noop_italics(new_collection)

    return new_collection


def _remove_noop_on_off_italics(collection):
    """Return an equivalent list to `collection`. It removes the italics node
     pairs that don't surround text nodes, if those nodes are in the order:
     on, off

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = []
    to_commit = None

    for node in collection:
        if node.is_italics_node() and node.sets_italics_on():
            to_commit = node
            continue

        elif node.is_italics_node() and node.sets_italics_off():
            if to_commit:
                to_commit = None
                continue
        else:
            if to_commit:
                new_collection.append(to_commit)
                to_commit = None

        new_collection.append(node)

    return new_collection


def _remove_noon_off_on_italics(collection):
    """Removes pairs of off-on italics nodes, that don't surround any other
    node

    :type collection: list[_InstructionNode]
    :return: list[_InstructionNode]
    """
    new_collection = []
    to_commit = None

    for node in collection:
        if node.is_italics_node() and node.sets_italics_off():
            to_commit = node
            continue

        elif node.is_italics_node() and node.sets_italics_on():
            if to_commit:
                to_commit = None
                continue
        else:
            if to_commit:
                new_collection.append(to_commit)
                to_commit = None

        new_collection.append(node)

    if to_commit:
        new_collection.append(to_commit)

    return new_collection


def _remove_noop_italics(collection):
    """Return an equivalent list to `collection`. It removes the italics node
     pairs that don't surround text nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = _remove_noop_on_off_italics(collection)

    new_collection = _remove_noon_off_on_italics(new_collection)

    return new_collection


def _skip_initial_italics_off_nodes(collection):
    """Return a collection like the one given, but without the
    initial <Italics OFF> nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = []
    can_add_italics_off_nodes = False

    for node in collection:
        if node.is_italics_node():
            if node.sets_italics_on():
                can_add_italics_off_nodes = True
                new_collection.append(node)
            elif can_add_italics_off_nodes:
                new_collection.append(node)
        else:
            new_collection.append(node)

    return new_collection


def _skip_empty_text_nodes(collection):
    """Return an iterable containing all the nodes in the previous
    collection except for the empty text nodes

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    return [node for node in collection
            if not (node.is_text_node() and node.is_empty())]


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
                new_collection.append(node)
                continue
            # skip the nodes that are like the previous
            if node.sets_italics_on() is state:
                continue
            else:
                state = node.sets_italics_on()
        new_collection.append(node)

    return new_collection


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

    for idx, node in enumerate(collection):
        if node.is_italics_node() and node.sets_italics_on():
            italics_on = True
            last_italics_on_node = node
        if node.is_italics_node() and node.sets_italics_off():
            italics_on = False
        if node.requires_repositioning() and italics_on:
            # Append an italics closing node before the position change
            new_collection.append(
                _InstructionNode.create_italics_style(
                    # The position info of this new node should be the same
                    position=last_italics_on_node.position,
                    turn_on=False
                )
            )
            new_collection.append(node)
            # Append an italics opening node after the positioning change
            new_collection.append(
                _InstructionNode.create_italics_style(
                    position=node.position
                )
            )
            continue
        new_collection.append(node)

    return new_collection


def _ensure_final_italics_node_closes(collection):
    """The final italics command needs to be closed

    :type collection: list[_InstructionNode]
    :rtype: list[_InstructionNode]
    """
    new_collection = list(collection)

    italics_on = False
    last_italics_on_node = None

    for node in collection:
        if node.is_italics_node() and node.sets_italics_on():
            italics_on = True
            last_italics_on_node = node
        if node.is_italics_node() and node.sets_italics_off():
            italics_on = False

    if italics_on:
        new_collection.append(
            _InstructionNode.create_italics_style(
                position=last_italics_on_node.position,
                turn_on=False
            )
        )
    return new_collection
