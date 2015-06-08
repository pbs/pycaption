# We thought about making pycaption.base objects immutable. This would be nice
# in a lot of cases, but since the transformations on them could be quite
# complex, the deepcopy method is good enough sometimes.
from copy import deepcopy

from .base import DFXPWriter, DFXP_DEFAULT_REGION
from ..base import BaseWriter, CaptionNode, merge_concurrent_captions

from xml.sax.saxutils import escape
from bs4 import BeautifulSoup

LEGACY_DFXP_BASE_MARKUP = u'''
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <styling/>
        <layout/>
    </head>
    <body/>
</tt>
'''

LEGACY_DFXP_DEFAULT_STYLE = {
    u'color': u'white',
    u'font-family': u'monospace',
    u'font-size': u'1c',
}

LEGACY_DFXP_DEFAULT_STYLE_ID = u'default'
LEGACY_DFXP_DEFAULT_REGION_ID = u'bottom'

LEGACY_DFXP_DEFAULT_REGION = {
    u'text-align': u'center',
    u'display-align': u'after'
}


class SinglePositioningDFXPWriter(DFXPWriter):
    """A dfxp writer, that ignores all positioning, using a single provided value
    """
    def __init__(self, default_positioning=DFXP_DEFAULT_REGION,
                 *args, **kwargs):
        super(SinglePositioningDFXPWriter, self).__init__(*args, **kwargs)
        self.default_positioning = default_positioning

    def write(self, captions_set, force=u''):
        """Writes a DFXP file using the positioning provided in the initializer

        :type captions_set: pycaption.base.CaptionSet
        :param force: only write this language, if available in the CaptionSet
        :rtype: unicode
        """
        captions_set = self._create_single_positioning_caption_set(
            captions_set, self.default_positioning)

        return super(SinglePositioningDFXPWriter, self).write(captions_set, force)  # noqa

    @staticmethod
    def _create_single_positioning_caption_set(caption_set, positioning):
        """Return a caption where all the positioning information was
        replaced from positioning

        :type caption_set: pycaption.base.CaptionSet
        :rtype: pycaption.base.CaptionSet
        """
        # If SinglePositioningDFXPWriter would modify the state of the caption
        # set, any writer using the same caption_set thereafter would be
        # affected. At the moment we know we don't use any other writers, but
        # this is important and mustn't be neglected
        caption_set = deepcopy(caption_set)
        caption_set = merge_concurrent_captions(caption_set)
        caption_set.layout_info = positioning

        for lang in caption_set.get_languages():
            caption_set.set_layout_info(lang, positioning)

            caption_list = caption_set.get_captions(lang)
            for caption in caption_list:
                caption.layout_info = positioning

                for node in caption.nodes:
                    if hasattr(node, 'layout_info'):
                        node.layout_info = positioning

        for _, style in caption_set.get_styles():
            if 'text-align' in style:
                style.pop('text-align')

        return caption_set

class LegacyDFXPWriter(BaseWriter):
    """Ported the legacy DFXPWriter from 0.4.5"""
    def __init__(self, *args, **kw):
        self.p_style = False
        self.open_span = False

    def write(self, caption_set, force=u''):
        caption_set = deepcopy(caption_set)
        caption_set = merge_concurrent_captions(caption_set)

        dfxp = BeautifulSoup(LEGACY_DFXP_BASE_MARKUP, u'xml')
        dfxp.find(u'tt')[u'xml:lang'] = u"en"

        for style_id, style in caption_set.get_styles():
            if style != {}:
                dfxp = self._recreate_styling_tag(style_id, style, dfxp)
        if not caption_set.get_styles():
            dfxp = self._recreate_styling_tag(
                LEGACY_DFXP_DEFAULT_STYLE_ID, LEGACY_DFXP_DEFAULT_STYLE, dfxp)

        # XXX For now we will always use this default region. In the future if
        # regions are provided, they will be kept
        dfxp = self._recreate_region_tag(
            LEGACY_DFXP_DEFAULT_REGION_ID, LEGACY_DFXP_DEFAULT_REGION, dfxp)

        body = dfxp.find(u'body')

        if force:
            langs = [self._force_language(force, caption_set.get_languages())]
        else:
            langs = caption_set.get_languages()

        for lang in langs:
            div = dfxp.new_tag(u'div')
            div[u'xml:lang'] = u'%s' % lang

            for caption in caption_set.get_captions(lang):
                if caption.style:
                    caption_style = caption.style
                    caption_style.update({u'region': LEGACY_DFXP_DEFAULT_REGION_ID})
                else:
                    caption_style = {u'class': LEGACY_DFXP_DEFAULT_STYLE_ID,
                                     u'region': LEGACY_DFXP_DEFAULT_REGION_ID}
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
            if node.type_ == CaptionNode.TEXT:
                line += escape(node.content) + u' '

            elif node.type_ == CaptionNode.BREAK:
                line = line.rstrip() + u'<br/>\n    '

            elif node.type_ == CaptionNode.STYLE:
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
