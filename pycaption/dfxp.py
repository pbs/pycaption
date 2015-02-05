from bs4 import BeautifulSoup, NavigableString
from xml.sax.saxutils import escape

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE)
from .exceptions import CaptionReadNoCaptions, CaptionReadSyntaxError
from .geometry import Point, Stretch, UnitEnum, Padding
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
        self.nodes = []

    def detect(self, content):
        if u'</tt>' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        if type(content) != unicode:
            raise RuntimeError(u'The content is not a unicode string.')

        dfxp_soup = LayoutAwareBeautifulSoup(content)
        captions = CaptionSet()

        # Each div represents all the captions for a single language.
        for div in dfxp_soup.find_all(u'div'):
            lang = div.attrs.get(u'xml:lang', DEFAULT_LANGUAGE_CODE)
            captions.set_captions(lang, self._translate_div(div))

        for style in dfxp_soup.find_all(u'style'):
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

        caption = Caption()
        caption.start = start
        caption.end = end
        caption.nodes = self.nodes
        caption.style = styles
        caption.layout_info = p_tag.layout_info
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
                node = CaptionNode.create_text(tag.strip())
                self.nodes.append(node)
        # convert line breaks
        elif tag.name == u'br':
            self.nodes.append(CaptionNode.create_break())
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
            node = CaptionNode.create_style(True, args)
            node.start = True
            node.content = args
            self.nodes.append(node)

            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            node = CaptionNode.create_style(False, args)
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

    def write(self, captions, force=u''):
        dfxp = BeautifulSoup(DFXP_BASE_MARKUP, u'xml')
        dfxp.find(u'tt')[u'xml:lang'] = u"en"

        for style_id, style in captions.get_styles():
            if style != {}:
                dfxp = self._recreate_styling_tag(style_id, style, dfxp)
        if not captions.get_styles():
            dfxp = self._recreate_styling_tag(
                DFXP_DEFAULT_STYLE_ID, DFXP_DEFAULT_STYLE, dfxp)

        # XXX For now we will always use this default region. In the future if
        # regions are provided, they will be kept
        dfxp = self._recreate_region_tag(
            DFXP_DEFAULT_REGION_ID, DFXP_DEFAULT_REGION, dfxp)

        body = dfxp.find(u'body')

        if force:
            langs = [self._force_language(force, captions.get_languages())]
        else:
            langs = captions.get_languages()

        for lang in langs:
            div = dfxp.new_tag(u'div')
            div[u'xml:lang'] = u'%s' % lang

            for caption in captions.get_captions(lang):
                if caption.style:
                    caption_style = caption.style
                    caption_style.update({u'region': DFXP_DEFAULT_REGION_ID})
                else:
                    caption_style = {u'class': DFXP_DEFAULT_STYLE_ID,
                                     u'region': DFXP_DEFAULT_REGION_ID}
                p = self._recreate_p_tag(caption, caption_style, dfxp)
                div.append(p)

            body.append(div)

        caption_content = dfxp.prettify(formatter=None)
        return caption_content

    # force the DFXP to only have one language, trying to match on "force"
    def _force_language(self, force, langs):
        for lang in langs:
            if force == lang:
                return lang

        return langs[-1]

    def _recreate_region_tag(self, region_id, styling, dfxp):
        dfxp_region = dfxp.new_tag(u'region')
        dfxp_region.attrs.update({u'xml:id': region_id})

        attributes = self._recreate_style(styling, dfxp)
        dfxp_region.attrs.update(attributes)

        new_tag = dfxp.new_tag(u'region')
        new_tag.attrs.update({u'xml:id': region_id})
        if dfxp_region != new_tag:
            dfxp.find(u'layout').append(dfxp_region)
        return dfxp

    def _recreate_styling_tag(self, style, content, dfxp):
        dfxp_style = dfxp.new_tag(u'style')
        dfxp_style.attrs.update({u'xml:id': style})

        attributes = self._recreate_style(content, dfxp)
        dfxp_style.attrs.update(attributes)

        new_tag = dfxp.new_tag(u'style')
        new_tag.attrs.update({u'xml:id': style})
        if dfxp_style != new_tag:
            dfxp.find(u'styling').append(dfxp_style)

        return dfxp

    def _recreate_p_tag(self, caption, caption_style, dfxp):
        start = caption.format_start()
        end = caption.format_end()
        p = dfxp.new_tag(u"p", begin=start, end=end)
        p.string = self._recreate_text(caption, dfxp)

        if dfxp.find(u"style", {u"xml:id": u"p"}):
            p[u'style'] = u'p'

        p.attrs.update(self._recreate_style(caption_style, dfxp))

        return p

    def _recreate_text(self, caption, dfxp):
        line = u''

        for node in caption.nodes:
            if node.type == CaptionNode.TEXT:
                line += escape(node.content) + u' '

            elif node.type == CaptionNode.BREAK:
                line = line.rstrip() + u'<br/>\n    '

            elif node.type == CaptionNode.STYLE:
                line = self._recreate_span(line, node, dfxp)

        return line.rstrip()

    def _recreate_span(self, line, node, dfxp):
        if node.start:
            styles = u''

            content_with_style = self._recreate_style(node.content, dfxp)
            for style, value in content_with_style.items():
                styles += u' %s="%s"' % (style, value)

            if styles:
                if self.open_span:
                    line = line.rstrip() + u'</span> '
                line += u'<span%s>' % styles
                self.open_span = True

        elif self.open_span:
            line = line.rstrip() + u'</span> '
            self.open_span = False

        return line

    def _recreate_style(self, content, dfxp):
        dfxp_style = {}

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


