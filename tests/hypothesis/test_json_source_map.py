"""Many generated tests for JSON source map functions."""

import json
import string
import subprocess

import hypothesis
from hypothesis import strategies

from json_source_map import calculate

json_strategy = strategies.recursive(
    strategies.none()
    | strategies.booleans()
    | strategies.floats(allow_infinity=False, allow_nan=False)
    | strategies.text(string.ascii_letters),
    lambda children: strategies.lists(children, min_size=0, max_size=5)
    | strategies.dictionaries(
        strategies.text(string.ascii_letters), children, min_size=0, max_size=5
    ),
)


@hypothesis.given(json_strategy)
def test_calculate(source):
    """
    GIVEN source
    WHEN calculate is called with the source
    THEN the expected source map is returned.
    """
    source_str = json.dumps(source)

    returned_source_map = calculate(source_str)
    returned_source_map = dict(
        map(lambda item: (item[0], item[1].to_dict()), returned_source_map.items())
    )

    # Also calculate using reference implementation in Node
    process = subprocess.run(
        ["node", "index.js", source_str], capture_output=True, check=True
    )
    expected_source_map = json.loads(process.stdout)
    assert returned_source_map == expected_source_map
