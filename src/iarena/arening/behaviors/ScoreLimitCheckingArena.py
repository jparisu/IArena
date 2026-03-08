"""Declares an arena behavior that enforces score-limit termination."""

from __future__ import annotations

from iarena.playing.PlayerIndex import PlayerIndex

from .ConfiguredArenaBase import ConfiguredArenaBase


class ScoreLimitCheckingArena(ConfiguredArenaBase):
    """Arena behavior implementing game-finish and score-limit checks."""

    def _check_score_limit(self) -> bool:
        """Return whether score-based termination conditions are met.

        Args:
            None.

        Returns:
            bool: `True` when the game is finished or score limits are reached.
        """
        if self._rules.is_finished(self._position):
            return True

        low_limit, high_limit = self._score_limits
        scoreboard = self._rules.get_score(self._position)

        raw_scores = getattr(scoreboard, "_scores", None)
        if isinstance(raw_scores, dict):
            return any(score <= low_limit or score >= high_limit for score in raw_scores.values())

        for player_index in range(len(self._players)):
            try:
                score = scoreboard.get_score(PlayerIndex(player_index))
            except (AttributeError, KeyError, NotImplementedError):
                continue
            if score <= low_limit or score >= high_limit:
                return True
        return False
