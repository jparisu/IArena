"""Tests for the generic composable arena loop."""

from __future__ import annotations

import pytest

from iarena.arening.ArenaBehaviors import GameHistoryObserver, TurnLimitCondition
from iarena.arening.ArenaExceptions import ArenaStoppedError
from iarena.arening.GenericArena import GenericArena
from ._dummy_game import DummyMovement, DummyRules, FixedMovementPlayer


def test_generic_arena_runs_full_game_and_returns_score() -> None:
    """Generic arena should complete the default loop and return final score.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=2, max_turns=4, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement), FixedMovementPlayer(movement=movement)]
    arena = GenericArena(rules=rules, players=players)

    result = arena.play()

    assert result.get_score(0) == 2.0
    assert result.get_score(1) == 2.0
    assert arena.turns_played() == 4
    assert arena.end_reason() is None


def test_generic_arena_raises_on_turn_limit_stop_condition_by_default() -> None:
    """Turn-limit stop condition should raise by default.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=2, max_turns=10, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement), FixedMovementPlayer(movement=movement)]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[TurnLimitCondition(max_turns=2)],
    )

    with pytest.raises(ArenaStoppedError) as error_info:
        arena.play()

    assert error_info.value.final_score.get_score(0) == -float("inf")
    assert error_info.value.final_score.get_score(1) == -float("inf")
    assert "turn limit exceeded" in error_info.value.reason
    assert arena.end_reason() is not None


def test_generic_arena_returns_failure_score_when_raise_disabled() -> None:
    """Arena should return failure score when stop exceptions are disabled.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=2, max_turns=10, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement), FixedMovementPlayer(movement=movement)]
    arena = GenericArena(
        rules=rules,
        players=players,
        stop_conditions=[TurnLimitCondition(max_turns=2)],
        raise_on_stop=False,
    )

    result = arena.play()

    assert result.get_score(0) == -float("inf")
    assert result.get_score(1) == -float("inf")


def test_generic_arena_exposes_record_from_history_observer() -> None:
    """Arena should expose immutable game record when history observer is attached.

    Args:
        None.

    Returns:
        None.
    """
    movement = DummyMovement(label="inc", amount=1.0)
    rules = DummyRules(n_players=1, max_turns=3, allowed_movements=(movement,))
    players = [FixedMovementPlayer(movement=movement)]
    observer = GameHistoryObserver()
    arena = GenericArena(rules=rules, players=players, observers=[observer])

    result = arena.play()
    record = arena.game_record()

    assert result.get_score(0) == 3.0
    assert record is not None
    assert len(record.turn_records) == 3
    assert len(record.positions()) == 4
    assert len(record.movements()) == 3


def test_generic_arena_raises_for_illegal_movement() -> None:
    """Arena should raise when a player returns an illegal movement.

    Args:
        None.

    Returns:
        None.
    """
    legal_movement = DummyMovement(label="legal", amount=1.0)
    illegal_movement = DummyMovement(label="illegal", amount=9.0)
    rules = DummyRules(n_players=1, max_turns=1, allowed_movements=(legal_movement,))
    players = [FixedMovementPlayer(movement=illegal_movement)]
    arena = GenericArena(rules=rules, players=players)

    with pytest.raises(ValueError):
        arena.play()
