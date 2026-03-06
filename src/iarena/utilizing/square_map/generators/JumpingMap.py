"""Jumping map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class JumpingMap(AbstractMapGenerator):
    """Bimodel map that always keeps `start` and `target` walkable."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> FloatGrid:
        """Generate a bimodal map with walkable endpoints.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            **kwargs: Supports `p` in `[0,1]`.

        Returns:
            Generated grid.
        """
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        p = float(kwargs.get("p", 0.4))
        cls._validate_probability(p)

        grid = np.ones((n, m), dtype=float)
        high_cost = float(n * m + 1)
        cls._set_random_high_tiles(grid, rng=rng, p=p, high_cost=high_cost, avoid=(start, target))
        grid[start.as_tuple()] = 1.0
        grid[target.as_tuple()] = 1.0
        return grid
