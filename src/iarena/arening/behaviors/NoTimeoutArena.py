"""Declares an arena behavior that disables timeout termination."""

from __future__ import annotations

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase


class NoTimeoutArena(ConfiguredArenaBase):
    """Arena behavior that never stops due to timeout checks."""

    def _check_timeout(self) -> bool:
        """Return `False` to disable timeout-based termination.

        Returns:
            bool: Always `False`.
        """
        return False
