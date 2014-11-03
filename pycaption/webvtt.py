import sys
import re

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
)
from .exceptions import (
    CaptionReadError, CaptionReadSyntaxError,
    CaptionReadNoCaptions
)


TIMING_PATTERN = re.compile(u'^(.+?) --> (.+)')
TIMESTAMP_PATTERN = re.compile(u'^(\d+):(\d{2})(:\d{2})?\.(\d{3})')
VOICE_SPAN_PATTERN = re.compile(u'<v(\\.\\w+)* ([^>]*)>')
OTHER_SPAN_PATTERN = re.compile(u'</?([cibuv]|ruby|rt|lang).*?>')


def microseconds(h, m, s, f):
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000000 + int(f) * 1000


class WebVTTReader(BaseReader):
    def detect(self, content):
        return u'WEBVTT' in content

    def read(self, content, lang=u'en-US'):
        if type(content) != unicode:
            raise RuntimeError('The content is not a unicode string.')

        caption_set = CaptionSet()
        caption_set.set_captions(lang, self._parse(content.splitlines()))

        if caption_set.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return caption_set

    def _parse(self, lines):
        captions = []
        caption = None
        found_timing = False

        for i, line in enumerate(lines):

            if u'-->' in line:
                found_timing = True
                timing_line = i
                last_start_time = captions[-1].start if captions else 0
                try:
                    caption = self._parse_timing_line(line, last_start_time)
                except CaptionReadError as e:
                    new_message = u'%s (line %d)' % (e.args[0], timing_line)
                    raise type(e), new_message, sys.exc_info()[2]

            elif u'' == line:
                if found_timing:
                    if caption.is_empty():
                        raise CaptionReadSyntaxError(
                            u'Cue without content. (line %d)' % timing_line)
                    else:
                        found_timing = False
                        captions.append(caption)
                        caption = None
            else:
                if found_timing:
                    if not caption.is_empty():
                        caption.nodes.append(CaptionNode.create_break())
                    caption.nodes.append(CaptionNode.create_text(
                        self._remove_styles(line)))
                else:
                    # it's a comment or some metadata; ignore it
                    pass

        if caption and not caption.is_empty():
            captions.append(caption)

        return captions

    def _remove_styles(self, line):
        partial_result = VOICE_SPAN_PATTERN.sub(u'\\2: ', line)
        return OTHER_SPAN_PATTERN.sub(u'', partial_result)

    def _parse_timing_line(self, line, last_start_time):
        m = TIMING_PATTERN.search(line)
        if not m:
            raise CaptionReadSyntaxError(
                u'Invalid timing format.')

        caption = Caption()

        caption.start = self._parse_timestamp(m.group(1))
        if caption.start is None:
            raise CaptionReadSyntaxError(
                u'Invalid cue start timestamp.')

        caption.end = self._parse_timestamp(m.group(2))
        if caption.end is None:
            raise CaptionReadSyntaxError(u'Invalid cue end timestamp.')

        if caption.start > caption.end:
            raise CaptionReadError(u'End timestamp is not greater than start timestamp.')

        if caption.start < last_start_time:
            raise CaptionReadError(
                u'Start timestamp is not greater than or equal'
                u'to start timestamp of previous cue.')

        return caption

    def _parse_timestamp(self, input):
        m = TIMESTAMP_PATTERN.search(input)
        if not m:
            return None

        m = m.groups()

        if m[2]:
            # Timestamp takes the form of [hours]:[minutes]:[seconds].[milliseconds]
            return microseconds(m[0], m[1], m[2].replace(u":", u""), m[3])
        else:
            # Timestamp takes the form of [minutes]:[seconds].[milliseconds]
            return microseconds(0, m[0], m[1], m[3])


class WebVTTWriter(BaseWriter):
    HEADER = u'WEBVTT\n\n'

    def __init__(self, *args, **kw):
        pass

    def write(self, caption_set):
        output = self.HEADER

        if caption_set.is_empty():
            return output

        # TODO: styles. These go into a separate CSS file, which doesn't really
        # fit the API here. Figure that out.  Though some style stuff can be
        # done in-line.  This format is a little bit crazy.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        lang = caption_set.get_languages()[0]
        for caption in caption_set.get_captions(lang):
            output += self._write_caption(caption)
            output += u'\n'

        return output

    def _timestamp(self, ts):
        ts = float(ts)/1000000
        hours = int(ts)/60/60
        minutes = int(ts)/60 - hours*60
        seconds = ts - hours*60*60 - minutes*60
        if hours:
            return u"%02d:%02d:%06.3f" % (hours, minutes, seconds)
        else:
            return u"%02d:%06.3f" % (minutes, seconds)

    def _write_caption(self, sub):
        start = self._timestamp(sub.start)
        end = self._timestamp(sub.end)

        output = u"%s --> %s\n" % (start, end)

        output += self._convert_nodes(sub.nodes)
        output += u'\n'

        return output

    def _convert_nodes(self, nodes):
        """Convert a Caption's nodes to text.
        """
        if not nodes:
            return u'&nbsp;'

        s = u''

        for i, node in enumerate(nodes):
            if node.type == CaptionNode.TEXT:
                s += node.content or u'&nbsp;'
            elif node.type == CaptionNode.STYLE:
                # TODO: Ignoring style so far.
                pass
            elif node.type == CaptionNode.BREAK:
                if i > 0 and nodes[i-1].type == CaptionNode.BREAK:
                    s += u'&nbsp;'
                s += u'\n'

        return s