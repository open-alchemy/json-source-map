"""Tests for JsonSourceMap."""

import pytest

from json_source_map import calculate, errors

CALCULATE_TESTS = [pytest.param("", {}, id="empty")]


@pytest.mark.parametrize("source, expected_source_map", CALCULATE_TESTS)
def test_calculate(source, expected_source_map):
    """
    GIVEN source and expected source map
    WHEN calculate is called with the source
    THEN the source map is returned.
    """
    returned_source_map = calculate(source)

    assert returned_source_map == expected_source_map


def test_calculate_source_not_string():
    """
    GIVEN source that is not a string
    WHEN calculate is called with the source
    THEN InvalidInputError is raised.
    """
    source = True

    with pytest.raises(errors.InvalidInputError):
        calculate(source)
