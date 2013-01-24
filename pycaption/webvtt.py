from datetime import timedelta
from pycaption import BaseReader, BaseWriter, CaptionDataType


class WebVTTWriter(BaseWriter):
    HEADER = u'WEBVTT\n\n'

    def __init__(self, *args, **kw):
        pass

    def write(self, captions):
        output = self.HEADER

        if not captions.captions:
            return

        # TODO: styles. These go into a separate CSS file, which doesn't
        # really fit the API here.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        lang = captions.captions.keys()[0]
        for sub in captions.captions[lang]:
            output += self._write_sub(sub)
            output += '\n'

        return output.encode("UTF-8")

    def _timestamp(self, ts):
        ts = float(ts)/1000000
        hours = int(ts)/60/60
        minutes = int(ts)/60 - hours*60
        seconds = ts - hours*60*60 - minutes*60
        if hours:
          return "%02d:%02d:%02.3f" % (hours, minutes, seconds)
        elif minutes:
          return "%02d:%02.3f" % (minutes, seconds)
        else:
          return "%02.3f" % (seconds,)

    def _write_sub(self, sub):
        start = self._timestamp(sub.start)
        end = self._timestamp(sub.end)

        output = "%s --> %s\n" % (start, end)
        # TODO: Figure out what 'sub[2]' actually contains, and munge
        # as appropriate.
        # And turn this fucker into real objects, this sucks.
        output += self._convert_nodes(sub.nodes)
        output += '\n'

        return output

    def _convert_nodes(self, nodes):
        s = ''
        for node in nodes:
            if node.type == CaptionDataType.TEXT:
              s += node.content
            elif node.type == CaptionDataType.STYLE:
              # TODO: Ignoring style so far.
              pass
            elif node.type == CaptionDataType.BREAK:
              s += '\n'

        return s


