import contextlib
import math
import re
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest

import umwelt
from umwelt import errors


def cm(result: Any):
    if isinstance(result, type) and issubclass(result, BaseException):
        return pytest.raises(result)
    if isinstance(result, BaseException):
        return pytest.raises(type(result), match=re.escape(str(result)))
    return contextlib.nullcontext()


@pytest.mark.parametrize("example, result", [("", ""), ("a", "a"), ("a B", "a B")])
def test_strings(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: str

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [
        ("True", True),
        ("False", False),
        ("x", errors.ConversionError(value="x", target=bool)),
        ("true", True),
        ("false", False),
        ("TRUE", True),
        ("FALSE", False),
        ("t", True),
        ("f", False),
        ("1", True),
        ("0", False),
        ("2", errors.ConversionError(value="2", target=bool)),
    ],
)
def test_booleans(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: bool

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [
        ("1", 1),
        ("1.2", errors.ConversionError(value="1.2", target=int)),
        ("-1", -1),
        ("123456789", 123456789),
        ("123_456_789", 123456789),
    ],
)
def test_ints(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: int

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [
        ("1", 1.0),
        ("1.2", 1.2),
        ("-1", -1.0),
        ("-1.3", -1.3),
        ("nan", math.nan),
        ("123_456_789", 123456789),
    ],
)
def test_floats(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: float

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        if math.isnan(result):
            assert math.isnan(conf.x)
        elif math.isinf(result):
            assert math.isinf(conf.x)
        else:
            assert conf.x == result


@pytest.mark.parametrize(
    "example, result", [("ab", b"ab"), ("", b""), ("é", b"\xc3\xa9")]
)
def test_bytes(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: bytes

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [
        ("1+j", complex(1, 1)),
        ("1+i", errors.ConversionError),
        ("", errors.ConversionError),
    ],
)
def test_complex(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: complex

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [("0", Decimal(0)), ("x", errors.ConversionError), ("", errors.ConversionError)],
)
def test_decimal(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: Decimal

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result


@pytest.mark.parametrize(
    "example, result",
    [
        ("0", Fraction(0)),
        ("0/1", Fraction(0)),
        ("1/2", Fraction(1, 2)),
        ("1/0", errors.ConversionError),
        ("x", errors.ConversionError),
        ("", errors.ConversionError),
    ],
)
def test_fraction(example: str, result: Any):
    src = {"X": example}

    @dataclass
    class Conf:
        x: Fraction

    with cm(result):
        conf = umwelt.new(Conf, source=src)
        assert conf.x == result
