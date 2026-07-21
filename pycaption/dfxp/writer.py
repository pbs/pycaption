from copy import deepcopy
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup

from ..base import BaseWriter, CaptionNode
from ..geometry import WritingDirectionEnum
from .constants import (
    DFXP_ATTR_XML_ID,
    DFXP_ATTR_XML_LANG,
    DFXP_BASE_MARKUP,
    DFXP_DEFAULT_LANGUAGE_CODE,
    DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID,
    DFXP_DEFAULT_STYLE,
    DFXP_DEFAULT_STYLE_ID,
    _create_external_alignment,
)

_WRITING_DIRECTION_TO_DFXP = {
    WritingDirectionEnum.VERTICAL_RL: "tbrl",
    WritingDirectionEnum.VERTICAL_LR: "tblr",
}


class DFXPWriter(BaseWriter):
    """Converts a CaptionSet to DFXP/TTML format.

    Supports layout positioning, inline styles (bold, italic, underline,
    color, background-color, font-family, font-size), writing direction,
    and region-based positioning.
    """

    def __init__(self, *args, **kwargs):
        """
        :param write_inline_positioning: if True, positioning attributes are
            written directly on <p> and <span> elements in addition to the
            region reference.
        """
        self.write_inline_positioning = kwargs.pop("write_inline_positioning", False)
        self.open_span = False
        self.region_creator = None
        super().__init__(*args, **kwargs)

    def write(self, caption_set, force=""):
        """Serialize a CaptionSet into a DFXP/TTML XML string.

        :type caption_set: CaptionSet
        :param force: if set and present in the caption_set, output only
            this language
        :rtype: str
        """
        dfxp = BeautifulSoup(DFXP_BASE_MARKUP, "lxml-xml")

        langs = caption_set.get_languages()
        if force in langs:
            langs = [force]
            dfxp.find("tt")[DFXP_ATTR_XML_LANG] = force
        else:
            dfxp.find("tt")[DFXP_ATTR_XML_LANG] = DFXP_DEFAULT_LANGUAGE_CODE

        caption_set = deepcopy(caption_set)
        self._relativize_layouts(caption_set, langs)
        self._write_styles(caption_set, dfxp)

        self.region_creator = RegionCreator(dfxp, caption_set)
        self.region_creator.create_document_regions()

        body = dfxp.find("body")
        if not body:
            raise RuntimeError("DFXP markup missing <body> element")
        for lang in langs:
            body.append(self._build_div(lang, caption_set, dfxp))

        self.region_creator.cleanup_regions()
        return dfxp.prettify(formatter=None)

    def _relativize_layouts(self, caption_set, langs):
        """Relativize and fit-to-screen all layout_info on captions and nodes.

        :type caption_set: CaptionSet
        :param langs: languages to process
        :type langs: list[str]
        """
        for lang in langs:
            for caption in caption_set.get_captions(lang):
                caption.layout_info = self._relativize_and_fit_to_screen(
                    caption.layout_info
                )
                for node in caption.nodes:
                    node.layout_info = self._relativize_and_fit_to_screen(
                        node.layout_info
                    )

    def _write_styles(self, caption_set, dfxp):
        """Write <style> elements into the <styling> section of the DFXP document.

        Skips pseudo-element styles (those starting with '::').  If the
        caption_set has no styles at all, a default style is created.

        :type caption_set: CaptionSet
        :type dfxp: BeautifulSoup
        """
        for style_id, style in caption_set.get_styles():
            if style != {} and not style_id.startswith("::"):
                self._recreate_styling_tag(style_id, style, dfxp)
        if not caption_set.get_styles():
            self._recreate_styling_tag(DFXP_DEFAULT_STYLE_ID, DFXP_DEFAULT_STYLE, dfxp)

    def _build_div(self, lang, caption_set, dfxp):
        """Build a <div> element containing all <p> tags for a given language.

        :type lang: str
        :type caption_set: CaptionSet
        :type dfxp: BeautifulSoup
        :rtype: bs4.element.Tag
        """
        div = dfxp.new_tag("div")
        div[DFXP_ATTR_XML_LANG] = lang
        self._assign_positioning_data(div, lang, caption_set)

        for caption in caption_set.get_captions(lang):
            caption_style = caption.style or {"class": DFXP_DEFAULT_STYLE_ID}
            p = self._recreate_p_tag(caption, caption_style, dfxp, caption_set, lang)
            self._assign_positioning_data(p, lang, caption_set, caption)
            div.append(p)

        return div

    def _assign_positioning_data(
        self, tag, lang, caption_set=None, caption=None, caption_node=None
    ):
        """Set the 'region' attribute on a tag, and optionally inline positioning.

        :param tag: the BeautifulSoup tag to be modified
        :type lang: str
        :type caption_set: CaptionSet | None
        :type caption: Caption | None
        :type caption_node: CaptionNode | None
        """
        assigned_id, attribs = self.region_creator.get_positioning_info(
            lang, caption_set, caption, caption_node
        )

        if assigned_id:
            tag["region"] = assigned_id
            if self.write_inline_positioning:
                tag.attrs.update(attribs)

    @staticmethod
    def _recreate_styling_tag(style, content, dfxp):
        """Create a <style> tag from an internal style dict and append it to <styling>.

        :param style: the xml:id to assign to the new <style> element
        :type style: str
        :param content: internal style dict (keys like 'color', 'italics', etc.)
        :type content: dict
        :type dfxp: BeautifulSoup
        :rtype: BeautifulSoup
        """
        attributes = _recreate_style(content, dfxp)
        if attributes:
            dfxp_style = dfxp.new_tag("style")
            dfxp_style.attrs.update({DFXP_ATTR_XML_ID: style})
            dfxp_style.attrs.update(attributes)
            dfxp.find("styling").append(dfxp_style)

        return dfxp

    def _recreate_p_tag(
        self, caption, caption_style, dfxp, caption_set=None, lang=None
    ):
        """Build a <p> element for a single caption cue.

        :param caption: the Caption object to serialize
        :param caption_style: internal style dict for this caption
        :type caption_style: dict
        :type dfxp: BeautifulSoup
        :type caption_set: CaptionSet | None
        :type lang: str | None
        :rtype: bs4.element.Tag
        """
        start = caption.format_start()
        end = caption.format_end()
        p = dfxp.new_tag("p", begin=start, end=end)
        p.string = self._recreate_text(caption, dfxp, caption_set, lang)

        if dfxp.find("style", {DFXP_ATTR_XML_ID: "p"}):
            p["style"] = "p"

        p.attrs.update(_recreate_style(caption_style, dfxp))

        return p

    def _recreate_text(self, caption, dfxp, caption_set=None, lang=None):
        """Serialize all nodes of a caption into DFXP inline markup.

        Handles text nodes, line breaks (<br/>), and style spans.

        :rtype: str
        """
        line = ""

        for node in caption.nodes:
            if node.type_ == CaptionNode.TEXT:
                line += escape(node.content)

            elif node.type_ == CaptionNode.BREAK:
                line = line.rstrip() + "<br/>\n    "

            elif node.type_ == CaptionNode.STYLE:
                line = self._recreate_span(line, node, dfxp, caption_set, caption, lang)

        return line.rstrip()

    def _recreate_span(
        self, line, node, dfxp, caption_set=None, caption=None, lang=None
    ):
        """Open or close a <span> element for a style node.

        When opening, collects style and positioning attributes.  Closes
        any previously open span before opening a new one.

        :param line: the accumulated markup string so far
        :type line: str
        :param node: a CaptionNode of type STYLE
        :rtype: str
        """
        if node.start:
            attrs = _recreate_style(node.content, dfxp)
            if node.layout_info:
                region_id, region_attribs = self.region_creator.get_positioning_info(
                    lang, caption_set, caption, node
                )
                attrs["region"] = region_id
                if self.write_inline_positioning:
                    attrs.update(region_attribs)

            if attrs:
                if self.open_span:
                    line = line.rstrip() + "</span> "
                attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
                line += f"<span {attr_str}>"
                self.open_span = True

        elif self.open_span:
            line = line.rstrip() + "</span> "
            self.open_span = False

        return line


