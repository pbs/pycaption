"""Plain-text transcript writer (requires nltk for sentence splitting)."""

from pycaption.base import BaseWriter, CaptionNode


class TranscriptWriter(BaseWriter):
    """Writes captions as a plain-text transcript with sentence boundaries.

    Requires the ``nltk`` package. All timing and styling information is
    discarded; only the text content is emitted, split into sentences.
    """

    def __init__(self, *args, **kw):
        try:
            from nltk import PunktSentenceTokenizer

            self.tokenizer = PunktSentenceTokenizer()
        except ModuleNotFoundError as exc:
            raise ModuleNotFoundError(
                "Missing Dependency: You must install nltk"
            ) from exc

    def write(self, captions):
        """Write a CaptionSet as sentence-split plain text.

        :type captions: CaptionSet
        :rtype: str
        """
        transcripts = []

        for lang in captions.get_languages():
            lang_transcript = ""

            for caption in captions.get_captions(lang):
                lang_transcript = self._strip_text(caption.nodes, lang_transcript)

            lang_transcript = "\n".join(self.tokenizer.tokenize(lang_transcript))
            transcripts.append(lang_transcript)

        return "\n".join(transcripts)

    def _strip_text(self, elements, lang_transcript):
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
