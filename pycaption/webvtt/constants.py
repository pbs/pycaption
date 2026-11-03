"""Shared constants, compiled patterns, and helpers for the WebVTT package.

All regular expressions are pre-compiled at import time. Module-level
docstrings below each pattern explain what they capture and give examples.
"""

import re

from ..geometry import (
    HorizontalAlignmentEnum,
    LineAlignmentEnum,
    PositionAlignmentEnum,
    WritingDirectionEnum,
)


TIMING_LINE_PATTERN = re.compile(r"^(\S+)\s+-->\s+(\S+)(?:\s+(.*?))?\s*$")
"""
Captures [start_timestamp], [end_timestamp], and optional [cue_settings]
from a WebVTT timing line.
00:00:01.000 --> 00:00:03.000 align:start position:10%
"""
TIMESTAMP_PATTERN = re.compile(r"^(\d+):(\d{2})(:\d{2})?\.(\d{3})")
"""
Parses a single WebVTT timestamp into its components.
Captures: hours (or minutes), minutes (or seconds),
optional :seconds, milliseconds.
00:01:23.456 or 01:23.456
"""
VOICE_SPAN_PATTERN = re.compile("<v(\\.\\w+)* ([^>]*)>")
"""
Matches a voice span opening tag, capturing the speaker annotation.
The speaker name is baked into cue text as "Speaker: " prefix.
<v Roger Bingham> or <v.loud Speaker>
"""
TAG_SPLIT_PATTERN = re.compile(r"(<[^>]+>)")
"""
Splits cue text into alternating [text, tag, text, tag, ...] segments.
The capturing group ensures matched tags are retained in the split result.
"""
KNOWN_TAGS = frozenset({"i", "b", "u", "c", "v", "lang", "ruby", "rt"})
"""
The set of recognized WebVTT inline tag names.
Used for classifying opening (<i>, <c.yellow>, <lang en>) and
closing (</i>, </c>, </v>, </lang>) tags during cue text parsing.
Note: "v" is included so </v> is consumed as a closing style node
(the opening <v> is already handled by VOICE_SPAN_PATTERN).
"""
REGION_SETTING_PATTERN = re.compile(r"^([\w]+):(.+)$")
"""
Matches a setting name (word chars) followed by colon and a value:
id:region1
width:50%
"""
REGION_ANCHOR_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)%,(\d+(?:\.\d+)?)%$")
"""
Matches two percentage values (integer or decimal) separated by a comma:
0%,0%
100%,100%
"""
PERCENTAGE_PATTERN = re.compile(r"([0-9]+(?:\.[0-9]+)?)%")
"""
The WebVTT percentage syntax, to be fullmatched: ASCII digits, an optional
fraction, then %. A sign, an exponent, or nan/inf does not match:
50%  33.33%  (not: +50%  1e1%  nan%)
"""
LINE_NUMBER_PATTERN = re.compile(r"-?[0-9]+(?:\.[0-9]+)?")
"""
A WebVTT line number, to be fullmatched: an optional leading minus, ASCII digits, and an
optional fraction:
3  -1  2.5  (not: +3  1-  .5)
"""
STYLE_SELECTOR_PATTERN = re.compile(
    r"::cue(?:\((\.[\w-]+(?:\.[\w-]+)*|[\w-]+)\))?\s*\{([^}]*)\}"
)
"""
Matches ::cue selectors with their declaration blocks:
::cue { color: white }           -> group(1)=None
::cue(.yellow) { color: yellow } -> group(1)=".yellow"
::cue(b) { color: red }          -> group(1)="b"
group(2) is always the declarations between { }.
Class selectors have a leading dot; tag selectors do not.
"""

LINE_GRID_SIZE = 15
"""Number of lines in the WebVTT virtual line grid used for integer
line positioning (W3C WebVTT spec §7.2)."""

LINE_HEIGHT_VH = 5.33
"""Approximate viewport-height percentage per line (100 / ~18.75),
used to convert region ``lines`` count into a vh-based extent."""

WEBVTT_VERSION_OF = {
    HorizontalAlignmentEnum.LEFT: "left",
    HorizontalAlignmentEnum.CENTER: "center",
    HorizontalAlignmentEnum.RIGHT: "right",
    HorizontalAlignmentEnum.START: "start",
    HorizontalAlignmentEnum.END: "end",
}
"""Maps internal HorizontalAlignmentEnum values to their WebVTT
``align`` cue setting string equivalents."""

DEFAULT_LINE_PERCENT = (LINE_GRID_SIZE - 1) / LINE_GRID_SIZE * 100
"""Where a cue with no ``line`` goes: the last line of the grid, as WebVTT's
auto line (-1) puts it."""

DEFAULT_ALIGN = "center"
"""The WebVTT ``align`` default, written for a caption whose source format
declares no default of its own."""

ALIGN_SETTING_MAP = {
    "start": HorizontalAlignmentEnum.START,
    "center": HorizontalAlignmentEnum.CENTER,
    "end": HorizontalAlignmentEnum.END,
    "left": HorizontalAlignmentEnum.LEFT,
    "right": HorizontalAlignmentEnum.RIGHT,
}
"""Reverse mapping from WebVTT ``align`` setting strings to internal
HorizontalAlignmentEnum values (used by the reader)."""

POSITION_ALIGN_MAP = {
    "line-left": PositionAlignmentEnum.LINE_LEFT,
    "center": PositionAlignmentEnum.CENTER,
    "line-right": PositionAlignmentEnum.LINE_RIGHT,
}
"""Maps WebVTT positionAlign qualifier strings to PositionAlignmentEnum.
The ``start``/``middle``/``end`` of earlier drafts are not valid WebVTT, so
a position qualified with them is ignored."""

VERTICAL_SETTING_MAP = {
    "rl": WritingDirectionEnum.VERTICAL_RL,
    "lr": WritingDirectionEnum.VERTICAL_LR,
}
"""Maps WebVTT ``vertical`` setting strings to WritingDirectionEnum."""

LINE_ALIGN_MAP = {
    "start": LineAlignmentEnum.START,
    "center": LineAlignmentEnum.CENTER,
    "end": LineAlignmentEnum.END,
}
"""Maps WebVTT lineAlign qualifier strings to LineAlignmentEnum."""


def _is_note_start(line):
    """Return True if the line begins a WebVTT NOTE block."""
    return line == "NOTE" or line.startswith("NOTE ") or line.startswith("NOTE\t")


def microseconds(h, m, s, f):
    """
    Returns an integer representing a number of microseconds
    :rtype: int
    """
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000000 + int(f) * 1000
