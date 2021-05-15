"""Tests for JsonSourceMap."""

import pytest

from json_source_map import handle_array, handle_object, handle_primitive, handle_value
from json_source_map.constants import (
    BEGIN_ARRAY,
    BEGIN_OBJECT,
    CONTROL_CHARACTER,
    END_ARRAY,
    END_OBJECT,
    ESCAPE,
    NAME_SEPARATOR,
    QUOTATION_MARK,
    SPACE,
    VALUE_SEPARATOR,
    WHITESPACE,
)
from json_source_map.errors import InvalidJsonError
from json_source_map.types import Entry, Location

HANDLE_VALUE_TESTS = [
    pytest.param(
        "0",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 1, 1)))],
        Location(0, 1, 1),
        id="number primitive",
    ),
    pytest.param(
        f"{SPACE}0",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="number primitive whitespace before",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{END_ARRAY}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="array",
    ),
    pytest.param(
        f"{SPACE}{BEGIN_ARRAY}{END_ARRAY}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="array whitespace before",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{END_OBJECT}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="object",
    ),
    pytest.param(
        f"{SPACE}{BEGIN_OBJECT}{END_OBJECT}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="object whitespace before",
    ),
]


@pytest.mark.parametrize(
    "source, location, expected_entries, expected_location",
    HANDLE_VALUE_TESTS,
)
def test_handle_value(source, location, expected_entries, expected_location):
    """
    GIVEN source, location and expected entries and location
    WHEN handle_value is called with the source and location
    THEN the expected entries are returned and the location is at the expected location.
    """
    returned_entries = handle_value(source=source, current_location=location)

    assert returned_entries == expected_entries
    assert location == expected_location


HANDLE_VALUE_ERROR_TESTS = [
    pytest.param("", Location(0, 1, 1), id="location after end"),
]


@pytest.mark.parametrize(
    "source, location",
    HANDLE_VALUE_ERROR_TESTS,
)
def test_handle_value_error(source, location):
    """
    GIVEN source and location
    WHEN handle_value is called with the source and location
    THEN InvalidJsonError is raised.
    """
    with pytest.raises(InvalidJsonError):
        handle_value(source=source, current_location=location)


HANDLE_OBJECT_TESTS = [
    pytest.param(
        f"{BEGIN_OBJECT}{END_OBJECT}]",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="empty",
    ),
    pytest.param(
        f"{SPACE}{BEGIN_OBJECT}{END_OBJECT}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="empty whitespace before",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{SPACE}{END_OBJECT}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="empty whitespace between",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{END_OBJECT}{SPACE}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="empty whitespace after",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"0{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 9, 9))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 8, 8),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 9, 9),
        id="single value",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{QUOTATION_MARK}{QUOTATION_MARK}{NAME_SEPARATOR}0{END_OBJECT}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 6, 6))),
            (
                "/",
                Entry(
                    value_start=Location(0, 4, 4),
                    value_end=Location(0, 5, 5),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 3, 3),
                ),
            ),
        ],
        Location(0, 6, 6),
        id="single value empty key",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{SPACE}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"0{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 10, 10))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 8, 8),
                    value_end=Location(0, 9, 9),
                    key_start=Location(0, 2, 2),
                    key_end=Location(0, 7, 7),
                ),
            ),
        ],
        Location(0, 10, 10),
        id="single value whitespace before",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{SPACE}{NAME_SEPARATOR}"
            f"0{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 10, 10))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 8, 8),
                    value_end=Location(0, 9, 9),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 10, 10),
        id="single value whitespace after key",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"{SPACE}0{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 10, 10))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 8, 8),
                    value_end=Location(0, 9, 9),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 10, 10),
        id="single value whitespace after name separator",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"0{SPACE}{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 10, 10))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 8, 8),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 10, 10),
        id="single value whitespace after value",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"0{END_OBJECT}{SPACE}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 9, 9))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 8, 8),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 9, 9),
        id="single value whitespace after",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"0{VALUE_SEPARATOR}{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 10, 10))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 8, 8),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
        ],
        Location(0, 10, 10),
        id="single value value separator",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}"
            f"{QUOTATION_MARK}key_1{QUOTATION_MARK}{NAME_SEPARATOR}0{VALUE_SEPARATOR}"
            f"{QUOTATION_MARK}key_2{QUOTATION_MARK}{NAME_SEPARATOR}0"
            f"{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 21, 21))),
            (
                "/key_1",
                Entry(
                    value_start=Location(0, 9, 9),
                    value_end=Location(0, 10, 10),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 8, 8),
                ),
            ),
            (
                "/key_2",
                Entry(
                    value_start=Location(0, 19, 19),
                    value_end=Location(0, 20, 20),
                    key_start=Location(0, 11, 11),
                    key_end=Location(0, 18, 18),
                ),
            ),
        ],
        Location(0, 21, 21),
        id="multi value",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}"
            f"{QUOTATION_MARK}key_1{QUOTATION_MARK}{NAME_SEPARATOR}0{VALUE_SEPARATOR}"
            f"{QUOTATION_MARK}key_2{QUOTATION_MARK}{NAME_SEPARATOR}0{VALUE_SEPARATOR}"
            f"{QUOTATION_MARK}key_3{QUOTATION_MARK}{NAME_SEPARATOR}0{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 31, 31))),
            (
                "/key_1",
                Entry(
                    value_start=Location(0, 9, 9),
                    value_end=Location(0, 10, 10),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 8, 8),
                ),
            ),
            (
                "/key_2",
                Entry(
                    value_start=Location(0, 19, 19),
                    value_end=Location(0, 20, 20),
                    key_start=Location(0, 11, 11),
                    key_end=Location(0, 18, 18),
                ),
            ),
            (
                "/key_3",
                Entry(
                    value_start=Location(0, 29, 29),
                    value_end=Location(0, 30, 30),
                    key_start=Location(0, 21, 21),
                    key_end=Location(0, 28, 28),
                ),
            ),
        ],
        Location(0, 31, 31),
        id="many value",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}"
            f"{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"{BEGIN_ARRAY}0{END_ARRAY}"
            f"{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 11, 11))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 10, 10),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
            (
                "/key/0",
                Entry(
                    value_start=Location(0, 8, 8),
                    value_end=Location(0, 9, 9),
                ),
            ),
        ],
        Location(0, 11, 11),
        id="nested array",
    ),
    pytest.param(
        (
            f"{BEGIN_OBJECT}"
            f"{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}"
            f"{BEGIN_OBJECT}"
            f"{QUOTATION_MARK}nestedKey{QUOTATION_MARK}{NAME_SEPARATOR}0"
            f"{END_OBJECT}"
            f"{END_OBJECT}"
        ),
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 23, 23))),
            (
                "/key",
                Entry(
                    value_start=Location(0, 7, 7),
                    value_end=Location(0, 22, 22),
                    key_start=Location(0, 1, 1),
                    key_end=Location(0, 6, 6),
                ),
            ),
            (
                "/key/nestedKey",
                Entry(
                    value_start=Location(0, 20, 20),
                    value_end=Location(0, 21, 21),
                    key_start=Location(0, 8, 8),
                    key_end=Location(0, 19, 19),
                ),
            ),
        ],
        Location(0, 23, 23),
        id="nested object",
    ),
]


