"""Declares the abstract player contract for selecting game movements."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from iarena.utilizing.protocoling.Recognizable import Recognizable
from iarena.playing.Player import Player

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.gaming.Rules import Rules
    from iarena.playing.PlayerIndex import PlayerIndex


class StudentPlayer(Player):
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

    def __init__(self, name: str, authors: list[str]) -> None:
        """Initialize the player with a name and list of authors.

        Args:
            name (str): Name for the player.
            authors (list[str]): List of author names responsible for this player.

        Returns:
            None.
        """
        if name is not None and not isinstance(name, str):
            raise TypeError("name must be a string or None.")
        if not isinstance(authors, list) or not all(isinstance(author, str) for author in authors):
            raise TypeError("authors must be a list of strings.")
        self._name = name if name is not None else f"Player_{id(self)}"
        self._authors = authors

    def authors(self) -> list[str]:
        """Return the list of authors responsible for this player.

        Returns:
            list[str]: List of author names.
        """
        return self._authors

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
        pass
