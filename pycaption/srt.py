from datetime import timedelta
from pycaption import BaseReader, BaseWriter, Caption, CaptionSet, CaptionData


class SRTReader(BaseReader):
    def detect(self, content):
        inlines = content.splitlines()
        if inlines[0].isdigit() and '-->' in inlines[1]:
            return True
        else:
            return False

    def read(self, content, lang='en'):
        captions = CaptionSet()
        inlines = content.splitlines()
        start_line = 0
        subdata = []

        while start_line < len(inlines):
            if not inlines[start_line].isdigit():
                break

            caption = Caption()

            end_line = self._find_text_line(start_line, inlines)

            timing = inlines[start_line + 1].split('-->')
            caption.start = self._srttomicro(timing[0].strip(' \r\n'))
            caption.end = self._srttomicro(timing[1].strip(' \r\n'))

            for line in inlines[start_line + 2:end_line - 1]:
                caption.nodes.append(CaptionData.create_text(line))
                caption.nodes.append(CaptionData.create_break())
            caption.nodes.pop()  # remove last line break from end of caption list

            subdata.append(caption)
            start_line = end_line

        captions.set_captions(lang, subdata)
        return captions

    def _srttomicro(self, stamp):
        timesplit = stamp.split(':')
        secsplit = timesplit[2].split(',')
        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)

        return microseconds

    def _find_text_line(self, start_line, inlines):
        end_line = start_line + 1

        while end_line < (len(inlines) + 1):
            try:
                int(inlines[end_line])
                break
            except (ValueError, IndexError):
                end_line += 1

        return end_line


class SRTWriter(BaseWriter):
    def write(self, captions):
        srts = []

        for lang in captions.get_languages():
            srts.append(self._recreate_lang(captions.get_captions(lang)))

        return 'MULTI-LANGUAGE SRT\n'.join(srts)

    def _recreate_lang(self, captions):
        srt = ''
        count = 1

        for sub in captions:
            srt += '%s\n' % count
            start = '0' + str(timedelta(milliseconds=(int(sub.start / 1000))))
            end = '0' + str(timedelta(milliseconds=(int(sub.end / 1000))))
            timestamp = '%s --> %s\n' % (start[:12], end[:12])
            srt += timestamp.replace('.', ',')
            for node in sub.nodes:
                srt = self._recreate_line(srt, node)
            srt += '\n\n'
            count += 1

        return srt[:-1]

    def _recreate_line(self, srt, line):
        if line.type == CaptionData.TEXT:
            return srt + '%s ' % line.content
        elif line.type == CaptionData.BREAK:
            return srt + '\n'
        else:
            return srt
