"""WebVTT cue settings, parsed as WebVTT does, and the cue box they give.

Follows the W3C WebVTT spec (https://www.w3.org/TR/webvtt1/): the cue settings
parsing rules, the computed position and computed position alignment of a
cue, and the cue box's maximum size and offset from the rendering rules
(including those for a cue inside a region). The box is resolved here, once,
so a WebVTT Layout's origin is always the box's left (or, for vertical text,
top) edge, as it is for every other format.
"""

import math
import re

from dataclasses import dataclass

from ..geometry import (
    POSITION_ALIGNMENT_SHARE,
    LineAlignmentEnum,
    Point,
    PositionAlignmentEnum,
    Size,
    Stretch,
    UnitEnum,
    WritingDirectionEnum,
    webvtt_cue_span,
)
from .constants import (
    ALIGN_SETTING_MAP,
    AUTO_POSITION_ALIGN_FOR,
    DEFAULT_LINE_PERCENT,
    LINE_ALIGN_MAP,
    LINE_GRID_SIZE,
    LINE_NUMBER_PATTERN,
    PERCENTAGE_PATTERN,
    POSITION_ALIGN_MAP,
    VERTICAL_SETTING_MAP,
)


_AUTO_POSITION_FOR = {"left": 0.0, "right": 100.0}
"""WebVTT's computed position, by align, for a cue with no position: 0% for
left, 100% for right, and 50% for every other align, or none."""

_SPACES = re.compile(r"[ \t\n\f\r]+")
"""WebVTT splits the settings on ASCII whitespace only, so a no-break space
is part of a setting, not a separator."""


@dataclass
class CueSettings:
    """A cue's valid settings. None is a setting not given (WebVTT's auto)."""

    vertical: WritingDirectionEnum | None = None
    line: float | None = None
    line_is_percent: bool = False
    line_align: LineAlignmentEnum | None = None
    position: float | None = None
    position_align: PositionAlignmentEnum | None = None
    size: float | None = None
    align: str | None = None
    region: str | None = None

    @classmethod
    def parse(cls, cue_settings, region_ids=()):
        """Parse a cue settings string, as WebVTT does.

        Each space-separated token is split at its first colon. A setting
        with an unknown name, or any part of its value invalid, is skipped
        as if not given, so an earlier valid one stands.

        The settings are read in order, so as in WebVTT a valid line, or a
        size other than 100%, takes the cue out of a region named before
        it but not of one named after it. region names the last REGION
        with that id, or none if no id in region_ids matches.
        """
        settings = cls()
        for token in _SPACES.split(cue_settings):
            name, _, value = token.partition(":")
            if name == "region" and value:
                settings.region = value if value in region_ids else None
                continue
            parse = _SETTING_PARSERS.get(name)
            if parse and value:
                parse(settings, value)
        return settings

    def computed_position(self):
        """The position, or WebVTT's computed one when none is given."""
        if self.position is not None:
            return self.position
        return _AUTO_POSITION_FOR.get(self.align, 50.0)

    def computed_position_alignment(self):
        """The position's qualifier, or where align puts the text."""
        if self.position_align:
            return self.position_align
        return AUTO_POSITION_ALIGN_FOR.get(self.align, PositionAlignmentEnum.CENTER)

    def stays_in_region(self):
        """Whether a cue that names a region is laid out in it.

        parse already took out a cue whose line or size followed its
        region. A vertical cue never stays, whatever the order: WebVTT
        notes there are no vertical regions.
        """
        return self.region is not None and not self.vertical

    def places_box(self):
        """Whether the settings put the box anywhere but the default place.

        That is any position, line, size or vertical setting, or an align
        whose computed position leaves the box narrower than the screen:
        start and end, which anchor an edge at 50%. A cue with neither has
        the default box, the whole width of the last line, so it gets none.
        """
        given = (self.position, self.line, self.size, self.vertical)
        if any(setting is not None for setting in given):
            return True
        return self.align in ("start", "end")

    def line_percent(self):
        """The line as a percentage offset across the lines.

        A missing line is WebVTT's auto, the last line of the grid (the
        leftmost for ``vertical:rl``). A line number is rounded, as WebVTT
        does, and placed on the 15-line grid: from the top (0) or the
        bottom (-1), and for vertical text across the width, from the right
        edge for ``vertical:rl``.
        """
        rl = self.vertical == WritingDirectionEnum.VERTICAL_RL
        if self.line is None:
            return 0.0 if rl else DEFAULT_LINE_PERCENT
        if self.line_is_percent:
            return self.line
        line = math.floor(self.line + 0.5)
        if line >= 0:
            pct = min(line / LINE_GRID_SIZE * 100, 100.0)
        else:
            pct = max((LINE_GRID_SIZE + line) / LINE_GRID_SIZE * 100, 0.0)
        if rl:
            return max(100 - 100 / LINE_GRID_SIZE - pct, 0.0)
        return pct


