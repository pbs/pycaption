from pycaption import BaseReader, BaseWriter, Caption, CaptionSet, CaptionNode


class SRTReader(BaseReader):
    def detect(self, content):
        lines = content.splitlines()
        if lines[0].isdigit() and '-->' in lines[1]:
            return True
        else:
            return False

    def read(self, content, lang='en-US'):
        content = self.force_byte_string(content)
        caption_set = CaptionSet()
        lines = content.splitlines()
        start_line = 0
        captions = []

        while start_line < len(lines):
            if not lines[start_line].isdigit():
                break

            caption = Caption()

            end_line = self._find_text_line(start_line, lines)

            timing = lines[start_line + 1].split('-->')
            caption.start = self._srttomicro(timing[0].strip(' \r\n'))
            caption.end = self._srttomicro(timing[1].strip(' \r\n'))

            for line in lines[start_line + 2:end_line - 1]:
                # skip extra blank lines
                if not caption.nodes or line != '':
                    caption.nodes.append(CaptionNode.create_text(line))
                    caption.nodes.append(CaptionNode.create_break())

            # remove last line break from end of caption list
            caption.nodes.pop()

            captions.append(caption)
            start_line = end_line

        caption_set.set_captions(lang, captions)
        return caption_set

    def _srttomicro(self, stamp):
        timesplit = stamp.split(':')
        if not ',' in timesplit[2]:
            timesplit[2] = timesplit[2] + ',000'
        secsplit = timesplit[2].split(',')
        microseconds = (int(timesplit[0]) * 3600000000 +
                        int(timesplit[1]) * 60000000 +
                        int(secsplit[0]) * 1000000 +
                        int(secsplit[1]) * 1000)

        return microseconds

    def _find_text_line(self, start_line, lines):
        end_line = start_line + 1

        while end_line < len(lines):
            if lines[end_line].strip() == "":
                return end_line + 1
            end_line += 1

        return end_line + 1


class SRTWriter(BaseWriter):
    def write(self, captions):
        srt_captions = []

        for lang in captions.get_languages():
            srt_captions.append(
                self._recreate_lang(captions.get_captions(lang))
            )

        caption_content = 'MULTI-LANGUAGE SRT\n'.join(srt_captions)
        return self.force_byte_string(caption_content)

    def _recreate_lang(self, captions):
        srt = ''
        count = 1

        for caption in captions:
            srt += '%s\n' % count

            start = caption.format_start(msec_separator=',')
            end = caption.format_end(msec_separator=',')
            timestamp = '%s --> %s\n' % (start[:12], end[:12])

            srt += timestamp.replace('.', ',')
            for node in caption.nodes:
                srt = self._recreate_line(srt, node)

            srt += '\n\n'
            count += 1

        return srt[:-1]  # remove unwanted newline at end of file

    def _recreate_line(self, srt, line):
        if line.type == CaptionNode.TEXT:
            return srt + '%s ' % line.content
        elif line.type == CaptionNode.BREAK:
            return srt + '\n'
        else:
            return srt
