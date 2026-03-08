"""Declares generator strategy for exponential-random cost maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from .AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class ExponentialMap(AbstractMapGenerator):
    """Map generator that samples costs from an exponential distribution."""

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

        scale = float(kwargs.get("scale", 1.0))
        grid = np.zeros((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                grid[i, j] = 1.0 + cls._exponential(rng, scale=scale)
        return grid
