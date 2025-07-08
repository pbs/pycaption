from pycaption.base import BaseWriter, CaptionNode


class TranscriptWriter(BaseWriter):
    def __init__(self, *args, **kw):
        try:
            from nltk import PunktSentenceTokenizer

            self.tokenizer = PunktSentenceTokenizer()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing Dependency: You must install nltk"
            ) from exc

    def write(self, captions):
        transcripts = []

        for lang in captions.get_languages():
            lang_transcript = ""

            for caption in captions.get_captions(lang):
                lang_transcript = self._strip_text(caption.nodes, lang_transcript)

            lang_transcript = "\n".join(self.tokenizer.tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return "\n".join(transcripts)

    def _strip_text(self, elements, lang_transcript):
        return " ".join(
            [lang_transcript]
            + [el.content for el in elements if el.type_ == CaptionNode.TEXT]
        )
