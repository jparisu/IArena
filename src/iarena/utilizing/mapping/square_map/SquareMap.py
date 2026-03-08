"""Declares rectangular square-grid container abstraction."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import numpy as np

if TYPE_CHECKING:
    from .SquareMapCoordinate import SquareMapCoordinate
    from .SquareMapDirection import SquareMapDirection


T = TypeVar("T")


class SquareMap(Generic[T]):  # noqa: UP046
    """Rectangular square-grid wrapper with navigation and numeric helpers."""

    def __init__(self, smap: Iterable[Iterable[T]]) -> None:
        rows = [list(row) for row in smap]
        if not rows:
            raise ValueError("Map must contain at least one row.")
        n_cols = len(rows[0])
        if n_cols == 0:
            raise ValueError("Map rows must contain at least one column.")
        if any(len(row) != n_cols for row in rows):
            raise ValueError("Map must be rectangular.")

        self._grid: list[list[T]] = rows
        self._n_rows = len(rows)
        self._n_cols = n_cols

    def __str__(self) -> str:
        return str(self._grid)

    def pretty_text(self) -> str:
        as_str = [[str(v) for v in row] for row in self._grid]
        width = max(len(value) for row in as_str for value in row)
        return "\n".join(" ".join(value.rjust(width) for value in row) for row in as_str)

    def size(self) -> tuple[int, int]:
        return (self._n_rows, self._n_cols)

    def n_rows(self) -> int:
        return self._n_rows

    def n_cols(self) -> int:
        return self._n_cols

    def __len__(self) -> int:
        return self._n_rows

    def __iter__(self) -> Iterator[list[T]]:
        return iter(self._grid)

    def __getitem__(self, index: SquareMapCoordinate) -> T:
        self.require_in_bounds(index)
        return self._grid[index.x][index.y]

    def __setitem__(self, index: SquareMapCoordinate, value: T) -> None:
        self.require_in_bounds(index)
        self._grid[index.x][index.y] = value

    def in_bounds(self, coord: SquareMapCoordinate) -> bool:
        return 0 <= coord.x < self._n_rows and 0 <= coord.y < self._n_cols

    def require_in_bounds(self, coord: SquareMapCoordinate, *, name: str = "coordinate") -> None:
        if not self.in_bounds(coord):
            raise ValueError(f"{name} {coord.as_tuple()} is out of bounds for map size {self.size()}.")

    def get(self, coord: SquareMapCoordinate, default: T | None = None) -> T | None:
        if not self.in_bounds(coord):
            return default
        return self._grid[coord.x][coord.y]

    def possible_direction_neighbors(
        self,
        coord: SquareMapCoordinate,
    ) -> Iterator[tuple[SquareMapDirection, SquareMapCoordinate]]:
        for direction, neighbor in coord.neighbors():
            if self.in_bounds(neighbor):
                yield direction, neighbor

    def possible_directions(self, coord: SquareMapCoordinate) -> Iterator[SquareMapDirection]:
        for direction, _ in self.possible_direction_neighbors(coord):
            yield direction

    def possible_neighbors(self, coord: SquareMapCoordinate) -> Iterator[SquareMapCoordinate]:
        for _, neighbor in self.possible_direction_neighbors(coord):
            yield neighbor

    def iter_coordinates(self) -> Iterator[SquareMapCoordinate]:
        from .SquareMapCoordinate import SquareMapCoordinate

        for i in range(self._n_rows):
            for j in range(self._n_cols):
                yield SquareMapCoordinate(i, j)

    def iter_values(self) -> Iterator[T]:
        for row in self._grid:
            yield from row

    def check(
        self,
        allow_zero: bool = True,
        skip_coordinate_validation: Iterable[SquareMapCoordinate] | None = None,
    ) -> None:
        skipped = set()
        if skip_coordinate_validation is not None:
            skipped = {(coord.x, coord.y) for coord in skip_coordinate_validation}

        for coord in self.iter_coordinates():
            if (coord.x, coord.y) in skipped:
                continue
            value = float(self[coord])
            if value < 0:
                raise ValueError(f"Map value at {coord.as_tuple()} must be non-negative.")
            if not allow_zero and value == 0:
                raise ValueError(f"Map value at {coord.as_tuple()} must be positive.")

    @classmethod
    def full(cls, n_rows: int, n_cols: int, value: T) -> SquareMap[T]:
        if n_rows <= 0 or n_cols <= 0:
            raise ValueError("Map dimensions must be positive.")
        return cls([[value for _ in range(n_cols)] for _ in range(n_rows)])

    @classmethod
    def zeros(cls, n_rows: int, n_cols: int) -> SquareMap[float]:
        return cls.full(n_rows, n_cols, 0.0)

    @classmethod
    def zeros_like(cls, smap: SquareMap[object]) -> SquareMap[float]:
        n_rows, n_cols = smap.size()
        return cls.zeros(n_rows, n_cols)

    @classmethod
    def from_numpy(cls, array: np.ndarray) -> SquareMap[float]:
        if array.ndim != 2:
            raise ValueError("Input array must be 2-dimensional.")
        return cls(array.tolist())

    def to_numpy(self, *, dtype: Any = float) -> np.ndarray:
        return np.asarray(self._grid, dtype=dtype)

    def copy(self) -> SquareMap[T]:
        return SquareMap([row.copy() for row in self._grid])

    def compass_direction(
        self,
        from_coord: SquareMapCoordinate,
        to_coord: SquareMapCoordinate,
    ) -> SquareMapDirection:
        from .SquareMapDirection import SquareMapDirection

        dx = to_coord.x - from_coord.x
        dy = to_coord.y - from_coord.y
        if dx == 0 and dy == 0:
            raise ValueError("Cannot compute direction between identical coordinates.")
        if abs(dx) >= abs(dy):
            return SquareMapDirection.DOWN if dx > 0 else SquareMapDirection.UP
        return SquareMapDirection.RIGHT if dy > 0 else SquareMapDirection.LEFT

    def min(self) -> float:
        return float(np.min(self.to_numpy(dtype=float)))

    def max(self) -> float:
        return float(np.max(self.to_numpy(dtype=float)))

    def sum(self) -> float:
        return float(np.sum(self.to_numpy(dtype=float)))
