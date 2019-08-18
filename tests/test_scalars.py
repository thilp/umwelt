from decimal import Decimal
from fractions import Fraction

import pytest

import umwelt


@pytest.fixture
def cls():
    class Config:
        a_str: str
        a_int: int
        a_bool: bool
        a_float: float
        a_bytes: bytes
        a_complex: complex
        a_decimal: Decimal
        a_fraction: Fraction

    return Config


@pytest.fixture
def source():
    return dict(
        A_STR="a",
        A_INT="1",
        A_BOOL="True",
        A_FLOAT="0.1",
        A_BYTES="a\0b",
        A_COMPLEX="1+2j",
        A_DECIMAL="0.1",
        A_FRACTION="1/3",
    )


def test_return_type(cls, source):
    c = umwelt.new(cls, source=source)
    assert isinstance(c, cls)


@pytest.mark.parametrize(
    "field, transform",
    [
        ("a_str", lambda x: x),
        ("a_int", int),
        ("a_bool", bool),
        ("a_float", float),
        ("a_complex", complex),
        ("a_decimal", Decimal),
        ("a_fraction", Fraction),
    ],
)
def test_attr_value(field: str, transform: callable, cls, source):
    c = umwelt.new(cls, source=source)
    assert getattr(c, field) == transform(source[field.upper()])


def test_attr_value_bytes(cls, source):
    c = umwelt.new(cls, source=source)
    assert c.a_bytes == source["A_BYTES"].encode()
