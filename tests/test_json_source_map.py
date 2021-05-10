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
    handle_primitive,
)


@pytest.mark.parametrize(
    "source, location, expected_entries, expected_location",
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
            f"{whitespace}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2)))],
            Location(0, 2, 2),
            id=f"start whitespace {repr(whitespace)}",
        )
        for whitespace in (SPACE, TAB, CARRIAGE_RETURN)
    ]
    + [
        pytest.param(
            f"{whitespace}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(1, 0, 1), value_end=Location(1, 1, 2)))],
            Location(1, 1, 2),
            id=f"start whitespace {repr(whitespace)}",
        )
        for whitespace in (RETURN)
    ]
    + [
        pytest.param(
            f"{SPACE}{SPACE}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 2, 2), value_end=Location(0, 3, 3)))],
            Location(0, 3, 3),
            id="start multi whitespace",
        ),
        pytest.param(
            f"{SPACE}{SPACE}{SPACE}0",
            Location(0, 0, 0),
            [("", Entry(value_start=Location(0, 3, 3), value_end=Location(0, 4, 4)))],
            Location(0, 4, 4),
            id="start many whitespace",
        ),
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
    ],
)
def test_handle_primitive(source, location, expected_entries, expected_location):
    """
    GIVEN source, location and expected entries and location
    WHEN handle_primitive is called with the source and location
    THEN the expected entries are returned and the location is at the expected location.
    """
    returned_entries = handle_primitive(source, location)

    assert returned_entries == expected_entries
    assert location == expected_location
