import sys
import re

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
)
from .exceptions import (
    CaptionReadError, CaptionReadSyntaxError,
    CaptionReadNoCaptions
)
from pycaption.geometry import UnitEnum, Size
import ic

TIMING_PATTERN = re.compile(u'^(.+?) --> (.+)')
TIMESTAMP_PATTERN = re.compile(u'^(\d+):(\d{2})(:\d{2})?\.(\d{3})')
VOICE_SPAN_PATTERN = re.compile(u'<v(\\.\\w+)* ([^>]*)>')
OTHER_SPAN_PATTERN = (
    re.compile(u'</?([cibuv]|ruby|rt|lang|(\d+):(\d{2})(:\d{2})?\.(\d{3})).*?>')
)  # These WebVTT tags are stripped off the cues on conversion

WEBVTT_VERSION_OF = {
    u'left': u'left',
    u'center': u'middle',
    u'right': u'right',
    u'start': u'start',
    u'end': u'end'
}

DEFAULT_ALIGNMENT = u'middle'

def microseconds(h, m, s, f):
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000000 + int(f) * 1000


class WebVTTReader(BaseReader):
    def __init__(self, ignore_timing_errors=True, *args, **kwargs):
        """
        :param ignore_timing_errors: Whether to ignore timing checks
        """
        super(WebVTTReader, self).__init__(
            ignore_timing_errors, *args, **kwargs
        )
        self.ignore_timing_errors = ignore_timing_errors

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

    def _validate_timings(self, caption, last_start_time):
        if caption.start is None:
            raise CaptionReadSyntaxError(
                u'Invalid cue start timestamp.')
        if caption.end is None:
            raise CaptionReadSyntaxError(u'Invalid cue end timestamp.')
        if caption.start > caption.end:
            raise CaptionReadError(
                u'End timestamp is not greater than start timestamp.')
        if caption.start < last_start_time:
            raise CaptionReadError(
                u'Start timestamp is not greater than or equal'
                u'to start timestamp of previous cue.')

    def _parse_timing_line(self, line, last_start_time):
        m = TIMING_PATTERN.search(line)
        if not m:
            raise CaptionReadSyntaxError(
                u'Invalid timing format.')

        caption = Caption()

        caption.start = self._parse_timestamp(m.group(1))
        caption.end = self._parse_timestamp(m.group(2))

        if not self.ignore_timing_errors:
            self._validate_timings(caption, last_start_time)

        return caption

    def _parse_timestamp(self, timestamp):
        m = TIMESTAMP_PATTERN.search(timestamp)
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
    global_layout = None
    video_width = None
    video_height = None

    def __init__(self, *args, **kwargs):
        self.video_width = kwargs.pop('video_width', None)
        self.video_height = kwargs.pop('video_height', None)

    def write(self, caption_set):
        """
        :type caption_set: CaptionSet
        """
        output = self.HEADER

        if caption_set.is_empty():
            return output

        # TODO: styles. These go into a separate CSS file, which doesn't really
        # fit the API here. Figure that out.  Though some style stuff can be
        # done in-line.  This format is a little bit crazy.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        lang = caption_set.get_languages()[0]

        self.global_layout = caption_set.get_layout_info(lang)

        captions = caption_set.get_captions(lang)

        return output + u'\n'.join(
            [self._write_caption(caption) for caption in captions])

    def _timestamp(self, ts):
        ts = float(ts) / 1000000
        hours = int(ts) / 60 / 60
        minutes = int(ts) / 60 - hours * 60
        seconds = ts - hours * 60 * 60 - minutes * 60
        if hours:
            return u"%02d:%02d:%06.3f" % (hours, minutes, seconds)
        else:
            return u"%02d:%06.3f" % (minutes, seconds)

    def _write_caption(self, caption):
        """
        :type caption: Caption
        """
        layout_groups = self._layout_groups(caption.nodes)

        start = self._timestamp(caption.start)
        end = self._timestamp(caption.end)
        timespan = u"%s --> %s" % (start, end)

        output = u''

        for cue_text, layout in layout_groups:
            if not layout:
                layout = caption.layout_info or self.global_layout

            cue_settings = self._cue_settings_from(layout)
            output += timespan + cue_settings + u'\n'
            output += cue_text + u'\n'

        return output

    def _cue_settings_from(self, layout):
        """
        :type layout: Layout
        """
        if not layout:
            return u''

        left_offset = None
        top_offset = None
        cue_width = None
        alignment = None

        # Ensure that all positioning values are measured using percentage
        layout.to_percentage_of(self.video_width, self.video_height)

        if layout.origin:
            left_offset = layout.origin.x
            top_offset = layout.origin.y

        if layout.extent:
            cue_width = layout.extent.horizontal

        if layout.padding:
            if layout.padding.start and left_offset:
                # Since there is no padding in WebVTT, the left padding is added
                # to the total left offset (if it is defined and not relative),
                if left_offset:
                    left_offset += layout.padding.start
                # and removed from the total cue width
                if cue_width:
                    cue_width -= layout.padding.start
            # the right padding is cut out of the total cue width,
            if layout.padding.end and cue_width:
                cue_width -= layout.padding.end
            # the top padding is added to the top offset
            # (if it is defined and not relative)
            if layout.padding.before and top_offset:
                top_offset += layout.padding.before
            # and the bottom padding is ignored because the cue box is only as
            # long vertically as the text it contains and nothing can be cut out

        try:
            alignment = WEBVTT_VERSION_OF[layout.alignment.horizontal]
        except KeyError:
            pass

        cue_settings = u''

        if alignment:
            cue_settings += u" align:" + alignment
        if left_offset:
            cue_settings += u" position:{},start".format(unicode(left_offset))
        if top_offset:
            cue_settings += u" line:" + unicode(top_offset)
        if cue_width:
            cue_settings += u" size:" + unicode(cue_width)

        return cue_settings

    def _layout_groups(self, nodes):
        """
        Convert a Caption's nodes to WebVTT cue or cues (depending on
        whether they have the same positioning or not).
        """
        if not nodes:
            return []

        current_layout = nodes[0].layout_info

        # A list with layout groups. Since WebVTT only support positioning
        # for different cues, each layout group has to be represented in a
        # new cue with the same timing but different positioning settings.
        layout_groups = []
        s = u''
        for i, node in enumerate(nodes):
            already_appended = False
            if node.type_ == CaptionNode.TEXT:
                if s and not node.layout_info == current_layout:
                    # If the positioning changes from one node to another,
                    # another WebVTT cue has to be created.
                    layout_groups.append((s, current_layout))
                    already_appended = True
                    current_layout = node.layout_info
                    s = u''
                s += node.content or u'&nbsp;'
            elif node.type_ == CaptionNode.STYLE:
                # TODO: Ignoring style so far.
                pass
            elif node.type_ == CaptionNode.BREAK:
                if i > 0 and nodes[i - 1].type_ == CaptionNode.BREAK:
                    s += u'&nbsp;'
                if i == 0:
                    s += u'&nbsp;'
                s += u'\n'
        if not already_appended:
            layout_groups.append((s, current_layout))
        return layout_groups
