"""Declares an arena behavior that enforces the configured turn budget."""

from __future__ import annotations

from .ConfiguredArenaBase import ConfiguredArenaBase


class MaxTurnsCheckingArena(ConfiguredArenaBase):
    """Arena behavior implementing max-turn termination checks."""

    def _check_max_turns(self) -> bool:
        """Return whether the configured turn budget has been exhausted.

        Args:
            None.

        Returns:
            bool: `True` when `max_turns` has been reached.
        """
        return self._turn_count >= self._max_turns
