"""Thread-based helpers to execute and interrupt callables with timeout support."""

from __future__ import annotations

import ctypes
import threading
import time
from collections.abc import Callable


class _ThreadTimeoutCancellationError(Exception):
    """Internal exception injected to stop timed-out worker threads."""


class ThreadCallTimeoutError(TimeoutError):
    """Raised when a worker-thread callable does not finish within timeout."""

    def __init__(
        self,
        timeout_seconds: float,
        elapsed_seconds: float,
        interrupted: bool,
        still_running: bool,
    ) -> None:
        """Initialize timeout error details.

        Args:
            timeout_seconds: Configured timeout threshold.
            elapsed_seconds: Time elapsed before timeout handling.
            interrupted: Whether asynchronous interruption was requested.
            still_running: Whether worker thread remains alive after interruption.

        Returns:
            None.
        """
        super().__init__(
            "threaded callable timed out: "
            f"elapsed={elapsed_seconds:.6f}s, timeout={timeout_seconds:.6f}s, "
            f"interrupted={interrupted}, still_running={still_running}"
        )
        self.timeout_seconds = timeout_seconds
        self.elapsed_seconds = elapsed_seconds
        self.interrupted = interrupted
        self.still_running = still_running


def _raise_async_exception(thread_id: int, exception_type: type[BaseException]) -> bool:
    """Inject an exception class asynchronously into a running Python thread.

    Args:
        thread_id: Identifier of a live Python thread.
        exception_type: Exception class to inject.

    Returns:
        ``True`` when interruption request succeeded, otherwise ``False``.
    """
    if thread_id <= 0:
        return False

    result = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_ulong(thread_id),
        ctypes.py_object(exception_type),
    )
    if result == 1:
        return True
    if result > 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(thread_id), None)
    return False


def run_callable_in_worker_thread[ResultType](
    callable_function: Callable[[], ResultType],
    timeout_seconds: float,
    interruption_join_seconds: float = 0.05,
) -> ResultType:
    """Run a callable in a daemon worker thread with timeout and interruption.

    Exceptions raised inside the worker are re-raised in the caller thread.

    Args:
        callable_function: Callable to execute in a worker thread.
        timeout_seconds: Maximum allowed execution time in seconds.
        interruption_join_seconds: Extra wait time after interruption request.

    Returns:
        Result produced by ``callable_function``.

    Raises:
        ValueError: If timeout values are non-positive.
        ThreadCallTimeoutError: If callable exceeds timeout.
        Exception: Re-raises any exception raised by ``callable_function``.
    """
    if timeout_seconds <= 0.0:
        raise ValueError("timeout_seconds must be > 0")
    if interruption_join_seconds < 0.0:
        raise ValueError("interruption_join_seconds must be >= 0")

    result_box: dict[str, ResultType] = {}
    exception_box: dict[str, Exception] = {}

    def _target() -> None:
        """Execute callable and capture result or error in shared boxes.

        Args:
            None.

        Returns:
            None.
        """
        try:
            result_box["value"] = callable_function()
        except Exception as error:  # pylint: disable=broad-exception-caught
            exception_box["error"] = error

    worker_thread = threading.Thread(target=_target, daemon=True)
    start_time = time.perf_counter()
    worker_thread.start()
    worker_thread.join(timeout_seconds)
    elapsed_seconds = time.perf_counter() - start_time

    if worker_thread.is_alive():
        interrupted = _raise_async_exception(worker_thread.ident or 0, _ThreadTimeoutCancellationError)
        if interruption_join_seconds > 0.0:
            worker_thread.join(interruption_join_seconds)
        raise ThreadCallTimeoutError(
            timeout_seconds=timeout_seconds,
            elapsed_seconds=elapsed_seconds,
            interrupted=interrupted,
            still_running=worker_thread.is_alive(),
        )

    if "error" in exception_box:
        raise exception_box["error"]
    return result_box["value"]
