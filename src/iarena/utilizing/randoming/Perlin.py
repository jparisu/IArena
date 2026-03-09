"""Declares Perlin-noise generation helper utilities."""

from __future__ import annotations

import numpy as np
from noise import pnoise2

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class Perlin:
    """Perlin noise utility class exposing static generation helpers.

    Purpose:
        Provides the `Perlin` type within the IArena architecture.
    How it works:
        Encapsulates behavior through its public API and type contracts defined in this class body.
    Used for:
        Building game, mapping, utility, or protocol components that can be composed by other modules.
    Public Attributes:
        None declared at class level in this base definition.
    """

    @classmethod
    def perlin_value_generator(
        cls,
        i: int,
        j: int,
        base: int,
        scale: float,
        persistence: float = 0.5,
        octaves: int = 2,
        lacunarity: float = 2.0,
    ) -> float:
        """Generate one Perlin noise value for a coordinate.

        What it does:
            Implements `perlin_value_generator` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            i (int): Input consumed by this operation.
            j (int): Input consumed by this operation.
            base (int): Input consumed by this operation.
            scale (float): Input consumed by this operation.
            persistence (float, optional): Input consumed by this operation.
            octaves (int, optional): Input consumed by this operation.
            lacunarity (float, optional): Input consumed by this operation.
        Returns:
            float: Result produced after executing the method contract.
        """
        if scale <= 0:
            raise ValueError("`scale` must be positive.")
        if octaves <= 0:
            raise ValueError("`octaves` must be positive.")
        if lacunarity <= 0:
            raise ValueError("`lacunarity` must be positive.")
        safe_base = abs(int(base)) % 1024

        value = float(
            pnoise2(
                i / scale,
                j / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                base=safe_base,
            )
        )

        # Normalize from [-1, 1] to [0, 1]
        normalized = (value + 1.0) / 2.0
        return float(min(1.0, max(0.0, normalized)))

    @classmethod
    def perlin_generator(
        cls,
        n: int,
        m: int,
        abruptness: float = 0.5,
        rng: RandomGenerator | None = None,
    ) -> np.ndarray:
        """Generate a matrix of Perlin-like noise values.

        What it does:
            Implements `perlin_generator` as part of the public behavior of its declaring class.
        How it works:
            Executes the operation according to the class contract and delegates detailed logic to the implementation.
        Args:
            n (int): Input consumed by this operation.
            m (int): Input consumed by this operation.
            abruptness (float, optional): Input consumed by this operation.
            rng (RandomGenerator | None, optional): Input consumed by this operation.
        Returns:
            np.ndarray: Result produced after executing the method contract.
        """
        if n <= 0 or m <= 0:
            raise ValueError("Map dimensions must be positive.")

        local_rng = rng if rng is not None else RandomGenerator()
        base = local_rng.randint(1024)
        scale = max(1.0, min(float(n), float(m)) * max(0.01, 1.0 - abruptness))

        grid = np.zeros((n, m), dtype=float)
        for i in range(n):
            for j in range(m):
                grid[i, j] = cls.perlin_value_generator(i, j, base=base, scale=scale)
        return grid
