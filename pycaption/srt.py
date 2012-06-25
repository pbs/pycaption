from datetime import timedelta
from pycaption import BaseReader, BaseWriter


class SRTReader(BaseReader):
    def detect(self, content):
        inlines = content.splitlines()
        if inlines[0].isdigit() and '-->' in inlines[1]:
            return True
        else:
            return False

    def read(self, content, lang='en'):
        inlines = content.splitlines()
        start_line = 0
        subdata = []

        while start_line < len(inlines):
            if not inlines[start_line].isdigit():
                break

            current_line = start_line + 1
            while current_line < (len(inlines) + 1):
                try:
                    if int(inlines[current_line]):
                        break
                except:
                    current_line += 1

            timing = inlines[start_line + 1].split('-->')
            start = self.srttomicro(timing[0].strip(' \r\n'))
            end = self.srttomicro(timing[1].strip(' \r\n'))
            text = []
            first = True
            for line in inlines[start_line + 2:current_line - 1]:
                if not first:
                    text += [{'type': 'break', 'content': ''}]
                text += [{'type': 'text', 'content': line}]
                first = False

            subdata += [[start, end, text, {}]]
            start_line = current_line

        return {'captions': {lang: subdata}, 'styles': {}}

    def srttomicro(self, stamp):
        timesplit = stamp.split(':')
        secsplit = timesplit[2].split(',')
        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)
        return microseconds


class SRTWriter(BaseWriter):
    def write(self, captions):
        srts = []

        for lang in captions['captions']:
            srts.append(self._recreate_lang(lang, captions))

        return 'MULTI-LANGUAGE SRT\n'.join(srts)

    def _recreate_lang(self, lang, captions):
        srt = ''
        count = 1
        srt += '"%s" SRT Captions\n' % lang
        for sub in captions['captions'][lang]:
            srt += '%s\n' % count
            start = '0' + str(timedelta(milliseconds=(int(sub[0] / 1000))))
            end = '0' + str(timedelta(milliseconds=(int(sub[1] / 1000))))
            timestamp = '%s --> %s\n' % (start[:12], end[:12])
            srt += timestamp.replace('.', ',')
            for line in sub[2]:
                srt = self._recreate_line(srt, line)
            srt += '\n\n'
            count += 1
        return srt[:-1]

    def _recreate_line(self, srt, line):
        if line['type'] == 'text':
            return srt + '%s ' % line['content']
        elif line['type'] == 'break':
            return srt + '\n'
        else:
            return srt
