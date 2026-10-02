"""Shared utility functions for pycaption."""


def is_leaf(element):
    """Return True if element is a BeautifulSoup leaf (NavigableString or <br>).

    :param element: A BeautifulSoup Tag or NavigableString.
    :rtype: bool
    """
    name = getattr(element, "name", None)
    if not name or name == "br":
        return True
    return False


def encode_leading_nbsp(text):
    """Write the leading non-breaking spaces of text as &#160; entities.

    prettify() strips the ends of a paragraph's text, and Python counts U+00A0
    as whitespace, so the indentation of a cue's first line would be lost.

    :type text: str
    :rtype: str
    """
    stripped = text.lstrip("\xa0")
    return "&#160;" * (len(text) - len(stripped)) + stripped
