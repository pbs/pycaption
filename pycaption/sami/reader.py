"""SAMI caption reader.

Parses SAMI documents into pycaption CaptionSet objects, handling CSS
styles, margin-based positioning, and multi-language content.
"""

from bs4 import BeautifulSoup, NavigableString

from ..base import BaseReader, Caption, CaptionList, CaptionNode, CaptionSet
from ..exceptions import (
    CaptionReadNoCaptions,
    CaptionReadTimingError,
    InvalidInputError,
)
from ..geometry import Alignment, Layout, Padding, Size
from .parser import SAMIParser

_TAG_TO_STYLE = {"i": "italics", "b": "bold", "u": "underline"}


class SAMIReader(BaseReader):
    """Reads SAMI caption files into a CaptionSet.

    Supports CSS-based styling (font, color, text-decoration), margin-based
    positioning converted to Layout objects, and multi-language documents.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        self.line = []
        self.first_alignment = None

    def detect(self, content):
        """Return True if content looks like a SAMI document."""
        return "<sami" in content.lower()

    def read(self, content):
        """Parse a SAMI string into a CaptionSet.

        :type content: str
        :rtype: CaptionSet
        :raises InvalidInputError: if content is not a string
        :raises CaptionReadNoCaptions: if no captions are found
        """
        if not isinstance(content, str):
            raise InvalidInputError("The content is not a unicode string.")

        content, doc_styles, doc_langs = SAMIParser().feed(content)
        sami_soup = BeautifulSoup(content, features="lxml")

        global_layout = self._build_layout(doc_styles.get("p", {}))

        caption_dict = {}
        for language in doc_langs:
            lang_layout = None
            for target, styling in list(doc_styles.items()):
                if target not in ["p", "sync", "span"]:
                    if styling.get("lang", None) == language:
                        lang_layout = self._build_layout(
                            doc_styles.get(target, {}), inherit_from=global_layout
                        )
                        break
            lang_layout = lang_layout or global_layout
            lang_captions = self._translate_lang(language, sami_soup, lang_layout)

            caption_dict[language] = lang_captions

        caption_set = CaptionSet(caption_dict, layout_info=global_layout)

        for style in list(doc_styles.items()):
            style = (style[0], self._translate_parsed_style(style[1]))

        caption_set.set_styles(doc_styles)

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    def _build_layout(self, styles, inherit_from=None):
        """Build a Layout from CSS margin and text-align properties.

        :type styles: dict
        :param inherit_from: parent Layout whose values are used as defaults
        :rtype: Layout
        """
        alignment = Alignment.from_horizontal_and_vertical_align(
            text_align=styles.get("text-align")
        )
        return Layout(
            origin=None,
            extent=None,
            padding=self._get_padding(styles),
            alignment=alignment,
            inherit_from=inherit_from,
        )

    def _get_padding(self, styles):
        """Convert CSS margin-* properties to a Padding object.

        :rtype: Padding | None
        """
        margin_before = self._get_size(styles, "margin-top")
        margin_after = self._get_size(styles, "margin-bottom")
        margin_start = self._get_size(styles, "margin-left")
        margin_end = self._get_size(styles, "margin-right")
        if not any([margin_before, margin_after, margin_start, margin_end]):
            return None
        return Padding(
            before=margin_before,
            after=margin_after,
            start=margin_start,
            end=margin_end,
        )

    def _get_size(self, styles, style_label):
        """Extract a Size from a CSS property value string.

        :rtype: Size | None
        """
        value_from_style = styles.get(style_label, None)
        if not value_from_style:
            return None
        return Size.from_string(value_from_style)

    def _translate_lang(self, language, sami_soup, parent_layout):
        """Convert all <p> tags for a language into a CaptionList.

        Sets end times by using the next caption's start time.  The last
        caption gets an arbitrary 4-second duration if no end is available.

        :rtype: CaptionList
        """
        captions = CaptionList(layout_info=parent_layout)
        milliseconds = 0

        for p in sami_soup.select(f"p[lang|={language}]"):
            start_str = p.parent.get("start")
            if not start_str:
                raise CaptionReadTimingError(
                    f"Missing start time on the following line: {p.parent}."
                )
            milliseconds = int(float(start_str))
            start = milliseconds * 1000

            self._backfill_end_times(captions, start)

            if p.get_text().strip():
                caption = self._build_caption(p, start, parent_layout)
                captions.append(caption)

        if captions and captions[-1].end == 0:
            captions[-1].end = (milliseconds + 4000) * 1000

        return captions

    @staticmethod
    def _backfill_end_times(captions, start):
        """Set end time on preceding captions that don't have one yet."""
        for i in reversed(range(len(captions))):
            if captions[i].end != 0:
                break
            if captions[i].start != start:
                captions[i].end = start

    def _build_caption(self, p, start, parent_layout):
        """Parse a single <p> element into a Caption object.

        :rtype: Caption
        """
        self.first_alignment = None
        styles = self._translate_attrs(p)
        layout_info = self._build_layout(styles, inherit_from=parent_layout)
        self.line = []

        self._translate_tag(p, layout_info)
        caption_layout = Layout(
            alignment=self.first_alignment, inherit_from=layout_info
        )
        for node in self.line:
            node.layout_info = Layout(
                alignment=self.first_alignment, inherit_from=node.layout_info
            )
        self.first_alignment = None

        return Caption(start, 0, self.line, styles, caption_layout)

    def _translate_tag(self, tag, inherit_from=None):
        """Recursively convert a BeautifulSoup element into CaptionNodes.

        Handles NavigableString (text), <br> (break), <i>/<b>/<u> (style),
        and <span> (class/inline-style).
        """
        if isinstance(tag, NavigableString):
            tag_text = str(tag)
            if tag_text and tag_text[0] in "\n\r":
                tag_text = tag_text.lstrip()
            tag_text = tag_text.rstrip("\n\r")
            if not tag_text:
                return
            self.line.append(CaptionNode.create_text(tag_text, inherit_from))
        elif tag.name == "br":
            self.line.append(CaptionNode.create_break(inherit_from))
        elif tag.name == "i" or tag.name == "b" or tag.name == "u":
            style_name = _TAG_TO_STYLE.get(tag.name)
            self.line.append(CaptionNode.create_style(True, {style_name: True}))
            for a in tag.contents:
                self._translate_tag(a, inherit_from)
            self.line.append(CaptionNode.create_style(False, {style_name: True}))
        elif tag.name == "span":
            self._translate_span(tag, inherit_from)
        else:
            for a in tag.contents:
                self._translate_tag(a, inherit_from)

    def _translate_span(self, tag, inherit_from=None):
        """Convert a <span> tag into style-start/end nodes with layout.

        If the span has styling attributes, wraps children between style
        nodes.  Otherwise processes children without wrapping.
        """
        args = self._translate_attrs(tag)
        if args:
            layout_info = self._build_layout(args, inherit_from)
            node = CaptionNode.create_style(True, args, layout_info)
            self.line.append(node)
            for a in tag.contents:
                self._translate_tag(a, layout_info)
            node = CaptionNode.create_style(False, args, layout_info)
            self.line.append(node)
        else:
            for a in tag.contents:
                self._translate_tag(a, inherit_from)

    def _translate_attrs(self, tag):
        """Extract class, id, and inline style from a tag into a style dict.

        :rtype: dict
        """
        attrs = {}
        css_attrs = tag.attrs

        if "class" in css_attrs:
            attrs["class"] = css_attrs["class"][0].lower()
        if "id" in css_attrs:
            attrs["class"] = css_attrs["id"].lower()
        if "style" in css_attrs:
            styles = css_attrs["style"].split(";")
            attrs.update(self._translate_style(attrs, styles))

        return attrs

    def _translate_style(self, attrs, styles):
        """Parse inline CSS declarations into the style dict.

        text-align is captured separately as a Layout alignment; other
        properties are delegated to _translate_css_property.

        :rtype: dict
        """
        for style in styles:
            style = style.split(":")
            if len(style) == 2:
                css_property, value = style
            else:
                continue
            if css_property == "text-align":
                self._save_first_alignment(value.strip())
            else:
                self._translate_css_property(attrs, css_property, value)

        return attrs

    def _translate_parsed_style(self, styles):
        """Normalize a stylesheet rule dict by mapping CSS names to internal keys.

        Mutates the dict in-place (e.g. font-style:italic → italics:True).

        :rtype: dict
        """
        attrs = styles
        for css_property in list(styles.keys()):
            value = styles[css_property]
            self._translate_css_property(attrs, css_property, value)

        return attrs

    @staticmethod
    def _translate_css_property(attrs, css_property, value):
        """Map a single CSS property to pycaption's internal style key.

        Recognized properties: font-family, font-size, font-style (italic),
        text-decoration (underline), font-weight (bold), lang, color.
        """
        if css_property == "font-family":
            attrs["font-family"] = value.strip()
        elif css_property == "font-size":
            attrs["font-size"] = value.strip()
        elif css_property == "font-style" and value.strip() == "italic":
            attrs["italics"] = True
        elif css_property == "text-decoration" and value.strip() == "underline":
            attrs["underline"] = True
        elif css_property == "font-weight" and value.strip() == "bold":
            attrs["bold"] = True
        elif css_property == "lang":
            attrs["lang"] = value.strip()
        elif css_property == "color":
            attrs["color"] = value.strip()

    def _save_first_alignment(self, align):
        """Capture the first text-align value encountered in a caption.

        Only the first alignment wins — subsequent spans with different
        alignments are ignored, since SAMI normalizes to one alignment
        per caption.
        """
        if not self.first_alignment:
            self.first_alignment = Alignment.from_horizontal_and_vertical_align(
                text_align=align
            )
