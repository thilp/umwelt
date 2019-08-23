import pytest
import typing as t

import umwelt


@pytest.mark.parametrize(
    "annot, example, expected",
    [
        (t.Sequence[str], '["x", "y"]', ["x", "y"]),
        (t.Sequence, '["x", 1]', ["x", 1]),
        (t.Mapping[int, t.Sequence[int]], '{"1":[2,"3"]}', {1: [2, 3]}),
    ],
)
def test_abc_are_instantiated_via_concrete_subtypes(annot, example, expected):
    class Config:
        x: annot

    src = {"X": example}

    conf = umwelt.new(Config, source=src)
    assert conf.x == expected
