"""DFXP/TTML caption reader.

Parses DFXP/TTML documents into pycaption CaptionSet objects, resolving
styles, regions, and positioning through LayoutAwareDFXPParser and
LayoutInfoScraper.
"""

import re

from bs4 import BeautifulSoup, NavigableString

from ..base import (
    DEFAULT_LANGUAGE_CODE,
    BaseReader,
    Caption,
    CaptionList,
    CaptionNode,
    CaptionSet,
)
from ..exceptions import (
    CaptionReadNoCaptions,
    CaptionReadSyntaxError,
    CaptionReadTimingError,
    InvalidInputError,
)
from ..geometry import (
    Alignment,
    Layout,
    Padding,
    Point,
    Stretch,
    UnitEnum,
    WritingDirectionEnum,
)
from ..utils import is_leaf
from .constants import (
    DFXP_ATTR_XML_ID,
    DFXP_ATTR_XML_LANG,
    DFXP_DEFAULT_FRAMERATE,
    DFXP_DEFAULT_FRAMERATE_MULTIPLIER,
    DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_SUBFRAMERATE,
    DFXP_DEFAULT_TICKRATE,
    HORIZONTAL_ALIGNMENT_TO_DFXP,
    MICROSECONDS_PER_UNIT,
    TIME_EXPRESSION_PATTERN,
    VERTICAL_ALIGNMENT_TO_DFXP,
)

_LEADING_WHITESPACE_RE = re.compile("^(?:[\n\r]+\\s*)?(.+)")

_DFXP_WRITING_MODE_MAP = {
    "tbrl": WritingDirectionEnum.VERTICAL_RL,
    "tblr": WritingDirectionEnum.VERTICAL_LR,
    "tb": WritingDirectionEnum.VERTICAL_RL,
}