class RegionCreator:
    """Creates DFXP <region> elements and assigns region IDs to document elements.

    Region resolution for a node follows this cascade:
        1. If the node has a non-None layout_info, use the region created for
           that exact Layout specification.
        2. Otherwise inherit layout_info from the Caption parent, then from
           the CaptionSet.
        3. If still None, fall back to the default region.
    """

    def __init__(self, dfxp, caption_set):
        """
        :type dfxp: BeautifulSoup
        :type caption_set: CaptionSet
        """
        self._dfxp = dfxp
        self._caption_set = caption_set
        self._region_map = {}
        self._id_seed = 0
        self._assigned_region_ids = set()

    @staticmethod
    def _collect_unique_regions(caption_set, ignore_region):
        """Collect all unique Layout objects from the caption set.

        Excludes None and ignore_region (typically the default region) to
        avoid duplicate region creation.

        :type caption_set: CaptionSet
        :param ignore_region: a Layout to exclude from the result
        :rtype: dict
        """
        unique_regions = {}
        languages = caption_set.get_languages()
        for lang in languages:
            layout_info = caption_set.get_layout_info(lang)
            unique_regions[layout_info] = None

            for caption in caption_set.get_captions(lang):
                unique_regions[caption.layout_info] = None

                for node in caption.nodes:
                    unique_regions[node.layout_info] = None

        unique_regions.pop(None, None)
        unique_regions.pop(ignore_region, None)
        return unique_regions

    @staticmethod
    def _create_unique_regions(unique_layouts, dfxp, id_factory):
        """Create <region> tags in the <layout> section for each Layout.

        Skips Layout objects that have no positioning data (no origin,
        extent, padding, alignment, or writing_direction).

        :param unique_layouts: iterable of geometry.Layout instances
        :type dfxp: BeautifulSoup
        :param id_factory: callable that returns a unique region ID string
        :return: mapping from Layout to the xml:id of its created region
        :rtype: dict
        """
        region_map = {}
        layout_section = dfxp.find("layout")

        for region_spec in unique_layouts:
            if (
                region_spec.origin
                or region_spec.extent
                or region_spec.padding
                or region_spec.alignment
                or region_spec.writing_direction
            ):
                new_region = dfxp.new_tag("region")
                new_id = id_factory()
                new_region[DFXP_ATTR_XML_ID] = new_id

                region_map[region_spec] = new_id
                region_attribs = _convert_layout_to_attributes(region_spec)
                new_region.attrs.update(region_attribs)

                layout_section.append(new_region)
        return region_map

    def create_document_regions(self):
        """Create all <region> tags needed by the caption set.

        Always creates a default region first, then creates additional
        regions for any unique Layout objects found in the caption set.
        """
        default_region_map = self._create_unique_regions(
            [DFXP_DEFAULT_REGION], self._dfxp, lambda: DFXP_DEFAULT_REGION_ID
        )
        unique_regions = self._collect_unique_regions(
            self._caption_set, DFXP_DEFAULT_REGION
        )

        self._region_map = self._create_unique_regions(
            unique_regions, self._dfxp, self._get_new_id
        )
        self._region_map.update(default_region_map)

    def _get_new_id(self, prefix="r"):
        """Generate a unique region ID using an incrementing counter.

        :param prefix: string prefix for the ID (default "r")
        :rtype: str
        """
        new_id = f"{prefix}{self._id_seed}"
        self._id_seed += 1
        return new_id

    def get_positioning_info(
        self, lang, caption_set=None, caption=None, caption_node=None
    ):
        """Return (region_id, positioning_attributes) for a caption element.

        Resolves layout_info by cascading: caption_node -> caption ->
        caption_set language -> caption_set default.  Falls back to the
        default region ID if no match is found in the region map.

        :type lang: str
        :type caption_set: CaptionSet | None
        :type caption: Caption | None
        :type caption_node: CaptionNode | None
        :rtype: tuple[str, dict]
        """
        layout_info = None
        if caption_node:
            layout_info = caption_node.layout_info

        if not layout_info and caption:
            layout_info = caption.layout_info

        if not layout_info and caption_set:
            layout_info = caption_set.get_layout_info(lang)
            if not layout_info:
                layout_info = caption_set.layout_info

        region_id = self._region_map.get(layout_info)
        if not region_id:
            region_id = DFXP_DEFAULT_REGION_ID

        positioning_attributes = _convert_layout_to_attributes(layout_info)
        self._assigned_region_ids.add(region_id)

        return region_id, positioning_attributes

    def cleanup_regions(self):
        """Remove <region> tags that were never assigned to any element."""
        layout_tag = self._dfxp.find("layout")
        if not layout_tag:
            return

        for region in layout_tag.findChildren("region"):
            if region.attrs.get(DFXP_ATTR_XML_ID) not in self._assigned_region_ids:
                region.extract()


