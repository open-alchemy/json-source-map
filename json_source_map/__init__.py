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


TSourceMapEntries = typing.List[typing.Tuple[str, Entry]]
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


class BaseError(Exception):
    """Base class for all errors."""


class InvalidJsonError(BaseError):
    """Raised when JSON is invalid."""


def advance_to_next_non_whitespace(*, source: str, current_location: Location) -> None:
    """
    Advance current_location to the next non-whitespace character.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    """
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


def check_not_end(*, source: str, current_location: Location) -> None:
    """
    Check that the position is not beyond the end of the document.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    """
    if current_location.position >= len(source):
        raise InvalidJsonError(
            f"the JSON document ended unexpectedly, {current_location=}"
        )


def handle_value(*, source: str, current_location: Location) -> TSourceMapEntries:
    """
    Calculate the source map of any value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance_to_next_non_whitespace(source=source, current_location=current_location)
    check_not_end(source=source, current_location=current_location)

    if source[current_location.position] == BEGIN_ARRAY:
        return handle_array(source=source, current_location=current_location)
    if source[current_location.position] == BEGIN_OBJECT:
        return handle_object(source=source, current_location=current_location)
    return handle_primitive(source=source, current_location=current_location)


def handle_object(*, source: str, current_location: Location) -> TSourceMapEntries:
    """
    Calculate the source map of an object value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance_to_next_non_whitespace(source=source, current_location=current_location)

    # Must be at the object start location
    check_not_end(source=source, current_location=current_location)
    if source[current_location.position] != BEGIN_OBJECT:
        raise InvalidJsonError(f"expected an object to start, {current_location=}")
    value_start = Location(
        current_location.line, current_location.column, current_location.position
    )

    current_location.column += 1
    current_location.position += 1

    entries: TSourceMapEntries = []
    while current_location.position < len(source):
        advance_to_next_non_whitespace(source=source, current_location=current_location)
        # Check for object end
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] == END_OBJECT:
            break
        # Check for value separator
        if source[current_location.position] == VALUE_SEPARATOR:
            current_location.column += 1
            current_location.position += 1
            continue
        # Check for other control characters
        if source[current_location.position] in {
            BEGIN_OBJECT,
            BEGIN_ARRAY,
            END_ARRAY,
            NAME_SEPARATOR,
        }:
            raise InvalidJsonError(
                f"invalid character {source[current_location.position]}, "
                f"{current_location=}"
            )

        # Must have a key
        key_start = Location(
            line=current_location.line,
            column=current_location.column,
            position=current_location.position,
        )
        handle_value(source=source, current_location=current_location)
        check_not_end(source=source, current_location=current_location)
        key_end = Location(
            line=current_location.line,
            column=current_location.column,
            position=current_location.position,
        )
        key_value = source[key_start.position + 1 : key_end.position - 1]

        # Handle value
        advance_to_next_non_whitespace(source=source, current_location=current_location)
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] != NAME_SEPARATOR:
            raise InvalidJsonError(
                f"expected name separator but got {source[current_location.position]}, "
                f"{current_location=}"
            )
        current_location.column += 1
        current_location.position += 1
        check_not_end(source=source, current_location=current_location)
        value_entries = iter(
            handle_value(source=source, current_location=current_location)
        )
        value_entry = next(value_entries)

        # Write pointers
        entries.append(
            (
                f"/{key_value}",
                Entry(
                    value_start=value_entry[1].value_start,
                    value_end=value_entry[1].value_end,
                    key_start=key_start,
                    key_end=key_end,
                ),
            )
        )
        entries.extend(
            (f"/{key_value}{pointer}", entry) for pointer, entry in value_entries
        )

    # Must be at the object end location
    check_not_end(source=source, current_location=current_location)
    current_location.column += 1
    current_location.position += 1
    value_end = Location(
        current_location.line, current_location.column, current_location.position
    )

    return [("", Entry(value_start=value_start, value_end=value_end))] + entries


def handle_array(*, source: str, current_location: Location) -> TSourceMapEntries:
    """
    Calculate the source map of an array value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance_to_next_non_whitespace(source=source, current_location=current_location)

    # Must be at the array start location
    check_not_end(source=source, current_location=current_location)
    if source[current_location.position] != BEGIN_ARRAY:
        raise InvalidJsonError(f"expected an array to start, {current_location=}")
    value_start = Location(
        current_location.line, current_location.column, current_location.position
    )

    current_location.column += 1
    current_location.position += 1

    array_index = 0
    entries: TSourceMapEntries = []
    while current_location.position < len(source):
        advance_to_next_non_whitespace(source=source, current_location=current_location)
        # Check for array end
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] == END_ARRAY:
            break
        # Check for value separator
        if source[current_location.position] == VALUE_SEPARATOR:
            current_location.column += 1
            current_location.position += 1
            continue
        # Check for other control characters
        if source[current_location.position] in {END_OBJECT, NAME_SEPARATOR}:
            raise InvalidJsonError(
                f"invalid character {source[current_location.position]}, "
                f"{current_location=}"
            )

        # Must have a value
        value_entries = handle_value(source=source, current_location=current_location)
        entries.extend(
            (f"/{array_index}{pointer}", entry) for pointer, entry in value_entries
        )
        array_index += 1

    # Must be at the array end location
    check_not_end(source=source, current_location=current_location)
    current_location.column += 1
    current_location.position += 1
    value_end = Location(
        current_location.line, current_location.column, current_location.position
    )

    return [("", Entry(value_start=value_start, value_end=value_end))] + entries


def handle_primitive(*, source: str, current_location: Location) -> TSourceMapEntries:
    """
    Calculate the source map of a primitive type.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance_to_next_non_whitespace(source=source, current_location=current_location)
    check_not_end(source=source, current_location=current_location)

    value_start = Location(
        current_location.line, current_location.column, current_location.position
    )

    # Check for string
    if source[current_location.position] == QUOTATION_MARK:
        # Find the end position of the string, ignoring because py_scanstring does exist
        try:
            _, end_position = decoder.py_scanstring(  # type: ignore[attr-defined]
                source, current_location.position + 1
            )
        except decoder.JSONDecodeError as error:
            raise InvalidJsonError(
                f"a string value is not valid, {current_location=}"
            ) from error

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
