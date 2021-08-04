import re
from copy import deepcopy

from .base import (
    BaseReader, BaseWriter, CaptionSet, CaptionList, Caption, CaptionNode,
    DEFAULT_LANGUAGE_CODE,
)
from .exceptions import (
    CaptionReadNoCaptions, CaptionReadSyntaxError, CaptionReadTimingError,
    InvalidInputError,
)


class MicroDVDReader(BaseReader):
    def detect(self, content):
        return re.match(r"{\d+}{\d+}", content) is not None

    def read(self, content, lang=DEFAULT_LANGUAGE_CODE):
        if not isinstance(content, str):
            raise InvalidInputError('The content is not a unicode string.')

        lines = content.splitlines()
        captions = CaptionList()
        fps = 25.0
        for line in lines:
            if not line:
                continue

            m = re.match(r"{(\d+)}{(\d+)}(.*)", line)
            if not m:
                raise CaptionReadSyntaxError(
                    "Line does not match expected format")

            start, end, txt = m.groups()

            if start == '0' and end == '0':
                try:
                    fps = float(txt)
                    continue
                except ValueError:
                    raise CaptionReadTimingError(
                        'FPS information is not provided')

            caption_start = self._framestomicro(int(start), fps)
            caption_end = self._framestomicro(int(end), fps)
            nodes = []

            for line in txt.split('|'):
                # skip extra blank lines
                if line != '':
                    nodes.append(CaptionNode.create_text(line))
                    nodes.append(CaptionNode.create_break())

            # remove last line break from end of caption list
            if len(nodes):
                nodes.pop()

                caption = Caption(caption_start, caption_end, nodes)
                captions.append(caption)

        caption_set = CaptionSet({lang: captions})
        caption_set.set_captions(lang, captions)

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("Empty caption file")

        return caption_set

    def _framestomicro(self, framenum, fps=25.0):
        return int(framenum / fps * (10 ** 6))


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
        return int(micro * fps / (10 ** 6))

    def _recreate_lang(self, captions):
        sub = ''

        for caption in captions:
            start = self._microtoframes(caption.start)
            end = self._microtoframes(caption.end)
            sub += f'{{{start}}}{{{end}}}'

            new_content = ''
            for node in caption.nodes:
                new_content = self._recreate_line(new_content, node)

            # Eliminate excessive line breaks
            new_content = new_content.strip() + '\n'
            while '\n\n' in new_content:
                new_content = new_content.replace('\n\n', '\n')
            # Break unnecessary on last line
            while '|\n' in new_content:
                new_content = new_content.replace('|\n', '\n')

            sub += new_content

        return sub

    def _recreate_line(self, sub, line):
        if line.type_ == CaptionNode.TEXT:
            return sub + line.content
        elif line.type_ == CaptionNode.BREAK:
            return sub + '|'
        else:
            return sub
