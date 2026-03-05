"""Tests for GoldMine game rules."""

from __future__ import annotations

from unittest.mock import Mock

import pytest

from iarena.gaming.GoldMine.GoldMineGameRules import GoldMineGameRules
from iarena.gaming.GoldMine.GoldMineHintMode import GoldMineHintMode
from iarena.gaming.GoldMine.GoldMineMovement import GoldMineMovement
from iarena.gaming.GoldMine.GoldMinePosition import GoldMinePosition
from iarena.utilizing.square_map.SquareMap import Coordinate, Direction, SquareMap


class NotGoldMinePosition:
    """Dummy object used for type-validation tests."""


class NotGoldMineMovement:
    """Dummy object used for movement type-validation tests."""


def _build_rules(
    *,
    hint_mode: GoldMineHintMode = GoldMineHintMode.NONE,
    heuristic_map: SquareMap[float] | None = None,
) -> GoldMineGameRules:
    """Build a deterministic 2x2 GoldMine rules object.

    Args:
        hint_mode: Hint mode to enable.
        heuristic_map: Optional map used for density hints.

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


def test_rules_basics_players_and_first_position() -> None:
    """Rules should initialize with one player and valid first position.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    assert rules.n_players() == 1
    assert isinstance(position, GoldMinePosition)
    assert position.current_position == Coordinate(0, 0)
    assert position.dug_tiles == frozenset({Coordinate(0, 0)})


def test_rules_directions_possible_movements_and_next_position() -> None:
    """Rules should provide legal directions and produce valid successors.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    assert rules.valid_directions(position.current_position) == (Direction.Down, Direction.Right)

    movements = list(rules.possible_movements(position))
    assert movements == [GoldMineMovement(Direction.Down), GoldMineMovement(Direction.Right)]

    moved = rules.next_position(GoldMineMovement(Direction.Right), position)
    assert moved.current_position == Coordinate(0, 1)
    assert moved.dug_tiles == frozenset({Coordinate(0, 0), Coordinate(0, 1)})


def test_rules_next_position_validates_types_and_bounds() -> None:
    """Rules should reject invalid movement and position arguments.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    with pytest.raises(TypeError):
        rules.next_position(NotGoldMineMovement(), position)
    with pytest.raises(TypeError):
        rules.next_position(GoldMineMovement(Direction.Right), NotGoldMinePosition())
    with pytest.raises(ValueError):
        rules.next_position(GoldMineMovement(Direction.Up), position)


def test_rules_finished_score_cost_and_accumulated_cost() -> None:
    """Rules should compute finish condition, scoring, and map costs.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()
    position = rules.next_position(GoldMineMovement(Direction.Right), position)
    position = rules.next_position(GoldMineMovement(Direction.Down), position)

    assert rules.finished(position) is True
    assert rules.score(position).get_score(0) == -7.0
    assert rules.cost_at(Coordinate(1, 0)) == 3.0
    assert rules.accumulated_cost([Coordinate(0, 0), Coordinate(1, 0)]) == 4.0


def test_rules_expose_copy_accessors_for_maps_and_coordinates() -> None:
    """Rules should expose start/target coordinates and defensive map copies.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules(
        hint_mode=GoldMineHintMode.DENSITY,
        heuristic_map=SquareMap([[10.0, 20.0], [30.0, 40.0]]),
    )

    cost_map_copy = rules.cost_map()
    heuristic_map_copy = rules.heuristic_map()
    assert rules.start_coordinate() == Coordinate(0, 0)
    assert rules.target_coordinate() == Coordinate(1, 1)

    cost_map_copy[(0, 1)] = 999.0
    heuristic_map_copy[(1, 0)] = 777.0
    assert rules.cost_at(Coordinate(0, 1)) == 2.0
    assert rules.density_hint(Coordinate(1, 0)) == 30.0


def test_rules_hint_mode_and_enabled_helper() -> None:
    """Rules should expose active hint mode and enablement checks.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules(hint_mode=GoldMineHintMode.PROXIMITY)

    assert rules.hint_mode() is GoldMineHintMode.PROXIMITY
    assert rules.is_hint_enabled(GoldMineHintMode.PROXIMITY) is True
    assert rules.is_hint_enabled(GoldMineHintMode.COMPASS) is False


def test_rules_compass_hint_enabled_and_disabled() -> None:
    """Compass hint should work only in compass mode.

    Args:
        None.

    Returns:
        None.
    """
    compass_rules = _build_rules(hint_mode=GoldMineHintMode.COMPASS)
    assert compass_rules.compass_hint(Coordinate(0, 0)) is Direction.Down

    no_hint_rules = _build_rules()
    with pytest.raises(RuntimeError):
        no_hint_rules.compass_hint(Coordinate(0, 0))


def test_rules_proximity_hint_enabled_and_disabled() -> None:
    """Proximity hint should work only in proximity mode.

    Args:
        None.

    Returns:
        None.
    """
    proximity_rules = _build_rules(hint_mode=GoldMineHintMode.PROXIMITY)
    assert proximity_rules.proximity_hint(Coordinate(0, 0)) == 2

    no_hint_rules = _build_rules()
    with pytest.raises(RuntimeError):
        no_hint_rules.proximity_hint(Coordinate(0, 0))


def test_rules_density_hint_enabled_and_disabled() -> None:
    """Density hint should work only in density mode.

    Args:
        None.

    Returns:
        None.
    """
    heuristic_map = SquareMap([[10.0, 20.0], [30.0, 40.0]])
    density_rules = _build_rules(hint_mode=GoldMineHintMode.DENSITY, heuristic_map=heuristic_map)
    assert density_rules.density_hint(Coordinate(1, 0)) == 30.0

    no_hint_rules = _build_rules()
    with pytest.raises(RuntimeError):
        no_hint_rules.density_hint(Coordinate(0, 0))


def test_rules_validate_position_types_for_public_interface_methods() -> None:
    """Rules methods using positions should reject foreign position objects.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()

    with pytest.raises(TypeError):
        list(rules.possible_movements(NotGoldMinePosition()))
    with pytest.raises(TypeError):
        rules.finished(NotGoldMinePosition())
    with pytest.raises(TypeError):
        rules.score(NotGoldMinePosition())


def test_rules_private_position_cast_helper() -> None:
    """Private cast helper should return valid positions and reject invalid ones.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()

    assert rules._as_position(position) is position
    with pytest.raises(TypeError):
        rules._as_position(NotGoldMinePosition())


def test_rules_plot_step_delegates_to_square_map_plotter() -> None:
    """Rules plotting should return the axis backend object.

    Args:
        None.

    Returns:
        None.
    """
    rules = _build_rules()
    position = rules.first_position()
    figure = Mock()
    axis = Mock()
    axis.get_figure.return_value = figure

    plotted = rules.plot_step(axis=axis, position=position)

    assert plotted is axis
