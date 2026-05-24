"""Declares an arena behavior that disables turn-budget termination."""

from __future__ import annotations

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase


class NoMaxTurnsArena(ConfiguredArenaBase):
    """Arena behavior that never stops due to max-turn checks."""

    def _check_max_turns(self) -> bool:
        """Return `False` to disable max-turn termination.

        Returns:
            bool: Always `False`.
        """
        return False
