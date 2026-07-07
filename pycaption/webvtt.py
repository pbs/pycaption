import datetime
import re
import sys
from copy import deepcopy

from .base import BaseReader, BaseWriter, Caption, CaptionList, CaptionNode, CaptionSet
from .exceptions import (
    CaptionReadError,
    CaptionReadNoCaptions,
    CaptionReadSyntaxError,
    InvalidInputError,
)
from .geometry import HorizontalAlignmentEnum, Layout, Point, Size, Stretch, UnitEnum

# A WebVTT timing line has both start/end times and layout related settings
# (referred to as 'cue settings' in the documentation)
# The following pattern captures [start], [end] and [cue settings] if existent
TIMING_LINE_PATTERN = re.compile(r"^(\S+)\s+-->\s+(\S+)(?:\s+(.*?))?\s*$")
"""
Captures [start_timestamp], [end_timestamp], and optional [cue_settings]
from a WebVTT timing line.
00:00:01.000 --> 00:00:03.000 align:start position:10%
"""
TIMESTAMP_PATTERN = re.compile(r"^(\d+):(\d{2})(:\d{2})?\.(\d{3})")
"""
Parses a single WebVTT timestamp into its components.
Captures: hours (or minutes), minutes (or seconds),
optional :seconds, milliseconds.
00:01:23.456 or 01:23.456
"""
VOICE_SPAN_PATTERN = re.compile("<v(\\.\\w+)* ([^>]*)>")
"""
Matches a voice span opening tag, capturing the speaker annotation.
The speaker name is baked into cue text as "Speaker: " prefix.
<v Roger Bingham> or <v.loud Speaker>
"""
TAG_SPLIT_PATTERN = re.compile(r"(<[^>]+>)")
"""
Splits cue text into alternating [text, tag, text, tag, ...] segments.
The capturing group ensures matched tags are retained in the split result.
"""
KNOWN_TAGS = frozenset({"i", "b", "u", "c", "v", "lang", "ruby", "rt"})
"""
The set of recognized WebVTT inline tag names.
Used for classifying opening (<i>, <c.yellow>, <lang en>) and
closing (</i>, </c>, </v>, </lang>) tags during cue text parsing.
Note: "v" is included so </v> is consumed as a closing style node
(the opening <v> is already handled by VOICE_SPAN_PATTERN).
"""
REGION_SETTING_PATTERN = re.compile(r"^([\w]+):(.+)$")
"""  
Matches a setting name (word chars) followed by colon and a value:
id:region1
width:50%
"""
REGION_ANCHOR_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%,(\d+(?:\.\d+)?)%$")
"""
Matches two percentage values (integer or decimal) separated by a comma:
0%,0%
100%,100%
"""
LINE_HEIGHT_VH = 5.33

WEBVTT_VERSION_OF = {
    HorizontalAlignmentEnum.LEFT: "left",
    HorizontalAlignmentEnum.CENTER: "center",
    HorizontalAlignmentEnum.RIGHT: "right",
    HorizontalAlignmentEnum.START: "start",
    HorizontalAlignmentEnum.END: "end",
}

DEFAULT_ALIGN = "start"


def microseconds(h, m, s, f):
    """
    Returns an integer representing a number of microseconds
    :rtype: int
    """
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000000 + int(f) * 1000


