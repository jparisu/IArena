"""Declares an arena behavior that ignores turn logs."""

from __future__ import annotations

from iarena.gaming.Movement import Movement

from .ConfiguredArenaBase import ConfiguredArenaBase


class NoLogsArena(ConfiguredArenaBase):
    """Arena behavior implementing no-op log persistence."""

    def _store_logs(self, last_movement: Movement) -> None:
        """Ignore the provided movement and keep logs untouched.

        Args:
            last_movement: Movement executed in the last turn.

        Returns:
            None.
        """
        _ = last_movement
