"""Declares coordinate model for square-grid locations."""
# pylint: disable=too-many-lines  # TODO: review

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from .SquareMapDirection import SquareMapDirection


@dataclass(slots=True)
class SquareMapCoordinate:
    """Square-grid coordinate with neighbor and distance helpers.

    Purpose:
        Provides the `SquareMapCoordinate` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        x (int): Public attribute exposed by this class.
        y (int): Public attribute exposed by this class.
    """

    x: int = 0
    y: int = 0

    @classmethod
    def from_tuple(cls, value: tuple[int, int]) -> SquareMapCoordinate:
        """Build a coordinate instance from a `(row, col)` tuple.

        What it does:
            Implements `from_tuple` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            value (tuple[int, int]): Input consumed by this operation.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return cls(x=value[0], y=value[1])

    def up(self) -> SquareMapCoordinate:
        """Return the coordinate one row above.

        What it does:
            Implements `up` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return SquareMapCoordinate(self.x - 1, self.y)

    def down(self) -> SquareMapCoordinate:
        """Return the coordinate one row below.

        What it does:
            Implements `down` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return SquareMapCoordinate(self.x + 1, self.y)

    def left(self) -> SquareMapCoordinate:
        """Return the coordinate one column to the left.

        What it does:
            Implements `left` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return SquareMapCoordinate(self.x, self.y - 1)

    def right(self) -> SquareMapCoordinate:
        """Return the coordinate one column to the right.

        What it does:
            Implements `right` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return SquareMapCoordinate(self.x, self.y + 1)

    def moved(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Return the coordinate moved by one step in the given direction.

        What it does:
            Implements `moved` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            direction (SquareMapDirection): Input consumed by this operation.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        dx, dy = direction.delta
        return SquareMapCoordinate(self.x + dx, self.y + dy)

    def from_direction(self, direction: SquareMapDirection) -> SquareMapCoordinate:
        """Return the coordinate moved in the given direction (compatibility alias).

        What it does:
            Implements `from_direction` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            direction (SquareMapDirection): Input consumed by this operation.
        Returns:
            SquareMapCoordinate: Result produced after executing the method contract.
        """
        return self.moved(direction)

    def manhattan_distance(self, other: SquareMapCoordinate) -> int:
        """Return the Manhattan distance to another coordinate.

        What it does:
            Implements `manhattan_distance` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            other (SquareMapCoordinate): Input consumed by this operation.
        Returns:
            int: Result produced after executing the method contract.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def as_tuple(self) -> tuple[int, int]:
        """Return the coordinate as a `(row, col)` tuple.

        What it does:
            Implements `as_tuple` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            tuple[int, int]: Result produced after executing the method contract.
        """
        return (self.x, self.y)

    def __iter__(self) -> Iterator[int]:
        """Iterate coordinate components in `(x, y)` order.

        What it does:
            Implements `__iter__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            Iterator[int]: Result produced after executing the method contract.
        """
        yield self.x
        yield self.y

    def __len__(self) -> int:
        """Return tuple-like length for coordinate unpacking semantics.

        What it does:
            Implements `__len__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            int: Result produced after executing the method contract.
        """
        return 2

    def __getitem__(self, index: int) -> int:
        """Return tuple-like indexed coordinate component.

        What it does:
            Implements `__getitem__` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            index (int): Input consumed by this operation.
        Returns:
            int: Result produced after executing the method contract.
        """
        values = (self.x, self.y)
        return values[index]

    def neighbors(self) -> Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
        """Yield four cardinal neighbors as direction-coordinate pairs.

        What it does:
            Implements `neighbors` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            None.
        Returns:
            Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
                Result produced after executing the method contract.
        """
        for direction in (
            SquareMapDirection.UP,
            SquareMapDirection.RIGHT,
            SquareMapDirection.DOWN,
            SquareMapDirection.LEFT,
        ):
            yield direction, self.moved(direction)
