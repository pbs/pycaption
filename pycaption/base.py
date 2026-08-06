"""Core data model for pycaption.

Defines the intermediate representation used by all readers and writers:
CaptionSet -> CaptionList -> Caption -> CaptionNode.  Also provides the
CaptionConverter orchestrator and base classes for readers/writers.
"""

import logging
import os
from datetime import timedelta
from numbers import Number

from .exceptions import CaptionReadError, CaptionReadTimingError, InvalidInputError

logger = logging.getLogger(__name__)

# `und` a special identifier for an undetermined language according to ISO 639-2
DEFAULT_LANGUAGE_CODE = os.getenv("PYCAPTION_DEFAULT_LANG", "und")


class CaptionConverter:
    """High-level orchestrator: read content with a reader, write with a writer.

    Usage::

        converter = CaptionConverter()
        converter.read(srt_content, SRTReader())
        output = converter.write(WebVTTWriter())
    """

    def __init__(self, captions=None):
        self.captions = captions

    def read(self, content, caption_reader):
        """Parse caption content using the given reader.

        :param content: Raw caption file content (string).
        :param caption_reader: A BaseReader subclass instance.
        :returns: self (for chaining).
        """
        if not hasattr(caption_reader, "read"):
            raise InvalidInputError(
                "The caption_reader must be a BaseReader instance "
                "with a read() method."
            )
        self.captions = caption_reader.read(content)
        return self

    def write(self, caption_writer):
        """Serialize the stored CaptionSet using the given writer.

        :param caption_writer: A BaseWriter subclass instance.
        :returns: The serialized caption string.
        :rtype: str
        """
        if not hasattr(caption_writer, "write"):
            raise InvalidInputError(
                "The caption_writer must be a BaseWriter instance "
                "with a write() method."
            )
        return caption_writer.write(self.captions)


class BaseReader:
    """Abstract base class for caption format readers."""

    def __init__(self, *args, **kwargs):
        pass

    @staticmethod
    def _decode_content(content):
        """Decode bytes to str (UTF-8 with BOM handling).

        :param content: str or bytes input.
        :returns: decoded str with BOM stripped.
        :raises InvalidInputError: if content is not str/bytes, is empty
            bytes, or is not valid UTF-8.
        """
        if isinstance(content, bytes):
            if not content:
                raise InvalidInputError("The content is empty.")
            try:
                content = content.decode("utf-8-sig")
            except UnicodeDecodeError as e:
                raise InvalidInputError(f"Content is not valid UTF-8: {e}") from e
        elif isinstance(content, str):
            if content.startswith("﻿"):
                content = content[1:]
        else:
            raise InvalidInputError(
                "The content must be a unicode string or UTF-8 bytes."
            )
        content = BaseReader._repair_double_encoding(content)
        return content

    @staticmethod
    def _repair_double_encoding(text):
        """Fix double-encoded UTF-8 (bytes misread as CP-1252)."""
        try:
            repaired = text.encode("cp1252").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            return text
        if repaired != text:
            logger.warning(
                "Detected and repaired double-encoded UTF-8 in caption content"
            )
            return repaired
        return text

    def detect(self, content):
        """Return True if content appears to be in this reader's format.

        :param content: Raw caption file content.
        :rtype: bool
        """
        return bool(content)

    def read(self, content):
        """Parse content into a CaptionSet.

        :param content: Raw caption file content.
        :rtype: CaptionSet
        """
        return CaptionSet({DEFAULT_LANGUAGE_CODE: []})


