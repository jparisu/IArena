"""Abstract interface for immutable or mutable game positions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.desining.playing.Player import PlayerIndex


class Position(ABC):
    """Represent a full game state at a specific turn."""

    @abstractmethod
    def next_player(self) -> PlayerIndex:
        """Return the player index that must act at this position.

        Args:
            None.

        Returns:
            Index of the player whose turn is next.
        """
        raise NotImplementedError
