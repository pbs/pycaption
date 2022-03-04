import pytest

from pycaption import CaptionReadSyntaxError
from pycaption.geometry import Size, Point, Stretch, Padding, UnitEnum, Layout


class TestIsValidGeometryObject:
    def test_size_is_valid(self):
        with pytest.raises(TypeError):
            Size()

        with pytest.raises(ValueError):
            Size(None, None)

    def test_point_is_valid(self):
        with pytest.raises(TypeError):
            Point()

        with pytest.raises(ValueError):
            Point(None, None)

    def test_stretch_is_valid(self):
        with pytest.raises(TypeError):
            Stretch()

        with pytest.raises(ValueError):
            Stretch(None, None)


class TestIsRelative:
    def test_size_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_percent = Size(30, UnitEnum.PERCENT)

        assert not size_px.is_relative()
        assert size_percent.is_relative()

    def test_point_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)

        point_abs = Point(size_px, size_px2)
        point_mix = Point(size_percent, size_px)
        point_rel = Point(size_percent, size_percent2)

        assert not point_abs.is_relative()
        assert not point_mix.is_relative()
        assert point_rel.is_relative()

    def test_stretch_is_relative(self):
        size_px = Size(30, UnitEnum.PIXEL)
        size_px2 = Size(30, UnitEnum.PIXEL)

        size_percent = Size(30, UnitEnum.PERCENT)
        size_percent2 = Size(30, UnitEnum.PERCENT)

        stretch_abs = Stretch(size_px, size_px2)
        stretch_mix = Stretch(size_percent, size_px)
        stretch_rel = Stretch(size_percent, size_percent2)

        assert not stretch_abs.is_relative()
        assert not stretch_mix.is_relative()
        assert stretch_rel.is_relative()

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

        assert not padding_abs.is_relative()
        assert not padding_mix.is_relative()
        assert padding_rel.is_relative()

    def test_layout_is_relative(self):
        empty_layout = Layout()

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

        assert empty_layout.is_relative()
        assert not layout_abs.is_relative()
        assert not layout_mix.is_relative()
        assert layout_rel.is_relative()


class TestSize:
    @pytest.mark.parametrize('string, value, unit', [
        ('1px', 1.0, UnitEnum.PIXEL), ('2.3em', 2.3, UnitEnum.EM),
        ('12.34%', 12.34, UnitEnum.PERCENT), ('1.234c', 1.234, UnitEnum.CELL),
        ('10pt', 10.0, UnitEnum.PT), ('0', 0.0, UnitEnum.PIXEL)])
    def test_valid_size_from_string(self, string, value, unit):
        size = Size.from_string(string)

        assert size.value == value
        assert size.unit == unit

    @pytest.mark.parametrize('string', ['10', '11,1px', '12xx', '%', 'o1pt'])
    def test_invalid_size_from_string(self, string):
        with pytest.raises(CaptionReadSyntaxError) as exc_info:
            Size.from_string(string)

        assert exc_info.value.args[0].startswith(f"Invalid size: {string}.")