class DFXPReader(BaseReader):
    """Reads DFXP/TTML caption files into a CaptionSet.

    Supports clock-time and offset-time timestamps, inline and referenced
    styles, and region-based positioning (via LayoutAwareDFXPParser).
    """

    def __init__(self, *args, **kw):
        """
        :param read_invalid_positioning: if True, read positioning attributes
            even when they appear directly on <p> elements (non-standard per
            the TTML spec, but common in real-world files).
        """
        super().__init__(*args, **kw)
        self.read_invalid_positioning = kw.get("read_invalid_positioning", False)
        self.nodes = []
        self.framerate = float(DFXP_DEFAULT_FRAMERATE)
        self.tickrate = float(DFXP_DEFAULT_TICKRATE)

    @staticmethod
    def _get_effective_framerate(framerate_str, multiplier_str):
        """Compute effective frame rate from ttp:frameRate and ttp:frameRateMultiplier.

        :param framerate_str: value of ttp:frameRate (e.g. "24", "30")
        :param multiplier_str: value of ttp:frameRateMultiplier (e.g. "1000 1001")
        :rtype: float
        :raises CaptionReadSyntaxError: if values are malformed or zero
        """
        try:
            framerate = float(framerate_str)
            parts = multiplier_str.strip().split()
            if len(parts) != 2:
                raise ValueError(
                    f"ttp:frameRateMultiplier must be two integers, got: "
                    f"'{multiplier_str}'"
                )
            result = framerate * (int(parts[0]) / int(parts[1]))
        except (ValueError, ZeroDivisionError) as err:
            raise CaptionReadSyntaxError(
                f"Invalid frame rate parameters (ttp:frameRate='{framerate_str}', "
                f"ttp:frameRateMultiplier='{multiplier_str}'): {err}"
            )
        if result <= 0:
            raise CaptionReadSyntaxError(
                f"Effective frame rate must be positive, got {result}"
            )
        return result

    def detect(self, content):
        """Return True if content looks like a DFXP/TTML document.

        :type content: str
        :rtype: bool
        """
        lowered = content.lower()
        return bool(re.search(r"<tt[\s>]", lowered)) and "</tt>" in lowered

    def read(self, content):
        """Parse a DFXP/TTML string into a CaptionSet.

        :type content: str
        :rtype: CaptionSet
        :raises InvalidInputError: if content is not a string
        :raises CaptionReadNoCaptions: if no captions are found
        """
        if not isinstance(content, str):
            raise InvalidInputError("The content is not a unicode string.")

        dfxp_document = LayoutAwareDFXPParser(
            content, read_invalid_positioning=self.read_invalid_positioning
        )

        tt_attrs = dfxp_document.tt.attrs if dfxp_document.tt else {}
        framerate_str = tt_attrs.get("ttp:framerate", str(DFXP_DEFAULT_FRAMERATE))
        multiplier_str = tt_attrs.get(
            "ttp:frameratemultiplier", DFXP_DEFAULT_FRAMERATE_MULTIPLIER
        )
        self.framerate = self._get_effective_framerate(framerate_str, multiplier_str)

        if "ttp:tickrate" in tt_attrs:
            try:
                tickrate = float(tt_attrs["ttp:tickrate"])
            except ValueError:
                raise CaptionReadSyntaxError(
                    f"ttp:tickRate must be a number, "
                    f"got '{tt_attrs['ttp:tickrate']}'"
                )
            if tickrate <= 0:
                raise CaptionReadSyntaxError(
                    f"ttp:tickRate must be positive, got '{tt_attrs['ttp:tickrate']}'"
                )
            self.tickrate = tickrate
        else:
            # TTML spec 8.2.12: default tickRate = frameRate × subFrameRate
            try:
                sub_framerate = int(
                    tt_attrs.get("ttp:subframerate", DFXP_DEFAULT_SUBFRAMERATE)
                )
            except ValueError:
                raise CaptionReadSyntaxError(
                    f"ttp:subFrameRate must be a positive integer, "
                    f"got '{tt_attrs['ttp:subframerate']}'"
                )
            try:
                framerate_int = int(framerate_str)
            except ValueError:
                raise CaptionReadSyntaxError(
                    f"ttp:frameRate must be a positive integer, "
                    f"got '{framerate_str}'"
                )
            self.tickrate = float(framerate_int * sub_framerate)

        caption_dict = {}
        style_dict = {}

        default_language = tt_attrs.get(DFXP_ATTR_XML_LANG, DEFAULT_LANGUAGE_CODE)

        for div in dfxp_document.find_all("div"):
            lang = div.attrs.get(DFXP_ATTR_XML_LANG, default_language)
            caption_dict[lang] = self._convert_div_to_caption_list(div)

        for style in dfxp_document.find_all("style"):
            id_ = style.attrs.get(DFXP_ATTR_XML_ID) or style.attrs.get("id")
            if id_:
                # Styles nested inside <region> tags are region-scoped and
                # should not appear as document-level styles.
                if "region" not in [parent_.name for parent_ in style.parents]:
                    style_dict[id_] = self._convert_style(style)

        caption_set = CaptionSet(caption_dict, styles=style_dict)

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    def _convert_div_to_caption_list(self, div):
        """Convert a <div> element into a CaptionList for one language.

        :param div: a BeautifulSoup <div> tag containing <p> children
        :rtype: CaptionList
        """
        return CaptionList(
            [
                caption
                for caption in (
                    self._convert_p_tag_to_caption(p_tag)
                    for p_tag in div.find_all("p")
                    if p_tag.get_text().strip()
                )
                if caption is not None
            ],
            div.layout_info,
        )

    def _convert_p_tag_to_caption(self, p_tag):
        """Convert a single <p> element into a Caption object.

        :param p_tag: a BeautifulSoup <p> tag with begin/end or dur attributes
        :rtype: Caption | None
        """
        start, end = self._find_and_convert_times(p_tag)
        self.nodes = []
        self._convert_tag_to_node(p_tag)
        styles = self._convert_style(p_tag)

        if len(self.nodes) > 0:
            return Caption(
                start, end, self.nodes, style=styles, layout_info=p_tag.layout_info
            )
        return None

    def _find_and_convert_times(self, p_tag):
        """Extract and convert begin/end timestamps from a <p> tag.

        Supports both end-time and duration (dur) attributes.

        :param p_tag: a BeautifulSoup <p> tag
        :rtype: tuple[int, int]
        :raises CaptionReadTimingError: if begin or end/dur is missing
        """
        begin = p_tag.get("begin")
        if not begin:
            raise CaptionReadTimingError(f"Missing begin time on line {p_tag}.")

        end = p_tag.get("end")
        dur = p_tag.get("dur")
        if not end and not dur:
            raise CaptionReadTimingError(
                f"Missing end time or duration on line {p_tag}."
            )

        start = self._convert_timestamp_to_microseconds(begin)
        if end:
            end = self._convert_timestamp_to_microseconds(p_tag["end"])
        else:
            dur = self._convert_timestamp_to_microseconds(p_tag["dur"])
            end = start + dur

        return start, end

    def _convert_timestamp_to_microseconds(self, stamp):
        """Parse a DFXP time expression into microseconds.

        Accepts clock-time (hh:mm:ss, hh:mm:ss:ff, hh:mm:ss.ms) and
        offset-time (count + metric) formats.

        :type stamp: str
        :rtype: int
        :raises CaptionReadTimingError: if the timestamp format is invalid
        """
        match = TIME_EXPRESSION_PATTERN.search(stamp)
        if not match:
            raise CaptionReadTimingError(
                f"Invalid timestamp: {stamp}. Accepted formats: hh:mm:ss / "
                "hh:mm:ss:ff / hh:mm:ss.sub-frames / time_count h|m|s|ms|f."
            )
        if match.group("clock_time"):
            return self._convert_clock_time_to_microseconds(match)
        else:
            return self._convert_time_count_to_microseconds(match)

    def _convert_clock_time_to_microseconds(self, clock_time_match):
        """Convert a clock-time regex match to microseconds.

        :param clock_time_match: regex match with groups hours, minutes,
            seconds, and optionally sub_frames or frames
        :rtype: int
        """
        microseconds = (
            int(clock_time_match.group("hours")) * MICROSECONDS_PER_UNIT["hours"]
        )
        microseconds += (
            int(clock_time_match.group("minutes")) * MICROSECONDS_PER_UNIT["minutes"]
        )
        microseconds += (
            int(clock_time_match.group("seconds")) * MICROSECONDS_PER_UNIT["seconds"]
        )
        if clock_time_match.group("sub_frames"):
            microseconds += (
                int(clock_time_match.group("sub_frames").ljust(3, "0"))
                * MICROSECONDS_PER_UNIT["milliseconds"]
            )
        elif clock_time_match.group("frames"):
            microseconds += (
                int(clock_time_match.group("frames"))
                / self.framerate
                * MICROSECONDS_PER_UNIT["seconds"]
            )
        return int(microseconds)

    def _convert_time_count_to_microseconds(self, time_count_match):
        """Convert an offset-time regex match to microseconds.

        :param time_count_match: regex match with groups time_count and metric
        :rtype: int
        """
        value = float(time_count_match.group("time_count"))
        metric = time_count_match.group("metric")
        microseconds = 0.0
        if metric == "h":
            microseconds = value * MICROSECONDS_PER_UNIT["hours"]
        elif metric == "m":
            microseconds = value * MICROSECONDS_PER_UNIT["minutes"]
        elif metric == "s":
            microseconds = value * MICROSECONDS_PER_UNIT["seconds"]
        elif metric == "ms":
            microseconds = value * MICROSECONDS_PER_UNIT["milliseconds"]
        elif metric == "f":
            microseconds = value / self.framerate * MICROSECONDS_PER_UNIT["seconds"]
        elif metric == "t":
            microseconds = value / self.tickrate * MICROSECONDS_PER_UNIT["seconds"]
        return int(microseconds)

    def _convert_tag_to_node(self, tag):
        """Recursively convert a BeautifulSoup element into CaptionNodes.

        Handles NavigableString (text), <br> (break), and <span> (style)
        elements, appending results to self.nodes.

        :param tag: a BeautifulSoup Tag or NavigableString
        """
        if isinstance(tag, NavigableString):
            result = _LEADING_WHITESPACE_RE.search(tag)
            if result:
                tag_text = result.groups()[0]
                node = CaptionNode.create_text(tag_text, layout_info=tag.layout_info)
                self.nodes.append(node)
        elif tag.name == "br":
            self.nodes.append(CaptionNode.create_break(layout_info=tag.layout_info))
        elif tag.name == "span":
            self._convert_span_to_nodes(tag)
        else:
            for a in tag.contents:
                self._convert_tag_to_node(a)

    def _convert_span_to_nodes(self, tag):
        """Convert a <span> tag into open/close style CaptionNodes.

        Wraps child content between style-start and style-end nodes.
        If the span has no style attributes, its children are processed
        without wrapping.

        :param tag: a BeautifulSoup <span> tag
        """
        args = self._convert_style(tag)
        # Comparison against "" is intentional: args is a dict, so this is
        # always truthy when any attributes are present (empty dict is falsy).
        if args != "":
            self.nodes.append(
                CaptionNode.create_style(True, args, layout_info=tag.layout_info)
            )

            for a in tag.contents:
                self._convert_tag_to_node(a)

            self.nodes.append(
                CaptionNode.create_style(False, args, layout_info=tag.layout_info)
            )
        else:
            for a in tag.contents:
                self._convert_tag_to_node(a)

    @staticmethod
    def _convert_style(tag):
        """Convert DFXP/TTS style attributes on a tag to an internal style dict.

        Maps tts:fontStyle, tts:fontWeight, tts:textDecoration, tts:textAlign,
        tts:fontFamily, tts:fontSize, tts:color, and the style reference
        attribute to pycaption's internal keys.

        :param tag: BeautifulSoup Tag
        :rtype: dict
        """
        attrs = {}
        dfxp_attrs = tag.attrs
        for arg in dfxp_attrs:
            if arg.lower() == "style":
                attrs["classes"] = dfxp_attrs[arg].strip().split(" ")
                attrs["class"] = dfxp_attrs[arg]
            elif arg.lower() == "tts:fontstyle" and dfxp_attrs[arg] == "italic":
                attrs["italics"] = True
            elif arg.lower() == "tts:fontweight" and dfxp_attrs[arg] == "bold":
                attrs["bold"] = True
            elif arg.lower() == "tts:textdecoration" and "underline" in dfxp_attrs[
                arg
            ].strip().split(" "):
                attrs["underline"] = True
            elif arg.lower() == "tts:textalign":
                attrs["text-align"] = dfxp_attrs[arg]
            elif arg.lower() == "tts:fontfamily":
                attrs["font-family"] = dfxp_attrs[arg]
            elif arg.lower() == "tts:fontsize":
                attrs["font-size"] = dfxp_attrs[arg]
            elif arg.lower() == "tts:color":
                attrs["color"] = dfxp_attrs[arg]
            elif arg.lower() == "tts:backgroundcolor":
                attrs["background-color"] = dfxp_attrs[arg]
        return attrs