def _recreate_style(content, dfxp):
    """Convert an internal style dict to DFXP/TTS style attributes.

    Maps pycaption's internal keys (class, italics, bold, underline, color,
    background-color, font-family, font-size, text-align, display-align)
    to their tts: namespace equivalents.

    :param content: internal style dictionary
    :type content: dict
    :param dfxp: the document, used to verify that referenced styles exist
    :type dfxp: BeautifulSoup
    :rtype: dict
    """
    dfxp_style = {}

    if (
        "class" in content
        and dfxp
        and dfxp.find("style", {DFXP_ATTR_XML_ID: content["class"]})
    ):
        dfxp_style["style"] = content["class"]
    if "text-align" in content:
        dfxp_style["tts:textAlign"] = content["text-align"]
    if "italics" in content:
        dfxp_style["tts:fontStyle"] = "italic"
    if "bold" in content:
        dfxp_style["tts:fontWeight"] = "bold"
    if "underline" in content:
        dfxp_style["tts:textDecoration"] = "underline"
    if "font-family" in content:
        dfxp_style["tts:fontFamily"] = content["font-family"]
    if "font-size" in content:
        dfxp_style["tts:fontSize"] = content["font-size"]
    if "color" in content:
        dfxp_style["tts:color"] = content["color"]
    if "background-color" in content:
        dfxp_style["tts:backgroundColor"] = content["background-color"]
    if "display-align" in content:
        dfxp_style["tts:displayAlign"] = content["display-align"]

    return dfxp_style


def _convert_layout_to_attributes(layout):
    """Convert a Layout object to a dict of DFXP region attributes.

    Maps origin, extent, padding, alignment, and writing_direction to their
    tts: namespace equivalents.  Returns default alignment attributes when
    layout is None.

    :type layout: Layout | None
    :rtype: dict
    """
    result = {}
    if not layout:
        return _create_external_alignment(DFXP_DEFAULT_REGION.alignment)

    if layout.origin:
        result["tts:origin"] = layout.origin.to_xml_attribute()

    if layout.extent:
        result["tts:extent"] = layout.extent.to_xml_attribute()

    if layout.padding:
        result["tts:padding"] = layout.padding.to_xml_attribute()

    if layout.alignment:
        result.update(_create_external_alignment(layout.alignment))
    else:
        result.update(_create_external_alignment(DFXP_DEFAULT_REGION.alignment))

    writing_mode = _WRITING_DIRECTION_TO_DFXP.get(layout.writing_direction)
    if writing_mode:
        result["tts:writingMode"] = writing_mode

    return result
