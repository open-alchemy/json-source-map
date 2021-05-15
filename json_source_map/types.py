"""Types for calculating the JSON source map."""

import dataclasses
import typing


@dataclasses.dataclass
class Location:
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
class Entry:
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

    value_start: Location
    value_end: Location
    key_start: typing.Optional[Location] = None
    key_end: typing.Optional[Location] = None


TSourceMapEntries = typing.List[typing.Tuple[str, Entry]]
TSourceMap = typing.Dict[str, typing.List[Entry]]
