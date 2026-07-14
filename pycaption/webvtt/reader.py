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


class WebVTTReader(BaseReader):
    def __init__(
        self, ignore_timing_errors=True, time_shift_milliseconds=0, *args, **kwargs
    ):
        """
        :param ignore_timing_errors: Whether to ignore timing checks
        :type ignore_timing_errors: bool
        :param time_shift_milliseconds: Move all the timestamps
        forward/backward with this number of milliseconds
        :type time_shift_milliseconds: int
        """
        self.ignore_timing_errors = ignore_timing_errors
        self.time_shift_microseconds = time_shift_milliseconds * 1000

    def detect(self, content):
        if content.startswith("﻿"):
            content = content[1:]
        first_line = content.splitlines()[0] if content.strip() else ""
        return (
            first_line == "WEBVTT"
            or first_line.startswith("WEBVTT ")
            or first_line.startswith("WEBVTT\t")
        )

    def read(self, content, lang="en-US"):
        if not isinstance(content, str):
            raise InvalidInputError("The content is not a unicode string.")

        if content.startswith("﻿"):
            content = content[1:]

        # str.splitlines() handles CR, LF, CRLF (RULE-FMT-005)
        lines = content.splitlines()
        self._validate_header(lines)
        styles = self._parse_style_blocks(lines)
        captions = self._parse(lines)
        self._resolve_cue_styles(captions, styles)
        # regions_raw carries the original REGION settings so the writer
        # can re-emit them (regions_layout is only used internally for
        # position inheritance during parsing).
        caption_set = CaptionSet(
            {lang: captions}, styles=styles, regions=self._regions_raw
        )

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    @staticmethod
    def _validate_header(lines):
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
        captions = CaptionList()
        start = None
        end = None
        nodes = []
        open_tags = []
        layout_info = None
        found_timing = False
        in_note_block = False
        in_style_block = False

        # Two dicts: _regions has computed Layouts (for inherit_from when
        # a cue references region:id), _regions_raw has the verbatim
        # key:value pairs (for the writer to reproduce REGION blocks).
        self._regions, self._regions_raw = self._parse_regions(lines)

        for i, line in enumerate(lines):
            if in_note_block:
                if line == "":
                    in_note_block = False
                continue

            if in_style_block:
                if line == "":
                    in_style_block = False
                continue

            if not found_timing and _is_note_start(line):
                in_note_block = True
                continue

            if not found_timing and line.strip() == "STYLE":
                in_style_block = True
                continue

            if "-->" in line:
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

            elif line == "":
                if found_timing and nodes:
                    found_timing = False
                    self._close_unclosed_tags(nodes, open_tags)
                    caption = Caption(start, end, nodes, layout_info=layout_info)
                    self._check_line_overflow(caption)
                    captions.append(caption)
                    nodes = []
                    open_tags = []
            else:
                if found_timing:
                    if nodes:
                        nodes.append(CaptionNode.create_break())
                    nodes.extend(self._parse_cue_text(line, open_tags))

        if nodes:
            self._close_unclosed_tags(nodes, open_tags)
            caption = Caption(start, end, nodes, layout_info=layout_info)
            self._check_line_overflow(caption)
            captions.append(caption)

        return captions

    @staticmethod
    def _check_line_overflow(caption):
        """Emit a warning if a multiline cue's line:% would place text
        partially off-screen.

        Uses WebVTT's 15-line grid (~6.67% per line) to estimate whether
        the cue's starting position plus its line count exceeds 100% of
        the viewport height.
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
        # BREAK nodes separate lines, so count + 1 = total lines
        num_lines = sum(1 for n in caption.nodes if n.type_ == CaptionNode.BREAK) + 1
        line_height = 100.0 / LINE_GRID_SIZE
        if line_pct + num_lines * line_height > 100.0:
            warnings.warn(
                f"Cue at {caption.format_start()} has line:{line_pct:.0f}% "
                f"with {num_lines} lines — extends beyond viewport.",
                CaptionReadWarning,
                stacklevel=4,
            )

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
        :returns: Tuple (int, int, Layout or None)
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

    def _parse_timestamp(self, timestamp):
        """Returns an integer representing a number of microseconds
        :rtype: int
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
        """Parse a single line of WebVTT cue text into a list of CaptionNodes.

        Converts inline markup tags into CaptionNode.STYLE open/close pairs
        and text content into CaptionNode.TEXT nodes.

        Voice tags are handled before splitting (baked into text as
        "Speaker: " prefix), matching the legacy behavior.

        :param line: A single line of cue text (raw WebVTT)
        :param open_tags: Mutable list tracking unclosed tag content dicts
            across lines within a cue. Callers pass the same list for each
            line so unclosed tags can be auto-closed at cue end.
        :returns: list of CaptionNode
        """
        line = line.strip()
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
                    if open_tags is not None and node.type_ == CaptionNode.STYLE:
                        if "timestamp" in node.content:
                            pass
                        elif node.start:
                            open_tags.append(node.content)
                        else:
                            self._pop_matching_tag(open_tags, node.content)

        return nodes

    @staticmethod
    def _pop_matching_tag(open_tags, content):
        """Remove the most recent matching open tag from the stack.

        Matches by tag-type key (e.g. "classes", "lang") rather than full
        dict equality, because closing tags lack the opener's value
        (</c> -> {'classes': []} vs <c.yellow> -> {'classes': ['yellow']}).
        """
        keys = set(content.keys())
        for j in range(len(open_tags) - 1, -1, -1):
            if set(open_tags[j].keys()) == keys:
                open_tags.pop(j)
                break

    @staticmethod
    def _close_unclosed_tags(nodes, open_tags):
        """Emit closing STYLE nodes for any tags left open at cue end.

        Per W3C WebVTT spec, unclosed tags are implicitly closed at the
        end of the cue. Closing order is reverse of opening (LIFO).
        """
        for content in reversed(open_tags):
            nodes.append(CaptionNode.create_style(False, content))

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
                us = microseconds(groups[0], groups[1], secs, groups[3])
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
        """Decode HTML character entities in a text segment.

        :type text: str
        :rtype: str
        """
        return html.unescape(text)

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

        :returns: tuple (regions_layout, regions_raw)
            regions_layout: dict mapping region id -> Layout (for inherit_from)
            regions_raw: dict mapping region id -> {key: value} (for writer)
        """
        regions_layout = {}
        regions_raw = {}
        in_note_block = False
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if in_note_block:
                if line == "":
                    in_note_block = False
                i += 1
                continue
            if _is_note_start(line):
                in_note_block = True
                i += 1
                continue
            if line == "REGION" or line.startswith(("REGION\t", "REGION ")):
                i += 1
                settings = {}
                seen_keys = set()
                while i < len(lines) and lines[i].strip() != "":
                    m = REGION_SETTING_PATTERN.match(lines[i].strip())
                    if m:
                        key, value = m.group(1), m.group(2)
                        if key in seen_keys:
                            i += 1
                            continue
                        seen_keys.add(key)
                        settings[key] = value
                    i += 1
                if "id" in settings:
                    region_id = settings["id"]
                    if region_id not in regions_layout:
                        regions_layout[region_id] = self._region_to_layout(settings)
                        # Store raw settings (minus id) for the writer to
                        # reconstruct the REGION block verbatim.
                        regions_raw[region_id] = {
                            k: v for k, v in settings.items() if k != "id"
                        }
            elif "-->" in line:
                break
            else:
                i += 1
        return regions_layout, regions_raw

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

        return Layout(origin=origin, extent=extent)

    @staticmethod
    def _extract_region_id(cue_settings):
        """Extract region id from cue settings string, if present."""
        for setting in cue_settings.split():
            if setting.startswith("region:"):
                return setting[7:]
        return None

    @staticmethod
    def _parse_percent_value(value):
        """Parse "50%" into a Size, or return None if invalid."""
        if not value.endswith("%"):
            return None
        try:
            return Size(float(value[:-1]), UnitEnum.PERCENT)
        except ValueError:
            return None

    @staticmethod
    def _line_number_to_percent(value):
        """Convert integer line number to viewport percentage
        using a 15-line grid."""
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
        """Parse cue settings string into a Layout object.

        Also preserves the raw string in webvtt_positioning for VTT round-trip.
        """
        origin_x = None
        origin_y = None
        extent_horizontal = None
        alignment = None
        writing_direction = None

        for match in CUE_SETTING_PATTERN.finditer(cue_settings):
            name, value = match.group(1), match.group(2)

            if name == "position":
                origin_x = WebVTTReader._parse_percent_value(value)

            elif name == "line":
                origin_y = WebVTTReader._parse_percent_value(value)
                if origin_y is None:
                    pct = WebVTTReader._line_number_to_percent(value)
                    if pct is not None:
                        origin_y = Size(pct, UnitEnum.PERCENT)

            elif name == "size":
                extent_horizontal = WebVTTReader._parse_percent_value(value)

            elif name == "align":
                if value in ALIGN_SETTING_MAP:
                    alignment = Alignment(ALIGN_SETTING_MAP[value], None)

            elif name == "vertical":
                if value == "rl":
                    writing_direction = WritingDirectionEnum.VERTICAL_RL
                elif value == "lr":
                    writing_direction = WritingDirectionEnum.VERTICAL_LR

        # Only create origin when line: is present — position: alone leaves
        # y unspecified (WebVTT default is "auto"/bottom, not 0%).
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

    def _parse_style_blocks(self, lines):
        """Extract ::cue rules from STYLE blocks before the first cue."""
        styles = {}
        in_style_block = False
        in_note_block = False
        css_text = ""

        for line in lines:
            if in_note_block:
                if line == "":
                    in_note_block = False
                continue
            if in_style_block:
                if line == "":
                    if css_text:
                        self._extract_cue_styles(css_text, styles)
                    in_style_block = False
                    css_text = ""
                else:
                    css_text += line + "\n"
            elif _is_note_start(line):
                in_note_block = True
            elif "-->" in line:
                break
            elif line.strip() == "STYLE":
                in_style_block = True
                css_text = ""

        if in_style_block and css_text:
            self._extract_cue_styles(css_text, styles)

        # Marker: signals to the writer that styles originated from VTT
        if styles and "::cue" not in styles:
            styles["::cue"] = {}

        return styles

    @staticmethod
    def _extract_cue_styles(css_text, styles):
        """Extract ::cue rules from CSS text into the styles dict.

        Tag selectors (::cue(b)) are skipped — only bare ::cue and
        class selectors (::cue(.name)) are supported.
        """
        for match in STYLE_SELECTOR_PATTERN.finditer(css_text):
            selector_inner = match.group(1)
            declarations = match.group(2)

            if selector_inner is None:
                key = "::cue"
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
        """Parse CSS declarations into pycaption's internal style dict.

        Only maps the 5 properties pycaption can represent; others are ignored.
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
        """Merge ::cue styles into STYLE nodes so all writers
        get resolved values."""
        if not styles:
            return

        base_style = styles.get("::cue", {})

        for caption in captions:
            for node in caption.nodes:
                if node.type_ != CaptionNode.STYLE or not node.start:
                    continue

                content = node.content
                classes = content.get("classes", [])
                if not classes and not base_style:
                    continue

                # Cascade: ::cue base < ::cue(.class)
                resolved = {}
                if base_style:
                    resolved.update(base_style)
                for class_name in classes:
                    class_style = styles.get(class_name, {})
                    if class_style:
                        resolved.update(class_style)

                # Preserve existing keys ("classes" needed for round-trip)
                if resolved:
                    for key, value in resolved.items():
                        if key not in content:
                            content[key] = value

        # Wrap bare text in STYLE nodes when a ::cue base rule has
        # text-decoration properties (italic/bold/underline). This ensures
        # downstream writers (SCC, DFXP, VTT) all see the styling — they
        # iterate caption.nodes looking for STYLE nodes to trigger
        # formatting. Only text-style keys are used; color/background-color
        # can't be represented as inline tags and stay in the STYLE block.
        _TEXT_STYLE_KEYS = {"italics", "bold", "underline"}
        base_text_props = {
            k: v for k, v in base_style.items() if k in _TEXT_STYLE_KEYS and v
        }
        if base_text_props:
            for caption in captions:
                if WebVTTReader._caption_needs_base_wrap(
                    caption.nodes, base_text_props
                ):
                    caption.nodes.insert(
                        0,
                        CaptionNode.create_style(True, dict(base_text_props)),
                    )
                    caption.nodes.append(
                        CaptionNode.create_style(False, dict(base_text_props))
                    )

    @staticmethod
    def _caption_needs_base_wrap(nodes, base_props):
        """Return True if any TEXT node is not fully covered by a STYLE
        opener carrying all base_props.

        Tracks a "depth" of open STYLE nodes that carry the required
        properties. A TEXT node at depth 0 means it's unstyled and needs
        wrapping. This avoids double-wrapping captions that are already
        entirely inside e.g. <i>...</i>.
        """
        depth = 0
        for node in nodes:
            if node.type_ == CaptionNode.STYLE:
                if node.start:
                    if all(node.content.get(k) == v for k, v in base_props.items()):
                        depth += 1
                else:
                    if depth > 0:
                        depth -= 1
            elif node.type_ == CaptionNode.TEXT and depth == 0:
                return True
        return False
