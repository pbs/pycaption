import pytest

from pycaption import CaptionReadSyntaxError, DFXPReader, DFXPWriter, WebVTTReader
from pycaption.geometry import (
    Alignment,
    HorizontalAlignmentEnum,
    Layout,
    Padding,
    Point,
    Size,
    Stretch,
    UnitEnum,
    VerticalAlignmentEnum,
)


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
        padding_rel = Padding(size_percent, size_percent2, size_percent3, size_percent4)

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

        layout_abs = Layout(origin=point_abs, extent=stretch_abs, padding=None)

        layout_mix = Layout(origin=point_abs, extent=stretch_rel, padding=None)

        layout_rel = Layout(origin=point_rel, extent=stretch_rel, padding=None)

        assert empty_layout.is_relative()
        assert not layout_abs.is_relative()
        assert not layout_mix.is_relative()
        assert layout_rel.is_relative()


class TestSize:
    @pytest.mark.parametrize(
        "string, value, unit",
        [
            ("1px", 1.0, UnitEnum.PIXEL),
            ("2.3em", 2.3, UnitEnum.EM),
            ("12.34%", 12.34, UnitEnum.PERCENT),
            ("1.234c", 1.234, UnitEnum.CELL),
            ("10pt", 10.0, UnitEnum.PT),
            ("0", 0.0, UnitEnum.PIXEL),
        ],
    )
    def test_valid_size_from_string(self, string, value, unit):
        size = Size.from_string(string)

        assert size.value == value
        assert size.unit == unit

    @pytest.mark.parametrize(
        "string, value, unit",
        [
            ("-5%", -5.0, UnitEnum.PERCENT),
            ("-2.5px", -2.5, UnitEnum.PIXEL),
        ],
    )
    def test_negative_size_from_string(self, string, value, unit):
        size = Size.from_string(string)

        assert size.value == value
        assert size.unit == unit

    @pytest.mark.parametrize(
        "string, value, unit",
        [
            ("80vw", 80.0, UnitEnum.VW),
            ("50vh", 50.0, UnitEnum.VH),
        ],
    )
    def test_viewport_units_from_string(self, string, value, unit):
        size = Size.from_string(string)

        assert size.value == value
        assert size.unit == unit

    @pytest.mark.parametrize("string", ["10", "11,1px", "12xx", "%", "o1pt"])
    def test_invalid_size_from_string(self, string):
        with pytest.raises(CaptionReadSyntaxError) as exc_info:
            Size.from_string(string)

        assert exc_info.value.args[0].startswith(f"Invalid size: {string}.")


class TestAlignmentFromHorizontalAndVertical:
    @pytest.mark.parametrize(
        "text_align, expected",
        [
            ("left", HorizontalAlignmentEnum.LEFT),
            ("start", HorizontalAlignmentEnum.START),
            ("center", HorizontalAlignmentEnum.CENTER),
            ("right", HorizontalAlignmentEnum.RIGHT),
            ("end", HorizontalAlignmentEnum.END),
        ],
    )
    def test_horizontal_mapping(self, text_align, expected):
        alignment = Alignment.from_horizontal_and_vertical_align(text_align=text_align)

        assert alignment.horizontal == expected
        assert alignment.vertical is None

    @pytest.mark.parametrize(
        "display_align, expected",
        [
            ("before", VerticalAlignmentEnum.TOP),
            ("center", VerticalAlignmentEnum.CENTER),
            ("after", VerticalAlignmentEnum.BOTTOM),
        ],
    )
    def test_vertical_mapping(self, display_align, expected):
        alignment = Alignment.from_horizontal_and_vertical_align(
            display_align=display_align
        )

        assert alignment.vertical == expected
        assert alignment.horizontal is None

    def test_both_dimensions(self):
        alignment = Alignment.from_horizontal_and_vertical_align(
            text_align="center", display_align="after"
        )

        assert alignment.horizontal == HorizontalAlignmentEnum.CENTER
        assert alignment.vertical == VerticalAlignmentEnum.BOTTOM

    def test_unknown_values_return_none(self):
        assert (
            Alignment.from_horizontal_and_vertical_align(
                text_align="bogus", display_align="bogus"
            )
            is None
        )

    def test_no_args_returns_none(self):
        assert Alignment.from_horizontal_and_vertical_align() is None


class TestFitToScreen:
    def test_origin_at_90_horizontal_returns_unchanged(self):
        origin = Point(Size(90, UnitEnum.PERCENT), Size(50, UnitEnum.PERCENT))
        extent = Stretch(Size(40, UnitEnum.PERCENT), Size(20, UnitEnum.PERCENT))
        layout = Layout(origin=origin, extent=extent)

        result = layout.fit_to_screen()

        assert result.extent == extent

    def test_origin_beyond_95_vertical_returns_unchanged(self):
        origin = Point(Size(50, UnitEnum.PERCENT), Size(95, UnitEnum.PERCENT))
        extent = Stretch(Size(40, UnitEnum.PERCENT), Size(20, UnitEnum.PERCENT))
        layout = Layout(origin=origin, extent=extent)

        result = layout.fit_to_screen()

        assert result.extent == extent

    def test_origin_below_thresholds_still_adjusts(self):
        origin = Point(Size(80, UnitEnum.PERCENT), Size(80, UnitEnum.PERCENT))
        extent = Stretch(Size(40, UnitEnum.PERCENT), Size(40, UnitEnum.PERCENT))
        layout = Layout(origin=origin, extent=extent)

        result = layout.fit_to_screen()

        assert result.extent.horizontal == Size(10, UnitEnum.PERCENT)
        assert result.extent.vertical == Size(15, UnitEnum.PERCENT)

    def test_non_percent_units_returns_unchanged(self):
        origin = Point(Size(10, UnitEnum.VW), Size(10, UnitEnum.VH))
        extent = Stretch(Size(80, UnitEnum.VW), Size(50, UnitEnum.VH))
        layout = Layout(origin=origin, extent=extent)

        result = layout.fit_to_screen()

        assert result is layout


class TestViewportUnitConversion:
    def test_vw_converts_to_percent(self):
        size = Size(80, UnitEnum.VW)

        result = size.as_percentage_of(video_width=1920)

        assert result.value == 80.0
        assert result.unit == UnitEnum.PERCENT

    def test_vh_converts_to_percent(self):
        size = Size(50, UnitEnum.VH)

        result = size.as_percentage_of(video_height=1080)

        assert result.value == 50.0
        assert result.unit == UnitEnum.PERCENT


class TestGeometryRoundTrips:
    def test_vtt_extreme_position_to_dfxp_roundtrip(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 position:95% line:95% size:40%\n"
            "Hello world\n"
        )
        caption_set = WebVTTReader().read(vtt)
        dfxp_output = DFXPWriter().write(caption_set)
        DFXPReader().read(dfxp_output)

    def test_dfxp_viewport_units_write_no_leak(self):
        dfxp = (
            '<?xml version="1.0" encoding="utf-8"?>\n'
            '<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"'
            ' xmlns:tts="http://www.w3.org/ns/ttml#styling">\n'
            "<head><layout>\n"
            '<region xml:id="r1" tts:origin="10vw 10vh"'
            ' tts:extent="80vw 50vh"/>\n'
            "</layout></head>\n"
            '<body><div><p begin="00:00:01.000" end="00:00:03.000"'
            ' region="r1">Hello</p></div></body></tt>\n'
        )
        caption_set = DFXPReader().read(dfxp)
        output = DFXPWriter(relativize=True, video_width=1920, video_height=1080).write(
            caption_set
        )

        assert "vw" not in output
        assert "vh" not in output
