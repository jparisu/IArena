"""Bimodal map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class BimodelMap(AbstractMapGenerator):
    """Maps with binary terrain: normal cost `1.0` and heavy cost `n*m+1`."""

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
        """Generate bimodal-cost map.

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
        cls._set_random_high_tiles(grid, rng=rng, p=p, high_cost=float(n * m + 1), avoid=None)
        return grid
