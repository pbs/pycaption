"""Plain-text transcript writer (requires nltk for sentence splitting)."""

from pycaption.base import BaseWriter, CaptionNode


class TranscriptWriter(BaseWriter):
    """Writes captions as a plain-text transcript with sentence boundaries.

    Requires the ``nltk`` package. All timing and styling information is
    discarded; only the text content is emitted, split into sentences.
    """

    def __init__(self, *args, **kw):
        super().__init__(*args, **kw)
        try:
            from nltk import PunktSentenceTokenizer

            self.tokenizer = PunktSentenceTokenizer()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing Dependency: You must install nltk"
            ) from exc

    def write(self, caption_set, **kwargs):
        """Write a CaptionSet as sentence-split plain text.

        :type captions: CaptionSet
        :rtype: str
        """
        transcripts = []

        for lang in caption_set.get_languages():
            lang_transcript = ""

            for caption in caption_set.get_captions(lang):
                lang_transcript = self._strip_text(caption.nodes, lang_transcript)

            lang_transcript = "\n".join(self.tokenizer.tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return "\n".join(transcripts)

    @staticmethod
    def _strip_text(elements, lang_transcript):
        """Extract and concatenate text nodes, appending to the transcript."""
        parts = []
        for el in elements:
            if el.type_ == CaptionNode.TEXT:
                parts.append(el.content)
            elif el.type_ == CaptionNode.BREAK:
                parts.append(" ")
        text = "".join(parts)
        if lang_transcript and text:
            return lang_transcript + " " + text
        return lang_transcript + text
