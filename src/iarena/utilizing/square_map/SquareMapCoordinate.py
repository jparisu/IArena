"""Reusable square-grid helpers for grid-based IArena games.

This module intentionally keeps the API lightweight and generic so games can
store any value type in the grid (costs, terrain codes, objects, etc.).
"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from iarena.utilizing.square_map.SquareMapDirection import SquareMapDirection


@dataclass(frozen=True, order=True, slots=True)
class SquareMapCoordinate:
    """Grid coordinate represented as `(x=row, y=col)`."""

    x: int
    y: int

    def up(self) -> SquareMapCoordinate:
        """Return coordinate one row above.

        Returns:
            New coordinate `(x-1, y)`.
        """
        return SquareMapCoordinate(self.x - 1, self.y)

    def down(self) -> SquareMapCoordinate:
        """Return coordinate one row below.

        Returns:
            New coordinate `(x+1, y)`.
        """
        return SquareMapCoordinate(self.x + 1, self.y)

    def left(self) -> SquareMapCoordinate:
        """Return coordinate one column to the left.

        Returns:
            New coordinate `(x, y-1)`.
        """
        return SquareMapCoordinate(self.x, self.y - 1)

    def right(self) -> SquareMapCoordinate:
        """Return coordinate one column to the right.

        Returns:
            New coordinate `(x, y+1)`.
        """
        return SquareMapCoordinate(self.x, self.y + 1)

    def moved(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Move one step in `direction`.

        Args:
            direction: Direction to apply.

        Returns:
            New shifted coordinate.
        """
        dx, dy = direction.delta
        return SquareMapCoordinate(self.x + dx, self.y + dy)

    def from_direction(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Backward-compatible alias of :meth:`moved`.

        Args:
            direction: Direction to apply.

        Returns:
            New shifted coordinate.
        """
        return self.moved(direction)

    def manhattan_distance(self, other: SquareMapCoordinate) -> int:
        """Compute Manhattan (L1) distance to another coordinate.

        Args:
            other: Destination coordinate.

        Returns:
            Integer Manhattan distance.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def as_tuple(self) -> tuple[int, int]:
        """Convert coordinate to tuple.

        Returns:
            Tuple `(x, y)`.
        """
        return (self.x, self.y)

    def __iter__(self) -> Iterator[int]:
        """Iterate coordinate components.

        Returns:
            Iterator yielding `x` then `y`.
        """
        yield self.x
        yield self.y

    def neighbors(self) -> Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
        """Iterate four cardinal neighbors.

        Returns:
            Iterator of `(direction, neighbor_coordinate)` pairs.
        """
        directions = (
            SquareMapDirection.Up,
            SquareMapDirection.Down,
            SquareMapDirection.Left,
            SquareMapDirection.Right,
        )
        for direction in directions:
            yield (direction, self.moved(direction))
