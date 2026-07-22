from collections import deque
from html.entities import name2codepoint
from html.parser import HTMLParser
from xml.dom import SyntaxErr

from bs4 import BeautifulSoup
from cssutils import css as cssutils_css
from cssutils import parseString

from ..base import DEFAULT_LANGUAGE_CODE
from ..exceptions import CaptionReadSyntaxError


class SAMIParser(HTMLParser):
    """HTML parser that normalizes raw SAMI markup into well-formed XML.

    Extracts CSS stylesheet rules and discovers caption languages during
    a single pass.  The result is a tuple of (normalized_xml, styles, langs)
    consumed by SAMIReader.
    """

    def __init__(self, *args, **kw):
        HTMLParser.__init__(self, *args, **kw)
        self.sami = ""
        self.styles = {}
        self.queue = deque()
        self.langs = set()
        self.last_element = ""
        self.name2codepoint = name2codepoint.copy()
        self.name2codepoint["apos"] = 0x0027
        self.convert_charrefs = False

    def handle_starttag(self, tag, attrs):
        """Normalize opening tags: treat <div> as <span>, detect language on <p>."""
        self.last_element = tag

        if tag == "div":
            tag = "span"

        if tag == "p":
            lang = self._find_lang(attrs)
            lang = lang or DEFAULT_LANGUAGE_CODE
            attrs.append(("lang", lang))
            self.langs.add(lang)

        if tag == "br":
            self.sami += "<br/>"
        else:
            # Close any already-open instance of this tag (LIFO) before re-opening
            while tag in self.queue:
                closer = self.queue.pop()
                self.sami += f"</{closer}>"
            self.queue.append(tag)
            for attr, value in attrs:
                tag += f' {attr.lower()}="{value}"'
            self.sami += f"<{tag}>"

    def handle_endtag(self, tag):
        """Close tags in LIFO order; handle SAMI's malformed sync/p nesting."""
        if tag == "div":
            tag = "span"

        # Skip duplicate close when the tag was just opened with no content
        if tag in ["p", "sync"] and tag == self.last_element:
            return

        while tag in self.queue:
            closing_tag = self.queue.pop()
            self.sami += f"</{closing_tag}>"

    def handle_entityref(self, name):
        """Convert named HTML entities to characters; preserve &gt; and &lt;."""
        if name in ["gt", "lt"]:
            self.sami += f"&{name};"
        else:
            try:
                self.sami += chr(self.name2codepoint[name])
            except (KeyError, ValueError):
                self.sami += f"&{name}"

        self.last_element = ""

    def handle_charref(self, name):
        """Convert numeric character references (&#NNN; or &#xHHH;) to characters."""
        self.sami += chr(int(name[1:], 16) if name[0] == "x" else int(name))

    def handle_data(self, data):
        """Append raw text content to the output."""
        self.sami += data
        self.last_element = ""

    def feed(self, data):
        """Parse raw SAMI content and return normalized XML, styles, and languages.

        :param data: Raw SAMI unicode string
        :returns: (normalized_xml, styles_dict, languages_set)
        :rtype: tuple[str, dict, set]
        :raises CaptionReadSyntaxError: if the file is HTML or has no captions
        """
        no_cc = "no closed captioning available"

        if "<html" in data.lower():
            raise CaptionReadSyntaxError("SAMI File seems to be an HTML file.")
        elif no_cc in data.lower():
            raise CaptionReadSyntaxError(f'SAMI File contains "{no_cc}"')

        index = data.lower().find("</head>")
        style = BeautifulSoup(data[:index], "lxml").find("style")
        if style and style.contents:
            self.styles = self._css_parse(" ".join(style.contents))
        else:
            self.styles = {}

        # Fix common SAMI authoring errors
        data = data.replace("<i/>", "<i>")
        data = data.replace(";>", ">")
        HTMLParser.feed(self, data)

        # Close any tags left open at end of document
        while self.queue:
            closing_tag = self.queue.pop()
            self.sami += f"</{closing_tag}>"

        return self.sami, self.styles, self.langs

    @staticmethod
    def _css_parse(css):
        """Parse a SAMI STYLE block into a dict of selector → properties.

        Color values are normalized to 6-digit hex (#rrggbb).

        :type css: str
        :rtype: dict[str, dict[str, str]]
        """
        sheet = parseString(css)
        style_sheet = {}

        for rule in sheet:
            new_style = {}
            selector = rule.selectorText.lower()
            if selector[0] in ["#", "."]:
                selector = selector[1:]
            for prop in rule.style:
                if prop.name == "color":
                    try:
                        cv = cssutils_css.ColorValue(prop.value)
                    except SyntaxErr:
                        raise CaptionReadSyntaxError(
                            f"Invalid color value: {prop.value}. Check for "
                            f"missing # before hex values or misspelled color "
                            f"values."
                        )
                    new_style["color"] = f"#{cv.red:02x}{cv.green:02x}{cv.blue:02x}"
                else:
                    new_style[prop.name] = prop.value
            if new_style:
                style_sheet[selector] = new_style

        return style_sheet

    def _find_lang(self, attrs):
        """Detect caption language from a <p> tag's attributes.

        Checks for an explicit lang attribute first, then looks up the
        class name in the parsed stylesheet for a lang property.

        :param attrs: list of (name, value) attribute tuples
        :rtype: str | None
        """
        for attr, value in attrs:
            if attr.lower() == "lang":
                return value[:2]
            if attr.lower() == "class":
                try:
                    return self.styles[value.lower()]["lang"]
                except KeyError:
                    pass

        return None
