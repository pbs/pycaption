import unittest

from pycaption.geometry import Size, Point, Stretch, Padding, UnitEnum, Layout

class IsValidGeometryObjectTestCase(unittest.TestCase):

    def test_size_is_valid(self):
        with self.assertRaises(TypeError):
            Size()

        with self.assertRaises(ValueError):
            Size(None, None)

    def test_point_is_valid(self):
        with self.assertRaises(TypeError):
            Point()

        with self.assertRaises(ValueError):
            Point(None, None)

    def test_stretch_is_valid(self):
        with self.assertRaises(TypeError):
            Stretch()

        with self.assertRaises(ValueError):
            Stretch(None, None)

class IsRelativeTestCase(unittest.TestCase):

    def test_size_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_percent = Size(30, UnitEnum.PERCENT)

        self.assertFalse(size_px.is_relative())
        self.assertTrue(size_percent.is_relative())

    def test_point_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)

        point_abs = Point(size_px, size_px2)
        point_mix = Point(size_percent, size_px)
        point_rel = Point(size_percent, size_percent2)

        self.assertFalse(point_abs.is_relative())
        self.assertFalse(point_mix.is_relative())
        self.assertTrue(point_rel.is_relative())

    def test_stretch_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)

        stretch_abs = Stretch(size_px, size_px2)
        stretch_mix = Stretch(size_percent, size_px)
        stretch_rel = Stretch(size_percent, size_percent2)

        self.assertFalse(stretch_abs.is_relative())
        self.assertFalse(stretch_mix.is_relative())
        self.assertTrue(stretch_rel.is_relative())

    def test_padding_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)
        size_px3 = Size(30, UnitEnum.PIXEL)
        size_px4 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)
        size_percent3 = Size(30, UnitEnum.PERCENT)
        size_percent4 = Size(30, UnitEnum.PERCENT)

        padding_abs = Padding(size_px, size_px2, size_px3, size_px4)
        padding_mix = Padding(size_px, size_px2, size_px3, size_percent)
        padding_rel = Padding(
            size_percent, size_percent2, size_percent3, size_percent4)

        self.assertFalse(padding_abs.is_relative())
        self.assertFalse(padding_mix.is_relative())
        self.assertTrue(padding_rel.is_relative())

    def test_layout_is_relative(self):
        empty_layout = Layout()

        self.assertTrue(empty_layout.is_relative())

        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)

        point_abs = Point(size_px, size_px2)
        point_rel = Point(size_percent, size_percent2)

        stretch_abs = Stretch(size_px, size_px2)
        stretch_rel = Stretch(size_percent, size_percent2)

        layout_abs = Layout(
            origin=point_abs,
            extent=stretch_abs,
            padding=None
        )

        layout_mix = Layout(
            origin=point_abs,
            extent=stretch_rel,
            padding=None
        )

        layout_rel = Layout(
            origin=point_rel,
            extent=stretch_rel,
            padding=None
        )

        self.assertFalse(layout_abs.is_relative())
        self.assertFalse(layout_mix.is_relative())
        self.assertTrue(layout_rel.is_relative())
