from .exceptions import RelativizationError

class Enum(object):
    """Generic class that's not easily instantiable, serving as a base for
    the enumeration classes
    """
    def __new__(cls, *args, **kwargs):
        raise Exception(u"Don't instantiate. Use like an enum")

    __init__ = __new__


class UnitEnum(Enum):
    """Enumeration-like object, specifying the units of measure for length

    Usage:
        unit = UnitEnum.PIXEL
        unit = UnitEnum.EM
        if unit == UnitEnum.CELL :
            ...
    """
    PIXEL = u'px'
    EM = u'em'
    PERCENT = u'%'
    CELL = u'c'
    PT = u'pt'


class VerticalAlignmentEnum(Enum):
    """Enumeration object, specifying the allowed vertical alignment options

    Usage:
        alignment = VerticalAlignmentEnum.TOP
        if alignment == VerticalAlignmentEnum.BOTTOM:
            ...
    """
    TOP = u'top'
    CENTER = u'center'
    BOTTOM = u'bottom'


class HorizontalAlignmentEnum(Enum):
    """Enumeration object specifying the horizontal alignment preferences
    """
    LEFT = u'left'
    CENTER = u'center'
    RIGHT = u'right'
    START = u'start'
    END = u'end'


class Alignment(object):
    def __init__(self, horizontal, vertical):
        """
        :type horizontal: unicode
        :param horizontal: HorizontalAlignmentEnum member
        :type vertical: unicode
        :param vertical: VerticalAlignmentEnum member
        """
        self.horizontal = horizontal
        self.vertical = vertical

    def __hash__(self):
        return hash(
            hash(self.horizontal) * 83 +
            hash(self.vertical) * 89 +
            97
        )

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.horizontal == other.horizontal and
            self.vertical == other.vertical
        )

    def __repr__(self):
        return u"<Alignment ({horizontal} {vertical})>".format(
            horizontal=self.horizontal, vertical=self.vertical
        )

    def serialized(self):
        """Returns a tuple of the useful information regarding this object
        """
        return self.horizontal, self.vertical

    @classmethod
    def from_horizontal_and_vertical_align(cls, text_align=None,
                                           display_align=None):
        horizontal_obj = None
        vertical_obj = None

        if text_align == u'left':
            horizontal_obj = HorizontalAlignmentEnum.LEFT
        if text_align == u'start':
            horizontal_obj = HorizontalAlignmentEnum.START
        if text_align == u'center':
            horizontal_obj = HorizontalAlignmentEnum.CENTER
        if text_align == u'right':
            horizontal_obj = HorizontalAlignmentEnum.RIGHT
        if text_align == u'end':
            horizontal_obj = HorizontalAlignmentEnum.END

        if display_align == u'before':
            vertical_obj = VerticalAlignmentEnum.TOP
        if display_align == u'center':
            vertical_obj = VerticalAlignmentEnum.CENTER
        if display_align == u'after':
            vertical_obj = VerticalAlignmentEnum.BOTTOM

        if not any([horizontal_obj, vertical_obj]):
            return None
        return cls(horizontal_obj, vertical_obj)


class TwoDimensionalObject(object):
    """Adds a couple useful methods to its subclasses, nothing fancy.
    """
    @classmethod
    # TODO - highly cachable. Should use WeakValueDictionary here to return
    # flyweights, not new objects.
    def from_xml_attribute(cls, attribute):
        """Instantiate the class from a value of the type "4px" or "5%"
        or any number concatenated with a measuring unit (member of UnitEnum)

        :type attribute: unicode
        """
        horizontal, vertical = unicode(attribute).split(u' ')
        horizontal = Size.from_string(horizontal)
        vertical = Size.from_string(vertical)

        return cls(horizontal, vertical)


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
        self.horizontal = horizontal
        self.vertical = vertical

    def is_measured_in(self, measure_unit):
        """Whether the stretch is only measured in the provided units

        :param measure_unit: a UnitEnum member
        :return: True/False
        """
        return (
            self.horizontal.unit == measure_unit
            and self.vertical.unit == measure_unit
        )

    def __repr__(self):
        return u'<Stretch ({horizontal}, {vertical})>'.format(
            horizontal=self.horizontal, vertical=self.vertical
        )

    def serialized(self):
        """Returns a tuple of the useful attributes of this object"""
        return (
            None if not self.horizontal else self.horizontal.serialized(),
            None if not self.vertical else self.vertical.serialized()
        )

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.horizontal == other.horizontal and
            self.vertical == other.vertical
        )

    def __hash__(self):
        return hash(
            hash(self.horizontal) * 59 +
            hash(self.vertical) * 61 +
            67
        )

    def to_xml_attribute(self, **kwargs):
        """Returns a unicode representation of this object as an xml attribute
        """
        return u'{horizontal} {vertical}'.format(
            horizontal=self.horizontal.to_xml_attribute(),
            vertical=self.vertical.to_xml_attribute()
        )

    def to_percentage_of(self, video_width, video_height):
        """
        Converts absolute units (e.g. px, pt etc) to percentage
        """
        self.horizontal.to_percentage_of(video_width=video_width)
        self.vertical.to_percentage_of(video_height=video_height)


