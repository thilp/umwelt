from __future__ import annotations

import pytest

import umwelt


class TopLevelConf:
    db: TopLevelDbConf


@umwelt.subconfig
class TopLevelDbConf:
    port: int


def test_top_level():
    config = umwelt.new(TopLevelConf, source={"DB_PORT": "2"})
    assert config.db.port == 2


@pytest.mark.xfail(
    reason="Can't easily locate the definition scope of a nested class; "
    "https://bugs.python.org/issue33453"
)
def test_nested_in_function():
    class NestedConf:
        db: NestedDbConf

    @umwelt.subconfig
    class NestedDbConf:
        port: int

    config = umwelt.new(NestedConf, source={"DB_PORT": "2"})
    assert config.db.port == 2
