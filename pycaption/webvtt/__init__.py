"""WebVTT (Web Video Text Tracks) reader and writer package.

Provides :class:`WebVTTReader` for parsing WebVTT files into a
:class:`~pycaption.base.CaptionSet`, and :class:`WebVTTWriter` for
serializing a CaptionSet back to WebVTT format.
"""

from .constants import microseconds
from .reader import WebVTTReader
from .writer import WebVTTWriter

__all__ = ["WebVTTReader", "WebVTTWriter", "microseconds"]
