"""Shared constants, compiled patterns, and helpers for the WebVTT package.

All regular expressions are pre-compiled at import time. Module-level
docstrings below each pattern explain what they capture and give examples.
"""

import re

from ..geometry import HorizontalAlignmentEnum

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
CUE_SETTING_PATTERN = re.compile(r"(position|line|size|align|vertical):([\w.%-]+)")
"""
Matches individual cue settings from the timing line:
position:50%  line:75%  size:80%  align:center  vertical:rl
"""
STYLE_SELECTOR_PATTERN = re.compile(r"::cue(?:\((\.?[\w-]+)\))?\s*\{([^}]*)\}")
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

# Fallback for captions with no alignment info
# (not the WebVTT spec default, which is "center")
DEFAULT_ALIGN = "start"

ALIGN_SETTING_MAP = {
    "start": HorizontalAlignmentEnum.START,
    "center": HorizontalAlignmentEnum.CENTER,
    "end": HorizontalAlignmentEnum.END,
    "left": HorizontalAlignmentEnum.LEFT,
    "right": HorizontalAlignmentEnum.RIGHT,
}
"""Reverse mapping from WebVTT ``align`` setting strings to internal
HorizontalAlignmentEnum values (used by the reader)."""


def _is_note_start(line):
    """Return True if the line begins a WebVTT NOTE block."""
    return line == "NOTE" or line.startswith("NOTE ") or line.startswith("NOTE\t")


def microseconds(h, m, s, f):
    """
    Returns an integer representing a number of microseconds
    :rtype: int
    """
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000000 + int(f) * 1000
