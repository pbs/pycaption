from .base import (
    CaptionConverter, CaptionNode, Caption, CaptionList, CaptionSet)
from .dfxp import DFXPWriter, DFXPReader
from .sami import SAMIReader, SAMIWriter
from .srt import SRTReader, SRTWriter
from .scc import SCCReader, SCCWriter
from .webvtt import WebVTTReader, WebVTTWriter
from .exceptions import (
    CaptionReadError, CaptionReadNoCaptions, CaptionReadSyntaxError)


__all__ = [
    'CaptionConverter', 'DFXPReader', 'DFXPWriter',
    'SAMIReader', 'SAMIWriter', 'SRTReader', 'SRTWriter',
    'SCCReader', 'SCCWriter', 'WebVTTReader', 'WebVTTWriter',
    'CaptionReadError', 'CaptionReadNoCaptions', 'CaptionReadSyntaxError',
    'detect_format', 'CaptionNode', 'Caption', 'CaptionList', 'CaptionSet'
]

SUPPORTED_READERS = (
    DFXPReader, WebVTTReader, SAMIReader, SRTReader, SCCReader)

SUPPORTED_WRITERS = (
    DFXPWriter, WebVTTWriter, SAMIWriter, SRTWriter, SCCWriter)


def detect_format(caps):
    """
    Detect the format of the provided caption string.

    :returns: the reader class for the detected format.
    """
    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
