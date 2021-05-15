"""Calculate the JSON source map."""

from . import errors, handle, types


def calculate(source: str) -> types.TSourceMap:
    """
    Calculate the source map for a JSON document.

    Args:
        source: The JSON document.

    Returns:
        The source map.

    """
    if not isinstance(source, str):
        raise errors.InvalidInputError(f"source must be a string, got {type(source)}")
    if not source:
        raise errors.InvalidInputError("source must not be empty")

    return dict(handle.value(source=source, current_location=types.Location(0, 0, 0)))
