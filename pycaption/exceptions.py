"""Exception hierarchy for pycaption read/write errors."""


class CaptionReadError(Exception):
    """Generic error raised when reading a caption file fails."""

    def __str__(self):
        return f"{self.__class__.__name__}({self.args[0]})"


class CaptionReadNoCaptions(CaptionReadError):
    """Error raised when a caption file contains no actual captions."""


class CaptionReadSyntaxError(CaptionReadError):
    """Error raised when a caption file has syntax errors."""


class CaptionReadTimingError(CaptionReadError):
    """Error raised when a Caption has invalid start/end timings."""


class RelativizationError(Exception):
    """
    Error raised when absolute positioning cannot be converted to
    percentage
    """


class InvalidInputError(RuntimeError):
    """Error raised when the input is invalid (i.e. a unicode string)"""


class CaptionLineLengthError(CaptionReadError):
    """
    Error raised when a Caption has a line longer than 32 characters.
    """


class CaptionReadWarning(UserWarning):
    """Warning emitted when caption content is parseable but may cause
    rendering issues (e.g. cue positioned partially off-screen)."""
