import nltk
from pycaption import BaseWriter


class TranscriptWriter(BaseWriter):
    def write(self, captions):
        transcripts = []

        for lang in captions['captions']:
            lang_transcript = '* %s Transcript *\n' % lang.upper()

            for sub in captions['captions'][lang]:
                for line in sub[2]:
                    if line['type'] == 'text':
                        lang_transcript += '%s ' % line['content']

            lang_transcript = '\n'.join(nltk.sent_tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return '\n'.join(transcripts)
