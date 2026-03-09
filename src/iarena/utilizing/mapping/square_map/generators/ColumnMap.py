"""Declares generator strategy that preserves path connectivity."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class ColumnMap(AbstractMapGenerator):
    """Map generator that ensures connectivity between start and target."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> np.ndarray:
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        p_block = float(kwargs.get("p_block", kwargs.get("p", 0.35)))
        cls._validate_probability(p_block)

        grid = np.ones((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                if (i, j) in {(start.x, start.y), (target.x, target.y)}:
                    continue
                if cls._uniform01(rng) < p_block:
                    grid[i, j] = 0.0

        if not cls._has_path_4neigh(grid, start, target):
            cls._carve_manhattan_path(grid, start, target)

        return grid
