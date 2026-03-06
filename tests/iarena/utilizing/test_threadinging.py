"""Tests for thread-based callable execution helpers."""

from __future__ import annotations

import pytest

from iarena.utilizing.threadinging import ThreadCallTimeoutError, run_callable_in_worker_thread


def test_run_callable_in_worker_thread_returns_value() -> None:
    """Worker runner should return callable value when no timeout occurs.

    Args:
        None.

    Returns:
        None.
    """

    def _build_value() -> int:
        """Build a deterministic numeric value.

        Args:
            None.

        Returns:
            Integer value.
        """
        return 42

    result = run_callable_in_worker_thread(callable_function=_build_value, timeout_seconds=0.5)

    assert result == 42


def test_run_callable_in_worker_thread_reraises_worker_exception() -> None:
    """Worker runner should propagate exceptions raised by callable.

    Args:
        None.

    Returns:
        None.
    """

    def _raise_error() -> int:
        """Raise an exception to validate propagation.

        Args:
            None.

        Returns:
            Never returns.
        """
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        run_callable_in_worker_thread(callable_function=_raise_error, timeout_seconds=0.5)


def test_run_callable_in_worker_thread_times_out_and_interrupts() -> None:
    """Worker runner should raise timeout when callable exceeds allowed time.

    Args:
        None.

    Returns:
        None.
    """

    def _spin_forever() -> int:
        """Run an infinite Python loop until interrupted.

        Args:
            None.

        Returns:
            Never returns.
        """
        while True:
            pass

    with pytest.raises(ThreadCallTimeoutError) as error_info:
        run_callable_in_worker_thread(callable_function=_spin_forever, timeout_seconds=0.01)

    assert error_info.value.timeout_seconds == 0.01
    assert error_info.value.elapsed_seconds > 0.0
    assert error_info.value.interrupted is True
