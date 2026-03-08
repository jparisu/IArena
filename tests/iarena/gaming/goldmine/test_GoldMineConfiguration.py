"""Tests for the GoldMine configuration model."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate


def test_init_stores_configuration_values() -> None:
    configuration = GoldMineConfiguration(
        n_rows=4,
        n_cols=5,
        start=SquareMapCoordinate(0, 0),
        target=SquareMapCoordinate(3, 4),
        map_generator="uniform",
        seed=7,
        compass_activated=True,
    )

    assert configuration.n_rows == 4
    assert configuration.n_cols == 5
    assert configuration.start == SquareMapCoordinate(0, 0)
    assert configuration.target == SquareMapCoordinate(3, 4)
    assert configuration.map_generator == "uniform"
    assert configuration.seed == 7
    assert configuration.compass_activated is True


def test_init_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        GoldMineConfiguration(n_rows=0, n_cols=2)


def test_init_rejects_out_of_bounds_coordinates() -> None:
    with pytest.raises(ValueError, match="start"):
        GoldMineConfiguration(n_rows=3, n_cols=3, start=SquareMapCoordinate(3, 0))


def test_from_dict_parses_aliases_and_coordinates() -> None:
    configuration = GoldMineConfiguration.from_dict(
        {
            "n": 3,
            "m": 4,
            "starting_position": [0, 1],
            "target_position": {"x": 2, "y": 3},
            "compass": True,
            "proximity": True,
        },
    )

    assert configuration.n_rows == 3
    assert configuration.n_cols == 4
    assert configuration.start == SquareMapCoordinate(0, 1)
    assert configuration.target == SquareMapCoordinate(2, 3)
    assert configuration.compass_activated is True
    assert configuration.proximity_activated is True
