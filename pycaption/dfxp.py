from bs4 import BeautifulSoup, NavigableString
from xml.sax.saxutils import escape

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE)
from .exceptions import CaptionReadNoCaptions, CaptionReadSyntaxError
from .geometry import (
    Point, Stretch, UnitEnum, Padding, VerticalAlignmentEnum,
    HorizontalAlignmentEnum, Alignment)
from pycaption.geometry import Layout


DFXP_BASE_MARKUP = u'''
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <styling/>
        <layout/>
    </head>
    <body/>
</tt>
'''

DFXP_DEFAULT_STYLE = {
    u'color': u'white',
    u'font-family': u'monospace',
    u'font-size': u'1c',
}

DFXP_DEFAULT_REGION = {
    u'text-align': u'center',
    u'display-align': u'after'
}

DFXP_DEFAULT_STYLE_ID = u'default'
DFXP_DEFAULT_REGION_ID = u'bottom'


class DFXPReader(BaseReader):
    def __init__(self, *args, **kw):
        self.read_invalid_positioning = (
            kw.get('read_invalid_positioning', False))
        self.nodes = []

    def detect(self, content):
        if u'</tt>' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        if type(content) != unicode:
            raise RuntimeError(u'The content is not a unicode string.')

        dfxp_document = LayoutAwareDFXPParser(
            content, read_invalid_positioning=self.read_invalid_positioning)
        captions = CaptionSet()

        # Each div represents all the captions for a single language.
        for div in dfxp_document.find_all(u'div'):
            lang = div.attrs.get(u'xml:lang', DEFAULT_LANGUAGE_CODE)
            captions.set_captions(lang, self._translate_div(div))
            captions.set_layout_info(lang, div.layout_info)

        for style in dfxp_document.find_all(u'style'):
            id = style.attrs.get(u'id')
            if not id:
                id = style.attrs.get(u'xml:id')
            captions.add_style(id, self._translate_style(style))

        captions = self._combine_matching_captions(captions)

        if captions.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return captions

    def _translate_div(self, div):
        captions = []
        for p_tag in div.find_all(u'p'):
            captions.append(self._translate_p_tag(p_tag))
        return captions

    def _translate_p_tag(self, p_tag):
        start, end = self._find_times(p_tag)
        self.nodes = []
        self._translate_tag(p_tag)
        styles = self._translate_style(p_tag)

        caption = Caption(layout_info=p_tag.layout_info)
        caption.start = start
        caption.end = end
        caption.nodes = self.nodes
        caption.style = styles
        return caption

    def _find_times(self, p_tag):
        start = self._translate_time(p_tag[u'begin'])

        try:
            end = self._translate_time(p_tag[u'end'])
        except KeyError:
            dur = self._translate_time(p_tag[u'dur'])
            end = start + dur

        return start, end

    def _translate_time(self, stamp):
        timesplit = stamp.split(u':')
        if u'.' not in timesplit[2]:
            timesplit[2] = timesplit[2] + u'.000'
        secsplit = timesplit[2].split(u'.')
        if len(timesplit) > 3:
            secsplit.append((int(timesplit[3]) / 30) * 100)
        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)
        return microseconds

    def _translate_tag(self, tag):
        # convert text
        if isinstance(tag, NavigableString):
            if tag.strip() != u'':
                node = CaptionNode.create_text(
                    tag.strip(), layout_info=tag.layout_info)
                self.nodes.append(node)
        # convert line breaks
        elif tag.name == u'br':
            self.nodes.append(
                CaptionNode.create_break(layout_info=tag.layout_info))
        # convert italics
        elif tag.name == u'span':
            # convert span
            self._translate_span(tag)
        else:
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)

    def _translate_span(self, tag):
        # convert tag attributes
        args = self._translate_style(tag)
        # only include span tag if attributes returned
        # TODO - this is an obvious very old bug. args will be a dictionary.
        # but since nobody complained, I'll leave it like that.
        # Happy investigating!
        if args != u'':
            node = CaptionNode.create_style(
                True, args, layout_info=tag.layout_info)
            node.start = True
            node.content = args
            self.nodes.append(node)

            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            node = CaptionNode.create_style(
                False, args, layout_info=tag.layout_info)
            node.start = False
            node.content = args
            self.nodes.append(node)
        else:
            for a in tag.contents:
                self._translate_tag(a)

    # convert style from DFXP
    def _translate_style(self, tag):
        attrs = {}
        dfxp_attrs = tag.attrs
        for arg in dfxp_attrs:
            if arg == u"style":
                attrs[u'class'] = dfxp_attrs[arg]
            elif arg == u"tts:fontstyle" and dfxp_attrs[arg] == u"italic":
                attrs[u'italics'] = True
            elif arg == u"tts:textalign":
                attrs[u'text-align'] = dfxp_attrs[arg]
            elif arg == u"tts:fontfamily":
                attrs[u'font-family'] = dfxp_attrs[arg]
            elif arg == u"tts:fontsize":
                attrs[u'font-size'] = dfxp_attrs[arg]
            elif arg == u"tts:color":
                attrs[u'color'] = dfxp_attrs[arg]
        return attrs

    # Merge together captions that have the same start/end times.
    def _combine_matching_captions(self, caption_set):
        for lang in caption_set.get_languages():
            captions = caption_set.get_captions(lang)
            new_caps = captions[:1]

            for caption in captions[1:]:
                if (caption.start == new_caps[-1].start
                        and caption.end == new_caps[-1].end):
                    new_caps[-1].nodes.append(CaptionNode.create_break())
                    new_caps[-1].nodes.extend(caption.nodes)
                else:
                    new_caps.append(caption)

            caption_set.set_captions(lang, new_caps)

        return caption_set


class DFXPWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.p_style = False
        self.open_span = False
        self.region_creator = None

    def write(self, captions, force=u''):
        dfxp = BeautifulSoup(DFXP_BASE_MARKUP, u'xml')
        dfxp.find(u'tt')[u'xml:lang'] = u"en"

        # Create the styles in the <styling> section, or a default style.
        for style_id, style in captions.get_styles():
            if style != {}:
                dfxp = self._recreate_styling_tag(style_id, style, dfxp)
        if not captions.get_styles():
            dfxp = self._recreate_styling_tag(
                DFXP_DEFAULT_STYLE_ID, DFXP_DEFAULT_STYLE, dfxp)

        self.region_creator = RegionCreator(dfxp, captions)
        self.region_creator.create_document_regions()

        body = dfxp.find(u'body')
        langs = captions.get_languages()
        if force in langs:
            langs = [force]

        for lang in langs:
            div = dfxp.new_tag(u'div')
            div[u'xml:lang'] = u'%s' % lang
            self._assign_region(div, lang, captions)

            for caption in captions.get_captions(lang):
                if caption.style:
                    caption_style = caption.style
                else:
                    caption_style = {u'class': DFXP_DEFAULT_STYLE_ID}

                p = self._recreate_p_tag(
                    caption, caption_style, dfxp, captions, lang)
                self._assign_region(p, lang, captions, caption)
                div.append(p)

            body.append(div)

        caption_content = dfxp.prettify(formatter=None)
        return caption_content

    def _assign_region(self, tag, lang,
                       caption_set=None, caption=None, caption_node=None):
        """Modifies the current tag, assigning it the 'region' attribute.

        :param tag: the BeautifulSoup tag to be modified
        :type lang: unicode
        :param lang: the caption language
        :type caption_set: CaptionSet
        :param caption_set: The CaptionSet parent
        :type caption: Caption
        :type caption_node: CaptionNode
        """
        assigned_id = self.region_creator.assign_region_id(
            lang, caption_set, caption, caption_node)

        if assigned_id:
            tag[u'region'] = assigned_id

    def _recreate_styling_tag(self, style, content, dfxp):
        # TODO - should be drastically simplified: if attributes : append
        dfxp_style = dfxp.new_tag(u'style')
        dfxp_style.attrs.update({u'xml:id': style})

        attributes = _recreate_style(content, dfxp)
        dfxp_style.attrs.update(attributes)

        new_tag = dfxp.new_tag(u'style')
        new_tag.attrs.update({u'xml:id': style})
        if dfxp_style != new_tag:
            dfxp.find(u'styling').append(dfxp_style)

        return dfxp

    def _recreate_p_tag(self, caption, caption_style, dfxp, caption_set=None,
                        lang=None):
        start = caption.format_start()
        end = caption.format_end()
        p = dfxp.new_tag(u"p", begin=start, end=end)
        p.string = self._recreate_text(caption, dfxp, caption_set, lang)

        if dfxp.find(u"style", {u"xml:id": u"p"}):
            p[u'style'] = u'p'

        p.attrs.update(_recreate_style(caption_style, dfxp))

        return p

    def _recreate_text(self, caption, dfxp, caption_set=None, lang=None):
        line = u''

        for node in caption.nodes:
            if node.type == CaptionNode.TEXT:
                line += escape(node.content) + u' '

            elif node.type == CaptionNode.BREAK:
                line = line.rstrip() + u'<br/>\n    '

            elif node.type == CaptionNode.STYLE:
                line = self._recreate_span(
                    line, node, dfxp, caption_set, caption, lang)

        return line.rstrip()

    def _recreate_span(self, line, node, dfxp, caption_set=None, caption=None,
                       lang=None):
        # TODO - This method seriously has to go away!
        # Because of the CaptionNode.STYLE nodes, tree-like structures are
        # are really hard to build, and proper xml elements can't be added.
        # We are left with creating tags manually, which is hard to understand
        # and harder to maintain
        if node.start:
            styles = u''

            content_with_style = _recreate_style(node.content, dfxp)
            for style, value in content_with_style.items():
                styles += u' %s="%s"' % (style, value)
            if node.layout_info:
                styles += u' region="{region_id}"'.format(
                    region_id=self.region_creator.assign_region_id(
                        lang, caption_set, caption, node
                    ))

            if styles:
                if self.open_span:
                    line = line.rstrip() + u'</span> '
                line += u'<span%s>' % styles
                self.open_span = True

        elif self.open_span:
            line = line.rstrip() + u'</span> '
            self.open_span = False

        return line


