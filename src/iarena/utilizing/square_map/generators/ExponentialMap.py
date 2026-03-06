"""Exponential map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class ExponentialMap(AbstractMapGenerator):
    """Random costs sampled from `1 + Exp(scale)`."""

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
        """Generate exponential random-cost map.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            **kwargs: Supports `scale` > 0.

        Returns:
            Generated grid.
        """
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        scale = float(kwargs.get("scale", 1.0))
        if scale <= 0:
            raise ValueError("scale must be > 0")

        grid = np.empty((n, m), dtype=float)
        for row in range(n):
            for col in range(m):
                grid[row, col] = 1.0 + cls._exponential(rng, scale=scale)
        return grid
