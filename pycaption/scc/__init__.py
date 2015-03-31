#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import math
import string
import textwrap

from pycaption.base import (
    BaseReader, BaseWriter, Caption, CaptionSet, CaptionNode,
)
from pycaption.geometry import Layout, Point, Size, UnitEnum
from pycaption.exceptions import CaptionReadNoCaptions, CaptionReadSyntaxError
from .constants import (
    HEADER, COMMANDS, SPECIAL_CHARS, EXTENDED_CHARS, CHARACTERS,
    MICROSECONDS_PER_CODEWORD, CHARACTER_TO_CODE,
    SPECIAL_OR_EXTENDED_CHAR_TO_CODE, PAC_BYTES_TO_POSITIONING_MAP,
    PAC_HIGH_BYTE_BY_ROW, PAC_LOW_BYTE_BY_ROW_RESTRICTED,
)


class SCCReader(BaseReader):
    def __init__(self, *args, **kw):
        self.caption_stash = _CaptionStash()
        self.time_translator = _SccTimeTranslator()

        self.last_command = u''

        self.pop_buffer = _InterpretableNodeStash()
        self.pop_on = False
        self.pop_time = 0

        self.paint_buffer = _InterpretableNodeStash()
        self.paint_on = False
        self.paint_time = 0

        self.roll_buffer = _InterpretableNodeStash()
        self.roll_rows = []
        self.roll_rows_expected = 0
        self.roll_on = False
        self.roll_time = 0
        self.simulate_roll_up = False

    def detect(self, content):
        lines = content.splitlines()
        if lines[0] == HEADER:
            return True
        else:
            return False

    def read(self, content, lang=u'en-US', simulate_roll_up=False, offset=0):
        if type(content) != unicode:
            raise RuntimeError(u'The content is not a unicode string.')

        self.simulate_roll_up = simulate_roll_up
        self.time_translator.set_offset(offset * 1000000)
        # split lines
        lines = content.splitlines()

        # loop through each line except the first
        for line in lines[1:]:
            self._translate_line(line)

        # Pop-Up captions are displayed explicitly (command 942f [EOC].
        # Also Roll-up's are explicitly rolled up (with 94ad [CR])
        # We should however check the paint_buffer for any remaining content
        # and turn that into a caption, or we'll lose the last line of the
        # Paint-on captions.
        # ALSO: because the paint and roll buffer were previously mixed, the
        # library was treating incorrectly the Roll-up's. We shouldn't convert
        # the characters in the buffer to a caption, but I'd still do that
        # seeing as though it's legacy behavior.
        if not self.roll_buffer.is_empty():
            self._roll_up()

        # after converting lines, see if anything is left in paint_buffer
        if not self.paint_buffer.is_empty():
            self.caption_stash.create_and_store(
                self.paint_buffer, self.paint_time)

        captions = CaptionSet()
        captions.set_captions(lang, self.caption_stash.get_all())

        if captions.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return captions

    def _translate_line(self, line):
        # ignore blank lines
        if line.strip() == u'':
            return

        # split line in timestamp and words
        r = re.compile(r"([0-9:;]*)([\s\t]*)((.)*)")
        parts = r.findall(line.lower())

        self.time_translator.start_at(parts[0][0])

        # loop through each word
        for word in parts[0][2].split(u' '):
            # ignore empty results
            if word.strip() != u'':
                self._translate_word(word)

    def _translate_word(self, word):
        # count frames for timing
        self.time_translator.increment_frames()

        # first check if word is a command
        # TODO - check that all the positioning commands are here, or use
        # some other strategy to determine if the word is a command.
        if word in COMMANDS:
            self._translate_command(word)

        # second, check if word is a special character
        elif word in SPECIAL_CHARS:
            self._translate_special_char(word)

        elif word in EXTENDED_CHARS:
            self._translate_extended_char(word)

        # third, try to convert word into 2 characters
        else:
            self._translate_characters(word)

    def _handle_double_command(self, word):
        # ensure we don't accidentally use the same command twice
        if word == self.last_command:
            self.last_command = u''
            return True
        else:
            self.last_command = word
            return False

    def _translate_special_char(self, word):
        # XXX - this looks highly buggy. Why should special chars be ignored
        # when printed 2 times one after another?
        if self._handle_double_command(word):
            return

        # add to buffer
        if self.paint_on:
            self.paint_buffer.add_chars(SPECIAL_CHARS[word])
        elif self.pop_on:
            self.pop_buffer.add_chars(SPECIAL_CHARS[word])
        elif self.roll_on:
            self.roll_buffer.add_chars(SPECIAL_CHARS[word])

    def _translate_extended_char(self, word):
        # XXX - this looks highly buggy. Why would a special char be ignored
        # if it's printed 2 times one after another?
        if self._handle_double_command(word):
            return

        # add to buffer
        if self.paint_on:
            if not self.paint_buffer.is_empty():
                self.paint_buffer.discard_last_char()
            self.paint_buffer.add_chars(EXTENDED_CHARS[word])
        elif self.pop_on:
            if not self.pop_buffer.is_empty():
                self.pop_buffer.discard_last_char()
            self.pop_buffer.add_chars(EXTENDED_CHARS[word])
        elif self.roll_on:
            if not self.roll_buffer.is_empty():
                self.roll_buffer.discard_last_char()
            self.roll_buffer.add_chars(EXTENDED_CHARS[word])

    def _translate_command(self, word):
        if self._handle_double_command(word):
            return

        # if command is pop_up
        if word == u'9420':
            self.pop_on = True
            self.paint_on = self.roll_on = False

        # command is paint_on [Resume Direct Captioning]
        elif word == u'9429':
            self.paint_on = True
            self.pop_on = self.roll_on = False

            self.roll_rows_expected = 1
            if not self.paint_buffer.is_empty():
                self.caption_stash.create_and_store(
                    self.paint_buffer, self.paint_time
                )
                self.paint_buffer = _InterpretableNodeStash()

            self.paint_time = self.time_translator.get_time()

        # if command is roll_up 2, 3 or 4 rows
        elif word in (u'9425', u'9426', u'94a7'):
            self.roll_on = True
            self.paint_on = self.pop_on = False

            # count how many lines are expected
            if word == u'9425':
                self.roll_rows_expected = 2
            elif word == u'9426':
                self.roll_rows_expected = 3
            elif word == u'94a7':
                self.roll_rows_expected = 4

            # if content is in the queue, turn it into a caption
            if not self.roll_buffer.is_empty():
                # convert and empty buffer
                self.caption_stash.create_and_store(
                    self.roll_buffer, self.roll_time)
                self.roll_buffer = _InterpretableNodeStash()

            # set rows to empty, configure start time for caption
            self.roll_rows = []
            self.roll_time = self.time_translator.get_time()

        # clear pop_on buffer
        elif word == u'94ae':
            self.pop_buffer = _InterpretableNodeStash()

        # display pop_on buffer [End Of Caption]
        elif word == u'942f':
            self.pop_time = self.time_translator.get_time()
            self.caption_stash.create_and_store(self.pop_buffer, self.pop_time)
            self.pop_buffer = _InterpretableNodeStash()

        # roll up captions [Carriage Return]
        elif word == u'94ad':
            # display roll-up buffer
            if not self.roll_buffer.is_empty():
                self._roll_up()

        # clear screen
        elif word == u'942c':
            self.roll_rows = []

            if not self.paint_buffer.is_empty():
                self.caption_stash.create_and_store(
                    self.paint_buffer, self.paint_time)
                self.paint_buffer = _InterpretableNodeStash()

            # attempt to add proper end time to last caption(s)
            self.caption_stash.correct_last_timing(
                self.time_translator.get_time())

        # if command not one of the aforementioned, add to buffer
        else:
            # determine whether the word is a PAC, save it for later
            if self.paint_on:
                self.paint_buffer.interpret_command(word)
            elif self.pop_on:
                self.pop_buffer.interpret_command(word)
            elif self.roll_on:
                self.roll_buffer.interpret_command(word)

    def _translate_characters(self, word):
        # split word into the 2 bytes
        byte1 = word[:2]
        byte2 = word[2:]

        # check to see if the the bytes are recognized characters
        if byte1 not in CHARACTERS or byte2 not in CHARACTERS:
            return

        # xxx - Polymorphism means avoiding conditional chains like this
        # if so, add to buffer
        if self.paint_on:
            self.paint_buffer.add_chars(CHARACTERS[byte1], CHARACTERS[byte2])
        elif self.pop_on:
            self.pop_buffer.add_chars(CHARACTERS[byte1], CHARACTERS[byte2])
        elif self.roll_on:
            self.roll_buffer.add_chars(CHARACTERS[byte1], CHARACTERS[byte2])

    def _roll_up(self):
        if self.simulate_roll_up:
            if self.roll_rows_expected > 1:
                if len(self.roll_rows) >= self.roll_rows_expected:
                    self.roll_rows.pop(0)

                self.roll_rows.append(self.roll_buffer)
                self.roll_buffer = _InterpretableNodeStash.from_list(
                    self.roll_rows)

        # convert buffer and empty
        self.caption_stash.create_and_store(
            self.roll_buffer, self.roll_time)
        self.roll_buffer = _InterpretableNodeStash()

        # configure time
        self.roll_time = self.time_translator.get_time()

        # try to insert the proper ending time for the previous caption
        self.caption_stash.correct_last_timing(self.roll_time, force=True)


