"""Declares an arena behavior that performs a no-op turn execution."""

from __future__ import annotations

from .ConfiguredArenaBase import ConfiguredArenaBase


class NoOpExecuteTurnArena(ConfiguredArenaBase):
    """Arena behavior implementing a no-op turn progression."""

    def _execute_turn(self) -> None:
        """Execute a no-op turn by only increasing the turn count.

        Args:
            None.

        Returns:
            None.
        """
        self._turn_count += 1
