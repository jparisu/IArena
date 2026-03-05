"""Factory class for square-map generators."""

from __future__ import annotations

from typing import Any

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.square_map.generators.BimodelMap import BimodelMap
from iarena.utilizing.square_map.generators.ColumnMap import ColumnMap
from iarena.utilizing.square_map.generators.EmptyMap import EmptyMap
from iarena.utilizing.square_map.generators.ExponentialMap import ExponentialMap
from iarena.utilizing.square_map.generators.JumpingMap import JumpingMap
from iarena.utilizing.square_map.generators.PerlinMap import PerlinMap
from iarena.utilizing.square_map.generators.UniformMap import UniformMap
from iarena.utilizing.square_map.SquareMap import Coordinate


class MapFactory:
    """Registry-based map generation facade."""

    _REGISTRY: dict[str, type[AbstractMapGenerator]] = {
        "empty": EmptyMap,
        "bimodel": BimodelMap,
        "jumping": JumpingMap,
        "column": ColumnMap,
        "uniform": UniformMap,
        "exponential": ExponentialMap,
        "perlin": PerlinMap,
        "exp": ExponentialMap,
        "uni": UniformMap,
        "random": UniformMap,
    }

    @classmethod
    def register(cls, name: str, generator: type[AbstractMapGenerator]) -> None:
        """Register or override a generator in the factory.

        Args:
            name: Registry key.
            generator: Generator class to associate with the key.

        Returns:
            `None`.
        """
        cls._REGISTRY[name.strip().lower()] = generator

    @classmethod
    def unregister(cls, name: str) -> None:
        """Remove generator from factory registry.

        Args:
            name: Registry key to remove.

        Returns:
            `None`.
        """
        key = name.strip().lower()
        if key not in cls._REGISTRY:
            raise KeyError(f"generator '{name}' is not registered")
        del cls._REGISTRY[key]

    @classmethod
    def generate(
        cls,
        name: str,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        integer: bool = False,
        **kwargs: Any,
    ) -> np.ndarray:
        """Generate a map by registered name.

        Args:
            name: Generator name or alias.
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random generator.
            integer: If `True`, round output to integers.
            **kwargs: Parameters forwarded to selected generator.

        Returns:
            Generated NumPy array.
        """
        key = name.strip().lower()
        if key not in cls._REGISTRY:
            available = ", ".join(sorted(cls._REGISTRY))
            raise ValueError(f"unknown map generator '{name}'. Available: {available}")

        generator_cls = cls._REGISTRY[key]
        grid = generator_cls.generate(n, m, start, target, rng, **kwargs)
        if integer:
            return np.round(grid).astype(int)
        return grid

    @classmethod
    def available_generation_methods(cls) -> list[str]:
        """List canonical generation method names.

        Returns:
            Sorted list with one name per unique generator class.
        """
        methods: list[str] = []
        seen: set[type[AbstractMapGenerator]] = set()
        for key, generator_cls in cls._REGISTRY.items():
            if generator_cls in seen:
                continue
            seen.add(generator_cls)
            methods.append(key)
        return sorted(methods)
