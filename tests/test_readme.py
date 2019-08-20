import dataclasses


def test_readme(monkeypatch):
    monkeypatch.setenv("APP_DB_PORT", "32")

    import umwelt
    from typing import Tuple
    from pydantic import UrlStr

    @umwelt.subconfig
    class DbConfig:
        port: int

    class MyConfig:
        db: DbConfig
        hosts: Tuple[UrlStr, ...] = ("http://b.org", "http://sky.net")

    config = umwelt.new(MyConfig, prefix="app")

    assert dataclasses.is_dataclass(config)
    assert config.hosts == ("http://b.org", "http://sky.net")
    assert config.db.port == 32
