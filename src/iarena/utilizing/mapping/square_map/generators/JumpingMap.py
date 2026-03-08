"""Declares generator strategy with protected endpoint walkability."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from .AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class JumpingMap(AbstractMapGenerator):
    """Map generator that preserves walkable endpoints while adding high-cost tiles."""

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

        p = float(kwargs.get("p", 0.2))
        high_cost = float(kwargs.get("high_cost", 10.0))

        grid = np.ones((n, m), dtype=float)
        cls._set_random_high_tiles(grid=grid, rng=rng, p=p, high_cost=high_cost, avoid=[start, target])
        grid[start.x, start.y] = max(1.0, grid[start.x, start.y])
        grid[target.x, target.y] = max(1.0, grid[target.x, target.y])
        return grid
