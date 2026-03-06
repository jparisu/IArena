"""Tests for the default GoldMine player."""

from __future__ import annotations

import pytest

from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMinePlayer import GoldMinePlayer
from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap


class NotGoldMinePosition:
    """Dummy object used to trigger position type checks."""


def test_player_selects_lowest_cost_direction_with_stable_tie_break() -> None:
    """Player should greedily pick minimum immediate-cost movement.

    Args:
        None.

    Returns:
        None.
    """
    rules = GoldMineGameRules(
        cost_map=SquareMap([[1.0, 1.0], [1.0, 5.0]]),
        target=Coordinate(1, 1),
        start=Coordinate(0, 0),
    )
    player = GoldMinePlayer(name="greedy")

    movement = player.play(rules.first_position())

    assert movement.direction is Direction.Down


def test_player_validates_position_type() -> None:
    """Player should reject unknown position implementations.

    Args:
        None.

    Returns:
        None.
    """
    player = GoldMinePlayer()

    with pytest.raises(TypeError):
        player.play(NotGoldMinePosition())


def test_player_raises_when_no_legal_movement_exists() -> None:
    """Player should fail loudly when game has no available movement.

    Args:
        None.

    Returns:
        None.
    """
    rules = GoldMineGameRules(
        cost_map=SquareMap([[1.0]]),
        target=Coordinate(0, 0),
        start=Coordinate(0, 0),
    )
    player = GoldMinePlayer()

    with pytest.raises(RuntimeError):
        player.play(rules.first_position())
