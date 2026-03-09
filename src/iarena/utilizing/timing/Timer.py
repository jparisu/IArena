"""Declares a timer helper for elapsed-time tracking."""

from __future__ import annotations

import time


class Timer:
    """Timer helper to track elapsed time and enforce timeouts.

    Purpose:
        Defines the timing contract used by IArena components that need elapsed-time
        measurements and timeout checks.
    Behavior:
        A concrete implementation is expected to support start/pause cycles, elapsed
        time accumulation, and timer reset semantics.
    Lifecycle:
        The timer can be created in an active or paused state depending on
        ``start_activated``.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, start_activated: bool = True) -> None:
        """Initialize the timer and optionally start it immediately.

        What it does:
            Creates a timer instance and sets its initial running state.
        How it works:
            Concrete implementations should initialize internal timing state and, when
            ``start_activated`` is ``True``, begin counting elapsed time immediately.
        Args:
            start_activated (bool, optional): If ``True``, the timer starts in an
                active state; if ``False``, it starts paused.
        Returns:
            None: Initializes instance state.
        """
        self._accumulated_s = 0.0
        self._running = start_activated
        self._started_at = self._now() if start_activated else None

    def start(self) -> None:
        """Start the timer if it is currently paused.

        What it does:
            Transitions the timer into a running state.
        How it works:
            Concrete implementations should record the current reference timestamp only
            when the timer is paused, so duplicate calls do not double-count time.
        Returns:
            None: Updates internal running state.
        """
        if self._running:
            return

        self._running = True
        self._started_at = self._now()

    def pause(self) -> None:
        """Pause the timer and accumulate elapsed time.

        What it does:
            Stops active time accumulation without discarding already measured time.
        How it works:
            Concrete implementations should add the current active span to the stored
            accumulated value and mark the timer as paused.
        Returns:
            None: Updates internal accumulated timing state.
        """
        if not self._running:
            return

        now = self._now()
        if self._started_at is not None:
            self._accumulated_s += now - self._started_at

        self._running = False
        self._started_at = None

    def reset(self) -> None:
        """Reset the accumulated timer value and keep current running mode.

        What it does:
            Clears elapsed-time accumulation to the initial zero value.
        How it works:
            Concrete implementations should preserve whether the timer is currently
            running or paused while zeroing the elapsed counter.
        Returns:
            None: Resets timing-related state.
        """
        self._accumulated_s = 0.0
        if self._running:
            self._started_at = self._now()

    def elapsed(self) -> float:
        """Return total elapsed time in seconds.

        What it does:
            Computes the total measured duration represented by the timer.
        How it works:
            Concrete implementations should include both accumulated paused spans and
            the current running span (if active) in the returned value.
        Returns:
            float: Elapsed time in seconds.
        """
        if not self._running:
            return self._accumulated_s

        if self._started_at is None:
            return self._accumulated_s

        return self._accumulated_s + (self._now() - self._started_at)

    def _now(self) -> float:
        """Return a monotonic timestamp in seconds.

        Returns:
            float: Monotonic timestamp suitable for duration measurement.
        """
        return time.monotonic()
