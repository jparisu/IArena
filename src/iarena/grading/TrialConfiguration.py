"""Declares the configuration for repeated-match trial execution."""

from __future__ import annotations

from dataclasses import dataclass

from iarena.gaming.Configuration import Configuration
from iarena.gaming.Rules import Rules
from iarena.grading.MatchConfiguration import MatchConfiguration
from iarena.playing.Player import Player
from iarena.playing.PlayerIndex import PlayerIndex


@dataclass
class TrialConfiguration:
    """Configuration for a trial consisting of repeated matches under the same setup.

    Purpose:
        Represent all inputs required to run a trial over several match
        repetitions.
    How it is used:
        Trial runners read this object to know which rules, players, and
        repetition policy to apply when executing grading loops.
    Why it exists:
        Ensures trial setup remains explicit, typed, and serializable as a
        standalone domain object.
    """

    match_configuration: MatchConfiguration
    trialing_player_index: PlayerIndex
    rules: Rules
    players: list[Player]
    repetitions: int
    description: str = ""
    game_configuration: Configuration | None = None
    value: float = 1.0
    max_score: float = float("inf")
    min_score: float = float("-inf")

    def __str__(self) -> str:
        """Return a compact human-readable representation of trial settings.

        Returns:
            str: One-line serialized trial summary for debug output.
        """
        game_configuration = self.game_configuration
        game_configuration_repr = str(game_configuration) if game_configuration is not None else "<unknown>"
        return (
            "TrialConfiguration("
            f"description={self.description!r}, "
            f"repetitions={self.repetitions}, "
            f"value={self.value}, "
            f"min_score={self.min_score}, "
            f"max_score={self.max_score}, "
            f"trialing_player_index={int(self.trialing_player_index)}, "
            f"move_timeout_s={self.match_configuration.move_timeout_s}, "
            f"total_timeout_s={self.match_configuration.total_timeout_s}, "
            f"max_turns={self.match_configuration.max_turns}, "
            f"game_configuration={game_configuration_repr}"
            ")"
        )
