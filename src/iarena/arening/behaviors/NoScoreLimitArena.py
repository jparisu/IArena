"""Declares an arena behavior that disables score-limit termination."""

from __future__ import annotations

from iarena.arening.behaviors.ConfiguredArenaBase import ConfiguredArenaBase


class NoScoreLimitArena(ConfiguredArenaBase):
    """Arena behavior that only checks game completion, not score bounds."""

    def _check_score_limit(self) -> bool:
        """Return whether the game is finished without applying score limits.

        Returns:
            bool: `True` only when rules declare the game finished.
        """
        return self._rules.is_finished(self._position)
