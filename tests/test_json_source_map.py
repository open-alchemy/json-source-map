"""Tests for JsonSourceMap."""

import pytest

from json_source_map import (
    CARRIAGE_RETURN,
    CONTROL_CHARACTER,
    ESCAPE,
    QUOTATION_MARK,
    RETURN,
    SPACE,
    TAB,
    WHITESPACE,
    Entry,
    Location,
    advance_to_next_non_whitespace,
    handle_primitive,
)

ADVANCE_TO_NEXT_NON_WHITESPACE_TESTS = (
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
    "source, location, expected_location", ADVANCE_TO_NEXT_NON_WHITESPACE_TESTS
)
def test_advance_to_next_non_whitespace(source, location, expected_location):
    """
    GIVEN source, location and expected location
    WHEN advance_to_next_non_whitespace is called with the source and location
    THEN the location is equal to the expected location.
    """
    advance_to_next_non_whitespace(source=source, current_location=location)

    assert location == expected_location


HANDLE_PRIMITIVE_TESTS = (
    [
        pytest.param(
            "0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 1, 1)))],
            Location(0, 1, 1),
            id="number primitive",
        ),
        pytest.param(
            "-0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id="negative number primitive",
        ),
        pytest.param(
            "+0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id="positive number primitive",
        ),
        pytest.param(
            "0.0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="decimal number primitive",
        ),
        pytest.param(
            "0e0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="exponential number primitive",
        ),
        pytest.param(
            "0E0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="capital exponential number primitive",
        ),
        pytest.param(
            "00",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id="multi character number primitive",
        ),
        pytest.param(
            "000",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="many character number primitive",
        ),
    ]
    + [
        pytest.param(
            f"{value}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 1, 1)))],
            Location(0, 1, 1),
            id=f"value number primitive {repr(value)}",
        )
        for value in range(10)
    ]
    + [
        pytest.param(
            f"{SPACE}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id="start whitespace",
        )
    ]
    + [
        pytest.param(
            f"0{control}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 1, 1)))],
            Location(0, 1, 1),
            id=f"end control {repr(control)}",
        )
        for control in CONTROL_CHARACTER
    ]
    + [
        pytest.param(
            f"0{whitespace}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 1, 1)))],
            Location(0, 1, 1),
            id=f"end whitespace {repr(whitespace)}",
        )
        for whitespace in WHITESPACE
    ]
    + [
        pytest.param(
            "true",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4)))],
            Location(0, 4, 4),
            id="true primitive",
        ),
        pytest.param(
            "false",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 5, 5)))],
            Location(0, 5, 5),
            id="false primitive",
        ),
        pytest.param(
            "null",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4)))],
            Location(0, 4, 4),
            id="null primitive",
        ),
    ]
    + [
        pytest.param(
            f"{QUOTATION_MARK}{QUOTATION_MARK}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id="empty string primitive",
        ),
    ]
    + [
        pytest.param(
            f"{QUOTATION_MARK}a{QUOTATION_MARK}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="single character string primitive",
        ),
    ]
    + [
        pytest.param(
            f"{QUOTATION_MARK}aa{QUOTATION_MARK}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4)))],
            Location(0, 4, 4),
            id="multi character string primitive",
        ),
    ]
    + [
        pytest.param(
            f"{QUOTATION_MARK}aaa{QUOTATION_MARK}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 5, 5)))],
            Location(0, 5, 5),
            id="many character string primitive",
        ),
    ]
    + [
        pytest.param(
            f"{QUOTATION_MARK}{ESCAPE}{QUOTATION_MARK}{QUOTATION_MARK}",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4)))],
            Location(0, 4, 4),
            id="escaped quote string primitive",
        ),
    ]
)


@pytest.mark.parametrize(
    "source, location, expected_entries, expected_location",
    HANDLE_PRIMITIVE_TESTS,
)
def test_handle_primitive(source, location, expected_entries, expected_location):
    """
    GIVEN source, location and expected entries and location
    WHEN handle_primitive is called with the source and location
    THEN the expected entries are returned and the location is at the expected location.
    """
    returned_entries = handle_primitive(source=source, current_location=location)

    assert returned_entries == expected_entries
    assert location == expected_location
