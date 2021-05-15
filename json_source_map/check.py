"""Checks for calculating the JSON source map."""

from . import errors, types


def not_end(*, source: str, current_location: types.Location) -> None:
    """
    Check that the position is not beyond the end of the document.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    """
    if current_location.position >= len(source):
        raise errors.InvalidJsonError(
            f"the JSON document ended unexpectedly, {current_location=}"
        )