class Region(object):
    """Represents the spatial coordinates of a rectangle

    Don't instantiate by hand. use Region.from_points or Region.from_extent
    """
    @classmethod
    def from_points(cls, p1, p2):
        """Create a rectangle, knowing 2 points on the plane.
        We assume that p1 is in the upper left (closer to the origin)

        :param p1: Point instance
        :param p2: Point instance
        :return: a Point instance
        """
        inst = cls()
        inst._p1 = p1
        inst._p2 = p2
        return inst

    @classmethod
    def from_extent(cls, extent, origin):
        """Create a rectangle, knowing its upper left origin, and
        spatial extension

        :type extent: Stretch
        :type origin: Point
        :return: a Point instance
        """
        inst = cls()
        inst._extent = extent
        inst._origin = origin
        return inst

    @property
    def extent(self):
        """How wide this rectangle stretches (horizontally and vertically)
        """
        if hasattr(self, '_extent'):
            return self._extent
        else:
            return self._p1 - self._p2

    @property
    def origin(self):
        """Out of its 4 points, returns the one closest to the origin
        """
        if hasattr(self, '_origin'):
            return self._origin
        else:
            return Point.align_from_origin(self._p1, self._p2)[0]

    upper_left_point = origin

    @property
    def lower_right_point(self):
        """The point furthest from the origin from the rectangle's 4 points
        """
        if hasattr(self, '_p2'):
            return Point.align_from_origin(self._p1, self._p2)[1]
        else:
            return self.origin.add_extent(self.extent)

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.extent == other.extent and
            self.origin == other.origin
        )

    def __hash__(self):
        return hash(
            hash(self.origin) * 71 +
            hash(self.extent) * 73 +
            79
        )


class Point(TwoDimensionalObject):
    """Represent a point in 2d space.
    """
    def __init__(self, x, y):
        """
        :type x: Size
        :type y: Size
        """
        self.x = x
        self.y = y

    def __sub__(self, other):
        """Returns an Stretch object, if the other point's units are compatible
        """
        return Stretch(abs(self.x - other.x), abs(self.y - other.y))

    def add_stretch(self, stretch):
        """Returns another Point instance, whose coordinates are the sum of the
         current Point's, and the Stretch instance's.
        """
        return Point(self.x + stretch.horizontal, self.y + stretch.vertical)

    def to_percentage_of(self, video_width, video_height):
        """
        Converts absolute units (e.g. px, pt etc) to percentage
        """
        self.x.to_percentage_of(video_width=video_width)
        self.y.to_percentage_of(video_height=video_height)

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
            return (Point(min(p1.x, p2.x), min(p1.y, p2.y)),
                    Point(max(p1.x, p2.x), max(p1.y, p2.y)))

    def __repr__(self):
        return u'<Point ({x}, {y})>'.format(
            x=self.x, y=self.y
        )

    def serialized(self):
        """Returns the "useful" values of this object.
        """
        return (
            None if not self.x else self.x.serialized(),
            None if not self.y else self.y.serialized()
        )

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.x == other.x and
            self.y == other.y
        )

    def __hash__(self):
        return hash(
            hash(self.x) * 51 +
            hash(self.y) * 53 +
            57
        )

    def to_xml_attribute(self, **kwargs):
        """Returns a unicode representation of this object as an xml attribute
        """
        return u'{x} {y}'.format(
            x=self.x.to_xml_attribute(), y=self.y.to_xml_attribute())


