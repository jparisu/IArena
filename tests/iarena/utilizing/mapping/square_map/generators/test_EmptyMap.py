from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.EmptyMap import EmptyMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_returns_uniform_walkable_grid() -> None:
    grid = EmptyMap.generate(4, 5, _coord(0, 0), _coord(3, 4), RandomGenerator(1))
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (4, 5)
    assert np.all(grid == grid[0, 0])
    assert grid[0, 0] > 0.0
