import nltk.data
import os
from pycaption import BaseWriter, CaptionData


class TranscriptWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.nltk = nltk.data.load('file:%s/english.pickle' %
                                   os.path.dirname(__file__))

    def write(self, captions):
        transcripts = []

        for lang in captions.get_languages():
            lang_transcript = '* %s Transcript *\n' % lang.upper()

            for sub in captions.get_captions(lang):
                lang_transcript = self._strip_text(sub.nodes, lang_transcript)

            lang_transcript = '\n'.join(self.nltk.tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return '\n'.join(transcripts)

    def _strip_text(self, elements, lang_transcript):
        for el in elements:
            if el.type == CaptionData.TEXT:
                lang_transcript += el.content
        return lang_transcript
