class CaptionReadError(Exception):
    """
    Generic error raised when the reading of the caption file failed.
    """
    def __str__(self):
        return f'{self.__class__.__name__}({self.args[0]})'


class CaptionReadNoCaptions(CaptionReadError):
    """
    Error raised when the provided caption file was not containing any
    actual captions.
    """


class CaptionReadSyntaxError(CaptionReadError):
    """
    Error raised when the provided caption file has syntax errors and could
    not be parsed.
    """


class CaptionReadTimingError(CaptionReadError):
    """
    Error raised when a Caption is initialized with invalid timings.
    """


class RelativizationError(Exception):
    """
    Error raised when absolute positioning cannot be converted to
    percentage
    """


class InvalidInputError(RuntimeError):
    """Error raised when the input is invalid (i.e. a unicode string)"""