class LayoutAwareDFXPParser(BeautifulSoup):
    """BeautifulSoup subclass that adds a layout_info attribute to every node.

    Traverses the element tree in pre-order as dictated by the DFXP style
    resolution spec, resolving region associations and positioning for each
    element.
    """

    NO_POSITIONING_INFO = None

    def __init__(
        self,
        markup="",
        features="html.parser",
        builder=None,
        parse_only=None,
        from_encoding=None,
        read_invalid_positioning=False,
        **kwargs,
    ):
        """Parse DFXP markup and attach layout_info to every element.

        Uses html.parser (forgiving with malformed XML like unescaped '<')
        rather than 'xml' (destroys entities) or 'lxml' (strict).
        Manually replaces &apos; since html.parser only supports HTML4 entities.

        :type read_invalid_positioning: bool
        :param read_invalid_positioning: if True, also read positioning
            attributes directly on elements (non-standard placement)
        """
        markup = markup.replace("&apos;", "'")

        super().__init__(markup, features, builder, parse_only, from_encoding, **kwargs)

        self.read_invalid_positioning = read_invalid_positioning

        for div in self.find_all("div"):
            self._pre_order_visit(div)

    def _pre_order_visit(self, element, inherit_from=None):
        """Attach a layout_info attribute to every element in pre-order.

        Leaf nodes inherit from their parent; non-leaf nodes resolve their
        own positioning from region associations.

        :param element: a BeautifulSoup Tag or NavigableString
        :param inherit_from: Layout inherited from the ancestor chain
        """
        if is_leaf(element):
            element.layout_info = inherit_from
        else:
            region_id = self._determine_region_id(element)
            layout_info = self._extract_positioning_information(region_id, element)
            element.layout_info = layout_info
            for child in element.contents:
                self._pre_order_visit(child, inherit_from=layout_info)

    @staticmethod
    def _get_region_from_ancestors(element):
        """Walk up the tree and return the first region ID found on an ancestor.

        :param element: a BeautifulSoup Tag or NavigableString
        :rtype: str | None
        """
        region_id = None
        parent = element.parent
        while parent:
            region_id = parent.get("region")
            if region_id:
                break
            parent = parent.parent

        return region_id

    @staticmethod
    def _get_region_from_descendants(element):
        """Get the region ID from descendant elements.

        If descendants reference more than one region, raises LookupError
        to signal ambiguous positioning (region data should be discarded).

        :param element: a BeautifulSoup Tag or NavigableString
        :rtype: str | None
        :raises LookupError: if descendants reference multiple regions
        """
        if isinstance(element, NavigableString):
            return None

        region_id = None
        child_region_ids = {child.get("region") for child in element.findChildren()}
        if len(child_region_ids) > 1:
            raise LookupError
        if len(child_region_ids) == 1:
            region_id = child_region_ids.pop()

        return region_id

    @classmethod
    def _determine_region_id(cls, element):
        """Determine the TTML region associated with an element.

        Checks (in order): the element itself, its ancestors, and its
        descendants.  Returns None if no region can be determined (the
        writer assigns the default region in that case).

        :param element: a BeautifulSoup Tag or NavigableString
        :rtype: str | None
        """
        region_id = None

        if hasattr(element, "get"):
            region_id = element.get("region")

        if not region_id:
            region_id = cls._get_region_from_ancestors(element)

        if not region_id:
            try:
                region_id = cls._get_region_from_descendants(element)
            except LookupError:
                return

        return region_id

    def _extract_positioning_information(self, region_id, element):
        """Build a Layout object from the element's associated region.

        Uses the LayoutInfoScraper to resolve origin, extent, padding, and
        alignment from the region (and optionally from the element itself
        when read_invalid_positioning is True).

        :param region_id: xml:id of the associated <region>, or None
        :type region_id: str | None
        :param element: BeautifulSoup Tag being processed
        :rtype: Layout | None
        """
        region_tag = None

        if region_id is not None:
            region_tag = self.find("region", {DFXP_ATTR_XML_ID: region_id})

        region_scraper = LayoutInfoScraper(self, region_tag)

        positioning = region_scraper.scrape_positioning_info(
            element, self.read_invalid_positioning
        )

        if positioning and any(positioning):
            origin, extent, padding, alignment, writing_direction = positioning
            return Layout(
                origin,
                extent,
                padding,
                alignment,
                writing_direction=writing_direction,
            )
        else:
            return self.NO_POSITIONING_INFO


