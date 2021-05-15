"""Calculate the JSON source map."""

from . import errors, types


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

    return {}
