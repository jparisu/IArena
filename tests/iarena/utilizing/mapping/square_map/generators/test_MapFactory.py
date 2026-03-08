from __future__ import annotations

import numpy as np

from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.generators.AbstractMapGenerator import AbstractMapGenerator
from iarena.utilizing.mapping.square_map.generators.MapFactory import MapFactory
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


class _DummyGenerator(AbstractMapGenerator):
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
        return np.full((n, m), 3.0)


def _coord(x: int, y: int) -> SquareMapCoordinate:
    c = SquareMapCoordinate()
    c.x = x
    c.y = y
    return c


def test_register_adds_generation_method() -> None:
    MapFactory.register("dummy", _DummyGenerator)
    assert "dummy" in MapFactory.available_generation_methods()


def test_generate_dispatches_to_registered_generator() -> None:
    MapFactory.register("dummy", _DummyGenerator)
    grid = MapFactory.generate("dummy", 3, 4, _coord(0, 0), _coord(2, 3), RandomGenerator(1))
    assert isinstance(grid, np.ndarray)
    assert grid.shape == (3, 4)
    assert np.all(grid == 3.0)


def test_unregister_removes_generation_method() -> None:
    MapFactory.register("dummy", _DummyGenerator)
    MapFactory.unregister("dummy")
    assert "dummy" not in MapFactory.available_generation_methods()


def test_available_generation_methods_lists_registered_names() -> None:
    available = MapFactory.available_generation_methods()
    assert isinstance(available, list)
    assert all(isinstance(name, str) for name in available)
