"""Empty map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class EmptyMap(AbstractMapGenerator):
    """All tiles cost `1.0`."""

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
        """Generate an empty walkable map.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator (unused).
            **kwargs: Unused extra arguments.

        Returns:
            Grid full of ones.
        """
        del rng, kwargs
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")
        return np.ones((n, m), dtype=float)
