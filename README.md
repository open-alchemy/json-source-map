# JsonSourceMap

Calculate JSON Pointers to each value within a JSON document along with the
line, column and character position for the start and end of that value. For
more information see: <https://github.com/open-alchemy/json-source-map/wiki>.

For example:

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

The following features have been implemented:

- support for primitive types (`strings`, `numbers`, `booleans` and `null`),
- support for structural types (`array` and `object`) and
- support for space, tab, carriage and return whitespace.
