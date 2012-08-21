from datetime import timedelta
from bs4 import BeautifulSoup
from pycaption import BaseReader, BaseWriter


dfxp_base = '''
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <styling/>
    </head>
    <body/>
</tt>
'''


class DFXPReader(BaseReader):
    def __init__(self, *args, **kw):
        self.line = []

    def detect(self, content):
        if '</tt>' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        dfxp_soup = BeautifulSoup(content)
        captions = {'captions': {}, 'styles': {}}

        for div in dfxp_soup.find_all('div'):
            lang = div.attrs.get('xml:lang', 'en')
            captions['captions'][lang] = self._translate_div(div)

        for style in dfxp_soup.find_all('style'):
            id = style.attrs.get('id')
            if not id:
                id = style.attrs.get('xml:id')
            captions['styles'][id] = self._translate_style(style)

        return captions

    def _translate_div(self, div):
        subdata = []
        for p_tag in div.find_all('p'):
            p_data = self._translate_p_tag(p_tag)
            subdata += [p_data]
        return subdata

    def _translate_p_tag(self, p_tag):
        start, end = self._find_times(p_tag)
        self.line = []
        self._translate_tag(p_tag)
        text = self.line
        styles = self._translate_style(p_tag)

        return [start, end, text, styles]

    def _find_times(self, p_tag):
        start = self._translate_time(p_tag['begin'])

        try:
            end = self._translate_time(p_tag['end'])
        except KeyError:
            dur = self._translate_time(p_tag['dur'])
            end = start + dur

        return start, end

    def _translate_time(self, stamp):
        timesplit = stamp.split(':')
        secsplit = timesplit[2].split('.')
        if len(timesplit) > 3:
            secsplit.append((int(timesplit[3]) / 30) * 100)
        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)
        return microseconds

    def _translate_tag(self, tag):
        # ensure that tag is not just text
        try:
            tag_name = tag.name
        # if no more tags found, strip text
        except AttributeError:
            if tag.strip() != '':
                self.line.append({
                    'type': 'text',
                    'content': '%s' % tag.strip()})
            return

        # convert line breaks
        if tag_name == 'br':
            self.line.append({'type': 'break', 'content': ''})
        # convert italics
        elif tag_name == 'span':
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
        if args != '':
            self.line.append({
                'type': 'style',
                'start': True,
                'content': args})
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

    # convert style from DFXP
    def _translate_style(self, tag):
        attrs = {}
        dfxp_attrs = tag.attrs
        for arg in dfxp_attrs:
            if arg == "style":
                attrs['class'] = dfxp_attrs[arg]
            elif arg == "tts:fontstyle" and dfxp_attrs[arg] == "italic":
                attrs['italics'] = True
            elif arg == "tts:textalign":
                attrs['text-align'] = dfxp_attrs[arg]
            elif arg == "tts:fontfamily":
                attrs['font-family'] = dfxp_attrs[arg]
            elif arg == "tts:fontsize":
                attrs['font-size'] = dfxp_attrs[arg]
            elif arg == "tts:color":
                attrs['color'] = dfxp_attrs[arg]
        return attrs


class DFXPWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.p_style = False
        self.open_span = False

    def write(self, captions, force=''):
        dfxp = BeautifulSoup(dfxp_base, 'xml')
        dfxp.find('tt')['xml:lang'] = "en"

        for style, content in captions['styles'].items():
            if content != {}:
                dfxp = self._recreate_styling_tag(style, content, dfxp)

        body = dfxp.find('body')

        if force:
            captions['captions'] = self._force_language(force,
                                                        captions['captions'])

        for lang in captions['captions']:
            div = dfxp.new_tag('div')
            div['xml:lang'] = '%s' % lang

            for sub in captions['captions'][lang]:
                p = self._recreate_p_tag(sub, dfxp)
                div.append(p)

            body.append(div)

        return unicode(dfxp.prettify(formatter=None))

    # force the DFXP to only have one language, trying to match on "force"
    def _force_language(self, force, captions):
        for lang in captions.keys():
            if force in lang:
                return {lang: captions[lang]}
            elif len(captions) > 1:
                del captions[lang]

        return captions

    def _recreate_styling_tag(self, style, content, dfxp):
        dfxp_style = dfxp.new_tag('style', id="%s" % style)

        attributes = self._recreate_style(content, dfxp)
        dfxp_style.attrs.update(attributes)

        if dfxp_style != dfxp.new_tag('style', id="%s" % style):
            dfxp.find('styling').append(dfxp_style)

        return dfxp

    def _recreate_p_tag(self, sub, dfxp):
        start = '0' + str(timedelta(milliseconds=(int(sub[0] / 1000))))[:11]
        end = '0' + str(timedelta(milliseconds=(int(sub[1] / 1000))))[:11]
        p = dfxp.new_tag("p", begin=start, end=end)
        p.string = self._recreate_text(sub[2], dfxp)

        if dfxp.find("style", {"id": "p"}):
            p['style'] = 'p'

        p.attrs.update(self._recreate_style(sub[3], dfxp))

        return p

    def _recreate_text(self, caption, dfxp):
        line = ''

        for element in caption:
            if element['type'] == 'text':
                line += element['content'] + ' '

            elif element['type'] == 'break':
                line = line.rstrip() + '<br/>\n    '

            elif element['type'] == 'style':
                line = self._recreate_span(line, element, dfxp)

        return line.rstrip()

    def _recreate_span(self, line, element, dfxp):
        if element['start']:
            styles = ''

            for a, b in self._recreate_style(element['content'], dfxp).items():
                styles += ' %s="%s"' % (a, b)

            if styles:
                if self.open_span:
                    line = line.rstrip() + '</span> '
                line += '<span%s>' % styles
                self.open_span = True

        elif self.open_span:
            line = line.rstrip() + '</span> '
            self.open_span = False

        return line

    def _recreate_style(self, content, dfxp):
        dfxp_style = {}

        if 'class' in content:
            if dfxp.find("style", {"id": content['class']}):
                dfxp_style['style'] = content['class']
        if 'text-align' in content:
            dfxp_style['tts:textAlign'] = content['text-align']
        if 'italics' in content:
            dfxp_style['tts:fontStyle'] = 'italic'
        if 'font-family' in content:
            dfxp_style['tts:fontfamily'] = content['font-family']
        if 'font-size' in content:
            dfxp_style['tts:fontsize'] = content['font-size']
        if 'color' in content:
            dfxp_style['tts:color'] = content['color']

        return dfxp_style
