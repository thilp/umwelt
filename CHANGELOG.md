# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Calendar Versioning](http://calver.org).

## [Unreleased][]

### Fixed

- Annotations provided as strings (explicitly or under the influence of
  `from __future__ import annotations`) are resolved into the corresponding
  Python types.
  However, this only works when these types are defined at the module level
  (i.e. not in methods or classes).

## [2019.8.1][] - 2019-08-21

### Added

- Fill [pydantic][] schema classes with values extracted from `os.environ` or
  another provided dictionary.
- `@subconfig` allows to unambiguously tag schema classes on which Umwelt
  should itself recursively, instead of trying to instantiate them from a
  single source value.
- The default decoder `jsonlike` uses a superset of the JSON syntax to read
  most Python built-in types from strings.

[Unreleased]: https://github.com/olivierlacan/keep-a-changelog/compare/v2019.8.1...HEAD
[2019.8.1]: https://github.com/thilp/umwelt/releases/tag/v2019.8.1

[pydantic]: https://pypi.org/project/pydantic/