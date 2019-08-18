import dataclasses
import json
import os
from typing import TypeVar, Type, Mapping, Union, Callable

from pydantic.dataclasses import dataclass

T = TypeVar("T")


class UmweltError(RuntimeError):
    """Base class for all exceptions raised by Umwelt."""


class MissingValueError(UmweltError):
    """Raised when a required value is not provided."""


Prefixer = Callable[[str], str]

Decoder = Callable[[Type[T], str], T]


def _jsonlike_decoder(t: Type[T], s: str) -> T:
    """
    Returns a function that can convert a string into a Python object that
    pydantic can later convert into an instance of *t*.
    """
    t = getattr(t, "__origin__", t)
    if t in (list, dict, set, frozenset, tuple):
        return t(json.loads(s))
    if t is bytes:
        return str.encode(s)
    return t(s)


def new(
    cls: Type[T],
    *,
    source: Mapping[str, str] = os.environ,
    prefix: Union[str, Prefixer] = "",
    decoder: Decoder = _jsonlike_decoder,
) -> T:
    if not dataclasses.is_dataclass(cls):
        cls = dataclass(cls, frozen=True, config=_PydanticConfig)

    if callable(prefix):
        prefixer = prefix
    else:
        prefixer = (lambda x: f"{prefix}_{x}".upper()) if prefix else str.upper

    kwargs = {}
    for field in dataclasses.fields(cls):
        print("field =", field)
        key = prefixer(field.name)
        raw = source.get(key, _MISSING)
        if raw is _MISSING:
            if field.default is dataclasses.MISSING:
                raise MissingValueError(key)
            kwargs[field.name] = field.default
        else:
            kwargs[field.name] = decoder(field.type, raw)

    return cls(**kwargs)


class _PydanticConfig:
    arbitrary_types_allowed = True


_MISSING = object()
