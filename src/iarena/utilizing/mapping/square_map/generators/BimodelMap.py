"""Declares generator strategy for bimodal terrain maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from .AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class BimodelMap(AbstractMapGenerator):
    """Map generator with low-cost and high-cost terrain states."""

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

        p_high = float(kwargs.get("p_high", 0.3))
        cls._validate_probability(p_high)
        low_cost = float(kwargs.get("low_cost", 1.0))
        high_cost = float(kwargs.get("high_cost", 10.0))

        grid = np.full((n, m), low_cost, dtype=float)
        for i in range(n):
            for j in range(m):
                if cls._uniform01(rng) < p_high:
                    grid[i, j] = high_cost
        return grid
