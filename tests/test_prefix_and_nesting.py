from dataclasses import dataclass

import pytest

import umwelt


@pytest.mark.parametrize(
    "prefix, key",
    [
        ("", "X"),
        ("P", "P_X"),
        ("PREF", "PREF_X"),
        ("P_", "P_X"),
        ("A_B", "A_B_X"),
        ("A_B_", "A_B_X"),
        ("A_B__", "A_B__X"),
        ("_", "_X"),
        ("A B", "A B_X"),
    ],
)
def test_prefixes(prefix, key):
    class Config:
        x: str

    source = {key: "hi"}
    assert umwelt.new(Config, source=source, prefix=prefix).x == "hi"


def test_nesting_without_prefix():
    @dataclass
    class A:
        x: str

    @dataclass
    class B:
        y: str
        z: A

    source = {"Y": "foo", "Z_X": "bar"}
    assert umwelt.new(B, source=source) == B(y="foo", z=A(x="bar"))


def test_nesting_with_prefix():
    @dataclass
    class A:
        x: str

    @dataclass
    class B:
        y: str
        z: A

    source = {"P_Y": "foo", "P_Z_X": "bar"}
    assert umwelt.new(B, source=source, prefix="P") == B(y="foo", z=A(x="bar"))
