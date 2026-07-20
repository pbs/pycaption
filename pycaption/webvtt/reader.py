import html
import sys
import warnings

from ..base import BaseReader, Caption, CaptionList, CaptionNode, CaptionSet
from ..exceptions import (
    CaptionReadError,
    CaptionReadNoCaptions,
    CaptionReadSyntaxError,
    CaptionReadWarning,
    InvalidInputError,
)
from ..geometry import (
    Alignment,
    Layout,
    Point,
    Size,
    Stretch,
    UnitEnum,
    WritingDirectionEnum,
)
from .constants import (
    ALIGN_SETTING_MAP,
    CUE_SETTING_PATTERN,
    KNOWN_TAGS,
    LINE_GRID_SIZE,
    LINE_HEIGHT_VH,
    REGION_ANCHOR_PATTERN,
    REGION_SETTING_PATTERN,
    STYLE_SELECTOR_PATTERN,
    TAG_SPLIT_PATTERN,
    TIMESTAMP_PATTERN,
    TIMING_LINE_PATTERN,
    VOICE_SPAN_PATTERN,
    _is_note_start,
    microseconds,
)


def _flush_css_block(css_lines, blocks):
    """Join accumulated CSS lines into a single block string and append
    to the blocks list. No-op if css_lines is empty."""
    if css_lines:
        blocks.append("\n".join(css_lines) + "\n")


def _covers_base(content, base_props):
    """Return True if content dict contains all key-value pairs from
    base_props (i.e. the style node already carries the base styling)."""
    return all(content.get(k) == v for k, v in base_props.items())


class _ParseState:
    """Mutable state container for the line-by-line cue parser.

    Tracks the current cue being assembled (timestamps, nodes, open tags)
    and whether we're inside a NOTE or STYLE block that should be skipped.
    """

    __slots__ = (
        "start",
        "end",
        "nodes",
        "open_tags",
        "layout_info",
        "found_timing",
        "in_note_block",
        "in_style_block",
    )

    def __init__(self):
        self.start = None
        self.end = None
        self.nodes = []
        self.open_tags = []
        self.layout_info = None
        self.found_timing = False
        self.in_note_block = False
        self.in_style_block = False


