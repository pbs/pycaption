from pycaption import BaseWriter, CaptionData


class WebVTTWriter(BaseWriter):
    HEADER = u'WEBVTT\n\n'

    def __init__(self, *args, **kw):
        pass

    def write(self, captionset):
        output = self.HEADER

        if captionset.is_empty():
            return

        # TODO: styles. These go into a separate CSS file, which doesn't
        # really fit the API here. Figure that out.
        # Though some style stuff can be done in-line.
        # This format is a little bit crazy.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        lang = captionset.get_languages()[0]
        for sub in captionset.get_captions(lang):
            output += self._write_sub(sub)
            output += '\n'

        return output.encode("UTF-8")

    def _timestamp(self, ts):
        ts = float(ts)/1000000
        hours = int(ts)/60/60
        minutes = int(ts)/60 - hours*60
        seconds = ts - hours*60*60 - minutes*60
        if hours:
          return "%02d:%02d:%06.3f" % (hours, minutes, seconds)
        elif minutes:
          return "%02d:%06.3f" % (minutes, seconds)
        else:
          return "%06.3f" % (seconds,)

    def _write_sub(self, sub):
        start = self._timestamp(sub.start)
        end = self._timestamp(sub.end)

        output = u"%s --> %s\n" % (start, end)
        output += self._convert_nodes(sub.nodes)
        output += u'\n'

        return output

    def _convert_nodes(self, nodes):
        s = u''
        for node in nodes:
            if node.type == CaptionData.TEXT:
              s += node.content
            elif node.type == CaptionData.STYLE:
              # TODO: Ignoring style so far.
              pass
            elif node.type == CaptionData.BREAK:
              s += u'\n'

        return s


