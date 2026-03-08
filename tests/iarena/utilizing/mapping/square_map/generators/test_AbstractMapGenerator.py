from __future__ import annotations

import numpy as np
import pytest

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class _ConcreteGenerator(AbstractMapGenerator):
    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: SquareMapCoordinate,
        target: SquareMapCoordinate,
        rng: RandomGenerator,
        **kwargs,
    ) -> np.ndarray:
        return np.ones((n, m), dtype=float)


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_validate_dims_requires_positive_sizes() -> None:
    AbstractMapGenerator._validate_dims(3, 4)
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_dims(0, 4)
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_dims(3, -1)


def test_validate_coordinate_rejects_out_of_bounds_points() -> None:
    AbstractMapGenerator._validate_coordinate(3, 3, _coord(0, 0), "start")
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_coordinate(3, 3, _coord(3, 0), "start")


def test_validate_probability_accepts_unit_interval_only() -> None:
    AbstractMapGenerator._validate_probability(0.0)
    AbstractMapGenerator._validate_probability(1.0)
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_probability(-0.1)
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_probability(1.1)


def test_uniform01_returns_value_in_closed_open_unit_interval() -> None:
    rng = RandomGenerator(123)
    value = AbstractMapGenerator._uniform01(rng)
    assert 0.0 <= value < 1.0


def test_uniform_returns_value_within_requested_range() -> None:
    rng = RandomGenerator(123)
    value = AbstractMapGenerator._uniform(rng, 10.0, 20.0)
    assert 10.0 <= value < 20.0


def test_exponential_returns_positive_sample() -> None:
    rng = RandomGenerator(123)
    value = AbstractMapGenerator._exponential(rng, scale=2.0)
    assert value >= 0.0


def test_has_path_4neigh_detects_connectivity_in_grid() -> None:
    grid = np.array(
        [
            [1.0, 0.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, 1.0, 1.0],
        ]
    )
    assert AbstractMapGenerator._has_path_4neigh(grid, _coord(0, 0), _coord(2, 2)) is True


def test_carve_manhattan_path_makes_connected_walkable_cells() -> None:
    grid = np.zeros((3, 3), dtype=float)
    AbstractMapGenerator._carve_manhattan_path(grid, _coord(0, 0), _coord(2, 2))
    assert grid[0, 0] > 0.0
    assert grid[2, 2] > 0.0
    assert AbstractMapGenerator._has_path_4neigh(grid, _coord(0, 0), _coord(2, 2)) is True


def test_set_random_high_tiles_changes_some_cells_while_respecting_avoid_set() -> None:
    grid = np.ones((4, 4), dtype=float)
    avoid = [_coord(0, 0), _coord(3, 3)]
    AbstractMapGenerator._set_random_high_tiles(
        grid=grid,
        rng=RandomGenerator(123),
        p=1.0,
        high_cost=9.0,
        avoid=avoid,
    )
    assert grid[0, 0] == 1.0
    assert grid[3, 3] == 1.0
    assert np.count_nonzero(grid == 9.0) == 14