class Size(object):
    """Ties together a number with a unit, to represent a size.

    Use as value objects! (don't change after creation)
    """
    def __init__(self, value, unit):
        """
        :param value: A number (float or int will do)
        :param unit: A UnitEnum member
        """
        self.value = value
        self.unit = unit

    def __sub__(self, other):
        if self.unit == other.unit:
            return Size(self.value - other.value, self.unit)
        else:
            raise ValueError(u"The sizes should have the same measure units.")

    def __abs__(self):
        return Size(abs(self.value), self.unit)

    def __cmp__(self, other):
        if self.unit == other.unit:
            return cmp(self.value, other.value)
        else:
            raise ValueError(u"The sizes should have the same measure units.")

    def __add__(self, other):
        if self.unit == other.unit:
            return Size(self.value + other.value, self.unit)
        else:
            raise ValueError(u"The sizes should have the same measure units.")

    def to_percentage_of(self, video_width=None, video_height=None):
        """
        :param video_width: An integer representing a width in pixels
        :param video_height: An integer representing a height in pixels
        """
        if self.unit == UnitEnum.PERCENT:
            return  # Nothing to do here

        # The input must be valid so that any conversion can be done
        if not (video_width or video_height):
            raise RelativizationError(
                u"Either video width or height must be given as a reference")
        elif video_width and video_height:
            raise RelativizationError(
                u"Only video width or height can be given as reference")

        if self.unit == UnitEnum.EM:
            # TODO: Implement proper conversion of em in function of font-size
            # The em unit is relative to the font-size, to which we currently
            # have no access. As a workaround, we presume the font-size is 16px,
            # which is a common default value but not guaranteed.
            self.value *= 16
            self.unit = UnitEnum.PIXEL

        if self.unit == UnitEnum.PT:
            # XXX: we will convert first to "px" and from "px" this will be
            # converted to percent. we don't take into consideration the
            # font-size
            self.value = self.value / 72.0 * 96.0
            self.unit = UnitEnum.PIXEL

        if self.unit == UnitEnum.PIXEL:
            self.value = self.value * 100 / (video_width or video_height)
            self.unit = UnitEnum.PERCENT

        if self.unit == UnitEnum.CELL:
            # TODO: Implement proper cell resolution
            # (w3.org/TR/ttaf1-dfxp/#parameter-attribute-cellResolution)
            # For now we will use the default values (32 columns and 15 rows)
            cell_reference = 32 if video_width else 15
            self.value = self.value * 100 / cell_reference
            self.unit = UnitEnum.PERCENT
        return self

    @classmethod
    # TODO - this also looks highly cachable. Should use a WeakValueDict here
    # to return flyweights
    def from_string(cls, string):
        """Given a string of the form "46px" or "5%" etc., returns the proper
        size object

        :param string: a number concatenated to any of the UnitEnum members.
        :type string: unicode
        :rtype: Size
        """
        units = [UnitEnum.CELL, UnitEnum.PERCENT, UnitEnum.PIXEL,
                 UnitEnum.EM, UnitEnum.PT]

        raw_number = string
        for unit in units:
            if raw_number.endswith(unit):
                raw_number = raw_number.rstrip(unit)
                break
        else:
            unit = None

        if unit is not None:
            value = None
            try:
                value = float(raw_number)
                value = int(raw_number)
            except ValueError:
                pass

            if value is None:
                raise ValueError(
                    u"""Couldn't recognize the value "{value}" as a number"""
                    .format(value=raw_number)
                )
            instance = cls(value, unit)
            return instance
        else:
            raise ValueError(
                u"The specified value is not valid because its unit "
                u"is not recognized: {value}. "
                u"The only supported units are: {supported}"
                .format(value=raw_number, supported=u', '.join(units))
            )

    def __repr__(self):
        return u'<Size ({value} {unit})>'.format(
            value=self.value, unit=self.unit
        )

    def __unicode__(self):
        return u"{}{}".format(self.value, self.unit)

    def to_xml_attribute(self, **kwargs):
        """Returns a unicode representation of this object, as an xml attribute
        """
        return unicode(self)

    def serialized(self):
        """Returns the "useful" values of this object"""
        return self.value, self.unit

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.value == other.value and
            self.unit == other.unit
        )

    def __hash__(self):
        return hash(
            hash(self.value) * 41 +
            hash(self.unit) * 43 +
            47
        )


