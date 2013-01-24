from datetime import timedelta
from pycaption import BaseReader, BaseWriter


class WebVTTWriter(BaseWriter):
    HEADER = u'WEBVTT\n\n'

    def __init__(self, *args, **kw):
        pass

    def write(self, captions):
        output = self.HEADER

        if not captions['captions']:
            return

        # TODO: styles. These go into a separate CSS file, which doesn't
        # really fit the API here.

        # WebVTT's language support seems to be a bit crazy, so let's just
        # support a single one for now.
        for sub in captions['captions'][captions['captions'].keys()[0]]:
            self._write_sub(output, sub)
            output += '\n\n'

        return output.encode("UTF-8")

    def _timestamp(self, ts):
        hours = int(ts)/60/60
        minutes = int(ts)/60 - hours*60
        seconds = ts - hours*60*60 - minutes*60
        if hours:
          return "%02d:%02d:%02.3f" % (hours, minutes, seconds)
        elif minutes:
          return "%02d:%02.3f" % (minutes, seconds)
        else:
          return "%02.3f" % (seconds,)

    def _write_sub(self, output, sub):
        # TODO: Need to make these into real objects :-(
        start = self._timestamp(sub[0])
        end = self._timestamp(sub[1])

        output += "%s --> %s\n" % (start, end)
        # TODO: Figure out what 'sub[2]' actually contains, and munge
        # as appropriate.
        # And turn this fucker into real objects, this sucks.
        print sub[2]
        output += sub[2]
        output += '\n\n'

