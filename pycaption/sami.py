from logging import FATAL
from collections import deque
from HTMLParser import HTMLParser, HTMLParseError
from htmlentitydefs import name2codepoint

from cssutils import parseString, log
from bs4 import BeautifulSoup
import re

from pycaption import BaseReader, BaseWriter

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
        content, doc_styles, doc_langs = SAMIParser().feed(content)
        sami_soup = BeautifulSoup(content)
        captions = {'captions': {}, 'styles': doc_styles}

        for language in doc_langs:
            lang_captions = self._translate_lang(language, sami_soup)
            captions['captions'][language] = lang_captions

        for caption_list in captions['captions'].values():
            if caption_list != []:
                return captions

        raise SAMIReaderError("Empty Caption File")

    def _translate_lang(self, language, sami_soup):
        subdata = []
        for p in sami_soup.select('p[lang|=%s]' % language):
            milliseconds = int(float(p.parent['start']))
            start = milliseconds * 1000
            end = 0

            if subdata != [] and subdata[-1][1] == 0:
                subdata[-1][1] = milliseconds * 1000

            if p.get_text().strip():
                self.line = []
                self._translate_tag(p)
                text = self.line
                styles = self._translate_attrs(p)
                subdata += [[start, end, text, styles]]

        if subdata and subdata[-1][1] == 0:
            subdata[-1][1] = (milliseconds + 4000) * 1000

        return subdata

    def _translate_tag(self, tag):
        # check to see if tag is just a string
        try:
            tag_name = tag.name
        except AttributeError:
            # if no more tags found, strip text
            self.line.append({'type': 'text', 'content': '%s' % tag.strip()})
            return

        # convert line breaks
        if tag.name == 'br':
            self.line.append({'type': 'break', 'content': ''})
        # convert italics
        elif tag.name == 'i':
            self.line.append({'type': 'style', 'start': True,
                              'content': {'italics': True}})
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            self.line.append({'type': 'style', 'start': False,
                              'content': {'italics': True}})
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
            self.line.append({'type': 'style', 'start': True,
                              'content':  args})
            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            self.line.append({'type': 'style', 'start': False,
                              'content': args})
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

        for lang in captions['captions']:
            self.last_time = None
            if not primary:
                primary = lang
            for sub in captions['captions'][lang]:
                sami = self._recreate_p_tag(sub, sami, lang, primary, captions)

        a = sami.prettify(formatter=None).split('\n')
        return '\n'.join(a[1:])

    def _recreate_p_tag(self, sub, sami, lang, primary, captions):
        time = sub[0] / 1000

        if self.last_time and time != self.last_time:
            sami = self._recreate_blank_tag(sami, sub, lang, primary, captions)

        self.last_time = sub[1] / 1000

        sami, sync = self._recreate_sync(sami, lang, primary, time)

        p = sami.new_tag("p")

        style = ''
        for a, b in self._recreate_style(sub[3]).items():
            style += '%s:%s;' % (a, b)
        if style:
            p['style'] = style

        p['class'] = self._recreate_p_lang(p, sub, lang, captions)
        p.string = self._recreate_text(sub[2])

        sync.append(p)

        return sami

    def _recreate_sync(self, sami, lang, primary, time):
        if lang == primary:
            sync = sami.new_tag("sync", start="%s" % time)
            sami.body.append(sync)
        else:
            sync = sami.find("sync", start="%s" % time)
            if sync == None:
                sami, sync = self._find_closest_sync(sami, time)

        return sami, sync

    def _find_closest_sync(self, sami, time):
        sync = sami.new_tag("sync", start="%s" % time)

        def earlier_syncs(start):
            return int(start) < time
        earlier = sami.find_all("sync", start=earlier_syncs)
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

    def _recreate_blank_tag(self, sami, sub, lang, primary, captions):
        sami, sync = self._recreate_sync(sami, lang, primary, self.last_time)

        p = sami.new_tag("p")
        p['class'] = self._recreate_p_lang(p, sub, lang, captions)
        p.string = '&nbsp;'

        sync.append(p)

        return sami

    def _recreate_p_lang(self, p, sub, lang, captions):
        try:
            if 'lang' in captions['styles'][sub[3]['class']]:
                return sub[3]['class']
        except KeyError:
            pass
        return lang

    def _recreate_stylesheet(self, captions):
        stylesheet = '<!--'

        for style, content in captions['styles'].items():
            if content != {}:
                stylesheet += self._recreate_style_tag(style, content)

        for lang in captions['captions'].keys():
            if 'lang: %s' % lang not in stylesheet:
                stylesheet += '\n    .%s {\n     lang: %s;\n    }\n' % (lang,
                                                                        lang)

        return stylesheet + '   --!>'

    def _recreate_style_tag(self, style, content):
        if style not in ['p', 'sync', 'span']:
            element = '.'
        else:
            element = ''

        sami_style = '\n    %s%s {\n    ' % (element, style)

        for a, b in self._recreate_style(content).items():
            sami_style += ' %s: %s;\n    ' % (a, b)

        return sami_style + '}\n'

    def _recreate_text(self, caption):
        line = ''

        for element in caption:
            if element['type'] == 'text':
                line += element['content'] + ' '
            elif element['type'] == 'break':
                line = line.rstrip() + '<br/>\n    '
            elif element['type'] == 'style':
                line = self._recreate_line_style(line, element)

        return line.rstrip()

    def _recreate_line_style(self, line, element):
        if element['start']:
            if self.open_span == True:
                line = line.rstrip() + '</span> '
            line = self._recreate_span(line, element['content'])
        else:
            if self.open_span == True:
                line = line.rstrip() + '</span> '
                self.open_span = False

        return line

    def _recreate_span(self, line, content):
        style = ''
        class_ = ''
        if 'class' in content:
            class_ += ' class="%s"' % content['class']

        for a, b in self._recreate_style(content).items():
            style += '%s:%s;' % (a, b)

        if style or class_:
            if style:
                style = ' style="%s"' % style
            line += '<span%s%s>' % (class_, style)
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
        self.sami = ''
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
            for attr in attrs:
                a, b = attr
                tag += ' %s="%s"' % (a.lower(), b)
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
        self.sami += data.lstrip()
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
            lang = None
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
                    new_style['color'] = prop.value
                    not_empty = True
                if prop.name == 'lang':
                    new_style['lang'] = prop.value
                    not_empty = True
            if not_empty:
                style_sheet[selector] = new_style

        return style_sheet

    def _find_lang(self, attrs):
        for attr in attrs:
            a, b = attr
            # if lang is an attribute of the tag
            if a.lower() == 'lang':
                return b[:2]
            # if the P tag has a class, try and find the language
            if a.lower() == 'class':
                try:
                    return self.styles[b.lower()]['lang']
                except KeyError:
                    pass

        return None


class SAMIReaderError(Exception):
    pass
