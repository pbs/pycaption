import bs4

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

# monkeypatch for https://bugs.launchpad.net/beautifulsoup/+bug/1840141

def patched__new__(cls, prefix, name, namespace=None):
    if not name:
        obj = str.__new__(cls, prefix)
    elif prefix is None:
        # Not really namespaced.
        obj = str.__new__(cls, name)
    else:
        obj = str.__new__(cls, prefix + ":" + name)
    obj.prefix = prefix
    obj.name = name
    obj.namespace = namespace
    return obj


bs4.element.NamespacedAttribute.__new__ = patched__new__


def detect_format(caps):
    """
    Detect the format of the provided caption string.

    :returns: the reader class for the detected format.
    """
    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
