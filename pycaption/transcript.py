import nltk
from pycaption import BaseWriter


class TranscriptWriter(BaseWriter):
    def write(self, captions):
        transcripts = []

        for lang in captions['captions']:
            lang_transcript = '* %s Transcript *\n' % lang.upper()

            for sub in captions['captions'][lang]:
                lang_transcript = self._strip_text(sub[2], lang_transcript)

            lang_transcript = '\n'.join(nltk.sent_tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return '\n'.join(transcripts)

    def _strip_text(self, elements, lang_transcript):
        for line in elements:
            if line['type'] == 'text':
                lang_transcript += '%s ' % line['content']
        return lang_transcript
