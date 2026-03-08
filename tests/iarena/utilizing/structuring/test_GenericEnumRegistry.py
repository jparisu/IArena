from __future__ import annotations

from iarena.utilizing.structuring.GenericEnumRegistry import GenericEnumRegistry


class _Color(GenericEnumRegistry):
    RED = "r"
    GREEN = "g"
    BLUE = "b"


class _Indexed(GenericEnumRegistry):
    ITEM = ("x", "y", "z")


class _Aliased(GenericEnumRegistry):
    A = "alpha"
    B = "beta"

    @classmethod
    def aliases(cls) -> dict[str, str]:
        return {"first": "a", "second": "b"}

    @classmethod
    def default(cls) -> _Aliased:
        return cls.A


def test_get_all_values_returns_member_values() -> None:
    assert _Color.get_all_values() == ["r", "g", "b"]


def test_get_returns_member_value_or_indexed_item() -> None:
    assert _Color.RED.get() == "r"
    assert _Indexed.ITEM.get(1) == "y"


def test_find_resolves_member_by_key_or_value() -> None:
    assert _Color.find("RED") is _Color.RED
    assert _Color.find("g") is _Color.GREEN


def test_from_string_resolves_enum_member_from_string_value() -> None:
    assert _Color.from_string("blue") is _Color.BLUE


def test_name_convention_normalizes_and_resolves_aliases() -> None:
    assert _Aliased.name_convention(" First ") == "a"
    assert _Aliased.name_convention("B") == "b"


def test_default_returns_expected_default_member_or_none() -> None:
    assert _Aliased.default() is _Aliased.A


def test_aliases_returns_alias_mapping() -> None:
    assert _Aliased.aliases() == {"first": "a", "second": "b"}
