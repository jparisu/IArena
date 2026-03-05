"""Column map generator implementation."""

from __future__ import annotations

from typing import Any

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.generators.JumpingMap import JumpingMap
from iarena.utilizing.square_map.SquareMap import Coordinate


class ColumnMap(AbstractMapGenerator):
    """Jumping map with guaranteed 4-neighborhood path between endpoints."""

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
        """Generate a connected map.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            **kwargs: Supports `p` in `[0,1]` and `max_tries` integer.

        Returns:
            Generated grid with guaranteed start-target connectivity.
        """
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        p = float(kwargs.get("p", 0.4))
        cls._validate_probability(p)
        max_tries = int(kwargs.get("max_tries", 200))
        if max_tries <= 0:
            raise ValueError("max_tries must be > 0")

        for _ in range(max_tries):
            grid = JumpingMap.generate(n, m, start, target, rng, p=p)
            if cls._has_path_4neigh(grid, start, target):
                return grid

        grid = JumpingMap.generate(n, m, start, target, rng, p=p)
        cls._carve_manhattan_path(grid, start, target)
        return grid
