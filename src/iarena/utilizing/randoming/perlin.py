"""Perlin-noise helpers used by map generators."""

from __future__ import annotations

import importlib
import math

import numpy as np

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def perlin_value_generator(
    i: int,
    j: int,
    base: int,
    scale: float,
    persistence: float = 0.5,
    octaves: int = 2,
    lacunarity: float = 2.0,
) -> float:
    """Compute one Perlin value for map coordinate `(i, j)`.

    Args:
        i: Row index.
        j: Column index.
        base: Noise seed/base offset.
        scale: Spatial scale (higher means smoother changes).
        persistence: Perlin persistence parameter.
        octaves: Number of octaves.
        lacunarity: Perlin lacunarity parameter.

    Returns:
        Perlin value as float.
    """
    try:
        noise_module = importlib.import_module("noise")
        pnoise2 = noise_module.pnoise2
    except ModuleNotFoundError:

        def pnoise2(x: float, y: float, persistence: float, octaves: int, lacunarity: float) -> float:
            """Return a deterministic pseudo-noise value when `noise` is unavailable.

            Args:
                x: X-like coordinate value.
                y: Y-like coordinate value.
                persistence: Persistence-like value.
                octaves: Octaves-like value.
                lacunarity: Lacunarity-like value.

            Returns:
                Deterministic pseudo-noise float.
            """
            return math.sin(x * lacunarity + y * persistence + float(octaves))

    return float(
        pnoise2(
            (base + i) / scale,
            (base + j) / scale,
            persistence=persistence,
            octaves=octaves,
            lacunarity=lacunarity,
        )
    )


def perlin_generator(
    n: int,
    m: int,
    abruptness: float = 0.5,
    rng: RandomGenerator | None = None,
) -> np.ndarray:
    """Generate a Perlin-noise grid.

    Args:
        n: Number of rows.
        m: Number of columns.
        abruptness: Controls variation intensity.
        rng: Optional random generator used for noise base.

    Returns:
        NumPy array of shape `(n, m)` with floating-point Perlin values.
    """
    if n <= 0 or m <= 0:
        raise ValueError("n and m must be positive integers")

    abruptness = max(0.0001, abruptness * 25.0)
    if rng is None:
        rng = RandomGenerator()
    base = rng.randint(high=100000, low=0)
    scale = math.sqrt(n * m) / abruptness

    grid = np.zeros((n, m), dtype=float)
    for i in range(n):
        for j in range(m):
            grid[i, j] = perlin_value_generator(i=i, j=j, base=base, scale=scale)
    return grid
