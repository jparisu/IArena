from __future__ import annotations

from iarena.utilizing.structuring.GenericRegistry import GenericRegistry


def test_init_accepts_optional_name_convention() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    assert isinstance(registry, GenericRegistry)


def test_register_stores_value_and_returns_canonical_name() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    canonical = registry.register(obj=123, name="MyName", aliases=["alias"])
    assert canonical == "myname"


def test_register_alias_points_to_existing_registered_name() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=123, name="main")
    registry.register_alias(alias="secondary", target_existing_alias="main")
    assert registry.get("secondary") == 123


def test_get_returns_value_by_name_or_alias() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj="value", name="main", aliases=["alias"])
    assert registry.get("main") == "value"
    assert registry.get("alias") == "value"


def test_remove_alias_deletes_only_alias_mapping() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj="value", name="main", aliases=["alias"])
    registry.remove_alias("alias")
    assert registry.get("alias", strict=False) is None
    assert registry.get("main") == "value"


def test_remove_value_deletes_object_and_all_aliases() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj="value", name="main", aliases=["a1", "a2"])
    removed = registry.remove_value("main")
    assert removed == "value"
    assert registry.get("main", strict=False) is None
    assert registry.get("a1", strict=False) is None
    assert registry.get("a2", strict=False) is None


def test_has_reports_presence_for_name_or_alias() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=1, name="main", aliases=["alias"])
    assert registry.has("main") is True
    assert registry.has("alias") is True
    assert registry.has("missing") is False


def test_list_aliases_returns_all_registered_alias_names() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=1, name="main", aliases=["a1", "a2"])
    assert set(registry.list_aliases()) == {"main", "a1", "a2"}


def test_contains_uses_registry_lookup_semantics() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=1, name="main")
    assert "main" in registry


def test_len_returns_number_of_unique_values() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=1, name="one", aliases=["uno"])
    registry.register(obj=2, name="two", aliases=["dos"])
    assert len(registry) == 2


def test_clear_removes_all_values_and_aliases() -> None:
    registry = GenericRegistry(name_convention=str.lower)
    registry.register(obj=1, name="one", aliases=["uno"])
    registry.clear()
    assert len(registry) == 0
    assert registry.get("one", strict=False) is None
