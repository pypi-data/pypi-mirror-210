"""Exception definitions used in Tixent."""


class TixentError(Exception):
    """A generic, tixent-specific error."""


class TextTooLongError(TixentError):
    """When the text is too long."""
