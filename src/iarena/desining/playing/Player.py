"""Abstract player interface used by arenas to request movements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.desining.gaming.GameRules import GameRules
    from iarena.desining.gaming.Movement import Movement
    from iarena.desining.gaming.Position import Position

PlayerIndex = int
"""Type alias for the index of a player in the game."""


class Player(ABC):
    """Represent an agent able to choose movements in a game."""

    def __init__(self, name: str | None = None) -> None:
        """Initialize player identity used in logs and reports.

        Args:
            name: Optional display name.

        Returns:
            None.
        """
        self._name = name if name is not None else f"{self.__class__.__name__}_{id(self)}"

    def name(self) -> str:
        """Return the human-readable name of this player.

        Args:
            None.

        Returns:
            Display name of this player instance.
        """
        return self._name

    @abstractmethod
    def play(self, position: Position) -> Movement:
        """Choose a movement for the current position.

        Args:
            position: Current game position.

        Returns:
            Selected movement to be applied by the arena.
        """
        raise NotImplementedError

    def starting_game(self, rules: GameRules, player_index: PlayerIndex) -> None:
        """Lifecycle hook called once before a game starts.

        Args:
            rules: Rules object that governs the upcoming game.
            player_index: Index assigned to this player in the match.

        Returns:
            None.
        """
        del rules, player_index
        return None
