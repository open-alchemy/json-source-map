"""Functions that advance to a certain next character."""

from . import constants, types


def to_next_non_whitespace(*, source: str, current_location: types.Location) -> None:
    """
    Advance current_location to the next non-whitespace character.

    Args:
        source: The JSON document.
        current_location: The current location in the source.

    """
    while (
        current_location.position < len(source)
        and source[current_location.position] in constants.WHITESPACE
    ):
        if source[current_location.position] in {
            constants.SPACE,
            constants.TAB,
            constants.CARRIAGE_RETURN,
        }:
            current_location.column += 1
            current_location.position += 1
        else:
            current_location.line += 1
            current_location.column = 0
            current_location.position += 1
