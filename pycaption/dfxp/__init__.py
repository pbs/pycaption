"""DFXP/TTML caption format reader and writer package.

Provides DFXPReader for parsing DFXP/TTML files into CaptionSet objects,
DFXPWriter for serializing CaptionSet objects to DFXP/TTML, and legacy/
single-positioning writer variants.
"""

from .constants import (  # noqa: F401
    DFXP_ATTR_XML_ID,
    DFXP_ATTR_XML_LANG,
    DFXP_BASE_MARKUP,
    DFXP_DEFAULT_LANGUAGE_CODE,
    DFXP_DEFAULT_REGION,
    DFXP_DEFAULT_REGION_ID,
    DFXP_DEFAULT_STYLE,
    DFXP_DEFAULT_STYLE_ID,
    HORIZONTAL_ALIGNMENT_TO_DFXP,
    VERTICAL_ALIGNMENT_TO_DFXP,
)
from .extras import LegacyDFXPWriter, SinglePositioningDFXPWriter  # noqa: F401
from .reader import DFXPReader  # noqa: F401
from .writer import DFXPWriter  # noqa: F401
