from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.JumpingMap import JumpingMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_keeps_endpoints_walkable() -> None:
    start = _coord(0, 0)
    target = _coord(4, 4)
    grid = JumpingMap.generate(5, 5, start, target, RandomGenerator(3), p=0.8, high_cost=20.0)
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (5, 5)
    assert grid[start.x, start.y] > 0.0
    assert grid[target.x, target.y] > 0.0
