from collections import deque
from htmlentitydefs import name2codepoint
from HTMLParser import HTMLParser, HTMLParseError
from logging import FATAL
from xml.sax.saxutils import escape

from cssutils import parseString, log, css as cssutils_css
from bs4 import BeautifulSoup, NavigableString

from pycaption import BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode

# change cssutils default logging
log.setLevel(FATAL)

sami_base = '''
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
        if '<sami' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        content = self.force_byte_string(content)
        content, doc_styles, doc_langs = SAMIParser().feed(content)
        sami_soup = BeautifulSoup(content)
        captions = CaptionSet()
        captions.set_styles(doc_styles)

        for language in doc_langs:
            lang_captions = self._translate_lang(language, sami_soup)
            captions.set_captions(language, lang_captions)

        if not captions.is_empty():
            return captions
        else:
            raise SAMIReaderError("Empty Caption File")

    def _translate_lang(self, language, sami_soup):
        captions = []
        milliseconds = 0

        for p in sami_soup.select('p[lang|=%s]' % language):
            milliseconds = int(float(p.parent['start']))
            start = milliseconds * 1000
            end = 0

            if captions != [] and captions[-1].end == 0:
                captions[-1].end = milliseconds * 1000

            if p.get_text().strip():
                self.line = []
                self._translate_tag(p)
                text = self.line
                styles = self._translate_attrs(p)
                caption = Caption()
                caption.start = start
                caption.end = end
                caption.nodes = text
                caption.style = styles
                captions.append(caption)

        if captions and captions[-1].end == 0:
            # Arbitrarily make this last 4 seconds. Not ideal...
            captions[-1].end = (milliseconds + 4000) * 1000

        return captions

    def _translate_tag(self, tag):
        # convert text
        if isinstance(tag, NavigableString):
            self.line.append(CaptionNode.create_text(tag.strip()))
        # convert line breaks
        elif tag.name == 'br':
            self.line.append(CaptionNode.create_break())
        # convert italics
        elif tag.name == 'i':
            self.line.append(CaptionNode.create_style(True, {'italics': True}))
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            self.line.append(
                CaptionNode.create_style(False, {'italics': True}))
        elif tag.name == 'span':
            self._translate_span(tag)
        else:
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)

    def _translate_span(self, tag):
        # convert tag attributes
        args = self._translate_attrs(tag)
        # only include span tag if attributes returned
        if args != '':
            node = CaptionNode.create_style(True, args)
            self.line.append(node)
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            node = CaptionNode.create_style(False, args)
            self.line.append(node)
        else:
            for a in tag.contents:
                self._translate_tag(a)

    def _translate_attrs(self, tag):
        attrs = {}
        css_attrs = tag.attrs

        if 'class' in css_attrs:
            attrs['class'] = css_attrs['class'][0].lower()
        if 'id' in css_attrs:
            attrs['class'] = css_attrs['id'].lower()
        if 'style' in css_attrs:
            styles = css_attrs['style'].split(';')
            attrs.update(self._translate_style(attrs, styles))

        return attrs

    # convert attributes from CSS
    def _translate_style(self, attrs, styles):
        for style in styles:
            style = style.split(':')
            if style[0] == 'text-align':
                attrs['text-align'] = style[1].strip()
            elif style[0] == 'font-family':
                attrs['font-family'] = style[1].strip()
            elif style[0] == 'font-size':
                attrs['font-size'] = style[1].strip()
            elif style[0] == 'font-style' and style[1].strip() == 'italic':
                attrs['italics'] = True
            elif style[0] == 'lang':
                attrs['lang'] = style[1].strip()
            elif style[0] == 'color':
                attrs['color'] = style[1].strip()

        return attrs


class SAMIWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.open_span = False
        self.last_time = None

    def write(self, captions):
        sami = BeautifulSoup(sami_base, "xml")
        stylesheet = self._recreate_stylesheet(captions)
        sami.find('style').append(stylesheet)
        primary = None

        for lang in captions.get_languages():
            self.last_time = None
            if primary is None:
                primary = lang
            for caption in captions.get_captions(lang):
                sami = self._recreate_p_tag(
                    caption, sami, lang, primary, captions)

        a = sami.prettify(formatter=None).split('\n')
        caption_content = '\n'.join(a[1:])
        return self.force_byte_string(caption_content)

    def _recreate_p_tag(self, caption, sami, lang, primary, captions):
        time = caption.start / 1000

        if self.last_time and time != self.last_time:
            sami = self._recreate_blank_tag(
                sami, caption, lang, primary, captions)

        self.last_time = caption.end / 1000

        sami, sync = self._recreate_sync(sami, lang, primary, time)

        p = sami.new_tag("p")

        p_style = ''
        for attr, value in self._recreate_style(caption.style).items():
            p_style += '%s:%s;' % (attr, value)
        if p_style:
            p['p_style'] = p_style

        p['class'] = self._recreate_p_lang(caption, lang, captions)
        p.string = self._recreate_text(caption.nodes)

        sync.append(p)

        return sami

    def _recreate_sync(self, sami, lang, primary, time):
        if lang == primary:
            sync = sami.new_tag("sync", start="%s" % time)
            sami.body.append(sync)
        else:
            sync = sami.find("sync", start="%s" % time)
            if sync is None:
                sami, sync = self._find_closest_sync(sami, time)

        return sami, sync

    def _find_closest_sync(self, sami, time):
        sync = sami.new_tag("sync", start="%s" % time)

        earlier = sami.find_all("sync", start=lambda x: int(x) < time)
        if earlier:
            last_sync = earlier[-1]
            last_sync.insert_after(sync)
        else:
            def later_syncs(start):
                return int(start) > time
            later = sami.find_all("sync", start=later_syncs)
            if later:
                last_sync = later[0]
                last_sync.insert_before(sync)
        return sami, sync

    def _recreate_blank_tag(self, sami, caption, lang, primary, captions):
        sami, sync = self._recreate_sync(sami, lang, primary, self.last_time)

        p = sami.new_tag("p")
        p['class'] = self._recreate_p_lang(caption, lang, captions)
        p.string = '&nbsp;'

        sync.append(p)

        return sami

    def _recreate_p_lang(self, caption, lang, captions):
        try:
            if 'lang' in captions.get_style(caption.style['class']):
                return caption.style['class']
        except KeyError:
            pass
        return lang

    def _recreate_stylesheet(self, captions):
        stylesheet = '<!--'

        for attr, value in captions.get_styles():
            if value != {}:
                stylesheet += self._recreate_style_tag(attr, value)

        for lang in captions.get_languages():
            if 'lang: %s' % lang not in stylesheet:
                stylesheet += '\n    .%s {\n     lang: %s;\n    }\n' % (lang,
                                                                        lang)

        return stylesheet + '   -->'

    def _recreate_style_tag(self, style, content):
        if style not in ['p', 'sync', 'span']:
            element = '.'
        else:
            element = ''

        sami_style = '\n    %s%s {\n    ' % (element, style)

        for attr, value in self._recreate_style(content).items():
            sami_style += ' %s: %s;\n    ' % (attr, value)

        return sami_style + '}\n'

    def _recreate_text(self, caption):
        line = ''

        for node in caption:
            if node.type == CaptionNode.TEXT:
                line += escape(node.content) + ' '
            elif node.type == CaptionNode.BREAK:
                line = line.rstrip() + '<br/>\n    '
            elif node.type == CaptionNode.STYLE:
                line = self._recreate_line_style(line, node)

        return line.rstrip()

    def _recreate_line_style(self, line, node):
        if node.start:
            if self.open_span:
                line = line.rstrip() + '</span> '
            line = self._recreate_span(line, node.content)
        else:
            if self.open_span:
                line = line.rstrip() + '</span> '
                self.open_span = False

        return line

    def _recreate_span(self, line, content):
        style = ''
        klass = ''
        if 'class' in content:
            klass += ' class="%s"' % content['class']

        for attr, value in self._recreate_style(content).items():
            style += '%s:%s;' % (attr, value)

        if style or klass:
            if style:
                style = ' style="%s"' % style
            line += '<span%s%s>' % (klass, style)
            self.open_span = True

        return line

    def _recreate_style(self, content):
        sami_style = {}

        if 'text-align' in content:
            sami_style['text-align'] = content['text-align']
        if 'italics' in content:
            sami_style['font-style'] = 'italic'
        if 'font-family' in content:
            sami_style['font-family'] = content['font-family']
        if 'font-size' in content:
            sami_style['font-size'] = content['font-size']
        if 'color' in content:
            sami_style['color'] = content['color']
        if 'lang' in content:
            sami_style['lang'] = content['lang']

        return sami_style


class SAMIParser(HTMLParser):
    def __init__(self, *args, **kw):
        HTMLParser.__init__(self, *args, **kw)
        self.sami = u''
        self.line = ''
        self.styles = {}
        self.queue = deque()
        self.langs = {}
        self.last_element = ''
        self.name2codepoint = name2codepoint.copy()
        self.name2codepoint['apos'] = 0x0027

    # override the parser's handling of starttags
    def handle_starttag(self, tag, attrs):
        self.last_element = tag

        # treat divs as spans
        if tag == 'div':
            tag = 'span'

        if tag == 'i':
            tag = 'span'
            attrs = [('style', 'font-style:italic;')]

        # figure out the caption language of P tags
        if tag == 'p':
            lang = self._find_lang(attrs)

            # if no language detected, set it as "none"
            if not lang:
                lang = 'unknown'
            attrs.append(('lang', lang))
            self.langs[lang] = 1

        # clean-up line breaks
        if tag == 'br':
            self.sami += "<br/>"
        # add tag to queue
        else:
            # if already in queue, first close tags off in LIFO order
            while tag in self.queue:
                closer = self.queue.pop()
                self.sami = self.sami + "</%s>" % closer
            # open new tag in queue
            self.queue.append(tag)
            # add tag with attributes
            for attr, value in attrs:
                tag += ' %s="%s"' % (attr.lower(), value)
            self.sami += "<%s>" % tag

    # override the parser's handling of endtags
    def handle_endtag(self, tag):
        # treat divs as spans
        if tag == 'div' or tag == 'i':
            tag = 'span'

        # handle incorrectly formatted sync/p tags
        if tag in ['p', 'sync'] and tag == self.last_element:
            return

        # close off tags in LIFO order, if matching starting tag in queue
        while tag in self.queue:
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag

    def handle_entityref(self, name):
        if name in ['gt', 'lt']:
            self.sami += '&%s;' % name
        else:
            try:
                self.sami += unichr(self.name2codepoint[name])
            except (KeyError, ValueError):
                self.sami += '&%s' % name

        self.last_element = ''

    def handle_charref(self, name):
        if name[0] == 'x':
            self.sami += unichr(int(name[1:], 16))
        else:
            self.sami += unichr(int(name))

    # override the parser's handling of data
    def handle_data(self, data):
        self.sami += data.decode('utf-8')
        self.last_element = ''

    # override the parser's feed function
    def feed(self, data):
        no_cc = 'no closed captioning available'

        if '<html' in data.lower():
            raise SAMIReaderError('SAMI File seems to be an HTML file.')
        elif no_cc in data.lower():
            raise SAMIReaderError('SAMI File contains "%s"' % no_cc)

        # try to find style tag in SAMI
        try:
            # prevent BS4 error with huge SAMI files with unclosed tags
            index = data.lower().find("</head>")

            self.styles = self._css_parse(
                BeautifulSoup(data[:index]).find('style').get_text())
        except AttributeError:
            self.styles = {}

        # fix erroneous italics tags
        data = data.replace('<i/>', '<i>')

        # fix awkward tags found in some SAMIs
        data = data.replace(';>', '>')
        try:
            HTMLParser.feed(self, data)
        except HTMLParseError as e:
            raise SAMIReaderError(e)

        # close any tags that remain in the queue
        while self.queue != deque([]):
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag

        return self.sami, self.styles, self.langs

    # parse the SAMI's stylesheet
    def _css_parse(self, css):
        # parse via cssutils modules
        sheet = parseString(css)
        style_sheet = {}

        for rule in sheet:
            not_empty = False
            new_style = {}
            selector = rule.selectorText.lower()
            if selector[0] in ['#', '.']:
                selector = selector[1:]
            # keep any style attributes that are needed
            for prop in rule.style:
                if prop.name == 'text-align':
                    new_style['text-align'] = prop.value
                    not_empty = True
                if prop.name == 'font-family':
                    new_style['font-family'] = prop.value
                    not_empty = True
                if prop.name == 'font-size':
                    new_style['font-size'] = prop.value
                    not_empty = True
                if prop.name == 'color':
                    cv = cssutils_css.ColorValue(prop.value)
                    # Code for RGB to hex conversion comes from
                    # http://bit.ly/1kwfBnQ
                    new_style['color'] = "#%02x%02x%02x" % (
                        cv.red, cv.green, cv.blue)
                    not_empty = True
                if prop.name == 'lang':
                    new_style['lang'] = prop.value
                    not_empty = True
            if not_empty:
                style_sheet[selector] = new_style

        return style_sheet

    def _find_lang(self, attrs):
        for attr, value in attrs:
            # if lang is an attribute of the tag
            if attr.lower() == 'lang':
                return value[:2]
            # if the P tag has a class, try and find the language
            if attr.lower() == 'class':
                try:
                    return self.styles[value.lower()]['lang']
                except KeyError:
                    pass

        return None


class SAMIReaderError(Exception):
    pass
