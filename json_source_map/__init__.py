"""Calculate the JSON source map."""

import dataclasses
import typing
from json import decoder


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


TSourceMap = typing.Dict[str, typing.List[Entry]]
SPACE = "\u0020"
TAB = "\u0009"
RETURN = "\u000A"
CARRIAGE_RETURN = "\u000D"
WHITESPACE = {SPACE, TAB, RETURN, CARRIAGE_RETURN}
BEGIN_ARRAY = "\u005B"
END_ARRAY = "\u005D"
BEGIN_OBJECT = "\u007B"
END_OBJECT = "\u007D"
NAME_SEPARATOR = "\u003A"
VALUE_SEPARATOR = "\u002C"
CONTROL_CHARACTER = {
    BEGIN_ARRAY,
    END_ARRAY,
    BEGIN_OBJECT,
    END_OBJECT,
    NAME_SEPARATOR,
    VALUE_SEPARATOR,
}
QUOTATION_MARK = "\u0022"
ESCAPE = "\u005C"


def handle_primitive(
    source: str, current_location: Location
) -> typing.List[typing.Tuple[str, Entry]]:
    """
    Calculate the source map of a primitive type.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    # Advance to first non-whitespace character
    while (
        current_location.position < len(source)
        and source[current_location.position] in WHITESPACE
    ):
        if source[current_location.position] in {SPACE, TAB, CARRIAGE_RETURN}:
            current_location.column += 1
            current_location.position += 1
        else:
            current_location.line += 1
            current_location.column = 0
            current_location.position += 1

    # The position must not be at the end of of the string
    assert current_location.position < len(source)

    value_start = Location(
        current_location.line, current_location.column, current_location.position
    )

    # Check for string
    if source[current_location.position] == QUOTATION_MARK:
        # Find the end position of the string, ignoring because py_scanstring does exist
        _, end_position = decoder.py_scanstring(  # type: ignore[attr-defined]
            source, current_location.position + 1
        )
        # py_scanstring returns the string index just after the closing quote mark
        current_location.column += end_position - current_location.position
        current_location.position = end_position

        value_end = Location(
            current_location.line, current_location.column, current_location.position
        )
        return [("", Entry(value_start=value_start, value_end=value_end))]

    # Advance to the next control character, whitespace or end of source
    while (
        current_location.position < len(source)
        and source[current_location.position] not in CONTROL_CHARACTER
        and source[current_location.position] not in WHITESPACE
    ):
        current_location.column += 1
        current_location.position += 1

    value_end = Location(
        current_location.line, current_location.column, current_location.position
    )
    return [("", Entry(value_start=value_start, value_end=value_end))]
