from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.ExponentialMap import ExponentialMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_returns_positive_exponential_costs() -> None:
    grid = ExponentialMap.generate(5, 4, _coord(0, 0), _coord(4, 3), RandomGenerator(99), scale=2.0)
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (5, 4)
    assert np.all(grid >= 1.0)
    assert len(np.unique(grid)) > 1
