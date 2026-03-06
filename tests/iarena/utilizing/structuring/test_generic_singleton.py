import threading

from iarena.utilizing.structuring.GenericSingleton import GenericSingleton


class _Service:
    def __init__(self, value: int) -> None:
        self.value = value


def test_generic_singleton_returns_same_instance() -> None:
    singleton = GenericSingleton(_Service)
    first = singleton(10)
    second = singleton(99)

    assert first is second
    assert first.value == 10


def test_generic_singleton_is_thread_safe() -> None:
    singleton = GenericSingleton(_Service)
    instances: list[_Service] = []

    def _build() -> None:
        instances.append(singleton(1))

    threads = [threading.Thread(target=_build) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len({id(instance) for instance in instances}) == 1
