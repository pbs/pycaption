from collections import deque
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser, HTMLParseError
from logging import FATAL
from xml.sax.saxutils import escape

from cssutils import parseString, log, css as cssutils_css
from bs4 import BeautifulSoup, NavigableString

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE)
from .exceptions import CaptionReadNoCaptions, CaptionReadSyntaxError
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
        self.line = []

    def detect(self, content):
        if u'<sami' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        if type(content) != unicode:
            raise RuntimeError('The content is not a unicode string.')

        content, doc_styles, doc_langs = SAMIParser().feed(content)
        sami_soup = BeautifulSoup(content)
        captions = CaptionSet()
        captions.set_styles(doc_styles)
        layout_info = self._build_layout(doc_styles.get('p', {}))

        for language in doc_langs:
            captions.set_layout_info(language, layout_info)
            lang_captions = self._translate_lang(language, sami_soup)
            captions.set_captions(language, lang_captions)

        if captions.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return captions

    def _build_layout(self, styles):
        """
        :type styles: dict
        :param styles: a dictionary CSS-like with styling rules
        """
        alignment = Alignment.from_horizontal_and_vertical_align(
            text_align=styles.get('text-align', None)
        )
        layout = Layout(
            origin=None,
            extent=None,
            padding=self._get_padding(styles),
            alignment=alignment
        )
        return layout

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

    def _translate_lang(self, language, sami_soup):
        captions = []
        milliseconds = 0

        for p in sami_soup.select(u'p[lang|=%s]' % language):
            milliseconds = int(float(p.parent[u'start']))
            start = milliseconds * 1000
            end = 0

            if captions != [] and captions[-1].end == 0:
                captions[-1].end = milliseconds * 1000

            if p.get_text().strip():
                styles = self._translate_attrs(p)
                layout_info = self._build_layout(styles)
                self.line = []
                self._translate_tag(p, layout_info)
                text = self.line
                caption = Caption(layout_info=layout_info)
                caption.start = start
                caption.end = end
                caption.nodes = text
                caption.style = styles
                captions.append(caption)

        if captions and captions[-1].end == 0:
            # Arbitrarily make this last 4 seconds. Not ideal...
            captions[-1].end = (milliseconds + 4000) * 1000

        return captions

    def _translate_tag(self, tag, inherited_layout=None):
        """
        :param inherited_layout: A Layout object extracted from an ancestor tag
                to be attached to leaf nodes
        """
        # convert text
        if isinstance(tag, NavigableString):
            # BeautifulSoup apparently handles unescaping character codes
            # (e.g. &amp;) automatically. The following variable, therefore,
            # should contain a plain unicode string.
            text = tag.strip()
            if not text:
                return
            self.line.append(CaptionNode.create_text(text, inherited_layout))
        # convert line breaks
        elif tag.name == u'br':
            self.line.append(CaptionNode.create_break(inherited_layout))
        # convert italics
        elif tag.name == u'i':
            self.line.append(
                CaptionNode.create_style(True, {u'italics': True})
            )
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            self.line.append(
                CaptionNode.create_style(False, {u'italics': True}))
        elif tag.name == u'span':
            self._translate_span(tag)
        else:
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a, inherited_layout)

    def _translate_span(self, tag):
        # convert tag attributes
        args = self._translate_attrs(tag)
        # only include span tag if attributes returned
        if args:
            layout_info = self._build_layout(args)
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
                self._translate_tag(a)

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

    # convert attributes from CSS
    def _translate_style(self, attrs, styles):
        for style in styles:
            style = style.split(u':')
            if style[0] == u'text-align':
                attrs[u'text-align'] = style[1].strip()
            elif style[0] == u'font-family':
                attrs[u'font-family'] = style[1].strip()
            elif style[0] == u'font-size':
                attrs[u'font-size'] = style[1].strip()
            elif style[0] == u'font-style' and style[1].strip() == u'italic':
                attrs[u'italics'] = True
            elif style[0] == u'lang':
                attrs[u'lang'] = style[1].strip()
            elif style[0] == u'color':
                attrs[u'color'] = style[1].strip()

        return attrs


class SAMIWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.open_span = False
        self.last_time = None

    def write(self, captions):
        sami = BeautifulSoup(SAMI_BASE_MARKUP, u"xml")
        stylesheet = self._recreate_stylesheet(captions)
        sami.find(u'style').append(stylesheet)
        primary = None

        for lang in captions.get_languages():
            self.last_time = None
            if primary is None:
                primary = lang
            for caption in captions.get_captions(lang):
                sami = self._recreate_p_tag(
                    caption, sami, lang, primary, captions)

        a = sami.prettify(formatter=None).split(u'\n')
        caption_content = u'\n'.join(a[1:])
        return caption_content

    def _recreate_p_tag(self, caption, sami, lang, primary, captions):
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

    def _recreate_stylesheet(self, captions):
        stylesheet = u'<!--'

        for attr, value in captions.get_styles():
            if value != {}:
                stylesheet += self._recreate_style_tag(attr, value)

        for lang in captions.get_languages():
            lang_string = u'lang: {}'.format(lang)
            if lang_string not in stylesheet:
                stylesheet += (
                    u'\n    .{lang} {{\n     lang: {lang};\n    }}\n'
                ).format(lang=lang)

        return stylesheet + u'   -->'

    def _recreate_style_tag(self, style, content):
        if style not in [u'p', u'sync', u'span']:
            element = u'.'
        else:
            element = u''

        sami_style = u'\n    %s%s {\n    ' % (element, style)

        for attr, value in self._recreate_style(content).items():
            sami_style += u' %s: %s;\n    ' % (attr, value)

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

    def _recreate_style(self, content):
        sami_style = {}

        if u'text-align' in content:
            sami_style[u'text-align'] = content[u'text-align']
        if u'italics' in content:
            sami_style[u'font-style'] = u'italic'
        if u'font-family' in content:
            sami_style[u'font-family'] = content[u'font-family']
        if u'font-size' in content:
            sami_style[u'font-size'] = content[u'font-size']
        if u'color' in content:
            sami_style[u'color'] = content[u'color']
        if u'lang' in content:
            sami_style[u'lang'] = content[u'lang']

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
        self.langs = {}
        self.last_element = u''
        self.name2codepoint = name2codepoint.copy()
        self.name2codepoint[u'apos'] = 0x0027

    # override the parser's handling of starttags
    def handle_starttag(self, tag, attrs):
        self.last_element = tag

        # treat divs as spans
        if tag == u'div':
            tag = u'span'

        if tag == u'i':
            tag = u'span'
            attrs = [(u'style', u'font-style:italic;')]

        # figure out the caption language of P tags
        if tag == u'p':
            lang = self._find_lang(attrs)

            # if no language detected, set it as the default
            lang = lang or DEFAULT_LANGUAGE_CODE
            attrs.append((u'lang', lang))
            self.langs[lang] = 1

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
        if tag == u'div' or tag == u'i':
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
        # parse via cssutils modules
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
