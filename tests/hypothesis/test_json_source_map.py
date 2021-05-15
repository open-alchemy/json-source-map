"""Many generated tests for JSON source map functions."""

import json
import string

import hypothesis
from hypothesis import strategies

from json_source_map import calculate

json_strategy = strategies.recursive(
    strategies.none()
    | strategies.booleans()
    | strategies.floats()
    | strategies.text(string.printable),
    lambda children: strategies.lists(children, min_size=0)
    | strategies.dictionaries(strategies.text(string.printable), children, min_size=0),
)


@hypothesis.given(json_strategy)
def test_calculate(source):
    """
    GIVEN source
    WHEN calculate is called with the source
    THEN the expected source map is returned.
    """
    source_str = json.dumps(source)

    calculate(source_str)
