"""
pycaption
~~~~~~~~

:copyright: (c) 2012 by PBS
:license: Apache 2.0

"""

__title__ = 'pycaption'
__version__ = '0.2.14'
__author__ = 'Joe Norton'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2012 PBS'

from .pycaption import CaptionConverter
from .dfxp import DFXPWriter, DFXPReader
from .sami import SAMIReader, SAMIWriter
from .srt import SRTReader, SRTWriter
from .scc import SCCReader
from .webvtt import WebVTTReader, WebVTTWriter


__all__ = [
    'CaptionConverter', 'DFXPReader', 'DFXPWriter',
    'SAMIReader', 'SAMIWriter', 'SRTReader', 'SRTWriter',
    'SCCReader', 'WebVTTReader', 'WebVTTWriter',
    'detect_format'
]


SUPPORTED_READERS = (
    DFXPReader, WebVTTReader, SAMIReader, SRTReader, SCCReader)


def detect_format(caps):
    """
    Detect the format of the provided caption string.

    :returns: the reader class for the detected format.
    """
    for reader in SUPPORTED_READERS:
        if reader().detect(caps):
            return reader

    return None
