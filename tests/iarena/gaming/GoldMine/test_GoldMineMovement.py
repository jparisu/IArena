"""Tests for GoldMine movement rendering."""

from __future__ import annotations

from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.utilizing.square_map.SquareMap import Direction


def test_movement_to_text_and_str_are_consistent() -> None:
    """Movement string methods should expose protocol-compliant text.

    Args:
        None.

    Returns:
        None.
    """
    movement = GoldMineMovement(direction=Direction.Up)

    assert movement.to_text() == "<Move Up>"
    assert str(movement) == "<Move Up>"
