import string


def punctuate(text: str) -> str:
    """
    Punctuate a string.

    Args:
        text: The text to punctuate.

    Returns:
        The punctuated text.
    """
    return text + "." if text[-1] not in string.punctuation else text


def depunctuate(text: str) -> str:
    """
    Depunctuate a string.

    Args:
        text: The text to depunctuate.

    Returns:
        The depunctuated text.
    """
    try:
        return text[:-1] if text[-1] in string.punctuation else text
    except IndexError:
        raise ValueError("Cannot depunctuate an empty string.", text)

def capitalize(text: str) -> str:
    """
    Capitalize a string.

    Args:
        text: The text to capitalize.

    Returns:
        The capitalized text.
    """
    return text[0].upper() + text[1:]

def embolden(text: str, keyword: str) -> str:
    """
    Embolden a keyword in a string.

    Args:
        text: The text to embolden.
        keyword: The keyword to embolden.

    Returns:
        The emboldened text.
    """
    return text.replace(keyword, f"<b>{keyword}</b>")