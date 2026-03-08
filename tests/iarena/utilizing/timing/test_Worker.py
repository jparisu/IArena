from __future__ import annotations

import time

import pytest

from iarena.utilizing.timing.Worker import Worker


def test_limited_time_call_returns_callable_result_with_args() -> None:
    def add(a: int, b: int) -> int:
        return a + b

    result = Worker.limited_time_call(add, 1.0, 2, 3)

    assert result == 5


def test_limited_time_call_raises_timeout_error_when_exceeded() -> None:
    def slow(delay_s: float) -> str:
        time.sleep(delay_s)
        return "done"

    with pytest.raises(TimeoutError):
        Worker.limited_time_call(slow, 0.01, 0.1)


def test_limited_time_call_propagates_callable_exceptions() -> None:
    def failing() -> None:
        raise ValueError("boom")

    with pytest.raises(ValueError, match="boom"):
        Worker.limited_time_call(failing, 1.0)
