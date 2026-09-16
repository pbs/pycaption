"""DFXP/TTML caption writer.

Serializes pycaption CaptionSet objects into DFXP/TTML XML documents,
including style elements, region-based positioning, and writing direction.
"""

import re
from copy import deepcopy
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup

from ..base import BaseWriter, CaptionNode
from ..geometry import HorizontalAlignmentEnum, LineAlignmentEnum, WritingDirectionEnum
from .constants import (
    DFXP_ATTR_XML_ID,
    DFXP_ATTR_XML_LANG,
    DFXP_BASE_MARKUP,
    DFXP_DEFAULT_LANGUAGE_CODE,
    DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID,
    DFXP_DEFAULT_STYLE,
    DFXP_DEFAULT_STYLE_ID,
    DFXP_WRITER_DEFAULT_REGION,
    DFXP_WRITER_FALLBACK_ALIGNMENT,
    _create_external_alignment,
)

_WRITING_DIRECTION_TO_DFXP = {
    WritingDirectionEnum.VERTICAL_RL: "tbrl",
    WritingDirectionEnum.VERTICAL_LR: "tblr",
}

_LINE_ALIGNMENT_TO_DISPLAY_ALIGN = {
    LineAlignmentEnum.START: "before",
    LineAlignmentEnum.CENTER: "center",
    LineAlignmentEnum.END: "after",
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
        self._span_stack = []
        self.region_creator = None
        super().__init__(*args, **kwargs)

    def write(self, caption_set, **kwargs):
        """Serialize a CaptionSet into a DFXP/TTML XML string.

        :type caption_set: CaptionSet
        :param kwargs:
            force (str): if set and present in the caption_set, output only
                this language
        :rtype: str
        """
        force = kwargs.get("force", "")
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

        Handles text nodes, line breaks (<br/>), and style spans.  Nodes are
        first split into runs sharing one region; a run whose region is not
        the one already in effect is wrapped in a <span> carrying it, so text
        renders at its own position instead of inheriting the one on the
        enclosing <p>, and a <br/> between two nodes of one region stays
        inside that region.

        :rtype: str
        """
        line = ""
        self._span_stack = []
        paragraph_region, _ = self.region_creator.get_positioning_info(
            lang, caption_set, caption
        )

        for region_id, region_attribs, nodes, wrappable in self._group_nodes_by_region(
            caption, paragraph_region, caption_set, lang
        ):
            wrap = wrappable and region_id != self._innermost_region(paragraph_region)
            if wrap:
                attrs = {"region": region_id}
                if self.write_inline_positioning:
                    attrs.update(region_attribs)
                attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
                line += f"<span {attr_str}>"

            for node in nodes:
                if node.type_ == CaptionNode.TEXT:
                    line += escape(node.content)

                elif node.type_ == CaptionNode.BREAK:
                    line = line.rstrip() + "<br/>\n    "

                elif node.type_ == CaptionNode.STYLE:
                    line = self._recreate_span(
                        line, node, dfxp, caption_set, caption, lang
                    )

            if wrap:
                line = line.rstrip() + "</span> "

        while self._span_stack:
            emitted, _ = self._span_stack.pop()
            if emitted:
                line = line.rstrip() + "</span> "

        return line.rstrip()

    def _group_nodes_by_region(self, caption, paragraph_region, caption_set, lang):
        """Split a caption's nodes into consecutive runs sharing one region.

        Line breaks are neutral: a run absorbs one only when it continues
        past it, so a break between two nodes of the same region ends up
        inside that region's span rather than outside it.  Breaks left over
        between two runs form a run of their own, which is never wrapped.
        A run is split again around any style tag whose partner falls
        outside it, so one such tag costs only itself a wrapper.

        :param paragraph_region: xml:id of the region on the enclosing <p>
        :return: (region_id, positioning_attributes, nodes, wrappable) per run
        :rtype: list[tuple[str | None, dict, list[CaptionNode], bool]]
        """
        resolved, partners = self._resolve_node_regions(
            caption, paragraph_region, caption_set, lang
        )

        groups = []
        current = None
        pending = []

        for index, (region_id, region_attribs) in enumerate(resolved):
            if region_id is None:
                pending.append(index)
                continue

            if current and region_id == current[0]:
                current[2].extend(pending)
            else:
                if current:
                    groups.append(current)
                if pending:
                    groups.append((None, {}, pending))
                current = [region_id, region_attribs, []]
            pending = []
            current[2].append(index)

        if current:
            groups.append(current)
        if pending:
            groups.append((None, {}, pending))

        return [
            (
                region_id,
                region_attribs,
                [caption.nodes[index] for index in segment],
                region_id is not None
                and self._is_wrappable(segment, partners, caption.nodes),
            )
            for region_id, region_attribs, indices in groups
            for segment in self._split_at_crossing_styles(
                indices, partners, caption.nodes
            )
        ]

    @staticmethod
    def _split_at_crossing_styles(indices, partners, nodes):
        """Split a run around style tags whose partner sits outside it.

        A span wrapping such a tag would cross another span and produce
        invalid XML, but only that tag is in the way — the nodes beside it
        still deserve their own region, so they come back as runs of their
        own instead of losing their position along with it.

        :rtype: list[list[int]]
        """
        run = set(indices)
        segments = [[]]

        for index in indices:
            crossing = (
                nodes[index].type_ == CaptionNode.STYLE
                and partners.get(index) not in run
            )
            if crossing:
                segments += [[index], []]
            else:
                segments[-1].append(index)

        return [segment for segment in segments if segment]

    def _resolve_node_regions(self, caption, paragraph_region, caption_set, lang):
        """Resolve the region every node of a caption belongs to.

        A node's own layout wins; lacking one it takes the region in effect
        around it — the innermost enclosing style span's, else the
        paragraph's.  For a closing style node that is its own opener's
        region, so a span is never separated from its own end tag.  Line
        breaks belong to no region and resolve to None.

        :return: a (region_id, positioning_attributes) pair per node, plus a
            map pairing the index of each style tag with its partner's
        :rtype: tuple[list[tuple[str | None, dict]], dict]
        """
        creator = self.region_creator
        resolved = []
        partners = {}
        open_styles = []

        for index, node in enumerate(caption.nodes):
            in_effect = open_styles[-1][1] if open_styles else paragraph_region

            if node.type_ == CaptionNode.BREAK:
                resolved.append((None, {}))

            elif node.type_ == CaptionNode.TEXT:
                region_id, region_attribs = None, {}
                if node.content.strip():
                    region_id, region_attribs = creator.get_node_positioning_info(
                        node.layout_info
                    )
                resolved.append((region_id or in_effect, region_attribs))

            elif node.start:
                if node.layout_info:
                    region_id, region_attribs = creator.get_positioning_info(
                        lang, caption_set, caption, node
                    )
                else:
                    region_id, region_attribs = in_effect, {}
                open_styles.append((index, region_id))
                resolved.append((region_id, region_attribs))

            else:
                if open_styles:
                    opener, _ = open_styles.pop()
                    partners[opener] = index
                    partners[index] = opener
                resolved.append((in_effect, {}))

        return resolved, partners

    @staticmethod
    def _is_wrappable(indices, partners, nodes):
        """Check whether a run of nodes can take a <span> holding its region.

        Every style tag in the run must be matched inside the run, or the
        wrapping span would cross a style span and produce invalid XML —
        which is what rules out a tag split off on its own.  A run that is
        nothing but one style span with a layout of its own already writes
        the region on that span, so it needs no wrapper.

        :rtype: bool
        """
        run = set(indices)
        for index in indices:
            if nodes[index].type_ == CaptionNode.STYLE:
                if partners.get(index) not in run:
                    return False

        first = nodes[indices[0]]

        return not (
            first.type_ == CaptionNode.STYLE
            and first.start
            and first.layout_info
            and partners.get(indices[0]) == indices[-1]
        )

    def _innermost_region(self, default):
        """Return the region in effect at the current point in the caption.

        The innermost open span carrying a region wins; with no such span,
        the region on the enclosing <p> applies.

        :param default: region of the enclosing <p>
        :rtype: str
        """
        for _, region_id in reversed(self._span_stack):
            if region_id:
                return region_id

        return default

    def _recreate_span(
        self, line, node, dfxp, caption_set=None, caption=None, lang=None
    ):
        """Open or close a <span> element for a style node.

        Supports nested spans via a stack.  Opening pushes onto the stack;
        closing pops the most recent span.  Each entry records whether a tag
        was actually emitted and which region it carries, if any.

        :param line: the accumulated markup string so far
        :type line: str
        :param node: a CaptionNode of type STYLE
        :rtype: str
        """
        if node.start:
            attrs = _recreate_style(node.content, dfxp)
            region_id = None
            if node.layout_info:
                region_id, region_attribs = self.region_creator.get_positioning_info(
                    lang, caption_set, caption, node
                )
                attrs["region"] = region_id
                if self.write_inline_positioning:
                    attrs.update(region_attribs)

            if attrs:
                attr_str = " ".join(f'{k}="{v}"' for k, v in attrs.items())
                line += f"<span {attr_str}>"
                self._span_stack.append((True, region_id))
            else:
                self._span_stack.append((False, None))

        else:
            if self._span_stack:
                had_span, _ = self._span_stack.pop()
                if had_span:
                    line = line.rstrip() + "</span> "

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
        self._fallback_alignment = None

    @staticmethod
    def _collect_unique_regions(caption_set, ignore_region):
        """Collect all unique Layout objects from the caption set.

        Excludes None and ignore_region (typically the default region).

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

    def _create_unique_regions(self, unique_layouts, dfxp, id_factory):
        """Create <region> tags in the <layout> section for each Layout.

        Skips Layout objects that have no positioning data (no origin,
        extent, padding, alignment, writing_direction, or line_alignment).

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
                or region_spec.line_alignment
            ):
                new_region = dfxp.new_tag("region")
                new_id = id_factory()
                new_region[DFXP_ATTR_XML_ID] = new_id

                region_map[region_spec] = new_id
                region_attribs = _convert_layout_to_attributes(
                    region_spec, self._fallback_alignment
                )
                new_region.attrs.update(region_attribs)

                layout_section.append(new_region)
        return region_map

    def _needs_center_promotion(self):
        """Check if the source format's visual default requires center promotion.

        Per SMPTE RP 2052-10, DFXP's native default is START/left. When the
        source format visually defaults to CENTER (WebVTT, SRT, SCC, MicroDVD),
        the writer must use CENTER alignment for its default region to prevent
        visual regression.

        Uses CaptionSet.visual_alignment_default set by the reader.
        """
        source_default = self._caption_set.visual_alignment_default
        return source_default == HorizontalAlignmentEnum.CENTER

    def create_document_regions(self):
        """Create all <region> tags needed by the caption set.

        Always creates a default region first, then creates additional
        regions for any unique Layout objects found in the caption set.
        When the source format defaults to center alignment, the default
        region uses CENTER per RP 2052-10; otherwise it uses the
        DFXP spec default (START) for round-trip fidelity.
        """
        if self._needs_center_promotion():
            default_layout = DFXP_WRITER_DEFAULT_REGION
            self._fallback_alignment = DFXP_WRITER_FALLBACK_ALIGNMENT
        else:
            default_layout = DFXP_DEFAULT_REGION
            self._fallback_alignment = None

        default_region_map = self._create_unique_regions(
            [default_layout], self._dfxp, lambda: DFXP_DEFAULT_REGION_ID
        )
        unique_regions = self._collect_unique_regions(self._caption_set, default_layout)

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

        positioning_attributes = _convert_layout_to_attributes(
            layout_info, self._fallback_alignment
        )
        self._assigned_region_ids.add(region_id)

        return region_id, positioning_attributes

    def get_node_positioning_info(self, layout_info):
        """Return (region_id, positioning_attributes) for a node's own layout.

        Unlike get_positioning_info, this neither cascades to the caption and
        the caption set nor falls back to the default region: a layout without
        a region of its own yields (None, {}).

        :type layout_info: geometry.Layout | None
        :rtype: tuple[str | None, dict]
        """
        region_id = self._region_map.get(layout_info)
        if not region_id:
            return None, {}

        self._assigned_region_ids.add(region_id)

        return region_id, _convert_layout_to_attributes(
            layout_info, self._fallback_alignment
        )

    def cleanup_regions(self):
        """Remove <region> tags that were never assigned to any element."""
        layout_tag = self._dfxp.find("layout")
        if not layout_tag:
            return

        for region in layout_tag.findChildren("region"):
            if region.attrs.get(DFXP_ATTR_XML_ID) not in self._assigned_region_ids:
                region.extract()


_CSS_LENGTH_RE = re.compile(r"^-?[\d.]+(?:px|em|%|pt|rem|c)?$")
_CSS_COLOR_RE = re.compile(r"^(?:#[0-9a-fA-F]{3,8}|rgba?\([^)]+\)|[a-zA-Z]{3,})$")


def _text_shadow_to_outline(value):
    """Best-effort conversion of CSS text-shadow to tts:textOutline.

    Extracts the color and a representative thickness from the first shadow
    in the list. Returns "color thickness" or None if unparseable.
    """
    first_shadow = value.split(",")[0].strip()
    tokens = first_shadow.split()
    color = None
    lengths = []
    for token in tokens:
        if _CSS_LENGTH_RE.match(token):
            lengths.append(token)
        elif _CSS_COLOR_RE.match(token):
            color = token
    if not lengths:
        return None
    if len(lengths) >= 3:
        thickness = lengths[2]
    else:
        thickness = lengths[0]
    if color:
        return f"{color} {thickness}"
    return thickness


def _recreate_style(content, dfxp):
    """Convert an internal style dict to DFXP/TTS style attributes.

    Maps pycaption's internal keys (class, italics, bold, underline, color,
    background-color, font-family, font-size, text-shadow, text-align,
    display-align) to their tts: namespace equivalents.

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
    if "text-shadow" in content:
        outline = _text_shadow_to_outline(content["text-shadow"])
        if outline:
            dfxp_style["tts:textOutline"] = outline
    if "color" in content:
        dfxp_style["tts:color"] = content["color"]
    if "background-color" in content:
        dfxp_style["tts:backgroundColor"] = content["background-color"]
    if "opacity" in content:
        dfxp_style["tts:opacity"] = content["opacity"]
    if "line-height" in content:
        dfxp_style["tts:lineHeight"] = content["line-height"]
    if "display-align" in content:
        dfxp_style["tts:displayAlign"] = content["display-align"]

    return dfxp_style


