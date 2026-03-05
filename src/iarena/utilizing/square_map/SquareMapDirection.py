"""Reusable square-grid helpers for grid-based IArena games.

This module intentionally keeps the API lightweight and generic so games can
store any value type in the grid (costs, terrain codes, objects, etc.).
"""

from __future__ import annotations

from enum import Enum


class SquareMapDirection(Enum):
    """4-neighborhood movement directions for a square map."""

    Up = (-1, 0)
    Down = (1, 0)
    Left = (0, -1)
    Right = (0, 1)

    @property
    def delta(self) -> tuple[int, int]:
        """Return coordinate delta represented by this direction.

        Returns:
            Pair `(dx, dy)` with row/column increment.
        """
        return self.value

    def opposite(self) -> SquareMapDirection:
        """Return the opposite cardinal direction.

        Returns:
            Opposite direction.
        """
        return {
            SquareMapDirection.Up: SquareMapDirection.Down,
            SquareMapDirection.Down: SquareMapDirection.Up,
            SquareMapDirection.Left: SquareMapDirection.Right,
            SquareMapDirection.Right: SquareMapDirection.Left,
        }[self]