@pytest.mark.parametrize(
    "source, location, expected_entries, expected_location",
    HANDLE_OBJECT_TESTS,
)
def test_handle_object(source, location, expected_entries, expected_location):
    """
    GIVEN source, location and expected entries and location
    WHEN handle_object is called with the source and location
    THEN the expected entries are returned and the location is at the expected location.
    """
    returned_entries = handle_object(source=source, current_location=location)

    assert returned_entries == expected_entries
    assert location == expected_location


HANDLE_OBJECT_ERROR_TESTS = [
    pytest.param("", Location(0, 1, 1), id="location after end"),
    pytest.param(f"{END_OBJECT}", Location(0, 0, 0), id="no start object"),
    pytest.param(f"{BEGIN_OBJECT}", Location(0, 0, 0), id="no end object"),
    pytest.param(
        f"{BEGIN_OBJECT}{QUOTATION_MARK}{QUOTATION_MARK}",
        Location(0, 0, 0),
        id="no end object with value",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{QUOTATION_MARK}{QUOTATION_MARK}{SPACE}",
        Location(0, 0, 0),
        id="no end object with value and whitespace",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{BEGIN_OBJECT}{END_OBJECT}",
        Location(0, 0, 0),
        id=f"invalid control character {BEGIN_OBJECT}",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{BEGIN_ARRAY}{END_OBJECT}",
        Location(0, 0, 0),
        id=f"invalid control character {BEGIN_ARRAY}",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{END_ARRAY}{END_OBJECT}",
        Location(0, 0, 0),
        id=f"invalid control character {END_ARRAY}",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{NAME_SEPARATOR}{END_OBJECT}",
        Location(0, 0, 0),
        id=f"invalid control character {NAME_SEPARATOR}",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{QUOTATION_MARK}{QUOTATION_MARK}{SPACE}{END_OBJECT}",
        Location(0, 0, 0),
        id="missing name separator",
    ),
    pytest.param(
        f"{BEGIN_OBJECT}{QUOTATION_MARK}{QUOTATION_MARK}{NAME_SEPARATOR}",
        Location(0, 0, 0),
        id="name separator end",
    ),
]


@pytest.mark.parametrize(
    "source, location",
    HANDLE_OBJECT_ERROR_TESTS,
)
def test_handle_object_error(source, location):
    """
    GIVEN source and location
    WHEN handle_object is called with the source and location
    THEN InvalidJsonError is raised.
    """
    with pytest.raises(InvalidJsonError):
        handle_object(source=source, current_location=location)