def _convert_layout_to_attributes(layout, fallback_alignment=None):
    """Convert a Layout object to a dict of DFXP region attributes.

    Maps origin, extent, padding, alignment, and writing_direction to their
    tts: namespace equivalents.

    When layout is None, uses fallback_alignment if provided
    (per RP 2052-10 center promotion).

    :type layout: Layout | None
    :param fallback_alignment: Alignment to use when the layout lacks one.
        Set by RegionCreator based on CaptionSet.visual_alignment_default.
    :type fallback_alignment: Alignment | None
    :rtype: dict
    """
    result = {}
    if not layout:
        if fallback_alignment:
            return _create_external_alignment(fallback_alignment)
        return result

    if layout.origin:
        result["tts:origin"] = layout.origin.to_xml_attribute()

    if layout.extent:
        result["tts:extent"] = layout.extent.to_xml_attribute()

    if layout.padding:
        result["tts:padding"] = layout.padding.to_xml_attribute()

    if layout.alignment:
        result.update(_create_external_alignment(layout.alignment))
    elif fallback_alignment:
        result.update(_create_external_alignment(fallback_alignment))

    writing_mode = _WRITING_DIRECTION_TO_DFXP.get(layout.writing_direction)
    if writing_mode:
        result["tts:writingMode"] = writing_mode

    if layout.line_alignment:
        display_align = _LINE_ALIGNMENT_TO_DISPLAY_ALIGN.get(layout.line_alignment)
        if display_align:
            result["tts:displayAlign"] = display_align

    return result
