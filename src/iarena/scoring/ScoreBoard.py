"""Declares the score board container abstraction for per-player scores."""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.playing.PlayerIndex import PlayerIndex
    from iarena.scoring.Score import Score


class ScoreBoard:
    """Container for per-player scores at a given position.

    Purpose:
        Provide a typed access point to per-player score values.
    How it works:
        Exposes score lookup operations keyed by `PlayerIndex`.
    Used for:
        Returning scoring results from rules, arenas, and game orchestration flows.
    API:
        `get_score(index: PlayerIndex) -> Score`: Return one player's score.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def get_score(self, index: PlayerIndex) -> Score:
        """Return the score assigned to a specific player index.

        What it does:
            Retrieves the score value corresponding to the provided player identifier.
        How it works:
            Uses the scoreboard's internal player-to-score association to resolve a `Score`.
        Args:
            index (PlayerIndex): Identifier of the player whose score is requested.
        Returns:
            Score: Score currently associated with the given `index`.
        Raises:
            AttributeError: If the internal score mapping is not initialized.
            KeyError: If `index` is not present in the scoreboard.
        """
        scores = getattr(self, "_scores", None)
        if scores is None:
            raise AttributeError("ScoreBoard requires an internal `_scores` mapping before calling `get_score`.")

        typed_scores: Mapping[PlayerIndex, Score] = scores
        return typed_scores[index]