class BaseWriter:
    """Abstract base class for caption format writers."""

    def __init__(
        self, relativize=True, video_width=None, video_height=None, fit_to_screen=True
    ):
        """
        Initialize writer with the given parameters.

        :param relativize: If True (default), converts absolute positioning
            values (e.g. px) to percentage. ATTENTION: WebVTT does not support
            absolute positioning. If relativize is set to False and it finds
            an absolute positioning parameter for a given caption, it will
            ignore all positioning for that cue and show it in the default
            position.
        :param video_width: The width of the video for which the captions being
            converted were made. This is necessary for relativization.
        :param video_height: The height of the video for which the captions
            being converted were made. This is necessary for relativization.
        :param fit_to_screen: If extent is not set or
            if origin + extent > 100%, (re)calculate it based on origin.
            It is a pycaption fix for caption files that are technically valid
            but contains inconsistent settings that may cause long captions to
            be cut out of the screen.
        """
        self.relativize = relativize
        self.video_width = video_width
        self.video_height = video_height
        self.fit_to_screen = fit_to_screen

    @staticmethod
    def _get_visual_alignment_default(caption_set):
        """Return the source format's visual alignment default from a CaptionSet.

        Per SMPTE RP 2052-10, caption formats have different implicit visual
        defaults when no alignment is specified:
        - CENTER: WebVTT, SRT, SCC, MicroDVD
        - LEFT/START: DFXP/TTML, SAMI

        When converting between formats with mismatched defaults, the source
        default must be made explicit in the output to prevent visual
        regression (e.g. centered text silently becoming left-aligned).

        Readers declare their default via CaptionSet.visual_alignment_default.
        Writers compare it to their own format's default to decide whether
        to emit explicit alignment.

        :type caption_set: CaptionSet
        :rtype: HorizontalAlignmentEnum | None
        """
        return caption_set.visual_alignment_default if caption_set else None

    def _relativize_and_fit_to_screen(self, layout_info):
        """Apply relativization and fit-to-screen adjustments to a Layout.

        :param layout_info: A Layout instance (or None).
        :rtype: Layout | None
        """
        if layout_info:
            if self.relativize:
                # Transform absolute values (e.g. px) into percentages
                layout_info = layout_info.as_percentage_of(
                    self.video_width, self.video_height
                )
            if self.fit_to_screen:
                # Make sure origin + extent <= 100%
                layout_info = layout_info.fit_to_screen()
        return layout_info

    def write(self, caption_set, **kwargs):
        """Serialize a CaptionSet. Subclasses override this.

        :type caption_set: CaptionSet
        :param kwargs: Format-specific options (e.g. force, lang).
        :rtype: str
        """
        return caption_set


class CaptionNode:
    """
    A single node within a caption, representing either
    text, a style, or a linebreak.

    Rules:
        1. All nodes should have the property layout_info set.
        The value None means specifically that no positioning information
        should be specified. Each reader is to supply its own default
        values (if necessary) when reading their respective formats.
    """

    TEXT = 1
    STYLE = 2
    BREAK = 3

    def __init__(
        self, type_, layout_info=None, content=None, start=None, position=None
    ):
        """
        :type type_: int
        :type layout_info: Layout
        """
        self.type_ = type_
        self.content = content
        self.position = position

        # Boolean. Marks the beginning/ end of a Style node.
        self.start = start
        self.layout_info = layout_info

    def __repr__(self):
        t = self.type_

        if t == CaptionNode.TEXT:
            return repr(self.content)
        elif t == CaptionNode.BREAK:
            return repr("BREAK")
        elif t == CaptionNode.STYLE:
            return repr(f"STYLE: {self.start} {self.content}")
        else:
            raise RuntimeError(f"Unknown node type: {t}")

    @staticmethod
    def create_text(text, layout_info=None, position=None):
        """Create a TEXT node with the given content string."""
        return CaptionNode(
            type_=CaptionNode.TEXT,
            layout_info=layout_info,
            position=position,
            content=text,
        )

    @staticmethod
    def create_style(start, content, layout_info=None):
        """Create a STYLE node (start=True opens, start=False closes)."""
        return CaptionNode(
            type_=CaptionNode.STYLE,
            layout_info=layout_info,
            content=content,
            start=start,
        )

    @staticmethod
    def create_break(layout_info=None, content=None):
        """Create a BREAK (line-break) node."""
        return CaptionNode(
            type_=CaptionNode.BREAK, layout_info=layout_info, content=content
        )


