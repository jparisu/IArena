"""Abstract base class and shared helpers for square-map generators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable
from math import log
from typing import Any

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.SquareMap import Coordinate

type FloatGrid = Any


class AbstractMapGenerator(ABC):
    """Define map-generator interface and reusable helper utilities."""

    @classmethod
    @abstractmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> FloatGrid:
        """Generate a floating-cost grid. Args: map dimensions/endpoints/rng/options. Returns: generated grid."""
        raise NotImplementedError

    @staticmethod
    def _validate_dims(n: int, m: int) -> None:
        """Validate dimensions. Args: `n` rows and `m` cols. Returns: `None`."""
        if n <= 0 or m <= 0:
            raise ValueError("n and m must be > 0")

    @staticmethod
    def _validate_coordinate(n: int, m: int, coordinate: Coordinate, label: str) -> None:
        """Validate bounds. Args: dimensions, coordinate and error label. Returns: `None`."""
        if coordinate.x < 0 or coordinate.x >= n or coordinate.y < 0 or coordinate.y >= m:
            raise ValueError(f"{label} coordinate out of bounds for {n}x{m} map")

    @staticmethod
    def _validate_probability(p: float) -> None:
        """Validate probability. Args: `p` in `[0, 1]`. Returns: `None`."""
        if p < 0.0 or p > 1.0:
            raise ValueError("probability p must be in [0, 1]")

    @staticmethod
    def _uniform01(rng: RandomGenerator) -> float:
        """Sample uniform value. Args: random generator. Returns: float in `[0, 1)`."""
        return float(rng.random())

    @classmethod
    def _uniform(cls, rng: RandomGenerator, low: float, high: float) -> float:
        """Sample uniform in range. Args: generator and bounds. Returns: sampled float in `[low, high)`."""
        return low + (high - low) * cls._uniform01(rng)

    @classmethod
    def _exponential(cls, rng: RandomGenerator, scale: float = 1.0) -> float:
        """Sample exponential variable. Args: generator and `scale`. Returns: positive sampled float."""
        u = max(cls._uniform01(rng), 1e-12)
        return -scale * log(1.0 - u)

    @staticmethod
    def _has_path_4neigh(grid: FloatGrid, start: Coordinate, target: Coordinate) -> bool:
        """Check walkable path. Args: grid/start/target. Returns: whether a 4-neighbor path exists."""
        n_rows, n_cols = grid.shape
        for coordinate in (start, target):
            if coordinate.x < 0 or coordinate.x >= n_rows or coordinate.y < 0 or coordinate.y >= n_cols:
                return False

        if grid[start.as_tuple()] > 1.0 or grid[target.as_tuple()] > 1.0:
            return False

        frontier: deque[tuple[int, int]] = deque([start.as_tuple()])
        visited: set[tuple[int, int]] = {start.as_tuple()}
        target_tuple = target.as_tuple()

        while frontier:
            row, col = frontier.popleft()
            if (row, col) == target_tuple:
                return True

            neighbors = ((row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1))
            for next_row, next_col in neighbors:
                if next_row < 0 or next_row >= n_rows or next_col < 0 or next_col >= n_cols:
                    continue
                if (next_row, next_col) in visited:
                    continue
                if grid[next_row, next_col] > 1.0:
                    continue

                visited.add((next_row, next_col))
                frontier.append((next_row, next_col))

        return False

    @staticmethod
    def _carve_manhattan_path(grid: FloatGrid, start: Coordinate, target: Coordinate) -> None:
        """Carve deterministic path. Args: grid/start/target. Returns: `None` after in-place updates."""
        row = start.x
        col = start.y
        grid[row, col] = 1.0

        row_step = 1 if target.x >= row else -1
        while row != target.x:
            row += row_step
            grid[row, col] = 1.0

        col_step = 1 if target.y >= col else -1
        while col != target.y:
            col += col_step
            grid[row, col] = 1.0

    @classmethod
    def _set_random_high_tiles(
        cls,
        grid: FloatGrid,
        rng: RandomGenerator,
        p: float,
        high_cost: float,
        avoid: Iterable[Coordinate] | None,
    ) -> None:
        """Raise random costs. Args: grid/rng/probability/high value/avoid list. Returns: `None`."""
        avoid_cells: set[tuple[int, int]] = set()
        if avoid is not None:
            avoid_cells = {coordinate.as_tuple() for coordinate in avoid}

        n_rows, n_cols = grid.shape
        for row in range(n_rows):
            for col in range(n_cols):
                if (row, col) in avoid_cells:
                    continue
                if cls._uniform01(rng) < p:
                    grid[row, col] = high_cost
