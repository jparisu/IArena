from __future__ import annotations

from iarena.utilizing.structuring.GenericSingleton import GenericSingleton


class _Counter:
    calls = 0

    def __init__(self, value: int) -> None:
        _Counter.calls += 1
        self.value = value


def test_init_registers_wrapped_class() -> None:
    singleton = GenericSingleton(_Counter)
    assert callable(singleton)


def test_call_creates_single_instance_once_and_reuses_it() -> None:
    _Counter.calls = 0
    singleton = GenericSingleton(_Counter)
    first = singleton(1)
    second = singleton(2)
    assert first is second
    assert _Counter.calls == 1


def test_get_instance_returns_existing_singleton_instance() -> None:
    _Counter.calls = 0
    singleton = GenericSingleton(_Counter)
    created = singleton(9)
    retrieved = singleton.get_instance()
    assert retrieved is created
