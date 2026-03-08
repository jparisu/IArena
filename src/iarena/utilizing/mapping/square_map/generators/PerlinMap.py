"""Declares generator strategy for smooth Perlin-like terrain maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from iarena.utilizing.randoming.Perlin import Perlin

from .AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class PerlinMap(AbstractMapGenerator):
    """Map generator that produces smooth Perlin-like terrain costs."""

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
        high = float(kwargs.get("high", 10.0))
        if high < low:
            raise ValueError("`high` must be greater than or equal to `low`.")

        noise = Perlin.perlin_generator(n, m, rng=rng)
        if high == low:
            return np.full((n, m), low, dtype=float)
        return low + (high - low) * noise
