from __future__ import annotations

import numpy as np
import pytest

from iarena.utilizing.randoming.Perlin import Perlin
from iarena.utilizing.randoming.RandomGenerator import RandomGenerator


def test_perlin_value_generator_returns_normalized_value() -> None:
    value = Perlin.perlin_value_generator(2, 3, base=7, scale=4.0)

    assert 0.0 <= value <= 1.0


def test_perlin_value_generator_is_deterministic_for_same_inputs() -> None:
    first = Perlin.perlin_value_generator(5, 1, base=13, scale=6.0, octaves=3)
    second = Perlin.perlin_value_generator(5, 1, base=13, scale=6.0, octaves=3)

    assert first == second


def test_perlin_value_generator_raises_for_non_positive_scale() -> None:
    with pytest.raises(ValueError, match="scale"):
        Perlin.perlin_value_generator(0, 0, base=1, scale=0.0)


def test_perlin_value_generator_raises_for_non_positive_octaves() -> None:
    with pytest.raises(ValueError, match="octaves"):
        Perlin.perlin_value_generator(0, 0, base=1, scale=1.0, octaves=0)


def test_perlin_value_generator_raises_for_non_positive_lacunarity() -> None:
    with pytest.raises(ValueError, match="lacunarity"):
        Perlin.perlin_value_generator(0, 0, base=1, scale=1.0, lacunarity=0.0)


def test_perlin_generator_returns_grid_with_expected_shape_and_bounds() -> None:
    grid = Perlin.perlin_generator(4, 6, abruptness=0.3, rng=RandomGenerator(2))

    assert isinstance(grid, np.ndarray)
    assert grid.shape == (4, 6)
    assert np.all(grid >= 0.0)
    assert np.all(grid <= 1.0)


def test_perlin_generator_is_deterministic_with_equal_rng_seed() -> None:
    first = Perlin.perlin_generator(3, 3, rng=RandomGenerator(17))
    second = Perlin.perlin_generator(3, 3, rng=RandomGenerator(17))

    assert np.array_equal(first, second)


def test_perlin_generator_raises_for_non_positive_dimensions() -> None:
    with pytest.raises(ValueError, match="dimensions"):
        Perlin.perlin_generator(0, 3)
