from datetime import timedelta


def format_timestamp(value, msec_separator=None):
    """
    Format a PCC timestamp into a string value suitable for some of the
    supported output formats (ex. SRT, DFXP).
    """
    datetime_value = timedelta(milliseconds=(int(value / 1000)))

    str_value = str(datetime_value)[:11]
    if not datetime_value.microseconds:
        str_value += '.000'

    if msec_separator is not None:
        str_value = str_value.replace(".", msec_separator)

    return '0' + str_value
