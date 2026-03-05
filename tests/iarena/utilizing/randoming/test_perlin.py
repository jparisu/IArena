"""Tests for Perlin noise helpers."""

from __future__ import annotations

from types import SimpleNamespace

import numpy as np
import pytest

from iarena.utilizing.randoming.RandomGenerator import RandomGenerator
from iarena.utilizing.randoming.perlin import perlin_generator, perlin_value_generator


def test_perlin_value_generator_uses_noise_module(monkeypatch) -> None:
    """Perlin value helper should call `noise.pnoise2` with transformed inputs."""
    captured: dict[str, float] = {}

    def fake_pnoise2(x, y, persistence, octaves, lacunarity):
        captured["x"] = x
        captured["y"] = y
        captured["persistence"] = persistence
        captured["octaves"] = float(octaves)
        captured["lacunarity"] = lacunarity
        return 0.75

    monkeypatch.setitem(__import__("sys").modules, "noise", SimpleNamespace(pnoise2=fake_pnoise2))

    value = perlin_value_generator(i=2, j=3, base=10, scale=5.0, persistence=0.4, octaves=3, lacunarity=1.8)
    assert value == 0.75
    assert captured["x"] == 12 / 5.0
    assert captured["y"] == 13 / 5.0
    assert captured["persistence"] == 0.4
    assert captured["octaves"] == 3.0
    assert captured["lacunarity"] == 1.8


def test_perlin_generator_validates_dims() -> None:
    """Grid dimensions must be positive."""
    with pytest.raises(ValueError):
        perlin_generator(0, 2)
    with pytest.raises(ValueError):
        perlin_generator(2, -1)


def test_perlin_generator_uses_rng_and_value_helper(monkeypatch) -> None:
    """Grid generator should call value helper for every coordinate."""
    calls: list[tuple[int, int, int]] = []

    def fake_value(i: int, j: int, base: int, scale: float, **_kwargs) -> float:
        calls.append((i, j, base))
        return float(i + j)

    monkeypatch.setattr("iarena.utilizing.randoming.perlin.perlin_value_generator", fake_value)

    rng = RandomGenerator(seed=12)
    grid = perlin_generator(2, 3, abruptness=0.6, rng=rng)

    assert isinstance(grid, np.ndarray)
    assert grid.shape == (2, 3)
    assert np.array_equal(grid, np.array([[0.0, 1.0, 2.0], [1.0, 2.0, 3.0]]))
    assert len(calls) == 6
    assert len({base for _, _, base in calls}) == 1


def test_perlin_generator_default_rng_branch(monkeypatch) -> None:
    """When RNG is omitted, helper should still produce a correctly shaped grid."""
    monkeypatch.setattr(
        "iarena.utilizing.randoming.perlin.perlin_value_generator",
        lambda i, j, base, scale, **_kwargs: float(base + i + j + int(scale > 0)),
    )
    monkeypatch.setattr(RandomGenerator, "randint", lambda self, high, low=0: 42)

    grid = perlin_generator(2, 2, abruptness=0.0, rng=None)
    assert grid.shape == (2, 2)
    assert np.all(grid >= 43.0)
