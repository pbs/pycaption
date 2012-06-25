import datetime
from bs4 import BeautifulSoup
from pycaption import BaseReader, BaseWriter


dfxp_base = '''
<tt xmlns="http://www.w3.org/ns/ttml">
    <head>
        <styling xmlns:tts="http://www.w3.org/ns/ttml#styling"/>
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
            captions['captions'][div['xml:lang']] = self._translate_div(div)

        for style in dfxp_soup.find_all('style'):
            captions['styles'][style['id']] = self._translate_style(style)

        return captions

    def _translate_div(self, div):
        subdata = []
        for p_tag in div.find_all('p'):
            p_data = self._translate_p_tag(p_tag)
            subdata += [p_data]
        return subdata

    def _translate_style(self, style):
        new_style = {'lang': 'None', 'style': {}}
        for arg in style.attrs:
            if arg == "tts:fontstyle" and style.attrs[arg] == "italic":
                new_style['style']['italics'] = True
            if arg == "tts:textalign":
                new_style['style']['text-align'] = style.attrs[arg]
        return new_style

    def _translate_p_tag(self, p_tag):
        start = self._translate_time(p_tag['begin'])
        end = self._translate_time(p_tag['end'])
        self.line = []
        self._translate_tag(p_tag)
        text = self.line
        styles = {}
        attrs = p_tag.attrs
        for arg in attrs:
            if arg == "id":
                styles['id'] = attrs[arg]
            elif arg == "class":
                styles['class'] = attrs[arg]
            elif arg == "tts:fontstyle" and attrs[arg] == "italic":
                styles['italics'] = True
            elif arg == "tts:textalign":
                styles['align'] = attrs[arg]
            elif arg == 'tts:fontfamily':
                styles['font-family'] = attrs[arg]
            elif arg == 'tts:fontsize':
                styles['font-size'] = attrs[arg]
            elif arg == 'tts:color':
                styles['color'] = attrs[arg]
        return [start, end, text, styles]

    def _translate_time(self, stamp):
        timesplit = stamp.split(':')
        secsplit = timesplit[2].split('.')
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
        args = self._translate_attrs(tag)
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

    # convert attributes from CSS to DFXP
    def _translate_attrs(self, tag):
        attrs = {}
        css_attrs = tag.attrs
        for arg in css_attrs:
            if arg == "id":
                attrs['id'] = css_attrs[arg]
            if arg == "tts:fontstyle" and css_attrs[arg] == "italic":
                attrs['italics'] = True
            if arg == "tts:textalign":
                attrs['text-align'] = css_attrs[arg]
            if arg == "tts:textalign":
                attrs['text-align'] = css_attrs[arg]
            if arg == "tts:fontfamily":
                attrs['font-family'] = css_attrs[arg]
            if arg == "tts:fontsize":
                attrs['font-size'] = css_attrs[arg]
            if arg == "tts:color":
                attrs['color'] = css_attrs[arg]
        return attrs


class DFXPWriter(BaseWriter):
    def write(self, captions):
        dfxp = BeautifulSoup(dfxp_base, 'xml')
        dfxp.find('tt')['xml:lang'] = "en"
        p_style = False

        for style, content in captions['styles'].items():
            if content['style'] != {}:
                dfxp_style = dfxp.new_tag('style', id="%s" % style)
                if style == 'p':
                    p_style = True
                if 'text-align' in content['style']:
                    dfxp_style['tts:textAlign'] = (
                        content['style']['text-align'])
                if 'font-family' in content['style']:
                    dfxp_style['tts:fontfamily'] = (
                        content['style']['font-family'])
                if 'font-size' in content['style']:
                    dfxp_style['tts:fontsize'] = content['style']['font-size']
                if 'color' in content['style']:
                    dfxp_style['tts:color'] = content['style']['color']
                if 'text-align' in content['style']:
                    dfxp_style['tts:textAlign'] = (
                        content['style']['text-align'])
                if dfxp_style != dfxp.new_tag('style', id="%s" % style):
                    dfxp.find('styling').append(dfxp_style)

        body = dfxp.find('body')

        if p_style:
            body['id'] = 'p'

        for lang in captions['captions']:
            div = dfxp.new_tag('div')
            div['xml:lang'] = '%s' % lang

            for sub in captions['captions'][lang]:
                start = '0' + str(datetime.timedelta(
                    milliseconds=(int(sub[0] / 1000))))[:11]
                end = '0' + str(datetime.timedelta(
                    milliseconds=(int(sub[1] / 1000))))[:11]
                text = self._recreate_text(sub[2])

                p = dfxp.new_tag("p", begin=start, end=end)
                if 'id' in sub[3]:
                    if dfxp.find("style", {"id": '#%s' % sub[3]['id']}):
                        p['id'] = '#%s' % sub[3]['id']
                elif 'class' in sub[3]:
                    if dfxp.find("style", {"id": '.%s' % sub[3]['class']}):
                        p['id'] = '.%s' % sub[3]['class']
                elif 'italics' in sub[3]:
                    p['tts:fontStyle'] = "italic"
                elif 'text-align' in sub[3]:
                    p['tts:textAlign'] = sub[3]['text-align']
                elif 'font-family' in sub[3]:
                    p['tts:fontfamily'] = sub[3]['font-family']
                elif 'font-size' in sub[3]:
                    p['tts:fontsize'] = sub[3]['font-size']
                elif 'color' in sub[3]:
                    p['tts:color'] = sub[3]['color']

                p.string = text
                div.append(p)

            body.append(div)

        return dfxp.prettify(formatter=None)

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
                    styles = ''
                    if 'italics' in element['content']:
                        styles += ' tts:fontStyle="italic"'
                    if 'text-align' in element['content']:
                        styles += (' tts:textAlign="%s"' %
                            element['content']['text-align'])
                    if 'font-family' in element['content']:
                        styles += (' tts:fontfamily="%s"' %
                            element['content']['font-family'])
                    if 'font-size' in element['content']:
                        styles += (' tts:fontsize="%s"' %
                            element['content']['font-size'])
                    if 'color' in element['content']:
                        styles += (' tts:color="%s"' %
                            element['content']['color'])
                    if styles:
                        line += '<span%s>' % styles
                        open_span = True
                elif open_span:
                    line = line.rstrip() + '</span> '

        return line.rstrip()
