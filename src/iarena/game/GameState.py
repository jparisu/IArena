"""Abstract base class for game state."""

from abc import ABC, abstractmethod


class GameState(ABC):
    """Dynamic representation of the current position in a turn-based game.

    Stores all information needed to describe the game at a single point
    in time: the active player, public board information, and any private
    or hidden information required by the rules.

    The state may be immutable, copy-on-write, or mutated in place by
    GameRules; the choice is left to concrete implementations.
    """

    @abstractmethod
    def current_player_id(self) -> int:
        """Return the identifier of the player whose turn it currently is.

        Returns
        -------
        int
            Zero-based index of the active player within the player list
            held by the engine.
        """
