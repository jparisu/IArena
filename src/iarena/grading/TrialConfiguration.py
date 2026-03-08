"""Declares the configuration for repeated-match trial execution."""

from __future__ import annotations

from dataclasses import dataclass

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
    allow_fails: int
