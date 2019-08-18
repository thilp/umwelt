import dataclasses
from dataclasses import is_dataclass
import os
from typing import TypeVar, Type, Mapping, Union, Callable, Any

from pydantic.dataclasses import dataclass

from umwelt.errors import MissingKeyError
from umwelt.decoders.jsonlike import jsonlike_decoder

T = TypeVar("T")

Prefixer = Callable[[str], str]

Decoder = Callable[[Type[T], str], T]


def new(
    cls: Type[T],
    *,
    source: Mapping[str, str] = os.environ,
    prefix: Union[str, Prefixer] = "",
    decoder: Decoder = jsonlike_decoder,
    frozen: bool = True,
) -> T:
    if not is_dataclass(cls):
        cls = dataclass(cls, frozen=frozen, config=_PydanticConfig)

    prefixer = _build_prefixer(prefix)

    kwargs = {}
    for field in dataclasses.fields(cls):
        kwargs[field.name] = _load_field_value(field, source, prefixer, decoder)

    return cls(**kwargs)


def _load_field_value(
    field: dataclasses.Field,
    source: Mapping[str, str],
    prefixer: Prefixer,
    decoder: Decoder,
) -> Any:
    if is_dataclass(field.type):  # conf nesting
        return new(
            field.type,
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
        return decoder(field.type, raw)


def _build_prefixer(prefix):
    if callable(prefix):
        return prefix
    if prefix:
        if prefix.endswith("_"):
            prefix = prefix[:-1]
        return lambda x: f"{prefix}_{x}".upper()
    return str.upper


class _PydanticConfig:
    arbitrary_types_allowed = True