class LayoutAwareDFXPParser(BeautifulSoup):
    """This makes the xml instance capable of providing layout information
    for every one of its nodes (it adds a 'layout_info' attribute on each node)

    It parses the element tree in post-order-like fashion (as dictated by the
    dfxp specs http://www.w3.org/TR/ttaf1-dfxp/#semantics-region-layout-step-1)
    for determining the layout information
    """
    # A lot of elements will have no positioning info. Use this flyweight
    # to save memory
    NO_POSITIONING_INFO = None

    def __init__(self, markup=u"", features="html.parser", builder=None,
                 parse_only=None, from_encoding=None,
                 read_invalid_positioning=False, **kwargs):
        """The `features` param determines the parser to be used. The parsers
        are usually html parsers, some more forgiving than others, and as such
        they do stuff very differently especially for xml files. We chose this
        one because even though the docs say it's slower, it just "works".

        The reason why we haven't used the 'xml' parser is that it destroys
        characters such as < or & (even the escaped ones).

        :type read_invalid_positioning: bool
        :param read_invalid_positioning: if True, will try to also look for
            layout info on every element itself (even if the docs explicitly
            call for ignoring attributes, when incorrectly placed)


        Check out the docs below for explanation.
        http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
        """
        super(LayoutAwareDFXPParser, self).__init__(
            markup, features, builder, parse_only, from_encoding, **kwargs)

        self.read_invalid_positioning = read_invalid_positioning

        for div in self.find_all(u'div'):
            self._post_order_visit(div)

    def _post_order_visit(self, element):
        """Process the xml tree elements in post order by adding a .layout_info
        attribute to each of them.

        The specs say this is how the attributes should be determined, but
        for the region attribute this might be irrelevant and any type of tree
        walk might do.
        :param element: a BeautifulSoup Tag or NavigableString.
        """
        if hasattr(element, 'contents'):
            for child in element.contents:
                self._post_order_visit(child)
        region_id = self._determine_region_id(element)

        # TODO - this looks highly cachable. If it turns out too much memory is
        # being taken up by the caption set, cache this with a WeakValueDict
        element.layout_info = (
            self._extract_positioning_information(region_id, element))

    @staticmethod
    def _get_region_from_ancestors(element):
        """Try to get the region ID from the nearest ancestor that has it
        """
        region_id = None
        parent = element.parent
        while parent:
            region_id = parent.get('region')
            if region_id:
                break
            parent = parent.parent

        return region_id

    @staticmethod
    def _get_region_from_descendants(element):
        """Try to get the region_id from the closest descendant (that has it)
        This is trickier, because at different times, the determined region
        could be different. If this happens, discard region data
        """
        # element might be a NavigableString, not a Tag.
        if not hasattr(element, 'findChildren'):
            return None

        region_id = None
        child_region_ids = {
            child.get('region') for child in element.findChildren()
        }
        if len(child_region_ids) > 1:
            raise LookupError
        if len(child_region_ids) == 1:
            region_id = child_region_ids.pop()

        return region_id

    @classmethod
    def _determine_region_id(cls, element):
        """Determines the TT region of an element.

        For determining the region of an element, check out the url, look for
        section "[associate region]". One difference, is that we leave the
        default region id empty. The writer will know what to do:
        http://www.w3.org/TR/ttaf1-dfxp/#semantics-region-layout-step-1

        :param element: the xml element for which we're trying to get region
            info
        """
        # element could be a NavigableString. Those are dumb.
        region_id = None

        if hasattr(element, 'get'):
            region_id = element.get('region')

        if not region_id:
            region_id = cls._get_region_from_ancestors(element)

        if not region_id:
            try:
                region_id = cls._get_region_from_descendants(element)
            except LookupError:
                return

        return region_id

    def _extract_positioning_information(self, region_id, element):
        """Returns a Layout object that describes the element's positioning
        information

        :param region_id: the id of the region to which the element is
            associated
        :type region_id: unicode
        :param element: BeautifulSoup Tag or NavigableString; this only comes
            into action (at the moment) if the
        :rtype: Layout
        """
        has_region = False

        if region_id is not None:
            region_list = self.findAll(u'region', {u'xml:id': region_id})
            if not region_list:
                has_region = False
            else:
                region_scraper = LayoutAwareRegionScraper(self, region_list[0])
                has_region = True

        if has_region:
            if self.read_invalid_positioning:
                # Read positioning info from the region, and inline, from the
                # element (Be forgiving)
                layout_info = region_scraper.get_positioning_info(element)
            else:
                # Only read positioning info from the region
                # (Be compatible with the specification)
                layout_info = region_scraper.get_positioning_info()
        else:
            if self.read_invalid_positioning:
                # Positioning info only specified inline?
                # TODO - replace this with a fake_scrapper.get_positioning_info
                # ...lol, no need to duplicate logic, especially complicated
                # one - Time perhapse to create some .set_something on the
                # region scrapper, eh?
                layout_info = self._read_inline_positioning(element)
            else:
                layout_info = self.NO_POSITIONING_INFO

        if layout_info and any(layout_info):
            # layout_info contains information?
            return Layout(*layout_info)
        else:
            # layout_info doesn't contain any information
            return self.NO_POSITIONING_INFO

    @staticmethod
    def _read_inline_positioning(element):
        """For the elements who don't have a region, but specify their
        positioning inline, return their positioning info too

        :param element: BeautifulSoup Tag or NavigableString
        :rtype: tuple
        """
        origin, extent, padding, alignment = (None,) * 4

        if hasattr(element, 'get'):
            origin = _get_usable_attribute_value(
                element, u'tts:origin', Point.from_xml_attribute)
            extent = _get_usable_attribute_value(
                element, u'tts:extent', Stretch.from_xml_attribute
            )
            padding = _get_usable_attribute_value(
                element, u'tts:extent', Padding.from_xml_attribute, []
            )

            text_align = element.get(u'tts:textAlign')
            display_align = element.get(u'tts:displayAlign')
            alignment = _create_internal_alignment(text_align, display_align)

        return origin, extent, padding, alignment


