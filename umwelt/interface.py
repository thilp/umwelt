import dataclasses
import os
import sys
import typing
from dataclasses import is_dataclass
from typing import TypeVar, Type, Mapping, Union, Callable, Any

import pydantic.dataclasses

from umwelt.decoders.jsonlike import jsonlike_decoder
from umwelt.errors import MissingKeyError

T = TypeVar("T")

Prefixer = Callable[[str], str]

D = TypeVar("D")
Decoder = Callable[[Type[D], str], D]


def new(
    cls: Type[T],
    *,
    source: Mapping[str, str] = os.environ,
    prefix: Union[str, Prefixer] = "",
    decoder: Decoder = jsonlike_decoder,
) -> T:
    """
    Instantiates *cls* by fetching a key-value pair from *source* (by default,
    ``os.environ``) for each *cls* field.
    Each key is a combination of *prefix* and the field's name.
    Each value is converted from string to a Python object using *decoder*, then
    coerced and validated by pydantic.
    """
    if not is_dataclass(cls):
        cls = pydantic.dataclasses.dataclass(cls, frozen=True, config=_PydanticConfig)

    prefixer = _build_prefixer(prefix)

    kwargs = {}
    resolved_annotations = None
    for field in dataclasses.fields(cls):
        if isinstance(field.type, str):  # deal with string annotations
            if resolved_annotations is None:
                resolved_annotations = typing.get_type_hints(
                    cls, sys.modules[cls.__module__].__dict__
                )
            resolved_field_type = resolved_annotations[field.name]
        else:
            resolved_field_type = field.type

        kwargs[field.name] = _load_field_value(
            resolved_field_type, field, source, prefixer, decoder
        )

    return cls(**kwargs)


def subconfig(cls: Type[T]) -> Type[T]:
    """
    Decorates configuration schema classes.

    Technically, this is only necessary if you use nested configuration classes,
    as Umwelt needs a way to distinguish them from "normal" classes that must
    be instantiated via pydantic with the value of a single environment variable.
    """
    cls.__umwelt__ = True
    return cls


def _load_field_value(
    resolved_field_type,
    field: dataclasses.Field,
    source: Mapping[str, str],
    prefixer: Prefixer,
    decoder: Decoder,
) -> Any:
    if hasattr(resolved_field_type, "__umwelt__"):  # conf nesting
        return new(
            resolved_field_type,
            source=source,
            prefix=lambda x: prefixer(f"{field.name}_{x}"),
            decoder=decoder,
        )
    key = prefixer(field.name)
    try:
        raw = source[key]
    except KeyError:
        if field.default is dataclasses.MISSING:
            raise MissingKeyError(name=key) from None
        return field.default
    else:
        return decoder(resolved_field_type, raw)


def _build_prefixer(prefix):
    if callable(prefix):
        return prefix
    if prefix:
        if prefix.endswith("_"):
            prefix = prefix[:-1]
        return lambda x: f"{prefix}_{x}".upper()
    return str.upper


class _PydanticConfig(pydantic.BaseConfig):
    arbitrary_types_allowed = True