class Caption:
    """
    A single caption, including the time and styling information
    for its display.
    """

    def __init__(self, start, end, nodes, style=None, layout_info=None):
        """
        Initialize the Caption object
        :param start: The start time in microseconds
        :type start: int
        :param end: The end time in microseconds
        :type end: int
        :param nodes: A list of CaptionNodes
        :type nodes: list
        :param style: A dictionary with CSS-like styling rules
        :type style: dict
        :param layout_info: A Layout object with the necessary positioning
            information
        :type layout_info: Layout
        """
        if not isinstance(start, Number):
            raise CaptionReadTimingError(
                "Captions must be initialized with a valid start time"
            )
        if not isinstance(end, Number):
            raise CaptionReadTimingError(
                "Captions must be initialized with a valid end time"
            )
        if not nodes:
            raise CaptionReadError("Node list cannot be empty")
        self.start = start
        self.end = end
        self.nodes = nodes
        self.style = style or {}
        self.layout_info = layout_info
        self.caption_mode = None
        self.roll_up_rows = None

    def format_start(self, msec_separator=None):
        """Format start time as HH:MM:SS.mmm string.

        :param msec_separator: Character between seconds and milliseconds
            (default '.').
        :rtype: str
        """
        return self._format_timestamp(self.start, msec_separator)

    def format_end(self, msec_separator=None):
        """Format end time as HH:MM:SS.mmm string.

        :param msec_separator: Character between seconds and milliseconds
            (default '.').
        :rtype: str
        """
        return self._format_timestamp(self.end, msec_separator)

    def __repr__(self):
        return repr(f"{self.format_start()} --> {self.format_end()}\n{self.get_text()}")

    def get_text_nodes(self):
        """Return list of text content strings (with '\\n' for breaks).

        :rtype: list[str]
        """
        return [
            node.content if node.type_ == CaptionNode.TEXT else "\n"
            for node in self.nodes
            if node.type_ in (CaptionNode.TEXT, CaptionNode.BREAK)
        ]

    def get_text(self):
        """Return the plain text content of this caption (no markup).

        :rtype: str
        """
        return "".join(self.get_text_nodes()).strip()

    @staticmethod
    def _format_timestamp(microseconds, msec_separator=None):
        """Convert microseconds to HH:MM:SS{sep}mmm string."""
        duration = timedelta(microseconds=microseconds)
        hours, rem = divmod(duration.seconds, 3600)
        minutes, seconds = divmod(rem, 60)
        milliseconds = duration.microseconds // 1000
        return (
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            f"{msec_separator or '.'}{milliseconds:03d}"
        )


class CaptionList(list):
    """A list of captions with a layout object attached to it"""

    def __init__(self, iterable=None, layout_info=None):
        """
        :param iterable: An iterator used to populate the caption list
        :param Layout layout_info: A Layout object with the positioning info
        """
        self.layout_info = layout_info
        args = [iterable] if iterable else []
        super().__init__(*args)

    def __getitem__(self, y):
        item = list.__getitem__(self, y)
        if isinstance(item, Caption):
            return item
        return CaptionList(item, layout_info=self.layout_info)

    def __add__(self, value):
        add_is_safe = (
            not hasattr(value, "layout_info")
            or not value.layout_info
            or self.layout_info == value.layout_info
        )
        if add_is_safe:
            return CaptionList(list.__add__(self, value), layout_info=self.layout_info)
        else:
            raise ValueError(
                "Cannot add CaptionList objects with different layout_info"
            )

    def __mul__(self, other):
        return CaptionList(list.__mul__(self, other), layout_info=self.layout_info)

    __rmul__ = __mul__


