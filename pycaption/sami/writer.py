"""SAMI caption writer.

Serializes pycaption CaptionSet objects into SAMI markup with CSS
stylesheets, sync-based timing, and multi-language support.
"""

from copy import deepcopy
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup

from ..base import BaseWriter, CaptionNode
from ..geometry import HorizontalAlignmentEnum
from ..utils import encode_leading_nbsp
from .constants import HORIZONTAL_ALIGNMENT_MAP, SAMI_BASE_MARKUP


_NON_CSS_KEYS = frozenset(
    {
        "classes",
        "class",
        "ruby",
        "ruby_text",
        "timestamp",
        "name",
        "sami_type",
        "lang",
        "webvtt_positioning",
        "writing_direction",
    }
)


class SAMIWriter(BaseWriter):
    """Writes a CaptionSet to SAMI markup."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._span_stack = []
        self._promote_center = False

    def write(self, caption_set, **kwargs):
        """Serialize a CaptionSet into a SAMI document string."""
        caption_set = deepcopy(caption_set)
        source_default = self._get_visual_alignment_default(caption_set)
        self._promote_center = source_default == HorizontalAlignmentEnum.CENTER
        sami = BeautifulSoup(SAMI_BASE_MARKUP, "lxml-xml")

        caption_set.layout_info = self._relativize_and_fit_to_screen(
            caption_set.layout_info
        )

        timelines = {}
        for lang in caption_set.get_languages():
            caption_set.set_layout_info(
                lang,
                self._relativize_and_fit_to_screen(caption_set.get_layout_info(lang)),
            )

            captions = caption_set.get_captions(lang)
            for caption in captions:
                caption.layout_info = self._relativize_and_fit_to_screen(
                    caption.layout_info
                )
                for node in caption.nodes:
                    node.layout_info = self._relativize_and_fit_to_screen(
                        node.layout_info
                    )
            cues = self._build_timeline(captions)
            if cues:
                timelines[lang] = cues

        self._recreate_syncs(sami, timelines, caption_set)

        stylesheet = self._recreate_stylesheet(caption_set)
        sami.find("style").append(stylesheet)

        a = sami.prettify(formatter=None).split("\n")
        caption_content = "\n".join(a[1:])
        return caption_content

    @staticmethod
    def _build_timeline(captions):
        """Return (start_ms, end_ms, caption) cues sorted by start.

        Zero-length cues are never on screen, so they are dropped.
        """
        cues = []
        for caption in captions:
            start = int(caption.start // 1000)
            end = int(caption.end // 1000)
            if end > start:
                cues.append((start, end, caption))
        cues.sort(key=lambda cue: cue[0])
        return cues

    def _recreate_syncs(self, sami, timelines, captions):
        """Append one <sync> per time at which any language's visible cues change.

        Overlapping cues of a language are merged: a <sync> repeats every cue
        of that language still on screen, so start times never decrease and
        no cue is cleared early.
        """
        times = sorted(
            {time for cues in timelines.values() for cue in cues for time in cue[:2]}
        )
        shown = {lang: [] for lang in timelines}
        pending = {lang: 0 for lang in timelines}

        for time in times:
            sync = None
            for lang, cues in timelines.items():
                active = [i for i in shown[lang] if cues[i][1] > time]
                while pending[lang] < len(cues) and cues[pending[lang]][0] <= time:
                    active.append(pending[lang])
                    pending[lang] += 1
                if active == shown[lang]:
                    continue
                shown[lang] = active

                if sync is None:
                    sync = sami.new_tag("sync", start=time)
                    sami.body.append(sync)

                if active:
                    for i in active:
                        sync.append(
                            self._recreate_p_tag(cues[i][2], sami, lang, captions)
                        )
                else:
                    # The blank takes the class of the next cue, or of the
                    # last cue once the language has no cues left.
                    upcoming = cues[min(pending[lang], len(cues) - 1)][2]
                    sync.append(
                        self._recreate_blank_tag(upcoming, sami, lang, captions)
                    )

    def _recreate_p_tag(self, caption, sami, lang, captions):
        """Build a <p> for a single caption with styling and alignment."""
        p = sami.new_tag("p")

        p_style = self._build_p_style(caption)

        if p_style:
            p["style"] = p_style

        p["class"] = self._recreate_p_lang(caption, lang, captions)
        p.string = encode_leading_nbsp(self._recreate_text(caption.nodes))

        return p

    def _build_p_style(self, caption):
        """Build the inline CSS style string for a <p> element."""
        parts = []
        for attr, value in self._recreate_style(caption.style).items():
            parts.append(f"{attr}:{value};")

        self._append_position_styles(caption.layout_info, parts)

        text_align = self._resolve_text_align(caption.layout_info)
        if text_align:
            parts.append(f"text-align:{text_align};")

        return "".join(parts)

    @staticmethod
    def _append_position_styles(layout_info, parts):
        """Append margin/width CSS from layout positioning."""
        if not layout_info:
            return

        if layout_info.origin:
            if layout_info.origin.x:
                parts.append(f"margin-left:{layout_info.origin.x};")
            if layout_info.origin.y:
                parts.append(f"margin-top:{layout_info.origin.y};")

        if layout_info.extent and layout_info.extent.horizontal:
            parts.append(f"width:{layout_info.extent.horizontal};")

    def _resolve_text_align(self, layout_info):
        """Return a CSS text-align value for the layout, or None to suppress.

        Uses self._promote_center (derived from CaptionSet.visual_alignment_default)
        to decide whether to emit explicit center alignment per RP 2052-10.
        """
        if not layout_info:
            return "center" if self._promote_center else None

        if not layout_info.alignment:
            return "center" if self._promote_center else None

        h = layout_info.alignment.horizontal
        if not h:
            return None

        return HORIZONTAL_ALIGNMENT_MAP.get(h)

    def _recreate_blank_tag(self, caption, sami, lang, captions):
        """Build an &nbsp; <p> that clears the language's previous caption."""
        p = sami.new_tag("p")
        p["class"] = self._recreate_p_lang(caption, lang, captions)
        p.string = "&nbsp;"

        return p

    @staticmethod
    def _recreate_p_lang(caption, lang, captions):
        """Return the CSS class for a <p> tag, preferring the language class."""
        try:
            if "lang" in captions.get_style(caption.style["class"]):
                return caption.style["class"]
        except KeyError:
            pass
        return lang

    def _recreate_stylesheet(self, caption_set):
        """Generate the CSS stylesheet block placed inside <style>."""
        stylesheet = "<!--"

        for attr, value in caption_set.get_styles():
            if value != {} and not attr.startswith("::"):
                stylesheet += self._recreate_style_block(
                    attr, value, caption_set.layout_info
                )

        for lang in caption_set.get_languages():
            lang_string = f"lang: {lang}"
            if lang_string not in stylesheet:
                stylesheet += self._recreate_style_block(
                    lang, {"lang": lang}, caption_set.get_layout_info(lang)
                )

        return stylesheet + "   -->"

    def _recreate_style_block(self, target, rules, layout_info):
        """Format a single CSS rule block (selector + properties) for the stylesheet."""
        if target not in ["p", "sync", "span"]:
            selector = f".{target}"
        else:
            selector = target

        sami_style = f"\n    {selector} {{\n    "

        rules = dict(rules)
        if layout_info and layout_info.padding:
            rules.update(
                {
                    "margin-top": str(layout_info.padding.before),
                    "margin-right": str(layout_info.padding.end),
                    "margin-bottom": str(layout_info.padding.after),
                    "margin-left": str(layout_info.padding.start),
                }
            )

        css_props = self._recreate_style(rules)
        if "lang" in rules:
            css_props["lang"] = rules["lang"]

        for attr, value in sorted(css_props.items()):
            sami_style += f" {attr}: {value};\n    "

        return sami_style + "}\n"

    def _recreate_text(self, caption):
        """Serialize caption nodes into an HTML text string with inline markup."""
        line = ""
        self._span_stack = []

        for node in caption:
            if node.type_ == CaptionNode.TEXT:
                line += escape(node.content) + " "
            elif node.type_ == CaptionNode.BREAK:
                line = line.rstrip() + "<br/>\n    "
            elif node.type_ == CaptionNode.STYLE:
                line = self._recreate_line_style(line, node)

        while self._span_stack:
            tag = self._span_stack.pop()
            if tag:
                line = line.rstrip() + f"</{tag}> "

        return line.rstrip()

    def _recreate_line_style(self, line, node):
        """Handle style node transitions, opening/closing inline markup."""
        if node.start:
            line = self._recreate_span(line, node.content)
        else:
            if self._span_stack:
                tag = self._span_stack.pop()
                if tag:
                    line = line.rstrip() + f"</{tag}> "

        return line

    @staticmethod
    def _get_semantic_tag(content):
        """Return a semantic HTML tag if content is a single style property."""
        keys = {k for k in content if k not in _NON_CSS_KEYS}
        if keys == {"italics"} and content.get("italics") is True:
            return "i"
        if keys == {"bold"} and content.get("bold") is True:
            return "b"
        if keys == {"underline"} and content.get("underline") is True:
            return "u"
        return None

    def _recreate_span(self, line, content):
        """Build an opening inline tag — semantic (<i>/<b>/<u>) when possible."""
        semantic = self._get_semantic_tag(content)
        if semantic:
            line += f"<{semantic}>"
            self._span_stack.append(semantic)
            return line

        style = ""
        klass = ""
        if "classes" in content and content["classes"]:
            klass += f' class="{" ".join(content["classes"])}"'
        elif "class" in content:
            klass += f' class="{content["class"]}"'

        for attr, value in self._recreate_style(content).items():
            style += f"{attr}:{value};"

        if style or klass:
            if style:
                style = f' style="{style}"'
            line += f"<span{klass}{style}>"
            self._span_stack.append("span")
        else:
            self._span_stack.append(None)

        return line

    @staticmethod
    def _recreate_style(rules):
        """Convert internal style keys to CSS property names, filtering non-CSS keys."""
        sami_style = {}

        for key, value in list(rules.items()):
            if key in _NON_CSS_KEYS:
                continue
            elif key == "italics" and value is True:
                sami_style["font-style"] = "italic"
            elif key == "bold" and value is True:
                sami_style["font-weight"] = "bold"
            elif key == "underline" and value is True:
                sami_style["text-decoration"] = "underline"
            else:
                sami_style[key] = value

        return sami_style
