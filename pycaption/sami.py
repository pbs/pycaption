"""
The classes in this module handle SAMI reading and writing. It supports several
CSS attributes, some of which are handled as positioning settings (and applied
to Layout objects) and others as simple styling (applied to legacy style nodes).

The following attributes are handled as positioning:

    'text-align' # Converted to Alignment
    'margin-top'
    'margin-right'
    'margin-bottom'
    'margin-left'

OBS:
    * Margins are converted to Padding
    * Margins defined inline are not supported
      TODO: Add support for inline margins

Any other CSS the BeautifulSoup library manages to parse is handled as simple
styling and applied to style nodes. However, apparently only these are actually
used by writers on conversion:

    'font-family'
    'font-size'
    'font-style'
    'color'
OBS:
    * Other parameters are preserved, but not if they're specified inline.
    TODO:
      Make this less confusing. Confirm whether these really are the only
      supported styling attributes and make it more clear, perhaps by listing
      them in constants in the beginning of the file and using them to filter
      out unneeded attributes either everywhere in the code or not at all, but
      most importantly regardless of whether they're defined inline or not,
      because this is irrelevant.

"""
import re

from collections import deque
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser, HTMLParseError
from logging import FATAL
from xml.sax.saxutils import escape
from copy import deepcopy

from cssutils import parseString, log, css as cssutils_css
from bs4 import BeautifulSoup, NavigableString

from .base import (
    BaseReader, BaseWriter, CaptionSet, CaptionList, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE)
from .exceptions import (
    CaptionReadNoCaptions, CaptionReadSyntaxError, InvalidInputError)
from .geometry import (
    Layout, Alignment, Padding, Size
)


# change cssutils default logging
log.setLevel(FATAL)


SAMI_BASE_MARKUP = u'''
<sami>
    <head>
        <style type="text/css"/>
    </head>
    <body/>
</sami>'''


