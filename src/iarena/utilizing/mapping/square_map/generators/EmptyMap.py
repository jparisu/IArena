"""Declares generator strategy for empty uniform-cost maps."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class EmptyMap(AbstractMapGenerator):
    """Map generator that returns a fully walkable uniform-cost grid."""

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
        cost = float(kwargs.get("cost", 1.0))
        return np.full((n, m), cost, dtype=float)