class SCCWriter(BaseWriter):

    def __init__(self, *args, **kw):
        pass

    def write(self, caption_set):
        output = HEADER + u'\n\n'

        if caption_set.is_empty():
            return output

        # Only support one language.
        lang = caption_set.get_languages()[0]
        captions = caption_set.get_captions(lang)

        # PASS 1: compute codes for each caption
        codes = [(self._text_to_code(caption), caption.start, caption.end)
                 for caption in captions]

        # PASS 2:
        # Advance start times so as to have time to write to the pop-on
        # buffer; possibly remove the previous clear-screen command
        for index, (code, start, end) in enumerate(codes):
            code_words = len(code) / 5 + 8
            code_time_microseconds = code_words * MICROSECONDS_PER_CODEWORD
            code_start = start - code_time_microseconds
            if index == 0:
                continue
            previous_code, previous_start, previous_end = codes[index-1]
            if previous_end + 3 * MICROSECONDS_PER_CODEWORD >= code_start:
                codes[index-1] = (previous_code, previous_start, None)
            codes[index] = (code, code_start, end)

        # PASS 3:
        # Write captions.
        for (code, start, end) in codes:
            output += (u'%s\t' % self._format_timestamp(start))
            output += u'94ae 94ae 9420 9420 '
            output += code
            output += u'942c 942c 942f 942f\n\n'
            if end is not None:
                output += u'%s\t942c 942c\n\n' % self._format_timestamp(end)

        return output

    # Wrap lines at 32 chars
    def _layout_line(self, caption):
        def caption_node_to_text(caption_node):
            if caption_node.type_ == CaptionNode.TEXT:
                return unicode(caption_node.content)
            elif caption_node.type_ == CaptionNode.BREAK:
                return u'\n'
        caption_text = u''.join([caption_node_to_text(node)
                                for node in caption.nodes])
        inner_lines = string.split(caption_text, u'\n')
        inner_lines_laid_out = [textwrap.fill(x, 32) for x in inner_lines]
        return u'\n'.join(inner_lines_laid_out)

    def _maybe_align(self, code):
        # Finish a half-word with a no-op so we can move to a full word
        if len(code) % 5 == 2:
            code += u'80 '
        return code

    def _maybe_space(self, code):
        if len(code) % 5 == 4:
            code += u' '
        return code

    def _print_character(self, code, char):
        try:
            char_code = CHARACTER_TO_CODE[char]
        except KeyError:
            try:
                char_code = SPECIAL_OR_EXTENDED_CHAR_TO_CODE[char]
            except KeyError:
                char_code = u'91b6'  # Use £ as "unknown character" symbol

        if len(char_code) == 2:
            return code + char_code
        elif len(char_code) == 4:
            return self._maybe_align(code) + char_code
        else:
            # This should not happen!
            return code

    def _text_to_code(self, s):
        code = u''
        lines = string.split(self._layout_line(s), u'\n')
        for row, line in enumerate(lines):
            row += 16 - len(lines)
            # Move cursor to column 0 of the destination row
            for _ in range(2):
                code += (u'%s%s ' % (PAC_HIGH_BYTE_BY_ROW[row],
                                     PAC_LOW_BYTE_BY_ROW_RESTRICTED[row]))
            # Print the line using the SCC encoding
            for char in line:
                code = self._print_character(code, char)
                code = self._maybe_space(code)
            code = self._maybe_align(code)
        return code

    def _format_timestamp(self, microseconds):
        seconds_float = microseconds / 1000.0 / 1000.0
        # Convert to non-drop-frame timecode
        seconds_float *= 1000.0 / 1001.0
        hours = math.floor(seconds_float / 3600)
        seconds_float -= hours * 3600
        minutes = math.floor(seconds_float / 60)
        seconds_float -= minutes * 60
        seconds = math.floor(seconds_float)
        seconds_float -= seconds
        frames = math.floor(seconds_float * 30)
        return u'%02d:%02d:%02d:%02d' % (hours, minutes, seconds, frames)