class SAMIReader(BaseReader):
    def __init__(self, *args, **kw):
        super(SAMIReader, self).__init__(*args, **kw)

        self.line = []
        self.first_alignment = None

    def detect(self, content):
        if u'<sami' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        if type(content) != unicode:
            raise InvalidInputError('The content is not a unicode string.')

        content, doc_styles, doc_langs = (
            self._get_sami_parser_class()().feed(content))
        sami_soup = self._get_xml_parser_class()(content)

        # Get the global layout that applies to all <p> tags
        global_layout = self._build_layout(doc_styles.get('p', {}))

        caption_dict = {}
        for language in doc_langs:
            lang_layout = None
            for target, styling in doc_styles.items():
                if target not in [u'p', u'sync', u'span']:
                    if styling.get(u'lang', None) == language:
                        lang_layout = self._build_layout(
                            doc_styles.get(target, {}),
                            inherit_from=global_layout
                        )
                        break
            lang_layout = lang_layout or global_layout
            lang_captions = self._translate_lang(
                language, sami_soup, lang_layout)

            caption_dict[language] = lang_captions

        caption_set = CaptionSet(
            caption_dict,
            layout_info=global_layout
        )

        # Convert styles from CSS to internal representation
        for style in doc_styles.items():
            style = (style[0], self._translate_parsed_style(style[1]))

        caption_set.set_styles(doc_styles)

        if caption_set.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return caption_set

    @staticmethod
    def _get_sami_parser_class():
        """Hook method for providing custom SAMIParser classes"""
        return SAMIParser

    @staticmethod
    def _get_xml_parser_class():
        """Hook method for providing a custom XML parser class"""
        return BeautifulSoup

    def _build_layout(self, styles, inherit_from=None):
        """
        :type styles: dict
        :param styles: a dictionary with CSS-like styling rules

        :type inherit_from: Layout
        :param inherit_from: The Layout with values to be used in case the
            positioning settings in the styles parameter don't specify
            something.
        """
        if self.ignore_layout:
            return None

        alignment = Alignment.from_horizontal_and_vertical_align(
            text_align=styles.get('text-align')
        )
        return self._get_layout_class()(
            origin=None,
            extent=None,
            padding=self._get_padding(styles),
            alignment=alignment,
            inherit_from=inherit_from
        )

    @staticmethod
    def _get_layout_class():
        """Hook method for providing a custom Layout class"""
        return Layout

    def _get_padding(self, styles):
        margin_before = self._get_size(styles, 'margin-top')
        margin_after = self._get_size(styles, 'margin-bottom')
        margin_start = self._get_size(styles, 'margin-left')
        margin_end = self._get_size(styles, 'margin-right')
        if not any([margin_before, margin_after, margin_start, margin_end]):
            return None
        return Padding(
            before=margin_before,  # top
            after=margin_after,  # bottom
            start=margin_start,  # left
            end=margin_end  # right
        )

    def _get_size(self, styles, style_label):
        value_from_style = styles.get(style_label, None)
        if not value_from_style:
            return None
        return Size.from_string(value_from_style)

    def _translate_lang(self, language, sami_soup, parent_layout):
        """
        For a given language, translate the SAMI XML to internal list of
        captions.

        :rtype: list
        """
        captions = CaptionList(layout_info=parent_layout)
        milliseconds = 0

        for p in sami_soup.select(u'p[lang|=%s]' % language):
            milliseconds = int(float(p.parent[u'start']))
            start = milliseconds * 1000
            end = 0

            if captions != [] and captions[-1].end == 0:
                captions[-1].end = milliseconds * 1000

            if p.get_text().strip():
                self.first_alignment = None
                styles = self._translate_attrs(p)
                layout_info = self._build_layout(styles,
                                                 inherit_from=parent_layout)
                self.line = []

                self._translate_tag(p, layout_info)

                if self.ignore_layout:
                    caption_layout = None
                else:
                    caption_layout = self._get_layout_class()(
                        alignment=self.first_alignment,
                        inherit_from=layout_info
                    )
                    for node in self.line:
                        node.layout_info = Layout(
                            alignment=self.first_alignment,
                            inherit_from=node.layout_info
                        )

                self.first_alignment = None

                caption = Caption(start, end, self.line, styles, caption_layout)
                captions.append(caption)

        if captions and captions[-1].end == 0:
            # Arbitrarily make this last 4 seconds. Not ideal...
            captions[-1].end = (milliseconds + 4000) * 1000

        return captions

    def _get_style_name_from_tag(self, tag):
        if tag == u'i':
            return u'italics'
        elif tag == u'b':
            return u'bold'
        elif tag == u'u':
            return u'underline'
        else:
            raise RuntimeError("Unknown style tag")

    def _translate_tag(self, tag, inherit_from=None):
        """
        :param inherit_from: A Layout object extracted from an ancestor tag
                to be attached to leaf nodes
        """
        # convert text
        if isinstance(tag, NavigableString):
            # BeautifulSoup apparently handles unescaping character codes
            # (e.g. &amp;) automatically. The following variable, therefore,
            # should contain a plain unicode string.
            # strips indentation whitespace only
            pattern = re.compile(u"^(?:[\n\r]+\s*)?(.+)")
            result = pattern.search(tag)
            if not result:
                return
            tag_text = result.groups()[0]
            self.line.append(CaptionNode.create_text(tag_text, inherit_from))
        # convert line breaks
        elif tag.name == u'br':
            self.line.append(CaptionNode.create_break(inherit_from))
        # convert italics, bold, and underline
        elif tag.name == u'i' or tag.name == u'b' or tag.name == u'u':
            style_name = self._get_style_name_from_tag(tag.name)
            self.line.append(
                CaptionNode.create_style(True, {style_name: True})
            )
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a, inherit_from)
            self.line.append(
                CaptionNode.create_style(False, {style_name: True}))
        elif tag.name == u'span':
            self._translate_span(tag, inherit_from)
        else:
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a, inherit_from)

    def _translate_span(self, tag, inherit_from=None):
        # convert tag attributes
        args = self._translate_attrs(tag)
        # only include span tag if attributes returned
        if args:
            layout_info = self._build_layout(args, inherit_from)
            # OLD: Create legacy style node
            # NEW: But pass new layout object
            node = CaptionNode.create_style(True, args, layout_info)
            self.line.append(node)
            # recursively call function for any children elements
            for a in tag.contents:
                # NEW: Pass the layout along so that it's eventually attached
                # to leaf nodes (e.g. text or break)
                self._translate_tag(a, layout_info)
            node = CaptionNode.create_style(False, args, layout_info)
            self.line.append(node)
        else:
            for a in tag.contents:
                self._translate_tag(a, inherit_from)

    def _translate_attrs(self, tag):
        attrs = {}
        css_attrs = tag.attrs

        if u'class' in css_attrs:
            attrs[u'class'] = css_attrs[u'class'][0].lower()
        if u'id' in css_attrs:
            attrs[u'class'] = css_attrs[u'id'].lower()
        if u'style' in css_attrs:
            styles = css_attrs[u'style'].split(u';')
            attrs.update(self._translate_style(attrs, styles))

        return attrs

    # convert attributes from inline CSS
    def _translate_style(self, attrs, styles):
        for style in styles:
            style = style.split(u':')
            if len(style) == 2:
                css_property, value = style
            else:
                continue
            if css_property == u'text-align':
                self._save_first_alignment(value.strip())
            else:
                self._translate_css_property(attrs, css_property, value)

        return attrs

    def _translate_parsed_style(self, styles):
        # Keep unknown styles by default
        attrs = styles
        for css_property, value in styles.items():
            self._translate_css_property(attrs, css_property, value)

        return attrs

    def _translate_css_property(self, attrs, css_property, value):
        if css_property == u'font-family':
            attrs[u'font-family'] = value.strip()
        elif css_property == u'font-size':
            attrs[u'font-size'] = value.strip()
        elif css_property == u'font-style' and value.strip() == u'italic':
            attrs[u'italics'] = True
        elif css_property == u'text-decoration' and value.strip() == u'underline':
            attrs[u'underline'] = True
        elif css_property == u'font-weight' and value.strip() == u'bold':
            attrs[u'bold'] = True
        elif css_property == u'lang':
            attrs[u'lang'] = value.strip()
        elif css_property == u'color':
            attrs[u'color'] = value.strip()

    def _save_first_alignment(self, align):
        """
        Unlike the other inline CSS attributes parsed in _translate_styles, the
        'text-align' setting must be applied to a Layout and not to a style
        because it affects positioning. This Layout must be assigned to the
        Caption object, and not a Node, because it doesn't make sense to have
        spans in the same caption with different alignments. Even though the
        SAMI format seems to in principle accept it, pycaption normalizes to
        something it can make sense of internally and convert to other formats.

        If there are multiple elements (span, div, etc) in the same line with
        different alignments, only the first alignment is taken into account.

        If the root element of the caption (sync's first child) has an inline
        text-align, it is preserved and any children alignment is ignored.

        :param align: A unicode string representing a CSS text-align value
        """
        if not self.first_alignment:
            self.first_alignment = Alignment.from_horizontal_and_vertical_align(  # noqa
                text_align=align
            )


