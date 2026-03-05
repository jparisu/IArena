"""Tests for GoldMine position helpers and rendering."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap


def _build_rules(
    *,
    hint_mode: GoldMineHintMode = GoldMineHintMode.NONE,
    heuristic_map: SquareMap[float] | None = None,
) -> GoldMineGameRules:
    """Build a deterministic rules object used by position tests.

    Args:
        hint_mode: Hint mode to enable.
        heuristic_map: Optional heuristic map for density mode.

    Returns:
        Configured GoldMine rules.
    """
    return GoldMineGameRules(
        cost_map=SquareMap([[1.0, 2.0], [3.0, 4.0]]),
        target=Coordinate(1, 1),
        start=Coordinate(0, 0),
        hint_mode=hint_mode,
        heuristic_map=heuristic_map,
    )


def test_position_next_player_and_cost_helpers() -> None:
    """Position should expose player turn and movement/cumulative costs.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    assert position.next_player() == 0
    assert position.accumulated_cost() == 1.0
    assert position.movement_cost(Direction.Right) == 2.0

    moved = rules.next_position(rules.possible_movements(position).__next__(), position)
    assert moved.movement_cost(Direction.Up) == 0.0


def test_position_directions_to_text_and_str() -> None:
    """Position should render valid directions and text output consistently.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    options = position.directions_with_cost()
    assert options == ((Direction.Down, 3.0), (Direction.Right, 2.0))

    rendered = position.to_text()
    assert "Possible moves:" in rendered
    assert "Accumulated cost:" in rendered
    assert str(position) == rendered


def test_position_hint_accessors() -> None:
    """Position hint helpers should delegate to rule hint logic.

    Args:
        None.

    Returns:
        None.
    """
    compass_position = _build_rules(hint_mode=GoldMineHintMode.COMPASS).first_position()
    assert compass_position.compass_hint() is Direction.Down

    proximity_position = _build_rules(hint_mode=GoldMineHintMode.PROXIMITY).first_position()
    assert proximity_position.proximity_hint() == 2

    density_position = _build_rules(
        hint_mode=GoldMineHintMode.DENSITY,
        heuristic_map=SquareMap([[10.0, 20.0], [30.0, 40.0]]),
    ).first_position()
    assert density_position.density_hint() == 10.0


def test_position_to_text_includes_enabled_hints() -> None:
    """Rendered text should include only active hints.

    Args:
        None.

    Returns:
        None.
    """
    position = _build_rules(hint_mode=GoldMineHintMode.PROXIMITY).first_position()

    text = position.to_text()

    assert "Proximity hint:" in text
    assert "Compass hint:" not in text


def test_position_plot_requires_axis_and_returns_backend_object() -> None:
    """Position plotting should validate axis and return plotting backend.

    Args:
        None.

    Returns:
        None.
    """
    position = _build_rules().first_position()

    with pytest.raises(ValueError):
        position.plot()

    figure = Mock()
    axis = Mock()
    axis.get_figure.return_value = figure
    assert position.plot(axis) is axis
