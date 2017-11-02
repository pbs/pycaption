#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
3 types of SCC captions:
    Roll-Up
    Paint-On
    Pop-On

Commands:
    94ae - [ENM] - Erase Non-displayed(buffer) Memory
    942c - [EDM] - Erase Displayed Memory
    9420 - [RCL] - Resume Caption Loading
    9429 - [RDC] - Resume Direct Captioning

    9425, 9426, 94a7 - [RU2], [RU3], [RU4] (roll up captions 2,3 or 4 rows)
        - these commands set the number of expected lines

    94ad - (in CEA-608-E: 142d) - [CR] carriage return.
        - This actually rolls the captions up as many rows as specified by
        [RU1], [RU2], or [RU3]

    80 - no-op char. Doesn't do anything, but must be used with other
        characters, to make a 2 byte word

    97a1, 97a2, 9723 - [TO] move 1, 2 or 3 columns - Tab Over command
        - this moves the positioning 1, 2, or 3 columns to the right
        - Nothing regarding this is implemented.

    942f - [EOC] - display the buffer on the screen - End Of Caption
    ... - [PAC] - Preamble address code (can set positioning and style)
        - All the PACs are specified by the first and second byte combined
        from pycaption.scc.constants.PAC_BYTES_TO_POSITIONING_MAP

    9429 - [RDC] - Resume Direct Captioning
    94a4 - (in CEA-608-E: 1424) - [DER] Delete to End of Row


