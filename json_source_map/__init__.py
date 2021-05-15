"""Calculate the JSON source map."""

from json import decoder

from . import advance, constants, errors, types


def check_not_end(*, source: str, current_location: types.Location) -> None:
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


def handle_value(
    *, source: str, current_location: types.Location
) -> types.TSourceMapEntries:
    """
    Calculate the source map of any value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance.to_next_non_whitespace(source=source, current_location=current_location)
    check_not_end(source=source, current_location=current_location)

    if source[current_location.position] == constants.BEGIN_ARRAY:
        return handle_array(source=source, current_location=current_location)
    if source[current_location.position] == constants.BEGIN_OBJECT:
        return handle_object(source=source, current_location=current_location)
    return handle_primitive(source=source, current_location=current_location)


def handle_object(
    *, source: str, current_location: types.Location
) -> types.TSourceMapEntries:
    """
    Calculate the source map of an object value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance.to_next_non_whitespace(source=source, current_location=current_location)

    # Must be at the object start location
    check_not_end(source=source, current_location=current_location)
    if source[current_location.position] != constants.BEGIN_OBJECT:
        raise errors.InvalidJsonError(
            f"expected an object to start, {current_location=}"
        )
    value_start = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    current_location.column += 1
    current_location.position += 1

    entries: types.TSourceMapEntries = []
    while current_location.position < len(source):
        advance.to_next_non_whitespace(source=source, current_location=current_location)
        # Check for object end
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] == constants.END_OBJECT:
            break
        # Check for value separator
        if source[current_location.position] == constants.VALUE_SEPARATOR:
            current_location.column += 1
            current_location.position += 1
            continue
        # Check for other control characters
        if source[current_location.position] in {
            constants.BEGIN_OBJECT,
            constants.BEGIN_ARRAY,
            constants.END_ARRAY,
            constants.NAME_SEPARATOR,
        }:
            raise errors.InvalidJsonError(
                f"invalid character {source[current_location.position]}, "
                f"{current_location=}"
            )

        # Must have a key
        key_start = types.Location(
            line=current_location.line,
            column=current_location.column,
            position=current_location.position,
        )
        handle_value(source=source, current_location=current_location)
        check_not_end(source=source, current_location=current_location)
        key_end = types.Location(
            line=current_location.line,
            column=current_location.column,
            position=current_location.position,
        )
        key_value = source[key_start.position + 1 : key_end.position - 1]

        # Handle value
        advance.to_next_non_whitespace(source=source, current_location=current_location)
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] != constants.NAME_SEPARATOR:
            raise errors.InvalidJsonError(
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
                types.Entry(
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
    value_end = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    return [("", types.Entry(value_start=value_start, value_end=value_end))] + entries


def handle_array(
    *, source: str, current_location: types.Location
) -> types.TSourceMapEntries:
    """
    Calculate the source map of an array value.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance.to_next_non_whitespace(source=source, current_location=current_location)

    # Must be at the array start location
    check_not_end(source=source, current_location=current_location)
    if source[current_location.position] != constants.BEGIN_ARRAY:
        raise errors.InvalidJsonError(
            f"expected an array to start, {current_location=}"
        )
    value_start = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    current_location.column += 1
    current_location.position += 1

    array_index = 0
    entries: types.TSourceMapEntries = []
    while current_location.position < len(source):
        advance.to_next_non_whitespace(source=source, current_location=current_location)
        # Check for array end
        check_not_end(source=source, current_location=current_location)
        if source[current_location.position] == constants.END_ARRAY:
            break
        # Check for value separator
        if source[current_location.position] == constants.VALUE_SEPARATOR:
            current_location.column += 1
            current_location.position += 1
            continue
        # Check for other control characters
        if source[current_location.position] in {
            constants.END_OBJECT,
            constants.NAME_SEPARATOR,
        }:
            raise errors.InvalidJsonError(
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
    value_end = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    return [("", types.Entry(value_start=value_start, value_end=value_end))] + entries


def handle_primitive(
    *, source: str, current_location: types.Location
) -> types.TSourceMapEntries:
    """
    Calculate the source map of a primitive type.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    Returns:
        A list of JSON pointers and source map entries.

    """
    advance.to_next_non_whitespace(source=source, current_location=current_location)
    check_not_end(source=source, current_location=current_location)

    value_start = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    # Check for string
    if source[current_location.position] == constants.QUOTATION_MARK:
        # Find the end position of the string, ignoring because py_scanstring does exist
        try:
            _, end_position = decoder.py_scanstring(  # type: ignore[attr-defined]
                source, current_location.position + 1
            )
        except decoder.JSONDecodeError as error:
            raise errors.InvalidJsonError(
                f"a string value is not valid, {current_location=}"
            ) from error

        # py_scanstring returns the string index just after the closing quote mark
        current_location.column += end_position - current_location.position
        current_location.position = end_position

        value_end = types.Location(
            current_location.line, current_location.column, current_location.position
        )
        return [("", types.Entry(value_start=value_start, value_end=value_end))]

    # Advance to the next control character, whitespace or end of source
    while (
        current_location.position < len(source)
        and source[current_location.position] not in constants.CONTROL_CHARACTER
        and source[current_location.position] not in constants.WHITESPACE
    ):
        current_location.column += 1
        current_location.position += 1

    value_end = types.Location(
        current_location.line, current_location.column, current_location.position
    )

    return [("", types.Entry(value_start=value_start, value_end=value_end))]
