from __future__ import annotations

from dataclasses import dataclass

from iarena.utilizing.structuring.GenericParameter import GenericParameter


@dataclass
class _Params(GenericParameter):
    count: int | None = None
    name: str | None = None

    @classmethod
    def aliases(cls) -> dict[str, str]:
        return {"n": "name"}


def test_from_dict_builds_instance_from_mapping() -> None:
    p = _Params.from_dict({"count": "3", "n": "demo"})
    assert isinstance(p, _Params)
    assert p.count == 3
    assert p.name == "demo"


def test_update_from_dict_updates_current_instance_fields() -> None:
    p = _Params(count=1, name="a")
    p.update_from_dict({"count": 2, "name": "b"})
    assert p.count == 2
    assert p.name == "b"


def test_convert_value_casts_to_requested_target_type() -> None:
    p = _Params()
    assert p._convert_value(int, "4") == 4


def test_to_dict_serializes_current_state() -> None:
    p = _Params(count=7, name="x")
    assert p.to_dict() == {"count": 7, "name": "x"}


def test_set_default_value_only_applies_when_field_is_none() -> None:
    p = _Params(count=None, name="x")
    p.set_default_value("count", 10)
    p.set_default_value("name", "y")
    assert p.count == 10
    assert p.name == "x"


def test_aliases_returns_key_alias_mapping() -> None:
    assert _Params.aliases() == {"n": "name"}


def test_copy_returns_distinct_parameter_instance() -> None:
    p = _Params(count=5, name="name")
    clone = p.copy()
    assert clone == p
    assert clone is not p
