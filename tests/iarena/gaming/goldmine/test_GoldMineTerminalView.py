"""Tests for the GoldMine terminal view textual rendering behavior."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineGame import GoldMineGame
from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.gaming.goldmine.GoldMineTerminalView import GoldMineTerminalView
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection
from iarena.visualizing.terminal_frontend.TerminalView import TerminalView


def _rules() -> GoldMineRules:
    """Create one deterministic GoldMine ruleset."""
    return GoldMineRules(
        GoldMineConfiguration(
            n_rows=2,
            n_cols=2,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(1, 1),
            map_data=[[0.0, 2.0], [3.0, 4.0]],
        ),
    )


def test_get_str_info_includes_goal_and_input_format() -> None:
    rules = _rules()
    view = GoldMineTerminalView()

    text = view.get_str_info(rules)

    assert "GoldMine" in text
    assert "Map size" in text
    assert "Input format" in text


def test_get_str_state_includes_known_map_and_possible_movements() -> None:
    rules = _rules()
    position = rules.first_position()
    view = GoldMineTerminalView()

    text = view.get_str_state(position)

    assert "Current coordinate" in text
    assert "Known map" in text
    assert "Possible movements:" in text
    assert "RIGHT" in text
    assert "DOWN" in text


def test_capture_input_parses_direction_alias_and_full_name() -> None:
    view = GoldMineTerminalView()

    movement_from_alias = view.capture_input("u")
    movement_from_name = view.capture_input("right")

    assert isinstance(movement_from_alias, GoldMineMovement)
    assert movement_from_alias.direction == SquareMapDirection.UP
    assert isinstance(movement_from_name, GoldMineMovement)
    assert movement_from_name.direction == SquareMapDirection.RIGHT


def test_capture_input_rejects_invalid_direction_text() -> None:
    view = GoldMineTerminalView()

    with pytest.raises(ValueError, match="Expected one direction"):
        view.capture_input("north")


def test_goldmine_game_exposes_terminal_renderer() -> None:
    renderers = GoldMineGame.instance().get_renderers(
        requirements=lambda renderer_cls: issubclass(renderer_cls, TerminalView),
    )

    assert GoldMineTerminalView in renderers
