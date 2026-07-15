import datetime
from copy import deepcopy

from ..base import BaseWriter, CaptionNode
from ..geometry import WritingDirectionEnum
from .constants import DEFAULT_ALIGN, WEBVTT_VERSION_OF

_SIMPLE_STRUCTURAL_TAGS = {
    "ruby": ("<ruby>", "</ruby>"),
    "ruby_text": ("<rt>", "</rt>"),
}


class WebVTTWriter(BaseWriter):
    HEADER = "WEBVTT\n\n"

    _INTERNAL_STYLE_KEYS = frozenset(
        {
            "lang",
            "italics",
            "bold",
            "underline",
            "class",
            "classes",
        }
    )
    _INTERNAL_TO_CSS = {
        "italics": ("font-style", "italic"),
        "bold": ("font-weight", "bold"),
        "underline": ("text-decoration", "underline"),
    }
    _CUE_SELECTOR = "::cue"
    _HTML_ELEMENT_NAMES = frozenset(
        {
            "p",
            "span",
            "sync",
            "body",
            "div",
        }
    )

    def write(self, caption_set, lang=None):
        """
        :type caption_set: CaptionSet
        :type lang: str
        """
        output = self.HEADER

        if caption_set.is_empty():
            return output

        caption_set = deepcopy(caption_set)

        if lang is None:
            lang = caption_set.get_languages()[0]

        captions = caption_set.get_captions(lang)
        self._roll_up_region_map = self._inject_scroll_regions(
            captions, caption_set
        )

        style_block = self._build_style_block(caption_set)
        if style_block:
            output += style_block

        region_blocks = self._build_region_blocks(caption_set)
        if region_blocks:
            output += region_blocks

        self.global_layout = caption_set.get_layout_info(lang)

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

    def _build_style_block(self, caption_set):
        """Build a STYLE section from the CaptionSet's styles.

        Only emits styles that originated from a WebVTT STYLE block.
        The reader always stores a '::cue' key (even if empty) when a
        STYLE block is parsed — its presence reliably signals VTT origin.
        """
        styles = caption_set.get_styles()
        if not styles:
            return ""

        style_dict = dict(styles)
        if self._CUE_SELECTOR not in style_dict:
            return ""

        global_rule = style_dict[self._CUE_SELECTOR] or None
        class_rules = self._collect_class_rules(styles)

        global_css = self._format_css_declarations(global_rule) if global_rule else ""
        class_outputs = [
            (name, css) for name, props in class_rules
            if (css := self._format_css_declarations(props))
        ]

        if not global_css and not class_outputs:
            return ""

        output = "STYLE\n"
        if global_css:
            output += f"{self._CUE_SELECTOR} {{ {global_css} }}\n"
        for class_name, css in class_outputs:
            output += f"::cue(.{class_name}) {{ {css} }}\n"
        output += "\n"
        return output

    def _collect_class_rules(self, styles):
        """Filter styles to only class-based rules suitable for STYLE output."""
        rules = []
        for key, props in styles:
            if key == self._CUE_SELECTOR or key.startswith("::"):
                continue
            if key in self._HTML_ELEMENT_NAMES:
                continue
            if "lang" in props:
                continue
            if props:
                rules.append((key, props))
        return rules

    @staticmethod
    def _inject_scroll_regions(captions, caption_set):
        """Create REGION blocks for roll-up captions that lack one.

        Returns a dict mapping roll_up_rows depth -> region id for use
        by _convert_caption when emitting cue settings.
        """
        existing_regions = caption_set.get_regions()
        depth_to_region = {}
        for cap in captions:
            if getattr(cap, "caption_mode", None) != "roll_up":
                continue
            depth = getattr(cap, "roll_up_rows", None) or 3
            if depth in depth_to_region:
                continue
            region_id = f"scroll{depth}"
            if region_id not in existing_regions:
                existing_regions[region_id] = {
                    "lines": str(depth),
                    "scroll": "up",
                }
            depth_to_region[depth] = region_id
        if existing_regions:
            caption_set.set_regions(existing_regions)
        return depth_to_region

    @staticmethod
    def _build_region_blocks(caption_set):
        """Build REGION blocks from the raw settings stored by the reader.

        Reconstructs the original REGION text so that cue settings like
        region:r1 remain valid references in the output.
        """
        regions = caption_set.get_regions()
        if not regions:
            return ""
        output = ""
        for region_id, settings in regions.items():
            output += "REGION\n"
            output += f"id:{region_id}\n"
            for key, value in settings.items():
                output += f"{key}:{value}\n"
            output += "\n"
        return output

    @classmethod
    def _format_css_declarations(cls, props):
        """Format a style dict as a CSS declaration string.

        Reverses internal keys (italics → font-style: italic) and
        skips non-CSS keys (classes, class, lang).
        """
        declarations = []
        for k, v in sorted(props.items()):
            if k in cls._INTERNAL_TO_CSS:
                css_prop, css_val = cls._INTERNAL_TO_CSS[k]
                declarations.append(f"{css_prop}: {css_val}")
            elif k not in cls._INTERNAL_STYLE_KEYS:
                declarations.append(f"{k}: {v}")
        return "; ".join(declarations)

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

        region_suffix = self._get_roll_up_region_setting(caption)

        for cue_text, layout in layout_groups:
            if not layout:
                layout = caption.layout_info or self.global_layout
            cue_settings = self._convert_positioning(layout) + region_suffix
            output += timespan + cue_settings + "\n"
            output += cue_style_tags[0] + cue_text + cue_style_tags[1] + "\n"

        return output

    def _get_roll_up_region_setting(self, caption):
        if getattr(caption, "caption_mode", None) != "roll_up":
            return ""
        depth = getattr(caption, "roll_up_rows", None) or 3
        region_id = self._roll_up_region_map.get(depth)
        if region_id:
            return f" region:{region_id}"
        return ""

    def _convert_positioning(self, layout):
        """
        Return WebVTT cue settings string based on layout info
        :type layout: Layout
        :rtype: str
        """
        if not layout:
            return ""

        if layout.webvtt_positioning:
            return f" {layout.webvtt_positioning}"

        resolved = self._resolve_layout(layout)
        if resolved is None:
            return ""

        left_offset = resolved.origin.x if resolved.origin else None
        top_offset = resolved.origin.y if resolved.origin else None
        cue_width = resolved.extent.horizontal if resolved.extent else None

        left_offset, top_offset, cue_width = self._apply_padding(
            resolved.padding, left_offset, top_offset, cue_width
        )

        return self._format_cue_settings(resolved, left_offset, top_offset, cue_width)

    def _resolve_layout(self, layout):
        """Normalize layout to relative percentages. Returns None if
        the writer is configured not to relativize absolute values."""
        already_relative = False
        if not self.relativize:
            if layout.is_relative():
                already_relative = True
            else:
                return None

        if not already_relative:
            layout = layout.as_percentage_of(self.video_width, self.video_height)

        if self.fit_to_screen:
            layout = layout.fit_to_screen()

        return layout

    @staticmethod
    def _apply_padding(padding, left_offset, top_offset, cue_width):
        """Fold padding into offset/width since WebVTT has no padding."""
        if not padding:
            return left_offset, top_offset, cue_width

        if padding.start and left_offset:
            left_offset += padding.start
            if cue_width:
                cue_width -= padding.start

        if padding.end and cue_width:
            cue_width -= padding.end

        if padding.before and top_offset:
            top_offset += padding.before

        return left_offset, top_offset, cue_width

    @staticmethod
    def _format_cue_settings(layout, left_offset, top_offset, cue_width):
        """Build the cue settings string from resolved values."""
        if layout.alignment:
            alignment = WEBVTT_VERSION_OF.get(
                layout.alignment.horizontal, DEFAULT_ALIGN
            )
        else:
            alignment = DEFAULT_ALIGN

        cue_settings = ""
        if (
            layout.writing_direction
            and layout.writing_direction != WritingDirectionEnum.HORIZONTAL
        ):
            cue_settings += f" vertical:{layout.writing_direction.value}"
        if alignment and alignment != "center":
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
        layout_groups = []
        s = ""

        for i, node in enumerate(nodes):
            if node.type_ == CaptionNode.TEXT:
                if s and current_layout and node.layout_info != current_layout:
                    layout_groups.append((s, current_layout))
                    s = ""
                s += self._encode_illegal_characters(node.content) or "&nbsp;"
                current_layout = node.layout_info
            elif node.type_ == CaptionNode.STYLE:
                s += self._render_style_node(node, caption_set)
            elif node.type_ == CaptionNode.BREAK:
                s += self._render_break_node(nodes, i)

        if s:
            layout_groups.append((s, current_layout))
        return layout_groups

    def _render_style_node(self, node, caption_set):
        """Convert a STYLE node into WebVTT text (inline tags or structural)."""
        resulting_style = self._calculate_resulting_style(
            node.content, caption_set
        )

        # VTT <c.class> nodes have "classes" but not "class".
        # Preserve them as structural tags even if they carry
        # resolved text-style properties from STYLE blocks.
        is_vtt_class_span = (
            "classes" in node.content and "class" not in node.content
        )

        if not is_vtt_class_span:
            text_tags = self._emit_text_style_tags(resulting_style, node.start)
            if text_tags:
                return text_tags

        return self._convert_structural_tag(node.content, node.start)

    def _emit_text_style_tags(self, resulting_style, is_start):
        """Emit <i>/<u>/<b> open or close tags for active text styles."""
        styles = ["italics", "underline", "bold"]
        if not is_start:
            styles.reverse()

        output = ""
        for style in styles:
            if resulting_style.get(style):
                tags = self._convert_style_to_text_tag(style)
                output += tags[0] if is_start else tags[1]
        return output

    @staticmethod
    def _render_break_node(nodes, i):
        """Convert a BREAK node, prepending &nbsp; if needed."""
        s = ""
        if i == 0 or nodes[i - 1].type_ != CaptionNode.TEXT:
            s += "&nbsp;"
        s += "\n"
        return s

    @staticmethod
    def _encode_illegal_characters(s):
        """Escape characters illegal in WebVTT cue text."""
        s = s.replace("&", "&amp;")
        s = s.replace("<", "&lt;")
        s = s.replace("-->", "--&gt;")
        return s

    def _convert_structural_tag(self, content, is_start):
        """Convert a structural style node back into a WebVTT tag string.

        Structural tags are WebVTT-specific (class, lang, ruby, timestamp).
        Other writers silently ignore these keys.
        """
        if "lang" in content:
            return self._lang_tag(content["lang"], is_start)
        if "classes" in content:
            return self._class_tag(content["classes"], is_start)
        for key, (open_tag, close_tag) in _SIMPLE_STRUCTURAL_TAGS.items():
            if key in content:
                return open_tag if is_start else close_tag
        if "timestamp" in content:
            return f"<{self._timestamp(content['timestamp'])}>" if is_start else ""
        return ""

    @staticmethod
    def _lang_tag(lang, is_start):
        if not is_start:
            return "</lang>"
        return f"<lang {lang}>" if lang else "<lang>"

    @staticmethod
    def _class_tag(classes, is_start):
        if not is_start:
            return "</c>"
        class_str = "." + ".".join(classes) if classes else ""
        return f"<c{class_str}>"
