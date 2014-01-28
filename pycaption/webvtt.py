import re

from pycaption import BaseWriter, CaptionNode
from .srt import SRTReader


class WebVTTReader(SRTReader):
    def detect(self, content):
        return 'WEBVTT' in content

    def read(self, content, lang='en-US'):

        # TODO: styles. Currently, we clean the WebVTT file to look like an SRT
        # file; longterm, it makes sense to parse the styles.  When we parse
        # styles, it may make sense t

        content = self.force_byte_string(content)
        cleaned_content = self._clean(content)
        return super(WebVTTReader, self).read(cleaned_content)

    def _clean(self, content):
        lines = content.splitlines()
        new_lines = []

        # remove header and metadata
        start_line = 1
        for line in lines:
            if line != '':
                start_line += 1
            else:
                break
        lines = lines[start_line:]

        # clean the rest of the file
        open_note = False
        last_line_blank = False
        for line in lines:
            # remove notes
            if line[:4] == 'NOTE':
                open_note = True
            elif open_note:
                if line == '':
                    open_note = False
            else:
                if line == '':
                    # skip blank lines in excess of 1, and blank lines at start
                    # of file
                    if new_lines and not last_line_blank:
                        last_line_blank = True
                        new_lines.append(line)
                    continue
                else:
                    last_line_blank = False

                if '-->' in line:
                    if not new_lines or new_lines[-1] == '':
                        # make mock cue
                        new_lines.append('0')

                    # remove cue settings and ensure proper timestamp format
                    timing = line.split(' --> ')
                    start = timing[0].replace('.', ',')
                    end = timing[1].split(' ')[0].replace('.', ',')
                    if start.count(':') < 2:
                        start = '00:%s' % start
                    if end.count(':') < 2:
                        end = '00:%s' % end

                    new_lines.append('%s --> %s' % (start, end))
                elif (line[0].isdigit()
                        and (not new_lines or new_lines[-1] == '')):
                    new_lines.append(line)
                else:
                    # remove cue payload styles
                    new_lines.append(re.sub('<[^>]*>', '', line))

        return '\n'.join(new_lines)


class WebVTTWriter(BaseWriter):
    HEADER = u'WEBVTT\n\n'

    def __init__(self, *args, **kw):
        pass

    def write(self, caption_set):
        output = self.HEADER

        if caption_set.is_empty():
            return self.force_byte_string(output)

        # TODO: styles. These go into a separate CSS file, which doesn't really
        # fit the API here. Figure that out.  Though some style stuff can be
        # done in-line.  This format is a little bit crazy.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        lang = caption_set.get_languages()[0]
        for caption in caption_set.get_captions(lang):
            output += self._write_caption(caption)
            output += '\n'

        return self.force_byte_string(output)

    def _timestamp(self, ts):
        ts = float(ts)/1000000
        hours = int(ts)/60/60
        minutes = int(ts)/60 - hours*60
        seconds = ts - hours*60*60 - minutes*60
        if hours:
            return "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        else:
            return "%02d:%06.3f" % (minutes, seconds)

    def _write_caption(self, sub):
        start = self._timestamp(sub.start)
        end = self._timestamp(sub.end)

        output = u"%s --> %s\n" % (start, end)
        output += self._convert_nodes(sub.nodes)
        output += u'\n'

        return output

    def _convert_nodes(self, nodes):
        s = u''
        for node in nodes:
            if node.type == CaptionNode.TEXT:
                s += node.content
            elif node.type == CaptionNode.STYLE:
                # TODO: Ignoring style so far.
                pass
            elif node.type == CaptionNode.BREAK:
                s += u'\n'

        return s
