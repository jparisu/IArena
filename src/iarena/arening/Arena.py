"""Declares the abstract arena contract that coordinates match execution."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.gaming.Rules import Rules
    from iarena.playing.Player import Player
    from iarena.scoring.ScoreBoard import ScoreBoard
    from iarena.visualizing.View import View


class Arena(ABC):
    """Abstract arena base that defines the role of a match orchestrator.

    Purpose:
        Represents the high-level component responsible for running a complete
        game session using rules, players, and a view.
    How it is used:
        Concrete arenas inherit from this class to provide game-loop behavior,
        turn progression policy, and match termination control.
    Why it exists:
        Keeps orchestration concerns separated from game logic, player strategy,
        and rendering concerns.
    """

    @abstractmethod
    def play(self, rules: Rules, players: list[Player], view: View | None = None) -> ScoreBoard:
        """Play a complete match and return the final scoreboard.

        What it does:
            Defines the high-level orchestration entrypoint used to execute one full
            game session.
        How it works:
            Concrete arenas coordinate turn progression, player actions, rule
            transitions, and rendering integration until a terminal condition is met.
        Args:
            rules (Rules): Rules engine that defines legal transitions and scoring.
            players (list[Player]): Ordered participants involved in the match.
            view (View | None): Optional visualization/input frontend used
                during execution. When omitted, arenas use `EmptyView`.
        Returns:
            ScoreBoard: Final scoreboard produced when the match finishes.
        """
        raise NotImplementedError
