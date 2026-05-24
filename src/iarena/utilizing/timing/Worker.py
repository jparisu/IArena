"""Declares worker utilities for time-limited callable execution."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Any


class Worker:
    """Worker utility to execute callables with an execution time limit.

    Purpose:
        Defines the contract for bounded-time execution of callables in IArena.
    Behavior:
        A concrete implementation is expected to invoke target functions and enforce
        timeout constraints.
    Scope:
        The API is designed for utility-level execution guards rather than business
        logic computation.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def limited_time_call(cls, func: Callable[..., Any], timeout_s: float, *args: Any) -> Any:
        """Run a callable with positional arguments under a timeout in seconds.

        What it does:
            Invokes ``func`` with positional arguments while enforcing an execution
            time budget.
        How it works:
            Concrete implementations should run the callable and either return its
            result when it completes before ``timeout_s`` or raise/propagate a timeout
            failure policy when it exceeds the limit.
        Args:
            cls (type[Worker]): Calling class provided by ``@classmethod``.
            func (Callable[..., Any]): Callable to execute.
            timeout_s (float): Maximum allowed runtime in seconds.
            *args (Any): Positional arguments forwarded to ``func``.
        Returns:
            Any: Value returned by ``func`` when execution completes in time.
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(func, *args)
            try:
                return future.result(timeout=timeout_s)
            except FutureTimeoutError as error:
                future.cancel()
                raise TimeoutError(f"Execution exceeded timeout of {timeout_s} seconds.") from error