class LayoutAwareRegionScraper(object):
    """Encapsulates the methods for determining the layout information about
    a region element.
    """
    def __init__(self, document, region):
        """
        :param document: the BeautifulSoup document instance, of which `region`
            is a descendant
        :param region: the region tag
        """
        self.region = region
        self.document = document
        self.styles = self._get_style_sources(document, region)

    @classmethod
    def _get_style_sources(cls, document, region):
        """Returns a list, containing  tags, in the order they should be
        evaluated, for determining layout information.

        This method should be extended if the styles provided by it are not
        enough (like for the captions created with CaptionMaker 6, which are
        not compatible with the specs)

        Check the URL for detailed description of how styles should be resolved
        http://www.w3.org/TR/ttaf1-dfxp/#semantics-style-association

        Returns:
          1. All child styles of the region, each with its reference chain
          2. The style referenced by the region, via the attrib. 'style="asdf"'
            together with its reference chain
        Note: the specs are unclear about the priority of styles that are
        referenced by nested styles. I've assumed it's higher than referential
        styling
        """
        styling_section = document.findChild('styling')

        nested_styles = []
        for style in region.findAll('style'):
            nested_styles.extend(
                cls._get_style_reference_chain(style, styling_section)
            )

        referenced_style_id = region.get('style')

        referenced_styles = []
        if referenced_style_id and styling_section:
            referenced_style = styling_section.findChild(
                'style', {'xml:id': referenced_style_id}
            )

            referenced_styles = (
                cls._get_style_reference_chain(
                    referenced_style, styling_section)
            )
        return nested_styles + referenced_styles

    @classmethod
    def _get_style_reference_chain(cls, style, styling_tag):
        """If style s1 references s2, and s3 -> s4 -> s5 -> ... -> sn,
        if called with s1, this returns [s1, s2, ... sn] (supposing all the
        styles are defined in the styling section, or stops at the last found
        style)

        :param style: a style tag, that might refer another style
        :param styling_tag: The tag representing the '<styling>' section of the
            dfxp document
        """
        if not style:
            return []

        result = [style]

        if not styling_tag:
            return result

        reference = style.get('style')

        if reference:
            referenced_styles = styling_tag.findChildren(
                'style', {'xml:id': reference}
            )

            if len(referenced_styles) == 1:
                return result + cls._get_style_reference_chain(
                    referenced_styles[0], styling_tag
                )
            elif len(referenced_styles) > 1:
                raise CaptionReadSyntaxError(
                    u"Invalid caption file. "
                    u"More than 1 style with 'xml:id': {id}"
                    .format(id=reference)
                )

        return result

    def get_positioning_info(self, element=None):
        """Determines the positioning information tuple
        (origin, extent, padding, alignment)
        from the region element.

        The 3 attributes can be specified inline, on the region node, on child
        tags of type <style> or on referenced <style> tags.

        :param element: BeautifulSoup Tag or NavigableString
        """

        origin = self._find_attribute(
            element, u'tts:origin', Point.from_xml_attribute)
        extent = self._find_attribute(
            element, u'tts:extent', Stretch.from_xml_attribute
        )

        if not extent:
            extent = self._find_root_extent()

        padding = self._find_attribute(
            element, u'tts:padding', Padding.from_xml_attribute
        )
        text_align = self._find_attribute(element, u'tts:textAlign')
        display_align = self._find_attribute(element, u'tts:displayAlign')
        alignment = _create_internal_alignment(text_align, display_align)

        return origin, extent, padding, alignment

    def _find_attribute(self, element, attribute_name, factory=lambda x: x):
        """Try to find the `attribute_name` specified on the element, its
         assigned region, its region's styles and their referenced styles.

        :param element: BeautifulSoup Tag or NavigableString
        :type attribute_name: unicode
        :rtype: unicode
        """
        value = None

        # Does the element itself have this inline?
        if element:
            value = _get_usable_attribute_value(
                element, attribute_name, factory
            )

        # Does self.region have the attribute?
        if value is None:
            value = _get_usable_attribute_value(
                self.region, attribute_name, factory
            )

        # Do any of its styles have the attribute?
        if value is None:
            for style in self.styles:
                value = _get_usable_attribute_value(
                    style, attribute_name, factory
                )
                # get the first value met in the style chain
                if value:
                    break

        return value

    def _find_root_extent(self):
        """Finds the "tts:extent" for the root <tt> element

        The tts:extent attribute, like the "tts:origin", can be specified on
        the region, its styles, or can be inherited from the root <tt> element.
        For the latter case, it must be specified in the unit 'pixel'.

        :rtype: Stretch
        """
        extent = None

        # Does the root 'tt' element have it?
        if extent is None:
            root = self.document.findAll(u'tt')[0]
            extent = _get_usable_attribute_value(
                root, u'tts:extent', Stretch.from_xml_attribute
            )

            if extent is not None:
                if not extent.is_measured_in(UnitEnum.PIXEL):
                    raise CaptionReadSyntaxError(
                        u"The base <tt> element attribute 'tts:extent' should "
                        u"only be specified in pixels. Check the docs: "
                        u"http://www.w3.org/TR/ttaf1-dfxp/"
                        u"#style-attribute-extent"
                    )
        return extent





