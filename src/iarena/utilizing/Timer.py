"""Utility timer with start, pause, reset, and elapsed-time helpers."""

import time


class Timer:
    """Track elapsed wall-clock time."""

    def __init__(self, start_activated: bool = True) -> None:
        """Initialize the timer.

        Args:
            start_activated: Whether the timer starts immediately.
        """
        self.start_time: float | None = None
        self.elapsed_time: float = 0.0
        self.is_active: bool = False

        if start_activated:
            self.start()

    def start(self) -> None:
        """Start counting time if the timer is currently paused."""
        if not self.is_active:
            self.start_time = time.time()
            self.is_active = True

    def pause(self) -> None:
        """Pause the timer and accumulate elapsed time."""
        if self.is_active:
            if self.start_time is None:
                return
            self.elapsed_time += time.time() - self.start_time
            self.is_active = False

    def reset(self) -> None:
        """Reset accumulated elapsed time.

        If the timer is active, the current start timestamp is refreshed.
        """
        self.elapsed_time = 0.0
        if self.is_active:
            self.start_time = time.time()

    def elapsed(self) -> float:
        """Get the total elapsed time in seconds.

        Returns:
            Elapsed time in seconds.
        """
        if self.is_active:
            if self.start_time is None:
                return self.elapsed_time
            return self.elapsed_time + time.time() - self.start_time
        return self.elapsed_time