Pop-On:
    The commands should usually appear in this order. Not strict though, and
    the the commands don't have to necessarily be on the same row.

    1. 94ae [ENM] (erase non displayed memory)
    2. 9420 [RCL] (resume caption loading => this command here means we're using Pop-On captions)
    2.1? [ENM] - if step 0 was skipped?
    3. [PAC] Positioning/ styling command (can position on columns divisible by 4)
        The control chars is called Preamble Address Code [PAC].
    4. If positioning needs to be on columns not divisible by 4, use a [TO] command
    5. text
    6. 942c [EDM] - optionally, erase the currently displayed caption
    7. 942f [EOC] display the caption


Roll-Up:
    1. [RU2], [RU3] or [RU4]    - sets Roll-Up style and depth
        - these set the Roll-Up style: (characteristic command)
    2. [CR] to roll the display up 1 row...lol?
    3. [PAC] - sets the indent of the base row


Paint-On:
    1. [RDC] - sets the Paint-On style (characteristic command)
    2. [PAC]
    3. text
    4. [PAC]
    5. text or [DER]

There are some rules regarding the parity of the commands.

This resource:
http://www.theneitherworld.com/mcpoodle/SCC_TOOLS/DOCS/SCC_FORMAT.HTML
 specifies that there are interpreters which only work if the commands have an
 odd parity. This however is not consistent, and we might not handle well
 these cases. Odd parity of a command means that, converting toe word into
 binary, should result in an odd number of '1's. The PAC commands obey this
 rule, but some do not. Some commands that do not are found in the COMMANDS
 dictionary. This is legacy logic, that I didn't know how to handle, and
 just carried over when implementing positioning.
"""


import re
import math
import string
import textwrap

from pycaption.base import (
    BaseReader, BaseWriter, CaptionSet, CaptionNode,
)
from pycaption.exceptions import CaptionReadNoCaptions, InvalidInputError
from .constants import (
    HEADER, COMMANDS, SPECIAL_CHARS, EXTENDED_CHARS, CHARACTERS,
    MICROSECONDS_PER_CODEWORD, CHARACTER_TO_CODE,
    SPECIAL_OR_EXTENDED_CHAR_TO_CODE, PAC_BYTES_TO_POSITIONING_MAP,
    PAC_HIGH_BYTE_BY_ROW, PAC_LOW_BYTE_BY_ROW_RESTRICTED,
)
from .specialized_collections import (
    TimingCorrectingCaptionList, NotifyingDict, CaptionCreator,
    InstructionNodeCreator)

from .state_machines import DefaultProvidingPositionTracker
from copy import deepcopy


class NodeCreatorFactory(object):
    """Will return instances of the given node_creator.

    This is used as a means of creating new InstructionNodeCreator instances,
    because these need to share state beyond their garbage collection, but
    storing the information at the class level is not good either, because
    this information must be erased after the reader's .read() operation
    completes.
    """
    def __init__(self, position_tracker,
                 node_creator=InstructionNodeCreator):
        self.position_tracker = position_tracker
        self.node_creator = node_creator

    def new_creator(self):
        """Returns a new instance of self.node_creator, initialized with
        the same italics_tracker, and position_tracker
        """
        return self.node_creator(position_tracker=self.position_tracker)

    def from_list(self, roll_rows):
        """Wraps the node_creator's method with the same name

        :param roll_rows: list of node_creator instances

        :return: a node_creator instance
        """
        return self.node_creator.from_list(
            roll_rows,
            position_tracker=self.position_tracker
        )


def get_corrected_end_time(caption):
    """If the last caption was never explicitly ended, set its end time to
    start + 4 seconds

    :param Caption caption: the last caption
    :rtype: int
    """
    if caption.end:
        return caption.end

    return caption.start + 4 * 1000 * 1000



class SCCReader(BaseReader):
    """Converts a given unicode string to a CaptionSet.

    This can be then later used for converting into any other supported formats
    """
    def __init__(self, *args, **kw):
        super(SCCReader, self).__init__(*args, **kw)

        self.caption_stash = CaptionCreator(ignore_layout=self.ignore_layout)
        self.time_translator = _SccTimeTranslator()

        self.node_creator_factory = NodeCreatorFactory(
            DefaultProvidingPositionTracker()
        )

        self.last_command = u''

        self.buffer_dict = NotifyingDict()

        self.buffer_dict[u'pop'] = self.node_creator_factory.new_creator()
        self.buffer_dict[u'paint'] = self.node_creator_factory.new_creator()
        self.buffer_dict[u'roll'] = self.node_creator_factory.new_creator()

        # Call this method when the active key changes
        self.buffer_dict.add_change_observer(self._flush_implicit_buffers)
        self.buffer_dict.set_active(u'pop')

        self.roll_rows = []
        self.roll_rows_expected = 0
        self.simulate_roll_up = False

        self.time = 0

    def detect(self, content):
        """Checks whether the given content is a proper SCC file

        :type content: unicode

        :rtype: bool
        """
        lines = content.splitlines()
        if lines[0] == HEADER:
            return True
        else:
            return False

    def read(self, content, lang=u'en-US', simulate_roll_up=False, offset=0):
        """Converts the unicode string into a CaptionSet

        :type content: unicode
        :param content: The SCC content to be converted to a CaptionSet

        :type lang: unicode
        :param lang: The language of the caption

        :type simulate_roll_up: bool
        :param simulate_roll_up: If True, when converting to other formats,
            the resulting captions will contain all the rows that were visible
            on the screen when the captions were rolling up.

        :type offset: int
        :param offset:

        :rtype: CaptionSet
        """
        if type(content) != unicode:
            raise InvalidInputError(u'The content is not a unicode string.')

        self.simulate_roll_up = simulate_roll_up
        self.time_translator.offset = offset * 1000000
        # split lines
        lines = content.splitlines()

        # loop through each line except the first
        for line in lines[1:]:
            self._translate_line(line)

        self._flush_implicit_buffers()

        captions = CaptionSet({lang: self.caption_stash.get_all()})

        # check captions for incorrect lengths
        for cap in captions.get_captions(lang):
            # if there's an end time on a caption and the difference is
            # less than .05s kill it (this is likely caused by a standalone
            # EOC marker in the SCC file)
            if 0 < cap.end - cap.start < 50000:
                raise ValueError('unsupported length found in SCC input file: ' + str(cap))

        if captions.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")
        else:
            last_caption = captions.get_captions(lang)[-1]
            last_caption.end = get_corrected_end_time(last_caption)

        return captions

    def _fix_last_timing(self, timing):
        """HACK HACK: Certain Paint-On captions don't specify the 942f [EOC]
        (End Of Caption) command on the same line.
        If this is a 942f line, also simulate a 942c (Erase Displayed Memory)
        to properly set the timing on the last caption.

        This method needs some serious attention, because it proves the timing
        calculation is not done well for Pop-On captions
        """
        # Calculate the end time from the current line
        time_translator = _SccTimeTranslator()
        time_translator.start_at(timing)
        time_translator.offset = self.time_translator.offset

        # But use the current time translator for the start time
        self.caption_stash.create_and_store(
            self.buffer, self.time_translator.get_time())

        self.caption_stash.correct_last_timing(time_translator.get_time())
        self.buffer = self.node_creator_factory.node_creator()

    def _flush_implicit_buffers(self, old_key=None, *args):
        """Convert to Captions those buffers whose behavior is implicit.

        The Paint-On buffer is explicit. New captions are created from it
        with the command 'End Of Caption' [EOC], '942f'

        The other 2 buffers, Roll-Up and Paint-On we treat as "more" implicit,
        meaning that they can be displayed by a command on the next row.
        If they're on the last row however, or if the caption type is changing,
        we make sure to convert the buffers to text, so we don't lose any info.
        """
        if old_key == u'pop':
            return

        elif old_key is None or old_key == u'roll':
            if not self.buffer.is_empty():
                self._roll_up()

        elif old_key is None or old_key == u'paint':
            # xxx - perhaps the self.buffer property is sufficient
            if not self.buffer_dict[u'paint'].is_empty():
                self.caption_stash.create_and_store(
                    self.buffer_dict[u'paint'], self.time)

    def _translate_line(self, line):
        # ignore blank lines
        if line.strip() == u'':
            return

        # split line in timestamp and words
        r = re.compile(r"([0-9:;]*)([\s\t]*)((.)*)")
        parts = r.findall(line.lower())

        # XXX!!!!!! THESE 2 LINES ARE A HACK
        if parts[0][2].strip() == u'942f':
            self._fix_last_timing(timing=parts[0][0])

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
        if word in COMMANDS or _is_pac_command(word):
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

        self.buffer.add_chars(SPECIAL_CHARS[word])

    def _translate_extended_char(self, word):
        # XXX - this looks highly buggy. Why would a special char be ignored
        # if it's printed 2 times one after another?
        if self._handle_double_command(word):
            return

        # add to buffer
        self.buffer.add_chars(EXTENDED_CHARS[word])

    def _translate_command(self, word):
        if self._handle_double_command(word):
            return

        # if command is pop_up
        if word == u'9420':
            self.buffer_dict.set_active(u'pop')

        # command is paint_on [Resume Direct Captioning]
        elif word == u'9429':
            self.buffer_dict.set_active(u'paint')

            self.roll_rows_expected = 1
            if not self.buffer.is_empty():
                self.caption_stash.create_and_store(
                    self.buffer, self.time
                )
                self.buffer = self.node_creator_factory.new_creator()

            self.time = self.time_translator.get_time()

        # if command is roll_up 2, 3 or 4 rows
        elif word in (u'9425', u'9426', u'94a7'):
            self.buffer_dict.set_active(u'roll')

            # count how many lines are expected
            if word == u'9425':
                self.roll_rows_expected = 2
            elif word == u'9426':
                self.roll_rows_expected = 3
            elif word == u'94a7':
                self.roll_rows_expected = 4

            # if content is in the queue, turn it into a caption
            if not self.buffer.is_empty():
                self.caption_stash.create_and_store(
                    self.buffer, self.time)
                self.buffer = self.node_creator_factory.new_creator()

            # set rows to empty, configure start time for caption
            self.roll_rows = []
            self.time = self.time_translator.get_time()

        # clear pop_on buffer
        elif word == u'94ae':
            self.buffer = self.node_creator_factory.new_creator()

        # display pop_on buffer [End Of Caption]
        elif word == u'942f':
            self.time = self.time_translator.get_time()
            self.caption_stash.create_and_store(self.buffer, self.time)
            self.buffer = self.node_creator_factory.new_creator()

        # roll up captions [Carriage Return]
        elif word == u'94ad':
            # display roll-up buffer
            if not self.buffer.is_empty():
                self._roll_up()

        # clear screen
        elif word == u'942c':
            self.roll_rows = []

            # XXX - The 942c command has nothing to do with paint-ons
            # This however is legacy code, and will break lots of tests if
            # the proper buffer (self.buffer) is used.
            # Most likely using `self.buffer` instead of the paint buffer
            # is the right thing to do, but this needs some further attention.
            if not self.buffer_dict[u'paint'].is_empty():
                self.caption_stash.create_and_store(
                    self.buffer_dict[u'paint'], self.time)
                self.buffer = self.node_creator_factory.new_creator()

            # attempt to add proper end time to last caption(s)
            self.caption_stash.correct_last_timing(
                self.time_translator.get_time())

        # if command not one of the aforementioned, add to buffer
        else:
            self.buffer.interpret_command(word)

    def _translate_characters(self, word):
        # split word into the 2 bytes
        byte1 = word[:2]
        byte2 = word[2:]

        # check to see if the the bytes are recognized characters
        if byte1 not in CHARACTERS or byte2 not in CHARACTERS:
            return

        self.buffer.add_chars(CHARACTERS[byte1], CHARACTERS[byte2])

    @property
    def buffer(self):
        """Returns the currently active buffer
        """
        return self.buffer_dict.get_active()

    @buffer.setter
    def buffer(self, value):
        """Sets a new value to the active key

        :param value: any object
        """
        try:
            key = self.buffer_dict.active_key
            self.buffer_dict[key] = value
        except TypeError:
            pass

    def _roll_up(self):
        # We expect the active buffer to be the rol buffer
        if self.simulate_roll_up:
            if self.roll_rows_expected > 1:
                if len(self.roll_rows) >= self.roll_rows_expected:
                    self.roll_rows.pop(0)

                self.roll_rows.append(self.buffer)
                self.buffer = self.node_creator_factory.from_list(
                    self.roll_rows)

        # convert buffer and empty
        self.caption_stash.create_and_store(self.buffer, self.time)
        self.buffer = self.node_creator_factory.new_creator()

        # configure time
        self.time = self.time_translator.get_time()

        # try to insert the proper ending time for the previous caption
        self.caption_stash.correct_last_timing(self.time, force=True)


class SCCWriter(BaseWriter):

    def __init__(self, *args, **kw):
        super(SCCWriter, self).__init__(*args, **kw)

    def write(self, caption_set):
        output = HEADER + u'\n\n'

        if caption_set.is_empty():
            return output

        caption_set = deepcopy(caption_set)

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
    @staticmethod
    def _layout_line(caption):
        def caption_node_to_text(caption_node):
            if caption_node.type_ == CaptionNode.TEXT:
                return unicode(caption_node.content)
            elif caption_node.type_ == CaptionNode.BREAK:
                return u'\n'
        caption_text = u''.join(
            [caption_node_to_text(node) for node in caption.nodes])
        inner_lines = string.split(caption_text, u'\n')
        inner_lines_laid_out = [textwrap.fill(x, 32) for x in inner_lines]
        return u'\n'.join(inner_lines_laid_out)

    @staticmethod
    def _maybe_align(code):
        # Finish a half-word with a no-op so we can move to a full word
        if len(code) % 5 == 2:
            code += u'80 '
        return code

    @staticmethod
    def _maybe_space(code):
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

    @staticmethod
    def _format_timestamp(microseconds):
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


class _SccTimeTranslator(object):
    """Converts SCC time to microseconds, keeping track of frames passed
    """
    def __init__(self):
        self._time = '00:00:00;00'

        # microseconds. The offset from which we begin the time calculation
        self.offset = 0
        self._frames = 0

    def get_time(self):
        """Returns the time, in microseconds. Takes into account the number of
        frames passed, and the offset

        :rtype: int
        """
        return self._translate_time(
            self._time[:-2] + unicode(int(self._time[-2:]) + self._frames),
            self.offset
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

    def increment_frames(self):
        """After a command was processed, we'd increment the number of frames
        """
        self._frames += 1


def _is_pac_command(word):
    """Checks whether the given word is a Preamble Address Code [PAC] command

    :type word: unicode
    :param word: 4 letter unicode command

    :rtype: bool
    """
    if not word or len(word) != 4:
        return False

    byte1, byte2 = word[:2], word[2:]

    try:
        PAC_BYTES_TO_POSITIONING_MAP[byte1][byte2]
    except KeyError:
        return False
    else:
        return True