class Padding(object):
    """Represents padding information. Consists of 4 Size objects, representing
    padding from (in this order): before (up), after (down), start (left) and
    end (right).
    """
    def __init__(self, before=None, after=None, start=None, end=None):
        """
        :type before: Size
        :type after: Size
        :type start: Size
        :type end: Size
        """
        self.before = before
        self.after = after
        self.start = start
        self.end = end

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
        values_list = unicode(attribute).split(u' ')
        sizes = []

        for value in values_list:
            sizes.append(Size.from_string(value))

        if len(sizes) == 1:
            return cls(sizes[0], sizes[0], sizes[0], sizes[0])
        elif len(sizes) == 2:
            return cls(sizes[0], sizes[0], sizes[1], sizes[1])
        elif len(sizes) == 3:
            return cls(sizes[0], sizes[2], sizes[1], sizes[1])
        elif len(sizes) == 4:
            return cls(sizes[0], sizes[2], sizes[3], sizes[1])
        else:
            raise ValueError(u'The provided value "{value}" could not be '
                             u"parsed into the a padding. Check out "
                             u"http://www.w3.org/TR/ttaf1-dfxp/"
                             u"#style-attribute-padding for the definition "
                             u"and examples".format(value=attribute))

    def __repr__(self):
        return (
            u"<Padding (before: {before}, after: {after}, start: {start}, "
            u"end: {end})>".format(
                before=self.before, after=self.after, start=self.start,
                end=self.end
            )
        )

    def serialized(self):
        """Returns a tuple containing the useful values of this object
        """
        return (
            None if not self.before else self.before.serialized(),
            None if not self.after else self.after.serialized(),
            None if not self.start else self.start.serialized(),
            None if not self.end else self.end.serialized()
        )

    def __eq__(self, other):
        return (
            other and
            type(self) == type(other) and
            self.before == other.before and
            self.after == other.after and
            self.start == other.start and
            self.end == other.end
        )

    def __hash__(self):
        return hash(
            hash(self.before) * 19 +
            hash(self.after) * 23 +
            hash(self.start) * 29 +
            hash(self.end) * 31 +
            37
        )

    def to_xml_attribute(
            self, attribute_order=(u'before', u'end', u'after', u'start'),
            **kwargs):
        """Returns a unicode representation of this object as an xml attribute

        TODO - should extend the attribute_order tuple to contain 4 tuples,
        so we can reduce the output length to 3, 2 or 1 element.

        :type attribute_order: tuple
        :param attribute_order: the order that the attributes should be
            serialized
        """
        try:
            string_list = []
            for attrib in attribute_order:
                if hasattr(self, attrib):
                    string_list.append(
                        getattr(self, attrib).to_xml_attribute())
        except AttributeError:
            raise ValueError(u"The attribute order specified is invalid.")

        return u' '.join(string_list)

    def to_percentage_of(self, video_width, video_height):
        if self.before:
            self.before.to_percentage_of(video_height=video_height)
        if self.after:
            self.after.to_percentage_of(video_height=video_height)
        if self.start:
            self.start.to_percentage_of(video_width=video_width)
        if self.end:
            self.end.to_percentage_of(video_width=video_width)


class Layout(object):
    """Should encapsulate all the information needed to determine (as correctly
    as possible) the layout (positioning) of elements on the screen.

     Inheritance of this property, from the CaptionSet to its children is
     specific for each caption type.
    """
    def __init__(self, origin=None, extent=None, padding=None, alignment=None,
                 webvtt_positioning=None):
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

        :type webvtt_positioning: unicode
        :param webvtt_positioning: A string with the raw WebVTT cue settings.
            This is used so that WebVTT positioning isn't lost on conversion
            from WebVTT to WebVTT. It is needed only because pycaption
            currently doesn't support reading positioning from WebVTT.
        """

        self.webvtt_positioning = webvtt_positioning
        self.origin = origin
        self.extent = extent
        self.padding = padding
        self.alignment = alignment

    def __nonzero__(self):
        attributes = [self.origin, self.extent, self.padding, self.alignment]
        return any(attributes)

    def __repr__(self):
        return (
            u"<Layout (origin: {origin}, extent: {extent}, "
            u"padding: {padding}, alignment: {alignment})>".format(
                origin=self.origin, extent=self.extent, padding=self.padding,
                alignment=self.alignment
            )
        )

    def serialized(self):
        """Returns nested tuple containing the "useful" values of this object
        """
        return (
            None if not self.origin else self.origin.serialized(),
            None if not self.extent else self.extent.serialized(),
            None if not self.padding else self.padding.serialized(),
            None if not self.alignment else self.alignment.serialized()
        )

    def __eq__(self, other):
        return (
            type(self) == type(other) and
            self.origin == other.origin and
            self.extent == other.extent and
            self.padding == other.padding and
            self.alignment == other.alignment
        )

    def __hash__(self):
        return hash(
            hash(self.origin) * 7
            + hash(self.extent) * 11
            + hash(self.padding) * 13
            + hash(self.alignment) * 5
            + 17
        )

    def to_percentage_of(self, video_width, video_height):
        for attr in [self.origin, self.extent, self.padding]:
            if attr:
                attr.to_percentage_of(video_width, video_height)