def cue_box(settings, region=None):
    """Return the (origin, extent) of a cue's box, or (None, None).

    The box of a cue in a region is the region's (see _region_box).
    Otherwise it spans webvtt_cue_span along the position axis (x for
    horizontal text, y for vertical) and starts at the line on the other
    axis. Its extent is the whole screen across the lines, and is None
    when the box reaches the far edge with the default size.

    :param settings: The cue's CueSettings.
    :param region: Layout of the region the cue names, if any.
    """
    if region and region.origin and region.extent and settings.stays_in_region():
        return _region_box(settings, region)
    if not settings.places_box():
        return None, None

    left, width = webvtt_cue_span(
        settings.computed_position(),
        settings.size,
        settings.computed_position_alignment(),
    )
    left = _percent(left)
    line = _percent(settings.line_percent())
    full = _percent(100)
    if settings.vertical:
        origin = Point(line, left)
        extent = None if width is None else Stretch(full, _percent(width))
    else:
        origin = Point(left, line)
        extent = None if width is None else Stretch(_percent(width), full)
    return origin, extent


def _region_box(settings, region):
    """Return the (origin, extent) of a cue that stays in its region.

    As WebVTT renders it: the cue box is as wide as the region and is
    shifted by its offset, the computed position times the region width
    over 100, less half the region width (center) or all of it
    (line-right), taken as a percentage of the region width. The region
    hides what overflows it, so the box is the part left inside. With the
    default anchors (left, center, right) the offset is 0, and the box is
    the region.
    """
    width = region.extent.horizontal.value
    offset = settings.computed_position() * width / 100
    share = POSITION_ALIGNMENT_SHARE[settings.computed_position_alignment()]
    offset -= share * width
    shift = offset * width / 100
    origin = Point(_percent(region.origin.x.value + max(shift, 0)), region.origin.y)
    extent = Stretch(_percent(width - abs(shift)), region.extent.vertical)
    return origin, extent


def _percent(value):
    return Size(value, UnitEnum.PERCENT)


def _parse_percentage(value):
    """Parse a WebVTT percentage, 0-100%; None if invalid ("+5%", "1e1%")."""
    match = PERCENTAGE_PATTERN.fullmatch(value)
    if not match or float(match.group(1)) > 100:
        return None
    return float(match.group(1))


def _split_qualifier(value, qualifiers):
    """Return (value, mapped qualifier or None), or None if it isn't valid.

    An empty qualifier ("50%,") or one not in ``qualifiers`` is invalid.
    """
    if "," not in value:
        return value, None
    value, qualifier = value.split(",", 1)
    if qualifier not in qualifiers:
        return None
    return value, qualifiers[qualifier]


def _parse_vertical(settings, value):
    if value in VERTICAL_SETTING_MAP:
        settings.vertical = VERTICAL_SETTING_MAP[value]


def _parse_line(settings, value):
    split = _split_qualifier(value, LINE_ALIGN_MAP)
    if not split:
        return
    number, qualifier = split
    if number.endswith("%"):
        line = _parse_percentage(number)
    elif LINE_NUMBER_PATTERN.fullmatch(number):
        line = float(number)
    else:
        return
    if line is None:
        return
    settings.line, settings.line_is_percent = line, number.endswith("%")
    if qualifier:
        settings.line_align = qualifier
    # Explicitly placed: the cue drops out of the region named before it
    settings.region = None


def _parse_position(settings, value):
    split = _split_qualifier(value, POSITION_ALIGN_MAP)
    if not split:
        return
    number, qualifier = split
    position = _parse_percentage(number)
    if position is None:
        return
    settings.position = position
    if qualifier:
        settings.position_align = qualifier


def _parse_size(settings, value):
    size = _parse_percentage(value)
    if size is not None:
        settings.size = size
        if size != 100:
            # Explicitly sized: the cue drops out of the region named before it
            settings.region = None


def _parse_align(settings, value):
    if value in ALIGN_SETTING_MAP:
        settings.align = value


_SETTING_PARSERS = {
    "vertical": _parse_vertical,
    "line": _parse_line,
    "position": _parse_position,
    "size": _parse_size,
    "align": _parse_align,
}
"""Parsers by setting name; each sets its fields only if the value is valid.
region is read by CueSettings.parse, which knows the region ids."""