class _TimingCorrectingCaptionList(list):
    """List of captions. Will know to correct the last caption's end time
    when adding a new caption.

    Also, doesn't allow Nones or empty captions
    """
    def append(self, p_object):
        """When appending a new caption to the list, make sure the last one
        has an end. Also, don't add empty captions

        :type p_object: Caption
        """
        if p_object is None:
            return

        if len(self) > 0 and self[-1].end == 0:
            self[-1].end = p_object.start

        if p_object.nodes:
            super(_TimingCorrectingCaptionList, self).append(p_object)

    def extend(self, iterable):
        for elem in iterable:
            self.append(elem)


class _CaptionStash(object):
    """Creates and maintains a collection of Captions
    """
    def __init__(self):
        self._collection = _TimingCorrectingCaptionList()

        # subset of self._collection;
        # captions here will be susceptible to time corrections
        self._still_editing = []

    def correct_last_timing(self, end_time, force=False):
        """Called to set the time on the last Caption(s) stored with no end
        time

        :type force: bool
        :param force: Set the end time even if there's already an end time

        :type end_time: int
        :param end_time: microseconds; the end of the caption;
        """
        if not self._still_editing:
            return

        if force:
            captions_to_correct = self._still_editing
        else:
            captions_to_correct = (
                caption for caption in self._still_editing
                if caption.end == 0
            )

        for caption in captions_to_correct:
            caption.end = end_time

    def get_last(self):
        """Returns the last caption stored (for setting the time on it),
        or None

        :rtype: Caption
        """
        if len(self._collection) > 0:
            return self._collection[-1]

        return None

    def create_and_store(self, node_buffer, start):
        """Given the buffer, create one (or multiple) Captions, storing them
        internally

        :type node_buffer: _InterpretableNodeStash

        :type start: int
        :param start: the start time in microseconds
        """
        if node_buffer.is_empty():
            return

        caption = Caption()
        caption.start = start
        caption.end = 0  # Not yet known; filled in later
        self._still_editing = [caption]

        open_italic = False

        for element in node_buffer:
            # skip empty elements
            if element.is_empty():
                continue

            elif element.requires_repositioning():
                self._remove_extra_italics(caption)
                caption = Caption()
                caption.start = start
                caption.end = 0
                self._still_editing.append(caption)

            # handle line breaks
            elif element.is_explicit_break():
                new_nodes = self._translate_break(open_italic)
                open_italic = False
                caption.nodes.extend(new_nodes)

            # handle open italics
            elif element.sets_italics_on():
                # add italics
                caption.nodes.append(
                    CaptionNode.create_style(True, {u'italics': True}))
                # open italics, no longer first element
                open_italic = True

            # handle clone italics
            elif element.sets_italics_off() and open_italic:
                caption.nodes.append(
                    CaptionNode.create_style(False, {u'italics': True}))
                open_italic = False

            # handle text
            else:
                # add text
                layout_info = _get_layout_from_tuple(element.position)
                caption.nodes.append(
                    CaptionNode.create_text(element.get_text(),
                                            layout_info=layout_info),
                )
                caption.layout_info = layout_info

        # close any open italics left over
        if open_italic:
            caption.nodes.append(
                CaptionNode.create_style(False, {u'italics': True}))

        # remove extraneous italics tags in the same caption
        self._remove_extra_italics(caption)

        self._collection.extend(self._still_editing)

    @staticmethod
    def _translate_break(open_italic):
        """Depending on the context, translates a line break into one or more
        nodes, returning them.

        :param open_italic: bool
        :rtype: tuple
        """
        new_nodes = []

        if open_italic:
            new_nodes.append(CaptionNode.create_style(
                False, {u'italics': True}))

        # add line break
        new_nodes.append(CaptionNode.create_break())

        return new_nodes

    @staticmethod
    def _remove_extra_italics(caption):
        """Legacy logic slightly refactored. Removes STYLE nodes that would
        surround a BREAK node.

        See CaptionNode

        :type caption: Caption
        """
        i = 0
        length = max(0, len(caption.nodes) - 2)
        while i < length:
            if (caption.nodes[i].type_ == CaptionNode.STYLE and
                    caption.nodes[i].content[u'italics'] and
                    caption.nodes[i + 1].type_ == CaptionNode.BREAK and
                    caption.nodes[i + 2].type_ == CaptionNode.STYLE and
                    caption.nodes[i + 2].content[u'italics']):
                # Remove the two italics style nodes
                caption.nodes.pop(i)
                caption.nodes.pop(i + 1)
                length -= 2
            i += 1

    def get_all(self):
        """Returns the Caption collection as a list

        :rtype: list
        """
        return list(self._collection)


