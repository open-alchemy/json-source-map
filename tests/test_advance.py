"""Tests for functions that advance position to certain characters."""

import pytest

from json_source_map.advance import to_next_non_whitespace
from json_source_map.constants import CARRIAGE_RETURN, RETURN, SPACE, TAB
from json_source_map.types import Location

TO_NEXT_NON_WHITESPACE_TESTS = (
    [
        pytest.param("", Location(0, 0, 0), Location(0, 0, 0), id="empty at start"),
        pytest.param(
            "", Location(0, 1, 1), Location(0, 1, 1), id="empty at beyond end"
        ),
        pytest.param(
            "a",
            Location(0, 0, 0),
            Location(0, 0, 0),
            id="single not whitespace at start",
        ),
        pytest.param(
            "a", Location(0, 1, 1), Location(0, 1, 1), id="single not whitespace at end"
        ),
    ]
    + [
        pytest.param(
            f"{whitespace}",
            Location(0, 0, 0),
            Location(0, 1, 1),
            id=f"single whitespace {repr(whitespace)}",
        )
        for whitespace in [SPACE, TAB, CARRIAGE_RETURN]
    ]
    + [
        pytest.param(
            f"{SPACE}{SPACE}",
            Location(0, 0, 0),
            Location(0, 2, 2),
            id="multiple same line whitespace",
        ),
        pytest.param(
            f"{SPACE}{SPACE}{SPACE}",
            Location(0, 0, 0),
            Location(0, 3, 3),
            id="many same line whitespace",
        ),
    ]
    + [
        pytest.param(
            f"{RETURN}",
            Location(0, 0, 0),
            Location(1, 0, 1),
            id="single new line whitespace",
        ),
        pytest.param(
            f"{RETURN}{RETURN}",
            Location(0, 0, 0),
            Location(2, 0, 2),
            id="multiple new line whitespace",
        ),
        pytest.param(
            f"{RETURN}{RETURN}{RETURN}",
            Location(0, 0, 0),
            Location(3, 0, 3),
            id="many new line whitespace",
        ),
    ]
)


@pytest.mark.parametrize(
    "source, location, expected_location", TO_NEXT_NON_WHITESPACE_TESTS
)
def test_to_next_non_whitespace(source, location, expected_location):
    """
    GIVEN source, location and expected location
    WHEN to_next_non_whitespace is called with the source and location
    THEN the location is equal to the expected location.
    """
    to_next_non_whitespace(source=source, current_location=location)

    assert location == expected_location
