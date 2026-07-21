import re

from ..geometry import (
    Alignment,
    HorizontalAlignmentEnum,
    Layout,
    VerticalAlignmentEnum,
)

DFXP_BASE_MARKUP = """
<tt xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
    <head>
        <styling/>
        <layout/>
    </head>
    <body/>
</tt>
"""

DFXP_DEFAULT_STYLE = {
    "color": "white",
    "font-family": "monospace",
    "font-size": "1c",
}

DFXP_DEFAULT_REGION = Layout(
    alignment=Alignment(HorizontalAlignmentEnum.START, VerticalAlignmentEnum.BOTTOM)
)

DFXP_DEFAULT_STYLE_ID = "default"
DFXP_DEFAULT_REGION_ID = "bottom"

CLOCK_TIME_PATTERN = (
    r"(?P<clock_time>(?P<hours>\d+):(?P<minutes>\d{2}):(?P<seconds>\d{2})"
    r"(:(?P<frames>\d{2})|\.(?P<sub_frames>\d+))?)"
)
OFFSET_TIME_PATTERN = (
    r"(?P<offset_time>(?P<time_count>\d+(\.\d+)?)" r"(?P<metric>h|m|s|ms|f|t))"
)
TIME_EXPRESSION_PATTERN = re.compile(rf"^({CLOCK_TIME_PATTERN}|{OFFSET_TIME_PATTERN})$")

MICROSECONDS_PER_UNIT = {
    "hours": 3600000000,
    "minutes": 60000000,
    "seconds": 1000000,
    "milliseconds": 1000,
}

DFXP_DEFAULT_LANGUAGE_CODE = "en"

DFXP_ATTR_XML_LANG = "xml:lang"
DFXP_ATTR_XML_ID = "xml:id"

HORIZONTAL_ALIGNMENT_TO_DFXP = {
    HorizontalAlignmentEnum.LEFT: "left",
    HorizontalAlignmentEnum.CENTER: "center",
    HorizontalAlignmentEnum.RIGHT: "right",
    HorizontalAlignmentEnum.START: "start",
    HorizontalAlignmentEnum.END: "end",
}

VERTICAL_ALIGNMENT_TO_DFXP = {
    VerticalAlignmentEnum.TOP: "before",
    VerticalAlignmentEnum.CENTER: "center",
    VerticalAlignmentEnum.BOTTOM: "after",
}


def _create_external_alignment(alignment):
    """Convert an Alignment object to a dict of DFXP attributes.

    :type alignment: Alignment
    :rtype: dict
    """
    result = {}
    if not alignment:
        return result
    if not (alignment.horizontal or alignment.vertical):
        return result

    horizontal = HORIZONTAL_ALIGNMENT_TO_DFXP.get(alignment.horizontal)
    if horizontal:
        result["tts:textAlign"] = horizontal

    vertical = VERTICAL_ALIGNMENT_TO_DFXP.get(alignment.vertical)
    if vertical:
        result["tts:displayAlign"] = vertical

    return result
