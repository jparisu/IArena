"""Declares an arena behavior that enforces timeout-based termination."""

from __future__ import annotations

from .ConfiguredArenaBase import ConfiguredArenaBase


class TimeoutCheckingArena(ConfiguredArenaBase):
    """Arena behavior implementing timeout termination checks."""

    def _check_timeout(self) -> bool:
        """Return whether timeout-based termination conditions are met.

        Args:
            None.

        Returns:
            bool: `True` when per-turn or total timeout conditions are met.
        """
        return self._timed_out or self._timer.elapsed() >= self._max_total_time_s
