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