class LayoutInfoScraper:
    """Resolves positioning attributes (origin, extent, padding, alignment)
    for a DFXP element by inspecting its region, referenced styles, and
    ancestor hierarchy.
    """

    def __init__(self, document, region=None):
        """
        :param document: the BeautifulSoup document instance, of which `region`
            is a descendant
        :param region: the region tag
        """
        self.region = region
        self._styling_section = document.findChild("styling")
        if region:
            self.region_styles = self._get_style_sources(self._styling_section, region)
        else:
            self.region_styles = []
        self.root_element = document.find("tt")

    @classmethod
    def _get_style_sources(cls, styling_section, element):
        """Return <style> tags applicable to an element, in evaluation order.

        Collects:
          1. Nested <style> children of the element (with reference chains).
          2. The <style> referenced via the element's style="" attribute
             (with its reference chain).

        Skips nested-style collection for <div>/<body>/<tt> to avoid O(n^2)
        performance on large documents.

        :param styling_section: the <styling> tag from the document
        :param element: a BeautifulSoup Tag to resolve styles for
        :rtype: list
        """
        if not hasattr(element, "findAll"):
            return ()

        nested_styles = []

        # Skip container elements to avoid O(n^2) child iteration.
        if element.name not in ("div", "body", "tt"):
            for style in element.contents:
                if getattr(style, "name", None) == "style":
                    nested_styles.extend(
                        cls._get_style_reference_chain(style, styling_section)
                    )

        referenced_style_id = element.get("style")

        referenced_styles = []
        if referenced_style_id and styling_section:
            referenced_style = styling_section.findChild(
                "style", {DFXP_ATTR_XML_ID: referenced_style_id}
            )

            referenced_styles = cls._get_style_reference_chain(
                referenced_style, styling_section
            )
        return nested_styles + referenced_styles

    @classmethod
    def _get_style_reference_chain(cls, style, styling_tag):
        """Follow the style reference chain: s1 -> s2 -> ... -> sN.

        Returns [s1, s2, ..., sN] by recursively following the style=""
        attribute on each <style> tag.

        :param style: a <style> tag that may reference another style
        :param styling_tag: the <styling> section of the document
        :rtype: list
        :raises CaptionReadSyntaxError: if multiple styles share the same xml:id
        """
        if not style:
            return []

        result = [style]

        if not styling_tag:
            return result

        reference = style.get("style")

        if reference:
            referenced_styles = styling_tag.findChildren(
                "style", {DFXP_ATTR_XML_ID: reference}
            )

            if len(referenced_styles) == 1:
                return result + cls._get_style_reference_chain(
                    referenced_styles[0], styling_tag
                )
            elif len(referenced_styles) > 1:
                raise CaptionReadSyntaxError(
                    "Invalid caption file. "
                    f"More than 1 style with 'xml:id': {reference}"
                )

        return result

    def scrape_positioning_info(self, element=None, even_invalid=False):
        """Resolve positioning attributes into a positioning tuple.

        Returns (origin, extent, padding, alignment, writing_direction).
        Attributes are resolved from the region, its referenced styles, and
        (when even_invalid=True) from the element itself.  Falls back to
        DFXP_DEFAULT_REGION values when attributes are not found.

        :param element: BeautifulSoup Tag or NavigableString
        :type even_invalid: bool
        :param even_invalid: if True, also check positioning attributes on
            the element (non-standard but common in real files)
        :rtype: tuple[Point | None, Stretch | None, Padding | None,
            Alignment | None, WritingDirectionEnum | None]
        """
        usable_elem = element if even_invalid else None

        origin = (
            self._find_attribute(
                usable_elem, "tts:origin", Point.from_xml_attribute, ["auto"]
            )
            or DFXP_DEFAULT_REGION.origin
        )

        extent = self._find_attribute(
            usable_elem, "tts:extent", Stretch.from_xml_attribute, ["auto"]
        )

        if not extent:
            extent = self._find_root_extent() or DFXP_DEFAULT_REGION.extent

        padding = (
            self._find_attribute(usable_elem, "tts:padding", Padding.from_xml_attribute)
            or DFXP_DEFAULT_REGION.padding
        )

        # tts:textAlign is always read from <p> and <span> elements directly.
        if getattr(element, "name", None) in ("span", "p"):
            text_align_source = element
        else:
            text_align_source = None

        text_align = self._find_attribute(
            text_align_source, "tts:textAlign"
        ) or HORIZONTAL_ALIGNMENT_TO_DFXP.get(DFXP_DEFAULT_REGION.alignment.horizontal)
        display_align = self._find_attribute(
            usable_elem, "tts:displayAlign"
        ) or VERTICAL_ALIGNMENT_TO_DFXP.get(DFXP_DEFAULT_REGION.alignment.vertical)
        alignment = _create_internal_alignment(text_align, display_align)

        writing_mode_raw = self._find_attribute(usable_elem, "tts:writingMode")
        writing_direction = _DFXP_WRITING_MODE_MAP.get(writing_mode_raw)

        return origin, extent, padding, alignment, writing_direction

    def _find_attribute_on_element_or_styles(
        self, attribute_name, element, factory, ignore, ignorecase
    ):
        """Look up an attribute on the element itself, then on its referenced styles.

        :type attribute_name: str
        :param element: BeautifulSoup Tag or NavigableString
        :param factory: callable to transform the raw attribute value
        :param ignore: values to treat as absent
        :param ignorecase: if True, also try lowercase attribute name
        :type ignorecase: bool
        :return: the factory-transformed value, or None
        """
        value = _get_object_from_attribute(
            element, attribute_name, factory, ignore, ignorecase
        )
        if value is None:
            for style in self._get_style_sources(self._styling_section, element):
                value = _get_object_from_attribute(
                    style, attribute_name, factory, ignore, ignorecase
                )
                if value:
                    break
        return value

    def _find_attribute(
        self, element, attribute_name, factory=lambda x: x, ignore=(), ignorecase=True
    ):
        """Resolve an attribute by searching the element, its ancestors, and the region.

        Search order: element itself and its styles, then each ancestor and
        their styles, then self.region and its styles.

        :param element: BeautifulSoup Tag or NavigableString (or None)
        :type attribute_name: str
        :param factory: callable to transform the raw attribute value
        :param ignore: values that should be treated as not-found
        :param ignorecase: if True, also search the lowercase attribute name
        :type ignorecase: bool
        :return: the factory-transformed value, or None if not found
        """
        value = None

        if element:
            value = self._find_attribute_on_element_or_styles(
                attribute_name, element, factory, ignore, ignorecase
            )

            if value is None:
                for parent in element.parents:
                    value = self._find_attribute_on_element_or_styles(
                        attribute_name, parent, factory, ignore, ignorecase
                    )
                    if value:
                        break

        if value is None:
            value = self._find_attribute_on_element_or_styles(
                attribute_name, self.region, factory, ignore, ignorecase
            )

        return value

    def _find_root_extent(self):
        """Get tts:extent from the root <tt> element (must be in pixels).

        Per the spec, a root-level tts:extent is only valid when specified
        in pixel units.

        :rtype: Stretch | None
        :raises CaptionReadSyntaxError: if the extent is not in pixels
        """
        extent = _get_object_from_attribute(
            self.root_element, "tts:extent", Stretch.from_xml_attribute
        )

        if extent is not None and not extent.is_measured_in(UnitEnum.PIXEL):
            raise CaptionReadSyntaxError(
                "The base <tt> element attribute 'tts:extent' should "
                "only be specified in pixels. Check the docs: "
                "http://www.w3.org/TR/ttaf1-dfxp/"
                "#style-attribute-extent"
            )
        return extent