class SAMIWriter(BaseWriter):
    def __init__(self, *args, **kwargs):
        super(SAMIWriter, self).__init__(*args, **kwargs)
        self.open_span = False
        self.last_time = None

    def write(self, caption_set):
        caption_set = deepcopy(caption_set)
        sami = BeautifulSoup(SAMI_BASE_MARKUP, u"xml")

        caption_set.layout_info = self._relativize_and_fit_to_screen(
            caption_set.layout_info)

        primary = None

        for lang in caption_set.get_languages():
            self.last_time = None
            if primary is None:
                primary = lang

            caption_set.set_layout_info(
                lang,
                self._relativize_and_fit_to_screen(
                    caption_set.get_layout_info(lang))
            )

            for caption in caption_set.get_captions(lang):
                # Loop through all captions/nodes and apply transformations to
                # layout in function of the provided or default settings
                caption.layout_info = self._relativize_and_fit_to_screen(
                    caption.layout_info)
                for node in caption.nodes:
                    node.layout_info = self._relativize_and_fit_to_screen(
                        node.layout_info)
                sami = self._recreate_p_tag(
                    caption, sami, lang, primary, caption_set)

        stylesheet = self._recreate_stylesheet(caption_set)
        sami.find(u'style').append(stylesheet)

        a = sami.prettify(formatter=None).split(u'\n')
        caption_content = u'\n'.join(a[1:])
        return caption_content

    def _recreate_p_tag(self, caption, sami, lang, primary, captions):
        """
        Creates a p tag for the given caption, attach it to the sami object
        and return it.

        :type caption: Caption
        :type sami: BeautifulSoup
        :type lang: unicode
        :type primary: unicode
        :type captions: CaptionSet

        :rtype: BeautifulSoup
        """
        time = caption.start / 1000

        if self.last_time and time != self.last_time:
            sami = self._recreate_blank_tag(
                sami, caption, lang, primary, captions)

        self.last_time = caption.end / 1000

        sami, sync = self._recreate_sync(sami, lang, primary, time)

        p = sami.new_tag(u"p")

        p_style = u''
        for attr, value in self._recreate_style(caption.style).items():
            p_style += u'%s:%s;' % (attr, value)
        if p_style:
            p[u'p_style'] = p_style

        p[u'class'] = self._recreate_p_lang(caption, lang, captions)
        p.string = self._recreate_text(caption.nodes)

        sync.append(p)

        return sami

    def _recreate_sync(self, sami, lang, primary, time):
        """
        Creates a sync tag for a given language and timing (if it doesn't
        already exist), attach it to the sami body and return the sami
        BeautifulSoupobject.

        :type sami: BeautifulSoup
        :type lang: unicode
        :type primary: unicode
        :type time: int

        :rtype: BeautifulSoup
        """
        if lang == primary:
            sync = sami.new_tag(u"sync", start=u"%s" % time)
            sami.body.append(sync)
        else:
            sync = sami.find(u"sync", start=u"%s" % time)
            if sync is None:
                sami, sync = self._find_closest_sync(sami, time)

        return sami, sync

    def _find_closest_sync(self, sami, time):
        sync = sami.new_tag(u"sync", start=u"%s" % time)

        earlier = sami.find_all(u"sync", start=lambda x: int(x) < time)
        if earlier:
            last_sync = earlier[-1]
            last_sync.insert_after(sync)
        else:
            def later_syncs(start):
                return int(start) > time
            later = sami.find_all(u"sync", start=later_syncs)
            if later:
                last_sync = later[0]
                last_sync.insert_before(sync)
        return sami, sync

    def _recreate_blank_tag(self, sami, caption, lang, primary, captions):
        sami, sync = self._recreate_sync(sami, lang, primary, self.last_time)

        p = sami.new_tag(u"p")
        p[u'class'] = self._recreate_p_lang(caption, lang, captions)
        p.string = u'&nbsp;'

        sync.append(p)

        return sami

    def _recreate_p_lang(self, caption, lang, captions):
        try:
            if u'lang' in captions.get_style(caption.style[u'class']):
                return caption.style[u'class']
        except KeyError:
            pass
        return lang

    def _recreate_stylesheet(self, caption_set):
        stylesheet = u'<!--'

        for attr, value in caption_set.get_styles():
            if value != {}:
                stylesheet += self._recreate_style_block(
                    attr, value, caption_set.layout_info)

        for lang in caption_set.get_languages():
            lang_string = u'lang: {}'.format(lang)
            if lang_string not in stylesheet:
                stylesheet += self._recreate_style_block(
                    lang, {u'lang': lang}, caption_set.get_layout_info(lang))

        return stylesheet + u'   -->'

    def _recreate_style_block(self, target, rules, layout_info):
        """
        :param target: A unicode string representing the target of the styling
            rules.
        :param rules: A dictionary with CSS-like styling rules.

        :param layout_info: A Layout object providing positioning information
            to be converted to CSS
        """
        if target not in [u'p', u'sync', u'span']:
            # If it's not a valid SAMI element, then it's a custom class name
            selector = u'.{}'.format(target)
        else:
            selector = target

        sami_style = u'\n    {} {{\n    '.format(selector)

        if layout_info and layout_info.padding:
            rules.update({
                'margin-top': unicode(layout_info.padding.before),
                'margin-right': unicode(layout_info.padding.end),
                'margin-bottom': unicode(layout_info.padding.after),
                'margin-left': unicode(layout_info.padding.start),
            })

        for attr, value in self._recreate_style(rules).items():
            sami_style += u' {}: {};\n    '.format(attr, value)

        return sami_style + u'}\n'

    def _recreate_text(self, caption):
        line = u''

        for node in caption:
            if node.type_ == CaptionNode.TEXT:
                line += self._encode(node.content) + u' '
            elif node.type_ == CaptionNode.BREAK:
                line = line.rstrip() + u'<br/>\n    '
            elif node.type_ == CaptionNode.STYLE:
                line = self._recreate_line_style(line, node)

        return line.rstrip()

    def _recreate_line_style(self, line, node):
        if node.start:
            if self.open_span:
                line = line.rstrip() + u'</span> '
            line = self._recreate_span(line, node.content)
        else:
            if self.open_span:
                line = line.rstrip() + u'</span> '
                self.open_span = False

        return line

    def _recreate_span(self, line, content):
        style = u''
        klass = u''
        if u'class' in content:
            klass += u' class="%s"' % content[u'class']

        for attr, value in self._recreate_style(content).items():
            style += u'%s:%s;' % (attr, value)

        if style or klass:
            if style:
                style = u' style="%s"' % style
            line += u'<span%s%s>' % (klass, style)
            self.open_span = True

        return line

    def _recreate_style(self, rules):
        """
        :param rules: A dictionary with CSS-like styling rules
        """
        sami_style = {}

        for key, value in rules.items():
            # Recreate original CSS rules from internal style
            if key == u'italics' and value == True:
                sami_style[u'font-style'] = u'italic'
            elif key == u'bold' and value == True:
                sami_style[u'font-weight'] = u'bold'
            elif key == u'underline' and value == True:
                sami_style[u'text-decoration'] = u'underline'
            else:
                sami_style[key] = value

        return sami_style

    def _encode(self, s):
        """
        Encodes plain unicode string to proper SAMI file escaping special
        characters in case they appear in the string.
        :type s: unicode
        """
        return escape(s)


