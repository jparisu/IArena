"""Tests for the GoldMine movement model."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


def test_init_stores_direction_value() -> None:
    movement = GoldMineMovement(direction=SquareMapDirection.UP)

    assert movement.direction == SquareMapDirection.UP


def test_init_rejects_non_direction_values() -> None:
    with pytest.raises(TypeError, match="SquareMapDirection"):
        GoldMineMovement(direction="UP")  # type: ignore[arg-type]