class WebVTTReader(BaseReader):
    def __init__(
        self, ignore_timing_errors=True, time_shift_milliseconds=0, *args, **kwargs
    ):
        """
        :param ignore_timing_errors: Whether to ignore timing checks
        :type ignore_timing_errors: bool
        :param time_shift_milliseconds: Move all the timestamps forward/backward with this number of milliseconds
        :type time_shift_milliseconds: int
        """
        self.ignore_timing_errors = ignore_timing_errors
        self.time_shift_microseconds = time_shift_milliseconds * 1000

    def detect(self, content):
        return "WEBVTT" in content

    def read(self, content, lang="en-US"):
        if not isinstance(content, str):
            raise InvalidInputError("The content is not a unicode string.")

        caption_set = CaptionSet({lang: self._parse(content.splitlines())})

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    def _parse(self, lines):
        # State machine: cycles through waiting-for-timing → collecting-text
        # → emit-caption-on-blank-line, repeat.
        captions = CaptionList()
        start = None
        end = None
        nodes = []
        layout_info = None
        found_timing = False

        # Parse REGION blocks from the header area before processing cues
        self._regions = self._parse_regions(lines)

        for i, line in enumerate(lines):
            if "-->" in line:
                # Timing line found (e.g. "00:00:01.000 --> 00:00:03.000")
                # marks the start of a new cue
                found_timing = True
                timing_line = i
                last_start_time = captions[-1].start if captions else 0
                try:
                    start, end, layout_info = self._parse_timing_line(
                        line, last_start_time
                    )
                except CaptionReadError as e:
                    new_msg = f"{e.args[0]} (line {timing_line})"
                    tb = sys.exc_info()[2]
                    raise type(e)(new_msg).with_traceback(tb) from None

            elif "" == line:
                # Blank line = block separator in WebVTT.
                # If we were collecting a cue, finalize and store it.
                if found_timing and nodes:
                    found_timing = False
                    caption = Caption(start, end, nodes, layout_info=layout_info)
                    captions.append(caption)
                    nodes = []
            else:
                if found_timing:
                    # We're inside a cue — this line is cue text.
                    # Add a line break between multi-line cue text.
                    if nodes:
                        nodes.append(CaptionNode.create_break())
                    nodes.extend(self._parse_cue_text(line))
                else:
                    # Outside a cue: cue identifiers, NOTE blocks,
                    # or other metadata — skip silently.
                    pass

        # File may not end with a blank line — emit any remaining cue
        if nodes:
            caption = Caption(start, end, nodes, layout_info=layout_info)
            captions.append(caption)

        return captions

    def _validate_timings(self, start, end, last_start_time):
        if start is None:
            raise CaptionReadSyntaxError("Invalid cue start timestamp.")
        if end is None:
            raise CaptionReadSyntaxError("Invalid cue end timestamp.")
        if start > end:
            raise CaptionReadError("End timestamp is not greater than start timestamp.")
        if start < last_start_time:
            raise CaptionReadError(
                "Start timestamp is not greater than or equal"
                "to start timestamp of previous cue."
            )

    def _parse_timing_line(self, line, last_start_time):
        """
        :returns: Tuple (int, int, Layout)
        """
        m = TIMING_LINE_PATTERN.search(line)
        if not m:
            raise CaptionReadSyntaxError("Invalid timing format.")

        start = self._parse_timestamp(m.group(1)) + self.time_shift_microseconds
        end = self._parse_timestamp(m.group(2)) + self.time_shift_microseconds

        cue_settings = m.group(3)

        if not self.ignore_timing_errors:
            self._validate_timings(start, end, last_start_time)

        layout_info = None
        if cue_settings:
            region_id = self._extract_region_id(cue_settings)
            if region_id and region_id in self._regions:
                layout_info = self._regions[region_id]
                layout_info = Layout(
                    origin=layout_info.origin,
                    extent=layout_info.extent,
                    padding=layout_info.padding,
                    alignment=layout_info.alignment,
                    webvtt_positioning=cue_settings,
                )
            else:
                layout_info = Layout(webvtt_positioning=cue_settings)

        return start, end, layout_info

    def _parse_timestamp(self, timestamp):
        """Returns an integer representing a number of microseconds
        :rtype: int
        """
        m = TIMESTAMP_PATTERN.search(timestamp)
        if not m:
            raise CaptionReadSyntaxError("Invalid timing format.")

        m = m.groups()

        if m[2]:
            # Timestamp of the form [hours]:[minutes]:[seconds].[milliseconds]
            return microseconds(m[0], m[1], m[2].replace(":", ""), m[3])
        else:
            # Timestamp of the form [minutes]:[seconds].[milliseconds]
            return microseconds(0, m[0], m[1], m[3])

    def _parse_cue_text(self, line):
        """Parse a single line of WebVTT cue text into a list of CaptionNodes.

        Converts inline markup tags into CaptionNode.STYLE open/close pairs
        and text content into CaptionNode.TEXT nodes.

        Voice tags are handled before splitting (baked into text as
        "Speaker: " prefix), matching the legacy behavior.

        :param line: A single line of cue text (raw WebVTT)
        :returns: list of CaptionNode
        """
        line = line.strip()
        # \2 is the speaker name capture group; replaces the full <v ...> tag
        # with "Speaker: " so voice identity is preserved as plain text.
        line = VOICE_SPAN_PATTERN.sub(r"\2: ", line)

        nodes = []
        # re.split() with a capturing group guarantees alternating segments:
        # even indices = text (possibly ""), odd indices = captured tags.
        # e.g. "Hello <i>world</i>" -> ["Hello ", "<i>", "world", "</i>", ""]
        parts = TAG_SPLIT_PATTERN.split(line)

        for i, part in enumerate(parts):
            if not part:
                continue

            if i % 2 == 0:
                # Even indices are plain text — decode entities and store
                text = self._decode_entities(part)
                if text:
                    nodes.append(CaptionNode.create_text(text))
            else:
                # Odd indices are tags — classify into style/text nodes
                node = self._classify_tag(part)
                if node is not None:
                    nodes.append(node)

        return nodes

    def _classify_tag(self, tag_str):
        """Classify a captured tag string and return the appropriate
        CaptionNode.

        Returns a STYLE node for recognized tags, a TEXT node for
        unrecognized angle-bracket content (e.g. "<LAUGHING>"), so that
        arbitrary text in angle brackets is preserved rather than dropped.

        :param tag_str: The raw tag string, e.g. "<i>", "</b>", "<c.yellow>"
        :returns: CaptionNode or None
        """
        # Strip the angle brackets: "<i>" -> "i", "</b>" -> "/b"
        inner = tag_str[1:-1]

        # Closing tag: starts with "/"
        if inner.startswith("/"):
            tag_name = inner[1:]
            if tag_name in KNOWN_TAGS:
                content = self._tag_content(tag_name)
                if not content:
                    return None
                return CaptionNode.create_style(False, content)
            else:
                text = self._decode_entities(tag_str)
                return CaptionNode.create_text(text)

        # Timestamp tag: e.g. "00:01:23.456"
        m = TIMESTAMP_PATTERN.match(inner)
        if m:
            groups = m.groups()
            if groups[2] is not None:
                secs = groups[2].replace(":", "")
                us = microseconds(
                    groups[0], groups[1], secs, groups[3]
                )
            else:
                us = microseconds(0, groups[0], groups[1], groups[3])
            return CaptionNode.create_style(True, {"timestamp": us})

        # Opening tag: extract tag name, optional .classes, optional annotation
        # Examples: "i", "c.yellow", "lang en"
        tag_name, class_suffix, annotation = self._parse_opening_tag(inner)
        if tag_name in KNOWN_TAGS:
            content = self._tag_content(tag_name, class_suffix, annotation)
            return CaptionNode.create_style(True, content)

        # Unrecognized — treat as literal text (e.g. "<LAUGHING & WHOOPS!>")
        text = self._decode_entities(tag_str)
        return CaptionNode.create_text(text)

    @staticmethod
    def _parse_opening_tag(inner):
        """Parse the inside of an opening tag into
        (name, class_suffix, annotation).

        "i"          -> ("i", None, None)
        "c.yellow"   -> ("c", "yellow", None)
        "lang en"    -> ("lang", None, "en")
        "c.a.b"      -> ("c", "a.b", None)

        :param inner: Tag content without angle brackets
        :returns: tuple (tag_name, class_suffix, annotation)
        """
        # Split on first space for annotation (e.g. "lang en-US")
        if " " in inner:
            tag_part, annotation = inner.split(" ", 1)
        else:
            tag_part, annotation = inner, None

        # Split on first dot for class suffix (e.g. "c.yellow.highlight")
        if "." in tag_part:
            tag_name, class_suffix = tag_part.split(".", 1)
        else:
            tag_name, class_suffix = tag_part, None

        return tag_name, class_suffix, annotation

    @staticmethod
    def _tag_content(tag_name, class_suffix=None, annotation=None):
        """Build the style content dict for a tag.

        :returns: dict
        """
        if tag_name == "i":
            return {"italics": True}
        elif tag_name == "b":
            return {"bold": True}
        elif tag_name == "u":
            return {"underline": True}
        elif tag_name == "c":
            classes = class_suffix.split(".") if class_suffix else []
            return {"classes": classes}
        elif tag_name == "lang":
            return {"lang": annotation.strip() if annotation else ""}
        elif tag_name == "ruby":
            return {"ruby": True}
        elif tag_name == "rt":
            return {"ruby_text": True}
        return {}

    @staticmethod
    def _decode_entities(text):
        """Decode WebVTT character entities in a text segment.

        :type text: str
        :rtype: str
        """
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&lrm;", "‎")
        text = text.replace("&rlm;", "‏")
        text = text.replace("&nbsp;", " ")
        text = text.replace("&amp;", "&")
        return text

    def _parse_regions(self, lines):
        """Parse REGION blocks from the file header area.

        A WebVTT region defines a named rectangular area on screen where cues
        can be rendered. Regions appear before any cues with the syntax:

            REGION
            id:subtitle_area
            width:50%
            lines:3
            regionanchor:0%,100%
            viewportanchor:10%,90%
            scroll:up

        Supported settings:
            id             - unique identifier (required)
            width          - region width as percentage (default: 100%)
            lines          - visible line count (default: 3)
            regionanchor   - anchor point within region as x%,y% (default: 0%,100%)
            viewportanchor - anchor point on viewport as x%,y% (default: 0%,100%)
            scroll         - scroll behavior, only "up" is valid (default: none)

        :returns: dict mapping region id -> Layout
        """
        regions = {}
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if line == "REGION" or line.startswith(("REGION\t", "REGION ")):
                i += 1
                settings = {}
                seen_keys = set()
                # Read settings until a blank line (block separator in WebVTT)
                while i < len(lines) and lines[i].strip() != "":
                    # Match key:value pair (e.g. "width:50%")
                    m = REGION_SETTING_PATTERN.match(lines[i].strip())
                    if m:
                        key, value = m.group(1), m.group(2)
                        if key in seen_keys:
                            i += 1
                            continue
                        seen_keys.add(key)
                        settings[key] = value
                    i += 1
                # Skip regions without id (spec requires it; cues can't reference them)
                if "id" in settings:
                    region_id = settings["id"]
                    # First definition wins; duplicates are ignored (RULE-REG-009)
                    if region_id not in regions:
                        regions[region_id] = self._region_to_layout(settings)
            elif "-->" in line:
                # REGIONs only appear before cues; stop scanning once cues begin
                break
            else:
                i += 1
        return regions

    def _region_to_layout(self, settings):
        """Convert parsed region settings dict into a Layout with origin/extent.

        Uses W3C TTML-WebVTT mapping formulas:
            origin_x = viewportanchor_x - (regionanchor_x / 100 * width)
            origin_y = viewportanchor_y - (regionanchor_y / 100 * height)
            height = lines * 5.33
        """
        # Spec defaults per W3C WebVTT §6
        width = 100.0
        lines = 3
        regionanchor_x, regionanchor_y = 0.0, 100.0
        viewportanchor_x, viewportanchor_y = 0.0, 100.0
        # Parse each setting, falling back to defaults on invalid values
        if "width" in settings:
            try:
                width = float(settings["width"].rstrip("%"))
            except ValueError:
                pass

        if "lines" in settings:
            try:
                lines = int(settings["lines"])
            except ValueError:
                pass

        # regionanchor: which point inside the region is "pinned"
        # e.g. 0%,100% means the bottom-left corner of the region
        if "regionanchor" in settings:
            m = REGION_ANCHOR_PATTERN.match(settings["regionanchor"])
            if m:
                regionanchor_x = float(m.group(1))
                regionanchor_y = float(m.group(2))

        # viewportanchor: where on the screen that pin is placed
        # e.g. 10%,90% means 10% from left, 90% from top
        if "viewportanchor" in settings:
            m = REGION_ANCHOR_PATTERN.match(settings["viewportanchor"])
            if m:
                viewportanchor_x = float(m.group(1))
                viewportanchor_y = float(m.group(2))

        # Calculate the top-left corner (origin) of the region box.
        # Each line is ~5.33% of viewport height (LINE_HEIGHT_VH).
        height = lines * LINE_HEIGHT_VH
        # The origin is where the viewport anchor is, offset back by how far
        # the region anchor is into the box (as a fraction of box dimensions).
        origin_x = viewportanchor_x - (regionanchor_x / 100.0 * width)
        origin_y = viewportanchor_y - (regionanchor_y / 100.0 * height)

        origin = Point(
            Size(origin_x, UnitEnum.PERCENT),
            Size(origin_y, UnitEnum.PERCENT),
        )
        extent = Stretch(
            Size(width, UnitEnum.PERCENT),
            Size(height, UnitEnum.PERCENT),
        )

        return Layout(
            origin=origin,
            extent=extent
        )

    @staticmethod
    def _extract_region_id(cue_settings):
        """Extract region id from cue settings string, if present."""
        for setting in cue_settings.split():
            if setting.startswith("region:"):
                return setting[7:]
        return None


