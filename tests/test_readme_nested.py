from __future__ import annotations

import dataclasses

from pydantic import UrlStr

import umwelt


class MyConfig:
    db: DbConfig
    host: UrlStr = "http://b.org"


@umwelt.subconfig
class DbConfig:
    port: int
    debug: bool = False


def test_readme_nested(monkeypatch):
    monkeypatch.setenv("APP_DB_PORT", "32")

    config = umwelt.new(MyConfig, prefix="app")

    assert dataclasses.is_dataclass(config)
    assert config.host == "http://b.org"
    assert config.db.port == 32
