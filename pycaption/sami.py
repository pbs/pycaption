from logging import FATAL
from collections import deque
from HTMLParser import HTMLParser

from cssutils import parseString, log
from bs4 import BeautifulSoup

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

        return captions

    def _translate_lang(self, language, sami_soup):
        subdata = []
        for p in sami_soup.select('p[lang|=%s]' % language):
            milliseconds = int(p.parent['start'])
            start = milliseconds * 1000
            end = 0

            if subdata != [] and subdata[-1][1] == 0:
                subdata[-1][1] = milliseconds * 1000

            if p.get_text() not in [u'\n', '\r', '']:
                self.line = []
                self._translate_tag(p)
                text = self.line
                styles = self._translate_attrs(p)
                subdata += [[start, end, text, styles]]

        if subdata[-1][1] == 0:
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

    # convert attributes from CSS to DFXP
    def _translate_attrs(self, tag):
        attrs = {}
        css_attrs = tag.attrs

        for arg in css_attrs:
            if arg == "id":
                attrs['id'] = css_attrs[arg].lower()
            elif arg == "class":
                attrs['class'] = css_attrs[arg][0].lower()
            elif arg == "style":
                styles = css_attrs[arg].split(';')
                attrs = self._translate_style(attrs, styles)

        return attrs

    def _translate_style(self, attrs, styles):
        for style in styles:
            style = style.split(':')
            if style[0] == 'text-align':
                attrs['text-align'] = style[1].strip()
            elif style[0] == 'font-family':
                attrs['font-family'] = style[1].strip()
            elif style[0] == 'font-size':
                attrs['font-size'] = style[1].strip()
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
        p = self._recreate_p_lang(p, sub, lang, captions)
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
        p = self._recreate_p_lang(p, sub, lang, captions)
        p.string = '&nbsp;'

        sync.append(p)

        return sami

    def _recreate_p_lang(self, p, sub, lang, captions):
        try:
            if 'lang' in captions['styles']['.%s' % sub[3]['class']]['style']:
                p['class'] = sub[3]['class']
        except KeyError:
            p['lang'] = "%s" % lang

        return p

    def _recreate_stylesheet(self, captions):
        stylesheet = '<!--'

        for style, content in captions['styles'].items():
            if content['style'] != {}:
                stylesheet += self._recreate_style(style, content['style'])

        return stylesheet + '   --!>'

    def _recreate_style(self, style, content):
        sami_style = '\n    %s {\n    ' % style

        if 'text-align' in content:
            sami_style += ' text-align: %s;\n    ' % content['text-align']
        if 'font-family' in content:
            sami_style += ' font-family: %s;\n    ' % content['font-family']
        if 'font-size' in content:
            sami_style += ' font-size: %s;\n    ' % content['font-size']
        if 'color' in content:
            sami_style += ' color: %s;\n    ' % content['color']
        if 'lang' in content:
            sami_style += ' lang: %s;\n    ' % content['lang']

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
            if 'italics' in element['content']:
                line += '<i>'
            else:
                line = self._recreate_span(line, element['content'])
        else:
            if 'italics' in element['content']:
                line = line.rstrip() + '</i> '
            elif self.open_span == True:
                line = line.rstrip() + '</span> '
                self.open_span = False

        return line

    def _recreate_span(self, line, element):
        style = ''
        if 'text-align' in element:
            style += 'text-align:%s;' % element['text-align']
        if 'font-family' in element:
            style += 'font-family:%s;' % element['font-family']
        if 'font-size' in element:
            style += 'font-size:%s;' % element['font-size']
        if 'color' in element:
            style += 'color:%s;' % element['color']
        if style:
            line += '<span style="%s">' % style
            self.open_span = True

        return line


# SAMI parser, made from modified html parser
class SAMIParser(HTMLParser):
    def __init__(self, *args, **kw):
        HTMLParser.__init__(self, *args, **kw)
        self.sami = ''
        self.line = ''
        self.styles = {}
        self.queue = deque()
        self.langs = {}

    # override the parser's handling of starttags
    def handle_starttag(self, tag, attrs):
        # treat divs as spans
        if tag == 'div':
            tag = 'span'

        # figure out the caption language of P tags
        if tag == 'p':
            lang = None

            for attr in attrs:
                a, b = attr
                # if lang is an attribute of the tag
                if a.lower() == 'lang':
                    lang = b[:2]
                # if the P tag has a class, try and find the language
                elif a.lower() == 'class':
                    if '.%s' % b.lower() in self.styles:
                        lang = self.styles['.%s' % b.lower()]['lang']
            # if no language detected, set it as "none"
            if not lang:
                lang = 'None'
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
        if tag == 'div':
            tag = 'span'

        # close off tags in LIFO order, if matching starting tag in queue
        while tag in self.queue:
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag

    # override the parser's handling of data
    def handle_data(self, data):
        self.sami += data.lstrip()

    # override the parser's feed function
    def feed(self, data):
        # try to find style tag in SAMI
        try:
            self.styles = self._css_to_dfxp(
                BeautifulSoup(data).find('style').get_text())
        except:
            self.styles = []
        # fix erroneous italics tags
        data = data.replace('<i/>', '<i>')
        # clean the SAMI
        HTMLParser.feed(self, data)
        # close any tags that remain in the queue
        while self.queue != deque([]):
            closing_tag = self.queue.pop()
            self.sami += "</%s>" % closing_tag

        return self.sami, self.styles, self.langs

    # parse into DFXP format the SAMI's stylesheet
    def _css_to_dfxp(self, css):
        # parse via cssutils modules
        sheet = parseString(css)
        dfxp_styles = {}

        for rule in sheet:
            lang = None
            not_empty = False
            new_style = {}
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
                    lang = prop.value
                    not_empty = True
            if not_empty:
                dfxp_styles[rule.selectorText.lower()] = {
                    'style': new_style,
                    'lang': '%s' % lang}
        return dfxp_styles