class SAMIParser(HTMLParser):
    def __init__(self, *args, **kw):
        HTMLParser.__init__(self, *args, **kw)
        self.sami = u''
        self.line = u''
        self.styles = {}
        self.queue = deque()
        self.langs = set()
        self.last_element = u''
        self.name2codepoint = name2codepoint.copy()
        self.name2codepoint[u'apos'] = 0x0027

    def handle_starttag(self, tag, attrs):
        """
        Override the parser's handling of starttags
        :param tag: unicode string indicating the tag type (e.g. "head" or "p")
        :param tag: list of attribute tuples of type (u'name', u'value')
        """
        self.last_element = tag

        # treat divs as spans
        if tag == u'div':
            tag = u'span'

        # figure out the caption language of P tags
        if tag == u'p':
            lang = self._find_lang(attrs)

            # if no language detected, set it as the default
            lang = lang or DEFAULT_LANGUAGE_CODE
            attrs.append((u'lang', lang))
            self.langs.add(lang)

        # clean-up line breaks
        if tag == u'br':
            self.sami += u"<br/>"
        # add tag to queue
        else:
            # if already in queue, first close tags off in LIFO order
            while tag in self.queue:
                closer = self.queue.pop()
                self.sami = self.sami + u"</%s>" % closer
            # open new tag in queue
            self.queue.append(tag)
            # add tag with attributes
            for attr, value in attrs:
                tag += u' %s="%s"' % (attr.lower(), value)
            self.sami += u"<%s>" % tag

    # override the parser's handling of endtags
    def handle_endtag(self, tag):
        # treat divs as spans
        if tag == u'div':
            tag = u'span'

        # handle incorrectly formatted sync/p tags
        if tag in [u'p', u'sync'] and tag == self.last_element:
            return

        # close off tags in LIFO order, if matching starting tag in queue
        while tag in self.queue:
            closing_tag = self.queue.pop()
            self.sami += u"</%s>" % closing_tag

    def handle_entityref(self, name):
        if name in [u'gt', u'lt']:
            self.sami += u'&%s;' % name
        else:
            try:
                self.sami += unichr(self.name2codepoint[name])
            except (KeyError, ValueError):
                self.sami += u'&%s' % name

        self.last_element = u''

    def handle_charref(self, name):
        if name[0] == u'x':
            self.sami += unichr(int(name[1:], 16))
        else:
            self.sami += unichr(int(name))

    # override the parser's handling of data
    def handle_data(self, data):
        self.sami += data
        self.last_element = u''

    # override the parser's feed function
    def feed(self, data):
        """
        :param data: Raw SAMI unicode string
        :returns: tuple (unicode, dict, set)
        """
        no_cc = u'no closed captioning available'

        if u'<html' in data.lower():
            raise CaptionReadSyntaxError(
                u'SAMI File seems to be an HTML file.')
        elif no_cc in data.lower():
            raise CaptionReadSyntaxError(u'SAMI File contains "%s"' % no_cc)

        # try to find style tag in SAMI
        try:
            # prevent BS4 error with huge SAMI files with unclosed tags
            index = data.lower().find(u"</head>")

            self.styles = self._css_parse(
                BeautifulSoup(data[:index]).find(u'style').get_text())
        except AttributeError:
            self.styles = {}

        # fix erroneous italics tags
        data = data.replace(u'<i/>', u'<i>')

        # fix awkward tags found in some SAMIs
        data = data.replace(u';>', u'>')
        try:
            HTMLParser.feed(self, data)
        except HTMLParseError as e:
            raise CaptionReadSyntaxError(e)

        # close any tags that remain in the queue
        while self.queue != deque([]):
            closing_tag = self.queue.pop()
            self.sami += u"</%s>" % closing_tag

        return self.sami, self.styles, self.langs

    # parse the SAMI's stylesheet
    def _css_parse(self, css):
        """
        Parse styling via cssutils modules
        :rtype: dict
        """
        sheet = parseString(css)
        style_sheet = {}

        for rule in sheet:
            new_style = {}
            selector = rule.selectorText.lower()
            if selector[0] in [u'#', u'.']:
                selector = selector[1:]
            # keep any style attributes that are needed
            for prop in rule.style:
                if prop.name == u'color':
                    cv = cssutils_css.ColorValue(prop.value)
                    # Code for RGB to hex conversion comes from
                    # http://bit.ly/1kwfBnQ
                    new_style[u'color'] = u"#%02x%02x%02x" % (
                        cv.red, cv.green, cv.blue)
                else:
                    new_style[prop.name] = prop.value
            if new_style:
                style_sheet[selector] = new_style

        return style_sheet

    def _find_lang(self, attrs):
        for attr, value in attrs:
            # if lang is an attribute of the tag
            if attr.lower() == u'lang':
                return value[:2]
            # if the P tag has a class, try and find the language
            if attr.lower() == u'class':
                try:
                    return self.styles[value.lower()][u'lang']
                except KeyError:
                    pass

        return None
