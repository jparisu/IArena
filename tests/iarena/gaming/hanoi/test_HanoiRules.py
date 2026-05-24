"""Tests for the Hanoi rules implementation."""

from __future__ import annotations

import pytest

from iarena.gaming.hanoi.HanoiConfiguration import HanoiConfiguration
from iarena.gaming.hanoi.HanoiMovement import HanoiMovement
from iarena.gaming.hanoi.HanoiPosition import HanoiPosition
from iarena.gaming.hanoi.HanoiRules import HanoiRules
from iarena.playing.PlayerIndex import PlayerIndex


def _rules() -> HanoiRules:
    return HanoiRules(HanoiConfiguration(n_pegs=3, disks=[0, 0, 0]))


def test_init_stores_configuration() -> None:
    configuration = HanoiConfiguration(n_pegs=4, disks=[0, 0])

    rules = HanoiRules(configuration)

    assert rules.configuration is configuration


def test_n_players_returns_one() -> None:
    assert _rules().n_players() == 1


def test_first_position_uses_configuration_and_zero_steps() -> None:
    position = _rules().first_position()

    assert isinstance(position, HanoiPosition)
    assert position.n_pegs == 3
    assert position.disks == [0, 0, 0]
    assert position.steps == 0


def test_next_position_applies_legal_move_and_increments_steps() -> None:
    rules = _rules()
    position = rules.first_position()

    next_position = rules.next_position(position, HanoiMovement(from_peg=0, to_peg=2))

    assert next_position.disks == [0, 0, 2]
    assert next_position.steps == 1


def test_next_position_rejects_illegal_larger_onto_smaller_move() -> None:
    rules = _rules()
    position = HanoiPosition(n_pegs=3, disks=[0, 1, 1], steps=0)

    with pytest.raises(ValueError, match="larger disk"):
        rules.next_position(position, HanoiMovement(from_peg=0, to_peg=1))


def test_possible_movements_yields_legal_candidates_only() -> None:
    rules = _rules()
    position = rules.first_position()

    movements = list(rules.possible_movements(position))

    assert {(m.from_peg, m.to_peg) for m in movements} == {(0, 1), (0, 2)}


def test_is_finished_detects_goal_state() -> None:
    rules = _rules()

    assert rules.is_finished(HanoiPosition(n_pegs=3, disks=[2, 2, 2], steps=7)) is True
    assert rules.is_finished(HanoiPosition(n_pegs=3, disks=[2, 2, 1], steps=7)) is False


def test_get_score_returns_negative_step_count_for_single_player() -> None:
    rules = _rules()

    unfinished = rules.get_score(HanoiPosition(n_pegs=3, disks=[0, 0, 0], steps=0))
    finished = rules.get_score(HanoiPosition(n_pegs=3, disks=[2, 2, 2], steps=7))

    assert float(unfinished._scores[PlayerIndex(0)]) == 0.0
    assert float(finished._scores[PlayerIndex(0)]) == -7.0