class WebVTTWriter(BaseWriter):
    HEADER = "WEBVTT\n\n"

    def write(self, caption_set, lang=None):
        """
        :type caption_set: CaptionSet
        :type lang: str
        """
        output = self.HEADER

        if caption_set.is_empty():
            return output

        caption_set = deepcopy(caption_set)

        # TODO: styles. These go into a separate CSS file, which doesn't really
        # fit the API here. Figure that out.  Though some style stuff can be
        # done in-line.  This format is a little bit crazy.

        if lang is None:
            lang = caption_set.get_languages()[0]

        self.global_layout = caption_set.get_layout_info(lang)

        captions = caption_set.get_captions(lang)

        return output + "\n".join(
            [self._convert_caption(caption_set, caption) for caption in captions]
        )

    def _timestamp(self, ts):
        td = datetime.timedelta(microseconds=ts)
        mm, ss = divmod(td.seconds, 60)
        hh, mm = divmod(mm, 60)
        s = f"{mm:02}:{ss:02}.{td.microseconds // 1000:03}"
        if hh:
            s = f"{hh:02}:{s}"
        return s

    @staticmethod
    def _convert_style_to_text_tag(style):
        if style == "italics":
            return ["<i>", "</i>"]
        elif style == "underline":
            return ["<u>", "</u>"]
        elif style == "bold":
            return ["<b>", "</b>"]
        else:
            return ["", ""]

    def _calculate_resulting_style(self, style, caption_set):
        resulting_style = {}

        style_classes = []
        if "classes" in style:
            style_classes = style["classes"]
        elif "class" in style:
            style_classes = [style["class"]]

        for style_class in style_classes:
            sub_style = caption_set.get_style(style_class).copy()
            # Recursively resolve class attributes and calculate style
            resulting_style.update(
                self._calculate_resulting_style(sub_style, caption_set)
            )

        resulting_style.update(style)

        return resulting_style

    def _convert_caption(self, caption_set, caption):
        """
        :type caption: Caption
        """
        layout_groups = self._group_cues_by_layout(caption.nodes, caption_set)

        start = self._timestamp(caption.start)
        end = self._timestamp(caption.end)
        timespan = f"{start} --> {end}"

        output = ""

        cue_style_tags = ["", ""]

        # Text styling
        style = self._calculate_resulting_style(caption.style, caption_set)
        for key, value in sorted(style.items()):
            if value:
                tags = self._convert_style_to_text_tag(key)
                cue_style_tags[0] += tags[0]
                cue_style_tags[1] = tags[1] + cue_style_tags[1]

        for cue_text, layout in layout_groups:
            if not layout:
                layout = caption.layout_info or self.global_layout
            cue_settings = self._convert_positioning(layout)
            output += timespan + cue_settings + "\n"
            output += cue_style_tags[0] + cue_text + cue_style_tags[1] + "\n"

        return output

    def _convert_positioning(self, layout):
        """
        Return WebVTT cue settings string based on layout info
        :type layout: Layout
        :rtype: str
        """
        if not layout:
            return ""

        # If it's converting from WebVTT to WebVTT, keep positioning info
        # unchanged
        if layout.webvtt_positioning:
            return f" {layout.webvtt_positioning}"

        left_offset = None
        top_offset = None
        cue_width = None

        already_relative = False
        if not self.relativize:
            if layout.is_relative():
                already_relative = True
            else:
                # There are absolute positioning values for this cue but the
                # Writer is explicitly configured not to do any relativization.
                # Ignore all positioning for this cue.
                return ""

        # Ensure that all positioning values are measured using percentage.
        # This may raise an exception if layout.is_relative() == False
        # If you want to avoid it, you have to turn off relativization by
        # initializing this Writer with relativize=False.
        if not already_relative:
            layout = layout.as_percentage_of(self.video_width, self.video_height)

        # Ensure that when there's a left offset the caption is not pushed out
        # of the screen. If the execution got this far it means origin and
        # extent are already relative by now.
        if self.fit_to_screen:
            layout = layout.fit_to_screen()

        if layout.origin:
            left_offset = layout.origin.x
            top_offset = layout.origin.y

        if layout.extent:
            cue_width = layout.extent.horizontal

        if layout.padding:
            if layout.padding.start and left_offset:
                # Since there is no padding in WebVTT, the left padding is
                # added to the total left offset (if it is defined and not
                # relative),
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
            # long vertically as the text it contains and nothing can be cut
            # out

        if layout.alignment:
            alignment = WEBVTT_VERSION_OF.get(
                layout.alignment.horizontal, DEFAULT_ALIGN
            )
        else:
            alignment = DEFAULT_ALIGN
        cue_settings = ""

        if alignment and alignment != WEBVTT_VERSION_OF[HorizontalAlignmentEnum.CENTER]:
            # Not sure why this condition was here, maybe because center
            # alignment is applied automatically without needing to specify it
            cue_settings += f" align:{alignment}"
        if left_offset:
            cue_settings += f" position:{left_offset}"
        if top_offset:
            cue_settings += f" line:{top_offset}"
        if cue_width:
            cue_settings += f" size:{cue_width}"

        return cue_settings

    def _group_cues_by_layout(self, nodes, caption_set):
        """
        Convert a Caption's nodes to WebVTT cue or cues (depending on
        whether they have the same positioning or not).
        """
        if not nodes:
            return []

        current_layout = None

        # A list with layout groups. Since WebVTT only support positioning
        # for different cues, each layout group has to be represented in a
        # new cue with the same timing but different positioning settings.
        layout_groups = []
        # A properly encoded WebVTT string (plain unicode must be properly
        # escaped before being appended to this string)
        s = ""
        for i, node in enumerate(nodes):
            if node.type_ == CaptionNode.TEXT:
                if s and current_layout and node.layout_info != current_layout:
                    # If the positioning changes from one text node to
                    # another, a new WebVTT cue has to be created.
                    layout_groups.append((s, current_layout))
                    s = ""
                # ATTENTION: This is where the plain unicode node content is
                # finally encoded as WebVTT.
                s += self._encode_illegal_characters(node.content) or "&nbsp;"
                current_layout = node.layout_info
            elif node.type_ == CaptionNode.STYLE:
                resulting_style = self._calculate_resulting_style(
                    node.content, caption_set
                )

                has_text_style = False
                styles = ["italics", "underline", "bold"]
                if not node.start:
                    styles.reverse()

                for style in styles:
                    if style in resulting_style and resulting_style[style]:
                        has_text_style = True
                        tags = self._convert_style_to_text_tag(style)
                        if node.start:
                            s += tags[0]
                        else:
                            s += tags[1]

                if not has_text_style:
                    s += self._convert_structural_tag(
                        node.content, node.start
                    )
            elif node.type_ == CaptionNode.BREAK:
                if i > 0 and nodes[i - 1].type_ != CaptionNode.TEXT:
                    s += "&nbsp;"
                if i == 0:  # cue text starts with a break
                    s += "&nbsp;"
                s += "\n"

        if s:
            layout_groups.append((s, current_layout))
        return layout_groups

    def _encode_illegal_characters(self, s):
        """
        Convert cue text from plain unicode to WebVTT XML-like format
        escaping illegal characters. For a list of illegal characters see:
            - http://dev.w3.org/html5/webvtt/#dfn-webvtt-cue-text-span
        :type s: str
        """
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;")

        # The substring "-->" is also not allowed according to this:
        #   - http://dev.w3.org/html5/webvtt/#dfn-webvtt-cue-block
        s = s.replace("-->", "--&gt;")

        # The following characters have escaping codes for some reason, but
        # they're not illegal, so for now I'll leave this commented out so that
        # we stay as close as possible to the specification and avoid doing
        # extra stuff "just to be safe".
        # s = s.replace('>', '&gt;')
        # s = s.replace('\u200e', '&lrm;')
        # s = s.replace('\u200f', '&rlm;')
        # s = s.replace('\u00a0', '&nbsp;')
        return s

    def _convert_structural_tag(self, content, is_start):
        """Convert a structural style node back into a WebVTT tag string.

        Structural tags are WebVTT-specific (class, lang, ruby, timestamp).
        Other writers silently ignore these keys.

        :param content: The style node's content dict
        :param is_start: True for opening tag, False for closing
        :returns: str
        """
        if "lang" in content:
            if is_start:
                lang = content["lang"]
                return f"<lang {lang}>" if lang else "<lang>"
            return "</lang>"
        elif "classes" in content:
            if is_start:
                classes = content["classes"]
                class_str = "." + ".".join(classes) if classes else ""
                return f"<c{class_str}>"
            return "</c>"
        elif "ruby" in content:
            return "<ruby>" if is_start else "</ruby>"
        elif "ruby_text" in content:
            return "<rt>" if is_start else "</rt>"
        elif "timestamp" in content:
            if is_start:
                return f"<{self._timestamp(content['timestamp'])}>"
            return ""
        return ""
