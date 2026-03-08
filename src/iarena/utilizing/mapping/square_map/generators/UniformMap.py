"""Declares generator strategy for uniform-random cost maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from .AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class UniformMap(AbstractMapGenerator):
    """Map generator that samples costs from a uniform distribution."""

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

        low = float(kwargs.get("low", 1.0))
        high = float(kwargs.get("high", 2.0))
        if high <= low:
            raise ValueError("`high` must be greater than `low`.")

        grid = np.zeros((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                grid[i, j] = cls._uniform(rng, low, high)
        return grid