class LayoutAwareBeautifulSoup(BeautifulSoup):
    """This makes the xml instance capable of providing layout information
    for every one of its nodes (it adds a 'layout_info' attribute on each node)

    It parses the element tree in post-order-like fashion (as dictated by the
    dfxp specs http://www.w3.org/TR/ttaf1-dfxp/#semantics-region-layout-step-1)
    for determining the layout information
    """
    # A lot of elements will have no positioning info. Use this flyweight
    # to save memory
    NO_POSITIONING_INFO = (None,) * 3

    def __init__(self, markup=u"", features="html.parser", builder=None,
                 parse_only=None, from_encoding=None, **kwargs):
        """The `features` param determines the parser to be used. The parsers
        are usually html parsers, some more forgiving than others, and as such
        they do stuff very differently especially for xml files. We chose this
        one because even though the docs say it's slower, it just "works".

        The reason why we haven't used the 'xml' parser is that it destroys
        characters such as < or & (even the escaped ones).

        Check out the docs below for explanation.
        http://www.crummy.com/software/BeautifulSoup/bs4/doc/#installing-a-parser
        """
        super(LayoutAwareBeautifulSoup, self).__init__(
            markup, features, builder, parse_only, from_encoding, **kwargs)

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
        element.layout_info = self._extract_positioning_information(region_id)

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

    def _extract_positioning_information(self, region_id):
        """Returns a tuple containing positioning information
        :param region_id: the id of the region to which the element is
            associated
        :return: see caller
        """
        if region_id is None:
            return self.NO_POSITIONING_INFO

        region_list = self.findAll('region', {'xml:id': region_id})

        if not region_list:
            return self.NO_POSITIONING_INFO

        if len(region_list) > 1:
            raise CaptionReadSyntaxError(
                u'Invalid caption file. '
                u'More than 1 region with the same id: {id}'
                .format(id=region_id)
            )
        region = LayoutAwareRegion(self, region_list[0])
        return Layout(*region.get_positioning_info())


class LayoutAwareRegion(object):
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
            referenced_styles = styling_tag.get('style', {'xml:id': reference})

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

    def get_positioning_info(self):
        """Determines the positioning information tuple (origin, extent, padding)
        from the region element.

        The 3 attributes can be specified inline, on the region node, on child
        tags of type <style> or on referenced <style> tags.
        """
        origin = self._find_origin()
        extent = self._find_extent()
        padding = self._find_padding()

        return origin, extent, padding

    @staticmethod
    def _get_usable_attribute_value(tag, attr_name, factory,
                                    ignore_vals=("auto",)):
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

    def _find_origin(self):
        """Finds the "tts:origin" for this region.

        The tts:origin attribute is either specified on the region, on its
        styles or referenced styles, or it's taken from the document root

        :return: .geometry.Point instance, or None
        """
        attribute_name = u'tts:origin'

        # Does self.region have the attribute?
        origin = self._get_usable_attribute_value(
            self.region, attribute_name, Point.from_dfxp_attribute
        )

        # Do any of its style have the attribute?
        if not origin:
            for style in self.styles:
                origin = self._get_usable_attribute_value(
                    style, attribute_name, Point.from_dfxp_attribute
                )
                # get the first value met in the style chain
                if origin:
                    break

        return origin

    def _find_extent(self):
        """Finds the "tts:extent" for this region.

        The tts:extent attribute, like the "tts:origin", can be specified on
        the region, its styles, or can be inherited from the root <tt> element.
        For the latter case, it must be specified in the unit 'pixel'.

        :return .geometry.Stretch, or None
        """
        attribute_name = u'tts:extent'

        # Does self.region have the attribute?
        extent = self._get_usable_attribute_value(
            self.region, attribute_name, Stretch.from_dfxp_attribute
        )

        # Do any of its style have the attribute?
        if extent is None:
            for style in self.styles:
                extent = self._get_usable_attribute_value(
                    style, attribute_name, Stretch.from_dfxp_attribute
                )
                if extent:
                    break

        # Does the root 'tt' element have it?
        if extent is None:
            root = self.document.findAll('tt')[0]
            extent = self._get_usable_attribute_value(
                root, attribute_name, Stretch.from_dfxp_attribute
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

    def _find_padding(self):
        """Finds the "tts:padding" for this region, and returns it as a 4-tuple
        of .geometry.Size objects

        Just like the extent and the origin, this attribute is not inheritable,
        and should only appear specified on the region (or its many styles).
        While this algorithm is short-circuited, many attributes might not
        work in the same way, so please maku sure to read the docs if extending
        Dfxp is complicated...
        http://www.w3.org/TR/ttaf1-dfxp/#style-attribute-padding

        Same observations as for self._find_extent and self._find_origin
        """
        attribute_name = u'tts:padding'

        # Does self.region have the attribute?
        padding = self._get_usable_attribute_value(
            self.region, attribute_name, Padding.from_dfxp_attribute, []
        )

        # Do any of its style have the attribute?
        if padding is None:
            for style in self.styles:
                padding = self._get_usable_attribute_value(
                    style, attribute_name, Padding.from_dfxp_attribute, []
                )
                if padding:
                    break

        return padding