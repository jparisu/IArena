"""Declares abstract strategy interface for square-map generation."""

from __future__ import annotations

import math
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Iterable
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class AbstractMapGenerator(ABC):
    """Abstract base for square-map generator strategies."""

    @classmethod
    @abstractmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a square-map grid for given dimensions, endpoints, and options."""

    @classmethod
    def _validate_dims(cls, n: int, m: int) -> None:
        if n <= 0 or m <= 0:
            raise ValueError("Map dimensions must be positive.")

    @classmethod
    def _validate_coordinate(cls, n: int, m: int, coordinate: SquareMapCoordinate, label: str) -> None:
        if coordinate.x < 0 or coordinate.x >= n or coordinate.y < 0 or coordinate.y >= m:
            raise ValueError(f"{label} coordinate {coordinate.as_tuple()} is out of bounds for {(n, m)}.")

    @classmethod
    def _validate_probability(cls, p: float) -> None:
        if p < 0.0 or p > 1.0:
            raise ValueError("Probability must be in [0, 1].")

    @classmethod
    def _uniform01(cls, rng: RandomGenerator) -> float:
        return rng.rand()

    @classmethod
    def _uniform(cls, rng: RandomGenerator, low: float, high: float) -> float:
        if high <= low:
            raise ValueError("`high` must be greater than `low`.")
        return low + (high - low) * cls._uniform01(rng)

    @classmethod
    def _exponential(cls, rng: RandomGenerator, scale: float = 1.0) -> float:
        if scale <= 0:
            raise ValueError("`scale` must be positive.")
        u = max(cls._uniform01(rng), 1e-12)
        return -scale * math.log(u)

    @classmethod
    def _has_path_4neigh(cls, grid: np.ndarray, start: SquareMapCoordinate, target: SquareMapCoordinate) -> bool:
        n, m = grid.shape
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")
        if grid[start.x, start.y] <= 0 or grid[target.x, target.y] <= 0:
            return False

        visited = np.zeros((n, m), dtype=bool)
        queue: deque[tuple[int, int]] = deque([(start.x, start.y)])
        visited[start.x, start.y] = True

        while queue:
            x, y = queue.popleft()
            if (x, y) == (target.x, target.y):
                return True
            for dx, dy in ((-1, 0), (0, 1), (1, 0), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or nx >= n or ny < 0 or ny >= m:
                    continue
                if visited[nx, ny] or grid[nx, ny] <= 0:
                    continue
                visited[nx, ny] = True
                queue.append((nx, ny))

        return False

    @classmethod
    def _carve_manhattan_path(cls, grid: np.ndarray, start: SquareMapCoordinate, target: SquareMapCoordinate) -> None:
        x, y = start.x, start.y
        grid[x, y] = max(float(grid[x, y]), 1.0)

        while x != target.x:
            x += 1 if target.x > x else -1
            grid[x, y] = max(float(grid[x, y]), 1.0)

        while y != target.y:
            y += 1 if target.y > y else -1
            grid[x, y] = max(float(grid[x, y]), 1.0)

    @classmethod
    def _set_random_high_tiles(
        cls,
        grid: np.ndarray,
        rng: RandomGenerator,
        p: float,
        high_cost: float,
        avoid: Iterable[SquareMapCoordinate] | None,
    ) -> None:
        cls._validate_probability(p)
        avoided = set()
        if avoid is not None:
            avoided = {(coord.x, coord.y) for coord in avoid}

        n, m = grid.shape
        for i in range(n):
            for j in range(m):
                if (i, j) in avoided:
                    continue
                if cls._uniform01(rng) < p:
                    grid[i, j] = high_cost
