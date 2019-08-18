from dataclasses import dataclass
from typing import Any


class UmweltError(RuntimeError):
    """Base class for all exceptions raised by Umwelt."""


@dataclass(frozen=True)
class MissingKeyError(UmweltError):
    """Raised when a required key-value pair is not provided in the source."""

    name: str

    def __str__(self) -> str:
        return f"missing required key: {self.name!r}"


@dataclass(frozen=True)
class ConversionError(UmweltError):
    """
    Raised by decoders when an input string cannot be used to instantiate
    the specified type.
    """

    value: str
    target: Any

    def __str__(self) -> str:
        if isinstance(self.target, type):
            t = self.target.__name__
        else:
            t = str(self.target)
        return f"can't build a {t} from invalid literal: {self.value!r}"
