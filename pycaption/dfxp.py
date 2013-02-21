from datetime import timedelta
from bs4 import BeautifulSoup
from pycaption import BaseReader, BaseWriter, CaptionSet, Caption, CaptionData


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
        self.nodes = []

    def detect(self, content):
        if '</tt>' in content.lower():
            return True
        else:
            return False

    def read(self, content):
        dfxp_soup = BeautifulSoup(content)
        captions = CaptionSet()

        # Each div represents all the captions for a single language.
        for div in dfxp_soup.find_all('div'):
            lang = div.attrs.get('xml:lang', 'en')
            captions.set_captions(lang, self._translate_div(div))

        for style in dfxp_soup.find_all('style'):
            id = style.attrs.get('id')
            if not id:
                id = style.attrs.get('xml:id')
            captions.add_style(id, self._translate_style(style))

        captions = self._combine_matching_captions(captions)

        return captions

    def _translate_div(self, div):
        captions = []
        # Each <p> represents a single caption
        for p_tag in div.find_all('p'):
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
        caption.styles = styles
        return caption

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
                node = CaptionData.create_text(tag.strip())
                self.nodes.append(node)
            return

        # convert line breaks
        if tag_name == 'br':
            self.nodes.append(CaptionData.create_break())
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
            node = CaptionData.create_style(True, args)
            node.start = True
            node.content = args
            self.nodes.append(node)

            # recursively call function for any children elements
            for a in tag.contents:
                self._translate_tag(a)
            node = CaptionData.create_style(False, args)
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

    # Merge together captions that have the same start/end times.
    def _combine_matching_captions(self, captionset):
        for lang in captionset.get_languages():
            captions = captionset.get_captions(lang)
            new_caps = captions[:1]

            for caption in captions[1:]:
                if caption.start == new_caps[-1].start and caption.end == new_caps.end:
                    new_caps[-1].nodes.append(CaptionData.create_break())
                    new_caps[-1].nodes.extend(caption.nodes)
                else:
                    new_caps.append(caption)

            captionset.set_captions(lang, new_caps)

        return captionset


class DFXPWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.p_style = False
        self.open_span = False

    def write(self, captions, force=''):
        dfxp = BeautifulSoup(dfxp_base, 'xml')
        dfxp.find('tt')['xml:lang'] = "en"

        for style_id, style in captions.get_styles():
            # TODO: fix comparison for empty style.
            if style != {}:
                dfxp = self._recreate_styling_tag(style_id, style, dfxp)

        body = dfxp.find('body')

        if force:
            langs = [self._force_language(force, captions.get_languages())]
        else:
            langs = captions.get_languages()

        for lang in langs:
            div = dfxp.new_tag('div')
            div['xml:lang'] = '%s' % lang

            for sub in captions.get_captions(lang):
                p = self._recreate_p_tag(sub, dfxp)
                div.append(p)

            body.append(div)

        return dfxp.prettify(formatter=None).encode("UTF-8")

    # force the DFXP to only have one language, trying to match on "force"
    def _force_language(self, force, langs):
        for lang in langs:
            if force == lang:
                return lang

        return langs[-1]

    def _recreate_styling_tag(self, style, content, dfxp):
        dfxp_style = dfxp.new_tag('style', id="%s" % style)

        attributes = self._recreate_style(content, dfxp)
        dfxp_style.attrs.update(attributes)

        if dfxp_style != dfxp.new_tag('style', id="%s" % style):
            dfxp.find('styling').append(dfxp_style)

        return dfxp

    def _recreate_p_tag(self, sub, dfxp):
        start = '0' + str(timedelta(milliseconds=(int(sub.start / 1000))))[:11]
        end = '0' + str(timedelta(milliseconds=(int(sub.end / 1000))))[:11]
        p = dfxp.new_tag("p", begin=start, end=end)
        p.string = self._recreate_text(sub.nodes, dfxp)

        if dfxp.find("style", {"id": "p"}):
            p['style'] = 'p'

        p.attrs.update(self._recreate_style(sub.style, dfxp))

        return p

    def _recreate_text(self, caption, dfxp):
        line = ''

        for data in caption:
            if data.type == CaptionData.TEXT:
                line += data.content + ' '

            elif data.type == CaptionData.BREAK:
                line = line.rstrip() + '<br/>\n    '

            elif data.type == CaptionData.STYLE:
                line = self._recreate_span(line, data, dfxp)

        return line.rstrip()

    def _recreate_span(self, line, data, dfxp):
        if data.start:
            styles = ''

            for a, b in self._recreate_style(data.content, dfxp).items():
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
