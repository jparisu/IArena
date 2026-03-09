"""Tests for the GoldMine rules implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.goldmine.GoldMineConfiguration import GoldMineConfiguration
from iarena.gaming.goldmine.GoldMineMovement import GoldMineMovement
from iarena.gaming.goldmine.GoldMinePosition import GoldMinePosition
from iarena.gaming.goldmine.GoldMineRules import GoldMineRules
from iarena.playing.PlayerIndex import PlayerIndex
from iarena.utilizing.mapping.square_map.SquareMapCoordinate import SquareMapCoordinate
from iarena.utilizing.mapping.square_map.SquareMapDirection import SquareMapDirection


def _rules() -> GoldMineRules:
    return GoldMineRules(
        GoldMineConfiguration(
            n_rows=2,
            n_cols=2,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(1, 1),
            map_data=[[0.0, 2.0], [3.0, 4.0]],
        ),
    )


def test_init_stores_configuration() -> None:
    configuration = GoldMineConfiguration(n_rows=3, n_cols=3)

    rules = GoldMineRules(configuration)

    assert rules.configuration is configuration


def test_n_players_returns_one() -> None:
    assert _rules().n_players() == 1


def test_first_position_uses_configuration_defaults() -> None:
    position = _rules().first_position()

    assert isinstance(position, GoldMinePosition)
    assert set(position.get_valid_directions()) == {SquareMapDirection.RIGHT, SquareMapDirection.DOWN}


def test_next_position_applies_legal_move_and_adds_dug_tile() -> None:
    rules = _rules()
    position = rules.first_position()

    next_position = rules.next_position(position, GoldMineMovement(direction=SquareMapDirection.RIGHT))

    assert isinstance(next_position, GoldMinePosition)
    assert set(next_position.get_valid_directions()) == {SquareMapDirection.LEFT, SquareMapDirection.DOWN}


def test_next_position_rejects_invalid_direction() -> None:
    rules = _rules()
    position = rules.first_position()

    with pytest.raises(ValueError, match="not valid"):
        rules.next_position(position, GoldMineMovement(direction=SquareMapDirection.LEFT))


def test_possible_movements_yields_cardinal_candidates_in_bounds() -> None:
    rules = _rules()
    position = rules.first_position()

    movements = list(rules.possible_movements(position))

    assert {m.direction for m in movements} == {SquareMapDirection.RIGHT, SquareMapDirection.DOWN}


def test_is_finished_detects_dug_target() -> None:
    rules = _rules()

    unfinished = rules.first_position()
    moved = rules.next_position(unfinished, GoldMineMovement(direction=SquareMapDirection.RIGHT))
    finished = rules.next_position(moved, GoldMineMovement(direction=SquareMapDirection.DOWN))

    assert rules.is_finished(unfinished) is False
    assert rules.is_finished(finished) is True


def test_get_score_returns_negative_accumulated_cost() -> None:
    rules = _rules()
    position = rules.first_position()
    position = rules.next_position(position, GoldMineMovement(direction=SquareMapDirection.RIGHT))

    score_board = rules.get_score(position)

    assert float(score_board._scores[PlayerIndex(0)]) == -2.0


def test_hint_methods_fail_when_disabled() -> None:
    rules = _rules()
    position = rules.first_position()

    with pytest.raises(RuntimeError, match="Compass"):
        position.get_compass()
    with pytest.raises(RuntimeError, match="Proximity"):
        position.get_proximity()
    with pytest.raises(RuntimeError, match="Density"):
        position.get_density()


def test_hint_methods_return_values_when_enabled() -> None:
    rules = GoldMineRules(
        GoldMineConfiguration(
            n_rows=2,
            n_cols=2,
            start=SquareMapCoordinate(0, 0),
            target=SquareMapCoordinate(1, 1),
            map_data=[[0.0, 2.0], [3.0, 4.0]],
            heuristic_map_data=[[0.0, 0.1], [0.2, 0.3]],
            compass_activated=True,
            proximity_activated=True,
            density_activated=True,
        ),
    )
    position = rules.first_position()

    assert position.get_compass() in (SquareMapDirection.RIGHT, SquareMapDirection.DOWN)
    assert position.get_proximity() == 2
    assert position.get_density() == 0.0
