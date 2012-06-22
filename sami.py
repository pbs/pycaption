import logging
from collections import deque
from HTMLParser import HTMLParser
import cssutils
from bs4 import BeautifulSoup
from pycaption import BaseReader, BaseWriter

# change cssutils default logging
cssutils.log.setLevel(logging.FATAL)

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
        content, doc_styles, doc_langs = SAMICleaner().feed(content)
        sami_soup = BeautifulSoup(content)
        captions = {'captions': {}, 'styles': doc_styles}

        for language in doc_langs:
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
                    styles = self._conv_attrs(p)
                    subdata += [[start, end, text, styles]]

            if subdata[-1][1] == 0:
                subdata[-1][1] = (milliseconds + 4000) * 1000
            captions['captions'][language] = subdata

        return captions

    def _translate_tag(self, tag):
        try:
            # convert line breaks
            if tag.name == 'br':
                self.line.append({'type': 'break', 'content': ''})
            # convert italics
            elif tag.name == 'i':
                self.line.append({
                    'type': 'style',
                    'start': True,
                    'content': {'italics': True}})
                # recursively call function for any children elements
                for a in tag.contents:
                    self._translate_tag(a)
                self.line.append({
                    'type': 'style',
                    'start': False,
                    'content': {'italics': True}})
            elif tag.name == 'span':
                # convert tag attributes
                args = self._conv_attrs(tag)
                # only include span tag if attributes returned
                if args != '':
                    self.line.append({
                        'type': 'style',
                        'start': True,
                        'content':  args})
                    # recursively call function for any children elements
                    for a in tag.contents:
                        self._translate_tag(a)
                    self.line.append({
                        'type': 'style',
                        'start': False,
                        'content': args})
                else:
                    for a in tag.contents:
                        self._translate_tag(a)
            else:
                # recursively call function for any children elements
                for a in tag.contents:
                    self._translate_tag(a)
        # if no more tags found, strip text
        except AttributeError:
            self.line.append({'type': 'text', 'content': '%s' % tag.strip()})

    # convert attributes from CSS to DFXP
    def _conv_attrs(self, tag):
        attrs = {}
        css_attrs = tag.attrs

        for arg in css_attrs:
            if arg == "id":
                attrs['id'] = css_attrs[arg].lower()
            elif arg == "class":
                attrs['class'] = css_attrs[arg][0].lower()
            elif arg == "style":
                styles = css_attrs[arg].split(';')
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
    def write(self, captions):
        sami = BeautifulSoup(sami_base, "xml")
        sami_style = '<!--'

        for style, content in captions['styles'].items():
            if content['style'] != {}:
                sami_style += '\n    %s {\n    ' % style
                if 'text-align' in content['style']:
                    sami_style += ' text-align: %s;\n    ' % \
                        content['style']['text-align']
                if 'font-family' in content['style']:
                    sami_style += ' font-family: %s;\n    ' % \
                        content['style']['font-family']
                if 'font-size' in content['style']:
                    sami_style += ' font-size: %s;\n    ' % \
                        content['style']['font-size']
                if 'color' in content['style']:
                    sami_style += ' color: %s;\n    ' % \
                        content['style']['color']
                if 'lang' in content['style']:
                    sami_style += ' lang: %s;\n    ' % \
                        content['style']['lang']
                sami_style += '}\n'

        sami_style += '   --!>'
        sami.find('style').append(sami_style)
        last_time = None
        primary_lang = captions['captions'].keys()[0]
        body = sami.find('body')

        for sub in captions['captions'][primary_lang]:
            time = sub[0] / 1000

            if last_time and time != last_time:
                sync = sami.new_tag("sync", start="%s" % last_time)
                p = sami.new_tag("p")
                try:
                    if 'lang' in captions['styles']['.%s' % \
                        sub[3]['class']]['style']:
                            p['class'] = sub[3]['class']
                except:
                    p['lang'] = "%s" % primary_lang
                p.string = '&nbsp;'
                sync.append(p)
                body.append(sync)

            last_time = sub[1] / 1000

            sync = sami.new_tag("sync", start="%s" % time)
            p = sami.new_tag("p")
            try:
                if 'lang' in captions['styles']['.%s' % \
                    sub[3]['class']]['style']:
                        p['class'] = sub[3]['class']
            except:
                p['lang'] = "%s" % primary_lang
            p.string = self._recreate_text(sub[2])
            sync.append(p)
            body.append(sync)

        for lang in captions['captions']:
            last_time = None

            if lang != primary_lang:
                for sub in captions['captions'][lang]:
                    time = sub[0] / 1000

                    if last_time and time != last_time:
                        sync = sami.find("sync", start="%s" % last_time)

                        if sync == None:
                            def earlier_samis(start):
                                return int(start) < last_time
                            last_sync = sami.find_all(
                                "sync", start=earlier_samis)[-1]
                            sync = sami.new_tag(
                                "sync", start="%s" % last_time)
                            last_sync.insert_after(sync)

                        p = sami.new_tag("p")
                        try:
                            if 'lang' in captions['styles']['.%s' % \
                                sub[3]['class']]['style']:
                                    p['class'] = sub[3]['class']
                        except:
                            p['lang'] = "%s" % primary_lang
                        p.string = '&nbsp;'
                        sync.append(p)

                    last_time = sub[1] / 1000

                    sync = sami.find("sync", start="%s" % time)
                    p = sami.new_tag("p")
                    try:
                        if 'lang' in captions['styles']['.%s' % \
                            sub[3]['class']]['style']:
                                p['class'] = sub[3]['class']
                    except:
                        p['lang'] = "%s" % primary_lang
                    p.string = self._recreate_text(sub[2])
                    sync.append(p)
        a = sami.prettify(formatter=None).split('\n')
        return '\n'.join(a[1:])

    def _recreate_text(self, caption):
        line = ''
        open_span = False

        for element in caption:
            if element['type'] == 'text':
                line += element['content'] + ' '
            elif element['type'] == 'break':
                line = line.rstrip() + '<br/>\n    '
            elif element['type'] == 'style':
                if element['start']:
                    if 'italics' in element['content']:
                        line += '<i>'
                    else:
                        style = ''
                        if 'text-align' in element['content']:
                            style += 'text-align:%s;' % \
                                element['content']['text-align']
                        if 'font-family' in element['content']:
                            style += 'font-family:%s;' % \
                                element['content']['font-family']
                        if 'font-size' in element['content']:
                            style += 'font-size:%s;' % \
                                element['content']['font-size']
                        if 'color' in element['content']:
                            style += 'color:%s;' % \
                                element['content']['color']
                        if style:
                            line += '<span style="%s">' % style
                            open_span = True
                else:
                    if 'italics' in element['content']:
                        line = line.rstrip() + '</i> '
                    elif open_span == True:
                        line = line.rstrip() + '</span> '
                        open_span = False

        return line.rstrip()


# SAMI parser, made from modified html parser
class SAMICleaner(HTMLParser):
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
        sheet = cssutils.parseString(css)
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
