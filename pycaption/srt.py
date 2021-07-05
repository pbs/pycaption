import os
from copy import deepcopy

from .base import (
    BaseReader, BaseWriter, CaptionSet, CaptionList, Caption, CaptionNode)
from .exceptions import CaptionReadNoCaptions, InvalidInputError

import re
from PIL import Image, ImageFont, ImageDraw


class SRTReader(BaseReader):
    RE_HTML = re.compile(r'<[^>]+>')
    RE_ASS = re.compile(r'{[^}]+}')

    def detect(self, content):
        lines = content.splitlines()
        if lines[0].isdigit() and '-->' in lines[1]:
            return True
        else:
            return False

    def read(self, content, lang='en-US', strip_html=False, strip_ass_tags=False):
        if type(content) != str:
            raise InvalidInputError('The content is not a unicode string.')

        lines = content.splitlines()
        start_line = 0
        captions = CaptionList()

        while start_line < len(lines):
            if not lines[start_line].isdigit():
                break

            end_line = self._find_text_line(start_line, lines)

            timing = lines[start_line + 1].split('-->')
            start = self._srttomicro(timing[0].strip(' \r\n'))
            end = self._srttomicro(timing[1].strip(' \r\n'))

            nodes = []

            for line in lines[start_line + 2:end_line - 1]:
                # skip extra blank lines
                if not nodes or line != '':
                    txt = line
                    if strip_html:
                        txt = SRTReader.RE_HTML.sub('', txt)

                    if strip_ass_tags:
                        txt = SRTReader.RE_ASS.sub('', txt)

                    nodes.append(CaptionNode.create_text(txt))
                    nodes.append(CaptionNode.create_break())

            if len(nodes):
                # remove last line break from end of caption list
                nodes.pop()
                caption = Caption(start, end, nodes)
                captions.append(caption)

            start_line = end_line

        caption_set = CaptionSet({lang: captions})

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    def _srttomicro(self, stamp):
        timesplit = stamp.split(':')

        # TODO(apeterka): add better support for "extended SRT"
        # This is a workaround for "extended SRT" format, whose timestamp looks like this:
        # 00:00:18,208 --> 00:00:20,792 X1:230 X2:490 Y1:393 Y2:431
        if len(timesplit) > 3:
            timesplit = timesplit[0:3]
        if ' ' in timesplit[2]:
            timesplit[2] = timesplit[2].split(' ')[0]

        if ',' not in timesplit[2]:
            timesplit[2] += ',000'
        secsplit = timesplit[2].split(',')

        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)

        return microseconds

    def _find_text_line(self, start_line, lines):
        end_line = start_line

        found = False
        while end_line < len(lines):
            if lines[end_line].strip() == "":
                found = True
            elif found is True:
                end_line -= 1
                break
            end_line += 1

        return end_line + 1


class SRTWriter(BaseWriter):
    VALID_POSITION = ['top', 'bottom']

    def write(self, caption_set, position='bottom'):
        position = position.lower().strip()
        if position not in SRTWriter.VALID_POSITION:
            raise ValueError('Unknown position. Supported: {}'.format(','.join(SRTWriter.VALID_POSITION)))

        if position == 'top' and not all([self.video_width, self.video_height]):
            raise ValueError('Top position requires video width and height.')

        caption_set = deepcopy(caption_set)

        srt_captions = []

        for lang in caption_set.get_languages():
            srt_captions.append(
                self._recreate_lang(caption_set.get_captions(lang), position)
            )

        caption_content = 'MULTI-LANGUAGE SRT\n'.join(srt_captions)
        return caption_content

    def _recreate_lang(self, captions, position='bottom'):
        srt = ''
        count = 1

        fnt = ImageFont.truetype(os.path.dirname(__file__) + '/NotoSansDisplay-Regular.ttf', 30)
        img = Image.new('RGB', (self.video_width, self.video_height), (0, 255, 0))
        draw = ImageDraw.Draw(img)

        for caption in captions:
            # Generate the text
            new_content = ''
            for node in caption.nodes:
                new_content = self._recreate_line(new_content, node)

            # Eliminate excessive line breaks
            new_content = new_content.strip()
            while '\n\n' in new_content:
                new_content = new_content.replace('\n\n', '\n')

            srt += '%s\n' % count

            start = caption.format_start(msec_separator=',')
            end = caption.format_end(msec_separator=',')
            if position == 'bottom':
                # "bottom" is standard (no position info).
                # Use the old behavior, output just the timestamp, no coordinates.
                timestamp = '%s --> %s\n' % (start[:12], end[:12])
            elif position == 'top':
                padding_top = 10
                l, t, r, b = draw.textbbox((0, 0), new_content, font=fnt)
                l, t, r, b = draw.textbbox((self.video_width / 2 - r / 2, padding_top), new_content, font=fnt)
                x1 = str(round(l)).zfill(3)
                x2 = str(round(r)).zfill(3)
                y1 = str(round(t)).zfill(3)
                y2 = str(round(b)).zfill(3)
                timestamp = '%s --> %s X1:%s X2:%s Y1:%s Y2:%s\n' % (start[:12], end[:12], x1, x2, y1, y2)
            else:
                raise ValueError('Unsupported position: %s' % position)

            srt += timestamp.replace('.', ',')
            srt += "%s%s" % (new_content, '\n\n')
            count += 1

        return srt[:-1]  # remove unwanted newline at end of file

    def _recreate_line(self, srt, line):
        if line.type_ == CaptionNode.TEXT:
            return srt + '%s ' % line.content
        elif line.type_ == CaptionNode.BREAK:
            return srt + '\n'
        else:
            return srt
