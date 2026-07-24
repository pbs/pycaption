"""SAMI caption writer.

Serializes pycaption CaptionSet objects into SAMI markup with CSS
stylesheets, sync-based timing, and multi-language support.
"""

from copy import deepcopy
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup

from ..base import BaseWriter, CaptionNode
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
        self.last_time = None

    def write(self, caption_set):
        """Serialize a CaptionSet into a SAMI document string."""
        caption_set = deepcopy(caption_set)
        sami = BeautifulSoup(SAMI_BASE_MARKUP, "lxml-xml")

        caption_set.layout_info = self._relativize_and_fit_to_screen(
            caption_set.layout_info
        )

        primary = None

        for lang in caption_set.get_languages():
            self.last_time = None
            if primary is None:
                primary = lang

            caption_set.set_layout_info(
                lang,
                self._relativize_and_fit_to_screen(caption_set.get_layout_info(lang)),
            )

            for caption in caption_set.get_captions(lang):
                caption.layout_info = self._relativize_and_fit_to_screen(
                    caption.layout_info
                )
                for node in caption.nodes:
                    node.layout_info = self._relativize_and_fit_to_screen(
                        node.layout_info
                    )
                sami = self._recreate_p_tag(caption, sami, lang, primary, caption_set)

        stylesheet = self._recreate_stylesheet(caption_set)
        sami.find("style").append(stylesheet)

        a = sami.prettify(formatter=None).split("\n")
        caption_content = "\n".join(a[1:])
        return caption_content

    def _recreate_p_tag(self, caption, sami, lang, primary, captions):
        """Build a <sync><p> block for a single caption with styling and alignment."""
        time = caption.start // 1000

        if self.last_time and time != self.last_time:
            sami = self._recreate_blank_tag(sami, caption, lang, primary, captions)

        self.last_time = caption.end // 1000

        sami, sync = self._recreate_sync(sami, lang, primary, time)

        p = sami.new_tag("p")

        p_style = ""
        for attr, value in self._recreate_style(caption.style).items():
            p_style += f"{attr}:{value};"

        if caption.layout_info and caption.layout_info.alignment:
            h = caption.layout_info.alignment.horizontal
            if h:
                css_align = HORIZONTAL_ALIGNMENT_MAP.get(h)
                if css_align:
                    p_style += f"text-align:{css_align};"

        if p_style:
            p["style"] = p_style

        p["class"] = self._recreate_p_lang(caption, lang, captions)
        p.string = self._recreate_text(caption.nodes)

        sync.append(p)

        return sami

    def _recreate_sync(self, sami, lang, primary, time):
        """Find or create a <sync> tag at the given millisecond timestamp."""
        if lang == primary:
            sync = sami.new_tag("sync", start=time)
            sami.body.append(sync)
        else:
            sync = sami.find("sync", start=time)
            if sync is None:
                sami, sync = self._find_closest_sync(sami, time)

        return sami, sync

    @staticmethod
    def _find_closest_sync(sami, time):
        """Insert a new <sync> tag in chronological order among existing syncs."""
        sync = sami.new_tag("sync", start=time)

        earlier = sami.find_all("sync", start=lambda x: int(x) < time)
        if earlier:
            last_sync = earlier[-1]
            last_sync.insert_after(sync)
        else:
            later = sami.find_all("sync", start=lambda x: int(x) > time)
            if later:
                last_sync = later[0]
                last_sync.insert_before(sync)
        return sami, sync

    def _recreate_blank_tag(self, sami, caption, lang, primary, captions):
        """Insert an &nbsp; paragraph to clear the previous caption at its end time."""
        sami, sync = self._recreate_sync(sami, lang, primary, self.last_time)

        p = sami.new_tag("p")
        p["class"] = self._recreate_p_lang(caption, lang, captions)
        p.string = "&nbsp;"

        sync.append(p)

        return sami

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
            line = line.rstrip() + "</span> "
            self._span_stack.pop()

        return line.rstrip()

    def _recreate_line_style(self, line, node):
        """Handle style node transitions, opening and closing <span> tags."""
        if node.start:
            line = self._recreate_span(line, node.content)
        else:
            if self._span_stack:
                had_span = self._span_stack.pop()
                if had_span:
                    line = line.rstrip() + "</span> "

        return line

    def _recreate_span(self, line, content):
        """Build an opening <span> with class and/or inline style attributes."""
        style = ""
        klass = ""
        if "classes" in content:
            klass += f' class="{" ".join(content["classes"])}"'
        elif "class" in content:
            klass += f' class="{content["class"]}"'

        for attr, value in self._recreate_style(content).items():
            style += f"{attr}:{value};"

        if style or klass:
            if style:
                style = f' style="{style}"'
            line += f"<span{klass}{style}>"
            self._span_stack.append(True)
        else:
            self._span_stack.append(False)

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
