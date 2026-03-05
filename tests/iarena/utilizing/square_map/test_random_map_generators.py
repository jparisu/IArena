"""Tests for random square-map generator classes and factory."""

from __future__ import annotations

from typing import Any

import numpy as np
import pytest
from numpy.typing import NDArray

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.square_map.generators import (
    AbstractMapGenerator,
    BimodelMap,
    ColumnMap,
    EmptyMap,
    ExponentialMap,
    JumpingMap,
    MapFactory,
    PerlinMap,
    UniformMap,
)
from iarena.utilizing.square_map.SquareMap import Coordinate


class DummyMap(AbstractMapGenerator):
    """Tiny concrete generator used for abstract-helper tests."""

    @classmethod
    def generate(
        cls,
        n: int,
        m: int,
        start: Coordinate,
        target: Coordinate,
        rng: RandomGenerator,
        **kwargs: Any,
    ) -> NDArray[np.float64]:
        """Generate a deterministic zero grid for factory tests.

        Args:
            n: Number of rows.
            m: Number of columns.
            start: Start coordinate.
            target: Target coordinate.
            rng: Random-number generator.
            **kwargs: Extra arguments ignored by this dummy implementation.

        Returns:
            ``n x m`` float array filled with zeros.
        """
        del start, target, rng, kwargs
        return np.zeros((n, m), dtype=float)


def test_abstract_helpers() -> None:
    """Validation, sampling and path helper methods should behave as expected."""
    rng = RandomGenerator(seed=2)

    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_dims(0, 1)
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_coordinate(2, 2, Coordinate(3, 0), "start")
    with pytest.raises(ValueError):
        AbstractMapGenerator._validate_probability(1.5)

    assert 0.0 <= AbstractMapGenerator._uniform01(rng) < 1.0
    assert 2.0 <= AbstractMapGenerator._uniform(rng, 2.0, 3.0) < 3.0
    assert AbstractMapGenerator._exponential(rng, scale=1.0) > 0.0

    grid = np.ones((3, 3), dtype=float)
    assert AbstractMapGenerator._has_path_4neigh(grid, Coordinate(0, 0), Coordinate(2, 2)) is True

    blocked = np.ones((3, 3), dtype=float)
    blocked[0, 0] = 99.0
    assert AbstractMapGenerator._has_path_4neigh(blocked, Coordinate(0, 0), Coordinate(0, 0)) is False

    carve = np.full((3, 3), 9.0, dtype=float)
    AbstractMapGenerator._carve_manhattan_path(carve, Coordinate(0, 0), Coordinate(2, 2))
    assert carve[0, 0] == 1.0
    assert carve[1, 0] == 1.0
    assert carve[2, 0] == 1.0
    assert carve[2, 1] == 1.0
    assert carve[2, 2] == 1.0

    tiles = np.ones((2, 2), dtype=float)
    AbstractMapGenerator._set_random_high_tiles(
        tiles,
        rng=RandomGenerator(seed=1),
        p=1.0,
        high_cost=7.0,
        avoid=(Coordinate(0, 0), Coordinate(1, 1)),
    )
    assert tiles[0, 0] == 1.0
    assert tiles[1, 1] == 1.0
    assert tiles[0, 1] == 7.0
    assert tiles[1, 0] == 7.0


def test_empty_map_generator_small_square() -> None:
    """EmptyMap should generate a 4x4 map with only walkable cells."""
    grid = EmptyMap.generate(4, 4, Coordinate(0, 0), Coordinate(3, 3), RandomGenerator(seed=123))
    assert grid.shape == (4, 4)
    assert np.all(grid == 1.0)


def test_bimodel_map_generator_small_square() -> None:
    """BimodelMap should generate a 4x4 map with binary costs."""
    grid = BimodelMap.generate(4, 4, Coordinate(0, 0), Coordinate(3, 3), RandomGenerator(seed=123), p=0.3)
    assert grid.shape == (4, 4)
    assert np.all(np.logical_or(grid == 1.0, grid == 17.0))


def test_jumping_map_generator_small_square() -> None:
    """JumpingMap should keep endpoints walkable on a 4x4 map."""
    start = Coordinate(0, 0)
    target = Coordinate(3, 3)
    grid = JumpingMap.generate(4, 4, start, target, RandomGenerator(seed=123), p=1.0)
    assert grid.shape == (4, 4)
    assert np.all(np.logical_or(grid == 1.0, grid == 17.0))
    assert grid[start.as_tuple()] == 1.0
    assert grid[target.as_tuple()] == 1.0


