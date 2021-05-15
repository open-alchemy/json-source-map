"""Errors for calculating the JSON source map."""


class BaseError(Exception):
    """Base class for all errors."""


class InvalidJsonError(BaseError):
    """Raised when JSON is invalid."""
