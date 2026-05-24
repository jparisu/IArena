from __future__ import annotations

from iarena.utilizing.structuring.GenericFactory import GenericFactory


class _Factory(GenericFactory[int]):
    pass


def _builder(base: int = 0, bonus: int = 0) -> int:
    return base + bonus


def test_register_constructor_stores_builder_callable() -> None:
    factory = _Factory(name_convention=str.lower)
    factory.register_constructor(_builder, name="sum", aliases=["add"])
    assert factory.get("sum") is _builder
    assert factory.get("add") is _builder


def test_construct_builds_instance_from_registered_constructor() -> None:
    factory = _Factory(name_convention=str.lower)
    factory.register_constructor(_builder, name="sum")
    assert factory.construct("sum", base=4, bonus=7) == 11
