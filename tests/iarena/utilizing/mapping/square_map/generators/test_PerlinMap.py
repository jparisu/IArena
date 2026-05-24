from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.PerlinMap import PerlinMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_returns_smooth_noise_like_cost_map() -> None:
    grid = PerlinMap.generate(8, 9, _coord(0, 0), _coord(7, 8), RandomGenerator(2), low=1.0, high=9.0)
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (8, 9)
    assert np.all(grid >= 1.0)
    assert np.all(grid <= 9.0)
