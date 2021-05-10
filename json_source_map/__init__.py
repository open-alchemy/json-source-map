"""Calculate the JSON source map."""

import dataclasses
import typing


@dataclasses.dataclass
class SourceMapEntryLocation:
    """
    The location of a source map entry.

    Attrs:
        line: The number of new line characters before the location in the source.
        column: The number of characters before the location in the source since the
            last new line character.
        position: The number of characters before the location in the source.

    """

    line: int
    column: int
    position: int


@dataclasses.dataclass
class SourceMapEntry:
    """
    The start and end location for a value in the source.

    Attrs:
        value: The start location of the value.
        valueEnd: The end location of the value.
        key: The start location of the key included if the item is directly with an
            object.
        keyEnd: The end location of the key included if the item is directly with an
            object.

    """

    value: SourceMapEntryLocation
    valueEnd: SourceMapEntryLocation
    key: typing.Optional[SourceMapEntryLocation] = None
    keyEnd: typing.Optional[SourceMapEntryLocation] = None


TSourceMap = dict[str, list[SourceMapEntry]]


def calculate(source: str) -> TSourceMap:
    """
    Calculate the source map for a JSON value.

    Args:
        source: The JSON document.

    Returns:
        The source map for the JSON document.

    """
