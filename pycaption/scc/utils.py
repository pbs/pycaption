from pycaption.scc.constants import (PAC_BYTES_TO_POSITIONING_MAP,
                                     PAC_TAB_OFFSET_COMMANDS)


def _is_pac_command(word):
    """Checks whether the given word is a Preamble Address Code [PAC] command

    :type word: str
    :param word: 4 letter unicode command

    :rtype: bool
    """
    byte1, byte2 = word[:2], word[2:]

    try:
        PAC_BYTES_TO_POSITIONING_MAP[byte1][byte2]
    except KeyError:
        return False
    else:
        return True


def is_pac_or_tab(word):
    return _is_pac_command(word) or word in PAC_TAB_OFFSET_COMMANDS
