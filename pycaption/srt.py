"""SRT (SubRip) caption format reader and writer."""

from copy import deepcopy

from .base import (
    BaseReader, BaseWriter, Caption, CaptionList, CaptionNode, CaptionSet,
    merge_caption_list,
)
from .exceptions import CaptionReadNoCaptions
from .geometry import HorizontalAlignmentEnum


class SRTReader(BaseReader):
    """Reads SRT subtitle files into a CaptionSet."""

    def detect(self, content):
        """Return True if content looks like an SRT file.

        Checks that the first line is a sequence number and the second
        contains an arrow ('-->').
        """
        content = self._decode_content(content)
        lines = content.splitlines()
        if lines[0].isdigit() and "-->" in lines[1]:
            return True
        else:
            return False

    def read(self, content, lang="en-US"):
        """Parse SRT content into a CaptionSet.

        :param content: Raw SRT file content.
        :param lang: Language code to assign to the captions.
        :rtype: CaptionSet
        :raises InvalidInputError: if content is not a string.
        :raises CaptionReadNoCaptions: if no captions are found.
        """
        content = self._decode_content(content)

        lines = content.splitlines()
        start_line = 0
        captions = CaptionList()

        while start_line < len(lines):
            if not lines[start_line].isdigit():
                break

            end_line = self._find_text_line(start_line, lines)

            timing = lines[start_line + 1].split("-->")
            start = self._srttomicro(timing[0].strip(" \r\n"))
            end = self._srttomicro(timing[1].strip(" \r\n"))

            nodes = []

            for line in lines[start_line + 2 : end_line - 1]:
                # skip extra blank lines
                if not nodes or line != "":
                    nodes.append(CaptionNode.create_text(line))
                    nodes.append(CaptionNode.create_break())

            if len(nodes):
                # remove last line break from end of caption list
                nodes.pop()
                caption = Caption(start, end, nodes)
                captions.append(caption)

            start_line = end_line

        caption_set = CaptionSet(
            {lang: captions},
            visual_alignment_default=HorizontalAlignmentEnum.CENTER,
        )

        if caption_set.is_empty():
            raise CaptionReadNoCaptions("empty caption file")

        return caption_set

    @staticmethod
    def _srttomicro(stamp):
        """Convert an SRT timestamp (HH:MM:SS,mmm) to microseconds."""
        timesplit = stamp.split(":")
        if "," not in timesplit[2]:
            timesplit[2] += ",000"
        secsplit = timesplit[2].split(",")
        microseconds = (
            int(timesplit[0]) * 3600000000
            + int(timesplit[1]) * 60000000
            + int(secsplit[0]) * 1000000
            + int(secsplit[1]) * 1000
        )

        return microseconds

    @staticmethod
    def _find_text_line(start_line, lines):
        """Find the line index where the next cue block ends (first blank)."""
        end_line = start_line

        found = False
        while end_line < len(lines):
            if lines[end_line].strip() == "":
                found = True
            elif found is True:
                end_line -= 1
                break
            end_line += 1

        return end_line + 1


class SRTWriter(BaseWriter):
    """Serializes a CaptionSet to SRT format."""

    def write(self, caption_set, **kwargs):
        """Write a CaptionSet as an SRT string.

        :type caption_set: CaptionSet
        :rtype: str
        """
        caption_set = deepcopy(caption_set)

        srt_captions = []

        for lang in caption_set.get_languages():
            srt_captions.append(self._recreate_lang(caption_set.get_captions(lang)))

        caption_content = "MULTI-LANGUAGE SRT\n".join(srt_captions)
        return caption_content

    def _recreate_lang(self, captions):
        """Serialize one language's captions to SRT text.

        Merges consecutive captions with identical timestamps (libass and
        similar players render duplicates in reverse order otherwise).
        """
        captions = merge_caption_list(captions)

        srt = ""
        count = 1

        for caption in captions:
            srt += f"{count}\n"

            start = caption.format_start(msec_separator=",")
            end = caption.format_end(msec_separator=",")

            srt += f"{start[:12]} --> {end[:12]}\n"

            new_content = ""
            for node in caption.nodes:
                new_content = self._recreate_line(new_content, node)

            # Eliminate excessive line breaks
            new_content = new_content.strip()

            srt += f"{new_content}\n\n"
            count += 1

        return srt[:-1]  # remove unwanted newline at end of file

    @staticmethod
    def _recreate_line(srt, line):
        """Append a single CaptionNode's content to the SRT output string."""
        if line.type_ == CaptionNode.TEXT:
            return srt + f"{line.content} "
        elif line.type_ == CaptionNode.BREAK:
            return srt + "\n"
        else:
            return srt