class CaptionSet:
    """
    A set of captions in potentially multiple languages,
    all representing the same underlying content.

    The .layout_info attribute, keeps information that should be inherited
    by all the children.
    """

    def __init__(
        self,
        captions,
        styles=None,
        layout_info=None,
        regions=None,
        visual_alignment_default=None,
    ):
        """
        :param captions: A dictionary of the format {'language': CaptionList}
        :param styles: A dictionary with CSS-like styling rules
        :param Layout layout_info: A Layout object with the positioning info
        :param regions: A dictionary mapping region id to raw settings dict
        :param visual_alignment_default: The source format's implicit text
            alignment when no explicit alignment is specified. Per SMPTE
            RP 2052-10, writers targeting a format with a different visual
            default must emit this alignment explicitly to prevent visual
            regression. Use HorizontalAlignmentEnum values.
        :type visual_alignment_default: HorizontalAlignmentEnum | None
        """
        self._captions = captions
        self._styles = styles or {}
        self._regions = regions or {}
        self.layout_info = layout_info
        self.visual_alignment_default = visual_alignment_default

    def set_captions(self, lang, captions):
        """Replace the caption list for a given language.

        :param lang: Language code (e.g. 'en-US').
        :param captions: A CaptionList instance.
        """
        self._captions[lang] = captions

    def get_languages(self):
        """Return list of language codes in this caption set.

        :rtype: list[str]
        """
        return list(self._captions.keys())

    def get_captions(self, lang):
        """Return the CaptionList for the given language, or empty list.

        :param lang: Language code.
        :rtype: CaptionList | list
        """
        return self._captions.get(lang, [])

    def add_style(self, selector, rules):
        """
        :param selector: The selector indicating the elements to which the
            rules should be applied.
        :param rules: A dictionary with CSS-like styling rules.
        """
        self._styles[selector] = rules

    def get_style(self, selector):
        """
        Returns a dictionary with CSS-like styling rules for a given selector.
        :param selector: The selector whose rules should be returned (e.g. an
            element or class name).
        """
        return self._styles.get(selector, {})

    def get_styles(self):
        """Return all styles as sorted (selector, rules) pairs.

        :rtype: list[tuple[str, dict]]
        """
        return sorted(self._styles.items())

    def set_styles(self, styles):
        """Replace all styles with the given dictionary.

        :param styles: dict mapping selectors to rule dictionaries.
        """
        self._styles = styles

    def get_regions(self):
        """Return raw region definitions for the writer to re-emit.

        :rtype: dict[str, dict[str, str]]
        """
        return self._regions

    def set_regions(self, regions):
        """Replace all region definitions.

        :param regions: dict mapping region id to settings dict.
        """
        self._regions = regions

    def is_empty(self):
        """Return True if no language contains any captions."""
        for captions in self._captions.values():
            if len(captions) > 0:
                return False
        return True

    def set_layout_info(self, lang, layout_info):
        """Set the layout_info on the CaptionList for a given language.

        :param lang: Language code.
        :param layout_info: A Layout instance.
        """
        self._captions[lang].layout_info = layout_info

    def get_layout_info(self, lang):
        """Return the layout_info for a given language's CaptionList.

        :param lang: Language code.
        :rtype: Layout | None
        """
        caption_list = self._captions.get(lang)
        if caption_list:
            return caption_list.layout_info
        return None

    def adjust_caption_timing(self, offset=0, rate_skew=1.0):
        """
        Adjust the timing according to offset and rate_skew.
        Skew is applied first, then offset.

        e.g. if skew == 1.1, and offset is 5, a caption originally
        displayed from 10-11 seconds would instead be at 16-17.1
        """
        for lang in self.get_languages():
            captions = self.get_captions(lang)
            out_captions = CaptionList()
            for caption in captions:
                caption.start = caption.start * rate_skew + offset
                caption.end = caption.end * rate_skew + offset
                if caption.start >= 0:
                    out_captions.append(caption)
            self.set_captions(lang, out_captions)


def merge_concurrent_captions(caption_set):
    """Merge captions that have the same start and end times"""
    for lang in caption_set.get_languages():
        captions = caption_set.get_captions(lang)
        merged = merge_caption_list(captions)
        if merged:
            caption_set.set_captions(lang, merged)
    return caption_set


def merge_caption_list(captions):
    """Merge consecutive captions with identical start/end times into one."""
    if not captions:
        return CaptionList()
    last_caption = None
    concurrent_captions = CaptionList()
    merged_captions = CaptionList()
    for caption in captions:
        if last_caption:
            last_timespan = last_caption.start, last_caption.end
            current_timespan = caption.start, caption.end
            if current_timespan == last_timespan:
                concurrent_captions.append(caption)
                last_caption = caption
                continue
            else:
                merged_captions.append(_merge_group(concurrent_captions))
        concurrent_captions = [caption]
        last_caption = caption

    if concurrent_captions:
        merged_captions.append(_merge_group(concurrent_captions))
    return merged_captions


def _merge_group(captions):
    """Merge a group of captions into one, keeping the first caption's timing."""
    new_nodes = []
    for caption in captions:
        if new_nodes:
            new_nodes.append(CaptionNode.create_break())
        new_nodes.extend(caption.nodes)
    return Caption(captions[0].start, captions[0].end, new_nodes, captions[0].style)
