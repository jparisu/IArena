"""Declares an arena behavior that stores turn logs."""

from __future__ import annotations

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase
from iarena.gaming.Movement import Movement


class LogsStoringArena(ConfiguredArenaBase):
    """Arena behavior implementing per-turn log storage."""

    def _store_logs(self, last_movement: Movement) -> None:
        """Store one turn log entry.

        Args:
            last_movement: Movement executed in the last turn.

        Returns:
            None.
        """
        self._logs.append(
            {
                "turn": self._turn_count,
                "movement": last_movement,
                "position": self._position,
                "elapsed_s": self._timer.elapsed(),
            },
        )
