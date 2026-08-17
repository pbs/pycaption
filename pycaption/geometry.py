"""
This module implements the classes used to represent positioning information.

CONVENTIONS:
* None of the methods should modify the state of the objects on which they're
  called. If the values of an object need to be recalculated, the method
  responsible for the recalculation should return a new object with the
  necessary modifications.
"""
import re
from enum import Enum
from functools import total_ordering

from .exceptions import CaptionReadSyntaxError, RelativizationError

_UNIT_MISMATCH_MSG = "The sizes should have the same measure units."


class UnitEnum(Enum):
    """Enumeration-like object, specifying the units of measure for length

    Usage:
        unit = UnitEnum.PIXEL
        unit = UnitEnum.EM
        if unit == UnitEnum.CELL :
            ...
    """

    PIXEL = "px"
    EM = "em"
    PERCENT = "%"
    CELL = "c"
    PT = "pt"
    VW = "vw"
    VH = "vh"


class VerticalAlignmentEnum(Enum):
    """Enumeration object, specifying the allowed vertical alignment options

    Usage:
        alignment = VerticalAlignmentEnum.TOP
        if alignment == VerticalAlignmentEnum.BOTTOM:
            ...
    """

    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"


class HorizontalAlignmentEnum(Enum):
    """Enumeration object specifying the horizontal alignment preferences"""

    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"
    START = "start"
    END = "end"


class PositionAlignmentEnum(Enum):
    """WebVTT position alignment: which edge of the cue box the position
    percentage anchors to."""

    LINE_LEFT = "line-left"
    CENTER = "center"
    LINE_RIGHT = "line-right"


class LineAlignmentEnum(Enum):
    """WebVTT line alignment: how the cue box is positioned relative to
    the line setting value (start, center, or end of the cue box)."""

    START = "start"
    CENTER = "center"
    END = "end"


class WritingDirectionEnum(Enum):
    """Specifies WebVTT writing direction (vertical cue setting)."""

    HORIZONTAL = ""
    VERTICAL_RL = "rl"
    VERTICAL_LR = "lr"


class Alignment:
    """Represents horizontal and vertical text alignment within a region."""

    _TEXT_ALIGN_MAP = {
        "left": HorizontalAlignmentEnum.LEFT,
        "start": HorizontalAlignmentEnum.START,
        "center": HorizontalAlignmentEnum.CENTER,
        "right": HorizontalAlignmentEnum.RIGHT,
        "end": HorizontalAlignmentEnum.END,
    }
    _DISPLAY_ALIGN_MAP = {
        "before": VerticalAlignmentEnum.TOP,
        "center": VerticalAlignmentEnum.CENTER,
        "after": VerticalAlignmentEnum.BOTTOM,
    }

    def __init__(self, horizontal=None, vertical=None):
        """
        :type horizontal: HorizontalAlignmentEnum | None
        :param horizontal: HorizontalAlignmentEnum member, or None
        :type vertical: VerticalAlignmentEnum | None
        :param vertical: VerticalAlignmentEnum member, or None
        """
        self.horizontal = horizontal
        self.vertical = vertical

    def __hash__(self):
        return hash(hash(self.horizontal) * 83 + hash(self.vertical) * 89 + 97)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Alignment):
            return NotImplemented
        return self.horizontal == other.horizontal and self.vertical == other.vertical

    def __repr__(self):
        h = self.horizontal.value if self.horizontal else "None"
        v = self.vertical.value if self.vertical else "None"
        return f"<Alignment ({h} {v})>"

    def serialized(self):
        """Returns a tuple of the useful information regarding this object"""
        return self.horizontal, self.vertical

    @classmethod
    def from_horizontal_and_vertical_align(cls, text_align=None, display_align=None):
        """Create an Alignment from DFXP-style textAlign/displayAlign strings.

        :param text_align: One of 'left', 'start', 'center', 'right', 'end'.
        :param display_align: One of 'before', 'center', 'after'.
        :returns: Alignment instance, or None if both params are None.
        :rtype: Alignment | None
        """
        horizontal_obj = cls._TEXT_ALIGN_MAP.get(text_align)
        vertical_obj = cls._DISPLAY_ALIGN_MAP.get(display_align)

        if not horizontal_obj and not vertical_obj:
            return None
        return Alignment(horizontal_obj, vertical_obj)


