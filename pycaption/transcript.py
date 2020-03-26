import os

try:
    import nltk.data
except ImportError:
    raise ImportError(u'You must install nltk==2.0.4 and numpy==1.7.1 to be able to use this.')
from pycaption.base import BaseWriter, CaptionNode


class TranscriptWriter(BaseWriter):
    def __init__(self, *args, **kw):
        self.nltk = nltk.data.load(u'file:%s/english.pickle' %
                                   os.path.dirname(__file__))

    def write(self, captions):
        transcripts = []

        for lang in captions.get_languages():
            lang_transcript = u'* %s Transcript *\n' % lang.upper()

            for caption in captions.get_captions(lang):
                lang_transcript = self._strip_text(caption.nodes, lang_transcript)

            lang_transcript = u'\n'.join(self.nltk.tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return u'\n'.join(transcripts)

    def _strip_text(self, elements, lang_transcript):
        for el in elements:
            if el.type_ == CaptionNode.TEXT:
                lang_transcript += el.content
        return lang_transcript
