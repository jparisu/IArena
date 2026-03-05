"""Abstract interface for immutable or mutable game positions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.interfacing.IPlayer import PlayerIndex


class IPosition(ABC):
    """Represents a full game state at a specific turn.

    Concrete games should subclass this interface and store only the state
    needed by rules and players to:
    - evaluate legal movements,
    - identify whose turn it is,
    - and compute game termination and scoring.

    The position intentionally does not own game rules; rule logic belongs to
    `IGameRules` and receives positions as input.
    """

    @abstractmethod
    def next_player(self) -> PlayerIndex:
        """Return the player index that must act at this position.

        Returns:
            Index of the player whose turn is next.
        """
        raise NotImplementedError
