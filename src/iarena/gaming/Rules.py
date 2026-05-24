"""Declares the abstract rules engine interface for game logic."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from iarena.gaming.Movement import Movement
    from iarena.gaming.Position import Position
    from iarena.scoring.ScoreBoard import ScoreBoard


class Rules(ABC):
    """Abstract stateless rules engine encapsulating game logic.

    Purpose:
        Provides the `Rules` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @abstractmethod
    def n_players(self) -> int:
        """Return the number of players supported by the game.

        What it does:
            Implements `n_players` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            int: Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def first_position(self) -> Position:
        """Return the initial position of a new game.

        What it does:
            Implements `first_position` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            'Position': Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def next_position(self, pos: Position, mov: Movement) -> Position:
        """Return the next position after applying a movement.

        What it does:
            Implements `next_position` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            pos ('Position'): Input consumed by this operation.
            mov ('Movement'): Input consumed by this operation.
        Returns:
            'Position': Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def possible_movements(self, pos: Position) -> Iterator[Movement]:
        """Yield all legal movements available from a position.

        What it does:
            Implements `possible_movements` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            pos ('Position'): Input consumed by this operation.
        Returns:
            Iterator['Movement']: Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def is_finished(self, pos: Position) -> bool:
        """Return whether the game is finished at a position.

        What it does:
            Implements `is_finished` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            pos ('Position'): Input consumed by this operation.
        Returns:
            bool: Result produced after executing the method contract.
        """
        # TODO
        ...

    @abstractmethod
    def get_score(self, pos: Position) -> ScoreBoard:
        """Return the scoreboard value for a position.

        What it does:
            Implements `get_score` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            pos ('Position'): Input consumed by this operation.
        Returns:
            'ScoreBoard': Result produced after executing the method contract.
        """
        # TODO
        ...
