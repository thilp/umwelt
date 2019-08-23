import collections.abc
import dataclasses
import json
from typing import Type, TypeVar

import pydantic

from umwelt.errors import ConversionError

T = TypeVar("T")

TUPLE_LIKE_ABCS = (
    collections.abc.Sized,
    collections.abc.Iterable,
    collections.abc.Container,
)


def jsonlike_decoder(t: Type[T], s: str) -> T:
    """
    Decodes a superset of JSON.

    Supports:
        - all JSON syntax,
        - boolean literals: all case variants of "true", "false", "t", and "f".

    JSON types are mapped to Python types as follows:
        - boolean: bool
        - null: None
        - number: int, float
        - string: str, bytes, Decimal, complex, Fraction
        - array: list, tuple, set
        - object: dict
    """
    t = getattr(t, "__origin__", t)
    try:
        if issubclass(t, str) or t in (pydantic.SecretStr, pydantic.SecretBytes):
            return s
        if t is bool:
            return _as_bool(s)
        if t is bytes:
            return str.encode(s)
        if (
            t in (list, dict, set, frozenset, tuple)
            or issubclass(t, TUPLE_LIKE_ABCS)
            or dataclasses.is_dataclass(t)
        ):
            return json.loads(s)
        return t(s)
    except Exception as err:
        raise ConversionError(value=s, target=t) from err


def _as_bool(s: str) -> bool:
    normalized = s.lower()
    if normalized in ("true", "t", "1"):
        return True
    if normalized in ("false", "f", "0"):
        return False
    raise ValueError(f"invalid literal for bool: {s!r}")