def _create_internal_alignment(text_align, display_align):
    """Convert DFXP tts:textAlign and tts:displayAlign values to an Alignment.

    tts:textAlign accepts: "left", "center", "right", "start", "end".
    tts:displayAlign accepts: "before", "center", "after".

    :type text_align: str | None
    :type display_align: str | None
    :rtype: Alignment | None
    """
    if not (text_align or display_align):
        return None

    return Alignment.from_horizontal_and_vertical_align(text_align, display_align)


def _get_object_from_attribute(
    tag, attr_name, factory, ignore_vals=(), ignorecase=True
):
    """Retrieve an XML attribute from a tag and transform it via factory.

    Returns None if the tag doesn't support attributes, the attribute is
    absent, or its value is in ignore_vals.

    :param tag: a BeautifulSoup Tag (or any object)
    :param attr_name: the XML attribute name to look up
    :type attr_name: str
    :param factory: callable to transform the raw string value
    :param ignore_vals: attribute values that should return None
    :param ignorecase: if True, also try the lowercase attribute name
    :type ignorecase: bool
    :raises CaptionReadSyntaxError: if factory raises ValueError
    """
    if not hasattr(tag, "has_attr"):
        return

    attr_value = None
    if tag.has_attr(attr_name):
        attr_value = tag.get(attr_name)

    if ignorecase and attr_name is not None:
        attr_value = tag.get(attr_name.lower())

    if attr_value is None:
        return

    usable_value = None

    if attr_value not in ignore_vals:
        try:
            usable_value = factory(attr_value)
        except ValueError as err:
            raise CaptionReadSyntaxError(err)

    return usable_value