class WebVTTReader(BaseReader):
    """Reader for the WebVTT (Web Video Text Tracks) caption format.

    Parses a WebVTT file into a CaptionSet containing captions with
    timing, positioning, inline styling, region definitions, and
    STYLE block declarations.
    """

    _CUE_SELECTOR = "::cue"

    def __init__(
        self, ignore_timing_errors=True, time_shift_milliseconds=0, *args, **kwargs
    ):
        """
        :param ignore_timing_errors: When False, raises on non-monotonic
            or inverted timestamps. Default True for lenient parsing.
        :param time_shift_milliseconds: Offset applied to all timestamps
            (positive = shift forward, negative = shift backward).
        """
        super().__init__(*args, **kwargs)
        self.ignore_timing_errors = ignore_timing_errors
        self.time_shift_microseconds = time_shift_milliseconds * 1000

    def detect(self, content):
        """Return True if content looks like a WebVTT file.

        Checks the first line for the required "WEBVTT" signature,
        optionally followed by a space or tab and header metadata.
        Handles BOM-prefixed content.
        """
        if content.startswith("﻿"):
            content = content[1:]
        first_line = content.splitlines()[0] if content.strip() else ""
        return (
            first_line == "WEBVTT"
            or first_line.startswith("WEBVTT ")
            or first_line.startswith("WEBVTT\t")
        )

    def read(self, content, lang="en-US"):
        """Parse a WebVTT string into a CaptionSet.

        Pipeline: validate header → parse STYLE blocks → parse REGION
        blocks and cues → cascade styles onto nodes → build CaptionSet.

        :param content: Full WebVTT file content as a unicode string.
        :param lang: BCP-47 language code for the caption track.
        :returns: CaptionSet with captions, styles, and regions.
        :raises InvalidInputError: If content is not a string.
        :raises CaptionReadNoCaptions: If no cues are found.
        """
        if not isinstance(content, str):
            raise InvalidInputError("The content is not a unicode string.")

        if content.startswith("﻿"):
            content = content[1:]

        # str.splitlines() handles CR, LF, CRLF (W3C WebVTT §3 RULE-FMT-005)
        lines = content.splitlines()
        self._validate_header(lines)
        styles = self._parse_style_blocks(lines)
        captions = self._parse(lines)
        self._resolve_cue_styles(captions, styles)

        caption_set = CaptionSet(
            {lang: captions}, styles=styles, regions=self._regions_raw
        )

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    @staticmethod
    def _validate_header(lines):
        """Enforce WebVTT header requirements.

        :raises CaptionReadSyntaxError: If file is empty, doesn't start
            with WEBVTT, or is missing the blank line after the header.
        """
        if not lines:
            raise CaptionReadSyntaxError("WebVTT file is empty.")

        first_line = lines[0]
        if not (
            first_line == "WEBVTT"
            or first_line.startswith("WEBVTT ")
            or first_line.startswith("WEBVTT\t")
        ):
            raise CaptionReadSyntaxError(
                "WebVTT file must start with 'WEBVTT' on the first line."
            )

        if len(lines) > 1 and lines[1] != "":
            raise CaptionReadSyntaxError("Missing blank line after WebVTT header.")

    def _parse(self, lines):
        """Parse all cues from the file lines into a CaptionList.

        Also parses REGION blocks (stored on self._regions and
        self._regions_raw) since regions must be resolved before cues
        that reference them.

        :returns: CaptionList of Caption objects.
        """
        self._regions, self._regions_raw = self._parse_regions(lines)

        captions = CaptionList()
        state = _ParseState()

        for i, line in enumerate(lines):
            self._parse_line(line, i, state, captions)

        # Flush the last cue if file doesn't end with a blank line
        if state.nodes:
            captions.append(
                self._build_cue(
                    state.nodes,
                    state.open_tags,
                    state.start,
                    state.end,
                    state.layout_info,
                )
            )

        return captions

    def _parse_line(self, line, line_index, state, captions):
        """Process a single line through the parsing state machine.

        Transitions: skip NOTE/STYLE blocks → detect timing line →
        accumulate cue text → finalize cue on blank line.
        """
        if state.in_note_block:
            state.in_note_block = line != ""
            return

        if state.in_style_block:
            state.in_style_block = line != ""
            return

        if self._check_block_start(line, state):
            return

        if "-->" in line:
            state.found_timing = True
            last_start_time = captions[-1].start if captions else 0
            state.start, state.end, state.layout_info = self._read_timing(
                line, line_index, last_start_time
            )
            return

        if line == "" and state.found_timing and state.nodes:
            self._finalize_cue(state, captions)
            return

        if state.found_timing and line != "":
            if state.nodes:
                state.nodes.append(CaptionNode.create_break())
            state.nodes.extend(self._parse_cue_text(line, state.open_tags))

    @staticmethod
    def _check_block_start(line, state):
        """Detect the start of a NOTE or STYLE block before any cue.

        :returns: True if the line starts a block (and state was updated).
        """
        if state.found_timing:
            return False
        if _is_note_start(line):
            state.in_note_block = True
            return True
        if line.strip() == "STYLE":
            state.in_style_block = True
            return True
        return False

    def _finalize_cue(self, state, captions):
        """Close the current cue, append it to captions, and reset state
        for the next cue."""
        state.found_timing = False
        captions.append(
            self._build_cue(
                state.nodes,
                state.open_tags,
                state.start,
                state.end,
                state.layout_info,
            )
        )
        state.nodes = []
        state.open_tags = []

    def _read_timing(self, line, line_index, last_start_time):
        """Parse a timing line, re-raising errors with line number context.

        :returns: Tuple of (start_us, end_us, Layout or None).
        """
        try:
            return self._parse_timing_line(line, last_start_time)
        except CaptionReadError as e:
            new_msg = f"{e.args[0]} (line {line_index})"
            tb = sys.exc_info()[2]
            raise type(e)(new_msg).with_traceback(tb) from None

    def _build_cue(self, nodes, open_tags, start, end, layout_info):
        """Assemble a Caption from accumulated nodes.

        Closes any unclosed tags and checks for viewport overflow.

        :returns: Caption instance.
        """
        self._close_unclosed_tags(nodes, open_tags)
        caption = Caption(start, end, nodes, layout_info=layout_info)
        self._check_line_overflow(caption)
        return caption

    @staticmethod
    def _check_line_overflow(caption):
        """Emit a CaptionReadWarning if a multiline cue's line:%
        positioning would place text partially outside the viewport.

        Estimates using WebVTT's 15-line grid (~6.67vh per line).
        """
        layout = caption.layout_info
        if not layout or not layout.origin:
            return
        origin_y = layout.origin.y
        if origin_y is None or origin_y.unit != UnitEnum.PERCENT:
            return
        line_pct = origin_y.value
        if line_pct <= 0:
            return
        num_lines = sum(1 for n in caption.nodes if n.type_ == CaptionNode.BREAK) + 1
        line_height = 100.0 / LINE_GRID_SIZE
        if line_pct + num_lines * line_height > 100.0:
            warnings.warn(
                f"Cue at {caption.format_start()} has line:{line_pct:.0f}% "
                f"with {num_lines} lines — extends beyond viewport.",
                CaptionReadWarning,
                stacklevel=4,
            )

    @staticmethod
    def _validate_timings(start, end, last_start_time):
        """Enforce WebVTT timing constraints: valid timestamps,
        end > start, and monotonically non-decreasing start times.

        :raises CaptionReadSyntaxError: On invalid/missing timestamps.
        :raises CaptionReadError: On inverted or non-monotonic timings.
        """
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
        """Parse a complete timing line (timestamps + optional cue settings).

        :param line: Raw timing line, e.g.
            "00:00:01.000 --> 00:00:05.000 line:80%"
        :param last_start_time: Start time of previous cue (for validation).
        :returns: Tuple of (start_us, end_us, Layout or None).
        :raises CaptionReadSyntaxError: On unparseable timing format.
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
            region = self._regions.get(region_id) if region_id else None
            layout_info = self._parse_cue_settings(cue_settings, inherit_from=region)

        return start, end, layout_info

    @staticmethod
    def _parse_timestamp(timestamp):
        """Convert a WebVTT timestamp string to microseconds.

        Accepts both HH:MM:SS.mmm and MM:SS.mmm formats.

        :param timestamp: e.g. "00:01:23.456" or "01:23.456"
        :returns: Integer microseconds.
        :raises CaptionReadSyntaxError: On invalid format.
        """
        m = TIMESTAMP_PATTERN.search(timestamp)
        if not m:
            raise CaptionReadSyntaxError("Invalid timing format.")

        m = m.groups()

        if m[2]:
            return microseconds(m[0], m[1], m[2].replace(":", ""), m[3])
        else:
            return microseconds(0, m[0], m[1], m[3])

    def _parse_cue_text(self, line, open_tags=None):
        """Parse a single line of WebVTT cue text into CaptionNodes.

        Splits on angle-bracket tags, converting recognized tags into
        STYLE open/close nodes, timestamp tags into timestamp STYLE nodes,
        and unrecognized tags (e.g. "<LAUGHING>") into literal TEXT nodes.
        Voice spans are flattened to "Speaker: " text prefixes.

        :param line: Raw cue text line.
        :param open_tags: Mutable stack tracking unclosed tags across
            lines within a cue (for auto-close at cue end).
        :returns: List of CaptionNode.
        """
        line = line.strip()
        line = VOICE_SPAN_PATTERN.sub(r"\2: ", line)

        nodes = []
        # re.split() with a capturing group produces alternating segments:
        # even indices = text, odd indices = captured tag strings.
        parts = TAG_SPLIT_PATTERN.split(line)

        for i, part in enumerate(parts):
            if not part:
                continue

            if i % 2 == 0:
                text = self._decode_entities(part)
                if text:
                    nodes.append(CaptionNode.create_text(text))
            else:
                node = self._classify_tag(part)
                if node is not None:
                    nodes.append(node)
                    self._track_open_tag(node, open_tags)

        return nodes

    @staticmethod
    def _track_open_tag(node, open_tags):
        """Update the open-tag stack when a STYLE node is emitted.

        Opening tags push; closing tags pop the most recent match.
        Timestamp nodes are excluded from tracking.
        """
        if open_tags is None or node.type_ != CaptionNode.STYLE:
            return
        if "timestamp" in node.content:
            return
        if node.start:
            open_tags.append(node.content)
        else:
            WebVTTReader._pop_matching_tag(open_tags, node.content)

    @staticmethod
    def _pop_matching_tag(open_tags, content):
        """Remove the most recent matching open tag from the stack.

        Matches by key set (e.g. {"classes"}) rather than full dict
        equality, because closing tags lack the opener's value
        (</c> produces {'classes': []} vs <c.yellow> {'classes': ['yellow']}).
        """
        keys = set(content.keys())
        for j in range(len(open_tags) - 1, -1, -1):
            if set(open_tags[j].keys()) == keys:
                open_tags.pop(j)
                break

    @staticmethod
    def _close_unclosed_tags(nodes, open_tags):
        """Emit closing STYLE nodes for tags left open at cue end.

        Per W3C WebVTT spec, unclosed tags are implicitly closed at
        cue boundaries. Closing order is reverse of opening (LIFO).
        """
        for content in reversed(open_tags):
            nodes.append(CaptionNode.create_style(False, content))

    def _classify_tag(self, tag_str):
        """Route a captured tag string to the appropriate CaptionNode type.

        - Recognized closing tags (e.g. "</i>") → STYLE close node
        - Timestamp tags (e.g. "<00:01:23.456>") → STYLE timestamp node
        - Recognized opening tags (e.g. "<c.yellow>") → STYLE open node
        - Unrecognized (e.g. "<LAUGHING>") → TEXT node (preserves content)

        :param tag_str: Raw tag with angle brackets, e.g. "<i>", "</b>".
        :returns: CaptionNode, or None if the tag produces no output.
        """
        inner = tag_str[1:-1]

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

        m = TIMESTAMP_PATTERN.match(inner)
        if m:
            groups = m.groups()
            if groups[2] is not None:
                secs = groups[2].replace(":", "")
                us = microseconds(groups[0], groups[1], secs, groups[3])
            else:
                us = microseconds(0, groups[0], groups[1], groups[3])
            return CaptionNode.create_style(True, {"timestamp": us})

        tag_name, class_suffix, annotation = self._parse_opening_tag(inner)
        if tag_name in KNOWN_TAGS:
            content = self._tag_content(tag_name, class_suffix, annotation)
            return CaptionNode.create_style(True, content)

        text = self._decode_entities(tag_str)
        return CaptionNode.create_text(text)

    @staticmethod
    def _parse_opening_tag(inner):
        """Decompose an opening tag's inner text into components.

        Examples:
            "i"        → ("i", None, None)
            "c.yellow" → ("c", "yellow", None)
            "c.a.b"   → ("c", "a.b", None)
            "lang en"  → ("lang", None, "en")

        :param inner: Tag content without angle brackets.
        :returns: Tuple of (tag_name, class_suffix, annotation).
        """
        if " " in inner:
            tag_part, annotation = inner.split(" ", 1)
        else:
            tag_part, annotation = inner, None

        if "." in tag_part:
            tag_name, class_suffix = tag_part.split(".", 1)
        else:
            tag_name, class_suffix = tag_part, None

        return tag_name, class_suffix, annotation

    @staticmethod
    def _tag_content(tag_name, class_suffix=None, annotation=None):
        """Build the internal style content dict for a recognized tag.

        Maps WebVTT tag names to pycaption's style representation:
        i→italics, b→bold, u→underline, c→classes list,
        lang→language, ruby/rt→ruby markers.

        :returns: Dict suitable for CaptionNode.create_style content.
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
        """Decode HTML character entities (e.g. &amp; → &, &#x27; → ').

        :param text: Raw text possibly containing HTML entities.
        :returns: Decoded string.
        """
        return html.unescape(text)

    def _parse_regions(self, lines):
        """Parse all REGION blocks from the file header area.

        Scans lines before the first cue, collecting REGION definitions.
        Skips NOTE blocks encountered along the way.

        :returns: Tuple of (regions_layout, regions_raw) where:
            - regions_layout: {id: Layout} for cue setting inheritance
            - regions_raw: {id: {key: value}} for writer round-trip
        """
        regions_layout = {}
        regions_raw = {}
        in_note_block = False
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if in_note_block:
                in_note_block = line != ""
                i += 1
                continue
            if _is_note_start(line):
                in_note_block = True
                i += 1
                continue
            if line == "REGION" or line.startswith(("REGION\t", "REGION ")):
                i = self._collect_region_block(
                    lines, i + 1, regions_layout, regions_raw
                )
            elif "-->" in line:
                break
            else:
                i += 1
        return regions_layout, regions_raw

    def _collect_region_block(self, lines, i, regions_layout, regions_raw):
        """Parse a single REGION block's key:value settings.

        Reads lines starting at index i until a blank line is reached,
        then registers the region if it has a valid, unique id.

        :returns: Updated line index (past the blank line).
        """
        settings = {}
        while i < len(lines) and lines[i].strip() != "":
            m = REGION_SETTING_PATTERN.match(lines[i].strip())
            if m:
                settings.setdefault(m.group(1), m.group(2))
            i += 1
        self._register_region(settings, regions_layout, regions_raw)
        return i

    def _register_region(self, settings, regions_layout, regions_raw):
        """Store a parsed region if it has a valid id not already registered.

        Converts settings to a Layout (for inheritance) and preserves
        the raw settings dict (for the writer to reproduce REGION blocks).
        """
        region_id = settings.get("id")
        if not region_id or region_id in regions_layout:
            return
        regions_layout[region_id] = self._region_to_layout(settings)
        regions_raw[region_id] = {k: v for k, v in settings.items() if k != "id"}

    @staticmethod
    def _region_to_layout(settings):
        """Convert region settings into a Layout with origin and extent.

        Applies W3C WebVTT region positioning formulas:
            origin_x = viewportanchor_x - (regionanchor_x / 100 * width)
            origin_y = viewportanchor_y - (regionanchor_y / 100 * height)
            height = lines * LINE_HEIGHT_VH (~5.33vh per line)

        Defaults per W3C WebVTT §6: width=100%, lines=3,
        regionanchor=0%,100%, viewportanchor=0%,100%.

        :param settings: Dict of region key:value pairs.
        :returns: Layout with origin (top-left corner) and extent.
        """
        width = 100.0
        lines = 3
        regionanchor_x, regionanchor_y = 0.0, 100.0
        viewportanchor_x, viewportanchor_y = 0.0, 100.0

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

        if "regionanchor" in settings:
            m = REGION_ANCHOR_PATTERN.match(settings["regionanchor"])
            if m:
                regionanchor_x = float(m.group(1))
                regionanchor_y = float(m.group(2))

        if "viewportanchor" in settings:
            m = REGION_ANCHOR_PATTERN.match(settings["viewportanchor"])
            if m:
                viewportanchor_x = float(m.group(1))
                viewportanchor_y = float(m.group(2))

        height = lines * LINE_HEIGHT_VH
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

        return Layout(origin=origin, extent=extent)

    @staticmethod
    def _extract_region_id(cue_settings):
        """Extract the region:id value from a cue settings string.

        :returns: Region id string, or None if not present.
        """
        for setting in cue_settings.split():
            if setting.startswith("region:"):
                return setting[7:]
        return None

    @staticmethod
    def _parse_percent_value(value):
        """Parse a percentage string (e.g. "50%") into a Size.

        :returns: Size with UnitEnum.PERCENT, or None if invalid.
        """
        if not value.endswith("%"):
            return None
        try:
            return Size(float(value[:-1]), UnitEnum.PERCENT)
        except ValueError:
            return None

    @staticmethod
    def _line_number_to_percent(value):
        """Convert an integer line number to viewport percentage.

        Uses a 15-line grid. Positive values count from top (0=0%),
        negative values count from bottom (-1=last line).

        :param value: String representation of an integer line number.
        :returns: Float percentage (0-100), or None if not a valid int.
        """
        try:
            line_num = int(value)
        except ValueError:
            return None

        if line_num >= 0:
            return min(line_num / LINE_GRID_SIZE * 100, 100.0)
        else:
            return max(
                (LINE_GRID_SIZE + line_num) / LINE_GRID_SIZE * 100,
                0.0,
            )

    @staticmethod
    def _parse_cue_settings(cue_settings, inherit_from=None):
        """Parse a cue settings string into a Layout object.

        Handles: line, position, size, align, vertical, region.
        Preserves the raw settings string in webvtt_positioning for
        lossless VTT→VTT round-trip.

        :param cue_settings: Raw settings string after the timing arrow.
        :param inherit_from: Layout from a referenced REGION to inherit.
        :returns: Layout with parsed positioning values.
        """
        parsed = {}
        for match in CUE_SETTING_PATTERN.finditer(cue_settings):
            name, value = match.group(1), match.group(2)
            parsed[name] = value

        origin_x = WebVTTReader._parse_percent_value(parsed.get("position", ""))
        origin_y = WebVTTReader._parse_line_value(parsed.get("line", ""))
        extent_horizontal = WebVTTReader._parse_percent_value(parsed.get("size", ""))
        alignment = WebVTTReader._parse_align_value(parsed.get("align", ""))
        writing_direction = WebVTTReader._parse_vertical_value(
            parsed.get("vertical", "")
        )

        origin = None
        if origin_y is not None:
            x = origin_x if origin_x is not None else Size(0, UnitEnum.PERCENT)
            origin = Point(x, origin_y)

        extent = None
        if extent_horizontal is not None:
            extent = Stretch(extent_horizontal, Size(100, UnitEnum.PERCENT))

        return Layout(
            origin=origin,
            extent=extent,
            alignment=alignment,
            writing_direction=writing_direction,
            webvtt_positioning=cue_settings,
            inherit_from=inherit_from,
        )

    @staticmethod
    def _parse_line_value(value):
        """Parse the line setting as either a percentage or integer.

        Tries percentage first (e.g. "80%"), then integer line number
        (converted to percentage via the 15-line grid).

        :returns: Size with UnitEnum.PERCENT, or None if invalid/empty.
        """
        if not value:
            return None
        result = WebVTTReader._parse_percent_value(value)
        if result is not None:
            return result
        pct = WebVTTReader._line_number_to_percent(value)
        if pct is not None:
            return Size(pct, UnitEnum.PERCENT)
        return None

    @staticmethod
    def _parse_align_value(value):
        """Map an align setting string to an Alignment object.

        :param value: One of "start", "center", "end", "left", "right".
        :returns: Alignment, or None if value is unrecognized/empty.
        """
        if value in ALIGN_SETTING_MAP:
            return Alignment(ALIGN_SETTING_MAP[value], None)
        return None

    @staticmethod
    def _parse_vertical_value(value):
        """Map a vertical setting to a WritingDirectionEnum.

        :param value: "rl" (right-to-left) or "lr" (left-to-right).
        :returns: WritingDirectionEnum, or None if not vertical.
        """
        if value == "rl":
            return WritingDirectionEnum.VERTICAL_RL
        if value == "lr":
            return WritingDirectionEnum.VERTICAL_LR
        return None

    def _parse_style_blocks(self, lines):
        """Extract and parse all STYLE blocks from the header area.

        Collects CSS text, then parses ::cue and ::cue(.class) selectors
        into a styles dict. Tag selectors (::cue(b)) are skipped.

        :returns: Dict mapping selector keys to property dicts, e.g.
            {"::cue": {"italics": True}, "yellow": {"color": "yellow"}}.
            Empty dict if no STYLE blocks found.
        """
        styles = {}
        blocks = self._collect_style_blocks(lines)
        for css_text in blocks:
            self._extract_cue_styles(css_text, styles)

        if styles and self._CUE_SELECTOR not in styles:
            styles[self._CUE_SELECTOR] = {}

        return styles

    @staticmethod
    def _collect_style_blocks(lines):
        """Collect raw CSS text from each STYLE block in the header.

        Stops at the first timing line (-->), as STYLE blocks are only
        valid before cues per the WebVTT spec.

        :returns: List of CSS text strings (one per STYLE block).
        """
        blocks = []
        in_style_block = False
        in_note_block = False
        css_lines = []

        for line in lines:
            if in_note_block:
                in_note_block = line != ""
                continue

            if in_style_block:
                if line != "":
                    css_lines.append(line)
                    continue
                _flush_css_block(css_lines, blocks)
                css_lines = []
                in_style_block = False
                continue

            if _is_note_start(line):
                in_note_block = True
            elif "-->" in line:
                break
            elif line.strip() == "STYLE":
                in_style_block = True
                css_lines = []

        if in_style_block:
            _flush_css_block(css_lines, blocks)

        return blocks

    @staticmethod
    def _extract_cue_styles(css_text, styles):
        """Parse ::cue rules from a CSS text block into the styles dict.

        Supports bare ::cue (global) and ::cue(.className) selectors.
        Tag selectors like ::cue(b) are skipped since pycaption
        represents tag styling via inline STYLE nodes instead.

        :param css_text: Raw CSS from a STYLE block.
        :param styles: Accumulator dict (mutated in place).
        """
        for match in STYLE_SELECTOR_PATTERN.finditer(css_text):
            selector_inner = match.group(1)
            declarations = match.group(2)

            if selector_inner is None:
                key = WebVTTReader._CUE_SELECTOR
            elif selector_inner.startswith("."):
                key = selector_inner[1:]
            else:
                continue

            props = WebVTTReader._parse_css_declarations(declarations)
            if props:
                if key in styles:
                    styles[key].update(props)
                else:
                    styles[key] = props

    @staticmethod
    def _parse_css_declarations(declarations):
        """Parse CSS declaration text into pycaption's style dict.

        Only maps properties pycaption can represent: font-style,
        font-weight, text-decoration, color, background-color.
        All other properties are silently ignored.

        :param declarations: CSS declarations string (between braces).
        :returns: Dict of recognized style properties.
        """
        props = {}
        for declaration in declarations.split(";"):
            declaration = declaration.strip()
            if not declaration or ":" not in declaration:
                continue
            prop_name, _, prop_value = declaration.partition(":")
            prop_name = prop_name.strip().lower()
            prop_value = prop_value.strip()
            if not prop_value:
                continue

            if prop_name == "font-style" and prop_value == "italic":
                props["italics"] = True
            elif prop_name == "font-weight" and prop_value in ("bold", "700"):
                props["bold"] = True
            elif prop_name == "text-decoration" and "underline" in prop_value:
                props["underline"] = True
            elif prop_name == "color":
                props["color"] = prop_value
            elif prop_name == "background-color":
                props["background-color"] = prop_value

        return props

    @staticmethod
    def _resolve_cue_styles(captions, styles):
        """Cascade STYLE block declarations into the caption node tree.

        Two-phase resolution:
        1. Merge ::cue base + class-specific styles onto STYLE open nodes.
        2. Wrap bare text with base style if ::cue declares italic/bold/underline.
        """
        if not styles:
            return

        base_style = styles.get(WebVTTReader._CUE_SELECTOR, {})
        WebVTTReader._cascade_class_styles(captions, styles, base_style)
        WebVTTReader._wrap_bare_text_with_base(captions, base_style)

    @staticmethod
    def _cascade_class_styles(captions, styles, base_style):
        """Apply cascaded ::cue base and class styles onto STYLE open
        nodes that carry class selectors."""
        for caption in captions:
            for node in caption.nodes:
                if node.type_ != CaptionNode.STYLE or not node.start:
                    continue
                WebVTTReader._apply_cascade(node.content, styles, base_style)

    @staticmethod
    def _apply_cascade(content, styles, base_style):
        """Merge base and class-resolved styles into a node's content dict.

        Resolution order: base (::cue) → each class in order. Existing
        keys in content are not overwritten (inline > cascade).

        :param content: The STYLE node's content dict (mutated in place).
        :param styles: Full styles dict with class entries.
        :param base_style: The ::cue base properties.
        """
        classes = content.get("classes", [])
        if not classes and not base_style:
            return

        resolved = {}
        if base_style:
            resolved.update(base_style)
        for class_name in classes:
            class_style = styles.get(class_name, {})
            if class_style:
                resolved.update(class_style)

        for key, value in resolved.items():
            if key not in content:
                content[key] = value

    @staticmethod
    def _wrap_bare_text_with_base(captions, base_style):
        """Wrap captions containing unstyled text with ::cue base styles.

        Only applies when ::cue declares text-formatting properties
        (italic/bold/underline). Inserts synthetic STYLE open/close
        nodes around the entire caption content.

        :param captions: CaptionList to process.
        :param base_style: The ::cue base properties dict.
        """
        text_style_keys = {"italics", "bold", "underline"}
        base_text_props = {
            k: v for k, v in base_style.items() if k in text_style_keys and v
        }
        if not base_text_props:
            return

        for caption in captions:
            if not WebVTTReader._caption_needs_base_wrap(
                caption.nodes, base_text_props
            ):
                continue
            caption.nodes.insert(
                0, CaptionNode.create_style(True, dict(base_text_props))
            )
            caption.nodes.append(CaptionNode.create_style(False, dict(base_text_props)))

    @staticmethod
    def _caption_needs_base_wrap(nodes, base_props):
        """Return True if any TEXT node exists outside a STYLE scope
        that already provides the base properties.

        Tracks nesting depth of qualifying STYLE openers. A TEXT node
        at depth 0 means it's not covered and the caption needs wrapping.
        """
        depth = 0
        for node in nodes:
            if node.type_ == CaptionNode.TEXT and depth == 0:
                return True
            if node.type_ != CaptionNode.STYLE:
                continue
            if node.start and _covers_base(node.content, base_props):
                depth += 1
            elif not node.start and depth > 0:
                depth -= 1
        return False
