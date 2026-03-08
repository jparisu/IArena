"""Declares cardinal directions for square-grid traversal."""

from __future__ import annotations

from enum import Enum


class SquareMapDirection(Enum):
    """Cardinal movement direction for square-grid traversal.

    Purpose:
        Provides the `SquareMapDirection` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    UP = (-1, 0)
    RIGHT = (0, 1)
    DOWN = (1, 0)
    LEFT = (0, -1)

    @property
    def delta(self) -> tuple[int, int]:
        """Return movement delta `(dx, dy)` represented by the direction.

        What it does:
            Implements `delta` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            tuple[int, int]: Result produced after executing the method contract.
        """
        return self.value

    def opposite(self) -> SquareMapDirection:
        """Return the opposite cardinal direction.

        What it does:
            Implements `opposite` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            SquareMapDirection: Result produced after executing the method contract.
        """
        opposites = {
            SquareMapDirection.UP: SquareMapDirection.DOWN,
            SquareMapDirection.RIGHT: SquareMapDirection.LEFT,
            SquareMapDirection.DOWN: SquareMapDirection.UP,
            SquareMapDirection.LEFT: SquareMapDirection.RIGHT,
        }
        return opposites[self]
