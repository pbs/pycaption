from logging import FATAL

from cssutils import log

from ..geometry import HorizontalAlignmentEnum

log.setLevel(FATAL)

SAMI_BASE_MARKUP = """
<sami>
    <head>
        <style type="text/css"/>
    </head>
    <body/>
</sami>"""

HORIZONTAL_ALIGNMENT_MAP = {
    HorizontalAlignmentEnum.LEFT: "left",
    HorizontalAlignmentEnum.CENTER: "center",
    HorizontalAlignmentEnum.RIGHT: "right",
    HorizontalAlignmentEnum.START: "left",
    HorizontalAlignmentEnum.END: "right",
}