HANDLE_ARRAY_TESTS = [
    pytest.param(
        f"{BEGIN_ARRAY}{END_ARRAY}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="empty",
    ),
    pytest.param(
        f"{SPACE}{BEGIN_ARRAY}{END_ARRAY}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="empty whitespace before",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{SPACE}{END_ARRAY}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3)))],
        Location(0, 3, 3),
        id="empty whitespace between",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{END_ARRAY}{SPACE}",
        Location(0, 0, 0),
        [("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 2, 2)))],
        Location(0, 2, 2),
        id="empty whitespace after",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 3, 3))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2))),
        ],
        Location(0, 3, 3),
        id="single value",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{SPACE}0{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4))),
            ("/0", Entry(value_start=Location(0, 2, 2), value_end=Location(0, 3, 3))),
        ],
        Location(0, 4, 4),
        id="single value whitespace before",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0{SPACE}{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2))),
        ],
        Location(0, 4, 4),
        id="single value whitespace after",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0,{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 4, 4))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2))),
        ],
        Location(0, 4, 4),
        id="single value separator",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0,0{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 5, 5))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2))),
            ("/1", Entry(value_start=Location(0, 3, 3), value_end=Location(0, 4, 4))),
        ],
        Location(0, 5, 5),
        id="multi value",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0,0,0{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 7, 7))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 2, 2))),
            ("/1", Entry(value_start=Location(0, 3, 3), value_end=Location(0, 4, 4))),
            ("/2", Entry(value_start=Location(0, 5, 5), value_end=Location(0, 6, 6))),
        ],
        Location(0, 7, 7),
        id="many value",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{BEGIN_ARRAY}0{END_ARRAY}{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 5, 5))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 4, 4))),
            ("/0/0", Entry(value_start=Location(0, 2, 2), value_end=Location(0, 3, 3))),
        ],
        Location(0, 5, 5),
        id="nested array",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}{BEGIN_OBJECT}"
        f"{QUOTATION_MARK}key{QUOTATION_MARK}{NAME_SEPARATOR}0"
        f"{END_OBJECT}{END_ARRAY}",
        Location(0, 0, 0),
        [
            ("", Entry(value_start=Location(0, 0, 0), value_end=Location(0, 11, 11))),
            ("/0", Entry(value_start=Location(0, 1, 1), value_end=Location(0, 10, 10))),
            (
                "/0/key",
                Entry(
                    value_start=Location(0, 8, 8),
                    value_end=Location(0, 9, 9),
                    key_start=Location(0, 2, 2),
                    key_end=Location(0, 7, 7),
                ),
            ),
        ],
        Location(0, 11, 11),
        id="nested object",
    ),
]


@pytest.mark.parametrize(
    "source, location, expected_entries, expected_location",
    HANDLE_ARRAY_TESTS,
)
def test_handle_array(source, location, expected_entries, expected_location):
    """
    GIVEN source, location and expected entries and location
    WHEN handle_array is called with the source and location
    THEN the expected entries are returned and the location is at the expected location.
    """
    returned_entries = handle_array(source=source, current_location=location)

    assert returned_entries == expected_entries
    assert location == expected_location


HANDLE_ARRAY_ERROR_TESTS = [
    pytest.param("", Location(0, 1, 1), id="location after end"),
    pytest.param(f"{END_ARRAY}", Location(0, 0, 0), id="no start array"),
    pytest.param(f"{BEGIN_ARRAY}{END_OBJECT}", Location(0, 0, 0), id="no end array"),
    pytest.param(f"{BEGIN_ARRAY}0", Location(0, 0, 0), id="no end array with value"),
    pytest.param(
        f"{BEGIN_ARRAY}0{NAME_SEPARATOR}{END_ARRAY}",
        Location(0, 0, 0),
        id="invalid name separator character",
    ),
    pytest.param(
        f"{BEGIN_ARRAY}0{END_OBJECT}{END_ARRAY}",
        Location(0, 0, 0),
        id="invalid object end character",
    ),
]


@pytest.mark.parametrize(
    "source, location",
    HANDLE_ARRAY_ERROR_TESTS,
)
def test_handle_array_error(source, location):
    """
    GIVEN source and location
    WHEN handle_array is called with the source and location
    THEN InvalidJsonError is raised.
    """
    with pytest.raises(InvalidJsonError):
        handle_array(source=source, current_location=location)


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


HANDLE_PRIMITIVE_ERROR_TESTS = [
    pytest.param("", Location(0, 1, 1), id="location after end"),
    pytest.param(f"{QUOTATION_MARK}", Location(0, 0, 0), id="quote without closing"),
]


@pytest.mark.parametrize(
    "source, location",
    HANDLE_PRIMITIVE_ERROR_TESTS,
)
def test_handle_primitive_error(source, location):
    """
    GIVEN source and location
    WHEN handle_primitive is called with the source and location
    THEN InvalidJsonError is raised.
    """
    with pytest.raises(InvalidJsonError):
        handle_primitive(source=source, current_location=location)
