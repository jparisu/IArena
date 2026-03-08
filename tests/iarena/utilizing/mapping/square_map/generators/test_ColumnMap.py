from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.mapping.square_map.generators.ColumnMap import ColumnMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_creates_connected_grid_for_start_and_target() -> None:
    start = _coord(0, 0)
    target = _coord(9, 9)
    grid = ColumnMap.generate(10, 10, start, target, RandomGenerator(8))
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (10, 10)
    assert AbstractMapGenerator._has_path_4neigh(grid, start, target) is True
