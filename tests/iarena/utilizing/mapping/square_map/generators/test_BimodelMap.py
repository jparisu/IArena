from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.BimodelMap import BimodelMap
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_generate_returns_bimodal_cost_grid() -> None:
    low_cost = 1.0
    high_cost = 10.0
    grid = BimodelMap.generate(
        7,
        8,
        _coord(0, 0),
        _coord(6, 7),
        RandomGenerator(22),
        p_high=0.4,
        low_cost=low_cost,
        high_cost=high_cost,
    )
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (7, 8)
    assert set(np.unique(grid)).issubset({low_cost, high_cost})
    assert low_cost in set(np.unique(grid))
    assert high_cost in set(np.unique(grid))
