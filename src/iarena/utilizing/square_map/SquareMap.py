# pylint: disable=too-many-lines
"""Reusable square-grid helpers for grid-based IArena games.

This module intentionally keeps the API lightweight and generic so games can
store any value type in the grid (costs, terrain codes, objects, etc.).
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator

import numpy as np

from iarena.utilizing.square_map.SquareMapCoordinate import SquareMapCoordinate as Coordinate
from iarena.utilizing.square_map.SquareMapDirection import SquareMapDirection as Direction

Index2D = tuple[int, int]


class SquareMap[T]:
    """Typed square-grid wrapper with bounds checks and navigation helpers.

    The underlying storage is a rectangular `list[list[T]]`. Input arrays are
    copied so callers can keep external matrices immutable if they want.
    """

    def __init__(self, smap: Iterable[Iterable[T]]) -> None:
        """Build a map from an iterable-of-iterables.

        Args:
            smap: Source rows and values.

        Returns:
            `None`.

        Raises:
            ValueError: If map is empty, has zero columns, or is ragged.
        """
        rows = [list(row) for row in smap]
        if not rows:
            raise ValueError("square map must contain at least one row")
        n_cols = len(rows[0])
        if n_cols == 0:
            raise ValueError("square map must contain at least one column")
        if any(len(row) != n_cols for row in rows):
            raise ValueError("all rows must have the same number of columns")
        self.map_: list[list[T]] = rows

    def __str__(self) -> str:
        """Render the map as aligned text.

        Returns:
            Multiline textual representation.
        """
        return self.to_text()

    def to_text(self) -> str:
        """Render the map as aligned text.

        Returns:
            Multiline textual representation.
        """
        rendered = [[str(v) for v in row] for row in self.map_]
        col_widths = [max(len(rendered[i][j]) for i in range(len(rendered))) for j in range(len(rendered[0]))]
        lines: list[str] = []
        for row in rendered:
            lines.append(" ".join(cell.rjust(col_widths[j]) for j, cell in enumerate(row)))
        return "\n".join(lines)

    def size(self) -> tuple[int, int]:
        """Get map shape.

        Returns:
            Pair `(n_rows, n_cols)`.
        """
        return (len(self.map_), len(self.map_[0]))

    def n_rows(self) -> int:
        """Return number of rows.

        Returns:
            Row count.
        """
        return len(self.map_)

    def n_cols(self) -> int:
        """Return number of columns.

        Returns:
            Column count.
        """
        return len(self.map_[0])

    def __len__(self) -> int:
        """Return number of rows.

        Returns:
            Row count.
        """
        return self.n_rows()

    def __iter__(self) -> Iterator[list[T]]:
        """Iterate rows.

        Returns:
            Iterator over underlying row lists.
        """
        return iter(self.map_)

    def __getitem__(self, index: Coordinate | Index2D) -> T:
        """Read value at coordinate.

        Args:
            index: Coordinate or `(row, col)` tuple.

        Returns:
            Stored cell value.
        """
        coord = self._to_coordinate(index)
        return self.map_[coord.x][coord.y]

    def __setitem__(self, index: Coordinate | Index2D, value: T) -> None:
        """Write value at coordinate.

        Args:
            index: Coordinate or `(row, col)` tuple.
            value: New value to store.

        Returns:
            `None`.
        """
        coord = self._to_coordinate(index)
        self.map_[coord.x][coord.y] = value

    def _to_coordinate(self, index: Coordinate | Index2D) -> Coordinate:
        """Normalize mixed index input to `Coordinate`.

        Args:
            index: Coordinate or tuple.

        Returns:
            Normalized coordinate.
        """
        if isinstance(index, Coordinate):
            return index
        x, y = index
        return Coordinate(x, y)

    def in_bounds(self, coord: Coordinate) -> bool:
        """Check if coordinate belongs to this map.

        Args:
            coord: Coordinate to validate.

        Returns:
            `True` if inside bounds, else `False`.
        """
        rows, cols = self.size()
        return 0 <= coord.x < rows and 0 <= coord.y < cols

    def require_in_bounds(self, coord: Coordinate, *, name: str = "coordinate") -> None:
        """Assert coordinate is in bounds.

        Args:
            coord: Coordinate to validate.
            name: Human-readable name used in error messages.

        Returns:
            `None`.

        Raises:
            IndexError: If coordinate is out of bounds.
        """
        if not self.in_bounds(coord):
            n_rows, n_cols = self.size()
            raise IndexError(f"{name} {coord} out of bounds for shape ({n_rows}, {n_cols})")

    def get(self, coord: Coordinate, default: T | None = None) -> T | None:
        """Read value with fallback for out-of-bounds coordinates.

        Args:
            coord: Coordinate to read.
            default: Fallback value when coordinate is outside map.

        Returns:
            Cell value or provided default.
        """
        if not self.in_bounds(coord):
            return default
        return self[coord]

    def possible_direction_neighbor(self, coord: Coordinate) -> Iterator[tuple[Direction, Coordinate]]:
        """Iterate in-bounds cardinal neighbors with direction labels.

        Args:
            coord: Origin coordinate.

        Returns:
            Iterator of `(direction, neighbor)` pairs.
        """
        for direction, neighbor in coord.neighbors():
            if self.in_bounds(neighbor):
                yield (direction, neighbor)

    def possible_direction_neighbors(self, coord: Coordinate) -> Iterator[tuple[Direction, Coordinate]]:
        """Alias of :meth:`possible_direction_neighbor`.

        Args:
            coord: Origin coordinate.

        Returns:
            Iterator of `(direction, neighbor)` pairs.
        """
        return self.possible_direction_neighbor(coord)

    def possible_directions(self, coord: Coordinate) -> Iterator[Direction]:
        """Iterate valid directions from coordinate.

        Args:
            coord: Origin coordinate.

        Returns:
            Iterator of legal cardinal directions.
        """
        for direction, _ in self.possible_direction_neighbor(coord):
            yield direction

    def possible_neighbors(self, coord: Coordinate) -> Iterator[Coordinate]:
        """Iterate in-bounds neighboring coordinates.

        Args:
            coord: Origin coordinate.

        Returns:
            Iterator of adjacent coordinates.
        """
        for _, neighbor in self.possible_direction_neighbor(coord):
            yield neighbor

    def iter_coordinates(self) -> Iterator[Coordinate]:
        """Iterate all coordinates in row-major order.

        Returns:
            Iterator of every coordinate in the map.
        """
        n_rows, n_cols = self.size()
        for x in range(n_rows):
            for y in range(n_cols):
                yield Coordinate(x, y)

    def iter_values(self) -> Iterator[T]:
        """Iterate all values in row-major order.

        Returns:
            Iterator of all stored values.
        """
        for coord in self.iter_coordinates():
            yield self[coord]

    def check(
        self,
        allow_zero: bool = True,
        skip_coordinate_validation: Iterable[Coordinate] | None = None,
    ) -> None:
        """Validate sign constraints over numeric-like cells.

        Args:
            allow_zero: If `True`, require values `>= 0`; otherwise require
                values strictly `> 0`.
            skip_coordinate_validation: Coordinates ignored by sign checks.

        Returns:
            `None`.

        Raises:
            ValueError: If any validated cell violates constraints.
        """
        skip = set(skip_coordinate_validation or [])
        for coord in self.iter_coordinates():
            if coord in skip:
                continue
            value = self[coord]
            if allow_zero:
                if value < 0:  # type: ignore[operator]
                    raise ValueError("all values must be non-negative")
            else:
                if value <= 0:  # type: ignore[operator]
                    raise ValueError("all values must be positive")

    @classmethod
    def full(cls, n_rows: int, n_cols: int, value: T) -> SquareMap[T]:
        """Build a map filled with a constant value.

        Args:
            n_rows: Number of rows.
            n_cols: Number of columns.
            value: Value copied to each cell.

        Returns:
            New `SquareMap` filled with `value`.

        Raises:
            ValueError: If shape is invalid.
        """
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError("n_rows and n_cols must be > 0")
        return cls([[value for _ in range(n_cols)] for _ in range(n_rows)])

    @classmethod
    def zeros(cls, n_rows: int, n_cols: int) -> SquareMap[float]:
        """Build a zero-filled floating-point map.

        Args:
            n_rows: Number of rows.
            n_cols: Number of columns.

        Returns:
            New zero-filled `SquareMap[float]`.

        Raises:
            ValueError: If shape is invalid.
        """
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError("n_rows and n_cols must be > 0")
        return SquareMap([[0.0 for _ in range(n_cols)] for _ in range(n_rows)])

    @classmethod
    def zeros_like(cls, smap: SquareMap[object]) -> SquareMap[float]:
        """Build a zero-filled map with shape of `smap`.

        Args:
            smap: Reference map for shape.

        Returns:
            Zero-filled map with same size as `smap`.
        """
        n_rows, n_cols = smap.size()
        return cls.zeros(n_rows, n_cols)

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> SquareMap[float]:
        """Build map from 2D NumPy array.

        Args:
            array: Two-dimensional source array.

        Returns:
            New `SquareMap[float]` copied from the array.

        Raises:
            ValueError: If array is not 2D.
        """
        if array.ndim != 2:
            raise ValueError("numpy array must be 2-dimensional")
        return SquareMap(array.astype(float, copy=True).tolist())

    def to_numpy(self, *, dtype: type[np.floating] | type[np.integer] | type[float] = float) -> np.ndarray:
        """Export map values to NumPy array.

        Args:
            dtype: Target dtype for resulting array.

        Returns:
            Copied NumPy array with map data.
        """
        return np.array(self.map_, dtype=dtype)

    def copy(self) -> SquareMap[T]:
        """Deep-copy map storage.

        Returns:
            New `SquareMap` with copied rows.
        """
        return SquareMap([list(row) for row in self.map_])

    def compass_direction(self, from_coord: Coordinate, to_coord: Coordinate) -> Direction:
        """Estimate dominant cardinal direction from one point to another.

        Args:
            from_coord: Origin coordinate.
            to_coord: Destination coordinate.

        Returns:
            Direction with dominant absolute delta.

        Raises:
            ValueError: If both coordinates are equal.
        """
        if from_coord == to_coord:
            raise ValueError("cannot infer compass direction between identical coordinates")
        dx = to_coord.x - from_coord.x
        dy = to_coord.y - from_coord.y
        if abs(dx) < abs(dy):
            return Direction.Right if dy > 0 else Direction.Left
        return Direction.Down if dx > 0 else Direction.Up

    def min(self) -> float:
        """Compute minimum numeric value in map.

        Returns:
            Minimum value as float.
        """
        return float(np.min(self.to_numpy(dtype=float)))

    def max(self) -> float:
        """Compute maximum numeric value in map.

        Returns:
            Maximum value as float.
        """
        return float(np.max(self.to_numpy(dtype=float)))

    def sum(self) -> float:
        """Compute sum of numeric values in map.

        Returns:
            Sum as float.
        """
        return float(np.sum(self.to_numpy(dtype=float)))