class _SccTimeTranslator(object):
    """Converts SCC time to microseconds, keeping track of frames passed
    """
    def __init__(self):
        self._time = 0
        self._offset = 0
        self._frames = 0

    def get_time(self):
        """Returns the time, in microseconds. Takes into account the number of
        frames passed, and the offset

        :rtype: int
        """
        return self._translate_time(
            self._time[:-2] + unicode(int(self._time[-2:]) + self._frames),
            self._offset
        )

    @staticmethod
    def _translate_time(stamp, offset):
        """
        :param stamp:
        :type offset: int
        :param offset: Subtract this many microseconds from the calculated time
            Helpful for when the captions are off by some time interval.
        :rtype: int
        """
        if u';' in stamp:
            # Drop-frame timebase runs at the same rate as wall clock
            seconds_per_timestamp_second = 1.0
        else:
            # Non-drop-frame timebase runs "slow"
            # 1 second of timecode is longer than an actual second (1.001s)
            seconds_per_timestamp_second = 1001.0 / 1000.0

        time_split = stamp.replace(u';', u':').split(u':')

        timestamp_seconds = (int(time_split[0]) * 3600 +
                             int(time_split[1]) * 60 +
                             int(time_split[2]) +
                             int(time_split[3]) / 30.0)

        seconds = timestamp_seconds * seconds_per_timestamp_second
        microseconds = seconds * 1000 * 1000 - offset

        if microseconds < 0:
            microseconds = 0

        return microseconds

    def start_at(self, timespec):
        """Reset the counter to the given time

        :type timespec: unicode
        """
        self._time = timespec
        self._frames = 0

    def set_offset(self, offset):
        """Sets the offset from which to calculate the time

        :param offset: number of microseconds. will be deducted when
            calculating the time
        :type offset: int
        """
        self._offset = offset

    def increment_frames(self):
        """After a command was processed, we'd increment the number of frames
        """
        self._frames += 1


