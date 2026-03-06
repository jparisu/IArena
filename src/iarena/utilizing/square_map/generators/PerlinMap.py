"""Perlin-like map generator implementation."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator, FloatGrid
from iarena.utilizing.square_map.SquareMap import Coordinate


class PerlinMap(AbstractMapGenerator):
    """Smooth noise-based costs, shifted and scaled to be >= 1."""

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
        """Generate Perlin-like smooth cost map.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            **kwargs: Supports `abruptness` and `highest`.

        Returns:
            Generated grid with values scaled to `[1, highest]` approximately.
        """
        cls._validate_dims(n, m)
        cls._validate_coordinate(n, m, start, "start")
        cls._validate_coordinate(n, m, target, "target")

        abruptness = float(kwargs.get("abruptness", 0.5))
        highest = float(kwargs.get("highest", n * m))
        if abruptness < 0:
            raise ValueError("abruptness must be >= 0")
        if highest <= 1.0:
            raise ValueError("highest must be > 1.0")

        from iarena.utilizing.randoming.perlin import perlin_generator

        grid = perlin_generator(n, m, abruptness=abruptness, rng=rng)
        min_cost = float(np.min(grid))
        max_cost = float(np.max(grid))
        if max_cost == min_cost:
            return np.full((n, m), highest, dtype=float)

        normalized = (grid - min_cost) / (max_cost - min_cost)
        return 1.0 + normalized * (highest - 1.0)
