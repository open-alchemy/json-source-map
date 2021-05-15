"""Types for calculating the JSON source map."""

import dataclasses
import typing


class TLocationDict(
    typing.TypedDict
):  # pylint: disable=inherit-non-class,too-few-public-methods
    """The location of a source map entry."""

    line: int
    column: int
    pos: int


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

    def to_dict(self) -> TLocationDict:
        """Convert to dictionary."""
        return {
            "line": self.line,
            "column": self.column,
            "pos": self.position,
        }


class TEntryDictBase(
    typing.TypedDict
):  # pylint: disable=inherit-non-class,too-few-public-methods
    """The base for start and end location dictionary for a value in the source."""

    value: TLocationDict
    valueEnd: TLocationDict


class TEntryDict(TEntryDictBase, total=False):  # pylint: disable=too-few-public-methods
    """The start and end location for a value dictionary in the source."""

    key: TLocationDict
    keyEnd: TLocationDict


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

    def to_dict(self) -> TEntryDict:
        """Convert to dictionary."""
        value: TEntryDict = {
            "value": self.value_start.to_dict(),
            "valueEnd": self.value_end.to_dict(),
        }
        if self.key_start is not None:
            value["key"] = self.key_start.to_dict()
        if self.key_end is not None:
            value["keyEnd"] = self.key_end.to_dict()
        return value


TSourceMapEntries = typing.List[typing.Tuple[str, Entry]]
TSourceMap = typing.Dict[str, Entry]
