"""Uniform map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class UniformMap(AbstractMapGenerator):
    """Continuous uniform random costs in `[min_val, max_val]`."""

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
        """Generate uniform random-cost map.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            **kwargs: Supports `min_val` and `max_val`.

        Returns:
            Generated grid.
        """
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        min_val = float(kwargs.get("min_val", 1.0))
        max_val = float(kwargs.get("max_val", 20.0))
        if min_val < 1.0:
            raise ValueError("min_val must be >= 1.0")
        if max_val < min_val:
            raise ValueError("max_val must be >= min_val")

        grid = np.empty((n, m), dtype=float)
        for row in range(n):
            for col in range(m):
                grid[row, col] = cls._uniform(rng, min_val, max_val)
        return grid