class RegionCreator(object):
    """Creates the DFXP regions, and knows how retrieve them, for assigning
    region IDs to every element

    # todo - needs to remember the IDs created, and later, when assigning a
    region to every dfxp element, needs to know what region to assign to that
    element, based on the CaptionNode, its Caption and its CaptionSet.

    The layout information for a node is determined like this:
        - If a node has a (NON-NULL*).layout_info attribute, return the region
            created for that exact specification
        - If a node has .layout_info = NULL*, retrieve the .layout_info from its
            Caption parent... if still NULL*, retrieve it from its CaptionSet
        - If the retrieval still resulted in None, assign to it the Default
            region

        *: NULL means LayoutAwareBeautifulParser.NO_POSITIONING_INFO... but
            should really add a .__nonzero__ method to the layout, and to
            the its every child..?

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

    def _create_default_region_from_dict(self, region_id, region_spec):
        """
        :type region_id: unicode
        :type region_spec: dict
        """
        dfxp_region = self._dfxp.new_tag(u'region')
        dfxp_region.attrs.update({u'xml:id': region_id})

        attributes = _recreate_style(region_spec, self._dfxp)

        if attributes:
            dfxp_region.attrs.update(attributes)
            self._dfxp.find(u'layout').append(dfxp_region)

    @staticmethod
    def _collect_unique_regions(caption_set):
        """Iterate through all the nodes in the caption set, and return a list
        of all unique region specs (Layout objects)

        :type caption_set: CaptionSet
        :return: iterable containing these
        """
        unique_regions = set()
        # Get all the regions for all the <div>'s..corresponding to all the
        # languages
        languages = caption_set.get_languages()
        for lang in languages:
            unique_regions.add(caption_set.get_layout_info(lang))

            # Get the regions of all the captions.. (the <p> tags)
            for caption in caption_set.get_captions(lang):
                unique_regions.add(caption.layout_info)

                # The regions of all the text/br/style nodes
                for node in caption.nodes:
                    unique_regions.add(node.layout_info)
        unique_regions.discard(None)
        return unique_regions

    @staticmethod
    def _create_unique_regions(unique_layouts, dfxp, id_factory):
        """Create each one of the regions in the list, inside the dfxp
        document, under the 'layout' section.

        :type unique_layouts: set
        :param unique_layouts: a set of geometry.Layout instances, describing
            the properties to be added to the dfxp regions
        :type dfxp: BeautifulSoup
        :param id_factory: A callable which generates unique IDs
        :return: a dict, mapping each unique layout to the ID of the region
            created for it
        :rtype: dict
        """
        region_map = {}
        layout_section = dfxp.find(u'layout')

        for region_spec in unique_layouts:
            if (region_spec.origin or region_spec.extent or region_spec.padding or region_spec.alignment):
                new_region = dfxp.new_tag(u'region')
                new_id = id_factory()
                new_region[u'xml:id'] = new_id

                region_map[region_spec] = new_id
                if region_spec.origin:
                    new_region[u'tts:origin'] = (
                        region_spec.origin.to_xml_attribute())
                if region_spec.extent:
                    new_region[u'tts:extent'] = (
                        region_spec.extent.to_xml_attribute())
                if region_spec.padding:
                    new_region[u'tts:padding'] = (
                        region_spec.padding.to_xml_attribute())

                layout_section.append(new_region)
        return region_map

    def create_document_regions(self):
        """Create the <region> tags required to position all the captions.
        """
        self._create_default_region_from_dict(
            DFXP_DEFAULT_REGION_ID, DFXP_DEFAULT_REGION)
        unique_regions = self._collect_unique_regions(self._caption_set)

        self._region_map = self._create_unique_regions(
            unique_regions, self._dfxp, self._get_new_id)

    def _get_new_id(self, prefix=u'r'):
        """Return new, unique ids (use an internal counter).

        :type prefix: unicode
        """
        new_id = unicode((prefix or u'') + unicode(self._id_seed))
        self._id_seed += 1
        return new_id

    def assign_region_id(
            self, lang, caption_set=None, caption=None, caption_node=None):
        """For the given element will return a valid region ID, used for
        assigning to the element.

        For the region_id to be returned for the entire CaptionSet, don't
        supply the `caption` or `caption_node` params.

        For the region_id to be returned for the Caption, don't supply the
        `caption_node` param

        <div> tags mean the caption is None and caption_node is None.
        <p> tags mean the caption_node is None

        :type lang: unicode
        :param lang: the language of the current caption element
        :type caption_set: CaptionSet
        :type caption: Caption
        :type caption_node: CaptionNode
        :rtype: unicode
        """
        # More intelligent people would have used an elem.parent.parent..parent
        # pattern, but pycaption is not yet structured for this. 3 params
        # is not too much of a bother. If someone wants to make the structure
        # tree-like, they can easily change this.
        layout_info = None
        if caption_node:
            layout_info = caption_node.layout_info

        if not layout_info and caption:
            layout_info = caption.layout_info

        if not layout_info and caption_set:
            layout_info = caption_set.get_layout_info(lang)

        region_id = self._region_map.get(layout_info)

        if not region_id and not self._region_map:
            region_id = DFXP_DEFAULT_REGION_ID

        return region_id


def _recreate_style(content, dfxp):
    dfxp_style = {}

    # TODO - don't really know, but the 'region' check might possibly have to
    # be excluded. Regions are handled by the specialized classes now. They're
    # not treated as styling info.
    if u'region' in content:
        if dfxp.find(u'region', {u'xml:id': content[u'region']}):
            dfxp_style[u'region'] = content[u'region']
    if u'class' in content:
        if dfxp.find(u"style", {u"xml:id": content[u'class']}):
            dfxp_style[u'style'] = content[u'class']
    if u'text-align' in content:
        dfxp_style[u'tts:textAlign'] = content[u'text-align']
    if u'italics' in content:
        dfxp_style[u'tts:fontStyle'] = u'italic'
    if u'font-family' in content:
        dfxp_style[u'tts:fontFamily'] = content[u'font-family']
    if u'font-size' in content:
        dfxp_style[u'tts:fontSize'] = content[u'font-size']
    if u'color' in content:
        dfxp_style[u'tts:color'] = content[u'color']
    if u'display-align' in content:
        dfxp_style[u'tts:displayAlign'] = content[u'display-align']

    return dfxp_style


# TODO - highly cacheable. use WeakValueDict to improve performance
def _create_internal_alignment(text_align, display_align):
    """Given the 2 DFXP specific attributes, return the internal representation
    of an alignment

    In DFXP, the tts:textAlign can have the values
        "left", "center", "right", "start" and "end"
        with the default being "start".
    We interpret "start" as "left"... we don't yet support languages
    with right-to-left writing

    The "tts:displayAlign" can have the values
        "before", "center" and "after",
    with the default of "before". These refer to top/bottom positioning.

    :type text_align: unicode
    :type display_align: unicode
    :rtype: Alignment
    """
    if not (text_align or display_align):
        return None

    horizontal = None
    vertical = None

    if text_align == u'left' or not text_align:
        horizontal = HorizontalAlignmentEnum.LEFT

    if text_align == u'start':
        horizontal = HorizontalAlignmentEnum.START

    if text_align == u'center':
        horizontal = HorizontalAlignmentEnum.CENTER

    if text_align == u'right':
        horizontal = HorizontalAlignmentEnum.RIGHT

    if text_align == u'end':
        horizontal = HorizontalAlignmentEnum.END

    if display_align == u'before' or not display_align:
        vertical = VerticalAlignmentEnum.TOP

    if display_align == u'center':
        vertical = VerticalAlignmentEnum.CENTER

    if display_align == u'after':
        vertical = VerticalAlignmentEnum.BOTTOM

    return Alignment(horizontal, vertical)


def _get_usable_attribute_value(tag, attr_name, factory,
                                ignore_vals=(u"auto",)):
    """For the xml `tag`, tries to retrieve the attribute `attr_name` and
    pass that to the factory in order to get a result. If the value of the
    attribute is in the `ignore_vals` iterable, returns None.

    :param tag: a BeautifulSoup tag
    :param attr_name: a string; represents an xml attribute name
    :param factory: a callable to transform the attribute into something
        usable (such as the classes from .geometry)
    :param ignore_vals: iterable of attribute values to ignore
    :raise CaptionReadSyntaxError: if the attribute has some crazy value
    """
    attr_value = None
    if tag.has_attr(attr_name):
        attr_value = tag.get(attr_name)

    if attr_value is None:
        return

    usable_value = None

    if attr_value not in ignore_vals:
        try:
            usable_value = factory(attr_value)
        except ValueError as err:
            raise CaptionReadSyntaxError(err)

    return usable_value