class _InterpretableNodeStash(object):
    """Creates _InterpretableNode instances from characters and commands,
    and stores them internally in a buffer.
    """
    def __init__(self, collection=None):
        if not collection:
            self._collection = []
        else:
            self._collection = collection
        self._position_tracer = _PositioningTracer()

    def is_empty(self):
        """Whether any text was added to the buffer
        """
        return not any(element.text for element in self._collection)

    def discard_last_char(self):
        """This was previously used to discard a mid-row command, but generated
        a bug, by confusing special/extended characters with mid-row commands.
        This method should only discard the last character if it's a mid-row
        command, and it's equal to the current command - that however should
        be handled by _handle_double_command already
        """
        pass

    def add_chars(self, *chars):
        """Adds characters to a text node (last text node, or a new one)

        :param chars: tuple containing text (unicode)
        """
        if not chars:
            return

        current_position = self._position_tracer.get_current_position()

        # get or create a usable node
        if self._collection:
            node = self._collection[-1]
        else:
            # create first node
            node = _InterpretableNode(position=current_position)
            self._collection.append(node)

        # handle a simple line break
        if self._position_tracer.is_linebreak_required():
            # must insert a line break here
            self._collection.append(_InterpretableNode.create_break(
                position=current_position))
            node = _InterpretableNode.create_text(current_position)
            self._collection.append(node)
            self._position_tracer.acknowledge_linebreak_consumed()

        # handle completely new positioning
        elif self._position_tracer.is_repositioning_required():
            # this node will have a different positioning than the previous one
            self._collection.append(
                _InterpretableNode.create_repositioning_command())
            node = _InterpretableNode.create_text(current_position)
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

        if u'<$>{italic}<$>' in text:
            self._collection.append(
                _InterpretableNode.create_italics_style(
                    self._position_tracer.get_current_position())
            )
        elif u'<$>{end-italic}<$>' in text:
            self._collection.append(
                _InterpretableNode.create_italics_style(
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
        return iter(self._collection)

    @classmethod
    def from_list(cls, stash_list):
        """Having received a list of instances of this class, creates a new
        instance that contains all the nodes of the previous instances
        (basically concatenates the many stashes into one)

        :param stash_list: a list of instances of this class
        :type stash_list: list[_InterpretableNodeStash]
        :rtype: _InterpretableNodeStash
        """
        instance = cls()
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


class _PositioningTracer(object):
    """Helps determine the positioning of a node, having kept track of
    positioning-related commands.

    Acts like a state-machine, with 2

    """
    def __init__(self, positioning=None):
        """
        :param positioning: positioning information (row, column)
        :type positioning: tuple[int]
        """
        self._positions = [positioning]
        self._break_required = False
        self._repositioning_required = False

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
                # set the positioning for the first time
                self._positions = [positioning]
            return

        row, col = current
        new_row, _ = positioning

        # is the new position simply one line below?
        if new_row == row + 1:
            self._positions.append((new_row, col))
            self._break_required = True
        else:
            # reset the "current" position altogether.
            self._positions = [positioning]
            self._repositioning_required = True

    def get_current_position(self):
        """Returns the current usable position

        :rtype: tuple[int]
        """
        if not any(self._positions):
            raise CaptionReadSyntaxError(
                u'No Preamble Address Code [PAC] was provided'
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
        """Acknowledge the position tracer that the position was changed
        """
        self._repositioning_required = False

    def is_linebreak_required(self):
        """If the current position is simply one line below the previous.
        :rtype: bool
        """
        return self._break_required

    def acknowledge_linebreak_consumed(self):
        """Call to acknowledge that the line required was consumed
        """
        self._break_required = False


class _InterpretableNode(object):
    """Value object, that can contain text information, or interpretable
    commands (such as explicit line breaks or turning italics on/off)
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

        :rtype: _InterpretableNode
        """
        return cls(type_=cls.BREAK, position=position)

    @classmethod
    def create_text(cls, position, *chars):
        """Create a node interpretable as text

        :type position: tuple[int]
        :param position: a tuple (row, col) to mark the positioning

        :type chars: tuple[unicode]
        :param chars: characters to add to the text

        :rtype: _InterpretableNode
        """
        return cls(u''.join(chars), position=position)

    @classmethod
    def create_italics_style(cls, position, turn_on=True):
        """Create a node, interpretable as a command to switch italics on/off

        :type position: tuple[int]
        :param position: a tuple (row, col) to mark the positioning

        :type turn_on: bool
        :param turn_on: whether to turn the italics on or off

        :rtype: _InterpretableNode
        """
        return cls(
            position=position,
            type_=cls.ITALICS_ON if turn_on else cls.ITALICS_OFF
        )

    @classmethod
    def create_repositioning_command(cls):
        """Create node interpretable as a command to change the current
        position
        """
        return cls(type_=cls.CHANGE_POSITION)

    def __repr__(self):
        if self._type == self.BREAK:
            return u'<INode: BR>'
        elif self._type == self.TEXT:
            return u'<INode: "{}">'.format(self.text)
        elif self._type in (self.ITALICS_ON, self.ITALICS_OFF):
            return u'<INode: italics {}>'.format(
                u'on' if self._type == self.ITALICS_ON else u'off')
        else:
            return u'<INode: change position>'


def _get_italics_state_from_command(command):
    """
    :type command: unicode
    :rtype: bool
    """
    if u'italic' in command:
        return True
    return False


def _get_layout_from_tuple(position_tuple):
    """Create a Layout object from the positioning information given

    The row can have a value from 1 to 15 inclusive. (vertical positioning)
    Toe column can have a value from 0 to 31 inclusive. (horizontal)

    :param position_tuple: a tuple of ints (row, col)
    :type position_tuple: tuple
    :rtype: Layout
    """
    if not position_tuple:
        return None

    row, column = position_tuple

    horizontal = Size(100 * column / 32.0, UnitEnum.PERCENT)
    vertical = Size(100 * row / 15.0, UnitEnum.PERCENT)
    return Layout(origin=Point(horizontal, vertical))
