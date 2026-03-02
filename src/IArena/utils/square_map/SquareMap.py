from __future__ import annotations

from typing import Dict, Iterator, List, Set, Tuple, Iterable, Generic, TypeVar
from enum import Enum
from dataclasses import dataclass

from IArena.utils.printing import matrix_map_to_str

class Direction(Enum):
    """Possible movement directions in the grid."""
    Up = 0
    Down = 1
    Left = 2
    Right = 3


@dataclass(frozen=True)
class Coordinate:
    """Represents a coordinate in the grid."""
    x: int
    y: int

    def up(self) -> Coordinate:
        """Return the coordinate above the given one."""
        return Coordinate(self.x - 1, self.y)

    def down(self) -> Coordinate:
        """Return the coordinate below the given one."""
        return Coordinate(self.x + 1, self.y)

    def left(self) -> Coordinate:
        """Return the coordinate to the left of the given one."""
        return Coordinate(self.x, self.y - 1)

    def right(self) -> Coordinate:
        """Return the coordinate to the right of the given one."""
        return Coordinate(self.x, self.y + 1)

    def from_direction(self, dir: Direction) -> Coordinate:
        """Return a new coordinate moved in the given direction."""
        if dir == Direction.Up:
            return self.up()
        elif dir == Direction.Down:
            return self.down()
        elif dir == Direction.Left:
            return self.left()
        elif dir == Direction.Right:
            return self.right()
        else:
            raise ValueError("Invalid direction")

    def __iter__(self):
        """Allow unpacking a Coordinate like `x, y = coord`."""
        yield self.x
        yield self.y

    def as_tuple(self) -> Tuple[int, int]:
        """Return the coordinate as a (x, y) tuple."""
        return (self.x, self.y)

    def neighbors(self) -> Iterator[Tuple[Direction, Coordinate]]:
        """Return the neighboring coordinates."""
        yield (Direction.Up, self.up())
        yield (Direction.Down, self.down())
        yield (Direction.Left, self.left())
        yield (Direction.Right, self.right())

    #####################
    # COMPARISON METHODS

    def __eq__(self, other):
        """Check equality of two coordinates."""
        if not isinstance(other, Coordinate):
            return NotImplemented
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        """Allow Coordinate to be used in sets and as dict keys."""
        return hash((self.x, self.y))

    def __lt__(self, other):
        """Define a less-than ordering for Coordinates (row-major order)."""
        if not isinstance(other, Coordinate):
            return NotImplemented
        return (self.x, self.y) < (other.x, other.y)



T = TypeVar("T")


class SquareMap(Generic[T]):
    """
    Represents the grid of the game.

    Attributes:
        map: List[List[T]] - The grid represented as a matrix of values.
    """

    def __init__(self, smap: List[List[T]]):
        """Initialize the map wrapper with a 2D matrix of costs/values."""
        self.map_ = smap

    def __str__(self):
        """Return a human-readable string representation of the map matrix."""
        return matrix_map_to_str(self.map_)

    def size(self) -> Tuple[int, int]:
        """Return (n_rows, n_cols) of the map."""
        return len(self.map_), len(self.map_[0])

    def __len__(self):
        """Return number of rows (so `len(map)` works)."""
        return len(self.map_)

    def __getitem__(self, index: Coordinate) -> T:
        """Return the cost/value at a given Coordinate (row=x, col=y)."""
        return self.map_[index.x][index.y]

    def in_bounds(self, coord: Coordinate) -> bool:
        """Check whether a coordinate is inside the map boundaries."""
        rows, cols = self.size()
        return 0 <= coord.x < rows and 0 <= coord.y < cols

    def possible_direction_neighbor(self, coord: Coordinate) -> Iterator[Tuple[Direction, Coordinate]]:
        """Yield (direction, neighbor_coordinate) pairs for all in-bounds 4-neighbors."""
        if self.in_bounds(Coordinate(coord.x - 1, coord.y)):
            yield (Direction.Up, Coordinate(coord.x - 1, coord.y))
        if self.in_bounds(Coordinate(coord.x + 1, coord.y)):
            yield (Direction.Down, Coordinate(coord.x + 1, coord.y))
        if self.in_bounds(Coordinate(coord.x, coord.y - 1)):
            yield (Direction.Left, Coordinate(coord.x, coord.y - 1))
        if self.in_bounds(Coordinate(coord.x, coord.y + 1)):
            yield (Direction.Right, Coordinate(coord.x, coord.y + 1))

    def possible_directions(self, coord: Coordinate) -> Iterator[Direction]:
        """Yield the directions that have an in-bounds neighbor from the given coordinate."""
        for direction, _ in self.possible_direction_neighbor(coord):
            yield direction

    def possible_neighbors(self, coord: Coordinate) -> Iterator[Coordinate]:
        """Yield all in-bounds neighboring coordinates (4-neighborhood)."""
        for _, neighbor in self.possible_direction_neighbor(coord):
            yield neighbor

    def check(
            self,
            allow_zero: bool = True,
            skip_coordinate_validation: List[Coordinate] = []):
        """
        Validate map shape and values.

        - Must have at least one row.
        - All rows must have the same length.
        - Values must be positive (or non-negative if allow_zero=True).
        """
        if len(self.map_) == 0:
            raise ValueError("The map must have at least one row.")
        n_cols = len(self.map_[0])
        for i, row in enumerate(self.map_):
            if len(row) != n_cols:
                raise ValueError("All rows must have the same length.")
            for j, value in enumerate(row):
                if allow_zero:
                    if value < 0 and Coordinate(i, j) not in skip_coordinate_validation:
                        raise ValueError("All values must be non-negative.")
                else:
                    if value <= 0 and Coordinate(i, j) not in skip_coordinate_validation:
                        raise ValueError("All values must be positive.")

    @classmethod
    def zeros(cls, n_rows: int, n_cols: int) -> SquareMap:
        """Create a SquareMap of given size filled with zeros."""
        return SquareMap([[0.0 for _ in range(n_cols)] for _ in range(n_rows)])

    @classmethod
    def zeros_like(cls, smap: SquareMap) -> SquareMap:
        """Create a SquareMap of the same size as this one, filled with zeros."""
        n_rows, n_cols = smap.size()
        return SquareMap.zeros(n_rows, n_cols)

    def compass_direction(self, from_coord: Coordinate, to_coord: Coordinate) -> Direction:
        """
        Determine the primary compass direction from one coordinate to another.

        Chooses the axis with the largest distance difference.
        """
        dx = to_coord.x - from_coord.x
        dy = to_coord.y - from_coord.y

        if abs(dx) < abs(dy):
            return Direction.Right if dy > 0 else Direction.Left
        else:
            return Direction.Down if dx > 0 else Direction.Up

    def min(self) -> T:
        """Return the minimum value in the map."""
        return min(min(row) for row in self.map_)

    def max(self) -> T:
        """Return the maximum value in the map."""
        return max(max(row) for row in self.map_)

    def sum(self) -> T:
        """Return the sum of all values in the map."""
        return sum(sum(row) for row in self.map_)
