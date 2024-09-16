from pycaption.scc.constants import ALL_CHARACTERS, COMMAND_LABELS


def translate_scc(scc_content, brackets='[]'):
    """
    Replaces hexadecimal words with their meaning

    In order to make SCC files more human-readable and easier to debug,
    this function is used to replace command codes with their labels and
    character bytes with their actual characters

    :param scc_content: SCC captions to be translated
    :type scc_content: str
    :param brackets: Brackets to group the translated content of a command
    :type brackets: str
    :return: Translated SCC captions
    :rtype: str
    """
    opening_bracket, closing_bracket = brackets if brackets else ('', '')
    scc_elements = set(scc_content.split())
    for elem in scc_elements:
        name = COMMAND_LABELS.get(elem, ALL_CHARACTERS.get(elem))
        # If a 2 byte command was not found, try retrieving 1 byte characters
        if not name:
            char1 = ALL_CHARACTERS.get(elem[:2])
            char2 = ALL_CHARACTERS.get(elem[2:])
            if char1 is not None and char2 is not None:
                name = f"{char1}{char2}"
        if name:
            scc_content = scc_content.replace(
                elem, f"{opening_bracket}{name}{closing_bracket}")
    return scc_content
