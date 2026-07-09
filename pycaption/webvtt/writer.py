import datetime
from copy import deepcopy

from ..base import BaseWriter, CaptionNode
from ..geometry import WritingDirectionEnum
from .constants import DEFAULT_ALIGN, WEBVTT_VERSION_OF


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

        style_block = self._build_style_block(caption_set)
        if style_block:
            output += style_block

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
        if "::cue" not in style_dict:
            return ""

        global_rule = style_dict["::cue"] or None
        class_rules = []

        for key, props in styles:
            if key == "::cue":
                continue
            elif key.startswith("::"):
                continue
            elif key in self._HTML_ELEMENT_NAMES:
                continue
            elif "lang" in props:
                continue
            elif self._has_internal_keys(props):
                continue
            elif props:
                class_rules.append((key, props))

        if not global_rule and not class_rules:
            return ""

        output = "STYLE\n"
        if global_rule:
            output += f"::cue {{ {self._format_css_declarations(global_rule)} }}\n"
        for class_name, css_props in class_rules:
            output += (
                f"::cue(.{class_name})"
                f" {{ {self._format_css_declarations(css_props)} }}\n"
            )
        output += "\n"
        return output

    def _has_internal_keys(self, props):
        """Check if a style dict contains pycaption-internal keys."""
        return bool(self._INTERNAL_STYLE_KEYS & props.keys())

    @staticmethod
    def _format_css_declarations(props):
        """Format a dict of CSS properties as a declaration string."""
        return "; ".join(f"{k}: {v}" for k, v in sorted(props.items()))

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

        if (
            layout.writing_direction
            and layout.writing_direction != WritingDirectionEnum.HORIZONTAL
        ):
            cue_settings += f" vertical:{layout.writing_direction.value}"
        # WebVTT spec default is "center" — omit to keep output minimal
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
                # VTT <c.class> nodes have "classes" but not "class".
                # Preserve them as structural tags even if they carry
                # resolved text-style properties from STYLE blocks.
                # DFXP nodes have both "classes" and "class" — those
                # should resolve to text tags (<i>, <b>, <u>).
                is_vtt_class_span = (
                    "classes" in node.content and "class" not in node.content
                )
                # VTT class spans (<c.yellow>) → structural tag
                if not is_vtt_class_span:
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
                    s += self._convert_structural_tag(node.content, node.start)
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
        # s = s.replace('‎', '&lrm;')
        # s = s.replace('‏', '&rlm;')
        # s = s.replace(' ', '&nbsp;')
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
