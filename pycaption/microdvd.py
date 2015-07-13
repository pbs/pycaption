from copy import deepcopy

from .base import (
    BaseReader, BaseWriter, CaptionSet, Caption, CaptionNode)
from .exceptions import CaptionReadNoCaptions, InvalidInputError
import re

class MicroDVDReader(BaseReader):
    def detect(self, content):
        return re.match("{\d+}{\d+}", content) is not None

    def read(self, content, lang=u'en-US'):
        if type(content) != unicode:
            raise InvalidInputError('The content is not a unicode string.')

        caption_set = CaptionSet()
        lines = content.splitlines()
        start_line = 0
        captions = []
        fps = 25.0
        for line in lines:
            m = re.match(r"{(\d+)}{(\d+)}(.*)", line)
            if not m: break
            caption = Caption()
            start, end, txt = m.groups()

            if start == '0' and end == '0':
                fps = float(txt)
                continue

            caption.start = self._framestomicro(int(start), fps)
            caption.end = self._framestomicro(int(end), fps)

            for line in txt.split('|'):
                # skip extra blank lines
                if not caption.nodes or line != u'':
                    caption.nodes.append(CaptionNode.create_text(line))
                    caption.nodes.append(CaptionNode.create_break())

            # remove last line break from end of caption list
            if len(caption.nodes):
                caption.nodes.pop()
                captions.append(caption)

        caption_set.set_captions(lang, captions)

        if caption_set.is_empty():
            raise CaptionReadNoCaptions(u"empty caption file")

        return caption_set

    def _framestomicro(self, framenum, fps=25.0):
        return int(framenum / fps * (10**6))


class MicroDVDWriter(BaseWriter):
    def write(self, caption_set):
        caption_set = deepcopy(caption_set)

        captions = []

        for lang in caption_set.get_languages():
            captions.append(
                self._recreate_lang(caption_set.get_captions(lang))
            )

        return ''.join(captions)

    def _microtoframes(self, micro, fps=25.0):
        return int(micro * fps / (10**6))

    def _recreate_lang(self, captions):
        sub = u''
        count = 1
        for caption in captions:
            start = self._microtoframes(caption.start)
            end = self._microtoframes(caption.end)
            sub += u'{%s}{%s}' % (start, end)

            new_content = u''
            for node in caption.nodes:
                new_content = self._recreate_line(new_content, node)

            # Eliminate excessive line breaks
            new_content = new_content.strip() + '\n'
            while u'\n\n' in new_content:
                new_content = new_content.replace(u'\n\n', u'\n')
            # Break unnecessary on last line
            while u'|\n' in new_content:
                new_content = new_content.replace(u'|\n', u'\n')

            sub += new_content

        return sub

    def _recreate_line(self, sub, line):
        if line.type_ == CaptionNode.TEXT:
            return sub + u'%s' % line.content
        elif line.type_ == CaptionNode.BREAK:
            return sub + u'|'
        else:
            return sub
