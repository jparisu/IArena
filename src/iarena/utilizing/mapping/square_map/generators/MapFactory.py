"""Declares factory entrypoint for square-map generators."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import numpy as np

from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.mapping.square_map.generators.BimodelMap import BimodelMap
from iarena.utilizing.mapping.square_map.generators.ColumnMap import ColumnMap
from iarena.utilizing.mapping.square_map.generators.EmptyMap import EmptyMap
from iarena.utilizing.mapping.square_map.generators.ExponentialMap import ExponentialMap
from iarena.utilizing.mapping.square_map.generators.JumpingMap import JumpingMap
from iarena.utilizing.mapping.square_map.generators.PerlinMap import PerlinMap
from iarena.utilizing.mapping.square_map.generators.UniformMap import UniformMap

if TYPE_CHECKING:
    from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
    from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class MapFactory:
    """Factory registry for square-map generation strategies."""

    _REGISTRY: dict[str, type[AbstractMapGenerator]] = {
        "empty": EmptyMap,
        "uniform": UniformMap,
        "bimodel": BimodelMap,
        "column": ColumnMap,
        "exponential": ExponentialMap,
        "jumping": JumpingMap,
        "perlin": PerlinMap,
    }

    @classmethod
    def register(cls, name: str, generator: type[AbstractMapGenerator]) -> None:
        if not issubclass(generator, AbstractMapGenerator):
            raise TypeError("`generator` must inherit from AbstractMapGenerator.")
        key = name.strip().lower()
        if not key:
            raise ValueError("`name` must not be empty.")
        cls._REGISTRY[key] = generator

    @classmethod
    def unregister(cls, name: str) -> None:
        key = name.strip().lower()
        cls._REGISTRY.pop(key, None)

    @classmethod
    def generate(
        cls,
        name: str,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        integer: bool = False,
        **kwargs: Any,
    ) -> np.ndarray:
        key = name.strip().lower()
        if key not in cls._REGISTRY:
            raise ValueError(f"Unknown map generation method: {name}")

        grid = cls._REGISTRY[key].generate(n=n, m=m, start=start, target=target, rng=rng, **kwargs)
        if integer:
            return np.rint(grid).astype(int)
        return grid.astype(float)

    @classmethod
    def available_generation_methods(cls) -> list[str]:
        return sorted(cls._REGISTRY.keys())