def test_column_map_generator_small_square() -> None:
    """ColumnMap should guarantee a start-target path on a 4x4 map."""
    start = Coordinate(0, 0)
    target = Coordinate(3, 3)
    grid = ColumnMap.generate(4, 4, start, target, RandomGenerator(seed=1), p=0.95, max_tries=2)
    assert grid.shape == (4, 4)
    assert grid[start.as_tuple()] == 1.0
    assert grid[target.as_tuple()] == 1.0
    assert AbstractMapGenerator._has_path_4neigh(grid, start, target) is True


def test_discrete_generators_validate_arguments() -> None:
    """Discrete generators should validate argument ranges."""
    start = Coordinate(0, 0)
    target = Coordinate(1, 1)
    rng = RandomGenerator(seed=123)

    with pytest.raises(ValueError):
        ColumnMap.generate(2, 2, start, target, rng, max_tries=0)
    with pytest.raises(ValueError):
        BimodelMap.generate(2, 2, start, target, rng, p=-0.1)


def test_column_map_fallback_path_branch(monkeypatch) -> None:
    """ColumnMap should carve a path when repeated attempts fail connectivity."""
    base = np.full((3, 3), 99.0, dtype=float)
    start = Coordinate(0, 0)
    target = Coordinate(2, 2)

    monkeypatch.setattr(JumpingMap, "generate", lambda *args, **kwargs: base.copy())
    monkeypatch.setattr(ColumnMap, "_has_path_4neigh", lambda *args, **kwargs: False)

    grid = ColumnMap.generate(3, 3, start, target, RandomGenerator(seed=0), p=1.0, max_tries=1)
    assert grid[start.as_tuple()] == 1.0
    assert grid[target.as_tuple()] == 1.0


def test_uniform_map_generator_small_square() -> None:
    """UniformMap should generate bounded random costs on a 4x4 map."""
    start = Coordinate(0, 0)
    target = Coordinate(3, 3)
    grid = UniformMap.generate(4, 4, start, target, RandomGenerator(seed=6), min_val=2.0, max_val=3.0)
    assert grid.shape == (4, 4)
    assert float(np.min(grid)) >= 2.0
    assert float(np.max(grid)) <= 3.0


def test_exponential_map_generator_small_square() -> None:
    """ExponentialMap should generate strictly positive increments over one."""
    start = Coordinate(0, 0)
    target = Coordinate(3, 3)
    grid = ExponentialMap.generate(4, 4, start, target, RandomGenerator(seed=6), scale=0.7)
    assert grid.shape == (4, 4)
    assert float(np.min(grid)) > 1.0


def test_perlin_map_generator_small_square(monkeypatch) -> None:
    """PerlinMap should generate 4x4 non-negative costs scaled up to highest."""
    monkeypatch.setattr(
        "iarena.utilizing.randoming.perlin.perlin_generator",
        lambda n, m, abruptness, rng: np.arange(n * m, dtype=float).reshape(n, m),
    )
    grid = PerlinMap.generate(
        4,
        4,
        Coordinate(0, 0),
        Coordinate(3, 3),
        RandomGenerator(seed=6),
        abruptness=0.3,
        highest=10.0,
    )
    assert grid.shape == (4, 4)
    assert float(np.min(grid)) >= 1.0
    assert float(np.max(grid)) == pytest.approx(10.0)


def test_continuous_generators_validate_arguments() -> None:
    """Continuous generators should validate argument ranges."""
    rng = RandomGenerator(seed=6)
    start = Coordinate(0, 0)
    target = Coordinate(1, 1)

    with pytest.raises(ValueError):
        UniformMap.generate(2, 2, start, target, rng, min_val=0.5)
    with pytest.raises(ValueError):
        UniformMap.generate(2, 2, start, target, rng, min_val=2.0, max_val=1.5)
    with pytest.raises(ValueError):
        ExponentialMap.generate(2, 2, start, target, rng, scale=0.0)
    with pytest.raises(ValueError):
        PerlinMap.generate(2, 2, start, target, rng, abruptness=-1.0)
    with pytest.raises(ValueError):
        PerlinMap.generate(2, 2, start, target, rng, highest=1.0)


def test_map_factory_registry_and_generation() -> None:
    """Factory should register, list, generate, and unregister generators."""
    methods = MapFactory.available_generation_methods()
    assert "uniform" in methods
    assert "uni" not in methods

    MapFactory.register("dummy", DummyMap)
    try:
        grid = MapFactory.generate(
            "dummy",
            2,
            3,
            Coordinate(0, 0),
            Coordinate(1, 2),
            RandomGenerator(seed=3),
            integer=True,
        )
        assert grid.shape == (2, 3)
        assert grid.dtype == np.int64
    finally:
        MapFactory.unregister("dummy")

    with pytest.raises(ValueError):
        MapFactory.generate("missing", 2, 2, Coordinate(0, 0), Coordinate(1, 1), RandomGenerator(seed=0))
    with pytest.raises(KeyError):
        MapFactory.unregister("missing")