class TwoDimensionalObject:
    """Adds a couple useful methods to its subclasses, nothing fancy."""

    def __init__(self, first, second):
        raise NotImplementedError

    @classmethod
    def from_xml_attribute(cls, attribute):
        """Instantiate the class from a value of the type "4px" or "5%"
        or any number concatenated with a measuring unit (member of UnitEnum)

        :type attribute: str
        """
        first, second = attribute.split(" ")
        first = Size.from_string(first)
        second = Size.from_string(second)

        return cls(first, second)


class Stretch(TwoDimensionalObject):
    """Used for specifying the extent of a rectangle (how much it stretches),
    or the padding in a rectangle (how much space should be left empty until
    text can be displayed)
    """

    def __init__(self, horizontal, vertical):
        """Use the .from_xxx methods. They know what's best for you.

        :type horizontal: Size
        :type vertical: Size
        """
        if not isinstance(horizontal, Size) or not isinstance(vertical, Size):
            raise ValueError("Stretch must be initialized with two valid Size objects.")
        self.horizontal = horizontal
        self.vertical = vertical

    def is_measured_in(self, measure_unit):
        """Whether the stretch is only measured in the provided units

        :param measure_unit: a UnitEnum member
        :return: True/False
        """
        return (
            self.horizontal.unit == measure_unit and self.vertical.unit == measure_unit
        )

    def __repr__(self):
        return f"<Stretch ({self.horizontal}, {self.vertical})>"

    def serialized(self):
        """Returns a tuple of the useful attributes of this object"""
        return (
            None if not self.horizontal else self.horizontal.serialized(),
            None if not self.vertical else self.vertical.serialized(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Stretch):
            return NotImplemented
        return self.horizontal == other.horizontal and self.vertical == other.vertical

    def __hash__(self):
        return hash(hash(self.horizontal) * 59 + hash(self.vertical) * 61 + 67)

    def __bool__(self):
        return bool(self.horizontal or self.vertical)

    def to_xml_attribute(self, **kwargs):
        """Returns a string representation of this object as an xml attribute"""
        h = self.horizontal.to_xml_attribute()
        v = self.vertical.to_xml_attribute()
        return f"{h} {v}"

    def is_relative(self):
        """Return True if all dimensions are expressed as percentages."""
        return (not self.horizontal or self.horizontal.is_relative()) and (
            not self.vertical or self.vertical.is_relative()
        )

    def as_percentage_of(self, video_width, video_height):
        """
        Converts absolute units (e.g. px, pt etc) to percentage
        """
        return Stretch(
            self.horizontal.as_percentage_of(video_width=video_width),
            self.vertical.as_percentage_of(video_height=video_height),
        )


class Point(TwoDimensionalObject):
    """Represent a point in 2d space."""

    def __init__(self, x, y):
        """
        :type x: Size
        :type y: Size
        """
        if not isinstance(x, Size) or not isinstance(y, Size):
            raise ValueError("Point must be initialized with two valid Size objects.")
        self.x = x
        self.y = y

    def __sub__(self, other):
        """Returns an Stretch object, if the other point's units are compatible"""
        return Stretch(abs(self.x - other.x), abs(self.y - other.y))

    def add_stretch(self, stretch):
        """Returns another Point instance, whose coordinates are the sum of the
        current Point's, and the Stretch instance's.
        """
        return Point(self.x + stretch.horizontal, self.y + stretch.vertical)

    def is_relative(self):
        """Return True if all dimensions are expressed as percentages."""
        return (not self.x or self.x.is_relative()) and (
            not self.y or self.y.is_relative()
        )

    def as_percentage_of(self, video_width, video_height):
        """
        Converts absolute units (e.g. px, pt etc) to percentage
        """
        return Point(
            self.x.as_percentage_of(video_width=video_width),
            self.y.as_percentage_of(video_height=video_height),
        )

    @classmethod
    def align_from_origin(cls, p1, p2):
        """Returns a tuple of 2 points. The first is closest to the origin
        on both axes than the second.

        If the 2 points fulfill this condition, returns them (ordered), if not,
        creates 2 new points.
        """
        if p1.x <= p2.x and p1.y <= p2.y:
            return p1
        if p1.x >= p2.x and p1.y >= p2.y:
            return p2
        else:
            return (
                Point(min(p1.x, p2.x), min(p1.y, p2.y)),
                Point(max(p1.x, p2.x), max(p1.y, p2.y)),
            )

    def __repr__(self):
        return f"<Point ({self.x}, {self.y})>"

    def serialized(self):
        """Returns the "useful" values of this object."""
        return (
            None if not self.x else self.x.serialized(),
            None if not self.y else self.y.serialized(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Point):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash(hash(self.x) * 51 + hash(self.y) * 53 + 57)

    def __bool__(self):
        return bool(self.x or self.y)

    def to_xml_attribute(self, **kwargs):
        """Returns a string representation of this object as an xml attribute"""
        return f"{self.x.to_xml_attribute()} {self.y.to_xml_attribute()}"


@total_ordering
class Size:
    """Ties together a number with a unit, to represent a size.

    Use as value objects! (don't change after creation)
    """

    def __init__(self, value, unit):
        """
        :param value: A number (float or int will do)
        :param unit: A UnitEnum member
        """
        if value is None:
            raise ValueError("Size must be initialized with a value.")
        if not isinstance(unit, UnitEnum):
            raise ValueError("Size must be initialized with a valid unit.")

        self.value = float(value)
        self.unit = unit

    def __sub__(self, other):
        if self.unit == other.unit:
            return Size(self.value - other.value, self.unit)
        else:
            raise ValueError(_UNIT_MISMATCH_MSG)

    def __abs__(self):
        return Size(abs(self.value), self.unit)

    def __lt__(self, other):
        if not isinstance(other, Size):
            return NotImplemented
        if self.unit != other.unit:
            raise ValueError(_UNIT_MISMATCH_MSG)
        return self.value < other.value

    def __add__(self, other):
        if self.unit == other.unit:
            return Size(self.value + other.value, self.unit)
        else:
            raise ValueError(_UNIT_MISMATCH_MSG)

    def is_relative(self):
        """
        Returns True if value is expressed as percentage, False otherwise.
        """
        return self.unit == UnitEnum.PERCENT

    def as_percentage_of(self, video_width=None, video_height=None):
        """
        :param video_width: An integer representing a width in pixels
        :param video_height: An integer representing a height in pixels
        """
        value = self.value
        unit = self.unit

        if unit == UnitEnum.PERCENT:
            return self  # Nothing to do here

        if unit in (UnitEnum.VW, UnitEnum.VH):
            return Size(value, UnitEnum.PERCENT)

        # The input must be valid so that any conversion can be done
        if not (video_width or video_height):
            raise RelativizationError(
                "At least one of video width or height must be given as a reference"
            )
        elif video_width and video_height:
            raise RelativizationError(
                "Only one of video width or height can be given as reference"
                " per value being converted"
            )

        if unit == UnitEnum.EM:
            # Assumes 16px font-size (common default); actual font-size is
            # not available at this layer.
            value *= 16
            unit = UnitEnum.PIXEL

        if unit == UnitEnum.PT:
            value = value / 72.0 * 96.0
            unit = UnitEnum.PIXEL

        if unit == UnitEnum.PIXEL:
            value = value * 100.0 / (video_width or video_height)
            unit = UnitEnum.PERCENT

        if unit == UnitEnum.CELL:
            # TTML default cell resolution (32 cols x 15 rows) per DFXP spec;
            # custom ttp:cellResolution is not currently parsed.
            cell_reference = 32 if video_width else 15
            value = value * 100.0 / cell_reference
            unit = UnitEnum.PERCENT

        return Size(value, unit)

    @classmethod
    def from_string(cls, string):
        """Given a string of the form "46px" or "5%" etc., returns the proper
        size object

        :param string: a number concatenated to any of the UnitEnum members.
        :type string: str
        :rtype: Size
        """
        size_pattern = re.compile(
            r"^(((?P<value>-?\d+(\.\d+)?)(?P<unit>"
            rf"{'|'.join([unit.value for unit in UnitEnum])}))|0)$"
        )
        match = size_pattern.search(string)
        if not match:
            raise CaptionReadSyntaxError(
                f"Invalid size: {string}. Please make sure the provided value "
                "is a number followed by one of the supported units: "
                f"{', '.join([unit.value for unit in UnitEnum])}."
            )
        unit = match.group("unit")
        if unit:
            value = match.group("value")
            return cls(value, UnitEnum(unit))
        else:
            return cls(match.group(0), UnitEnum.PIXEL)

    def __repr__(self):
        return f"<Size ({self.value} {self.unit.value})>"

    def __str__(self):
        value = round(self.value, 2)
        if value.is_integer():
            s = f"{int(value)}"
        else:
            s = f"{value:.2f}".rstrip("0").rstrip(".")
        return f"{s}{self.unit.value}"

    def to_xml_attribute(self, **kwargs):
        """Returns a string representation of this object, as an xml attribute"""
        return str(self)

    def serialized(self):
        """Returns the "useful" values of this object"""
        return self.value, self.unit

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Size):
            return NotImplemented
        return self.value == other.value and self.unit == other.unit

    def __hash__(self):
        return hash(hash(self.value) * 41 + hash(self.unit) * 43 + 47)


class Padding:
    """Represents padding information. Consists of 4 Size objects, representing
    padding from (in this order): before (up), after (down), start (left) and
    end (right).

    A valid Padding object must always have all paddings set and different from
    None. If this is not true Writers may fail for they rely on this assumption.
    """

    def __init__(self, before=None, after=None, start=None, end=None):
        """
        :type before: Size
        :type after: Size
        :type start: Size
        :type end: Size
        """
        default = Size(0, UnitEnum.PERCENT)
        self.before = before if isinstance(before, Size) else default
        self.after = after if isinstance(after, Size) else default
        self.start = start if isinstance(start, Size) else default
        self.end = end if isinstance(end, Size) else default

    @classmethod
    def from_xml_attribute(cls, attribute):
        """As per the docs, the style attribute can contain 1,2,3 or 4 values.

        If 1 value: apply to all edges
        If 2: first applies to before and after, second to start and end
        If 3: first applies to before, second to start and end, third to after
        If 4: before, end, after, start;

        http://www.w3.org/TR/ttaf1-dfxp/#style-attribute-padding

        :param attribute: a string like object, representing a dfxp attr. value
        :return: a Padding object
        """
        sizes = [Size.from_string(v) for v in attribute.split(" ")]

        if len(sizes) == 1:
            return cls(sizes[0], sizes[0], sizes[0], sizes[0])
        elif len(sizes) == 2:
            return cls(sizes[0], sizes[0], sizes[1], sizes[1])
        elif len(sizes) == 3:
            return cls(sizes[0], sizes[2], sizes[1], sizes[1])
        elif len(sizes) == 4:
            return cls(sizes[0], sizes[2], sizes[3], sizes[1])
        else:
            raise ValueError(
                f'The provided value "{attribute}" could not be '
                "parsed into the a padding. Check out "
                "http://www.w3.org/TR/ttaf1-dfxp/"
                "#style-attribute-padding for the definition "
                "and examples"
            )

    def __repr__(self):
        return (
            f"<Padding (before: {self.before}, after: {self.after}, "
            f"start: {self.start}, end: {self.end})>"
        )

    def serialized(self):
        """Returns a tuple containing the useful values of this object"""
        return (
            None if not self.before else self.before.serialized(),
            None if not self.after else self.after.serialized(),
            None if not self.start else self.start.serialized(),
            None if not self.end else self.end.serialized(),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Padding):
            return NotImplemented
        return (
            self.before == other.before
            and self.after == other.after
            and self.start == other.start
            and self.end == other.end
        )

    def __hash__(self):
        return hash(
            hash(self.before) * 19
            + hash(self.after) * 23
            + hash(self.start) * 29
            + hash(self.end) * 31
            + 37
        )

    def to_xml_attribute(
        self, attribute_order=("before", "end", "after", "start"), **kwargs
    ):
        """Returns a string representation of this object as an xml attribute.

        :type attribute_order: tuple
        :param attribute_order: the order that the attributes should be
            serialized
        """
        try:
            string_list = []
            for attrib in attribute_order:
                if hasattr(self, attrib):
                    string_list.append(getattr(self, attrib).to_xml_attribute())
        except AttributeError:
            # A Padding object with attributes set to None is considered
            # invalid. All four possible paddings must be set. If one of them
            # is not, this error is raised.
            raise ValueError("The attribute order specified is invalid.")

        return " ".join(string_list)

    def as_percentage_of(self, video_width, video_height):
        """Convert all padding sizes to percentages of video dimensions.

        :param video_width: Video width in pixels.
        :param video_height: Video height in pixels.
        :rtype: Padding
        """
        return Padding(
            self.before.as_percentage_of(video_height=video_height),
            self.after.as_percentage_of(video_height=video_height),
            self.start.as_percentage_of(video_width=video_width),
            self.end.as_percentage_of(video_width=video_width),
        )

    def is_relative(self):
        """Return True if all padding values are expressed as percentages."""
        return all(
            not size or size.is_relative()
            for size in (self.before, self.after, self.start, self.end)
        )


class Layout:
    """Should encapsulate all the information needed to determine (as correctly
    as possible) the layout (positioning) of elements on the screen.

     Inheritance of this property, from the CaptionSet to its children is
     specific for each caption type.
    """

    def __init__(
        self,
        origin=None,
        extent=None,
        padding=None,
        alignment=None,
        webvtt_positioning=None,
        writing_direction=None,
        position_alignment=None,
        line_alignment=None,
        inherit_from=None,
    ):
        """
        :type origin: Point
        :param origin: The point on the screen which is the top left vertex
            of a rectangular region where the captions should be placed

        :type extent: Stretch
        :param extent: The width and height of the rectangle where the caption
            should be placed on the screen.

        :type padding: Padding
        :param padding: The padding of the text inside the region described
            by the origin and the extent

        :type alignment: Alignment

        :type webvtt_positioning: str
        :param webvtt_positioning: A string with the raw WebVTT cue settings.
            This is used so that WebVTT positioning isn't lost on conversion
            from WebVTT to WebVTT.

        :type writing_direction: WritingDirectionEnum
        :param writing_direction: WebVTT vertical writing direction (rl or lr).

        :type position_alignment: PositionAlignmentEnum
        :param position_alignment: Which edge of the cue box the position
            percentage anchors to (line-left, center, or line-right).

        :type line_alignment: LineAlignmentEnum
        :param line_alignment: How the cue box is vertically aligned relative
            to the line position (start, center, or end).

        :type inherit_from: Layout
        :param inherit_from: A Layout with the positioning parameters to be
            used if not specified by the positioning arguments,
        """

        self.origin = origin
        self.extent = extent
        self.padding = padding
        self.alignment = alignment
        self.webvtt_positioning = webvtt_positioning
        self.writing_direction = writing_direction
        self.position_alignment = position_alignment
        self.line_alignment = line_alignment

        if inherit_from:
            for attr_name in [
                "origin",
                "extent",
                "padding",
                "alignment",
                "writing_direction",
                "position_alignment",
                "line_alignment",
            ]:
                attr = getattr(self, attr_name)
                if not attr:
                    setattr(self, attr_name, getattr(inherit_from, attr_name))

    def __bool__(self):
        return any(
            (
                self.origin,
                self.extent,
                self.padding,
                self.alignment,
                self.webvtt_positioning,
                self.writing_direction,
                self.position_alignment,
                self.line_alignment,
            )
        )

    def __repr__(self):
        return (
            f"<Layout (origin: {self.origin}, extent: {self.extent}, "
            f"padding: {self.padding}, alignment: {self.alignment})>"
        )

    def serialized(self):
        """Returns nested tuple containing the "useful" values of this object"""
        return (
            None if not self.origin else self.origin.serialized(),
            None if not self.extent else self.extent.serialized(),
            None if not self.padding else self.padding.serialized(),
            None if not self.alignment else self.alignment.serialized(),
            self.writing_direction,
            self.position_alignment,
            self.line_alignment,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Layout):
            return NotImplemented
        return (
            self.origin == other.origin
            and self.extent == other.extent
            and self.padding == other.padding
            and self.alignment == other.alignment
            and self.writing_direction == other.writing_direction
            and self.position_alignment == other.position_alignment
            and self.line_alignment == other.line_alignment
        )

    def __hash__(self):
        return hash(
            hash(self.origin) * 7
            + hash(self.extent) * 11
            + hash(self.padding) * 13
            + hash(self.alignment) * 5
            + hash(self.writing_direction) * 19
            + hash(self.position_alignment) * 23
            + hash(self.line_alignment) * 29
            + 17
        )

    def is_relative(self):
        """Return True if all positioning values are expressed as percentages."""
        return all(
            not attr or attr.is_relative()
            for attr in (self.origin, self.extent, self.padding)
        )

    def as_percentage_of(self, video_width, video_height):
        """Convert absolute positioning values to percentages.

        :param video_width: Video width in pixels.
        :param video_height: Video height in pixels.
        :rtype: Layout
        """
        params = {
            "alignment": self.alignment,
            "writing_direction": self.writing_direction,
            "position_alignment": self.position_alignment,
            "line_alignment": self.line_alignment,
        }
        for attr_name in ["origin", "extent", "padding"]:
            attr = getattr(self, attr_name)
            if attr:
                params[attr_name] = attr.as_percentage_of(video_width, video_height)
        return Layout(**params)

    def fit_to_screen(self):
        """
        If extent is not set or if origin + extent > 90%, (re)calculate it
        based on origin. It is a pycaption fix for caption files that are
        technically valid but contain inconsistent settings that may cause
        long captions to be cut out of the screen.

        When position_alignment is set, the origin is first adjusted so that
        origin.x represents the true left edge of the cue box (the W3C spec
        allows the position to anchor to center or right edge).

        ATTENTION: This must be called on relativized objects (such as the one
        returned by as_percentage_of). All units are presumed to be percentages.
        """
        if not self.origin:
            return self

        if (
            self.origin.x.unit != UnitEnum.PERCENT
            or self.origin.y.unit != UnitEnum.PERCENT
        ):
            return self

        origin = self._resolve_position_alignment()

        if origin.x.value >= 90 or origin.y.value >= 95:
            return self

        diff_horizontal = Size(90 - origin.x.value, UnitEnum.PERCENT)
        diff_vertical = Size(95 - origin.y.value, UnitEnum.PERCENT)

        if not self.extent:
            new_extent = Stretch(diff_horizontal, diff_vertical)
        else:
            new_extent = self._corrected_extent_from(
                origin, diff_horizontal, diff_vertical
            )

        return Layout(
            origin=origin,
            extent=new_extent,
            padding=self.padding,
            alignment=self.alignment,
            writing_direction=self.writing_direction,
            line_alignment=self.line_alignment,
        )

    def _resolve_position_alignment(self):
        """Adjust origin.x based on position_alignment and extent width.

        The VTT reader always stores the ``position`` setting in origin.x
        and ``size`` in extent.horizontal, regardless of writing direction.
        This method adjusts origin.x so it represents the true left edge
        of the cue box.

        Returns a new Point (or self.origin unchanged for LINE_LEFT/None).
        """
        if not self.position_alignment or not self.extent:
            return self.origin

        width = self.extent.horizontal.value

        if self.position_alignment == PositionAlignmentEnum.CENTER:
            adjusted_x = max(0, self.origin.x.value - width / 2)
        elif self.position_alignment == PositionAlignmentEnum.LINE_RIGHT:
            adjusted_x = max(0, self.origin.x.value - width)
        else:
            return self.origin

        return Point(Size(adjusted_x, UnitEnum.PERCENT), self.origin.y)

    def _corrected_extent_from(self, origin, diff_horizontal, diff_vertical):
        """Return extent clamped so origin + extent doesn't exceed the screen."""
        bottom_right = origin.add_stretch(self.extent)

        if (
            bottom_right.x.unit != UnitEnum.PERCENT
            or bottom_right.y.unit != UnitEnum.PERCENT
        ):
            raise ValueError(
                "Units must be relativized before extent "
                "can be calculated based on origin."
            )

        new_horizontal = self.extent.horizontal
        new_vertical = self.extent.vertical
        if bottom_right.x.value > 90:
            new_horizontal = diff_horizontal
        if bottom_right.y.value > 95:
            new_vertical = diff_vertical

        return Stretch(new_horizontal, new_vertical)
