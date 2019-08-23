import dataclasses


def test_readme_simple(monkeypatch):
    monkeypatch.setenv("APP_HOSTS", '["b.org","sky.net"]')
    monkeypatch.setenv("APP_TOKEN", "very secret")

    from typing import Sequence
    from pydantic import SecretStr
    import umwelt

    class MyConfig:
        hosts: Sequence[str]
        token: SecretStr
        replicas: int = 2

    config = umwelt.new(MyConfig, prefix="app")

    assert dataclasses.is_dataclass(config)
    assert config.hosts == ["b.org", "sky.net"]
    assert str(config.token) == "SecretStr('**********')"
    assert config.replicas == 2
