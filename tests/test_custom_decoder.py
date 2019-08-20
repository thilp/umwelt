from dataclasses import dataclass
from fractions import Fraction

import pytest

import umwelt


class WeirdPoint:
    # Constructor that pydantic can't plan for.
    def __init__(self, f: Fraction) -> None:
        self.x = f.numerator
        self.y = f.denominator

    def __eq__(self, o: object) -> bool:
        return isinstance(o, type(self)) and (o.x, o.y) == (self.x, self.y)


@dataclass
class DataclassPoint:
    x: int
    y: int


@umwelt.subconfig
class ConfigPoint:
    x: int
    y: int


def weird_point_decoder(_, s: str):
    return WeirdPoint(Fraction(s))


class TestCustomConstructor:
    class Conf:
        point: WeirdPoint

    def test_without_custom_decoder(self):
        with pytest.raises(umwelt.ConversionError):
            umwelt.new(self.Conf, source={"POINT": "1/2"})

    def test_with_custom_decoder(self):
        conf = umwelt.new(
            self.Conf, source={"POINT": "1/2"}, decoder=weird_point_decoder
        )
        assert conf.point == WeirdPoint(Fraction("1/2"))


class TestDataclass:
    class Conf:
        point: DataclassPoint

    def test_without_custom_decoder(self):
        with pytest.raises(umwelt.ConversionError):
            umwelt.new(self.Conf, source={"POINT": "(1,2)"})


class TestSubconfig:
    class Conf:
        point: ConfigPoint

    def test_without_custom_decoder(self):
        conf = umwelt.new(self.Conf, source={"POINT_X": "1", "POINT_Y": "2"})
        assert conf.point.x == 1
        assert conf.point.y == 2
