# Umwelt

[dataclasses]: https://docs.python.org/3/library/dataclasses.html
[pydantic]: https://pydantic-docs.helpmanual.io/

Describe a configuration schema with [dataclasses][] or [pydantic][] and
load values from the environment, in a static-typing-friendly way.

## Examples

### Flat

```python
>>> os.environ["APP_HOSTS"] = '["b.org","sky.net"]'
>>> os.environ["APP_TOKEN"] = "very secret"
```

```python
from typing import Sequence
from pydantic import SecretStr
import umwelt

class MyConfig:
    hosts: Sequence[str]
    token: SecretStr
    replicas: int = 2

config = umwelt.new(MyConfig, prefix="app")
```

```python
>>> dataclasses.is_dataclass(config)
True
>>> config.hosts
["b.org", "sky.net"]
>>> config.token
SecretStr('**********')
>>> config.replicas
2
```

### Nested

```python
>>> os.environ["APP_DB_PORT"] = "32"
```

```python
from __future__ import annotations  # for forward-references
from pydantic import UrlStr
import umwelt

class MyConfig:
    db: DbConfig
    host: UrlStr = "http://b.org"

@umwelt.subconfig
class DbConfig:
    port: int
    debug: bool = False

config = umwelt.new(MyConfig, prefix="app")
```

```python
>>> config.host
"http://b.org"
>>> config.db.port
32
```

## Install

```shell script
$ pip install umwelt
```

## Features

### umwelt.new

`umwelt.new` expects one positional argument: the config class to fill.
Umwelt will convert it into a [dataclass][dataclasses] if it's not one already.

`umwelt.new` also accepts named arguments:
- **`source`** (by default `os.environ`) is a `Mapping[str, str]` from which
values are extracted.
- **`prefix`** can be a string or a callable. As a string, it is prepended to
the config field's name. As a callable, it receives the config field's name and
its result is the source key name.
- **`decoder`** is a callable expecting a type and a string, and returns a
conversion of that string in that type, or in a type that pydantic can convert
in that type.
For example, when umwelt's default `decoder` is called with (`List[Set[int]]`,
`"[[1]]"`), it simply decodes the string from JSON and hence returns a list of
_lists_, which pydantic properly converts into a list of _sets_. 

### @umwelt.subconfig

`@umwelt.subconfig` tags classes so that, when they appear as field annotations
in another config class, `umwelt.new` doesn't instantiate them from a single
`source` value, but rather from one `source` value _per class field_.

Example:

```python
class Point:                              # no @subconfig
    def __init__(self, s: str):           # string input
        self.x, self.y = s.split(",", 1)  # arbitrary implementation

class MyConf:
    point: Point

conf = umwelt.new(MyConf, source={"POINT": "1,2"})  # one source entry
conf.point  # <Point at 0x7f07b1d04750>
```

`conf.point` is an instance of _Point_, built by passing the input value `"1,2"`
directly to `Point.__new__`.
There is only one `source` key: `POINT`.

Now compare with `@umwelt.subconfig`:

```python
@umwelt.subconfig
class Point:
    x: int
    y: int

class MyConf:
    point: Point

conf = umwelt.new(MyConf, source={"POINT_X": "1", "POINT_Y": "2"})
conf.point  # Point(x=1, y=2)
```

`conf.point` is still an instance of _Point_ (_Point_ has been made a
dataclass by Umwelt, hence the automatic `__str__` implementation).
There are **two** `source` keys: `POINT_X` and `POINT_Y`, each corresponding to
a field of the _Point_ class.

## Comparison with Ecological

I've used [Ecological][] for a long time.
Today, a large part of Ecological's codebase implements features already found
in [dataclasses][] and [pydantic][], which are more mature.
I believe Ecological's design can be dramatically simplified _and_ improved by
enforcing a strict separation of concerns:

- class scaffolding is the responsibility of [dataclasses][] (which, compared
  to metaclasses, is simpler, more introspectable, and comes with helpers like
  `asdict`);
- type coercion and validation is the responsibility of [pydantic][] (which has
  more features, e.g. nested data types, JSON Schema, serialization, etc.);
- mapping a [pydantic][] schema (the configuration class) to a string-to-string
  dict (like `os.environ`) is the responsibility of Umwelt.

Some compatibility-breaking decisions prevent from doing this in Ecological:

- Don't autoload configuration values, especially not at class definition time.
  Instead, offer just one function (`umwelt.new`) that loads the configuration
  when it is called.
- Don't tie variable prefixes to configuration classes, as that doesn't play
  well with nested configurations.

[ecological]: https://github.com/jmcs/ecological
[autoloading]: https://github.com/jmcs/ecological/issues/20
