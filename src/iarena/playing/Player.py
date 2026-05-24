"""Declares the abstract player contract for selecting game movements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from iarena.utilizing.protocoling.Recognizable import Recognizable

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class Player(Recognizable, ABC):
    """Abstract player capable of selecting movements during a match.

    Purpose:
        Provides the `Player` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    def __init__(self, name: str | None = None) -> None:
        """Initialize the player with an optional name.

        Args:
            name (str | None): Optional name for the player. If None, a default name is assigned.

        Returns:
            None.
        """
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a string or None.")
        self._name = name if name is not None else f"Player_{id(self)}"

    def __str__(self) -> str:
        """Return a string representation of the player.

        Returns:
            str: The player's name.
        """
        return self.name()

    def name(self) -> str:
        """Return the player's name.

        Returns:
            str: The player's name.
        """
        return self._name

    @abstractmethod
    def play(self, pos: Position) -> Movement:
        """Choose and return the next movement for the given position.

        What it does:
            Declares the core decision method that produces one legal movement.
        How it works:
            Concrete subclasses evaluate the input position and select a movement.
        Args:
            pos (Position): Current game position where the player must act.
        Returns:
            Movement: Movement chosen by the player strategy.
        """
        raise NotImplementedError

    @abstractmethod
    def starting_game(self, rules: Rules, player_index: PlayerIndex) -> None:
        """Initialize player state when a new game begins.

        What it does:
            Declares the setup hook executed before the first turn of a match.
        How it works:
            Concrete subclasses store runtime context required while playing.
        Args:
            rules (Rules): Rules instance associated with the game to be played.
            player_index (PlayerIndex): Player identifier assigned in the arena.
        Returns:
            None: This method updates internal state and returns no value.

        Warning:
            This method must be overridden by concrete player implementations to properly initialize game context.
        """
