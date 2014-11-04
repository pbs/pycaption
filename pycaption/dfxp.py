from bs4 import BeautifulSoup, NavigableString
from xml.sax.saxutils import escape

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE)
from .exceptions import CaptionReadNoCaptions


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
            raise RuntimeError('The content is not a unicode string.')

        dfxp_soup = BeautifulSoup(content)
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
