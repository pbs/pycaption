"""pycaption — closed caption reading/writing library.

Reads captions from DFXP/TTML, SRT, SAMI, SCC, WebVTT, and MicroDVD into
a common intermediate representation (CaptionSet), and writes them back
to any supported format.
"""

from .base import Caption, CaptionConverter, CaptionList, CaptionNode, CaptionSet
from .dfxp import DFXPReader, DFXPWriter
from .exceptions import (
    CaptionReadError,
    CaptionReadNoCaptions,
    CaptionReadSyntaxError,
    CaptionReadWarning,
)
from .microdvd import MicroDVDReader, MicroDVDWriter
from .sami import SAMIReader, SAMIWriter
from .scc import SCCReader, SCCWriter
from .scc.translator import translate_scc
from .srt import SRTReader, SRTWriter
from .transcript import TranscriptWriter
from .webvtt import WebVTTReader, WebVTTWriter

__all__ = [
    "CaptionConverter",
    "DFXPReader",
    "DFXPWriter",
    "MicroDVDReader",
    "MicroDVDWriter",
    "SAMIReader",
    "SAMIWriter",
    "SRTReader",
    "SRTWriter",
    "SCCReader",
    "SCCWriter",
    "translate_scc",
    "WebVTTReader",
    "WebVTTWriter",
    "CaptionReadError",
    "CaptionReadNoCaptions",
    "CaptionReadSyntaxError",
    "CaptionReadWarning",
    "detect_format",
    "CaptionNode",
    "Caption",
    "CaptionList",
    "CaptionSet",
    "TranscriptWriter",
]

SUPPORTED_READERS = (
    DFXPReader,
    MicroDVDReader,
    WebVTTReader,
    SAMIReader,
    SRTReader,
    SCCReader,
)


def detect_format(caps):
    """Detect the caption format of the provided string.

    Tries each reader's ``detect()`` method in order and returns the
    first matching reader class, or None if no format matches.

    :param caps: Raw caption file content.
    :returns: The reader class for the detected format, or None.
    :rtype: type | None
    :raises CaptionReadNoCaptions: if caps is empty.
    """
    if not len(caps):
        raise CaptionReadNoCaptions("Empty caption file")

    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
