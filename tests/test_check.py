"""Tests functions that check expectations."""

import pytest

from json_source_map.check import not_end
from json_source_map.errors import InvalidJsonError
from json_source_map.types import Location

NOT_END_TESTS = [
    pytest.param(
        "",
        Location(0, 0, 0),
        True,
        id="empty",
    ),
    pytest.param(
        "a",
        Location(0, 0, 0),
        False,
        id="single character start",
    ),
    pytest.param(
        "a",
        Location(0, 1, 1),
        True,
        id="single character after end",
    ),
]


@pytest.mark.parametrize(
    "source, location, expected_raise",
    NOT_END_TESTS,
)
def test_handle_value(source, location, expected_raise):
    """
    GIVEN source, location and expected raise
    WHEN not_end is called with the source and location
    THEN the InvalidJson is raised if expected raise is True.
    """
    if expected_raise:
        with pytest.raises(InvalidJsonError):
            not_end(source=source, current_location=location)
    else:
        not_end(source=source, current_location=location)
