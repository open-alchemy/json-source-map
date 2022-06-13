# JsonSourceMap

Calculate JSON Pointers to each value within a JSON document along with the
line, column and character position for the start and end of that value. For
more information see: <https://github.com/open-alchemy/json-source-map/wiki>.

For example:

```bash
python -m pip install json_source_map
```

```Python
from json_source_map import calculate


print(calculate('{"foo": "bar"}'))
```

The above prints:

```Python
{
    '': Entry(
        value_start=Location(line=0, column=0, position=0),
        value_end=Location(line=0, column=14, position=14),
        key_start=None,
        key_end=None,
    ),
    '/foo': Entry(
        value_start=Location(line=0, column=8, position=8),
        value_end=Location(line=0, column=13, position=13),
        key_start=Location(line=0, column=1, position=1),
        key_end=Location(line=0, column=6, position=6),
    ),
}
```

Where:

- each key in the dictionary is a JSON path to an item,
- each value in the dictionarty contains the mapping of the item at the JSON
  path which have the following properties:
  - `value_start` is the start of the value,
  - `value_end` is the end of the value,
  - `key_start` is the start of the key (which is `None` at the root level and
    for array items),
  - `key_end` is the end of the key (which is `None` at the root level and for
    array items) and
- each of the above have the following properties:
  - `line` is the zero-indexed line position,
  - `column` is the zero-indexed column position and
  - `position` is the zero-indexed character position in the string
    (independent of the line and column).

The following features have been implemented:

- support for primitive types (`strings`, `numbers`, `booleans` and `null`),
- support for structural types (`array` and `object`) and
- support for space, tab, carriage and return whitespace.
