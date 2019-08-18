from typing import List, Set, Dict, Tuple, FrozenSet

import pydantic
import pytest
import umwelt


@pytest.mark.parametrize(
    "t, example, expected",
    [
        (list, '[1, "b"]', [1, "b"]),
        (List[str], '["ab","cd"]', ["ab", "cd"]),
        (List[int], "[1, 2]", [1, 2]),
        (List[list], '[[1, "a"], [2, "b"]]', [[1, "a"], [2, "b"]]),
        (List[List[str]], '[["a"],["b"]]', [["a"], ["b"]]),
        (List[List[int]], "[[1],[2]]", [[1], [2]]),
        (set, '[1, "b"]', {1, "b"}),
        (Set[str], '["a","b"]', {"a", "b"}),
        (Set[int], "[1, 2]", {1, 2}),
        (frozenset, '[1, "b"]', frozenset([1, "b"])),
        (tuple, '[1, "b"]', (1, "b")),
        (Tuple[int, str], '[1, "b"]', (1, "b")),
        (Tuple[str, ...], '["ab","cd"]', ("ab", "cd")),
        (Tuple[str], '["a"]', ("a",)),
        (Tuple[str, str], '["a", "b"]', ("a", "b")),
        (Tuple[int, ...], "[1, 2]", (1, 2)),
        (Tuple[int], "[1]", (1,)),
        (Tuple[int, int], "[1, 2]", (1, 2)),
        (Tuple[tuple, ...], '[[1, "a"], [2, "b"]]', ((1, "a"), (2, "b"))),
        (Tuple[tuple], '[[1, "a"]]', ((1, "a"),)),
        (Tuple[tuple, tuple], "[[1], [2]]", ((1,), (2,))),
        (Tuple[Tuple[int, ...], ...], "[[1, 3, 5],[2, 4]]", ((1, 3, 5), (2, 4))),
        (Tuple[Tuple[int, ...]], "[[1,2]]", ((1, 2),)),
        (Tuple[Tuple[int, ...], Tuple[int, ...]], "[[1,2],[3]]", ((1, 2), (3,))),
        (Tuple[Tuple[int], ...], "[[1],[2]]", ((1,), (2,))),
        (Tuple[Tuple[int, int], ...], "[[1,2],[3,4],[5,6]]", ((1, 2), (3, 4), (5, 6))),
        (Tuple[Tuple[int]], "[[1]]", ((1,),)),
        (Tuple[Tuple[int], Tuple[int]], "[[1],[2]]", ((1,), (2,))),
        (Tuple[Tuple[int, int]], "[[1, 2]]", ((1, 2),)),
        (Tuple[Tuple[int, int], Tuple[int, int]], "[[1, 2],[3,4]]", ((1, 2), (3, 4))),
        (dict, '{"a":1, "b": 2,"3":"c"}', {"a": 1, "b": 2, "3": "c"}),
        (Dict[str, str], '{"a":"b"}', {"a": "b"}),
        (Dict[str, int], '{"a":2}', {"a": 2}),
        (Dict[int, int], '{"1":2}', {1: 2}),
        (Dict[str, dict], '{"a":{"b":1,"2":"c"}}', {"a": {"b": 1, "2": "c"}}),
        (Dict[str, Dict[str, bytes]], '{"a":{"b":"c"}}', {"a": {"b": b"c"}}),
        (Dict[str, Dict[str, int]], '{"a":{"b":1}}', {"a": {"b": 1}}),
        (Dict[str, Dict[int, int]], '{"a":{"1":2}}', {"a": {1: 2}}),
        (Dict[int, Dict[int, int]], '{"1":{"2":3}}', {1: {2: 3}}),
    ],
)
def test_attr_value(t, example, expected):
    class Config:
        x: t

    source = {"X": example}
    assert umwelt.new(Config, source=source).x == expected


@pytest.mark.xfail(
    condition=pydantic.VERSION.version[0] < 1,
    reason="https://github.com/samuelcolvin/pydantic/issues/745",
    strict=True,  # makes XPASS a failure
)
@pytest.mark.parametrize(
    "t, example, expected",
    [
        (
            Set[frozenset],
            '[[1,"a"],[2,"b"]]',
            {frozenset([1, "a"]), frozenset([2, "b"])},
        ),
        (Set[FrozenSet[str]], '[["a"],["b"]]', {frozenset(["a"]), frozenset(["b"])}),
        (Set[FrozenSet[int]], "[[1],[2]]", {frozenset([1]), frozenset([2])}),
        (FrozenSet[str], '["a","b"]', frozenset(["a", "b"])),
        (FrozenSet[int], "[1,2]", frozenset([1, 2])),
        (
            FrozenSet[frozenset],
            '[[1,"a"],[2,"b"]]',
            frozenset([frozenset([1, "a"]), frozenset([2, "b"])]),
        ),
        (
            FrozenSet[FrozenSet[str]],
            '[["a"],["b"]]',
            frozenset([frozenset(["a"]), frozenset(["b"])]),
        ),
        (
            FrozenSet[FrozenSet[int]],
            "[[1],[2]]",
            frozenset([frozenset([1]), frozenset([2])]),
        ),
    ],
)
def test_frozenset(t, example, expected):
    class Config:
        x: t

    source = {"X": example}
    assert umwelt.new(Config, source=source).x == expected
