from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.UniformMap import UniformMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_returns_uniformly_sampled_cost_grid() -> None:
    grid = UniformMap.generate(6, 7, _coord(0, 0), _coord(5, 6), RandomGenerator(10), low=1.0, high=3.0)
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (6, 7)
    assert np.all(grid >= 1.0)
    assert np.all(grid < 3.0)
    assert len(np.unique(grid)) > 1
