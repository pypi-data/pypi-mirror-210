"""Type definitions used in Tixent."""

from typing import Callable, List

Template = Callable[[List[str]], str]
"""Type of function to generate a string from a list of texts."""

Counter = Callable[[str], int]
"""Type of function to count string."""
