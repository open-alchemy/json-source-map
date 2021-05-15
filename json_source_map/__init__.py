"""Calculate the JSON source map."""

import json

from . import errors, handle, types


def calculate(source: str) -> types.TSourceMap:
    """
    Calculate the source map for a JSON document.

    Assume that the source is valid JSON.

    Args:
        source: The JSON document.

    Returns:
        The source map.

    """
    if not isinstance(source, str):
        raise errors.InvalidInputError(f"source must be a string, got {type(source)}")
    if not source:
        raise errors.InvalidInputError("source must not be empty")
    try:
        json.loads(source)
    except json.JSONDecodeError as error:
        raise errors.InvalidInputError("JSON is not valid") from error

    return dict(handle.value(source=source, current_location=types.Location(0, 0, 0)))
