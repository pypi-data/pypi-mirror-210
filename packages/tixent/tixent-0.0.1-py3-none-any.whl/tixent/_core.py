from typing import List

import tiktoken
from tiktoken.model import MODEL_TO_ENCODING

from tixent.exceptions import TextTooLongError
from tixent.types import Counter, Template


def tiktoken_counter(name: str) -> Counter:
    """
    Create a function to count string using
    [tiktoken](https://pypi.org/project/tiktoken/).

    Parameters
    ----------
    name : str
        Model or encoding name to determine the encoding, e.g., "gpt-4",
        "gpt-3.5-turbo", "text-davinci-003", "cl100k_base" or "p50k_base".

    Returns
    -------
    Counter
        A function that counts the number of tokens in a string.

    Examples
    --------
    >>> counter = tiktoken_counter("text-davinci-003")
    >>> count = counter("hello world")
    >>> assert count == 2

    See Also
    --------
    tiktoken.model.MODEL_TO_ENCODING :
        Correspondence between model name and encoding name in tiktoken.
    """
    encoding_name = MODEL_TO_ENCODING.get(name, name)
    encoding = tiktoken.get_encoding(encoding_name)

    def counter(text: str) -> int:
        tokens: List[int] = encoding.encode(text)
        return len(tokens)

    return counter


def _check_text_length(
    texts: List[str], template: Template, counter: Counter, max_count: int
) -> None:
    for i, text in enumerate(texts):
        t = template([text])
        count = counter(t)
        if count > max_count:
            message = f"texts[{i}] is too long"
            raise TextTooLongError(message)


def split(
    texts: List[str], template: Template, counter: Counter, max_count: int
) -> List[str]:
    """
    Split a List of texts so that the count of each element is less than or equal to
    specified `max_count`.

    Parameters
    ----------
    texts : List[str]
        A list of texts.
    template : Template
        A function to generate a string from a list of texts.
    counter : Counter
        A function to count string.
    max_count : int
        The maximum count of each element of the list returned by this function.

    Returns
    -------
    List[str]
        A list of texts that has been split and to which a template has been applied.
    """
    _check_text_length(texts, template, counter, max_count)

    split_texts: List[str] = []

    n = len(texts)
    i = 0

    while i < n:
        s = slice(i, i + 1)

        for j in range(i + 1, n + 1):
            s = slice(i, j)
            t = template(texts[s])
            count = counter(t)
            if count > max_count:
                s = slice(i, j - 1)
                break

        split_texts.append(template(texts[s]))
        i = s.stop

    return split_texts
