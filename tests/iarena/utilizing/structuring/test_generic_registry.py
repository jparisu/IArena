import pytest

from iarena.utilizing.structuring.GenericRegistry import GenericRegistry


class _Registry(GenericRegistry[int]):
    pass


def test_register_and_get_with_aliases() -> None:
    registry = _Registry()
    registry.register(10, name="Primary", aliases=["Alias One"])

    assert registry.get("primary") == 10
    assert registry.get("alias-one") == 10


def test_register_conflict_and_overwrite() -> None:
    registry = _Registry()
    registry.register(1, name="x")

    with pytest.raises(ValueError):
        registry.register(2, name="x")

    registry.register(2, name="x", overwrite=True)
    assert registry.get("x") == 2
    assert len(registry) == 1


def test_register_alias_and_remove() -> None:
    registry = _Registry()
    registry.register(3, name="name")
    registry.register_alias("alt", "name")

    assert registry.get("alt") == 3
    registry.remove_alias("alt")
    assert not registry.has("alt")


def test_remove_value_deletes_all_aliases() -> None:
    registry = _Registry()
    registry.register(5, name="n1", aliases=["a1", "a2"])

    removed = registry.remove_value("a1")

    assert removed == 5
    assert not registry.has("n1")
    assert not registry.has("a2")


def test_get_non_strict_returns_none() -> None:
    registry = _Registry()
    assert registry.get("missing", strict=False) is None


def test_clear_empties_registry() -> None:
    registry = _Registry()
    registry.register(9, name="v")
    registry.clear()

    assert len(registry) == 0
    assert registry.list_aliases() == []
